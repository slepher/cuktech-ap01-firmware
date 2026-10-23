"""Bounded ROM/text checks only; never executes target or analyzer models."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
def raw(pc, n):
    return rom[pc-BASE:pc-BASE+n]
def sx(v, bits):
    return (v ^ (1 << (bits-1))) - (1 << (bits-1))
def target(pc):
    w = int.from_bytes(raw(pc, 4), 'little')
    if w & 127 == 0x6f:
        v = ((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        return (pc + sx(v, 21)) & 0xffffffff
    q = int.from_bytes(raw(pc+4, 4), 'little')
    assert w & 0xfff == 0x97 and q & 0xfffff == 0x80e7
    return (pc + sx(w & 0xfffff000, 32) + sx(q>>20, 12)) & 0xfffffffe

calls = [(0xa005a822,0xa0098b60), (0xa005c174,0xa0098b60),
         (0xa005c17a,0xa009d304), (0xa005c814,0xa0098b60),
         (0xa005c81a,0xa009d304), (0xa0098b6c,0xa019e1a2),
         (0xa0098b7e,0xa001b302), (0xa019e1b0,0xa002696a),
         (0xa019e1c8,0xa0019672), (0xa0026984,0xa002645a)]
for pc, expected in calls:
    assert target(pc) == expected, (hex(pc), hex(target(pc)))

windows = []
for name, first, end in [
    ('new_writer',0xa0098b60,0xa0098b94),
    ('new_source_wrapper',0xa019e1a2,0xa019e1f2),
    ('selector1_direct_branch',0xa0026974,0xa002699c),
    ('selector1_success_return',0xa00269f0,0xa00269fc),
    ('retained_refresh_before_dispatch',0xa005c172,0xa005c17e),
    ('division_entry_only',0xa001b302,0xa001b322),
    ('division_digit_instructions_only',0xa001b356,0xa001b372),
    ('division_pair_return_only',0xa001b50e,0xa001b518),
]:
    pc = first
    insns = []
    while pc < end:
        n = 4 if raw(pc,1)[0] & 3 == 3 else 2
        b = raw(pc,n)
        i = next(md.disasm(b,pc),None)
        if pc == 0xa019e1ea:
            assert b.hex() == '7715f7a4'
            asm = 'UMAR64 existing rule; fields checked separately'
        else:
            assert i and i.size == n, (hex(pc),b.hex())
            asm = i.mnemonic + ' ' + i.op_str
        insns.append(dict(pc=hex(pc),bytes=b.hex(),asm=asm))
        pc += n
    assert pc == end
    windows.append(dict(name=name,start=hex(first),end_exclusive=hex(end),instructions=insns))

w = int.from_bytes(raw(0xa019e1ea,4),'little')
fields = dict(op=w&127,f3=(w>>12)&7,f7=w>>25,rd=(w>>7)&31,rs1=(w>>15)&31,rs2=(w>>20)&31)
assert fields == dict(op=0x77,f3=1,f7=0x52,rd=10,rs1=14,rs2=15)
patch = (TREE / 'tooling/scripts/qemu-ap01-cpu.patch').read_text()
for text in ['ap01_umar64 1010010 ..... ..... 001 ..... 1110111 @r',
             'int rd = a->rd & ~1;', 'tcg_gen_mulu2_i32(pl, ph, left, right);',
             'tcg_gen_add2_i32(low, high, al, ah, pl, ph);']:
    assert text in patch

old = json.loads((TREE / 'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
assert old['address'] == '0xa005a736'
anchors = [x for x in old['assembly'] if any(hex(pc) in x for pc in [0xa005a822,0xa005c174,0xa005c17a,0xa005c814,0xa005c81a])]
assert len(anchors) == 5
# Later round3 reuse is examined for these exact procedure bodies, not full-ROM field scans.
p = MAIN / 'evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json'
j = json.loads(p.read_text())
found = {}
def walk(v, pointer=''):
    if isinstance(v,dict):
        if v.get('address') in ['0xa0098b60','0xa019e1a2'] and 'body' in v:
            found.setdefault(v['address'],dict(address=v['address'],body=v['body'],first_pointer=pointer))
        for k,x in v.items(): walk(x,pointer+'/'+k)
    elif isinstance(v,list):
        for k,x in enumerate(v): walk(x,pointer+'/'+str(k))
walk(j)
result = dict(task='E16',result='PASS',calls=[dict(pc=hex(a),target=hex(b)) for a,b in calls],
              windows=windows,umar64_fields=fields,
              retained_initializer=dict(evidence_id=old['evidence_id'],anchors=anchors),
              round3_scope=str(p),round3_callee_boundary_metadata=list(found.values()),
              limits=['No target/model execution or new REA session.',
                      'Division helper sparse observations support inference, not complete algorithm authentication.',
                      'a002645a output semantics, clock origin, units and epoch not established.'])
(HERE / 'verification.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('PASS: 10 exact call targets, UMAR64 fields, 8 bounded windows, 5 retained caller anchors; round3 exact bodies',len(found))
