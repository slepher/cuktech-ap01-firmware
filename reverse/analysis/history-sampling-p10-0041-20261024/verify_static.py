"""P-10: retained-window/ROM consistency only; no emulation or target execution."""
import json
import pathlib
import datetime

ROOT = pathlib.Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = pathlib.Path(__file__).resolve().parent
BASE = 0x9ffff000

def read(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

dock_path = 'reverse/analysis/dock-presence-polling-0041-20261023/instruction-windows.json'
dock = read(dock_path)
disp_path = 'reverse/analysis/buzzer-backlight-0041-20261023.json'
disp = next(f for f in read(disp_path)['functions'] if f.get('address') == '0xa00a8582')
raw = disp['raw_ranges'][0]
raw_start = int(raw['start'], 16)
raw_bytes = bytes.fromhex(raw['hex'])
assembly = {int(s.split(':')[0], 16): s.split(':', 1)[1].strip() for s in disp['assembly']}
windows = []
checks = []

with (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').open('rb') as rom:
    def window(name, start, end, inherited):
        rom.seek(start - BASE)
        actual = rom.read(end - start)
        expected = bytes.fromhex(inherited['hex'])
        assert actual == expected, name
        cursor = 0
        lengths = []
        while cursor < len(actual):
            half = int.from_bytes(actual[cursor:cursor + 2], 'little')
            size = 2 if half & 3 != 3 else 4
            assert cursor + size <= len(actual), name
            lengths.append((start + cursor, size))
            cursor += size
        inherited_addresses = [int(i['address'], 16) for i in inherited['instructions']]
        assert inherited_addresses == [a for a, _ in lengths], name
        checks.append({'check': name + ': retained bytes and independent length boundaries', 'pass': True})
        windows.append({'name': name, 'start': hex(start), 'end_exclusive': hex(end),
                        'file_offset': start - BASE, 'hex': actual.hex(),
                        'source': inherited['source'], 'instructions': inherited['instructions']})

    for name, start, end in [
        ('timer_presence_stage', 0xa00a80a8, 0xa00a80ca),
        ('timer_round_completion', 0xa00a82be, 0xa00a82f2),
        ('timer_sent_reset', 0xa00a830a, 0xa00a831a),
        ('cache_completion', 0xa0191652, 0xa0191700),
        ('selector', 0xa0191746, 0xa01917d0),
        ('timer_registration', 0xa005ab4c, 0xa005ab64),
    ]:
        w = next(w for w in dock['windows'] if int(w['start'], 16) <= start and int(w['end_exclusive'], 16) >= end)
        offset = start - int(w['start'], 16)
        window(name, start, end, {'hex': bytes.fromhex(w['hex'])[offset:offset + end-start].hex(),
            'source': dock_path + '#windows[name=' + w['name'] + ']',
            'instructions': [i for i in w['instructions'] if start <= int(i['address'],16) < end]})

    for name, start, end in [
        ('cmd50_gate', 0xa00a8b72, 0xa00a8bc0),
        ('cmd50_total_tail', 0xa00a8bcc, 0xa00a8c58),
        ('item_history_gate', 0xa00a9290, 0xa00a92ae),
        ('history_skip_tails', 0xa00a937a, 0xa00a93a4),
        ('cmd58_phase_reset', 0xa00a876e, 0xa00a8794),
    ]:
        data = raw_bytes[start-raw_start:end-raw_start]
        insns = []
        addresses = sorted(a for a in assembly if start <= a < end)
        for index, a in enumerate(addresses):
            next_a = addresses[index + 1] if index + 1 < len(addresses) else end
            insns.append({'address': hex(a), 'hex': raw_bytes[a-raw_start:next_a-raw_start].hex(), 'assembly': assembly[a]})
        window(name, start, end, {'hex': data.hex(), 'instructions': insns,
            'source': disp_path + '#functions[address=0xa00a8582], ' + disp['evidence_id']})

    initial = read('reverse/analysis/dock-presence-polling-0041-20261023/poll-initializers.json')['regions'][0]
    rom.seek(initial['file_offset'])
    table = rom.read(len(bytes.fromhex(initial['hex'])))
    assert table == bytes.fromhex(initial['hex'])
    assert table[4:7] == bytes([1,1,0]) and table[12:15] == bytes([4,10,0])
    assert table[24] == 0x58 and table[28:32] == bytes([0x50,0x51,0x57,0x59])
    checks.append({'check': 'default table ROM bytes / priorities / periods / command order', 'pass': True})

# Exact retained instruction contracts: assertions concern text plus the checked original bytes.
for address, needle in {
    0xa00a8b8c: '0xa0191652', 0xa00a8bb4: '0xa00a8aae',
    0xa00a8bd8: '0xa00a8c10', 0xa00a8c14: 'lhu a1, 0x4, a0',
    0xa00a8c1a: '0xa00a398c', 0xa00a8c52: '0xa00a536c',
    0xa00a9298: 'lhu a1, 0x8, s10', 0xa00a92a0: '0xa00a398c',
    0xa00a939c: '0xa00a8aae',
}.items():
    assert needle in assembly[address], (hex(address), needle)
    checks.append({'check': hex(address) + ': ' + needle, 'pass': True})

result = {'claim': 'P-10', 'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'authority': 'offline original-byte consistency and static retained-instruction reading; not new REA Evidence',
    'target_sha256_inherited': dock['rom_sha256'], 'mapping': 'VA - 0x9ffff000',
    'new_target_execution': False, 'model_execution': False, 'shared_rea_access': False,
    'source_profile_note': 'dock windows are prior static decoder rows; dispatcher is original thead3 dossier; do not relabel either as a new observation',
    'dispatcher_source': {k: disp[k] for k in ['evidence_id','source','profile']},
    'checks': checks, 'windows': windows, 'window_bytes': sum(len(bytes.fromhex(w['hex'])) for w in windows),
    'instruction_rows': sum(len(w['instructions']) for w in windows),
    'limitations': ['Original vendor instruction semantics inherited, not reimplemented or executed.',
        'No dynamic request count, timer delivery, wall-clock sampling interval or peripheral capture.',
        'Byte/length checks do not prove complete control/data flow or all global writers.']}
(OUT / 'static-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k:result[k] for k in ['claim','window_bytes','instruction_rows']}))
print('checks', len(checks), 'PASS')
