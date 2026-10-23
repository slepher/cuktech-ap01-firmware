"""D03 static bytes/ABI evidence only; never executes firmware."""
import json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware');BASE=0x9ffff000
raw=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
regions=[('dispatch',0xa0025874,0xa00258a0),('page_ref',0xa00258a0,0xa00258e4),('fd_divide',0xa00258e4,0xa0025904),('acquire',0xa0025904,0xa002595c),('release',0xa0027e54,0xa0027e94),('wrapper',0xa0027e94,0xa0027eee),('release_zero_contract',0xa0027d9a,0xa0027dc0),('tty_registration',0xa0029690,0xa00296e0),('uart_register',0xa01b5a7e,0xa01b5b0e),('inode_install',0xa01b5a12,0xa01b5a7e),('file_install_slice',0xa01b5bec,0xa01b5c3a),('open_wrapper',0xa003f4f6,0xa003f546),('open_slice',0xa003eb4e,0xa003eb7c),('application_open',0xa005ab10,0xa005ab32),('application_config',0xa005b214,0xa005b2e6),('uart_write',0xa002c206,0xa002c3a6),('enqueue_byte',0xa002c140,0xa002c206),('direct_write',0xa002ad82,0xa002adde),('always_ready',0xa001972c,0xa001973a),('lower_send',0xa0019876,0xa00198bc),('txint_contract',0xa0019810,0xa0019876),('context_predicate',0xa0027830,0xa002786c)]
regs=['zero','ra','sp','gp','tp','t0','t1','t2','s0','s1','a0','a1','a2','a3','a4','a5','a6','a7','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','t3','t4','t5','t6']
modelpath=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc';model=modelpath.read_text().splitlines();modelused={}
def vendor(w):
 rd,rs1,rs2,shift=(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3
 f,hi=(w>>12)&7,w>>27
 if f==1 and w>>25==16: key=':th.mula ';text=f'th.mula {regs[rd]}, {regs[rs1]}, {regs[rs2]}'
 elif f==4 and hi in (8,16):
  name='lrw' if hi==8 else 'lrbu';key=f':th.{name} ';text=f'th.{name} {regs[rd]}, {regs[rs1]}, {regs[rs2]}, {shift}'
 elif f==5 and hi==0:key=':th.srb ';text=f'th.srb {regs[rd]}, {regs[rs1]}, {regs[rs2]}, {shift}'
 elif f in (2,3):
  name='ext' if f==2 else 'extu';msb=(w>>26)&31;lsb=(w>>20)&31;key=f':th.{name} rd,rs1,{msb},{lsb} ';text=f'th.{name} {regs[rd]}, {regs[rs1]}, {msb}, {lsb}'
 elif f==4 and hi==19:key=':th.lbuia ';text=f'th.lbuia {regs[rd]}, {regs[rs1]}, {rs2 if rs2<16 else rs2-32}, {shift}'
 else:raise AssertionError(hex(w))
 start=next(i for i,l in enumerate(model) if l.startswith(key));end=next(i for i in range(start+1,len(model)) if model[i]=='}')
 modelused[key]={'line':start+1,'text':'\n'.join(model[start:end+1])}
 return text,dict(rd=rd,rs1=rs1,rs2=rs2,shift=shift,funct3=f,high5=hi)
windows=[];rows={};vendors=[]
for name,a,b in regions:
 pc=a;items=[]
 while pc<b:
  off=pc-BASE;w=int.from_bytes(raw[off:off+4],'little');sz=4 if w&3==3 else 2;assert pc+sz<=b
  v=raw[off:off+sz]
  if sz==4 and w&127==11:
   text,fields=vendor(w);vendors.append(dict(address=hex(pc),bytes=v.hex(),decode=text,fields=fields))
  else:
   d=list(cs.disasm(v,pc));assert len(d)==1 and d[0].size==sz,(hex(pc),v.hex());text=d[0].mnemonic+' '+d[0].op_str
  row=dict(address=hex(pc),file_offset=off,bytes=v.hex(),decode=text);rows[pc]=row;items.append(row);pc+=sz
 windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),instructions=items))
