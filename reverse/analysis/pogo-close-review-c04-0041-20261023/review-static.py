"""C04 bounded static review; reads original ROM, writes only this directory."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = 0x9ffff000
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
prior = json.loads((ROOT/'reverse/analysis/pogo-close-callback-c03-0041-20261023/instruction-evidence.json').read_text())
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
def raw(pc, n): return ROM[pc-BASE:pc-BASE+n]
def value(pc, n=4): return int.from_bytes(raw(pc,n), 'little')
def sx(v,n): return v-(1<<n) if v & (1<<(n-1)) else v
checks=[]
def record(pc, kind, actual, expected):
    assert actual == expected, (hex(pc), kind, actual, expected)
    checks.append(dict(site=hex(pc), raw_hex=raw(pc, 4 if value(pc,2)&3 == 3 else 2).hex(), kind=kind, decoded_fields=actual))
def load(pc, rd, rs1, off):
    v=value(pc); record(pc,'RV32 LW', [v&127,(v>>12)&7,(v>>7)&31,(v>>15)&31,sx(v>>20,12)], [3,2,rd,rs1,off])
def store(pc, rs2, rs1, off):
    v=value(pc); record(pc,'RV32 SW',[v&127,(v>>12)&7,(v>>20)&31,(v>>15)&31,sx(((v>>25)<<5)|((v>>7)&31),12)],[35,2,rs2,rs1,off])
def addi(pc,rd,rs1,off):
    v=value(pc);record(pc,'RV32 ADDI',[v&127,(v>>12)&7,(v>>7)&31,(v>>15)&31,sx(v>>20,12)],[19,0,rd,rs1,off])
def caddi(pc, rd, off):
    v=value(pc,2);record(pc,'C.ADDI',[v&0xe003,(v>>7)&31,sx(((v>>12)&1)<<5|((v>>2)&31),6)],[1,rd,off])
def compact_mem(pc,store_flag,reg,base,off):
    v=value(pc,2)
    imm=(((v>>10)&7)<<3)|(((v>>6)&1)<<2)|(((v>>5)&1)<<6)
    record(pc,'C.SW' if store_flag else 'C.LW',[v&0xe003,8+((v>>2)&7),8+((v>>7)&7),imm],[0xc000 if store_flag else 0x4000,reg,base,off])
def branch(pc,funct,rs1,rs2,target):
    v=value(pc);imm=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
    record(pc,'RV32 branch',[v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,(pc+sx(imm,13))&0xffffffff],[99,funct,rs1,rs2,target])
def jal(pc,target):
    v=value(pc);imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
    record(pc,'RV32 JAL',[v&127,(v>>7)&31,(pc+sx(imm,21))&0xffffffff],[111,1,target])

windows=[]
for w in prior['windows']:
    start=int(w['start'],16);end=int(w['end_exclusive'],16)
    ins=list(cs.disasm(raw(start,end-start),start))
    assert sum(i.size for i in ins)==end-start
    rows=[dict(address=hex(i.address),hex=i.bytes.hex(),decode=i.mnemonic+' '+i.op_str) for i in ins]
    assert rows==w['instructions']
    windows.append(dict(name=w['name'],start=w['start'],end_exclusive=w['end_exclusive'],instruction_count=len(rows),matches_C03=True))

compact_mem(0xa00a3bd0,False,9,10,0)
load(0xa00a3bd2,15,9,0x198);caddi(0xa00a3bd6,15,-1);store(0xa00a3bd8,15,9,0x198)
# funct3=4 is signed BLT, comparing x0 with x15; funct3=6 would be BLTU.
branch(0xa00a3bdc,4,0,15,0xa00a3c08)
record(0xa00a3c02,'C.MV a0,s1',[value(0xa00a3c02,2)&0xf003,(value(0xa00a3c02,2)>>7)&31,(value(0xa00a3c02,2)>>2)&31],[0x8002,10,9])
jal(0xa00a3bfe,0xa008b51a);jal(0xa00a3c04,0xa008ab8a)
record(0xa008ab8a,'LUI a5',[value(0xa008ab8a)&0xfff,value(0xa008ab8a)&0xfffff000],[0x7b7,0x62fc9000])
addi(0xa008ab8e,15,15,0x5e0)
branch(0xa008ab92,0,10,15,0xa008abae);branch(0xa008ab96,0,10,0,0xa008abae)
jal(0xa008aba2,0xa002e14e)
for start,obj,save,ld,inc,st,init_call,start_call in [
    (0xa005b14e,0x68,0xa005b154,0xa005b15e,0xa005b16a,0xa005b16e,0xa005b15a,0xa005b174),
    (0xa005b190,0xcc,0xa005b196,0xa005b1a0,0xa005b1ac,0xa005b1b0,0xa005b19c,0xa005b1b6),
    (0xa005b1d2,0x130,0xa005b1d8,0xa005b1e2,0xa005b1ee,0xa005b1f2,0xa005b1de,0xa005b1f8)]:
    addi(start,19,18,obj);store(save,18,18,obj);load(ld,15,18,0x198);caddi(inc,15,1);store(st,15,18,0x198)
    jal(init_call,0xa009e4f6);jal(start_call,0xa009f9b6)
load(0xa005b2e6,12,18,4);addi(0xa005b2ea,19,18,8);store(0xa005b2f0,18,18,8)
jal(0xa005b2f6,0xa009e4f6);addi(0xa005b2fa,14,18,0x180)
compact_mem(0xa005b2fe,False,15,14,0x18);caddi(0xa005b308,15,1);compact_mem(0xa005b30a,True,15,14,0x18)
jal(0xa005b310,0xa009f9b6)
# Verify C02's exact neutral name is present, without treating it as semantics.
c01=(ROOT/'reverse/reports/ap01/pogo-timer-lifecycle-c01-0041-20261023.md').read_text(encoding='utf-8')
assert 'observed_word_190 = word_at(ctx, 0x190)' in c01
assert 'phase = word_at(ctx, 0x190)' not in c01
result=dict(task='C04',verdict='accepted',windows=windows,manual_encoding_checks=checks,
    validation=dict(selected_windows=6,selected_bytes=sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),
                    undecoded_bytes=0,original_rom_matches_C03=True,manual_encoding_checks=len(checks),
                    C02_neutral_name_applied=True,firmware_executed=False),
    limitations=['Only six C03 windows were redecoded; no whole-function boundary rediscovery.',
                 'Callee behavior, timer teardown, all count writers and global scheduling remain unverified.'])
(HERE/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result['validation']))
