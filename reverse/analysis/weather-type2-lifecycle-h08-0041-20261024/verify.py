"""H08: read-only original-byte recheck plus bounded type2 cleanup evidence."""
import json,re
from pathlib import Path
import capstone
H=Path(__file__).resolve().parent
M=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
b=(M/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
d=json.loads((M/'reverse/rehost/weather-calendar-complete-0041.json').read_text(encoding='utf-8'))
old=d['evidence'][18]['stdout']
checks=[]
def ck(name,a,e):
 assert a==e,(name,a,e)
 checks.append(dict(name=name,actual=a,expected=e))
def word(a):return int.from_bytes(b[a-BASE:a-BASE+4],'little')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def jal(a,t):
 w=word(a);v=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 ck(hex(a)+' jal',[w&127,(w>>7)&31,a+sx(v,21)],[111,1,t])
def mem(a,op,r,r1,off,f3=2):
 w=word(a);i=sx(((w>>25)<<5|((w>>7)&31)) if op==35 else w>>20,12)
 ck(hex(a)+' memory',[w&127,(w>>12)&7,((w>>20)&31) if op==35 else ((w>>7)&31),(w>>15)&31,i],[op,f3,r,r1,off])
# Recheck inherited callback only against retained original instructions, no duplicate export.
n=0
for line in old.splitlines():
 m=re.match(r'(a[0-9a-f]+):\s+([0-9a-f]{4,8})\s',line)
 if m and 0xa00ab754<=int(m[1],16)<0xa00ab834:
  a=int(m[1],16);raw=bytes.fromhex(m[2])[::-1]
  assert b[a-BASE:a-BASE+len(raw)]==raw,hex(a)
  n+=1
ck('inherited callback instructions matching original',n,78)
# New evidence restricted to allocation identity, hookup, DELETE core and callback ABI loads.
spans=[('type2-tag-constant',0xa005e182,0xa005e184),('type2-wrapper-identity',0xa005cf9a,0xa005cfb8),('type2-context-identity',0xa005da90,0xa005dace),('type2-success-hookup',0xa005e1f2,0xa005e224),('inherited-callback-ABI-recheck',0xa00ab754,0xa00ab780),('DELETE-event-owner-cleanup',0xa00aba9c,0xa00abb52)]
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[]
for name,a,e in spans:
 rows=[];at=a
 for i in cs.disasm(b[a-BASE:e-BASE],a):
  assert i.address==at
  rows.append(dict(address=hex(at),offset=hex(at-BASE),bytes=i.bytes.hex(),text=i.mnemonic+' '+i.op_str));at+=i.size
 assert at==e,(hex(at),hex(e))
 windows.append(dict(name=name,start=hex(a),end_exclusive=hex(e),instructions=rows))
ck('ctx allocation immediate',sx(word(0xa005da90)>>20,12),0x88)
for a,t in [(0xa005cfa6,0xa008e362),(0xa005da94,0xa008e362),(0xa005dac6,0xa008ab8a),(0xa005e1fc,0xa00b3a68),(0xa00abb30,0xa008ae58),(0xa00abb36,0xa008ab8a),(0xa00abb44,0xa00b3abe),(0xa00abb4a,0xa008ab8a)]:jal(a,t)
for a,op,r,r1,off,f3 in [(0xa00ab76a,3,12,10,8,1),(0xa00ab76e,3,11,10,10,1),(0xa00ab774,3,19,10,26,5),(0xa00ab778,3,18,10,12,1),(0xa00ab77c,3,20,10,28,2),(0xa00ababa,3,18,10,4,2),(0xa00ababe,3,19,18,16,2),(0xa00abac6,3,9,19,4,2),(0xa005e204,35,21,23,0,2),(0xa005e208,35,18,23,4,2),(0xa005e20c,35,23,19,16,2),(0xa00abb4e,35,0,18,16,2)]:mem(a,op,r,r1,off,f3)
clear_offsets=[0x24,0x1c,0,0xc,8,0x48,0x34,0x18,0x14,0x30,0x44,0x2c,0x4c,0x50,0x54,0x58,0x38,0x3c,0x40,4,0x10,0x5c,0x60,0x64,0x84]
for a,off in zip(range(0xa00abacc,0xa00abb30,4),clear_offsets):mem(a,35,0,9,off)
for a,h in [(0xa00abaca,'a85c'),(0xa00abb34,'2685'),(0xa00abb3e,'ca85'),(0xa00abb48,'4e85')]:
 ck(hex(a)+' compressed ABI',b[a-BASE:a-BASE+2].hex(),h)
ck('type2 tag literal',b[0xa005e182-BASE:0xa005e184-BASE].hex(),'894a')
ck('wrapper size literal',b[0xa005cfa4-BASE:0xa005cfa6-BASE].hex(),'5145')
def branch(a,f3,r1,r2,t):
 w=word(a);v=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
 ck(hex(a)+' branch',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,a+sx(v,13)],[99,f3,r1,r2,t])
branch(0xa00abaa8,1,15,14,0xa00abb60)
branch(0xa00abac2,0,19,0,0xa00abb52)
ck('event DELETE immediate',sx(word(0xa00abaa4)>>20,12),0x29)
ck('event mask compressed instructions',b[0xa00aba9e-BASE:0xa00abaa4-BASE].hex(),'61777d17f98f')
for a,t in [(0xa005e1f2,0xa00ab754),(0xa00abb3a,0xa00ab754)]:ck(hex(a)+' callback key',(word(a)&0xfffff000)+sx(word(a+6)>>20,12),t)
ck('DELETE installer address',(word(0xa005e200)&0xfffff000)+sx(word(0xa005e216)>>20,12),0xa00aba9c)
ck('event installer call',0xa005e21c+(word(0xa005e21c)&0xfffff000)+sx(word(0xa005e220)>>20,12),0xa01ad654)
# Strings are read solely for identity, no asset extraction.
strings={}
for a in [0xa037be30,0xa01c43a0]:
 raw=b[a-BASE:b.index(0,a-BASE)];strings[hex(a)]=raw.decode('utf-8')
record=dict(source=str(M/'roms/0041/ap01-1.0.2_0041.bin'),mapping_base=hex(BASE),decoder=capstone.__version__,inherited_recheck=dict(source='weather-calendar-complete-0041.json evidence[18]',instructions=n,new_business_recovery=0),windows=windows,checks=checks,clear_offsets=clear_offsets,strings=strings,limitations=['Static only, no target execution','No new REA Evidence ID; retained old stdout reused','Timer initializer and normal upper DELETE trigger not certified'])
(H/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(status='passed',windows=len(windows),bytes=sum(e-a for _,a,e in spans),instructions=sum(len(w['instructions']) for w in windows),checks=len(checks),inherited_instruction_rechecks=n)))
