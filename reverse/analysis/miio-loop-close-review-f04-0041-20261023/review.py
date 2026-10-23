"""F04 independent static review; only read ROM bytes, never execute them."""
import json,re
from pathlib import Path
import capstone
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
ROM=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
r=ROM.read_bytes(); base=0x9ffff000
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
# New review windows include full caller prefix and return, not F03 producer output.
spans=[('register',0xa009d106,0xa009d146),('close_dispatch',0xa009fb96,0xa009fc5a),('stop_pair',0xa009fd94,0xa009fd9e),('close_enqueue',0xa009fcde,0xa009fce6),('close_return',0xa00a0026,0xa00a003a),('pending',0xa009c228,0xa009c26a),('finish_dispatch',0xa009f524,0xa009f59a),('finish_tail',0xa009f8b6,0xa009f8ea),('finish_return',0xa009f5ba,0xa009f5ce),('unlink',0xa0098b4a,0xa0098b60),('caller',0xa005cc1e,0xa005cf06),('caller_flag',0xa005ee9a,0xa005eeba),('post_object',0xa0081554,0xa0081646),('chain_setup',0xa005a7ec,0xa005a822),('walker_head',0xa005a972,0xa005a97a),('walker',0xa005a9d4,0xa005a9ec),('pending_take',0xa005c166,0xa005c172),('pending_consume',0xa005c802,0xa005c83e),('exit',0xa005c9ea,0xa005cad2),('expiry_callback_read',0xa009d36a,0xa009d382),('request_release',0xa00a0cce,0xa00a0cda)]
D={}; windows=[]
for name,a,b in spans:
 p=a; lines=[]
 while p<b:
  blob=r[p-base:p-base+4]; n=4 if blob[0]&3==3 else 2
  i=next(md.disasm(blob[:n],p),None)
  assert i and i.size==n and p+n<=b,(hex(p),blob.hex())
  D[p]=i;lines.append({'pc':hex(p),'raw':blob[:n].hex(),'text':i.mnemonic+' '+i.op_str});p+=n
 windows.append({'name':name,'start':hex(a),'end':hex(b),'instructions':lines})
checks=[]
def q(p,text):
 i=D[p];assert i.mnemonic+' '+i.op_str==text,(hex(p),i.mnemonic,i.op_str,text)
 checks.append({'pc':hex(p),'expected':text})
