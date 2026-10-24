"""A56: bounded static bytes and inherited rows; never execute the target."""
from pathlib import Path
import json
import capstone

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
BASE, START, END = 0x9ffff000, 0xa019d708, 0xa019d798
assert ROM.stat().st_size == 6769704
with ROM.open('rb') as f:
    f.seek(START - BASE)
    buf = f.read(END - START)
assert len(buf) == END - START
cs = capstone.Cs(capstone.CS_ARCH_RISCV,
                 capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
rows = []
pc = START
while pc < END:
    at = pc - START
    n = 4 if buf[at] & 3 == 3 else 2
    raw = buf[at:at+n]
    ins = next(cs.disasm(raw, pc), None)
    rows.append(dict(pc=hex(pc), file_offset=hex(pc-BASE), raw=raw.hex(),
                     asm=(ins.mnemonic + ' ' + ins.op_str if ins else 'UNDECODED')))
    pc += n
assert pc == END
D = {int(r['pc'], 16): r for r in rows}
checks = []

def check(name, got, expected):
    assert got == expected, (name, got, expected)
    checks.append(dict(name=name, value=got))

def sx(v, bits):
    return v - (1 << bits) if v & (1 << (bits-1)) else v

def w(pc):
    return int.from_bytes(bytes.fromhex(D[pc]['raw']), 'little')

def i_fields(pc):
    v = w(pc)
    return [v & 127, (v >> 7) & 31, (v >> 12) & 7,
            (v >> 15) & 31, sx(v >> 20, 12)]

def branch(pc):
    v = w(pc)
    check(hex(pc)+' branch opcode', v & 127, 99)
    imm = ((v >> 31) << 12) | (((v >> 7) & 1) << 11)
    imm |= (((v >> 25) & 63) << 5) | (((v >> 8) & 15) << 1)
    return pc + sx(imm, 13)

def cb(pc):
    v = w(pc)
    check(hex(pc)+' compressed branch class', [v & 3, v >> 13], [1, 7])
    imm = (((v >> 12) & 1) << 8) | (((v >> 10) & 3) << 3)
    imm |= (((v >> 5) & 3) << 6) | (((v >> 3) & 3) << 1) | (((v >> 2) & 1) << 5)
    return pc + sx(imm, 9)

def cj(pc):
    v = w(pc)
    check(hex(pc)+' compressed jump class', [v & 3, v >> 13], [1, 5])
    imm = (((v >> 12) & 1) << 11) | (((v >> 11) & 1) << 4)
    imm |= (((v >> 9) & 3) << 8) | (((v >> 8) & 1) << 10)
    imm |= (((v >> 7) & 1) << 6) | (((v >> 6) & 1) << 7)
    imm |= (((v >> 3) & 7) << 1) | (((v >> 2) & 1) << 5)
    return pc + sx(imm, 12)

check('registry base LUI rd=a3', [w(0xa019d708)&127, (w(0xa019d708)>>7)&31,
                               w(0xa019d708)&0xfffff000], [55, 13, 0x62fc9000])
check('registry base addi', i_fields(0xa019d70c), [19, 13, 0, 13, 0x57c])
check('head load is word', i_fields(0xa019d710), [3, 14, 2, 13, 0x1c8])
check('stride load is word', i_fields(0xa019d714), [3, 13, 2, 13, 0x1c4])
check('next offset add4', [w(0xa019d718)&3, w(0xa019d718)>>13,
                          (w(0xa019d718)>>7)&31,
                          sx((((w(0xa019d718)>>12)&1)<<5)|((w(0xa019d718)>>2)&31),6)],
      [1, 0, 13, 4])
check('nonempty node target', cb(0xa019d71a), 0xa019d746)
check('D=word(node)', [w(0xa019d746)&3, w(0xa019d746)>>13,
                       8+((w(0xa019d746)>>2)&7), 8+((w(0xa019d746)>>7)&7),
                       ((w(0xa019d746)>>6)&1)*4+((w(0xa019d746)>>10)&7)*8+((w(0xa019d746)>>5)&1)*64],
      [0, 2, 9, 14, 0])
check('D letter unsigned byte', i_fields(0xa019d748), [3, 10, 4, 9, 0])
v = w(0xa019d74c)
check('compare D byte to inherited a2', [(v>>12)&7, (v>>15)&31, (v>>20)&31], [0,10,12])
check('matching branch target', branch(0xa019d74c), 0xa019d864)
v = w(0xa019d750)
vendor = dict(op=v&127, rd=(v>>7)&31, f3=(v>>12)&7, rs1=(v>>15)&31,
              rs2=(v>>20)&31, shift=(v>>25)&3, top5=v>>27)
check('vendor indexed word fields', list(vendor.values()), [11,14,4,14,13,0,8])
check('walk repeats head null gate', cj(0xa019d754), 0xa019d71a)
check('callback a0=D', w(0xa019d756), 0x8526)
for pc, reg, off in [(0xa019d758,15,-0x28),(0xa019d75c,11,-0x24)]:
    v=w(pc)
    check(hex(pc)+' preserve register', [v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,
                                        sx(((v>>25)<<5)|((v>>7)&31),12)], [35,2,8,reg,off])
check('indirect callback via a4', w(0xa019d760), 0x9702)
check('restore suffix a1', i_fields(0xa019d762), [3,11,2,8,-0x24])
check('restore original source a5', i_fields(0xa019d766), [3,15,2,8,-0x28])
check('callback return nonzero test', [(w(0xa019d76a)>>12)&7,(w(0xa019d76a)>>15)&31,
                                     (w(0xa019d76a)>>20)&31], [1,10,0])
check('nonzero callback target', branch(0xa019d76a), 0xa019d86a)
for pc in (0xa019d73a,0xa019d78c):
    u,j=w(pc),w(pc+4)
    check(hex(pc)+' diagnostic AUIPC/JALR', [u&127,(u>>7)&31,j&127,(j>>7)&31,(j>>15)&31],
          [23,1,103,1,1])
    check(hex(pc)+' diagnostic target', (pc+sx(u&0xfffff000,32)+sx(j>>20,12))&0xffffffff,
          0xa008b51a)
check('no candidate status register', w(0xa019d742), 0x498d)
check('callback zero status register', w(0xa019d794), 0x4985)
check('no candidate common exit', cj(0xa019d744), 0xa019d6dc)
check('callback zero common exit', cj(0xa019d796), 0xa019d6dc)

old_path = MAIN / 'reverse/analysis/photo-reader-mode-a47-0041-20261024/evidence.json'
old = json.loads(old_path.read_text(encoding='utf8'))
old_rows={int(r['pc'],16):r for r in old['rows']}
inherited = [old_rows[a] for a in (0xa019d6ec,0xa019d6f0,0xa019d6f2,0xa019d6f4,
                                  0xa019d6f6,0xa019d6fa,0xa019d6fe,0xa019d704,
                                  0xa019d864,0xa019d866,0xa019d86a,0xa019d86c,0xa019d798)]
check('inherited ready slot gate', old_rows[0xa019d864]['asm'], 'c.lw a4, 8(s1)')
check('inherited ready optional branch', old_rows[0xa019d866]['asm'], 'bnez a4, -0x110')
check('inherited open slot gate', old_rows[0xa019d86a]['asm'], 'c.lw a4, 0xc(s1)')
check('inherited open slot branch', old_rows[0xa019d86c]['asm'], 'c.bnez a4, -0xd4')
check('inherited selected D save', old_rows[0xa019d798]['asm'], 'sw s1, 4(s2)')
model_path=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model=model_path.read_text(encoding='utf8')
p=model.index(':th.lrw ')
rule=model[p:model.index('\n}',p)+2]
check('existing lrw rule has indexed 32-bit load',
      all(s in rule for s in ('op1214=4 & op2731=8', 'rs2 << thshift',
                              'local updated:4 = rs1 + delta',
                              'local value:4 = *[ram]:4 ea;', 'rd = value;')), True)
check('existing lrw rule no separate base writeback', 'thbase = updated;' in rule, False)
out=dict(status='PASS',claim='J08/1',task='A56',baseline='32f9c9e',static_only=True,
         identity=dict(path=str(ROM),length=6769704,
                       inherited_sha256='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
                       mapping='file_offset = VA - 0x9ffff000',hash_recomputed=False),
         new_read=dict(start=hex(START),end_exclusive=hex(END),bytes=len(buf)),
         decoder=dict(name='Capstone',version=capstone.__version__,mode='RV32 + RVC'),
         checks=checks,rows=rows,vendor=dict(pc='0xa019d750',raw='0b47d740',fields=vendor,
                                           rule_path=str(model_path),rule=rule,
                                           limitation='Existing local profile semantics; no new upstream ISA authentication'),
         inherited=dict(path=str(old_path),rows=inherited),
         derived=dict(registry_base='0x62fc957c',head_slot='0x62fc9744',stride_slot='0x62fc9740',
                      node_driver='word(N)',node_next='word(N + word(stride_slot) + 4)'),
         limits=['No runtime or target instruction execution.',
                 'No bytes outside the exact selection window newly read; external branch destinations use inherited rows only.',
                 'No actual registry values, writer, concrete D, callback slot target or POSIX binding established.',
                 's3 status assignments are observed; common epilogue and full return ABI remain outside this window.'])
(OUT/'evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),instructions=len(rows),new_bytes=len(buf))))