checks=[]
for pc,text in {
0xa0025904:'sw zero, 0(a1)',0xa0025910:'c.lw a5, 8(a5)',0xa002591c:'lbu a5, 0x5c(a5)',0xa00258e6:'rem a2, a1, a5',0xa00258f4:'div a1, a1, a5',0xa00258ae:'th.lrw a0, a5, a1, 2',0xa00258b4:'th.mula a0, a2, a5',0xa00258c2:'c.sw a5, 4(a0)',0xa0027e78:'c.addi a5, -1',0xa0027e7a:'c.sw a5, 4(a0)',0xa0027e7c:'csrw mstatus, a4',0xa0025884:'c.lw a4, 0xc(a4)',0xa0025890:'c.jalr a4',0xa01b5a4a:'c.sw s1, 0x10(a4)',0xa01b5a4c:'c.sw a2, 0x18(a4)',0xa01b5c04:'sw s4, 0xc(a1)',0xa01b5c08:'c.sw a4, 4(a1)',0xa005b232:'sw s5, 0(s6)',0xa002c228:'c.lw s1, 0x18(a5)',0xa002c2fc:'lw s5, 0(s4)',0xa002c30a:'th.extu s5, s5, 6, 6',0xa002c324:'th.lrbu a1, s6, a5, 0',0xa002c192:'th.srb s3, a4, a5, 0',0xa002c196:'sh s2, 0x50(s1)',0xa002c15c:'lh a5, 0x54(a0)',0xa002c162:'th.ext s2, s2, 15, 0',0xa002add2:'th.lbuia a1, s1, 1, 0',0xa0019734:'c.li a0, 1',0xa0019882:'sw a1, -0x14(s0)',0xa00198b4:'addi a1, s0, -0x14',0xa00198b0:'c.li a2, 1',
}.items():
 assert rows[pc]['decode']==text,(hex(pc),rows[pc],text);checks.append(dict(address=hex(pc),expected=text))
sx=lambda v,n:v-(1<<n) if v&(1<<(n-1)) else v
edges=[]
for pc,target in {0xa002593a:0xa00258e4,0xa00258f8:0xa00258a0,0xa0027e84:0xa0027d9a,0xa0027eae:0xa0025904,0xa0027ec2:0xa0025874,0xa0027ecc:0xa0027e54,0xa01b5afe:0xa01b5a12,0xa005ab1c:0xa003f4f6,0xa002c33e:0xa002c140,0xa002c360:0xa002c140,0xa002c252:0xa002ad82,0xa002c2ee:0xa0027968}.items():
 w=int.from_bytes(bytes.fromhex(rows[pc]['bytes']),'little');assert w&127==0x6f
 im=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 assert (pc+sx(im,21))&0xffffffff==target;edges.append(dict(address=hex(pc),target=hex(target)))
for pc,target in {0xa00296c4:0xa01b5a7e,0xa003eb66:0xa01b5b74,0xa0019894:0x62fc22ae}.items():
 w=int.from_bytes(bytes.fromhex(rows[pc]['bytes']),'little');z=int.from_bytes(bytes.fromhex(rows[pc+4]['bytes']),'little')
 actual=(pc+sx(w&0xfffff000,32)+sx(z>>20,12))&0xffffffff
 assert actual==target,(hex(pc),hex(actual),hex(target));edges.append(dict(address=hex(pc),target=hex(target),kind='AUIPC/JALR'))
def u32(a):return struct.unpack_from('<I',raw,a-BASE)[0]
assert u32(0xa066d7c8+12)==0xa002c206
assert u32(0xa01bcb18+0x48)==0
assert u32(0xa01bcb18+0x30)==0xa0019876
assert u32(0xa01bcb18+0x38)==0xa001972c
ram=0x62fc36d0;rom=0xa00027d4+ram-0x62fc2cc0
assert rom==0xa00031e4 and u32(rom+0xa0)==0xa01bcb18 and u32(rom+0xa4)==0x62fc36b4
assert raw[0xa0566d7c-BASE]==13 and raw[0xa062cda0-BASE]==10
assert raw[0xa01bc32c-BASE:0xa01bc32c-BASE+11]==b'/dev/ttyS1\0'
initializers=[dict(name='ttyS1_device',ram=hex(ram),rom=hex(rom),bytes=raw[rom-BASE:rom-BASE+0xb0].hex()),dict(name='uart_operations',rom=hex(0xa066d7c8),words=[hex(u32(0xa066d7c8+i)) for i in range(0,40,4)]),dict(name='lower_operations',rom=hex(0xa01bcb18),words=[hex(u32(0xa01bcb18+i)) for i in range(0,76,4)])]
source=json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text(encoding='utf-8'))
# Keep provenance only, no redundant full initializer copy.
f=source['function']
provenance=dict(path='reverse/analysis/factory-test-0041-20261023/retained-initializer.json',evidence_id=f['evidence_id'],profile_digest=f['profile']['digest'],address=f['address'])
out=dict(task='D03',rom_path=str(ROOT/'roms/0041/ap01-1.0.2_0041.bin'),mapping='file offset=VA-0x9ffff000',windows=windows,exact_checks=checks,edges=edges,vendor_words=vendors,vendor_model=dict(path=str(modelpath),excerpts=list(modelused.values())),initializers=initializers,prior_initializer=provenance,limitations=['Static byte decoding only; no firmware execution, replay, external source lookup or model modification.','RAM initializers use prior reviewed startup copy contract ROMa00027d4 -> RAM62fc2cc0; runtime replacement is not excluded.','No original-source/version certification; lower callbacks and RTOS routines retain explicit boundaries.'])
(HERE/'instruction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(static_checks_passed=True,windows=len(windows),instructions=len(rows),exact_checks=len(checks),edges=len(edges),vendor_words=len(vendors),initializer_regions=len(initializers))))
