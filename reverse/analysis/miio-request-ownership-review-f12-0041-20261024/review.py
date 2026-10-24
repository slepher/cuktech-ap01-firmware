"""F12 independent static checks: read only selected 0041 instruction windows.

No author checker imports, target execution, emulation, database/model mutation.
"""
import json
from pathlib import Path
import capstone

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
assert ROM.stat().st_size == 6769704
md = capstone.Cs(capstone.CS_ARCH_RISCV,
                 capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
# Deliberately bounded samples at the ownership transitions, not whole functions.
windows = [
 (0xa01b6304,0xa01b632e), (0xa0112052,0xa0112066),
 (0xa011f9ea,0xa011f9f8), (0xa011fa14,0xa011fa1e),
 (0xa011f886,0xa011f892), (0xa011f8a4,0xa011f8a8),
 (0xa011f8f6,0xa011f93a), (0xa011f93e,0xa011f956),
 (0xa011f956,0xa011f96c), (0xa011f992,0xa011f9a8),
 (0xa011f622,0xa011f65c), (0xa011f674,0xa011f678),
 (0xa011f850,0xa011f85a), (0xa011f862,0xa011f864),
 (0xa011f79a,0xa011f79c), (0xa011f818,0xa011f832),
 (0xa011f73a,0xa011f744), (0xa0119ca2,0xa0119ca8),
 (0xa0119d02,0xa0119d2c), (0xa0119d2c,0xa0119d3e),
 (0xa0119768,0xa011978a), (0xa0116cf0,0xa0116d18),
 (0xa01ab838,0xa01ab844), (0xa01ab850,0xa01ab862),
 (0xa011f6a0,0xa011f6d8), (0xa005f22a,0xa005f236),
 (0xa0119b7e,0xa0119b9c), (0xa0119ba6,0xa0119bb6),
 (0xa011972a,0xa011973c),
]
rows = {}
with ROM.open('rb') as f:
    for start,end in windows:
        f.seek(start-BASE)
        data=f.read(end-start)
        decoded=list(md.disasm(data,start))
        assert sum(i.size for i in decoded)==len(data), hex(start)
        for i in decoded:
            rows[i.address]={'pc':hex(i.address),'file_offset':hex(i.address-BASE),
                'raw':bytes(i.bytes).hex(),'asm':i.mnemonic+' '+i.op_str}
    f.seek(0xa011f93a-BASE)
    vendor=f.read(4)

checks=[]
def expect(pc,asm,reason):
    actual=rows[pc]['asm']
    assert actual==asm,(hex(pc),actual,asm)
    checks.append({'pc':hex(pc),'observed':actual,'reason':reason})

for pc,asm,reason in [
 (0xa01b6308,'addi a5, a5, 0x222','callback constant following LUI a005f'),
 (0xa01b631c,'sw a5, -0x28(s0)','D+2c callback'),
 (0xa01b6320,'sw s1, -0x24(s0)','D+30 user'),
 (0xa01b6326,'addi a1, s0, -0x54','D stack descriptor'),
 (0xa0112052,'c.lw a3, 0x30(s1)','user read'),
 (0xa0112054,'c.lw a2, 0x2c(s1)','callback read'),
 (0xa011205c,'addi a1, s1, 4','Q is D+4'),
 (0xa011f9f0,'c.li a2, 8','adapter clear length'),
 (0xa011f9f2,'c.li a1, 0','adapter clear byte'),
 (0xa011f9f4,'addi a0, s1, 0x10','adapter clear Q+10'),
 (0xa011f888,'c.mv s2, a1','constructor Q register'),
 (0xa011f88a,'c.mv s3, a2','constructor callback register'),
 (0xa011f88c,'c.mv s7, a3','constructor user register'),
 (0xa011f8f6,'lw a5, 0(s2)','load Q.id'),
 (0xa011f900,'c.sw a5, 4(s1)','store R.id'),
 (0xa011f902,'lbu a5, 0xc(s2)','load Q kind byte'),
 (0xa011f90a,'sb a5, 0x10(s1)','store R kind byte'),
 (0xa011f8fc,'addi a1, s2, 0x10','8B source'),
 (0xa011f906,'addi a0, s1, 0x14','8B destination'),
 (0xa011f916,'lw a0, 0x1c(s2)','load Q.len'),
 (0xa011f91a,'c.sw a0, 0x20(s1)','store R.len'),
 (0xa011f91e,'c.addi a0, 1','allocation size len+1'),
 (0xa011f924,'c.sw a0, 0x24(s1)','owned message pointer'),
 (0xa011f928,'c.lw a2, 0x20(s1)','message copy length'),
 (0xa011f92a,'lw a1, 0x20(s2)','message copy source'),
 (0xa011f936,'c.lw a4, 0x24(s1)','vendor store base'),
 (0xa011f938,'c.lw a5, 0x20(s1)','vendor store index'),
 (0xa011f93e,'sw s3, 0x2c(s1)','store callback'),
 (0xa011f942,'sw s7, 0x30(s1)','store user pointer'),
 (0xa011f94e,'beqz s5, 8','zero input skips R+34 assignment'),
 (0xa011f952,'sw s5, 0x34(s1)','conditional R+34 word'),
 (0xa011f95e,'c.li a2, 8','invocation payload size'),
 (0xa011f996,'sw s4, 0(a0)','payload ctx'),
 (0xa011f99a,'c.sw s1, 4(a0)','payload R'),
 (0xa011f622,'c.addi a2, 3','allocation alignment add'),
 (0xa011f624,'c.andi a2, -4','allocation alignment mask'),
 (0xa011f626,'c.addi a2, 0x18','allocation prefix'),
 (0xa011f64c,'c.sw a5, 4(s1)','I dispatcher slot'),
 (0xa011f650,'sb a5, 8(s1)','I type byte'),
 (0xa011f654,'sw s2, 0xc(s1)','I loop'),
 (0xa011f658,'sw s3, 0x10(s1)','I executor'),
 (0xa011f674,'c.addi a0, 0x1b','payload alignment add'),
 (0xa011f676,'c.andi a0, -4','payload alignment mask'),
 (0xa011f852,'c.sw a1, 0x14(a0)','I submit parameter'),
 (0xa011f856,'c.addi a0, 4','dispatcher receives I+4'),
 (0xa011f862,'c.jalr a5','indirect dispatcher call'),
 (0xa011f79a,'c.bnez a0, 0x7e','prior nonzero branch reaches f818'),
 (0xa011f81a,'c.lw a4, 0x34(a5)','message lifetime first gate'),
 (0xa011f81c,'c.bnez a4, 0x16','nonzero R+34 skips to f832'),
 (0xa011f81e,'c.lw a0, 0x24(a5)','message passed as a0'),
 (0xa011f820,'c.beqz a0, 0x12','null message skips'),
 (0xa011f826,'c.lw a5, 4(s1)','reload R after return service'),
 (0xa011f828,'sw zero, 0x24(a5)','first clear message slot'),
 (0xa011f82c,'c.lw a5, 4(s1)','second reload R'),
 (0xa011f82e,'sw zero, 0x24(a5)','second clear same slot'),
 (0xa011f73a,'c.lw a2, 4(s1)','worker passes payload R'),
 (0xa011f73c,'c.lw a0, 0(s1)','worker passes payload ctx'),
 (0xa011f73e,'c.li a1, 0','session kind 0'),
 (0xa0119ca6,'c.mv s5, a2','preserve request R'),
 (0xa0119d10,'sw s2, 4(s1)','session ctx'),
 (0xa0119d18,'sw s1, 0x20(s2)','ctx chain head'),
 (0xa0119d1c,'sb s3, 8(s1)','session kind'),
 (0xa0119d26,'sw s5, 0x10(s1)','session stores original R'),
 (0xa0119d3a,'c.sw s1, 0(a4)','nonempty chain tail insertion'),
 (0xa0119772,'addi a1, a1, -0x316','predicate address low'),
 (0xa0119776,'sw s3, -0x2c(s0)','criterion id'),
 (0xa011977a,'sb s2, -0x30(s0)','criterion kind'),
 (0xa011977e,'sw zero, -0x28(s0)','criterion output starts null'),
 (0xa0119786,'lw a0, -0x28(s0)','lookup returns output'),
 (0xa0116cf0,'lbu a4, 8(a0)','predicate session kind'),
 (0xa0116cfc,'c.lw a5, 0x10(a0)','predicate session R'),
 (0xa0116d00,'c.lw a3, 4(a5)','predicate R.id'),
 (0xa0116d08,'c.sw a0, 8(a1)','matched P stored in output'),
 (0xa0116d0a,'c.li a5, -1','match returns nonzero -1'),
 (0xa01ab840,'beqz a0, 0x10','traversal continues only on zero'),
 (0xa01ab856,'c.mv a0, s1','predicate arg0 P'),
 (0xa01ab858,'c.jalr s2','predicate indirect call'),
 (0xa01ab85e,'c.lw s1, 0(s1)','next read after callback'),
 (0xa011f6ae,'c.lw a5, 0x10(a0)','matched session R'),
 (0xa011f6b2,'c.lw a0, 4(s1)','callback receives S'),
 (0xa011f6b4,'c.lw a1, 0x30(a5)','callback user from R'),
 (0xa011f6b6,'c.lw a4, 0x2c(a5)','callback function from R'),
 (0xa011f6b8,'c.addi a0, 4','callback view S+4'),
 (0xa011f6ba,'c.jalr a4','synchronous indirect callback'),
 (0xa011f6c4,'c.mv a0, s2','then session return argument'),
 (0xa011f6d2,'c.lw a0, 4(s1)','then S return argument'),
 (0xa005f22a,'c.lw a1, 0x1c(a0)','view length replaces user'),
 (0xa005f22c,'c.lw a0, 0x20(a0)','view message'),
 (0xa0119b90,'c.lw a0, 0x10(a0)','session R passed to return'),
 (0xa0119b96,'c.mv a0, s1','then session P itself'),
]: expect(pc,asm,reason)

def jal(pc,target):
    w=int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
    assert w&127==0x6f
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    if imm&(1<<20):imm-=1<<21
    assert pc+imm==target,(hex(pc),hex(pc+imm),hex(target))
    checks.append({'pc':hex(pc),'target':hex(target),'reason':'independent JAL bit decode'})
for pc,target in [(0xa01b632a,0xa0111ff6),(0xa0112062,0xa011f9da),
 (0xa011fa1a,0xa011f86c),(0xa011f964,0xa011f610),
 (0xa011f9a0,0xa011f84a),(0xa011f822,0xa002e14e),
 (0xa011f740,0xa0119c8e),(0xa0119782,0xa01ab82c),
 (0xa011f6a8,0xa0119748),(0xa011f6c6,0xa0119b72),
 (0xa011f6d4,0xa0119720),(0xa0119b92,0xa0119720),
 (0xa0119b98,0xa002e14e)]:jal(pc,target)

w=int.from_bytes(vendor,'little')
fields={'opcode':w&127,'f3':(w>>12)&7,'rd':(w>>7)&31,
        'base':(w>>15)&31,'index':(w>>20)&31,'top5':w>>27,'shift':(w>>25)&3}
assert fields==dict(opcode=11,f3=5,rd=0,base=14,index=15,top5=0,shift=0)
checks.append({'pc':'0xa011f93a','raw':vendor.hex(),'fields':fields,
 'reason':'matches inherited local th.srb byte store rule; not independent vendor ISA authentication'})
assert 0xa0117000-0x316==0xa0116cea
# Independently decode both full-width stores: preserve repeated read/clear ordering.
for pc in (0xa011f828,0xa011f82e):
    w=int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
    assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,((w>>25)<<5)|((w>>7)&31))==(35,2,15,0,0x24)
    checks.append({'pc':hex(pc),'reason':'independent S-format: SW x0,0x24(x15)'})

