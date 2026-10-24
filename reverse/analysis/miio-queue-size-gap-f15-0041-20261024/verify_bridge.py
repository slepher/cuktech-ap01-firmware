"""F15 approved attach ctx+4 bridge plus necessary retained callback rows."""
import json
from pathlib import Path
import capstone

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[(0xa01ab564,0xa01ab58e),(0xa01ab5d4,0xa01ab5e4),(0xa01ab61c,0xa01ab634)]
rows={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a)
        ins=list(md.disasm(data,a));assert sum(x.size for x in ins)==len(data)
        for x in ins:rows[x.address]={'pc':hex(x.address),'file_offset':hex(x.address-BASE),
            'raw':bytes(x.bytes).hex(),'asm':x.mnemonic+' '+x.op_str}
checks=[]
for pc,asm,meaning in [
 (0xa01ab564,'c.mv s1, a1','preserve ctx'),
 (0xa01ab568,'c.mv s2, a0','preserve L'),
 (0xa01ab56a,'c.li a2, 0xc','12B clear call length only'),
 (0xa01ab56c,'c.li a1, 0','clear byte argument'),
 (0xa01ab56e,'c.mv a0, s1','clear call targets same ctx'),
 (0xa01ab586,'lw a5, 0xc(s2)','thread-id gate reads same L'),
 (0xa01ab58a,'beq a5, a0, 0x4a','normal matching thread to attach list'),
 (0xa01ab5d4,'lw a5, 0x1c(s2)','same L watcher head'),
 (0xa01ab5d8,'c.bnez a5, 0xe','nonempty head to traversal'),
 (0xa01ab5da,'sw s1, 0x1c(s2)','empty list publishes ctx'),
 (0xa01ab5de,'sw s2, 4(s1)','ctx+4 receives same L'),
 (0xa01ab5e2,'c.j 0x3a','normal common return'),
 (0xa01ab628,'c.lw a4, 0(a5)','traverse existing next'),
 (0xa01ab62a,'c.bnez a4, -0x46','nonzero next to compare/traversal'),
 (0xa01ab62c,'sw zero, 0(s1)','new tail next null'),
 (0xa01ab630,'c.sw s1, 0(a5)','publish ctx at tail'),
 (0xa01ab632,'c.j -0x54','tail joins ctx+4 write'),
]:
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'])
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
v=w(0xa01ab5de)
fields=(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,((v>>25)<<5)|((v>>7)&31))
assert fields==(35,2,9,18,4)
checks.append({'pc':'0xa01ab5de','fields':fields,'meaning':'independent S-format word store L to ctx+4'})
v=w(0xa01ab58a)
imm=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
assert 0xa01ab58a+sx(imm,13)==0xa01ab5d4
checks.append({'pc':'0xa01ab58a','target':'0xa01ab5d4','meaning':'independent B-format'})

source=MAIN/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
upper=json.loads(source.read_text(encoding='utf-8'))
specs={
 248:[(0xa0064da6,0xa0064daa),(0xa0064f4a,0xa0064f4e),
      (0xa00653ac,0xa006540a),(0xa006548e,0xa0065492),(0xa006549e,0xa00654a2)],
 195:[(0xa011e3ee,0xa011e400),(0xa011e428,0xa011e430)],
 96:[(0xa011e08e,0xa011e0a0)],27:[(0xa0110700,0xa011071c)]}
retained=[];old_rows={}
for idx,bounds in specs.items():
    r=upper['records'][idx];n=r['normalized_result']
    selected=[s for s in n['assembly'] if any(a<=int(s.split(':')[0],16)<z for a,z in bounds)]
    assert selected
    for s in selected:old_rows[int(s.split(':')[0],16)]=s
    retained.append({'record':idx,'procedure':n['procedure']['address'],
       'evidence_id':r['evidence_id'],'profile':r['analysis_profile']['digest'],'assembly':selected})
for pc,asm in [
 (0xa0064da6,'addi s10, s1, 0xe8'),(0xa0064f4a,'addi s7, s1, 0x128'),
 (0xa00653b0,'addi a5, a5, 0x6f2'),(0xa00653b4,'sw a5, -0x128, s0'),
 (0xa00653d8,'sw s10, -0x11c, s0'),(0xa00653e8,'sw a5, 0x158, s1'),
 (0xa00653fe,'sw s7, 0x160, s1'),(0xa0065402,'addi a0, s1, 0x164'),
 (0xa0065406,'jal ra, 0xa000589c'),(0xa006549e,'sw a5, 0x138, s1'),
 (0xa011e3f8,'c.lw a4, 0x10, s1'),(0xa011e3fc,'c.lw a5, 0x0, a4'),
 (0xa011e428,'c.lw a1, 0x8, a4'),(0xa011e42a,'c.mv a0, s1'),
 (0xa011e42c,'c.jalr a5'),(0xa011e08e,'c.lw a5, 0x3c, a1'),
 (0xa011e09a,'c.mv a0, a1'),(0xa011e09c,'c.lw a1, 0x48, a1'),
 (0xa011e09e,'c.jalr a5'),(0xa0110700,'c.mv s1, a1'),
 (0xa0110702,'addi a1, a1, 0x8c'),(0xa0110706,'c.mv s2, a0'),
 (0xa0110708,'jal ra, 0xa01ab55a'),(0xa011070e,'addi a5, a5, -0x780'),
 (0xa0110712,'c.add s1, a5'),(0xa0110714,'c.mv a1, s1'),
 (0xa0110716,'c.mv a0, s2'),(0xa0110718,'jal ra, 0xa01ab55a'),
]:
    assert old_rows[pc]==hex(pc)+': '+asm,(hex(pc),old_rows[pc])
    checks.append({'pc':hex(pc),'retained_assembly':old_rows[pc],'meaning':'retained callback identity bridge'})
assert 0xe8+0x8c==0x174 and 0xe8+0x880==0x968
checks.append({'meaning':'same master instance two ctx addresses',
 'first':'M+0xe8+0x8c=M+0x174','second':'M+0xe8+0x880=M+0x968'})
result={'claim':'F11/4','task':'F15','baseline':'bd457a6','static_only':True,
 'source':str(ROM),'length':ROM.stat().st_size,'mapping':'file_offset=VA-0x9ffff000',
 'decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'discovery_bytes':140,'sample_bytes':sum(z-a for a,z in windows),
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'rows':list(rows.values()),'checks':checks,'retained_source':str(source),'retained':retained,
 'conclusion':'On the identified normal setup/attach path, ctx at M+174 and M+968 both save L=M+128 at ctx+4',
 'limits':['Callback configuration copy16 inherits its aligned valid-storage preconditions',
 'Normal matching-thread/attach path only, not arbitrary callback/duplicate branch',
 'Static same master-instance bridge, not observed runtime execution or later-writer absence',
 'No copy4B algorithm or queue lifetime certification']}
dest=OUT/'bridge-evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'sample_bytes':result['sample_bytes']}))
