"""D22 bounded local-source and ROM-field review. Never executes firmware."""
from pathlib import Path
import json
import subprocess

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=0x9ffff000
ROM=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
old=json.loads((ROOT/'reverse/analysis/backlight-animation-d19-0041-20261024/instruction-windows.json').read_text())
sources=json.loads((ROOT/'reverse/analysis/backlight-animation-source-d21-0041-20261024/candidate-excerpts.json').read_text())
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
def store(pc,f3,src,base,offset):
    v=w(pc)
    eq(hex(pc)+' store fields',(v&127,(v>>12)&7,(v>>20)&31,(v>>15)&31,sx(((v>>25)<<5)|((v>>7)&31),12)),(35,f3,src,base,offset))
def cls(pc,is_store,reg,base,offset):
    v=w(pc,2)
    eq(hex(pc)+' compressed word',(v&3,v>>13,8+((v>>2)&7),8+((v>>7)&7),((v>>10)&7)*8+((v>>6)&1)*4+((v>>5)&1)*64),(0,6 if is_store else 2,reg,base,offset))
def mv(pc,rd,r2):
    v=w(pc,2)
    eq(hex(pc)+' C.MV',(v&3,v>>12,(v>>7)&31,(v>>2)&31),(2,8,rd,r2))
def branch(pc,f3,r1,r2,target):
    v=w(pc)
    off=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
    eq(hex(pc)+' branch',(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,pc+sx(off,13)),(99,f3,r1,r2,target))
def call(pc,target):
    v=w(pc)
    off=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
    eq(hex(pc)+' JAL',(v&127,(v>>7)&31,pc+sx(off,21)),(111,1,target))
names={'exec-byte-argument','exec-style-binding','init-clear-and-defaults','start-copy-96','start-immediate-dispatch','tick-completion','tick-repeat'}
selected=[r for r in old if r['name'] in names]
eq('selected bounded window count',len(selected),7)
for r in selected: eq(r['name']+' retained raw',raw(int(r['start'],16),len(bytes.fromhex(r['hex']))).hex(),r['hex'])
imm(0xa00f43c4,19,7,11,11,255)
call(0xa00f43c8,0xa018fb3c)
mv(0xa018fb44,12,11)
v=w(0xa018fb46)
eq('selector LUI',(v&127,(v>>7)&31,v&0xfffff000),(55,13,0x20000))
imm(0xa018fb4a,19,0,11,0,0x3e)
call(0xa018fb4e,0xa00df94c)
imm(0xa008df46,19,0,11,0,96)
imm(0xa008bfe6,19,0,12,0,96)
imm(0xa008df6a,3,4,15,9,0x5c)
imm(0xa008df72,19,6,15,15,16)
store(0xa008df76,0,15,9,0x5c)
for a,reg,base,offset in [(0xa008c044,15,9,32),(0xa008c04a,15,9,4),(0xa008c052,10,9,0),(0xa008c1cc,11,9,0x34),(0xa008c1ce,13,9,0x30),(0xa008c248,11,9,0x40)]: cls(a,False,reg,base,offset)
mv(0xa008c046,10,9)
eq('path C.JALR',w(0xa008c048,2),0x9782)
cls(0xa008c04c,True,10,9,0x28)
mv(0xa008c04e,11,10)
eq('exec C.JALR',w(0xa008c054,2),0x9782)
branch(0xa008c1d0,4,11,13,0xa008c20a)
branch(0xa008c232,0,14,19,0xa008c23e)
branch(0xa008c240,5,13,11,0xa008c248)
v=w(0xa008c244)
eq('excess signed SUB',(v&127,v>>25,(v>>12)&7,(v>>7)&31,(v>>15)&31,(v>>20)&31),(51,32,0,14,11,13))
eq('delay C.SUB',w(0xa008c24a,2),0x8f0d)
cls(0xa008c24c,True,14,9,0x34)
# Only sparse early-apply gate anchors absent from the old retained windows.
extra=[(0xa008c018,'83c7c405'),(0xa008c026,'c18b85cf')]
for pc,h in extra: eq(hex(pc)+' supplemental raw',raw(pc,len(bytes.fromhex(h))).hex(),h)
imm(0xa008c018,3,4,15,9,0x5c)
v=w(0xa008c026,2)
eq('early_apply C.ANDI',(v&3,v>>13,(v>>10)&3,8+((v>>7)&7),sx((((v>>12)&1)<<5)|((v>>2)&31),6)),(1,4,2,15,16))
v=w(0xa008c028,2)
off=(((v>>12)&1)<<8)|(((v>>10)&3)<<3)|(((v>>5)&3)<<6)|(((v>>3)&3)<<1)|(((v>>2)&1)<<5)
eq('early_apply zero gate',(v&3,v>>13,8+((v>>7)&7),0xa008c028+sx(off,9)),(1,6,15,0xa008c060))
remote=r'''from pathlib import Path
import sys,json,zipfile
items=json.load(sys.stdin)
root=Path('/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl')
result=[]
with zipfile.ZipFile(root.parent/'v9.2.1.zip') as z:
 for item in items:
  p=Path(item['path']); data=p.read_bytes(); lines=data.decode().splitlines()
  assert data==z.read('lvgl-9.2.1/'+str(p.relative_to(root)))
  count=0
  for ex in item['excerpts']:
   got=[str(i+1)+': '+lines[i] for i in range(ex['first']-1,ex['last'])]
   assert got==ex['lines'],str(p)
   count+=len(got)
  result.append({'path':str(p),'retained_lines_equal':count,'local_zip_member_equal':True})
p=root/'src/misc/lv_anim.h'; lines=p.read_text().splitlines()
extra=[str(i+1)+': '+lines[i] for i in range(113,122)]
assert all(any('int16_t '+f+';' in line for line in extra) for f in ['x1','y1','x2','y2'])
print(json.dumps({'comparisons':result,'supplemental_bezier_lines':extra}))
'''
p=subprocess.run(['wsl.exe','-d','Ubuntu-24.04','--exec','python3','-c',remote],input=json.dumps(sources).encode(),capture_output=True)
assert p.returncode==0,p.stderr.decode(errors='replace')+p.stdout.decode(errors='replace')
source_result=json.loads(p.stdout)
eq('candidate file count',len(source_result['comparisons']),7)
# Conditional ordinary RV32 arithmetic, not a compiler sizeof test.
eq('candidate flags offset',9*4+9*4+4*2+4,0x54)
eq('candidate aligned size',((0x54+1+3)//4)*4,88)
result={'status':'PASS','static_only':True,'checks':checks,'retained_rom_windows_compared':[r['name'] for r in selected],'source_review':source_result,'supplemental_rom_bytes':[{'pc':hex(a),'raw':h} for a,h in extra],'new_rom_functionality':0,'limits':['88B and low-bit-first bitfield layout are conditional ABI calculations, not compiled layout measurements.','Local source/ZIP equality does not establish exact ROM version, compiler inputs or remote provenance.','No style engine, actual rendering or target/context lifetime certification.']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':'PASS','checks':len(checks),'rom_windows':len(selected),'source_files':len(source_result['comparisons']),'supplemental_rom_bytes':sum(len(bytes.fromhex(h)) for _,h in extra)}))
