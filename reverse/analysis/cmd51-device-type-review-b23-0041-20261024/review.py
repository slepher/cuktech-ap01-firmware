"""B23 independent static byte, field and CFG-anchor review; no inputs run."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE=0x9ffff000
prior=json.loads((ROOT/'reverse/analysis/cmd51-device-type-b22-0041-20261024/evidence.json').read_text(encoding='utf8'))
checks=[]
def raw(pc,n): return ROM[pc-BASE:pc-BASE+n]
def w(pc,n=4): return int.from_bytes(raw(pc,n),'little')
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
def eq(label,got,expected):
 assert got==expected,(label,got,expected)
 checks.append(label)
def imm(pc,op,f3,rd,r1,value):
 v=w(pc)
 eq(hex(pc)+' I fields',(v&127,(v>>12)&7,(v>>7)&31,(v>>15)&31,sx(v>>20,12)),(op,f3,rd,r1,value))
def cli(pc,rd,value):
 v=w(pc,2)
 eq(hex(pc)+' C.LI',(v&3,v>>13,(v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6)),(1,2,rd,value))
def caddi(pc,rd,value):
 v=w(pc,2)
 eq(hex(pc)+' C.ADDI',(v&3,v>>13,(v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6)),(1,0,rd,value))
def clui(pc,rd,value):
 v=w(pc,2)
 eq(hex(pc)+' C.LUI',(v&3,v>>13,(v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6)<<12),(1,3,rd,value))
def bfields(pc):
 v=w(pc)
 off=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
 return (v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,pc+sx(off,13))
def cjtarget(pc):
 v=w(pc,2)
 off=(((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5)
 return (v&3,v>>13,pc+sx(off,12))
for r in prior['instructions']:
 eq(r['pc']+' retained raw',raw(int(r['pc'],16),len(bytes.fromhex(r['raw']))).hex(),r['raw'])
for b in prior['branch_targets']:
 pc=int(b['pc'],16); target=int(b['target'],16)
 if b['kind']=='B':
  got=bfields(pc); eq(hex(pc)+' B kind/target',(got[0],got[1],got[4]),(99,b['funct3'],target))
 else: eq(hex(pc)+' C.J target',cjtarget(pc),(1,5,target))
for args in [(0xa00a9410,3,5,14,18,4),(0xa00a94c0,3,5,14,18,6),(0xa00a96b4,3,5,12,27,24),(0xa00a96e4,3,5,12,27,24),(0xa00a9708,3,5,12,27,24),(0xa00a9408,3,4,15,27,13),(0xa00a9504,3,4,14,27,14)]: imm(*args)
v=w(0xa00a950e)
eq('a5 published as item byte',(v&127,(v>>12)&7,(v>>20)&31,(v>>15)&31,sx(((v>>25)<<5)|((v>>7)&31),12)),(35,0,15,27,14))
for pc,expected in [(0xa00a9426,(99,0,14,15,0xa00a94c0)),(0xa00a94fe,(99,1,14,13,0xa00a9504)),(0xa00a961a,(99,1,14,13,0xa00a9504)),(0xa00a9648,(99,1,14,13,0xa00a9504)),(0xa00a967a,(99,1,14,13,0xa00a9504)),(0xa00a96dc,(99,1,14,13,0xa00a9504)),(0xa00a9700,(99,7,14,12,0xa00a9504)),(0xa00a950a,(99,0,14,15,0xa00a9598))]: eq(hex(pc)+' identity/threshold/join gate',bfields(pc),expected)
clui(0xa00a93d2,21,0x2000)
clui(0xa00a93d4,26,0x7000)
clui(0xa00a948e,13,0x1000)
clui(0xa00a94ac,13,0x3000)
# Verify every stored static ADDI constant; this is disassembly, not execution.
for pc_text,value in prior['derived_constants'].items():
 pc=int(pc_text,16); v=w(pc); rs=(v>>15)&31
 bases={0:0,21:0x2000,26:0x7000,13:0x1000}
 if pc==0xa00a94ae: bases[13]=0x3000
 eq(hex(pc)+' constant opcode',(v&127,(v>>12)&7),(19,0))
 eq(hex(pc)+' static constant',bases[rs]+sx(v>>20,12),int(value,16))
types=[(0xa00a9418,0x12),(0xa00a9432,0x10),(0xa00a9482,0x10),(0xa00a9494,0x10),(0xa00a949e,0x13),(0xa00a94a6,1),(0xa00a94b2,0x14),(0xa00a94bc,0x11),(0xa00a94c8,0x1e),(0xa00a94d6,0x16),(0xa00a94e4,0x18),(0xa00a94f2,0x17),(0xa00a94fc,2),(0xa00a9502,0x1a),(0xa00a960e,0x1b),(0xa00a9618,2),(0xa00a961e,0x1f),(0xa00a9626,0x1c),(0xa00a963c,0x1d),(0xa00a9646,2),(0xa00a964c,0x19),(0xa00a9660,4),(0xa00a966e,3),(0xa00a9678,2),(0xa00a967e,6),(0xa00a9686,5),(0xa00a9694,2),(0xa00a9698,0xc),(0xa00a96a6,0xd),(0xa00a96da,2),(0xa00a96e0,8),(0xa00a96c4,2),(0xa00a96f4,2),(0xa00a96fe,7),(0xa00a9704,0xb),(0xa00a9718,2)]
for pc,value in types: cli(pc,15,value)
imm(0xa00a9630,19,0,15,0,0x20)
for pc in [0xa00a96b8,0xa00a96e8,0xa00a970c]: clui(pc,14,0x10000)
for pc in [0xa00a96ba,0xa00a96ea,0xa00a970e]: caddi(pc,14,-3)
for pc in [0xa00a96bc,0xa00a96ec,0xa00a9710]: imm(pc,19,0,13,12,-1)
for pc in [0xa00a96c0,0xa00a96f0,0xa00a9714]:
 v=w(pc)
 eq(hex(pc)+' extu fields',(v&127,(v>>12)&7,(v>>26)&63,(v>>20)&63,(v>>7)&31,(v>>15)&31),(11,3,15,0,13,13))
for pc in [0xa00a96c6,0xa00a96f6,0xa00a971a]: eq(hex(pc)+' unsigned masked range gate',bfields(pc),(99,6,14,13,0xa00a9504))
imm(0xa00a96fa,19,0,14,0,159)
for pc in [0xa00a96ca,0xa00a971e]: imm(pc,19,0,15,0,169)
for pc in [0xa00a96ce,0xa00a9722]:
 v=w(pc); eq(hex(pc)+' SLTU threshold',(v&127,v>>25,(v>>12)&7,(v>>7)&31,(v>>15)&31,(v>>20)&31),(51,0,3,15,15,12))
caddi(0xa00a96d2,15,14)
caddi(0xa00a9726,15,9)
caddi(0xa00a9738,9,1)
caddi(0xa00a973a,18,8)
model=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
text=model.read_text(encoding='utf8'); start=text.index(':th.extu rd,rs1,15,0 ')
rule=text[start:text.index('\n}',start)+2]
eq('existing local extu rule unchanged',rule,prior['vendor_rule']['text'])
eq('extu rule masks by zero-fill shifts',all(s in rule for s in ['local value:4 = rs1 << 16;','rd = value >> 16;']),True)
result={'status':'PASS','static_only':True,'checks':checks,'retained_raw_instructions':len(prior['instructions']),'branch_targets_checked':len(prior['branch_targets']),'additional_rom_bytes_saved':0,'new_rom_functionality':0,'vendor_rule_scope':{'path':str(model),'match_existing_rule':True,'hardware_isa_certified':False},'limits':['No dispatcher execution or classification inputs enumerated.','E01/E02 fallback and five-pointer lifecycle inherited, not revalidated.','Protocol/brand IDs, item+18 writer/units and actual driver behavior remain unknown.']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':'PASS','checks':len(checks),'retained_raw_instructions':len(prior['instructions']),'branch_targets':len(prior['branch_targets']),'new_rom_functionality':0}))
