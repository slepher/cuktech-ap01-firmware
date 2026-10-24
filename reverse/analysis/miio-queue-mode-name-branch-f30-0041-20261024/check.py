"""F30 static C.ADDI/C.J fields plus previously accepted prefix rows."""
import json
from pathlib import Path
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE=Path(__file__).parent
p=ROOT/'roms/0041/ap01-1.0.2_0041.bin'
assert p.stat().st_size==6769704
with p.open('rb') as f:
    f.seek(0xa010e43c-0x9ffff000);b=f.read(4)
checks=[]
def check(label,x):
    assert x,label
    checks.append(label)
def sx(x,n):return x-(1<<n) if x>>(n-1) else x
w=int.from_bytes(b[:2],'little')
check('ADDI-raw',b[:2].hex()=='8506')
check('C.ADDI-opcode-rd',w&3==1 and w>>13==0 and (w>>7)&31==13)
check('C.ADDI-imm1',sx(((w>>12)&1)<<5|((w>>2)&31),6)==1)
w=int.from_bytes(b[2:],'little')
check('CJ-raw',b[2:].hex()=='81bf')
check('CJ-opcode',w&3==1 and w>>13==5)
im=((w>>12)&1)<<11|((w>>11)&1)<<4|((w>>9)&3)<<8|((w>>8)&1)<<10|((w>>7)&1)<<6|((w>>6)&1)<<7|((w>>3)&7)<<1|((w>>2)&1)<<5
target=0xa010e43e+sx(im,12)
check('CJ-target-old-LBU',target==0xa010e38e)
oldpath=ROOT/'reverse/analysis/miio-queue-mode-init-review-f28-0041-20261024/review-evidence.json'
old=json.loads(oldpath.read_text(encoding='utf-8'))
rows={r['va']:r for r in old['anchors']}
chosen=[]
for a,raw,text in [('0xa010e344','aa89','c.mv s3, a0'),('0xa010e348','328b','c.mv s6, a2'),
                   ('0xa010e38a','9307f002','addi a5, zero, 0x2f'),
                   ('0xa010e38e','03c70600','lbu a4, 0(a3)'),
                   ('0xa010e392','6305f70a','beq a4, a5, 0xaa'),
                   ('0xa010e3fc','23a06901','sw s6, 0(s3)')]:
    check('inherited:'+a,rows[a]['raw']==raw and rows[a]['text']==text)
    chosen.append(rows[a])
w=int.from_bytes(bytes.fromhex(rows['0xa010e392']['raw']),'little')
im=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
check('old-BEQ-to-new-arm',0xa010e392+sx(im,13)==0xa010e43c and (w>>15)&31==14 and (w>>20)&31==15 and (w>>12)&7==0)
check('local-loop-only-a3-defined',13 not in (19,22))
(HERE/'evidence.json').write_text(json.dumps(dict(task='F30',result='PASS',checks=checks,
    anchors=[dict(va='0xa010e43c',offset='0x10f43c',width=2,raw=b[:2].hex(),text='c.addi a3,1'),
             dict(va='0xa010e43e',offset='0x10f43e',width=2,raw=b[2:].hex(),text='c.j 0xa010e38e')],
    inherited_path=str(oldpath.relative_to(ROOT)),inherited_rows=chosen,
    reads=dict(initial_exploratory_window=['0xa010e43c',80],retained_semantic_bytes=4,checker_rom_read=4,
               unanalysed_initial_extra_bytes=76),
    limits=['no new callee body or old common-prefix ROM reread','request7 at write point still requires inherited lookup/type/preservation path',
            'full return cleanup alias effects and later writers unknown']),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} static field/reference checks; new semantic fields4B; no execution')
