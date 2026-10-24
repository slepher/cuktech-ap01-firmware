"""Bounded retained/ROM audit, no target or instruction-model execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
SOURCE = 'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json'
bundle = json.loads((MAIN / SOURCE).read_text(encoding='utf8'))
r = next(x for x in bundle['records'] if x.get('parameters', {}).get('procedure') == '0xa00ad602')
assert r['evidence_id'] == 'ev_9a7754188b853599f5646fcd698e04fa0a888175362857916605f5ae6e3478f0'
assert r['analysis_profile']['digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
assert r['analysis_profile']['parameters']['language_id'] == 'RISCV:LE:32:ap01thead2'
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
BASE = 0x9ffff000
asm = {int(s.split(':')[0], 16): s.split(': ', 1)[1] for s in r['normalized_result']['assembly']}
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []
rows = []
# Sparse necessary state, branch and call slices; no complete body re-export.
spans = [(0xad61e,0xad620),(0xad640,0xad6a4),(0xad6de,0xad6f6),
         (0xad72e,0xad74a),(0xad784,0xad798),(0xad7b4,0xad7c6),
         (0xad7fe,0xad81a),(0xad854,0xad86c),(0xad8a4,0xad8bc),
         (0xad8f6,0xad912),(0xad94e,0xad96c),(0xad998,0xad9c0),
         (0xad9c0,0xad9fc),(0xada28,0xada82),(0xada82,0xadabc)]
norm = lambda m: {'beqz':'beq','bnez':'bne','li':'addi','not':'xori'}.get(m,m)
for lo,hi in spans:
    pc = lo + 0xa0000000
    end = hi + 0xa0000000
    while pc < end:
        half = int.from_bytes(rom[pc-BASE:pc-BASE+2], 'little')
        size = 4 if half & 3 == 3 else 2
        raw = rom[pc-BASE:pc-BASE+size]
        old = asm[pc]
        if pc == 0xa00ad65a:
            w = int.from_bytes(raw, 'little')
            assert raw.hex() == '0b482d81'
            assert [(w >> x) & 31 for x in (7,15,20)] == [16,26,18]
            assert old == 'th.lrbu a6, s10, s2, 0x0'
            decoded = 'private-model indexed unsigned byte load; raw fields rd=a6, base=s10, index=s2'
        else:
            ins = list(cs.disasm(raw, pc))
            assert len(ins) == 1 and ins[0].size == size, (hex(pc), old)
            ins = ins[0]
            assert norm(ins.mnemonic) == norm(old.split()[0]), (hex(pc), ins.mnemonic, old)
            decoded = ins.mnemonic + ' ' + ins.op_str
            if ins.mnemonic in ('jal','beq','bne','beqz','bnez','bltu','bgeu','c.j','c.beqz','c.bnez'):
                target = pc + int(ins.op_str.split(',')[-1],0)
                assert target == int(old.split()[-1],0)
                checks.append({'address':hex(pc),'direct_target':hex(target)})
        rows.append({'address':hex(pc),'bytes':raw.hex(),'retained':old,'local_decode':decoded})
        pc += size
    assert pc == end
anchors = {
0xad61e:'c.lw s1, 0xc, a0',0xad642:'c.lui s4, 0x1',0xad64c:'addi s10, s1, 0x101',
0xad658:'c.li s7, 0x5',0xad674:'andi s3, s3, 0xff',
0xad684:'lbu a5, 0x102, s1',0xad688:'lbu a4, 0x101, s1',
0xad69c:'sb s2, 0xfa, s1',0xad6ee:'sb s2, 0xfa, s1',
0xad742:'sb s2, 0xfa, s1',0xad7be:'sb s2, 0xfa, s1',
0xad812:'sb s2, 0xfa, s1',0xad864:'sb s2, 0xfa, s1',
0xad8b4:'sb s2, 0xfa, s1',0xad90a:'sb s2, 0xfa, s1',
0xad788:'c.li a1, 0x2',0xad78c:'jal ra, 0xa00abbf6',
0xad790:'sb s2, 0xfb, s1',0xad794:'sb zero, 0xf9, s1',
0xad8fa:'c.li a1, 0x4',0xad94e:'addi s4, s4, -0x6f7',
0xad952:'sh s4, 0xfa, s1',0xad962:'lbu a5, 0xf8, s1',
0xad9a6:'lbu a1, 0x101, s1',0xad9bc:'jal ra, 0xa00abbf6',
0xad9de:'sb a5, 0xf8, s1',0xada36:'lbu a1, 0x102, s1',
0xada4c:'jal ra, 0xa00abbf6',0xad9c0:'lw a0, 0xa4, s1',
0xad9d0:'lw a0, 0xc0, s1',0xada50:'lw a0, 0xcc, s1',0xada60:'lw a0, 0xe8, s1'}
for pc, text in anchors.items():
    assert asm[pc+0xa0000000] == text
    assert any(x['address'] == hex(pc+0xa0000000) for x in rows)
    checks.append({'address':hex(pc+0xa0000000),'operand_anchor':text})
assert rom[0xa01c3bd4-BASE:0xa01c3bdc-BASE] == b'C2\0\0C1\0\0'
assert 'unreachable' not in str(r['raw_result']).lower()
result = {'status':'PASS','source':SOURCE,'evidence_id':r['evidence_id'],
          'profile_digest':r['analysis_profile']['digest'], 'checks':checks,'selected_instructions':rows,
          'label_bytes':{'0xa01c3bd4':'43320000','0xa01c3bd8':'43310000'},
          'limits':['No complete callback/body export.','Capstone handles standard instructions only; th.lrbu is raw-field/model-source cross-check, not independent model verification.',
                    'No execution, full dataflow proof, helper abb f6 internals, or complete application lifecycle verification.']}
(HERE/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary={'status':'PASS','selected_bytes':sum(len(bytes.fromhex(x['bytes'])) for x in rows),
         'selected_instructions':len(rows),'checks':len(checks),'spans':len(spans),
         'unreachable_warning_in_this_record':False,'new_function_exports':0}
(HERE/'checks.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
print(summary)
