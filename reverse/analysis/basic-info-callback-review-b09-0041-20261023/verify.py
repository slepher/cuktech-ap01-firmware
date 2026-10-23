"""B09 independent static review. Reads ROM; never executes target instructions."""
from pathlib import Path
import json
import sys
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROM_ROOT = Path(sys.argv[1])
ROM = ROM_ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
rom = ROM.read_bytes()
prior = json.loads((HERE.parent / 'basic-info-callback-b08-0041-20261023/instruction-evidence.json').read_text())
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
words = {}
checks = []

def check(label, actual, expected):
    assert actual == expected, (label, actual, expected)
    checks.append({'check': label, 'observed': actual})

ordinary = 0
for window in prior['windows']:
    cursor = int(window['start'], 16)
    for row in window['instructions']:
        address = int(row['address'], 16)
        assert address == cursor
        pos = address - BASE
        n = 4 if rom[pos] & 3 == 3 else 2
        raw = rom[pos:pos+n]
        assert raw.hex() == row['hex'] and row['file_offset'] == pos
        words[address] = int.from_bytes(raw, 'little')
        decoded = next(md.disasm(raw, address), None)
        if decoded:
            assert decoded.size == n
            assert decoded.mnemonic + ' ' + decoded.op_str == row['decode']
            ordinary += 1
        else:
            assert address in (0xa00a38d8, 0xa00a3c9e)
        cursor += n
    assert cursor == int(window['end_exclusive'], 16)

def clw_fields(w):
    return [w & 3, w >> 13, 8+(w >> 2 & 7), 8+(w >> 7 & 7),
            ((w >> 5 & 1) << 6) | ((w >> 10 & 7) << 3) | ((w >> 6 & 1) << 2)]

for address, rd, rs, offset in [(0xa00a38ee,15,9,0), (0xa00a38f2,10,9,4),
                               (0xa00a38cc,9,14,4), (0xa00a38fe,9,9,4),
                               (0xa00a3c92,14,11,36)]:
    check(hex(address)+' raw C.LW', clw_fields(words[address]), [0,2,rd,rs,offset])
for address,rd,rs in [(0xa00a38f4,11,21),(0xa00a3c94,15,10)]:
    w=words[address]
    check(hex(address)+' raw C.MV', [w&3,w>>12,w>>7&31,w>>2&31], [2,8,rd,rs])
check('indirect call encoding/link register', words[0xa00a38f6], 0x9782)

# Independent compressed stack-store field extraction, including complete argument order.
stack = {}
for address, rs, offset, value in [(0xa00a3ca2,13,12,'record[0x24]&15'),
                                  (0xa00a3ca4,14,8,'(record[0x24]>>4)&3'),
                                  (0xa00a3cb2,14,4,'U8(record+0xe)'),
                                  (0xa00a3cba,14,0,'U8(record+0xd)')]:
    w=words[address]
    check(hex(address)+' raw C.SWSP', [w&3,w>>13,w>>2&31,((w>>7&3)<<6)|((w>>9&15)<<2)], [2,6,rs,offset])
    stack[str(offset)] = value
for address, rd, offset, f3 in [(0xa00a3ca6,14,14,4), (0xa00a3cb4,14,13,4),
                               (0xa00a3cbc,17,6,5), (0xa00a3cc0,16,4,5)]:
    w=words[address]
    check(hex(address)+' raw unsigned load', [w&127,w>>7&31,w>>12&7,w>>15&31,w>>20], [3,rd,f3,11,offset])

# Check every writer of a5 in callback, independent of B08 textual decoding.
# Ordinary RV32+C destination formats used by this bounded window.
a5_writers=[]
for address,w in words.items():
    if not 0xa00a3c8a <= address < 0xa00a3ce0:
        continue
    if w&3==3:
        rd=(w>>7)&31 if w&127 in (3,11,19,23,51,55,103,111) else None
    else:
        group=(w&3,w>>13)
        if group==(0,2): rd=8+(w>>2&7)
        elif group==(0,0): rd=8+(w>>2&7)
        elif group in [(2,0),(2,2),(1,0),(1,2),(1,3)]: rd=w>>7&31
        elif group==(2,4):
            rd=1 if (w>>12&1 and w>>2&31==0) else (None if w>>2&31==0 else w>>7&31)
        else: rd=None
    if rd==15: a5_writers.append(hex(address))
check('callback a5 writers', a5_writers, ['0xa00a3c94'])

for address,rd,upper in [(0xa00a3caa,13,0xa026a000),(0xa00a3cc4,14,0xa0268000),(0xa00a3cc8,11,0xa0268000)]:
    w=words[address]
    check(hex(address)+' raw LUI', [w&127,w>>7&31,w&0xfffff000], [55,rd,upper])
for address,rd,rs,imm in [(0xa00a3c96,12,0,0xc5),(0xa00a3cae,13,13,0x5d0),
                         (0xa00a3ccc,14,14,0x540),(0xa00a3cd0,11,11,0x4f0)]:
    w=words[address]
    check(hex(address)+' raw ADDI', [w&127,w>>7&31,w>>12&7,w>>15&31,w>>20], [19,rd,0,rs,imm])
check('log a0=4 compressed LI', words[0xa00a3cb8], 0x4511)
w=words[0xa00a3cd4]
imm=((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
if imm & 0x100000: imm-=0x200000
check('log JAL rd/target', [w&127,w>>7&31,hex(0xa00a3cd4+imm)], [111,1,'0xa008b51a'])

for row in prior['strings']:
    p=int(row['address'],16)-BASE
    check(row['address']+' ROM string', rom[p:].split(b'\0',1)[0].decode('ascii'), row['text'])

w=words[0xa00a3c9e]
check('extu raw fields', [w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&63,w>>26], [11,14,3,14,4,5])
w=words[0xa00a38d8]
check('srw raw fields', [w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31,w>>25&3,w>>27], [11,0,5,20,18,0,8])
model = ROM_ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model.read_text().splitlines()
for excerpt in prior['model_excerpts']:
    start=excerpt['line']-1
    check('existing model excerpt line '+str(start+1), '\n'.join(lines[start:start+len(excerpt['text'].splitlines())]), excerpt['text'])

result={'task':'B09','result':'passed','source':str(ROM),'mapping':'offset=VA-0x9ffff000',
        'windows':2,'bytes':190,'ordinary_instructions':ordinary,'vendor_words':2,
        'independent_checks':len(checks),'checks':checks,'log_stack_arguments':stack,
        'verdict':'accepted_with_boundary_clarifications',
        'limits':['Static ROM reads only; no target execution.',
                  'Vendor semantics checked against existing local model only.',
                  'Dynamic callback target, runtime list and source C types remain unknown.']}
(HERE/'review-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['result','windows','bytes','ordinary_instructions','vendor_words','independent_checks','verdict']}))
