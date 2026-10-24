"""F27 approved creator arguments and wrapper only; no open execution."""
import json
from pathlib import Path
import capstone
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin';BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[(0xa005f10a,0xa005f11a),(0xa01974de,0xa019750e)]
rows={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a);ins=list(md.disasm(data,a))
        assert sum(x.size for x in ins)==len(data)
        for x in ins:rows[x.address]={'pc':hex(x.address),'offset':hex(x.address-BASE),
            'raw':bytes(x.bytes).hex(),'asm':x.mnemonic+' '+x.op_str}
checks=[]
for pc,asm,meaning in [
 (0xa005f10a,'addi a4, s0, -0x50','creator attrs address'),
 (0xa005f10e,'addi a3, zero, 0x180','creator fourth argument value'),
 (0xa005f112,'c.li a2, 7','creator request arg2=7, not yet Q.word0'),
 (0xa005f114,'addi a1, s0, -0x40','creator local name/address argument'),
 (0xa005f118,'c.mv a0, s1','same Q saved by F15 creator'),
 (0xa01974e6,'c.sw a3, 0xc(s0)','pack original arg3'),
 (0xa01974e8,'c.sw a4, 0x10(s0)','pack original attrs address'),
 (0xa01974ea,'c.sw a5, 0x14(s0)','pack original arg5 without assigning its value'),
 (0xa01974ec,'addi a4, s0, 0xc','new arg4 points at packed original arg3'),
 (0xa01974f0,'c.li a5, 0','new arg5=0'),
 (0xa01974f2,'c.li a3, 0','new arg3=0'),
 (0xa01974f4,'c.li a2, 7','wrapper explicitly sets request7'),
 (0xa01974f6,'sw a6, 0x18(s0)','pack original arg6, value unknown'),
 (0xa01974fa,'sw a7, 0x1c(s0)','pack original arg7, value unknown'),
 (0xa01974fe,'sw a4, -0x14(s0)','local pack pointer bookkeeping'),
 (0xa019750c,'c.jr ra','wrapper returns after restoring frame, no a0 replacement'),
]:
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'])
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
pc=0xa0197502;v=w(pc)
imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
assert v&127==0x6f and pc+sx(imm,21)==0xa010e320
checks.append({'pc':hex(pc),'target':'0xa010e320','meaning':'independent JAL; new body is not part of this script'})
creator_path=MAIN/'reverse/analysis/miio-queue-size-gap-f15-0041-20261024/creator-evidence.json'
creator=json.loads(creator_path.read_text(encoding='utf-8'))
selected=[x for x in creator['rows'] if x['pc'] in ['0xa005f0c0','0xa005f0c4','0xa005f0c6','0xa005f0e4',
 '0xa005f11a','0xa005f11e','0xa005f122','0xa005f126','0xa005f12a','0xa005f144','0xa005f148']]
assert len(selected)==11
checks.append({'meaning':'necessary F15 Q/attrs/out identity rows inherited without rerunning its script'})
index_path=MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
idx=json.loads(index_path.read_text(encoding='utf-8'))
metadata=[]
for i,x in enumerate(idx['functions']):
    if x['address'] in ['0xa01974de','0xa010e320']:metadata.append({'pointer':'#/functions/'+str(i),'metadata':x})
assert len(metadata)==2
result={'claim':'F11/10','task':'F27','baseline':'bd457a6','static_only':True,
 'source':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset=VA-0x9ffff000','decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'bytes':sum(z-a for a,z in windows),'rows':list(rows.values()),'checks':checks,
 'inherited_creator':{'path':str(creator_path),'rows':selected},
 'metadata_source':str(index_path),'metadata':metadata,
 'conclusion':'same Q/name passed to lower service with request7, arg3=0,arg4=&packed original args,arg5=0; Q.word0 not written by wrapper',
 'limits':['Request7 has bit0x40 clear but is not proof of Q.word0 value',
 'No lower service/file-open/allocator execution or body in this parameter-only stage',
 'No formal bit names, later writer absence or runtime mode certification']}
dest=OUT/'parameter-evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'bytes':result['bytes']}))
