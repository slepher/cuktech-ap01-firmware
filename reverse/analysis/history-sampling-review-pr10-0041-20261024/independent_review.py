"""P-R10 offline checks. Standard library only; never imports author verification."""
import datetime
import json
import pathlib
import struct

ROOT = pathlib.Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = pathlib.Path(__file__).resolve().parent
BASE = 0x9ffff000
def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))
rom = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
checks = []
def check(name, ok, detail=None):
    checks.append({'check': name, 'pass': bool(ok), 'detail': detail})
    assert ok, name
def data(address, size):
    with rom.open('rb') as stream:
        stream.seek(address - BASE)
        value = stream.read(size)
    assert len(value) == size
    return value
check('original length against CATALOG', rom.stat().st_size == 6769704)
dock = read('reverse/analysis/dock-presence-polling-0041-20261023/instruction-windows.json')
dispatcher = next(f for f in read('reverse/analysis/buzzer-backlight-0041-20261023.json')['functions'] if f['address'] == '0xa00a8582')
author = read('reverse/analysis/history-sampling-p10-0041-20261024/static-evidence.json')
retained = read('reverse/analysis/dock-presence-polling-0041-20261023/retained-functions.json')['functions'][1]
helper = read('reverse/analysis/uart-response-0041-20261023.json')['functions'][1]
sources = []
for label, entry, expected_id, language, digest in [
    ('timer', retained, 'ev_5fd69f489ac24670f4c858f79225e681a50079c28b088bb18e6f7b999de4fa59', 'RISCV:LE:32:ap01thead2', 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'),
    ('helper', helper, 'ev_3a861f94ddb2b4481b6d96b4f46d593f35e2729ecb9022aa64949e92b607615c', 'RISCV:LE:32:ap01thead2', 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'),
    ('dispatcher', dispatcher, 'ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c', 'RISCV:LE:32:ap01thead3', 'bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279'),
]:
    check(label + ' Evidence identity', entry['evidence_id'] == expected_id)
    profile = entry.get('profile')
    if profile:
        check(label + ' profile', profile['parameters']['language_id'] == language and profile['digest'] == digest)
    else:
        check(label + ' retained profile digest', entry['profile_digest'] == digest)
        original = read(entry['source']['path'])['structuredContent']
        check(label + ' original profile and Evidence', original['evidence_id'] == expected_id and original['analysis_profile']['digest'] == digest and original['analysis_profile']['parameters']['language_id'] == language and original['provider']['version'] == '12.1.4')
    sources.append({'role': label, 'source': entry['source'], 'evidence_id': entry['evidence_id'], 'language': language, 'digest': digest, 'language_basis': 'direct profile' if profile else 'directly verified original structuredContent analysis_profile; retained entry stores digest only'})
check('old dock decoder identity', dock['engine'] == [5, 0, 1280])
registration = read('reverse/analysis/dock-presence-polling-0041-20261023/timer-registration-source.json')
check('timer registration profile differs from timer callback', registration['profile']['digest'] == dispatcher['profile']['digest'] and registration['profile']['parameters']['language_id'] == 'RISCV:LE:32:ap01thead3')
windows = []
for window in author['windows']:
    start, end = int(window['start'], 16), int(window['end_exclusive'], 16)
    raw = data(start, end-start)
    check(window['name'] + ' author byte equality', raw.hex() == window['hex'])
    old = next((w for w in dock['windows'] if int(w['start'],16) <= start and end <= int(w['end_exclusive'],16)), None)
    if old:
        old_bytes = bytes.fromhex(old['hex'])[start-int(old['start'],16):end-int(old['start'],16)]
        old_rows = [r for r in old['instructions'] if start <= int(r['address'],16) < end]
        check(window['name'] + ' direct old rows', old_rows == window['instructions'])
    else:
        prior = next(r for r in dispatcher['raw_ranges'] if int(r['start'],16) <= start and end-1 <= int(r['end'],16))
        old_bytes = bytes.fromhex(prior['hex'])[start-int(prior['start'],16):end-int(prior['start'],16)]
        old_rows = [line for line in dispatcher['assembly'] if start <= int(line.split(':')[0],16) < end]
        check(window['name'] + ' direct old assembly', old_rows == [r['address'] + ': ' + r['assembly'] for r in window['instructions']])
    check(window['name'] + ' direct old raw bytes', old_bytes == raw)
    cursor = start
    for row in window['instructions']:
        check(row['address'] + ' length and row bytes', int(row['address'],16) == cursor and data(cursor,len(bytes.fromhex(row['hex']))).hex() == row['hex'] and len(bytes.fromhex(row['hex'])) == (4 if int.from_bytes(data(cursor,2),'little') & 3 == 3 else 2))
        cursor += len(bytes.fromhex(row['hex']))
    check(window['name'] + ' window endpoint', cursor == end)
    windows.append({'name':window['name'],'start':window['start'],'end_exclusive':window['end_exclusive'],'bytes':len(raw),'rows':len(window['instructions'])})
table = data(0xa0004634, 32)
check('direct default table', table.hex() == '384bfc62010100003c4bfc62040a0000204bfc620a0002005800000050515759')
check('default group fields', struct.unpack_from('<IBBBB',table,0) == (0x62fc4b38,1,1,0,0) and struct.unpack_from('<IBBBB',table,8) == (0x62fc4b3c,4,10,0,0))
check('default controller fields', struct.unpack_from('<IBBBB',table,16) == (0x62fc4b20,10,0,2,0))
def word(address): return int.from_bytes(data(address,4),'little')
def sext(value,bits): return value - (1<<bits) if value & (1<<(bits-1)) else value
def jal(address,target):
    w=word(address)
    offset=sext(((w>>31)&1)<<20 | ((w>>12)&255)<<12 | ((w>>20)&1)<<11 | ((w>>21)&1023)<<1,21)
    check(hex(address)+' independent JAL target', w&127 == 0x6f and address+offset == target, hex(address+offset))
for address,target in [(0xa00a8b8c,0xa0191652),(0xa00a8780,0xa0191652),(0xa00a92a0,0xa00a398c),(0xa00a8c1a,0xa00a398c),(0xa01917b6,0xa01951e2),(0xa00a82ee,0xa0191746)]: jal(address,target)
def load(address,rd,rs,imm,width):
    w=word(address)
    check(hex(address)+' independent load fields', (w&127,(w>>7)&31,(w>>15)&31,sext(w>>20,12),(w>>12)&7)==(3,rd,rs,imm,width))
for args in [(0xa00a9298,11,26,8,5),(0xa00a8c14,11,10,4,5),(0xa00a82ca,14,14,7,4),(0xa00a82d4,14,15,5,4),(0xa01917ba,15,9,6,4)]: load(*args)
def store(address,rs,base,imm,width):
    w=word(address)
    offset=sext(((w>>25)<<5)|((w>>7)&31),12)
    check(hex(address)+' independent store fields',(w&127,(w>>20)&31,(w>>15)&31,offset,(w>>12)&7)==(0x23,rs,base,imm,width))
for args in [(0xa00a82da,0,15,7,0),(0xa00a82e0,14,15,5,0),(0xa019168e,15,13,7,0),(0xa00a878e,0,15,-0x4cb,0),(0xa01917c2,15,9,6,0)]: store(*args)
def branch(address,target):
    w=word(address)
    offset=sext(((w>>31)&1)<<12|((w>>7)&1)<<11|((w>>25)&63)<<5|((w>>8)&15)<<1,13)
    check(hex(address)+' independent branch', w&127 == 0x63 and address+offset==target,hex(address+offset))
for args in [(0xa00a8bb4,0xa00a8aae),(0xa00a8bd8,0xa00a8c10),(0xa00a939c,0xa00a8aae),(0xa019179c,0xa019176a)]: branch(*args)
check('cmd50 byte-count truncation instruction', word(0xa00a8b88) == 0x0f85f593)
check('cmd50 helper return falls through to factory gate, no a0 branch', word(0xa00a8b90) == 0x62fcbbb7 and word(0xa00a8b94) == 0x6b0ba783)
check('sample caller input offsets are scalar and history object differs', word(0xa00a929c) == 0x03cd0513 and data(0xa00a8c18,2).hex() == '3905')
check('0x400 follows history call, not a prerequisite', word(0xa00a92a6) == 0x400cec93 and word(0xa00a8c22) == 0x4009e993)
result={'claim':'P-R10','observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authority':'independent stdlib original-byte/old-source/field checks; not new REA Evidence or execution','sources':sources,'windows':windows,'window_bytes':sum(w['bytes'] for w in windows),'rows':sum(w['rows'] for w in windows),'table_hex':table.hex(),'checks':checks,'pass_count':len(checks),'limitations':['No vendor ISA reimplementation, target/model execution, graph-reader analysis or public library analysis.','Byte and local field equality is not complete control/data flow proof; static manual composition retains independently accepted contracts.','Original provider bad-flow/truncation limitations remain inherited.']}
(OUT/'independent-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pass_count':len(checks),'window_bytes':result['window_bytes'],'rows':result['rows']}))
