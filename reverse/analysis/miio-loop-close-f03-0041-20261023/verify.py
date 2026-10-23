"""F03 bounded static byte evidence. Never executes target instructions."""
import json
from pathlib import Path
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ROM=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE=0x9ffff000
raw=ROM.read_bytes()
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
def data(pc,n):
 b=raw[pc-BASE:pc-BASE+n]; assert len(b)==n; return b
specs=[
 ('loop_chain_setup',0xa005a7ec,0xa005a822),
 ('initializer_error_chain',0xa005a972,0xa005a97a),
 ('initializer_error_chain_walk',0xa005a9d4,0xa005a9ec),
 ('timer_register',0xa009d106,0xa009d146),
 ('close_entry_type13_selection',0xa009fb96,0xa009fc5a),
 ('close_common_enqueue',0xa009fcde,0xa009fce6),
 ('close_type13_stop',0xa009fd94,0xa009fd9e),
 ('close_return',0xa00a0026,0xa00a003a),
 ('enqueue',0xa009c228,0xa009c26a),
 ('finish_type13_selection',0xa009f524,0xa009f5ce),
 ('finish_common',0xa009f8b6,0xa009f8ea),
 ('remove_registration_node',0xa0098b4a,0xa0098b60),
 ('consumer_head',0xa005c166,0xa005c172),
 ('consumer_next_and_exit',0xa005c802,0xa005c83e),
 ('deinit_and_return',0xa005c9ea,0xa005cad2),
 ('caller_stack_zero',0xa005cc5a,0xa005cc68),
 ('caller_entry_and_post',0xa005cebe,0xa005cf06),
 ('caller_post_flag_branch',0xa005ee9a,0xa005eeba),
 ('caller_return',0xa005ccfc,0xa005cd36),
 ('post_callee',0xa0081554,0xa0081646),
 ('business_request_cleanup',0xa00a0cce,0xa00a0cda),
]
ins={}; windows=[]
for name,a,b in specs:
 p=a; lines=[]
 while p<b:
  n=4 if data(p,1)[0]&3==3 else 2
  assert p+n<=b
  blob=data(p,n); i=next(md.disasm(blob,p),None)
  assert i and i.size==n,(hex(p),blob.hex())
  ins[p]=i; lines.append(dict(pc=hex(p),bytes=blob.hex(),asm=i.mnemonic+' '+i.op_str));p+=n
 windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),instructions=lines))
checks=[]
def expect(pc,m,o):
 i=ins[pc];assert (i.mnemonic,i.op_str)==(m,o),(hex(pc),i.mnemonic,i.op_str)
 checks.append(dict(pc=hex(pc),claim=m+' '+o,method='fresh ROM RV32/RVC decode'))
def sx(v,n):return (v^(1<<(n-1)))-(1<<(n-1))
def call(pc,target):
 w=int.from_bytes(data(pc,4),'little')
 if w&0x7f==0x6f:
  assert w>>7&31==1
  imm=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
  actual=(pc+sx(imm,21))&0xffffffff
 else:
  v=int.from_bytes(data(pc+4,4),'little');assert w&0xfff==0x97 and v&0xfffff==0x80e7
  actual=(pc+sx(w&0xfffff000,32)+sx(v>>20,12))&0xfffffffe
 assert actual==target,(hex(pc),hex(actual),hex(target))
 checks.append(dict(pc=hex(pc),target=hex(target),method='JAL/AUIPC-JALR immediate bitfields'))
