"""F31 independent4B review and minimum retained endpoint fields; no execution."""
import json
from pathlib import Path

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
p=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
assert p.stat().st_size==6769704
with p.open('rb') as f:
    f.seek(0xa010e43c-0x9ffff000); raw=f.read(4)
checks=[]
def check(name,a,b):
    assert a==b,(name,a,b)
    checks.append({'check':name,'value':a})
def sx(x,n):return x-(1<<n) if x&(1<<(n-1)) else x
w=int.from_bytes(raw[:2],'little')
check('C.ADDI fields',[w&3,w>>13,(w>>7)&31,sx(((w>>2)&31)|(((w>>12)&1)<<5),6)],[1,0,13,1])
w=int.from_bytes(raw[2:],'little')
imm=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
check('C.J fields/target',[w&3,w>>13,0xa010e43e+sx(imm,12)],[1,5,0xa010e38e])

oldpath=MAIN/'reverse/analysis/miio-queue-mode-init-review-f28-0041-20261024/review-evidence.json'
old=json.loads(oldpath.read_text(encoding='utf-8'))
rows={r['va']:r for r in old['anchors']}
addresses=['0xa010e344','0xa010e348','0xa010e38a','0xa010e38e','0xa010e392','0xa010e3fc']
def word(va):return int.from_bytes(bytes.fromhex(rows[va]['raw']),'little')
for va,rd,src in [('0xa010e344',19,10),('0xa010e348',22,12)]:
    w=word(va)
    check('inherited C.MV:'+va,[w&3,w>>13,(w>>12)&1,(w>>7)&31,(w>>2)&31],[2,4,0,rd,src])
w=word('0xa010e38a')
check('inherited constant47',[w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,sx(w>>20,12)],[19,15,0,0,47])
w=word('0xa010e38e')
check('inherited cursor LBU',[w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,sx(w>>20,12)],[3,14,4,13,0])
w=word('0xa010e392')
imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
check('inherited slash BEQ',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,0xa010e392+sx(imm,13)],[99,0,14,15,0xa010e43c])
check('inherited unequal fallthrough',0xa010e392+rows['0xa010e392']['width'],0xa010e396)
w=word('0xa010e3fc')
check('inherited Q word SW',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,sx(((w>>25)<<5)|((w>>7)&31),12)],[35,2,19,22,0])
check('new raw',raw.hex(),'850681bf')
out={'task':'F31','checks_pass':len(checks),'checks':checks,'new_ROM_bytes':4,
 'raw_anchors':[{'va':'0xa010e43c','offset':'0x10f43c','raw':raw[:2].hex()},{'va':'0xa010e43e','offset':'0x10f43e','raw':raw[2:].hex()}],
 'inherited_source':str(oldpath),'inherited_rows':[rows[v] for v in addresses],
 'local_effect':'new arm changes a3 only; inherited load changes a4; BEQ reads a4/a5; no s3/s6 definition, call, store or return in this finite loop',
 'limits':['only inherited normal exit/public write assumptions; no whole creation/return persistence','author exploratory80B not reread; extra76B excluded','no target/model/input execution']}
Path(__file__).with_name('evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} static checks; new4B; inherited6 anchors')
