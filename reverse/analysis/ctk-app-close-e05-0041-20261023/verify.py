"""E05 static evidence collection. Never executes the firmware."""
import json
from pathlib import Path
from decode import decode, rom, BASE, regs, signed
HERE=Path(__file__).resolve().parent
spans=[
 ('app_create_and_state',0xa005cd68,0xa005cd98),
 ('app_registration_and_delete_hook',0xa005d0f2,0xa005d1a2),
 ('window_create',0xa00b2f6c,0xa00b2ff4),
 ('class_allocation_size',0xa00d76ae,0xa00d76ee),
 ('parent_child_attach',0xa00d77be,0xa00d7806),
 ('item_register',0xa01b28ce,0xa01b291a),
 ('item_dispatch',0xa00a389c,0xa00a3904),
 ('app_delete_callback',0xa00ab8ec,0xa00ab96c),
 ('event_registration_adapter',0xa01ad6a8,0xa01ad6d8),
 ('event_descriptor_writes',0xa01b9432,0xa01b943c),
 ('event_delivery_abi',0xa008ad72,0xa008adba),
 ('timer_delete',0xa008ae58,0xa008ae8c),
 ('list_remove_and_link_setters',0xa0089cda,0xa0089d76),
 ('list_append',0xa008af14,0xa008af68),
 ('window_destructor',0xa00b1df8,0xa00b1e54),
 ('class_destructor_dispatch',0xa00d7806,0xa00d7832),
 ('base_destructor',0xa00d87d0,0xa00d8860),
 ('delete_core',0xa00dcf52,0xa00dd144),
 ('same_head_other_key_remover',0xa00f2f98,0xa00f2fd2),
]
windows=[dict(name=n,start=hex(a),end_exclusive=hex(b),instructions=decode(a,b)) for n,a,b in spans]
for w in windows:
 assert int(w['instructions'][-1]['address'],16)+len(bytes.fromhex(w['instructions'][-1]['hex']))==int(w['end_exclusive'],16),w['name']
idx={int(r['address'],16):r for w in windows for r in w['instructions']}
checks=[]
def exact(pc,raw,label):
 assert idx[pc]['hex']==raw,(hex(pc),label)
 checks.append(dict(address=hex(pc),label=label,hex=raw))
for args in [
 (0xa005cd80,'2a8a','constructor result becomes app s4'),
 (0xa005cd82,'2145','separate state size eight'),
 (0xa005d122,'832784c3','reload state pointer'),
 (0xa005d12c,'2328fa00','state held in app+10'),
 (0xa005d140,'d285','item userdata is app'),
 (0xa005d142,'1305c5ab','callback low half'),
 (0xa005d18c,'a686','DELETE userdata is saved first timer'),
 (0xa005d18e,'13069002','DELETE filter 0x29'),
 (0xa005d192,'9385c58e','DELETE callback low half'),
 (0xa00ab908,'4441','callback original target e+4'),
 (0xa00ab90a,'03a90401','callback reads app+10 state'),
 (0xa00ab940,'4845','timer read from e+12'),
 (0xa00ab95e,'4a85','free receives state not app'),
 (0xa00ab964,'23a80400','clear app+10 after free'),
 (0xa008ad92,'23a6f900','delivery writes descriptor userdata'),
 (0xa008ad98,'8297','indirect cb(e) call'),
 (0xa008ae7a,'238fe75e','timer-list changed flag byte'),
 (0xa01b28fa,'04c1','node callback word'),
 (0xa01b28fc,'23222501','node app word'),
 (0xa00f2fa8,'13078728','other remover key a00f5288'),
 (0xa00b1e06,'a851','window dtor timer is obj+60'),
 (0xa00b1e18,'23aee75a','window dtor restores previous input association'),
 (0xa00dd03c,'2685','final free receives object'),
]: exact(*args)
def pair(pc,target):
 w=int.from_bytes(rom[pc-BASE:pc-BASE+4],'little');v=int.from_bytes(rom[pc-BASE+4:pc-BASE+8],'little')
 assert (pc+(w&0xfffff000)+signed(v>>20,12))&0xffffffff==target
 checks.append(dict(address=hex(pc),target=hex(target),kind='AUIPC/JALR'))
for pc,target in [(0xa005d146,0xa01b28ce),(0xa005d198,0xa01ad654),(0xa01b28f2,0xa008af14)]: pair(pc,target)
for pc,target in [(0xa00ab95a,0xa008ae58),(0xa00ab960,0xa008ab8a),(0xa008ae6e,0xa0089d02),(0xa008ae7e,0xa008ab8a),(0xa00f2fba,0xa0089d02),(0xa00dcf88,0xa00d831a),(0xa00dd000,0xa00d7806),(0xa00dd03e,0xa008ab8a)]:
 assert idx[pc]['target']==hex(target)
 checks.append(dict(address=hex(pc),target=hex(target),kind='direct-edge'))
class_va=0xa05647fc
class_data=[dict(address=hex(class_va+i),hex=rom[class_va-BASE+i:class_va-BASE+i+4].hex(),word=hex(int.from_bytes(rom[class_va-BASE+i:class_va-BASE+i+4],'little'))) for i in range(0,40,4)]
assert int(class_data[2]['word'],16)==0xa00b1df8
assert (int(class_data[8]['word'],16)>>4)&0xffff==0x68
# Bounded raw candidate search, deliberately not an alias proof. Retain false
# positives; later register clobber analysis distinguishes true head operands.
candidates=[]
for p in range(0x1000,0x1ba800,2):
 w=int.from_bytes(rom[p:p+4],'little')
 if w&0x7f!=0x37 or w&0xfffff000!=0x62fcb000: continue
 rd=(w>>7)&31
 for q in range(p+4,p+38,2):
  v=int.from_bytes(rom[q:q+4],'little');imm=signed(v>>20,12)
  if (v>>15)&31==rd and v&0x7f in (3,0x13) and 0x530<=imm<=0x53c:
   candidates.append(dict(lui=hex(p+BASE),candidate=hex(q+BASE),register=regs[rd],immediate=hex(imm)))
result=dict(rom='D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin',base=hex(BASE),windows=windows,checks=checks,class_words=class_data,head_candidate_search=dict(range_start='0xa0000000',range_end_exclusive='0xa01b9800',method='halfword LUI 62fcb000 then same-rs1 I-load/addi immediate 530..53c in next34 bytes; candidates include clobbers/data',candidates=candidates))
(HERE/'instruction-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Preserve retained provenance/ref boundary without duplicating entire UI function.
root=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json')
d=json.loads(root.read_text())
records=[]
for r in d['records']:
 if r['operation']=='analyze_function' and r['parameters']['procedure'] in ('0xa005cc1e','0xa00adabc','0xa00afc88'):
  n=r['normalized_result'];entry=r['parameters']['procedure']
  rec=dict(evidence_id=r['evidence_id'],procedure=entry,incoming_references=n['incoming_references'],callers=n['callers'])
  if entry=='0xa005cc1e': rec['selected_initializer_assembly']=[x for x in n['assembly'] if 0xa005d0f2<=int(x.split(':')[0],16)<0xa005d1a2]
  records.append(rec)
(HERE/'retained-boundaries.json').write_text(json.dumps(dict(source=str(root),records=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(windows)} windows; {sum(len(w["instructions"]) for w in windows)} instructions; {len(checks)} checks; {len(candidates)} head candidates; {len(records)} retained reference boundaries')
