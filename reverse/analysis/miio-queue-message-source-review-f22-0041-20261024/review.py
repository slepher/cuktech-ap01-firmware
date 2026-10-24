"""F22 independent original-field review of registered getter/list helper only."""
import json
from pathlib import Path
import capstone

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin';BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[(0xa01318de,0xa0131920),(0xa010d70e,0xa010d738)]
rows={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a);ins=list(md.disasm(data,a))
        assert sum(x.size for x in ins)==len(data)
        for x in ins:rows[x.address]={'pc':hex(x.address),'offset':hex(x.address-BASE),
            'raw':bytes(x.bytes).hex(),'asm':x.mnemonic+' '+x.op_str}
checks=[]
for pc,asm,meaning in [
 (0xa01318e6,'addi a0, gp, 0xb8','entry overwrites prior Q argument; first sentinel'),
 (0xa01318ee,'c.bnez a0, 0x14','first nonzero pointer returns directly'),
 (0xa01318f0,'lui a5, 0x62fc6','flag address upper'),
 (0xa01318f4,'lw a5, 0x34(a5)','flag reread after first sentinel empty'),
 (0xa01318f8,'c.beqz a5, 0x12','only zero flag to request branch'),
 (0xa01318fa,'addi a0, gp, 0xc0','second sentinel distinct from first'),
 (0xa0131902,'c.lwsp ra, 0xc(sp)','second service falls directly into epilogue'),
 (0xa0131908,'c.jr ra','preserve raw a0 result including second empty0'),
 (0xa013190a,'addi a0, zero, 0x14c','fixed request332, not n or Q'),
 (0xa0131916,'c.beqz a0, -0x14','request return0 skips marker'),
 (0xa0131918,'c.li a5, 1','marker value1'),
 (0xa013191a,'sb a5, 8(a0)','only byte marker M+8'),
 (0xa013191e,'c.j -0x1c','return original request-service a0'),
 (0xa010d714,'c.lw a5, 4(a0)','N from H+4'),
 (0xa010d716,'beq a5, a0, 0x1e','sentinel emptiness N==H'),
 (0xa010d71a,'c.lw a3, 4(a5)','first N.prev read'),
 (0xa010d71c,'c.lw a4, 0(a5)','N.next read'),
 (0xa010d71e,'c.sw a4, 0(a3)','previous.next=N.next'),
 (0xa010d720,'c.lw a3, 4(a5)','reread N.prev after prior write'),
 (0xa010d722,'c.sw a3, 4(a4)','next.prev=reread previous'),
 (0xa010d724,'sw zero, 4(a5)','first clear N+4'),
 (0xa010d728,'sw zero, 0(a5)','then clear N+0'),
 (0xa010d72e,'c.mv a0, a5','return original N register'),
 (0xa010d732,'c.jr ra','common helper return'),
 (0xa010d734,'c.li a5, 0','sentinel empty -> null return'),
 (0xa010d736,'c.j -0xa','empty joins common helper epilogue'),
]:
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'])
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
for pc,target in [(0xa01318ea,0xa010d70e),(0xa01318fe,0xa010d70e)]:
    v=w(pc);imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
    assert v&127==0x6f and pc+sx(imm,21)==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent JAL target'})
pc=0xa013190e
target=(pc+sx(w(pc)&0xfffff000,32)+sx(w(0xa0131912)>>20,12))&0xfffffffe
assert target==0xa002fcc8
checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent AUIPC/JALR; allocator body not read'})
v=w(0xa010d716);imm=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
assert 0xa010d716+sx(imm,13)==0xa010d734
checks.append({'pc':'0xa010d716','target':'0xa010d734','meaning':'independent B-format sentinel branch'})
for pc,expected in [(0xa010d724,4),(0xa010d728,0)]:
    v=w(pc);fields=(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,((v>>25)<<5)|((v>>7)&31))
    assert fields==(35,2,15,0,expected)
    checks.append({'pc':hex(pc),'fields':fields,'meaning':'independent S-format ordered clear'})
v=w(0xa013191a)
assert (v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,((v>>25)<<5)|((v>>7)&31))==(35,0,10,15,8)
checks.append({'pc':'0xa013191a','meaning':'independent S-format byte marker, not word or whole-node clear'})
helper=[x for pc,x in rows.items() if 0xa010d70e<=pc<0xa010d738]
assert all(not x['asm'].startswith(('jal ','jalr ','c.jalr ')) for x in helper)
checks.append({'meaning':'helper no callee; no allocation, copy service or callback on registered path'})

caller_path=MAIN/'reverse/analysis/miio-native-queue-f13-0041-20261024/evidence.json'
caller=json.loads(caller_path.read_text(encoding='utf-8'))
selected=[x for x in caller['rows'] if x['pc'] in
 ['0xa0197ac2','0xa0197ac6','0xa0197aca','0xa0197acc','0xa0197ad0',
  '0xa0197b12','0xa0197b14','0xa0197b16','0xa0197b18','0xa0197b1a']]
assert len(selected)==10
by_pc={x['pc']:x for x in selected}
assert by_pc['0xa0197aca']['asm']=='c.beqz a5, 0x1e'
assert by_pc['0xa0197acc']['asm']=='jal -0x661ee'
checks.append({'meaning':'inherited F13 caller enters getter only when its first flag read is nonzero',
               'limit':'getter reread need not be stable; this is not allocator-branch unreachability proof'})
result={'claim':'F11/7','review':'F22','reviewer':'/root/f12','baseline':'bd457a6',
 'static_only':True,'rom':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset=VA-0x9ffff000','decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'bytes':sum(z-a for a,z in windows),'rows':list(rows.values()),'checks':checks,
 'inherited_caller':{'path':str(caller_path),'rows':selected},
 'decision':'limited acceptance; semantic correction0; new business0',
 'limits':['Normal valid sentinel/node pointers and service ABI preconditions; no whole-system exclusivity',
 'gp absolute base, pools initialization and node capacity unknown',
 '332-byte request is not successful allocation or320-byte usable storage certification',
 'Caller/getter flag reads and pool accesses not proven stable/nonaliasing/asynchronous-safe',
 'No allocator/pool initializer/scheduler body or actual execution']}
dest=OUT/'evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'bytes':result['bytes'],'positions':len(rows)}))
