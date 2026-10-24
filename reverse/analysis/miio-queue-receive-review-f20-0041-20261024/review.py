"""F20 independent normal finite/nonempty receive review; no F19 script run."""
import json
from pathlib import Path
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
assert ROM.stat().st_size==6769704
checks=[];anchors=[]
def check(label,x,want):
    assert x==want,(label,x,want)
    checks.append(dict(label=label,value=x))
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def raw(a,n):
    assert any(lo<=a and a+n<=hi for lo,hi in [
     (0xa005f518,0xa005f5a8),(0xa0197986,0xa0197a78),
     (0xa0131a02,0xa0131a46),(0xa0131b68,0xa0131baa)])
    with ROM.open('rb') as f:f.seek(a-0x9ffff000);return f.read(n)
d=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
def inst(a,text):
    n=4 if int.from_bytes(raw(a,2),'little')&3==3 else 2
    b=raw(a,n);r=list(d.disasm(b,a))
    check(hex(a),[v.mnemonic+' '+v.op_str for v in r],[text])
    anchors.append(dict(address=hex(a),raw=b.hex(),decode=text))
def mem(a,op,f,base,reg,imm):
    w=int.from_bytes(raw(a,4),'little')
    q=((w>>25)<<5)|((w>>7)&31) if op==0x23 else w>>20
    r=(w>>20)&31 if op==0x23 else (w>>7)&31
    check('independent memory '+hex(a),(w&127,(w>>12)&7,(w>>15)&31,r,sx(q,12)),(op,f,base,reg,imm))
def jal(a,target):
    w=int.from_bytes(raw(a,4),'little')
    q=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    check('independent JAL '+hex(a),(w&127,(w>>7)&31,a+sx(q,21)),(0x6f,1,target))
def pair(a,target):
    w=int.from_bytes(raw(a,4),'little');v=int.from_bytes(raw(a+4,4),'little')
    check('pair selectors '+hex(a),(w&127,(w>>7)&31,v&127,(v>>12)&7,(v>>7)&31,(v>>15)&31),(0x17,1,0x67,0,1,1))
    dest=(a+sx(w&0xfffff000,32)+sx(v>>20,12))&0xfffffffe
    check('pair target '+hex(a),dest,target)
    anchors.append(dict(address=hex(a),raw=raw(a,8).hex(),kind='independent-auipc-jalr',target=hex(target)))

# Old caller records, selected lines only. Do not import/run locator or old code.
p=MAIN/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
r=json.loads(p.read_text(encoding='utf8'))['records'][195]
check('old caller identity',r['normalized_result']['procedure']['address'],'0xa011e3d6')
a=r['normalized_result']['assembly'];old=[]
for pc,text in {
 '0xa011e408':'c.lui s7, 0x2','0xa011e416':'addi s7, s7, 0x710',
 '0xa011e518':'c.lw a5, 0x2c, s1','0xa011e51a':'sw zero, -0x34, s0',
 '0xa011e51e':'c.beqz a5, 0xa011e5ea','0xa011e5ec':'c.mv a2, s7',
 '0xa011e5f0':'c.lw a2, 0x4, a5','0xa011e5f2':'c.lw a0, 0x18, s1',
 '0xa011e5f6':'addi a1, s0, -0x34','0xa011e5fa':'jal ra, 0xa005f508',
 '0xa011e5fe':'c.j 0xa011e548','0xa011e548':'lw a1, -0x34, s0',
 '0xa011e54c':'beq a1, zero, 0xa011e41a','0xa011e550':'lbu s2, 0x8, a1',
}.items():
    line=next(t for t in a if t.startswith(pc+':'))
    check('old '+pc,line,pc+': '+text);old.append(line)
check('default timeout constant',(2<<12)+0x710,10000)

