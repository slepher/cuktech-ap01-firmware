"""Firmware-owned RV32 compilation, auditing and linking for AP01 0041."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT / 'tooling/firmware-modules'
PLATFORM_SOURCES = (
    'native_io_0041.cpp', 'screen_host_0041.c', 'screen_port_0041.cpp',
    'native_vfs_0041.cpp', 'native_calendar_0041.cpp', 'native_runtime_0041.cpp',
    'native_sha256_0041.cpp', 'native_device_code_0041.cpp', 'native_wifi_profiles_0041.cpp',
    'native_wifi_profiles_port_0041.cpp', 'native_diagnostic_0041.cpp', 'native_firmware_0041.cpp',
    'native_ota_image_0041.c', 'native_slot_0041.cpp', 'native_wifi_switch_0041.cpp',
    'native_wifi_switch_port_0041.cpp', 'native_maintenance_0041.cpp', 'native_services_0041.cpp',
    'native_http_transport_0041.cpp', 'native_device_code_font_0041.cpp',
    'native_device_code_menu_0041.cpp', 'native_device_code_hooks_0041.cpp')
FLAGS = ['-march=rv32imafc', '-mabi=ilp32f', '-Os', '-std=c++17', '-ffreestanding', '-fno-builtin',
         '-fno-exceptions', '-fno-rtti', '-fno-pic', '-mno-relax', '-msmall-data-limit=0',
         '-ffunction-sections', '-fdata-sections', '-fstack-usage', '-nostdlib',
         '-DARDUINOJSON_ENABLE_STD_STRING=0', '-DARDUINOJSON_ENABLE_STD_STREAM=0']
FORBIDDEN = ('.data', '.bss', '.sdata', '.sbss', '.got', '.tdata', '.tbss',
             '.init_array', '.fini_array', '.ctors', '.dtors')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def tool_prefix(value=None):
    if value:
        return value
    compiler = shutil.which('riscv32-esp-elf-g++')
    if compiler:
        return compiler[:-len('g++.exe' if compiler.lower().endswith('.exe') else 'g++')]
    if os.environ.get('USERPROFILE'):
        return str(Path(os.environ['USERPROFILE']) / '.platformio/packages/toolchain-riscv32-esp/bin/riscv32-esp-elf-')
    raise ValueError('Supply --tool-prefix /path/to/riscv32-esp-elf-')


def tools(prefix):
    def executable(name):
        path = prefix + name
        return path + '.exe' if Path(path + '.exe').is_file() else path
    return executable


def read_app_config(path):
    path = path.resolve()
    config = json.loads(path.read_text(encoding='utf-8'))
    if config.get('format') != 1 or set(config) - {'format', 'root', 'include_dirs', 'defines', 'plain_sources', 'sources'}:
        raise ValueError('Unsupported App source configuration')
    app = (path.parent / config['root']).resolve()
    for key in ('include_dirs', 'plain_sources', 'sources'):
        paths = [(app / p).resolve() for p in config[key]]
        if any(not p.is_relative_to(app) or not p.exists() for p in paths):
            raise ValueError('App paths must exist within its source root: ' + key)
        config[key] = paths
    if any(not isinstance(d, str) or not d or d.startswith('-') for d in config['defines']):
        raise ValueError('App defines must be macro names/values')
    config['path'] = path
    return config


def audit(out, prefix, app_config=None, screen_host_probe=False, json_header=None):
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    executable = tools(prefix)
    config = read_app_config(app_config) if app_config else None
    if screen_host_probe and not config:
        raise ValueError('--screen-host-probe requires an App configuration')
    json_header = (json_header or ROOT / 'tooling/vendor/ArduinoJson/src').resolve()
    if not (json_header / 'ArduinoJson.h').is_file():
        raise ValueError('ArduinoJson src directory required')
    includes = [MODULES, json_header] + (config['include_dirs'] if config else [])
    sources = [MODULES / name for name in PLATFORM_SOURCES]
    sources += config['plain_sources'] + config['sources'] if config else [MODULES / 'native_platform_0041.cpp']
    if screen_host_probe:
        sources.append(MODULES / 'test_screen_peer_0041.cpp')
    if len({p.stem for p in sources}) != len(sources):
        raise ValueError('Source object names must be unique')
    flags = FLAGS + ['-I' + str(p) for p in includes]
    headers = sorted({p for directory in includes for p in directory.rglob('*')
                      if p.is_file() and p.suffix in ('.h', '.hpp', '.inc')})
    report = {'passed': False, 'scope': 'firmware-owned RV32 audit; execution verified separately',
              'runtime': 'application' if config else 'platform', 'firmware_target': 'cuktech-ap01-0041',
              'flashable': False, 'hardware_verified': False, 'flags': flags, 'objects': [],
              'compiler': subprocess.check_output([executable('g++'), '--version'], text=True).splitlines()[0],
              'generator_sha256': sha(Path(__file__)),
              'input_headers': [{'path': str(p), 'sha256': sha(p)} for p in headers]}
    if config:
        report['app_config'] = {'path': str(config['path']), 'sha256': sha(config['path'])}
    write_json(out / 'native-core-audit.json', report)
    write_json(out / 'native-link-report.json', {'linked': False, 'flashable': False})
    for source in sources:
        obj = out / (source.stem + '.o')
        plain = config and source in config['plain_sources']
        source_flags = flags + ['-DARDUINOJSON_ENABLE_ARDUINO_STRING=' + ('0' if plain else '1')]
        if config and not plain:
            source_flags += ['-D' + d for d in config['defines']]
        if screen_host_probe:
            source_flags += ['-DAP01_SCREEN_HOST_PROBE=1']
        c = source.suffix == '.c'
        if c:
            source_flags = [f.replace('c++17', 'c11') for f in source_flags
                            if f not in ('-fno-exceptions', '-fno-rtti')]
        subprocess.run([executable('gcc' if c else 'g++'), *source_flags, '-c', str(source), '-o', str(obj)], check=True)
        sizes = subprocess.check_output([executable('size'), '-A', str(obj)], text=True)
        sections = []
        for line in sizes.splitlines():
            fields = line.split()
            if len(fields) == 3 and fields[0].startswith('.'):
                name, size = fields[0], int(fields[1])
                sections.append({'name': name, 'bytes': size})
                if size and name.startswith(FORBIDDEN):
                    raise ValueError('XIP writable state or implicit initializer: ' + name)
        report['objects'].append({'file': str(obj), 'source': str(source), 'source_sha256': sha(source),
            'sha256': sha(obj), 'bytes': obj.stat().st_size, 'flags': source_flags, 'sections': sections,
            'undefined_imports': subprocess.check_output([executable('nm'), '-u', str(obj)], text=True).splitlines(),
            'stack': obj.with_suffix('.su').read_text().splitlines()})
    collect_budgets(out, executable, report, bool(config))
    partial = out / 'ap01-shared-core.o'
    subprocess.run([executable('ld'), '-r', *[r['file'] for r in report['objects']], '-o', str(partial)], check=True)
    report['combined'] = {'path': str(partial), 'sha256': sha(partial), 'bytes': partial.stat().st_size,
        'undefined_imports': subprocess.check_output([executable('nm'), '-u', str(partial)], text=True).splitlines()}
    report['passed'] = True
    write_json(out / 'native-core-audit.json', report)
    return report


def validate_audit(out):
    report = json.loads((out / 'native-core-audit.json').read_text(encoding='utf-8'))
    if not report.get('passed'):
        raise ValueError('Native audit did not pass')
    for item in report['objects']:
        if sha(Path(item['source'])) != item['source_sha256'] or sha(Path(item['file'])) != item['sha256']:
            raise ValueError('Source/object changed: rerun audit')
    for item in report['input_headers'] + ([report['app_config']] if 'app_config' in report else []):
        if sha(Path(item['path'])) != item['sha256']:
            raise ValueError('Header/App configuration changed: rerun audit')
    return report


def link(out, prefix):
    out = out.resolve()
    write_json(out / 'native-link-report.json', {'linked': False, 'flashable': False})
    report = validate_audit(out)
    executable = tools(prefix)
    elf = out / 'ap01-native-0041.elf'
    script = MODULES / 'native_application_0041.ld'
    command = [executable('g++'), '-march=rv32imafc', '-mabi=ilp32f', '-nostdlib', '-mno-relax',
        '-Wl,--no-relax,--gc-sections', '-Wl,-T,' + str(script), '-Wl,-Map,' + str(out / 'ap01-native-0041.map'),
        *[r['file'] for r in report['objects'] if Path(r['file']).name != 'abi_budget.o'],
        '-Wl,--start-group', '-lm', '-lgcc', '-Wl,--end-group', '-o', str(elf)]
    subprocess.run(command, check=True)
    undefined = subprocess.check_output([executable('nm'), '-u', str(elf)], text=True).strip()
    if undefined:
        raise ValueError('Unresolved imports: ' + undefined)
    module = out / 'ap01-native-0041.module.bin'
    subprocess.run([executable('objcopy'), '-O', 'binary', str(elf), str(module)], check=True)
    linked = {'linked': True, 'flashable': False, 'runtime': report['runtime'],
        'audit_sha256': sha(out / 'native-core-audit.json'), 'module_sha256': sha(module), 'command': command,
        'linker_script': {'path': str(script), 'sha256': sha(script)},
        'elf': {'path': str(elf), 'bytes': elf.stat().st_size, 'sha256': sha(elf)},
        'sections': subprocess.check_output([executable('size'), '-A', str(elf)], text=True), 'undefined_imports': undefined}
    write_json(out / 'native-link-report.json', linked)
    return linked

def collect_budgets(out, executable, report, application):
    budget_file=out/'abi-budget.bin'
    report['budget']={}
    if application:
        subprocess.run([executable('objcopy'),'-O','binary','--only-section=.ap01_budget',
                        str(out/'abi_budget.o'),str(budget_file)],check=True)
        pointer,state,record,count,header,maximum,frame=struct.unpack('<7I',budget_file.read_bytes())
        assert pointer==4
        report['budget']={'state_heap_bytes':state,'record_heap_bytes':record,'bindings_max':count,
                          'frame_bytes':frame,'persistent_empty_bytes':header,
                          'persistent_single_typical_bytes':header+5+16+16+4+32+32,
                          'persistent_eight_typical_bytes':header+8*(5+16+16+4+32+32),
                          'persistent_single_max_bytes':header+maximum,'persistent_eight_max_bytes':header+8*maximum,
                          'commit_heap_max_bytes':state+2*count*record+header+count*maximum,
                          'limitations':'allocator overhead, JSON/UI/Bundle allocations and native calling chains require separate audit'}
        subprocess.run([executable('objcopy'),'-O','binary','--only-section=.ap01_render_budget',
                        str(out/'abi_budget.o'),str(budget_file)],check=True)
        paint,renderer,compiled = struct.unpack('<3I', budget_file.read_bytes())
        report['budget'].update({'paint_state_bytes':paint,'renderer_state_bytes':renderer,
                                'compiled_template_bytes':compiled})
    subprocess.run([executable('objcopy'),'-O','binary','--only-section=.ap01_firmware_budget',
                    str(out/'native_firmware_0041.o'),str(budget_file)],check=True)
    firmware,transaction,body,headers,receipt,scratch=struct.unpack('<6I',budget_file.read_bytes())
    report['budget']['firmware']={'service_bytes':firmware,'transaction_bytes':transaction,
        'max_chunk_heap_bytes':body,'http_header_and_small_body_heap_bytes':headers,
        'max_persistent_record_bytes':receipt,'max_pending_plus_record_bytes':receipt*2,
        'native_write_scratch_stack_bytes':scratch}
    subprocess.run([executable('objcopy'),'-O','binary','--only-section=.ap01_platform_budget',
                    str(out/'native_services_0041.o'),str(budget_file)],check=True)
    service_state,maintenance,service_handle,wifi_switch,filesystem=struct.unpack('<5I',budget_file.read_bytes())
    report['budget']['platform_services']={'state_bytes':service_state,'maintenance_bytes':maintenance,
        'app_handle_bytes':service_handle,'wifi_switch_bytes':wifi_switch,'filesystem_bytes':filesystem,
        'additional_threads':0,'maintenance_stack_bytes':16384,'persistent_format_changes':False}
    subprocess.run([executable('objcopy'),'-O','binary','--only-section=.ap01_menu_budget',
                    str(out/'native_device_code_menu_0041.o'),str(budget_file)],check=True)
    menu_context,ssid_row,list_snapshot,max_rows=struct.unpack('<4I',budget_file.read_bytes())
    subprocess.run([executable('objcopy'),'-O','binary','--only-section=.ap01_wifi_switch_budget',
                    str(out/'native_wifi_switch_0041.o'),str(budget_file)],check=True)
    switch_owner,switch_attempt=struct.unpack('<2I',budget_file.read_bytes())
    report['budget']['wifi_menu']={'context_bytes':menu_context,'ssid_row_bytes':ssid_row,
        'rows_empty_single_typical_max_bytes':[0,ssid_row,3*ssid_row,max_rows*ssid_row],
        'temporary_list_snapshot_bytes':list_snapshot,'switch_owner_bytes':switch_owner,
        'switch_attempt_bytes':switch_attempt,'max_rollback_plain_bytes':106,
        'max_encrypted_journal_bytes':112,'max_pending_plus_journal_bytes':224,
        'added_threads':0,'limits':'allocator/widget/font-cache overhead and original ROM call-chain stack require separate accounting'}