# Retained evidence is read, not produced anew, and only needed transition rows retained.
retained_path=MAIN/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
retained=json.loads(retained_path.read_text(encoding='utf-8'))
old=[]
for idx,lo,hi in [(13,0xa011f89c,0xa011f8aa),(142,0xa011f726,0xa011f73a),
                  (142,0xa011f79a,0xa011f79e),(142,0xa011f838,0xa011f84a),
                  (204,0xa0119720,0xa011973c)]:
    r=retained['records'][idx]
    selected=[s for s in r['normalized_result']['assembly'] if lo<=int(s.split(':')[0],16)<hi]
    assert selected
    old.append({'record':idx,'evidence_id':r['evidence_id'],
        'profile_digest':r['analysis_profile']['digest'],'assembly':selected})

result={'claim_ids':['F11/1','F11/2'],'reviewer':'/root/f12','baseline':'32f9c9e',
 'static_only':True,'rom':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset = VA - 0x9ffff000','decoder':'Capstone '+capstone.__version__,
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'read_instruction_bytes':sum(z-a for a,z in windows)+4,
 'instructions':list(rows.values()),'checks':checks,'retained':old,
 'new_business_functionality':0,'conclusion':'bounded independent acceptance; no semantic correction',
 'limitations':['No native queue body or execution guarantee','No ID uniqueness or concrete runtime instance identity',
 'No allocator or physical free observation','Vendor store meaning inherits existing local profile rule',
 'No full function, whole ROM, locking, timeout/cancellation, or service-success certification']}
dest=OUT/'evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'instructions':len(rows),
 'instruction_bytes':result['read_instruction_bytes'],'output':str(dest)}))
