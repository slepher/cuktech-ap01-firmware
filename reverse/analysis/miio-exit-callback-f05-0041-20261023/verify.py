"""F05: offline ROM reading/disassembly only. Does not execute target code."""
import json, re
from pathlib import Path
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

OUT = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
r = ROM.read_bytes()
BASE = 0x9ffff000
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
spans = [
 ('caller_create',0xa005cc9c,0xa005ccd8),
 ('caller_return',0xa005cebe,0xa005ced2),
 ('creator_entry',0xa0084b96,0xa0084bd2),
 ('backend_alloc',0xa0084d50,0xa0084d5c),
 ('display_alloc',0xa0084d9a,0xa0084daa),
 ('display_initialize',0xa0084de8,0xa0084e32),
 ('payload_initialize',0xa0084e6e,0xa0084eea),
 ('backend_register',0xa0086ca8,0xa0086ce2),
 ('backend_open',0xa0086d26,0xa0086d44),
 ('output_publish',0xa00873b6,0xa0087412),
 ('creator_return',0xa0087482,0xa00874b0),
 ('display_delete',0xa0081554,0xa0081646),
 ('delete_event',0xa00800b4,0xa0080134),
 ('backend_get',0xa007fe32,0xa007fe4e),
 ('zero',0xa0080d8e,0xa0080da6),
 ('payload_zero',0xa00819d0,0xa0081a36),
 ('payload_default',0xa0081978,0xa00819d0),
 ('event_registration',0xa007ffa0,0xa0080002),
 ('event_send',0xa00814f4,0xa0081554),
 ('event_add',0xa01b93b4,0xa01b951c),
 ('event_dispatch',0xa008acfa,0xa008adf4),
 ('list_allocate',0xa008aec0,0xa008af14),
 ('release',0xa008ab8a,0xa008abb0),
]
D = {}; windows = []
for name,a,z in spans:
 p=a; rows=[]
 while p<z:
  raw=r[p-BASE:p-BASE+4]; n=4 if raw[0]&3==3 else 2
  i=next(md.disasm(raw[:n],p),None)
  vendor={0xa008ad78:('8bb6f73c','th.extu a3, a5, 15, 15 [existing local model]'),
          0xa01b94f2:('0b15f620','th.mula a0, a2, a5 [existing local model]')}
  if p in vendor:
   assert raw.hex()==vendor[p][0]; t=vendor[p][1]
  else:
   assert i and i.size==n and p+n<=z,(hex(p),raw.hex())
   t=i.mnemonic+' '+i.op_str
  D[p]=t; rows.append(dict(pc=hex(p),raw=raw[:n].hex(),asm=t)); p+=n
 windows.append(dict(name=name,start=hex(a),end=hex(z),instructions=rows))
checks=[]
def q(pc,t):
 assert D[pc]==t,(hex(pc),D[pc],t)
 checks.append(dict(pc=hex(pc),expected=t))
