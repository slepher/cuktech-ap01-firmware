"""A28 sparse independent original-byte review. No target execution or new recovery."""
from pathlib import Path
import json,capstone
OUT=Path(__file__).resolve().parent
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
b=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
checks=[];anchors={}
def ck(label,actual,expected):
 assert actual==expected,(label,actual,expected)
 checks.append(dict(claim=label,actual=actual,expected=expected))
def read(a,n):
 o=a-0x9ffff000;assert 0<=o<=len(b)-n
 return b[o:o+n]
def word(a):return int.from_bytes(read(a,4),'little')
def sx(x,n):return x-(1<<n) if x>>(n-1) else x
def inst(a,text):
 n=4 if read(a,1)[0]&3==3 else 2
 i=next(md.disasm(read(a,n),a));ck(hex(a),i.mnemonic+' '+i.op_str,text)
 anchors[hex(a)]=dict(bytes=read(a,n).hex(),instruction=text)
def pair(a,t):
 x,y=word(a),word(a+4)
 ck(hex(a)+' call shape',[x&127,(x>>7)&31,y&127,(y>>7)&31,(y>>15)&31],[23,1,103,1,1])
 ck(hex(a)+' callee',(a+sx(x&0xfffff000,32)+sx(y>>20,12))&0xfffffffe,t)
 anchors[hex(a)]=dict(bytes=read(a,8).hex(),callee=hex(t))
def jal(a,t):
 x=word(a);v=((x>>31)<<20)|(((x>>12)&255)<<12)|(((x>>20)&1)<<11)|(((x>>21)&1023)<<1)
 ck(hex(a)+' direct call',[x&127,(x>>7)&31,(a+sx(v,21))&0xffffffff],[111,1,t])
 anchors[hex(a)]=dict(bytes=read(a,4).hex(),callee=hex(t))
