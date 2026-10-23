"""H07: bounded recheck of inherited navigation anchors, never execute target."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
ROOT=Path("D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware")
OUT=Path(__file__).resolve().parent
rom=(ROOT/"roms/0041/ap01-1.0.2_0041.bin").read_bytes()
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
windows=[(0xa00afd2a,0xa00afd32),(0xa00aff60,0xa00aff66),(0xa00affc8,0xa00affce),(0xa00b0288,0xa00b028e),(0xa00b03be,0xa00b03c2),(0xa00b0088,0xa00b008c),(0xa00b3192,0xa00b319a),(0xa00b31c4,0xa00b31cc),(0xa00ab632,0xa00ab63e)]
rows=[]
for start,end in windows:
 raw=rom[start-0x9ffff000:end-0x9ffff000];ins=list(md.disasm(raw,start))
 assert sum(i.size for i in ins)==len(raw),(hex(start),"incomplete decode")
 rows.extend(dict(va=f"{i.address:08x}",file_offset=i.address-0x9ffff000,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in ins)
def word(a,n):return int.from_bytes(rom[a-0x9ffff000:a-0x9ffff000+n],"little")
def sx(v,n):return v-(1<<n) if v>>(n-1) else v
def branch(a):
 w=word(a,4);assert w&127==99
 return a+sx(((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1),13)
def jal(a):
 w=word(a,4);assert w&127==111
 return a+sx(((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1),21)
def cj(a):
 w=word(a,2);assert w&0xe003==0xa001
 imm=((w>>12&1)<<11)|((w>>11&1)<<4)|((w>>9&3)<<8)|((w>>8&1)<<10)|((w>>7&1)<<6)|((w>>6&1)<<7)|((w>>3&7)<<1)|((w>>2&1)<<5)
 return a+sx(imm,12)
checks=[]
def check(name,got,want):
 assert got==want,(name,got,want);checks.append(dict(name=name,observed=got,expected=want))
check("shared normal-navigation direct call",jal(0xa00afd2c),0xa00b3106)
check("active5 right dispatch",branch(0xa00aff62),0xa00affc8)
check("right tail joins shared call",cj(0xa00affcc),0xa00afd2a)
check("active5 left dispatch",branch(0xa00b028a),0xa00b0354)
check("left refresh tail joins target4",cj(0xa00b03c0),0xa00b0088)
check("target4 joins shared call",cj(0xa00b008a),0xa00afd2a)
# Independent RV32 store field extraction, not a decompiler interpretation.
w=word(0xa00b3194,4)
check("active index SW fields",[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,sx(((w>>25)<<5)|((w>>7)&31),12)],[35,2,9,20,0x34])
check("right direction/target compressed words",[word(0xa00affc8,2),word(0xa00affca,2)],[0x4609,0x459d])
check("left target compressed word",word(0xa00b0088,2),0x4591)
check("shared object parameter MV a0,s1",word(0xa00afd2a,2),0x8526)
w=word(0xa00b31c8,4)
check("animation busy SB fields",[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,sx(((w>>25)<<5)|((w>>7)&31),12)],[35,0,9,0,0x4c])
w=word(0xa00ab638,4)
check("ready SB fields",[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,sx(((w>>25)<<5)|((w>>7)&31),12)],[35,0,9,15,0x4c])
result=dict(kind="old-conclusion recheck; new business recovery=0",scope="only inherited normal overview navigation, not app teardown or DELETE delivery",windows=[dict(start=f"{a:08x}",end_exclusive=f"{b:08x}") for a,b in windows],bytes=sum(b-a for a,b in windows),instruction_count=len(rows),checks=checks,anchors=rows,status="passed")
(OUT/"navigation-recheck.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:result[k] for k in ["status","bytes","instruction_count"]}|{"checks":len(checks)},ensure_ascii=False))
