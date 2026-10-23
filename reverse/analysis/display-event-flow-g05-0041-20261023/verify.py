"""G05 static extraction and contracts; never executes firmware or imported historical validators."""
from pathlib import Path
import json
import read_rom as rr
OUT=Path(__file__).resolve().parent
spans=[('construct_identity',0xa0084da6,0xa0084daa),('construct_clear',0xa0084de8,0xa0084e32),('construct_timer',0xa0084e6e,0xa0084eea),('construct_descriptor',0xa0086b98,0xa0086bc6),('construct_final_timer',0xa00872e8,0xa00872ee),('replace_callback',0xa00873b6,0xa00873c6),('register_wrapper',0xa007ffa0,0xa0080002),('real_callback',0xa0080002,0xa0080030),('register',0xa01b93b4,0xa01b951c),('event_wrapper',0xa00814f4,0xa0081554),('dispatcher',0xa008acfa,0xa008adf4),('timer_create',0xa008bc64,0xa008bd16),('resume_pause',0xa008bd16,0xa008bdd4),('notify',0xa0087b06,0xa0087b30),('timer_scheduler',0xa00804e2,0xa00806d0),('poll_adapter',0xa0080da6,0xa0080dfe),('consumer_entry',0xa00e0ac8,0xa00e0b70),('delete_event_boundary',0xa0081554,0xa008158a),('delete_timer_boundary',0xa00815c8,0xa0081604),('descriptor_delete',0xa008b7f0,0xa008b888),('descriptor_cleanup',0xa008ac38,0xa008acfa),('timer_delete',0xa008ae58,0xa008ae8c),('alternative_install',0xa0083494,0xa0083528),('alternative_callback',0xa00806d0,0xa0080728),('submit_event_calls',0xa00ddd64,0xa00ddde0)]
windows=[]; D={}
for name,a,z in spans:
 rs=list(rr.rows(a,z)); assert sum(len(bytes.fromhex(r['raw'])) for r in rs)==z-a
 windows.append(dict(name=name,start=hex(a),end=hex(z),rows=rs));D.update({int(r['pc'],16):r for r in rs})
checks=[]
def asm(pc,v):
 assert D[pc]['asm']==v,(hex(pc),D[pc]['asm'],v)
 checks.append(dict(pc=hex(pc),asm=v))
def raw(pc,v):
 assert D[pc]['raw']==v,(hex(pc),D[pc]['raw'],v)
 checks.append(dict(pc=hex(pc),raw=v))
def edge(pc,v):
 assert D[pc]['target']==hex(v),(hex(pc),D[pc],hex(v))
 checks.append(dict(pc=hex(pc),target=hex(v)))