for pc,text in {
 0xa005f518:'c.li a5, -1',0xa005f51a:'c.mv s2, a0',0xa005f51c:'c.mv s1, a2',
 0xa005f51e:'bne a2, a5, 0x1e',0xa005f536:'c.srai a0, 0x1f',
 0xa005f53c:'c.mv s3, a1',0xa005f53e:'c.li a0, 0',
 0xa005f540:'addi a1, s0, -0x28',0xa005f548:'addi a2, zero, 0x3e8',
 0xa005f54c:'divu a4, s1, a2',0xa005f550:'lw a5, -0x28(s0)',
 0xa005f554:'lui a3, 0xf4',0xa005f558:'addi a3, a3, 0x240',
 0xa005f55c:'remu s1, s1, a2',0xa005f560:'c.add a4, a5',
 0xa005f562:'lw a5, -0x24(s0)',0xa005f566:'sw a4, -0x28(s0)',
 0xa005f56e:'lui a3, 0x3b9ad',0xa005f572:'addi a3, a3, -0x601',
 0xa005f576:'sw a5, -0x24(s0)',0xa005f57a:'bge a3, a5, 0x18',
 0xa005f57e:'c.addi a4, 1',0xa005f580:'sw a4, -0x28(s0)',
 0xa005f584:'lui a4, 0xc4653',0xa005f588:'addi a4, a4, 0x600',
 0xa005f58c:'c.add a5, a4',0xa005f58e:'sw a5, -0x24(s0)',
 0xa005f592:'lw a2, 0x18(s2)',0xa005f596:'addi a3, s0, -0x28',
 0xa005f59a:'c.mv a1, s3',0xa005f59c:'c.mv a0, s2',0xa005f5a6:'c.j -0x7a',
 0xa0197986:'c.lw a5, 0xc(a0)',0xa0197988:'c.mv s1, a0',
 0xa019798e:'lw s2, 0x18(a5)',0xa019799c:'lhu a5, 0x24(s2)',
 0xa01979ba:'c.mv s5, a1',0xa01979bc:'c.li s4, 8',
 0xa01979be:'csrrc s4, mstatus, s4',0xa01979c2:'lw a4, 0x1c(s2)',
 0xa01979c6:'addi a5, s2, 0x18',0xa01979ca:'bne a4, a5, 0x64',
 0xa0197a2e:'c.lw a1, 0(s1)',0xa0197a30:'addi a2, s0, -0x24',
 0xa0197a34:'c.mv a0, s2',0xa0197a3a:'c.mv s1, a0',
 0xa0197a3c:'addi a0, s3, 0x28',0xa0197a40:'jal 0x1d83a',
 0xa0197a44:'c.bnez s1, -0x54',0xa0197a46:'lw s3, -0x24(s0)',
 0xa0197a4a:'bnez s3, 0xc',0xa0197a56:'lhu s1, 0xa(s3)',
 0xa0197a5a:'addi a1, s3, 0xc',0xa0197a5e:'c.mv a0, s5',
 0xa0197a60:'c.mv a2, s1',0xa0197a6a:'c.mv a0, s3',
 0xa0197a70:'lh a5, 0x10(s2)',0xa0197a74:'blez a5, -0x84',
 0xa01979f0:'csrw mstatus, s4',0xa0197a00:'c.mv a0, s1',
 0xa0131a02:'c.mv s1, a0',0xa0131a04:'c.mv s4, a2',
 0xa0131a06:'addi s5, a0, 0x18',0xa0131a14:'c.mv a0, s5',
 0xa0131a1a:'c.mv s2, a0',0xa0131a1c:'c.beqz a0, 0x2a',
 0xa0131a1e:'lh a5, 0x22(s1)',0xa0131a22:'addi a4, a5, -1',
 0xa0131a26:'sh a4, 0x22(s1)',0xa0131a32:'c.li a2, 4',
 0xa0131a34:'c.li a1, 4',0xa0131a36:'addi a0, s1, 0x5c',
 0xa0131a3e:'sw s2, 0(s4)',0xa0131a42:'c.li a0, 0',
 0xa0131b68:'lbu a4, 8(a0)',0xa0131b6c:'c.mv a5, a0',
 0xa0131b6e:'c.bnez a4, 0x12',0xa0131b70:'addi a4, gp, 0xb8',
 0xa0131b74:'c.lw a3, 0(a4)',0xa0131b76:'c.sw a4, 4(a5)',
 0xa0131b78:'c.sw a3, 0(a5)',0xa0131b7a:'c.sw a5, 4(a3)',
 0xa0131b7c:'c.sw a5, 0(a4)',0xa0131b7e:'c.jr ra',
 0xa0131b80:'c.li a3, 2',0xa0131b82:'bne a4, a3, 0xa',
 0xa0131b86:'addi a4, gp, 0xc0',0xa0131b8a:'c.j -0x16',
 0xa0131b94:'c.li a5, 1',0xa0131b96:'bne a4, a5, 0x14',
 0xa0131ba8:'c.jr ra',
}.items():inst(pc,text)
pair(0xa005f59e,0xa0197954);pair(0xa0197a62,0xa000589c);pair(0xa0131b9a,0xa002e14e)
for pc,target in [(0xa0197a36,0xa01319e8),(0xa0197a6c,0xa0131b68),(0xa0131a16,0xa010d70e)]:
    inst(pc,'jal '+{0xa0197a36:'-0x6604e',0xa0197a6c:'-0x65f04',0xa0131a16:'-0x24308'}[pc]);jal(pc,target)
