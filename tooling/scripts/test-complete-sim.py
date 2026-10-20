#!/usr/bin/env python3
"""0041 full-flow acceptance through real X11 keyboard and local service events.

Owns only its SIM process and temporary configuration. Existing user state is
restored in finally. A running interactive SIM must be stopped before use.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import subprocess
import time
import io
from PIL import Image

ROOT = Path(os.environ.get('NUTTX_SIM_HOME', '/home/slepher/nuttx-ap01-sim'))
SOURCE = Path(__file__).resolve().parent
EVIDENCE = Path(os.environ.get('AP01_SIM_EVIDENCE', SOURCE.parents[1] / 'reverse/rehost'))
REPORT = EVIDENCE / 'complete-nuttx-sim-verification.json'
LOG = EVIDENCE / 'complete-nuttx-sim-keyboard.log'
assert EVIDENCE.is_dir()
spec = importlib.util.spec_from_file_location('control', SOURCE / 'sim-control.py')
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)
exe = ROOT / 'nuttx/nuttx'
report = {'passed': False, 'status': 'running', 'binary_sha256': hashlib.sha256(exe.read_bytes()).hexdigest(),
          'steps': [], 'screenshots': []}
REPORT.write_text(json.dumps(report, indent=2) + '\n')
store = ROOT / 'ap01-sim-state.bin'
backup = ROOT / 'ap01-sim-state.acceptance-backup'
assert not backup.exists(), 'Previous state backup requires recovery first'
wifi_files = list(ROOT.glob('ap01-sim-state.bin.wifi-*')) + list(ROOT.glob('ap01-sim-state.bin.wapi.conf*'))
wifi_backups = [(file, file.with_name(file.name + '.acceptance-backup')) for file in wifi_files]
assert all(not file.name.endswith('.acceptance-backup') and not saved.exists()
           for file, saved in wifi_backups), 'Wi-Fi backup requires recovery first'
if store.exists():
    store.rename(backup)
for file, saved in wifi_backups:
    file.rename(saved)
sim = None
xserver = None
log = None
env = None
wid = None


def snapshot():
    try:
        return json.loads((ROOT / 'sim-response.json').read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def wait(check, description, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        state = snapshot()
        if state and check(state):
            return state
        if sim is not None and sim.poll() is not None:
            raise AssertionError(f'SIM exited: {description}\n{LOG.read_text()[-6000:]}')
        time.sleep(.05)
    raise AssertionError(f'Timeout: {description}; state={snapshot()}\n{LOG.read_text()[-2500:]}')


def check(condition, description):
    assert condition, description
    report['steps'].append({'assert': description})


def command(operation, *values, status=None):
    result = control.request(operation, values, ROOT)
    report['steps'].append({'service_event': operation, 'arguments': values, 'reply': result['reply']})
    if status is not None:
        assert result['reply']['status'] == status, result
    return result


def raw_request(session, sequence, operation):
    temporary = ROOT / 'sim-request.txt.new'
    temporary.write_text(f'{session} {sequence} {operation} 0 0 0 0\n')
    temporary.replace(ROOT / 'sim-request.txt')


def key(name, count=1):
    for _ in range(count):
        subprocess.run(['xdotool', 'keydown', '--window', wid, name], env=env,
                       check=True, timeout=5, capture_output=True)
        time.sleep(.09)
        subprocess.run(['xdotool', 'keyup', '--window', wid, name], env=env,
                       check=True, timeout=5, capture_output=True)
        time.sleep(.18)
        report['steps'].append({'key': name, 'state': snapshot()})


def capture(name):
    time.sleep(.25)
    path = EVIDENCE / f'complete-ui-{name}.png'
    subprocess.run(['import', '-window', wid, str(path)], env=env, check=True,
                   timeout=5, capture_output=True)
    report['screenshots'].append({'name': name, 'path': str(path),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    return path


def go(page):
    # Escape is the simulator's explicit back key, never a shortcut to a page.
    for _ in range(12):
        s = snapshot()
        ui = s.get('ui', {})
        if not ui.get('system') and not ui.get('guide_active') and not ui.get('charge_popup') and not ui.get('saver') and s.get('mode') == 0:
            break
        key('Escape')
    for _ in range(12):
        if snapshot().get('page') == page:
            return
        key('Right')
    raise AssertionError(f'Cannot reach {page}: {snapshot()}')


def charge(view, item=None):
    return wait(lambda s: s.get('ui', {}).get('charge_view') == view and
                (item is None or s['ui']['charge_item'] == item), f'charge view={view} item={item}')


def port(bank, index):
    return next(p for p in snapshot()['ports'] if p['bank'] == bank and p['port'] == index)


def clock_pixels(path, digits):
    asset_spec = importlib.util.spec_from_file_location('assets', SOURCE / 'rehost-assets.py')
    assets = importlib.util.module_from_spec(asset_spec)
    asset_spec.loader.exec_module(assets)
    rom = Path(os.environ.get('AP01_ROM', SOURCE.parents[1] / 'roms/0041/ap01-1.0.2_0041.bin')).read_bytes()
    actual = Image.open(path).convert('RGB')
    for x, digit in zip((20, 83, 181, 244), digits):
        png, width, height = assets.png_at(rom, assets.DIGITS[int(digit)])
        foreground = Image.open(io.BytesIO(png)).convert('RGBA')
        expected = Image.new('RGBA', foreground.size, (0, 0, 0, 255))
        expected.alpha_composite(foreground)
        wanted = expected.convert('RGB').tobytes()
        observed = actual.crop((x, 90, x + width, 90 + height)).tobytes()
        error = sum(abs(a - b) for a, b in zip(wanted, observed)) / len(wanted)
        check(error < 5, f'native clock digit {digit} pixel mean error {error:.3f}')


def start(retain_transport=False, verify_boot=False):
    global sim, wid
    previous_session = snapshot().get('session')
    if not retain_transport:
        (ROOT / 'sim-response.json').unlink(missing_ok=True)
        (ROOT / 'sim-request.txt').unlink(missing_ok=True)
    sim = subprocess.Popen([str(exe)], cwd=exe.parent, stdin=subprocess.DEVNULL,
                           stdout=log, stderr=subprocess.STDOUT, env=env)
    wait(lambda s: bool(s) and s.get('session') != previous_session, 'new process publishes state')
    windows = subprocess.check_output(['xdotool', 'search', '--name', '^NuttX$'],
                                     env=env, text=True, timeout=5).splitlines()
    assert len(windows) == 1, windows
    wid = windows[0]
    geometry = subprocess.check_output(['xwininfo', '-id', wid], env=env, text=True)
    check('Width: 320' in geometry and 'Height: 240' in geometry, 'native 320x240 framebuffer')
    if verify_boot:
        check(snapshot()['ui']['boot'], 'native boot stage is active before ready')
        capture('boot-logo')
        page = snapshot()['page']
        key('Right')
        check(snapshot()['page'] == page, 'boot consumes rotary input')
    wait(lambda s: not s.get('ui', {}).get('boot'), 'boot ready')


def stop():
    global sim
    if sim and sim.poll() is None:
        sim.terminate()
        sim.wait(timeout=5)
    sim = None


try:
    xserver = subprocess.Popen(['Xvfb', '-displayfd', '1', '-screen', '0', '640x480x24',
                               '-nolisten', 'unix', '-nolisten', 'tcp'],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    assert select.select([xserver.stdout], [], [], 10)[0]
    display = xserver.stdout.readline().decode().strip()
    assert display.isdecimal()
    env = dict(os.environ, DISPLAY=f':{display}')
    log = LOG.open('w')
    start(verify_boot=True)
    capture('first-boot')
    # The first-use guide is reachable on unconfigured Mijia. It must require
    # rotation for its rotation task rather than acknowledge an inert button.
    if not snapshot()['ui']['guide_active']:
        go('Mijia')
        key('Return')
    wait(lambda s: s['ui']['guide_active'], 'guide opened')
    key('Return')  # panel 1 -> panel 2
    key('Return')  # welcome
    wait(lambda s: s['ui']['guide_stage'] == 0x27, 'guide welcome')
    key('Return')
    wait(lambda s: s['ui']['guide_stage'] == 0x28, 'rotation task')
    key('Return')
    check(snapshot()['ui']['guide_stage'] == 0x28, 'press does not complete rotation task')
    key('Right')
    wait(lambda s: s['ui']['guide_stage'] == 0x29, 'rotation completes task')
    key('Return', 3)
    wait(lambda s: s['ui']['guide_stage'] == 0x2c, 'guide congratulations')
    capture('guide-completed')
    command('fault', 1)
    key('Return')
    check(snapshot()['settings']['guide'] == 0 and snapshot()['ui']['guide_active'], 'guide save failure remains retryable')
    key('Return')
    wait(lambda s: s['settings']['guide'] == 1 and not s['ui']['guide_active'], 'guide persisted')
    # Both Wi-Fi configured visibility and current network state matter.
    command('wifi', 1, status=2)
    command('weather', status=1)
    wait(lambda s: s['weather'] == 2, 'weather asynchronous response')
    command('charger', 1, status=2)
    command('bank', 0, 1, status=2)
    wait(lambda s: not s['ui']['charge_popup'], 'C1 insertion popup expires', 6)
    command('bank', 1, 1, status=2)
    capture('bank-insertion')
    wait(lambda s: not s['ui']['charge_popup'], 'C2 insertion popup expires', 6)
    command('fixture', 1, status=2)
    for page in ('Power', 'C1', 'C2', 'Time', 'Date', 'Weather', 'Pet', 'Settings'):
        go(page)
        shot = capture(page.lower())
        if page == 'Time':
            clock_pixels(shot, '0037')
    # Native C1/C2 are telemetry overviews: press is deliberately a no-op.
    for page in ('C1', 'C2'):
        go(page)
        key('Return')
        check(snapshot()['mode'] == 0, f'{page} native press no-op')
    command('port-state', 0, 0, 7, 100, status=2)
    command('telemetry', 0, 0, 28000, 5000, status=2)
    go('C1')
    capture('c1-input-bms-full')
    command('port-state', 0, 0, 4, 0, status=2)
    capture('c1-output-no-bms')
    command('port-state', 0, 0, 6, 67, status=2)
    command('telemetry', 0, 0, 9000, 2200, status=2)
    # The Power menu controls the four local charger ports.
    for page, bank in (('Power', 2),):
        go(page)
        key('Return')
        charge(0, 0)
        key('Return')
        charge(1, 0)
        for mode in range(3):
            if mode:
                key('Right')
            key('Return')
            check(snapshot()['settings']['mode'] == mode, f'{page} mode {mode} committed')
        command('fault', 2)
        key('Left')
        key('Return')
        wait(lambda s: s['ui']['system'] == 7, 'mode timeout feedback')
        check(snapshot()['settings']['mode'] == 2, 'failed mode command rolls back')
        capture(f'{page.lower()}-service-timeout')
        key('Return')
        key('Escape')
        charge(0, 0)
        for index in range(4):
            key('Right')
            charge(0, index + 1)
            key('Return')
            charge(2, 0)
            capture(f'{page.lower()}-port-{index+1}')
            if index == 0:
                command('telemetry', 2, 0, 28000, 5000, status=2)
                capture('port-three-digit-power')
                command('telemetry', 2, 0, 20000, 3500, status=2)
            key('Right')
            key('Return')
            charge(3, 0)
            key('Right')
            key('Return')
            check(not port(bank, index)['enabled'], f'{page} port {index+1} disabled')
            key('Left')
            key('Return')
            check(port(bank, index)['enabled'], f'{page} port {index+1} enabled')
            key('Escape')
            charge(2, 1)
            key('Escape')
            charge(0, index + 1)
        key('Escape')
    # Device attachment populates local protocol/safe support and native popup.
    command('device', 2, 0, 1, status=2)
    capture('device-insertion')
    wait(lambda s: not s['ui']['charge_popup'], 'device popup expires', 6)
    go('Power')
    key('Return')
    key('Right')
    key('Return')
    charge(2, 0)
    key('Right', 2)
    key('Return')
    charge(4, 0)
    key('Return')
    charge(5)
    capture('safe-charge-intro')
    wait(lambda s: s['ui']['charge_view'] == 4, 'safe introduction timer', 9)
    check(port(2, 0)['safe'], 'safe-charge command persisted')
    command('device', 2, 0, 0, status=2)
    command('device', 2, 0, 1, status=2)
    wait(lambda s: s['ui']['charge_popup'] == 3, 'safe-charge device popup')
    capture('safe-device-insertion')
    wait(lambda s: not s['ui']['charge_popup'], 'safe-device popup expires', 6)
    key('Right')
    key('Return')
    check(not port(2, 0)['safe'], 'safe-charge disabled')
    key('Escape')
    key('Right')
    key('Return')
    charge(6, 1)
    capture('protocol-intro')
    command('protocol-mask', 2, 0, 5, status=2)
    command('fault', 2)
    key('Return')
    check(port(2, 0)['protocol'] == 1, 'protocol detection pending')
    key('Left')
    check(snapshot()['ui']['charge_item'] == 1, 'protocol pending ignores rotation')
    wait(lambda s: port(2, 0)['protocol'] == 4, 'protocol timeout result')
    capture('protocol-timeout')
    key('Return')
    wait(lambda s: port(2, 0)['protocol'] == 2, 'protocol retry success')
    capture('protocol-result')
    key('Return')
    charge(2, 3)
    check(port(2, 0)['disabled'] == 2, 'protocol confirm writes inverse detected mask (PPS disabled)')
    # Date is independent from the host RTC; rotary moves weeks both ways.
    go('Date')
    key('Return')
    key('Left', 6)
    capture('date-previous-year')
    key('Right', 12)
    capture('date-next-month')
    key('Return')
    # Five native weather detail positions, bounded at both ends.
    go('Weather')
    key('Return')
    key('Left', 2)
    capture('weather-detail-top')
    for index in range(1, 5):
        key('Right')
        capture(f'weather-detail-{index}')
    key('Right', 2)
    key('Return')
    for code, humidity, aqi, uvi in ((100, 0, 0, 0), (101, 100, 50, 2), (300, 58, 100, 5),
                                   (400, 80, 150, 7), (500, 80, 200, 10), (999, 50, 500, 20)):
        command('weather-data', code, humidity, aqi, uvi, status=2)
        go('Weather')
        capture(f'weather-code-{code}')
        key('Return')
        key('Right')
        capture(f'weather-metrics-{code}')
        key('Return')
    command('fault', 2)
    command('weather', status=1)
    wait(lambda s: s['weather'] == 4, 'weather timeout')
    capture('weather-timeout')
    key('r')
    wait(lambda s: s['weather'] == 2, 'weather recovery')
    # Native time-format choices commit through the same persistent service.
    go('Time')
    key('Return')
    key('Right')
    key('Return')
    check(snapshot()['settings']['hour12'], '12-hour format saved')
    capture('time-format-menu-12-hour')
    key('Escape')
    shot = capture('time-12-hour')
    clock_pixels(shot, '1237')
    key('Return')
    key('Left')
    key('Return')
    check(not snapshot()['settings']['hour12'], '24-hour format saved')
    key('Right', 2)
    key('Return')
    go('Time')
    key('Return')
    subprocess.run(['xdotool', 'keydown', '--window', wid, 'Return'], env=env, check=True)
    time.sleep(2.5)
    check(snapshot()['page'] == 'Time' and snapshot()['mode'] == 2, 'hold under3s does not trigger native long press')
    time.sleep(.8)
    subprocess.run(['xdotool', 'keyup', '--window', wid, 'Return'], env=env, check=True)
    wait(lambda s: s['page'] == 'Power' and s['mode'] == 0, '3s hold returns native Power')
    report['steps'].append({'hold': 'Return', 'seconds': 3.3})
    # Full setting families, including scroll boundaries and transactional
    # preview/confirm brightness rather than writing on every encoder tick.
    go('Settings')
    key('Return')
    for index, field in ((0, 'always_on'), (1, 'saver')):
        if index:
            key('Right')
        key('Return')
        key('Right')
        key('Return')
        check(not snapshot()['settings'][field], f'{field} disabled')
        key('Left')
        key('Return')
        check(snapshot()['settings'][field], f'{field} enabled')
        key('Right', 2)
        key('Return')
    key('Right')  # Wi-Fi is directly below screensaver.
    key('Return')
    check(snapshot()['selection'] == 2 and snapshot()['mode'] == 2, 'Wi-Fi menu position')
    capture('wifi-empty')
    key('Return')
    check(snapshot()['mode'] == 1, 'empty Wi-Fi list has working Back')
    fixture_native = b'opaque-original-config-test\x00\xff'
    result = control.request('wifi-put', (0,), ROOT, profile=('Home', fixture_native))
    check(result['request_ok'], 'management imports saved Wi-Fi without activation')
    result = control.request('wifi-put', (3,), ROOT, profile=('Office', fixture_native + b'2'))
    check(result['request_ok'] and result['wifi_active'] == -1, 'profile edits leave active configuration unchanged')
    key('Return')
    capture('wifi-names')
    binding_before_wifi = snapshot()['bound']
    command('wifi-plan', 0, 0, 800, status=2)
    key('Return')
    check(not snapshot()['wifi'] and snapshot()['wifi_target'] == 0,
          'menu selection starts a network attempt without claiming connected')
    capture('wifi-associating')
    wait(lambda s: s['wifi_phase'] == 'waiting-ip', 'association is distinct from IP ready')
    check(not snapshot()['wifi'], 'association alone is not network success')
    capture('wifi-waiting-ip')
    wait(lambda s: s['wifi_active'] == 0 and s['wifi'], 'click Wi-Fi name confirms IP')
    check((ROOT / 'ap01-sim-state.bin.wapi.conf').read_bytes() == fixture_native, 'active native bytes preserved')
    result = control.request('wifi-put', (0,), ROOT, profile=('Home', fixture_native + b'-candidate'))
    check(result['request_ok'] and result['wifi'] and result['wifi_current_ssid'] == 'Home',
          'editing current SSID candidate only changes saved list')
    check((ROOT / 'ap01-sim-state.bin.wapi.conf').read_bytes() == fixture_native,
          'list update leaves current network configuration untouched')
    command('wifi-delete', 0, status=2)
    check(snapshot()['wifi'] and snapshot()['wifi_active'] == 8 and snapshot()['wifi_current_virtual'],
          'deleted current record remains a unique local recovery item')
    check(sum(p['ssid'] == 'Home' for p in snapshot()['wifi_profiles']) == 1,
          'uniq merges current SSID once after saved record deletion')
    capture('wifi-current-uniq')
    result = control.request('wifi-put', (0,), ROOT, profile=('Home', fixture_native))
    check(result['request_ok'] and not result['wifi_current_virtual'] and result['wifi'],
          'saving current SSID merges without duplicate or reconnection')
    command('fault', 1, status=2)
    key('Right')
    key('Return')
    check(snapshot()['wifi_active'] == 0 and snapshot()['ui']['system'] == 7, 'failed switch retains old Wi-Fi')
    key('Return')  # dismiss error; keep selected row
    command('wifi-plan', 1, 0, 100, status=2)
    key('Return')
    wait(lambda s: s['wifi_phase'] == 'confirmed' and s['wifi_active'] == 0 and s['wifi'],
         'post-disconnect association failure restores original network')
    check((ROOT / 'ap01-sim-state.bin.wapi.conf').read_bytes() == fixture_native,
          'failed candidate restores original persistent bytes')
    capture('wifi-automatic-rollback')
    command('wifi-plan', 2, 0, 100, status=2)
    key('Return')
    wait(lambda s: s['wifi_phase'] == 'confirmed' and s['wifi_active'] == 0 and s['wifi'],
         'silent network timeout restores original network')
    command('wifi-plan', 1, 1, 100, status=2)
    key('Return')
    wait(lambda s: s['wifi_phase'] == 'disconnected' and not s['wifi'],
         'candidate and original network can both be unavailable')
    check(snapshot()['mode'] == 2 and snapshot()['selection'] == 2,
          'local Wi-Fi menu remains usable with no network')
    capture('wifi-offline-menu')
    # No management request is issued between this snapshot and restored IP.
    offline_request = snapshot()['request_high_water']
    key('Left')
    key('Return')
    wait(lambda s: s['wifi_phase'] == 'confirmed' and s['wifi_active'] == 0 and s['wifi'],
         'rotary menu alone reconnects original network while offline')
    check(snapshot()['request_high_water'] == offline_request,
          'offline recovery needs no management command or session')
    capture('wifi-local-recovery')
    # Interrupt a trial before the driver can produce association/IP events.
    command('wifi-plan', 2, 0, 3000, status=2)
    key('Right')
    key('Return')
    check((ROOT / 'ap01-sim-state.bin.wifi-pending').exists(), 'trial has durable recovery marker')
    stop()
    start()
    wait(lambda s: s['wifi_phase'] == 'confirmed' and s['wifi_active'] == 0 and s['wifi'],
         'restart during trial restores original configuration and reconnects')
    check((ROOT / 'ap01-sim-state.bin.wapi.conf').read_bytes() == fixture_native,
          'restart never commits an unconfirmed candidate')
    check(not (ROOT / 'ap01-sim-state.bin.wifi-pending').exists(), 'recovered trial marker cleared')
    go('Settings')
    key('Return')
    key('Right', 2)
    key('Return')
    command('wifi-plan', 0, 0, 200, status=2)
    key('Right')
    key('Return')
    wait(lambda s: s['wifi_phase'] == 'confirmed' and s['wifi_active'] == 3 and s['wifi'],
         'retry activates second Wi-Fi only after IP confirmation')
    check(snapshot()['bound'] == binding_before_wifi, 'SIM binding survives trials, rollback and restart')
    capture('wifi-second-network-confirmed')
    key('Right')
    key('Return')
    check(snapshot()['mode'] == 1, 'Wi-Fi Back returns to settings')
    key('Right')  # brightness
    key('Return')
    key('Return')
    key('Left', 12)
    check(snapshot()['settings']['brightness'] == 10, 'brightness preview does not commit')
    key('Right')  # native raw0 -> raw110
    key('Return')
    check(snapshot()['settings']['brightness'] == 11, 'native brightness 0 to110 transition saved')
    capture('brightness-110')
    key('Return')
    key('Left')
    key('Return')
    check(snapshot()['settings']['brightness'] == 10, 'brightness restored')
    key('Escape')
    key('Right')
    key('Return')
    capture('versions-connected')
    key('Escape')
    key('Right')
    key('Return')
    key('Left')
    key('Return')  # native panel Skip -> Welcome, not guide completion
    wait(lambda s: s['ui']['guide_stage'] == 0x27, 'guide panel skip opens welcome')
    key('Left')
    key('Return')
    check(snapshot()['settings']['guide'] and not snapshot()['ui']['guide_active'], 'welcome skip completes guide')
    go('Pet')
    for pet in range(5):
        check(snapshot()['settings']['pet'] == pet, f'pet {pet} selected')
        image_a = capture(f'pet-{pet}-a')
        time.sleep(.8)
        image_b = capture(f'pet-{pet}-b')
        raw_a = subprocess.check_output(['convert', str(image_a), 'RGB:-'])
        raw_b = subprocess.check_output(['convert', str(image_b), 'RGB:-'])
        check(raw_a != raw_b, f'pet {pet} native GIF advances')
        key('Return')
    # Known Gregorian/lunar anchors and range boundaries use an isolated
    # simulated clock; the host RTC remains untouched.
    for date in ('1888-02-11', '1888-02-12', '2023-03-22', '2024-02-09', '2024-02-10',
                 '2024-02-29', '2024-04-04', '2024-09-17', '2024-12-31', '2111-12-31', '2112-01-01'):
        command('date', int(date.replace('-', '')), status=2)
        go('Date')
        capture('date-' + date)
        key('Return')
        capture('calendar-' + date)
        year, month, day = map(int, date.split('-'))
        prefix = f'DATE calendar view=detail year={year} month={month} day={day} subtitle='
        labels = {'1888-02-12': '春节', '2024-02-09': '除夕', '2024-02-10': '春节', '2024-09-17': '中秋节'}
        if date in labels:
            check(prefix + labels[date] in LOG.read_text(), f'actual C calendar subtitle {date}={labels[date]}')
        if date in ('1888-02-11', '2112-01-01'):
            matching = [line for line in LOG.read_text().splitlines() if line.startswith(prefix)]
            check(bool(matching) and 'lunarSupported=0' in matching[-1], f'{date} safely outside native lunar table')
        key('Return')
    # Screen savers consume only the wake event; follow-up event navigates.
    for mode in (1, 2, 3):
        command('saver', mode, status=2)
        wait(lambda s: s['ui']['saver'] == mode, f'saver mode {mode}')
        capture(f'saver-{mode}')
        page = snapshot()['page']
        key('Right')
        check(not snapshot()['ui']['saver'] and snapshot()['page'] == page, 'wake key consumed')
    go('Settings')
    key('Return')
    key('Return')
    key('Right')
    key('Return')  # always-on off; saver remains enabled
    key('Escape', 2)
    command('timers', 1, 2, 2, status=2)
    wait(lambda s: s['ui']['saver'] == 2, 'idle enters time saver')
    wait(lambda s: s['ui']['saver'] == 3, 'blank deadline continues while saver active')
    capture('idle-screen-off')
    key('Right')
    command('timers', 180, 60, 2, status=2)
    # Persistence survives a new NuttX process, not merely a redraw.
    before = snapshot()['settings'].copy()
    stop()
    # A stale destructive command must be retired, not executed on startup.
    old_session = snapshot()['session']
    (ROOT / 'sim-request.txt').write_text(f'{old_session} 99999 reset 0 0 0 0\n')
    start(retain_transport=True)
    check(snapshot()['request_retired'] and snapshot()['request'] == 99999, 'stale request is retired across restart')
    check(snapshot()['settings'] == before, 'configuration persists across process restart')
    session = snapshot()['session']
    raw_request(session, 99999, 'status')
    wait(lambda s: not s['request_retired'] and s['request_high_water'] == 99999, 'new session accepts retired numeric id')
    command('status')
    high_water = snapshot()['request_high_water']
    raw_request(session, 99999, 'reset')
    wait(lambda s: s['request'] == 99999 and s['reply']['stage'] == 'replay', 'older id cannot replay reset')
    check(snapshot()['settings'] == before, 'replayed reset has no side effect')
    raw_request(session, high_water, 'reset')
    wait(lambda s: s['request'] == high_water and s['reply']['stage'] == 'replay', 'used id cannot be reused with different content')
    raw_request(old_session, high_water + 1, 'reset')
    wait(lambda s: s['request_retired'] and s['request'] == high_water + 1, 'old session cannot send a higher reset id')
    command('status')
    check(not snapshot()['request_retired'] and snapshot()['request_ok'] and snapshot()['settings'] == before,
          'new-session status recovers after rejected old-session request')
    capture('restart-persistent')
    # Binding from the external local provider covers the native result route.
    command('fault', 2)
    command('bind', status=1)
    wait(lambda s: s['binding'] == 4, 'binding timeout')
    capture('binding-timeout')
    key('Return')
    wait(lambda s: not s['ui']['boot'] and s['binding'] == 0, 'binding timeout restart')
    command('bind', status=1)
    wait(lambda s: s['binding'] == 2 and s['bound'], 'binding success persisted')
    # Distinct AP01 and TA1208 update state machines: offer/cancel/failure/retry.
    for target, version in ((0, 42), (1, 11)):
        command('charger', 1, status=2)
        command('package', target, version, 1, 0, status=3)
        command('package', 2, version, 0, 0, status=3)
        command('package', target, version, 0, 0, status=2)
        if target == 1:
            go('Settings')
            key('Return')
            key('Right', 4)
            key('Return')
            key('Return')  # native conditional TA1208 update row
        else:
            command('offer', target, status=2)
        wait(lambda s: s['ui']['system'] == 3, 'OTA offer')
        capture(f'ota-{target}-offer')
        key('Left' if target == 1 else 'Right')
        key('Return')
        wait(lambda s: s['ui']['system'] == 0 and s['ota'] == 0, 'OTA offer cancel')
        if target == 1:
            key('Return')
        else:
            command('offer', target, status=2)
        command('fault', 2, status=2)
        key('Return')
        wait(lambda s: s['ota'] == 4 and s['ui']['system'] == 6, 'OTA transfer timeout')
        capture(f'ota-{target}-timeout')
        key('Return')  # default native Retry
        wait(lambda s: s['ota'] == 1 and s['ui']['system'] == 4, 'OTA retry progress')
        command('offer', 1 - target, status=3)
        command('bind', status=3)
        command('check', 1 - target, status=3)
        check(snapshot()['ota_target'] == target and snapshot()['ui']['system'] == 4,
              'concurrent requests cannot replace OTA target or foreground')
        subprocess.run(['xdotool', 'keydown', '--window', wid, 'Return'], env=env, check=True)
        time.sleep(3.3)
        subprocess.run(['xdotool', 'keyup', '--window', wid, 'Return'], env=env, check=True)
        wait(lambda s: s['ota'] == 2, 'OTA unsigned valid package succeeds', 8)
        check(snapshot()['ui']['system'] == 5 and snapshot()['firmware'][target] != version,
              'long press cannot escape or acknowledge OTA success')
        capture(f'ota-{target}-success')
        key('Return')
        wait(lambda s: s['firmware'][target] == version and not s['ui']['boot'], 'OTA restart commits version', 8)
    command('recovery', 1, status=2)
    wait(lambda s: s['ui']['system'] == 9, 'native TA1208 bootloader recovery prompt')
    command('recovery', 0, status=2)
    wait(lambda s: s['ui']['system'] == 0, 'normal device report retires recovery prompt')
    command('recovery', 1, status=2)
    wait(lambda s: s['ui']['system'] == 9, 're-enter remote recovery state')
    command('package', 1, 11, 0, 0, status=2)  # same-version repair is valid only in recovery
    capture('ota-recovery-required')
    key('Right')
    key('Escape')
    check(snapshot()['ui']['system'] == 9, 'OTA recovery prompt only accepts confirm')
    key('Return')
    wait(lambda s: s['ota'] == 2, 'same-version TA1208 recovery succeeds', 8)
    key('Return')
    wait(lambda s: not s['device_recovery'] and not s['ui']['boot'], 'recovery restart clears remote recovery state', 8)
    command('bank', 0, 0, status=2)
    command('bank', 1, 0, status=2)
    command('charger', 0, status=2)
    go('Settings')
    key('Return')
    key('Right', 4)
    key('Return')
    capture('versions-disconnected')
    key('Return')  # only native Back remains when TA1208 absent
    check(snapshot()['mode'] == 1, 'disconnected version page has only Back')
    key('Escape')
    command('wifi', 0, status=2)
    go('Weather')
    capture('weather-network-disconnected')
    check(snapshot()['configured'] and not snapshot()['wifi'], 'configured and online states remain distinct')
    go('Settings')
    key('Return')
    key('Right', 6)
    key('Return')
    capture('factory-reset-confirm')
    key('Left')  # native default is Confirm; choose Cancel explicitly
    key('Return')
    check(snapshot()['configured'], 'factory reset cancel preserves configuration')
    key('Return')
    command('fault', 1, status=2)
    key('Return')
    wait(lambda s: s['ui']['system'] == 7, 'factory reset failure feedback')
    check(snapshot()['configured'], 'factory reset failure rolls back')
    key('Return')
    key('Return')
    wait(lambda s: not s['configured'] and not s['ui']['boot'] and s['ui']['system'] == 0,
         'factory reset commit and reboot', 8)
    check(not snapshot()['bound'] and snapshot()['settings']['guide'] == 0,
          'factory reset clears binding and guide')
    check(snapshot()['firmware'] == [42, 11], 'factory reset preserves installed firmware versions')
    capture('factory-reset-complete')
    runtime_log = LOG.read_text()
    check('glyph dsc. not found' not in runtime_log, 'no missing glyphs in all runtime flows')
    check('[LVGL] [Error]' not in runtime_log and 'PANIC!!!' not in runtime_log, 'no LVGL errors or NuttX panic')
    report['passed'] = True
    report['status'] = 'passed'
except BaseException as exc:
    report['status'] = 'failed'
    report['failure'] = repr(exc)
    if wid and sim and sim.poll() is None:
        capture('failure')
    raise
finally:
    stop()
    if log:
        log.close()
    if xserver:
        xserver.terminate()
        xserver.wait(timeout=5)
    for file in list(ROOT.glob('ap01-sim-state.bin.wifi-*')) + list(ROOT.glob('ap01-sim-state.bin.wapi.conf*')):
        if not file.name.endswith('.acceptance-backup'):
            file.unlink(missing_ok=True)
    for file, saved in wifi_backups:
        saved.rename(file)
    store.unlink(missing_ok=True)
    if backup.exists():
        backup.rename(store)
    report['step_count'] = len(report['steps'])
    if LOG.exists():
        report['log_sha256'] = hashlib.sha256(LOG.read_bytes()).hexdigest()
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(f"COMPLETE SIM PASS: {len(report['steps'])} steps, {len(report['screenshots'])} screenshots")
