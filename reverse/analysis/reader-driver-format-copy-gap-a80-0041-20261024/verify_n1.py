"""A80 authorized24B n1 dispatcher raw fields only; F18 endpoints inherited."""
import json
from pathlib import Path
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
p=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
assert p.stat().st_size==6769704
start=0xa00058ae
with p.open('rb') as f:
    f.seek(start-0x9ffff000); data=f.read(24)
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
ins=list(md.disasm(data,start))
assert len(ins)==8 and sum(i.size for i in ins)==24
checks=[]
def check(name,actual,expected):
    assert actual==expected,(name,actual,expected)
    checks.append({'name':name,'value':actual})
def sx(x,n): return x-(1<<n) if x&(1<<(n-1)) else x
def raw(pc,n): return int.from_bytes(data[pc-start:pc-start+n],'little')
expected=[(0xa00058ae,'bltu','a4, a2, 0x1a'),(0xa00058b2,'c.li','a5, 2'),
 (0xa00058b4,'beq','a2, a5, 0x6c'),(0xa00058b8,'c.li','a4, 3'),
 (0xa00058ba,'c.mv','a5, a0'),(0xa00058bc,'beq','a2, a4, 0x42'),
 (0xa00058c0,'c.li','a4, 1'),(0xa00058c2,'beq','a2, a4, 0x4c')]
for i,e in zip(ins,expected): check('decode:'+hex(i.address),(i.address,i.mnemonic,i.op_str),e)
for pc,f3,r1,r2,target in [(0xa00058ae,6,14,12,0xa00058c8),(0xa00058b4,0,12,15,0xa0005920),(0xa00058bc,0,12,14,0xa00058fe),(0xa00058c2,0,12,14,0xa000590e)]:
    w=raw(pc,4)
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    check('branch:'+hex(pc),[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,pc+sx(imm,13)],[99,f3,r1,r2,target])
for pc,rd,value in [(0xa00058b2,15,2),(0xa00058b8,14,3),(0xa00058c0,14,1)]:
    w=raw(pc,2)
    check('C.LI:'+hex(pc),[w&3,w>>13,(w>>7)&31,sx(((w>>2)&31)|(((w>>12)&1)<<5),6)],[1,2,rd,value])
w=raw(0xa00058ba,2)
check('dst to a5',[w&3,w>>13,(w>>12)&1,(w>>7)&31,(w>>2)&31],[2,4,0,15,10])
out={'task':'A80','new_raw_window':[hex(start),24],'checks_pass':len(checks),'checks':checks,
 'raw_anchors':[{'VA':hex(i.address),'offset':hex(i.address-0x9ffff000),'raw':i.bytes.hex()} for i in ins],
 'inherited_endpoints':'F18 accepted589c..58ae and590e..5918; no reread',
 'route':'n1:7<n false,n4 false,4<n false,n2 false,a5=dst,n3 false,n1 true->590e LBU/5912 SB/5916 RET',
 'limits':'valid separated byte source/destination; n1 only; no alignment/padding needed on this ordinary-byte route; no bounded bulk acceptance'}
Path(__file__).with_name('n1-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} raw checks;24B/8positions; endpoints inherited')
