"""A81 independent static bitfields. Reads only authorized dispatcher24B."""
import json
from pathlib import Path
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE=Path(__file__).parent
rom=ROOT/'roms/0041/ap01-1.0.2_0041.bin'
assert rom.stat().st_size==6769704
with rom.open('rb') as f:
 f.seek(0xa00058ae-0x9ffff000);data=f.read(24)
checks=[];anchors=[]
def ck(label,v):
 assert v,label
 checks.append(label)
def sx(x,n):return x-(1<<n) if x>>(n-1) else x
def raw(a,n):return int.from_bytes(data[a-0xa00058ae:a-0xa00058ae+n],'little')
for a,f3,r1,r2,target in [(0xa00058ae,6,14,12,0xa00058c8),(0xa00058b4,0,12,15,0xa0005920),(0xa00058bc,0,12,14,0xa00058fe),(0xa00058c2,0,12,14,0xa000590e)]:
 w=raw(a,4); im=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
 ck('B-fields:'+hex(a),(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31)==(99,f3,r1,r2))
 ck('B-target:'+hex(a),a+sx(im,13)==target)
 anchors.append(dict(va=hex(a),offset=hex(a-0x9ffff000),raw=w.to_bytes(4,'little').hex(),width=4))
for a,rd,imm in [(0xa00058b2,15,2),(0xa00058b8,14,3),(0xa00058c0,14,1)]:
 w=raw(a,2)
 ck('CLI-fields:'+hex(a),(w&3,w>>13,(w>>7)&31,sx(((w>>12)&1)<<5|((w>>2)&31),6))==(1,2,rd,imm))
 anchors.append(dict(va=hex(a),offset=hex(a-0x9ffff000),raw=w.to_bytes(2,'little').hex(),width=2))
w=raw(0xa00058ba,2)
ck('CMV-a5-original-a0',(w&3,w>>12,(w>>7)&31,(w>>2)&31)==(2,8,15,10))
anchors.append(dict(va='0xa00058ba',offset='0x68ba',raw=w.to_bytes(2,'little').hex(),width=2))
ck('24B-exact-positions',sum(a['width'] for a in anchors)==24 and len(anchors)==8)
oldpath=ROOT/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
r=json.loads(oldpath.read_text(encoding='utf-8'))['records'][76]
ck('record76-EID',r['evidence_id']=='ev_32725e49dc86c4d072d48e396f5c14986a521284bea8c8ff59cd533fc995a848')
ck('record76-profile',r['analysis_profile']['digest']=='4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621')
oldrows=r['normalized_result']['assembly']
needed=[s for s in oldrows if 0xa000589c<=int(s.split(':')[0],16)<0xa00058ae or 0xa000590e<=int(s.split(':')[0],16)<0xa0005918]
f18path=ROOT/'reverse/analysis/miio-queue-copy4-review-f18-0041-20261024/evidence.json'
f18=json.loads(f18path.read_text(encoding='utf-8'))
frows={x['pc']:x for x in f18['rows']}
for a,rawhex in [('0xa000589c','9d47'),('0xa000590e','03c70500'),('0xa0005912','2380e700'),('0xa0005916','8280')]:
 ck('accepted-endpoint:'+a,frows[a]['raw']==rawhex)
ck('old-final-LBU','0xa000590e: lbu a4, 0x0, a1' in needed)
ck('old-final-SB','0xa0005912: sb a4, 0x0, a5' in needed)
ck('old-final-RET','0xa0005916: ret' in needed)
# Independent endpoint fields taken from accepted F18 retained bytes, no ROM reread.
w=int.from_bytes(bytes.fromhex(frows['0xa000590e']['raw']),'little')
ck('endpoint-LBU-width-base-offset',(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,w>>20)==(3,4,14,11,0))
w=int.from_bytes(bytes.fromhex(frows['0xa0005912']['raw']),'little')
ck('endpoint-SB-width-base-offset',(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,((w>>25)<<5)|((w>>7)&31))==(35,0,15,14,0))
(HERE/'review-evidence.json').write_text(json.dumps(dict(task='A81',result='PASS',checks=checks,
 rom_window=['0xa00058ae',24],anchors=sorted(anchors,key=lambda x:x['va']),
 inherited=dict(record76_path=str(oldpath.relative_to(ROOT)),eid=r['evidence_id'],profile=r['analysis_profile']['digest'],rows=needed,
                F18_path=str(f18path.relative_to(ROOT)),F18_rows=[frows[hex(a)] for a in [0xa000589c,0xa000589e,0xa00058a0,0xa00058a4,0xa00058a8,0xa00058aa,0xa000590e,0xa0005912,0xa0005916]]),
 limits=['n1 effective1B separated no interference only','no other short/bulk branch read','no target/input/model execution','no complete format output or storage-lifetime claim']),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} independent static checks; raw24B; endpoints inherited')