def sx(v,n): return v-(1<<n) if v>>(n-1) else v
def edge(pc,target):
 w=int.from_bytes(r[pc-BASE:pc-BASE+4],'little'); op=w&127
 if op==0x6f: off=sx((w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1,21)
 elif op==0x17:
  v=int.from_bytes(r[pc-BASE+4:pc-BASE+8],'little'); assert v&127==0x67
  off=sx(w&0xfffff000,32)+sx(v>>20,12)
 else: raise AssertionError(hex(pc))
 assert (pc+off)&0xffffffff==target,(hex(pc),hex((pc+off)&0xffffffff),hex(target))
 checks.append(dict(pc=hex(pc),target=hex(target),method='independent immediate bitfields'))
for pc,t in {
 0xa005ccba:'addi a1, s0, -0x314',0xa005ccbe:'addi a0, s0, -0x308',
 0xa005ccae:'sw a5, -0x308(s0)',0xa005ccc2:'sw a5, -0x304(s0)',
 0xa005cebe:'addi a1, s0, -0x314',0xa005cec2:'addi a0, s0, -0x240',0xa005ceca:'lw a0, -0x314(s0)',
 0xa0084bba:'c.mv s7, a1',0xa0084bb4:'sw a0, -0xa4(s0)',
 0xa0084d50:'addi a0, zero, 0x94',0xa0084d58:'c.mv s5, a0',
 0xa0084da6:'c.mv s1, a0',0xa0084de8:'addi a1, zero, 0x324',
 0xa0084e26:'addi a0, zero, 0x58',0xa0084e2e:'sw a0, 0x2b0(s1)',
 0xa0084e72:'lw a5, 0x2b4(s1)',0xa0084e78:'lw a1, 0x2b0(s1)',0xa0084e7c:'c.mv a0, s1',0xa0084e7e:'c.jalr a5',
 0xa0086cb0:'lui a1, 0xa0080',0xa0086cb4:'c.mv a3, s1',
 0xa0086cc2:'sw a5, 0(s5)',0xa0086cc6:'sw s5, 0x2e0(s1)',
 0xa0086cca:'addi a2, zero, 0x29',0xa0086cce:'addi a1, a1, 0xb4',0xa0086cd2:'c.mv a0, s1',
 0xa0086d26:'c.mv a0, s1',0xa0086d2c:'c.mv s2, a0',0xa0086d2e:'c.lw a0, 0(a0)',
 0xa00873ea:'sw s1, 0(s7)',
 0xa0081574:'c.mv s1, a0',0xa0081570:'addi a1, zero, 0x29',
 0xa00815e8:'lw a5, 0x2b8(s1)',0xa00815ee:'lw a1, 0x2b0(s1)',0xa00815f2:'c.mv a0, s1',0xa00815f4:'c.jalr a5',
 0xa00815f6:'lw a0, 0x2b0(s1)',0xa00815fe:'c.mv a0, s1',
 0xa00800c0:'lw s2, 0xc(a0)',0xa00800c4:'c.mv a0, s2',0xa00800cc:'c.mv s1, a0',
 0xa00800de:'sw zero, 0x2e0(s2)',0xa00800e2:'sw zero, 0x2c(s2)',
 0xa00800e6:'c.lw a0, 0(s1)',0xa00800f2:'c.sw a5, 0(s1)',
 0xa00800f4:'c.lw a0, 0x34(s1)',0xa00800fc:'sw zero, 0x34(s1)',0xa0080100:'c.mv a0, s1',
 0xa007fe44:'lw a0, 0x2e0(a0)',0xa0080d96:'c.mv a2, a1',0xa0080d98:'c.li a1, 0',
 0xa0081a1c:'addi a1, zero, 0x58',0xa00819c8:'c.sw a5, 0x38(a0)',
 0xa007ffec:'addi a0, a0, 0x2e8',0xa008151e:'addi s1, s1, 0x2e8',
 0xa0081516:'sw s1, -0x2c(s0)',0xa008151a:'sw s1, -0x28(s0)',0xa0081522:'sw a2, -0x1c(s0)',0xa008152e:'sw s2, -0x24(s0)',
 0xa0086d40:'sw a0, 0(s2)',
 0xa01b9432:'c.sw a1, 0(a0)',0xa01b9438:'c.sw a2, 8(a5)',0xa01b943a:'c.sw a3, 4(a5)',
 0xa008ad70:'c.lw a5, 8(a4)',0xa008ad78:'th.extu a3, a5, 15, 15 [existing local model]',
 0xa008ad86:'lw a3, 8(s3)',0xa008ad8a:'bne a5, a3, -0x1e',
 0xa008ad8e:'c.lw a5, 4(a4)',0xa008ad90:'c.mv a0, s3',0xa008ad92:'sw a5, 0xc(s3)',0xa008ad96:'c.lw a5, 0(a4)',0xa008ad98:'c.jalr a5',
}.items(): q(pc,t)
for pc,target in [
 (0xa005ccc6,0xa0084b96),(0xa005cec6,0xa005a736),(0xa005cece,0xa0081554),
 (0xa0084d54,0xa008e362),(0xa0084da2,0xa008aec0),(0xa0084dec,0xa0080d8e),
 (0xa0084e2a,0xa008ae8c),(0xa0084e6e,0xa00819d0),(0xa0086cd4,0xa007ffa0),
 (0xa0086d28,0xa007fe32),(0xa0086d34,0xa0026888),
 (0xa008157e,0xa00814f4),(0xa0081586,0xa008b7f0),(0xa00815cc,0xa008ae42),
 (0xa00815da,0xa0089d02),(0xa00815e4,0xa008ae58),
 (0xa00815fa,0xa008ab8a),(0xa0081600,0xa008ab8a),
 (0xa00800c6,0xa007fe32),(0xa00800ec,0xa0026888),(0xa00800f8,0xa002e14e),(0xa0080102,0xa008ab8a),
 (0xa0080d9a,0xa0024906),(0xa0081a22,0xa0080d8e),(0xa0081a28,0xa0081978),
 (0xa007fff0,0xa01b93b4),
 (0xa0081532,0xa008acfa),(0xa0081544,0xa008acfa),(0xa0086d3c,0xa003f4f6),
]: edge(pc,target)
strings=[]
for a,expected in [(0xa01c3af4,b'/dev/fb0'),(0xa01c3b00,b'/dev/input0'),
 (0xa025f00c,b'/home/jiangmingmin/ap01/AP01_BL618/apps/graphics/lvgl/lvgl/src/drivers/nuttx/lv_nuttx_entry.c'),
 (0xa025e3d8,b'/home/jiangmingmin/ap01/AP01_BL618/apps/graphics/lvgl/lvgl/src/display/lv_display.c')]:
 actual=r[a-BASE:].split(b'\0',1)[0];assert actual==expected
 strings.append(dict(address=hex(a),text=actual.decode()))
# Raw encoding search is explicitly not complete alias analysis or a code/data classifier.
matches=[]
for o in range(0,len(r)-4,2):
 w=int.from_bytes(r[o:o+4],'little')
 if w&0x707f==0x2023 and ((w>>25)<<5|(w>>7&31))==0x2b8:
  i=next(md.disasm(r[o:o+4],BASE+o),None)
  matches.append(dict(pc=hex(BASE+o),raw=r[o:o+4].hex(),asm=i.mnemonic+' '+i.op_str if i else None))
assert [int(x['pc'],16) for x in matches]==[0xa00efd3e,0xa00eff32,0xa014e264]
# Constructor bounded register-definition inventory, including unknown custom words.
# This records why a proof that callbacks stay NULL is not claimed.
constructor_custom=[];p=0xa0084b96
while p<0xa00874b0:
 raw=r[p-BASE:p-BASE+4];n=4 if raw[0]&3==3 else 2;i=next(md.disasm(raw[:n],p),None)
 if not i:constructor_custom.append(dict(pc=hex(p),raw=raw[:n].hex()))
 p+=n
retained=json.loads((OUT.parents[2]/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
for z in retained['raw_ranges']:
 raw=bytes.fromhex(z.get('hex') or z.get('bytes_hex'));a=int(z['start'],16);assert r[a-BASE:a-BASE+len(raw)]==raw
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model_lines=model.read_text().splitlines(); excerpts=[]
for prefix in [':th.extu rd,rs1,15,15 ',':th.mula ']:
 k=next(i for i,l in enumerate(model_lines) if l.startswith(prefix))
 excerpts.append(dict(path=str(model),line=k+1,text='\n'.join(model_lines[k:k+6])))
assert ((0x3cf7b68b>>20)&63,0x3cf7b68b>>26)==(15,15)
assert ((0x20f6150b>>7)&31,(0x20f6150b>>15)&31,(0x20f6150b>>20)&31,0x20f6150b>>25)==(10,12,15,16)
out=dict(task='F05',mode='static only',engine=capstone.__version__,mapping='file_offset=VA-0x9ffff000',
 vendor_model_excerpts=excerpts,
 windows=windows,checks=checks,strings=strings,
 ordinary_sw_2b8_search=dict(range=[hex(BASE),hex(BASE+len(r))],alignment=2,matches=matches,
 limitation='Encoding scan; aliases, custom indexed stores, bulk writes and execution reachability are not covered.'),
 constructor_unknown_words=constructor_custom,
 retained_container_source=dict(evidence_id=retained['evidence_id'],profile=retained['profile']['digest'],raw_ranges_match=True),
 limitations=['No target code executed','obj+2b8 initial NULL established; value at delete call is not proven NULL',
 'No non-NULL obj+2b8 target established','Generic event array growth/deferred maintenance retain helper contracts; no reentrant path analysis',
 'No connection to caller loop, 62fc9428 or its data established; indirect effects remain unknown',
 'Source paths identify subsystem, not authenticated upstream version'])
(OUT/'instruction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS',len(checks),'instruction/edge checks;',len(windows),'windows;',sum(z-a for _,a,z in spans),'bytes;',len(matches),'SW encoding matches;',len(constructor_custom),'constructor custom words retained')
