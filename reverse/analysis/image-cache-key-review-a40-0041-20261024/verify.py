from pathlib import Path
import json
H=Path(__file__).resolve().parent
R=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
rom=(R/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
def raw(a,n): return rom[a-0x9ffff000:a-0x9ffff000+n]
def word(a): return int.from_bytes(raw(a,4),'little')
def signed(x,n): return (x^(1<<(n-1)))-(1<<(n-1))
rows=[]
def check(a,h,claim):
 assert raw(a,len(bytes.fromhex(h))).hex()==h
 rows.append(dict(address=hex(a),bytes=h,claim=claim))
def branch(a,rs1,rs2,f3,target):
 w=word(a); d=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
 assert (w&127,(w>>15)&31,(w>>20)&31,(w>>12)&7)==(0x63,rs1,rs2,f3)
 assert a+signed(d,13)==target
 rows.append(dict(address=hex(a),bytes=raw(a,4).hex(),branch=dict(rs1=rs1,rs2=rs2,funct3=f3,target=hex(target))))
def jal(a,target):
 w=word(a);d=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 assert w&127==0x6f and a+signed(d,21)==target
 rows.append(dict(address=hex(a),bytes=raw(a,4).hex(),direct_target=hex(target)))
check(0xa008e642,'b78708a0938767bc2322f4fc','LUI+ADDI produces a0087bc6; stack callback first slot (A23 identity inherited)')
check(0xa01985cc,'aa8423202501232605003146ce854105','cache saved in s1; size 12, callbacks s3, destination cache+10')
check(0xa00f0d26,'0c49a9e1','cache+10 -> a1; nonzero branch to d6a')
check(0xa00f0d6a,'1c4daa8495ef','normal callback+18 nonzero branch to daa; a1 preserved')
check(0xa00f0daa,'504115ea','cache+4 -> a2; nonzero branch to de0; a1 preserved')
check(0xa00f0de0,'510613054502','a2+=14; a0=cache+24')
jal(0xa00f0de6,0xa00f0b80)
check(0xa00f0c02,'2e89','save comparator a1 -> s2')
check(0xa00f0c14,'23a0040023a2240190c4','clear tree+0; comparator s2 -> tree+4; saved size a2 -> tree+8')
for a,base,rd in [(0xa0087bce,11,13),(0xa0087bd4,10,11)]:
 w=word(a); assert (w&127,(w>>12)&7,(w>>15)&31,(w>>7)&31,w>>20)==(3,4,base,rd,8)
 rows.append(dict(address=hex(a),bytes=raw(a,4).hex(),claim='LBU class +8, zero-extended'))
check(0xa0087bd2,'d041','C.LW right source+4 -> a2')
check(0xa0087bd8,'4841','C.LW left source+4 -> a0')
jal(0xa0087bda,0xa0087b5c)
check(0xa0087bde,'b240224441018280','adapter epilogue restores ra/s0/sp and returns without changing a0')
branch(0xa0087b5c,11,13,1,0xa0087b9c)
branch(0xa0087b62,11,15,1,0xa0087b8a)
jal(0xa0087b70,0xa002db16)
check(0xa0087b74,'814709c5fd57','default 0; zero -> 7b80; otherwise candidate -1')
branch(0xa0087b7a,0,10,5,0xa0087b80)
check(0xa0087b7e,'8547','positive result -> 1')
check(0xa0087b8a,'814799e9','same class other than 0/1 keeps zero and branches 7ba2')
branch(0xa0087b8e,10,12,0,0xa0087ba2)
branch(0xa0087b94,12,10,7,0xa0087ba2)
branch(0xa0087b9e,13,11,6,0xa0087b98)
for a,rd,base in [(0xa002db3e,15,10),(0xa002db42,13,11)]:
 w=word(a);f=(w&127,(w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3)
 assert f==(11,4,16,rd,base,14,0)
 rows.append(dict(address=hex(a),bytes=raw(a,4).hex(),claim='th.lrbu unsigned byte, base + (a4 << 0)',fields=f))
check(0xa002db46,'81c70507','left zero -> db4e; otherwise advance byte index')
branch(0xa002db4a,15,13,0,0xa002db3e)
check(0xa002db4e,'3385d740','SUB a0,a5,a3: two zero-extended U8 difference, signed range -255..255')
check(0xa00eba8c,'1c492685d294829779f1','head uses cache+10; a0=payload; inherited a1=key; nonzero fallback')
check(0xa00ea842,'2a89ae89','tree descriptor saved s2, key saved s3')
check(0xa00ea858,'832749008c484e8582977dd1','tree+4 -> callback; a1=payload; a0=key; zero -> return candidate')
model=R/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
s=model.read_text(); a=s.index(':th.lrbu '); rule=s[a:s.index('\n}',a)+2]
assert 'rd = zext(value)' in rule and 'rs2 << thshift' in rule
out=dict(result='passed',static_only=True,checks=rows,check_count=len(rows),model=str(model),model_rule=rule,limitations='Sparse independent raw-byte and bitfield review; no firmware execution, no new function recovery. Existing A38 complete necessary windows retained by reference.')
(H/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(result='passed',checks=len(rows),static_only=True)))