def sx(x,n):return x-(1<<n) if x>>(n-1) else x
def edge(p,target):
 w=int.from_bytes(r[p-base:p-base+4],'little'); op=w&127
 if op==0x6f: off=sx(((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1),21)
 elif op==0x63: off=sx(((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1),13)
 elif op==0x17:
  v=int.from_bytes(r[p-base+4:p-base+8],'little');assert v&127==0x67
  off=sx(w&0xfffff000,32)+sx(v>>20,12)
 else: raise AssertionError(hex(p))
 assert (p+off)&0xffffffff==target,(hex(p),hex((p+off)&0xffffffff))
 checks.append({'pc':hex(p),'target':hex(target),'method':'independent immediate-bitfields'})
# Full initializer write set guards field identity and widths.
writes=[(i.address,i.mnemonic,i.op_str) for p,i in D.items() if 0xa009d106<=p<0xa009d146 and i.mnemonic in ('sb','sw','c.sw') and '(a1)' in i.op_str]
assert len(writes)==11
assert all(not re.search(r', (?:0|0xc)\(a1\)$',t) for _,_,t in writes)
checks.append({'claim':'all 11 initializer timer writes exclude data+0 and close_cb+c','writes':[(hex(a),m,t) for a,m,t in writes]})
for p,t in {
0xa009d10e:'sb a5, 8(a1)',0xa009d118:'c.sw a0, 4(a1)',0xa009d11a:'c.sw a5, 0x2c(a1)',0xa009d11c:'c.sw a4, 0x10(a1)',0xa009d11e:'c.lw a4, 0xc(a0)',0xa009d124:'c.sw a4, 0x14(a1)',0xa009d126:'c.sw a5, 0(a4)',0xa009d128:'c.sw a5, 0xc(a0)',0xa009d134:'sw zero, 0x30(a1)',
0xa009fbac:'andi a4, a5, 3',0xa009fbc2:'ori a4, a5, 1',0xa009fbc6:'c.sw a4, 0x2c(a0)',0xa009fbc8:'lbu a4, 8(a0)',0xa009fbcc:'c.sw a1, 0xc(a0)',0xa009fbd0:'c.mv s2, a0',0xa009fc4e:'c.li a5, 0xd',0xa009fd9c:'c.j -0xbe',0xa009fcde:'c.mv a0, s2',
0xa009c232:'andi a4, a5, 1',0xa009c24a:'c.andi a5, 2',0xa009c256:'c.lw a5, 4(a0)',0xa009c258:'lw a4, 0xd4(a5)',0xa009c25c:'c.sw a4, 0x28(a0)',0xa009c25e:'sw a0, 0xd4(a5)',
0xa009f560:'ori a4, a5, 2',0xa009f564:'c.sw a4, 0x2c(a0)',0xa009f566:'lbu a4, 8(a0)',0xa009f582:'sll a4, a5, a4',0xa009f586:'c.lui a5, 2',0xa009f588:'addi a5, a5, 0x75e',0xa009f58c:'c.and a5, a4',0xa009f8be:'andi a4, a5, -9',0xa009f8c2:'c.sw a4, 0x2c(s1)',0xa009f8c4:'andi a4, a5, 1',0xa009f8c8:'c.bnez a4, 0xe',0xa009f8d6:'addi a0, s1, 0x10',0xa009f8de:'c.lw a5, 0xc(s1)',0xa009f8e4:'c.mv a0, s1',0xa009f8e6:'c.jalr a5',
0xa0098b50:'c.lw a4, 4(a0)',0xa0098b52:'c.lw a5, 0(a0)',0xa0098b54:'c.sw a5, 0(a4)',0xa0098b56:'c.lw a4, 4(a0)',0xa0098b58:'c.sw a4, 4(a5)',
0xa005cc1e:'addi sp, sp, -0x400',0xa005cc2a:'addi s0, sp, 0x400',0xa005cc5a:'addi a2, zero, 0x200',0xa005cc60:'addi a0, s0, -0x240',0xa005cebe:'addi a1, s0, -0x314',0xa005cec2:'addi a0, s0, -0x240',0xa005ceca:'lw a0, -0x314(s0)',0xa005cf04:'c.j -0x208',0xa005cd34:'c.jr ra',
0xa0081574:'c.mv s1, a0',0xa00815e8:'lw a5, 0x2b8(s1)',0xa00815ee:'lw a1, 0x2b0(s1)',0xa00815f2:'c.mv a0, s1',0xa00815f4:'c.jalr a5',0xa00815f6:'lw a0, 0x2b0(s1)',0xa00815fe:'c.mv a0, s1',
0xa005a9d4:'lbu a5, -8(s4)',0xa005a9dc:'addi a0, s4, -0x10',0xa005a9e4:'lw s4, 0(s4)',0xa005c802:'lw s5, 0x28(a0)',0xa009d36a:'lw a5, -4(s1)',0xa009d36e:'c.mv a0, s2',0xa009d370:'c.jalr a5',0xa00a0cce:'c.mv a0, s4',0xa00a0cd4:'sw zero, 0(s5)'
}.items():q(p,t)
for p,target in [(0xa009fc50,0xa009fd94),(0xa009fd94,0xa01b2b5c),(0xa009fce0,0xa009c228),(0xa009f58e,0xa009f8b6),(0xa009f8da,0xa0098b4a),(0xa009f8e0,0xa009f5ba),(0xa005cec6,0xa005a736),(0xa005cece,0xa0081554),(0xa00815fa,0xa008ab8a),(0xa0081600,0xa008ab8a),(0xa005c806,0xa009f524),(0xa005a9e0,0xa009e840),(0xa00a0cd0,0xa002e14e)]:edge(p,target)
assert (1<<13)&(0x2000+0x75e)==0x2000
# Rebind retained container source and reproduce only bounded direct-base search.
f=json.loads((TREE/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
for z in f['raw_ranges']:
 b=bytes.fromhex(z.get('hex') or z.get('bytes_hex'));a=int(z['start'],16);assert r[a-base:a-base+len(b)]==b
refs=[s for s in f['assembly'] if re.search(r', 0x(?:8|c), s1$',s)]
result={'scope':'F04 conditional close review; not full loop or obj callback recovery','engine':capstone.__version__,'windows':windows,'checks':checks,'initializer_write_set':[(hex(a),m,t) for a,m,t in writes],'bounded_container_direct_s1_chain_refs':refs,'source':{'path':'reverse/analysis/factory-test-0041-20261023/retained-initializer.json','evidence_id':f['evidence_id'],'profile':f['profile']['digest'],'raw_ranges_match':True},'limitations':['No target execution','No actual close(9428,cb) established','No post-exit consumer opportunity established','obj+2b8 callback installation/identity unresolved','No verified upstream library version']}
(OUT/'independent-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS',len(checks),'checks;',len(windows),'windows;',sum(b-a for _,a,b in spans),'bytes; retained container bound; type13 mask = 0x2000')