for x in [
 (0xa005a7f0,'addi','s2, s1, 8'),(0xa005a802,'sw','s2, 8(s1)'),(0xa005a806,'sw','s2, 0xc(s1)'),
 (0xa005a972,'lw','s4, 8(s1)'),(0xa005a976,'c.li','s6, 0x10'),
 (0xa005a9d4,'lbu','a5, -8(s4)'),(0xa005a9d8,'bne','a5, s6, 0xc'),
 (0xa005a9dc,'addi','a0, s4, -0x10'),(0xa005a9e4,'lw','s4, 0(s4)'),(0xa005a9e8,'bne','s2, s4, -0x14'),
 (0xa009d10e,'sb','a5, 8(a1)'),(0xa009d112,'addi','a4, a0, 8'),
 (0xa009d11c,'c.sw','a4, 0x10(a1)'),(0xa009d11e,'c.lw','a4, 0xc(a0)'),
 (0xa009d120,'addi','a5, a1, 0x10'),(0xa009d124,'c.sw','a4, 0x14(a1)'),
 (0xa009d126,'c.sw','a5, 0(a4)'),(0xa009d128,'c.sw','a5, 0xc(a0)'),
 (0xa009fbc6,'c.sw','a4, 0x2c(a0)'),(0xa009fbc8,'lbu','a4, 8(a0)'),
 (0xa009fbcc,'c.sw','a1, 0xc(a0)'),(0xa009fd9c,'c.j','-0xbe'),
 (0xa009fc4e,'c.li','a5, 0xd'),(0xa009fc50,'beq','a4, a5, 0x144'),
 (0xa009f56c,'c.mv','s1, a0'),(0xa009f588,'addi','a5, a5, 0x75e'),
 (0xa009f58e,'bnez','a5, 0x328'),(0xa009f8c8,'c.bnez','a4, 0xe'),
 (0xa009f8d6,'addi','a0, s1, 0x10'),(0xa009f8de,'c.lw','a5, 0xc(s1)'),
 (0xa009f8e0,'beqz','a5, -0x326'),(0xa009f8e4,'c.mv','a0, s1'),(0xa009f8e6,'c.jalr','a5'),
 (0xa0098b50,'c.lw','a4, 4(a0)'),(0xa0098b52,'c.lw','a5, 0(a0)'),
 (0xa0098b54,'c.sw','a5, 0(a4)'),(0xa0098b58,'c.sw','a4, 4(a5)'),
 (0xa009c256,'c.lw','a5, 4(a0)'),(0xa009c258,'lw','a4, 0xd4(a5)'),
 (0xa009c25c,'c.sw','a4, 0x28(a0)'),(0xa009c25e,'sw','a0, 0xd4(a5)'),
 (0xa005c802,'lw','s5, 0x28(a0)'),(0xa005cad0,'c.jr','ra'),
 (0xa005cec2,'addi','a0, s0, -0x240'),(0xa005cebe,'addi','a1, s0, -0x314'),
 (0xa005ceca,'lw','a0, -0x314(s0)'),(0xa005cedc,'j','0x1fbe'),
 (0xa005cf02,'c.li','a0, 0'),(0xa005cf04,'c.j','-0x208'),
 (0xa005eea6,'j','-0x21aa'),(0xa005eeb6,'j','-0x21ba'),(0xa005cd34,'c.jr','ra'),
 (0xa0081574,'c.mv','s1, a0'),(0xa00815e8,'lw','a5, 0x2b8(s1)'),
 (0xa00815ee,'lw','a1, 0x2b0(s1)'),(0xa00815f2,'c.mv','a0, s1'),(0xa00815f4,'c.jalr','a5'),
 (0xa00a0cce,'c.mv','a0, s4'),(0xa00a0cd4,'sw','zero, 0(s5)')]:expect(*x)
for x in [(0xa005a9e0,0xa009e840),(0xa009fd94,0xa01b2b5c),(0xa009fce0,0xa009c228),
 (0xa009f8da,0xa0098b4a),(0xa005c806,0xa009f524),(0xa005cec6,0xa005a736),
 (0xa005cece,0xa0081554),(0xa00815fa,0xa008ab8a),(0xa0081600,0xa008ab8a),(0xa00a0cd0,0xa002e14e)]:call(*x)
assert (1<<13)&0x275e
checks.append(dict(claim='type13 belongs to common finish mask',mask='0x275e',type=13))
f=json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
for span in f['raw_ranges']:
 a=int(span['start'],16); blob=bytes.fromhex(span.get('hex') or span.get('bytes_hex'));assert data(a,len(blob))==blob
# Save only focused chain-reference metadata, not another copy of the huge container.
refs=[line for line in f['assembly'] if any(t in line+'\n' for t in ['0x8, s1'+'\n','0xc, s1'+'\n'])]
sources=[dict(path='reverse/analysis/factory-test-0041-20261023/retained-initializer.json',evidence_id=f['evidence_id'],profile_digest=f['profile']['digest'],raw_ranges_match=True)]
result=dict(scope='F03 selected loop registration, conditional type13 close, caller post-return frontier',engine='Capstone '+capstone.__version__,windows=windows,checks=checks,sources=sources,container_direct_base_chain_references=refs,limitations=['Static instruction reading only; no firmware execution','No established caller of close(9428, cb)','Post callee indirect callback at a00815f4 remains unresolved','No open-source version identity proven'])
(HERE/'instruction-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} checks, {len(windows)} windows, {sum(int(w["end_exclusive"],16)-int(w["start"],16) for w in windows)} bytes; retained raw ranges match')