# Normal entry and re-read: cache=s2, entry=s1; decrement is a word store.
for a,t in [(0xa019da4c,'c.mv s2, a0'),(0xa019da4e,'c.mv a0, a1'),(0xa019da50,'c.mv s1, a1'),(0xa019da5a,'c.lw a5, 4(s1)'),(0xa019da5c,'c.bnez a0, 0x62'),(0xa019dabe,'c.addi a5, -1'),(0xa019dac0,'c.sw a5, 4(s1)'),(0xa019dac2,'bgez a5, -0x3e'),(0xa008b604,'c.bnez a0, 0x4c'),(0xa008b650,'c.lw a0, 4(a0)'),(0xa019da84,'c.mv a0, s1'),(0xa019da8e,'c.bnez a0, 0x24'),(0xa019da90,'lbu a5, 0xc(s1)'),(0xa019da94,'c.beqz a5, 0x1e'),(0xa019da96,'c.mv a0, s1'),(0xa019daa0,'lw a5, 0x18(s2)'),(0xa019daa4,'c.li a1, 0'),(0xa019daa6,'c.jalr a5'),(0xa019daa8,'c.mv a0, s1')]:inst(a,t)
for a,t in [(0xa019da52,0xa008b604),(0xa019da86,0xa008b604),(0xa019da98,0xa008b654),(0xa019daaa,0xa008b6a6)]:pair(a,t)
# Only inherited payload adapter / destructor's allocation-base tail are rechecked.
for a,t in [(0xa008b6a0,'c.lw a5, 8(a0)'),(0xa008b6a2,'c.sub a0, a5'),(0xa008b6b0,'c.bnez a0, 0x42')]:inst(a,t)
for a,t in [(0xa008b6f2,0xa008b654),(0xa008b6f6,0xa008ab8a)]:jal(a,t)
# Cache callback and backend identity, without re-exporting installation or PNG cleanup.
for a,t in [(0xa01985ce,'sw s2, 0(a0)'),(0xa01985d6,'c.li a2, 0xc'),(0xa01985d8,'c.mv a1, s3'),(0xa01985da,'c.addi a0, 0x10')]:inst(a,t)
pair(0xa01985dc,0xa000589c)
for off,t in [(0x10,0xa00ebb90),(0x14,0xa00ebe98),(0x20,0xa00ec1e6),(0x24,0xa00ea78c)]:ck('backend slot '+hex(off),word(0xa0263afc+off),t)
# Marking branch and zero-reference immediate cleanup; no upper invalidation business claim.
for a,t in [(0xa019d02a,'c.bnez a0, 0x34'),(0xa019d030,'c.mv a1, s2'),(0xa019d032,'c.lw a5, 0x14(a5)'),(0xa019d034,'c.mv a0, s1'),(0xa019d036,'c.jalr a5'),(0xa019d038,'c.mv a0, s2'),(0xa019d042,'c.lw a5, 0x18(s1)'),(0xa019d044,'c.li a1, 0'),(0xa019d046,'c.jalr a5'),(0xa019d048,'c.mv a0, s2'),(0xa019d05e,'c.li a5, 1'),(0xa019d060,'sb a5, 0xc(s2)'),(0xa019d068,'c.mv a1, s2'),(0xa019d06a,'c.lw a5, 0x14(a5)'),(0xa019d06c,'c.mv a0, s1'),(0xa019d06e,'c.jalr a5')]:inst(a,t)
for a,t in [(0xa019d022,0xa008b604),(0xa019d03a,0xa008b654),(0xa019d04a,0xa008b6a6)]:pair(a,t)
# Capacity reconnect and victim cleanup order.
for a,t in [(0xa019d98e,'c.li s3, 2'),(0xa019d9cc,'c.beqz a0, -0x5a'),(0xa019d9d0,'c.li a3, 0'),(0xa019d9d2,'c.li a2, 0'),(0xa019d9d4,'c.lw a5, 0x24(a5)'),(0xa019d9d6,'c.mv a1, s2'),(0xa019d9d8,'c.mv a0, s1'),(0xa019d9da,'c.jalr a5'),(0xa019d9dc,'beq a0, s3, -0x16'),(0xa019d8a6,'c.li a1, 0'),(0xa019d8a8,'c.mv s2, a0'),(0xa019d8aa,'c.lw a5, 0x20(a5)'),(0xa019d8ac,'c.jalr a5'),(0xa019d8ae,'c.bnez a0, 0x36'),(0xa019d8d6,'c.li a0, 0'),(0xa019d8ea,'c.mv a1, a0'),(0xa019d8ec,'c.lw a5, 0x14(a5)'),(0xa019d8ee,'c.mv s1, a0'),(0xa019d8f0,'c.mv a0, s2'),(0xa019d8f2,'c.jalr a5'),(0xa019d8f4,'c.mv a0, s1'),(0xa019d8fe,'lw a5, 0x18(s2)'),(0xa019d902,'c.li a1, 0'),(0xa019d904,'c.jalr a5'),(0xa019d906,'c.mv a0, s1'),(0xa019d910,'c.li a0, 1')]:inst(a,t)
jal(0xa019d9c8,0xa019d898)
for a,t in [(0xa019d8f6,0xa008b654),(0xa019d908,0xa008b6a6)]:pair(a,t)
# Victim normal reference gate and load-index instruction, independently decoded bit fields.
for a,t in [(0xa00ec236,'lw s2, 0x38(a0)'),(0xa00ec256,'c.lw s1, 0x10(a5)'),(0xa00ec258,'lw a5, 4(s3)'),(0xa00ec262,'c.add s1, a5'),(0xa00ec264,'c.mv a0, s1'),(0xa00ec26a,'c.beqz a0, -0x28'),(0xa00ec26c,'lw a5, 0x30(s3)'),(0xa00ec274,'c.j -0x38'),(0xa00ec24a,'c.mv a0, s1')]:inst(a,t)
jal(0xa00ec266,0xa008b604)
x=word(0xa00ec270)
ck('th.lrw opcode/f3/top5/rd/base/index/shift',[x&127,(x>>12)&7,x>>27,(x>>7)&31,(x>>15)&31,(x>>20)&31,(x>>25)&3],[11,4,8,18,18,15,0])
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
s=model.read_text();rule=s[s.index(':th.lrw '):];rule=rule[:rule.index('\n}')+2]
ck('read-only existing lrw semantics writes rd only',[line.strip() for line in rule.splitlines() if line.strip().startswith(('rd =','rs1 =','rs2 ='))],['rd = value;'])
anchors['0xa00ec270']=dict(bytes=read(0xa00ec270,4).hex(),instruction='th.lrw s2,s2,a5,0',note='rd aliases base: replaces s2 with loaded word, no separate base update')
# The backend normal tail updates usage before caller invokes cleanup.
for a,t in [(0xa00ebf60,'c.lw a5, 0x3c(s1)'),(0xa00ebf62,'c.mv a0, s2'),(0xa00ebf64,'c.jalr a5'),(0xa00ebf66,'c.lw a5, 0xc(s1)'),(0xa00ebf68,'c.sub a5, a0'),(0xa00ebf6a,'c.sw a5, 0xc(s1)')]:inst(a,t)
summary=dict(result='passed',kind='old conclusion independent review',new_functional_recovery=0,checks=len(checks),sparse_anchors=len(anchors),shared_REA_target_opened=False)
(OUT/'review-evidence.json').write_text(json.dumps(dict(summary=summary,rom=str(ROOT/'roms/0041/ap01-1.0.2_0041.bin'),mapping='offset=VA-0x9ffff000',checks=checks,sparse_original_byte_anchors=anchors,lrw_existing_rule=str(model),limits=['No fresh whole-function export; A27 evidence and A23-A26 inherited.', 'No source version certification, sorting, upper invalidation trigger, accounting unit or heap recovery.', 'No SIM, build, replay, target/device/network execution.']),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary))
