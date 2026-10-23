"""F01 bounded static ROM evidence; no target execution, REA state or model edits."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, __version__

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
initializer = json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
prior = json.loads((ROOT/'reverse/analysis/miio-deferred-settings-0041-20261023/retained-functions.json').read_text())['functions']
for f in [initializer] + prior:
    for r in f['raw_ranges']:
        a = int(r['start'], 16)
        data = bytes.fromhex(r['hex'])
        assert rom[a-BASE:a-BASE+len(data)] == data

specs = [
 ('outer_loop_binding',0xa005a76e,0xa005a79a),
 ('shared_init',0xa005ac04,0xa005ac38),
 ('timer_init',0xa009d106,0xa009d146),
 ('timer_start',0xa009d146,0xa009d286),
 ('submission',0xa009d286,0xa009d304),
 ('due_dispatch',0xa009d304,0xa009d382),
 ('int_brightness',0xa009dac0,0xa009dae2),
 ('int_mode',0xa009de14,0xa009de38),
 ('string_location',0xa00a0f10,0xa00a0f5e),
 ('callback',0xa00a0bd8,0xa00a0e78),
 ('weather_bridge',0xa00a5b90,0xa00a5bbe),
 ('stop_prefix',0xa01b2b5c,0xa01b2bb2),
 ('loop_dispatch_caller',0xa005c80e,0xa005c83a),
 ('miio_deinit',0xa005c9ea,0xa005ca9a)]
windows = []
slots = {}
for name,a,b in specs:
    pc = a
    instructions=[]
    while pc < b:
        size = 4 if rom[pc-BASE]&3 == 3 else 2
        raw = rom[pc-BASE:pc-BASE+size]
        i=next(md.disasm(raw,pc),None)
        line=dict(pc=hex(pc),hex=raw.hex(),assembly=i.mnemonic+' '+i.op_str if i else 'UNKNOWN; raw preserved, semantics not assigned')
        instructions.append(line); slots[pc]=line
        pc+=size
    assert pc==b
    windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),instructions=instructions))

checks=[]
def exact(pc, value):
    actual=slots[pc]['hex']; assert actual==value,(hex(pc),actual,value)
    checks.append(dict(pc=hex(pc),hex=actual,kind='independently selected exact opcode'))
for pc,h in [(0xa009d10e,'2384f500'),(0xa009d130,'23a40502'),
             (0xa009d1a0,'23a83403'),(0xa009d1a8,'23a46405'),
             (0xa009d2b4,'23249542'),(0xa00a0bf0,'032a0500'),
             (0xa00a0bfc,'83470a00'),(0xa00a0c00,'03284a00'),
             (0xa00a0c20,'83470a00'),(0xa00a0cd4,'23a00a00'),
             (0xa009d36a,'83a7c4ff'),(0xa009d36e,'4a85'),(0xa009d370,'8297')]:
    exact(pc,h)
def sext(v,n): return (v^(1<<(n-1)))-(1<<(n-1))
def call(pc,target):
    w=int.from_bytes(rom[pc-BASE:pc-BASE+4],'little')
    if w&127==0x6f:
        imm=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
        actual=(pc+sext(imm,21))&0xffffffff
    else:
        v=int.from_bytes(rom[pc+4-BASE:pc+8-BASE],'little')
        assert w&0xfff==0x97 and v&0xfffff==0x80e7
        actual=(pc+sext(w&0xfffff000,32)+sext(v>>20,12))&0xfffffffe
    assert actual==target,(hex(pc),hex(actual),hex(target))
    checks.append(dict(pc=hex(pc),target=hex(target),kind='decoded direct call'))
for pc,target in [(0xa005ac0e,0xa009d106),(0xa009d2c8,0xa009d146),
                  (0xa009d29a,0xa002fcc8),(0xa009d2f4,0xa002e14e),
                  (0xa00a0cd0,0xa002e14e),(0xa009d338,0xa01b2b5c),
                  (0xa009d350,0xa01b2b5c),(0xa009d366,0xa009d146),
                  (0xa005c81a,0xa009d304),(0xa005ca12,0xa01b2b5c),
                  (0xa005ca22,0xa01b2b5c),(0xa005ca32,0xa01b2cb0),
                  (0xa005ca44,0xa009fb96),(0xa009dacc,0xa009d286),
                  (0xa009de26,0xa009d286),(0xa00a0f32,0xa009d286),
                  (0xa00a5ba0,0xa01b2b5c),(0xa00a5bae,0xa01b24c0)]: call(pc,target)

# Check that s1 stays the outer argument through this local initialization prefix.
binding=[s for s in initializer['assembly'] if 0xa005a736<=int(s.split(':')[0],16)<0xa005ac38 and s.split(': ')[1].split(' ')[1].rstrip(',')=='s1']
assert binding==['0xa005a73c: sw s1, 0x184, sp','0xa005a77a: c.mv s1, a0','0xa005a8cc: sw s1, 0x17c, s1']
out=dict(task='F01',capstone=__version__,method='read-only original ROM and retained REA records; no shared active session',
 sources=[dict(path='reverse/analysis/factory-test-0041-20261023/retained-initializer.json',evidence_id=initializer['evidence_id'],profile=initializer['profile']['digest'])]+[dict(path='reverse/analysis/miio-deferred-settings-0041-20261023/retained-functions.json',procedure=f['normalized_result']['procedure']['address'],evidence_id=f['evidence_id'],profile=f['profile']['digest']) for f in prior],
 windows=windows,checks=checks,outer_loop_s1_mentions=binding,
 limits=['Start arithmetic vendor instructions at a009d18c/a009d1bc retained without semantic claims.', 'No complete generic timer heap or library provenance recovery.', 'MiIO deinit window is a local bounded negative result, not all-ROM no-destroy proof.', 'Prior retained complete function bytes matched; unrelated property branches not semantically reviewed.'])
(HERE/'instruction-evidence.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print('PASS',len(checks),'checks;',len(windows),'windows;',sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),'bytes; unknown slots', [i['pc'] for w in windows for i in w['instructions'] if i['assembly'].startswith('UNKNOWN')])