for p,v in {
0xa0084dec:0xa0080d8e,0xa0084ee2:0xa008bc64,0xa0086bba:0xa007ffa0,0xa007fff0:0xa01b93b4,
0xa0080022:0xa008bd70,0xa0081532:0xa008acfa,0xa0081544:0xa008acfa,0xa008bdc6:0xa0087b06,
0xa008bc82:0xa008aec0,0xa008bce2:0xa008b17e,0xa00805b0:0xa008b17e,0xa0080594:0xa008b236,
0xa0080ddc:0xa003f546,0xa0080dee:0xa00e0ac8,0xa00e0af4:0xa008bd16,0xa00815e4:0xa008ae58,
0xa008157e:0xa00814f4,0xa0081586:0xa008b7f0,0xa008ae6e:0xa0089d02,0xa008ae7e:0xa008ab8a,
0xa0083522:0xa007ffa0,0xa00806e6:0xa00e0ac8,0xa008071a:0xa009f9b6,
0xa01b93d0:0xa008ae8c,0xa01b94f6:0xa008ab76,0xa008b852:0xa008acc6,0xa008acae:0xa008ab8a}.items():edge(p,v)
for p,v in {
0xa0084de8:'addi a1, zero, 0x324',0xa0084e94:'addi s3, s1, 0x300',0xa0084eca:'lui a0, 0xa00e1',0xa0084ed6:'addi a0, a0, -0x538',0xa0084ed2:'c.mv a2, s1',0xa0084ed4:'c.li a1, 0x10',0xa0084ee6:'sw a0, 8(s3)',
0xa0086ba2:'lui a1, 0xa0080',0xa0086baa:'c.li a3, 0',0xa0086bac:'addi a2, zero, 0x38',0xa0086bb0:'addi a1, a1, 2',0xa0086bb4:'c.mv a0, s1',0xa0086bbe:'lw s2, 0x308(s1)',
0xa00873b6:'lui a5, 0xa0081',0xa00873ba:'addi a5, a5, -0x25a',0xa00873be:'c.sw a5, 8(a4)',0xa007ffec:'addi a0, a0, 0x2e8',
0xa0080002:'c.lw a5, 8(a0)',0xa0080006:'c.addi a4, -1',0xa0080012:'c.lw a5, 4(a0)',0xa0080014:'lw a0, 0x308(a5)',
0xa01b9432:'c.sw a1, 0(a0)',0xa01b9438:'c.sw a2, 8(a5)',0xa01b943a:'c.sw a3, 4(a5)',0xa01b9502:'c.sw a5, 4(s1)',
0xa0081522:'sw a2, -0x1c(s0)',0xa008ad92:'sw a5, 0xc(s3)',0xa008ad98:'c.jalr a5',0xa008bdc0:'c.andi a5, -2',0xa008bdc2:'sb a5, 0x14(a0)',0xa008bd66:'ori a5, a5, 1',
0xa0087b12:'sw zero, 0x84(a5)',0xa0087b0e:'lw a4, 0x9c(a5)',0xa0087b20:'lw a0, 0xa0(a5)',0xa0087b24:'c.jalr a4',
0xa008bcd4:'c.sw a1, 0(a0)',0xa008bcd6:'sw s3, 8(a0)',0xa008bcea:'c.sw a0, 4(s1)',0xa008bcec:'sw s2, 0xc(s1)',0xa008bcce:'c.sw a5, 0x10(a0)',
0xa0080598:'lw a5, 0(s2)',0xa00805a0:'lw s9, 0x10(s2)',0xa00805ac:'sw a5, 0x10(s2)',0xa00805b4:'lw a5, 8(s2)',0xa00805b8:'sw a0, 4(s2)',0xa00805c4:'c.mv a0, s2',0xa00805c6:'c.jalr a5',
0xa0080db4:'c.lw a0, 0xc(a0)',0xa0080dce:'sw a5, -0x28(s0)',0xa0080dd8:'sw a5, -0x24(s0)',0xa0080de4:'lw a5, -0x20(s0)',0xa0080de8:'c.andi a5, 4',
0xa00e0af0:'c.lw a5, 0xc(a0)',0xa00e0af2:'c.sw a5, 0x10(s1)',0xa008b87e:'c.lw a5, 8(a4)',0xa008b884:'c.sw a5, 8(a4)',0xa008acb6:'c.sw a5, 0(a0)',
0xa00815de:'lw a0, 0x308(s1)',0xa00834f0:'addi a1, a1, 0x728',0xa0083518:'addi a2, zero, 0x38',0xa008351c:'addi a1, a1, 0x6f8',0xa00806f8:'c.lw a0, 0xc(a0)',0xa008070e:'sb a5, 4(a0)',
0xa00ddd76:'c.li a2, 0',0xa00ddd90:'addi a2, s0, -0x30',0xa00ddd94:'addi a1, zero, 0x35'}.items():asm(p,v)
raw(0xa01b94f2,'0b15f620');raw(0xa008ad78,'8bb6f73c')
MODEL=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc')
model=MODEL.read_text(encoding='utf-8');parts={}
for token in (':th.extu rd,rs1,15,15 ',':th.mula rd,rs1,rs2 '):
 a=model.index(token);parts[token]=model[a:model.index('\n}',a)+2]
# This bounded linear scan finds encoded direct edges; it does not prove all indirect registrations absent.
refs=[r for r in rr.rows(0xa0000000,0xa01c0000) if r['target'] in ('0xa007ffa0','0xa01b93b4')]
(OUT/'evidence.json').write_text(json.dumps(dict(mapping='VA - 0x9ffff000',windows=windows,checks=checks,direct_reference_scan=dict(start='0xa0000000',end='0xa01c0000',rows=refs),model_source=str(MODEL),model_text=parts),indent=2),encoding='utf-8')
(OUT/'instructions.txt').write_text('\n'.join('\n'+w['name']+'\n'+'\n'.join((r['pc']+' off='+hex(int(r['pc'],16)-rr.BASE)+' '+r['raw']+' '+r['asm']+' '+(r['target'] or '')).rstrip() for r in w['rows']) for w in windows),encoding='utf-8')
print('passed',len(windows),'windows',sum(len(w['rows']) for w in windows),'instructions',len(checks),'checks',len(refs),'direct refs')