for row in [(0xa005f592,3,2,18,12,24),(0xa0197a56,3,5,19,9,10),
            (0xa0131a1e,3,1,9,15,34),(0xa0131a26,0x23,1,9,14,34),
            (0xa0131a3e,0x23,2,20,18,0),(0xa0131b68,3,4,10,14,8)]:mem(*row)
for pc,f,r1,r2,target in [
 (0xa005f51e,1,12,15,0xa005f53c),(0xa01979ca,1,14,15,0xa0197a2e),
 (0xa0197a4a,1,19,0,0xa0197a56),(0xa0197a74,5,0,15,0xa01979f0),
 (0xa0131b82,1,14,13,0xa0131b8c),(0xa0131b96,1,14,15,0xa0131baa)]:
    w=int.from_bytes(raw(pc,4),'little')
    q=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    check('independent branch '+hex(pc),(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,pc+sx(q,13)),
          (0x63,f,r1,r2,target))

w=int.from_bytes(raw(0xa005f56a,4),'little')
check('vendor raw',raw(0xa005f56a,4).hex(),'8b97d420')
check('independent mula fields',(w&127,(w>>12)&7,w>>25,(w>>7)&31,(w>>15)&31,(w>>20)&31),
      (0x0b,1,16,15,9,13))
mp=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
mt=mp.read_text(encoding='utf8');marker=':th.mula rd,rs1,rs2';at=mt.index(marker);end=mt.index('\n}',at)+2;rule=mt[at:end]
check('existing model selectors',all(s in rule for s in ['op0006=0xb','op1214=1','op2531=16']),True)
check('existing local model formula','rd = rd + (rs1 * rs2);' in rule,True)
anchors.append(dict(address='0xa005f56a',raw=raw(0xa005f56a,4).hex(),decode='UNDECODED by Capstone',
 kind='conditional-existing-private-model',rule_path=str(mp),line=mt.count('\n',0,at)+1,rule=rule))

result=dict(status='PASS-independent-limited-review',claim='F11/6',review='F20',baseline='bd457a6',
 checks=checks,anchors=anchors,
 old_caller=dict(path=str(p.relative_to(MAIN)),pointer='/records/195/normalized_result',
 evidence_id=r['evidence_id'],profile=r.get('analysis_profile'),selected_lines=old),
 original=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
 inherited_sha256='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',digest_recomputed=False),
 new_business=0,semantic_corrections=0,
 helper_inheritance='F22 independently conditionally accepted F21; normal H=K+0x18 contract inherited, no helper body reread; F19 pending-F22 text is historical',
 f22_status_source='reverse/reports/ap01/miio-queue-message-source-review-f22-0041-20261024.md',
 limits=['Actual Msg.len is U16(Msg+0xa), not assumed Q.size4 or same runtime send message',
         'K queue and gp pools are distinct; kind1 release interface is not all-message heapfree',
         'No clock units, arbitrary-timeout domain, model execution or independent vendor ISA certification',
         'No allocator/wait/notify/clock/new callee body expansion; no F19/old scripts executed'])
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} independent caller/original-field checks')
