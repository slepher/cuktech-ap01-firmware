"""Independent P-R05 static review. Standard library only; no author code imported."""
import json
from pathlib import Path
from datetime import datetime, timezone
M=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
O=Path(__file__).resolve().parent
B=0x9ffff000
read=lambda p:json.loads((M/p).read_text(encoding='utf-8'))
a=read('reverse/analysis/telemetry-latch-p05-0041-20261024/static-evidence.json')
d=read(a['source']['path']); f=next(x for x in d['functions'] if x['address']=='0xa00a8582')
b=read(a['metadata_source']['path']);r=b['records'][2]
with (M/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as rom:
 rom.seek(0,2); assert rom.tell()==6769704
 def raw(pc,n=4):
  rom.seek(pc-B);return rom.read(n)
 def num(pc,n=4):return int.from_bytes(raw(pc,n),'little')
 def signed(x,n):return x-(1<<n) if x>>(n-1) else x
 def fields(pc):
  w=num(pc);return [w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,(w>>20)&31,w>>25]
 checks=[]
 def ck(name,actual,expected):
  assert actual==expected,(name,actual,expected)
  checks.append({'name':name,'actual':actual,'expected':expected})
 ck('ROM identity from retained metadata',d['rom_sha256'],a['rom_sha256'])
 ck('language',f['profile']['parameters']['language_id'],'RISCV:LE:32:ap01thead3')
 ck('profile agreement',r['analysis_profile']['digest'],f['profile']['digest'])
 ck('profile manifest',a['profile_digest'],f['profile']['digest'])
 ck('Evidence ID',r['evidence_id'],f['evidence_id'])
 rr=f['raw_ranges'][0];old=bytes.fromhex(rr['hex']);start=int(rr['start'],16)
 assembly={int(s.split(':',1)[0],16):s.split(':',1)[1].strip() for s in f['assembly']}
 coverage=[]
 for w in a['windows']:
  lo=int(w['start'],16);hi=int(w['end_exclusive'],16);actual=raw(lo,hi-lo)
  ck(w['name']+' ROM/author bytes',actual.hex(),w['hex'])
  ck(w['name']+' ROM/prior bytes',actual.hex(),old[lo-start:hi-start].hex())
  pc=lo
  for ins in w['instructions']:
   ck('instruction '+hex(pc),[ins['pc'],ins['file_offset'],ins['retained_decode'],ins['hex']],[hex(pc),pc-B,assembly[pc],raw(pc,4 if num(pc,2)&3==3 else 2).hex()])
   pc+=4 if num(pc,2)&3==3 else 2
  ck(w['name']+' end',pc,hi);coverage.append({'name':w['name'],'start':hex(lo),'end':hex(hi),'bytes':hi-lo})
 # Independently reconstruct the 30 non-text-search checks in the author's 33-item ledger.
 regenerated={}
 for w in a['windows']:
  lo=int(w['start'],16);hi=int(w['end_exclusive'],16)
  regenerated[w['name']+' retained bytes']=raw(lo,hi-lo).hex()
  regenerated[w['name']+' boundary']=hi
 for pc in [0xa00a8606,0xa00a8966,0xa00a8a06,0xa00a921c]:
  w=num(pc);v=fields(pc);off=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
  regenerated[hex(pc)+' branch']=[v[0],v[2],v[3],v[4],pc+signed(off,13)]
 for pc in [0xa00a8930,0xa00a8934,0xa00a8950,0xa00a8996,0xa00a89e0,0xa00a9212,0xa00a9228]:
  v=fields(pc);regenerated[hex(pc)+' load']=[v[0],v[1],v[2],v[3],signed(num(pc)>>20,12)]
 for pc in [0xa00a898e,0xa00a8a1e,0xa00a9234]:
  w=num(pc);v=fields(pc);regenerated[hex(pc)+' store']=[v[0],v[2],v[3],v[4],signed(((w>>25)<<5)|((w>>7)&31),12)]
 regenerated['count-zero branch c.beqz']=raw(0xa00a899a,2).hex()
 regenerated['record identity']=r['evidence_id']
 refs=[x for x in r['normalized_result']['outgoing_references'] if x.get('target_address')=='0x62fcb50a']
 regenerated['dispatcher exact target reference sites']=[[x['source_address'],x['kind']['type']] for x in refs]
 init=next(x for x in b['records'] if x.get('normalized_result',{}).get('procedure',{}).get('address')=='0xa005a736')
 regenerated['initializer exact-target metadata']=sum(x.get('target_address')=='0x62fcb50a' for x in init['normalized_result']['outgoing_references'])
 retry=read('reverse/analysis/uart-retry-receive-0041-20261023.json')
 for addr in ['0xa0191746','0xa00a5558']:
  q=next(x for x in retry['functions'] if x['address']==addr)
  regenerated[addr+' retained pseudocode exact token']=q['pseudocode'].lower().count('62fcb50a')
 ck('author ledger entries',len(a['checks']),33)
 ledger=[]
 for c in a['checks']:
  label=c['label'];ck('author internal '+label,c['actual'],c['expected'])
  if label in regenerated:
   ck('independent '+label,regenerated[label],c['expected']);status='independently rederived'
  else:
   assert label in ['0041-ghidra-pass'+str(n)+'.txt exact-address text count' for n in (3,4,5)]
   status='record-only; no text search rerun'
  ledger.append({'label':label,'status':status})
 ck('independently rederived author checks',len(regenerated),30)
 # Selected control and data flow beyond the author's check ledger.
 def cb(pc,rs,target):
  w=num(pc,2);imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
  ck('compressed branch '+hex(pc),[w&3,w>>13,8+((w>>7)&7),pc+signed(imm,9)],[1,6 if pc==0xa00a899a else 7,rs,target])
 cb(0xa00a893e,14,0xa00a8950);cb(0xa00a899a,10,0xa00a8a22)
 # JAL target (helper called before any latch-path loads/clear).
 pc=0xa00a8904;w=num(pc);off=(((w>>31)&1)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 ck('cache helper JAL target',pc+signed(off,21),0xa0191652)
 ck('writer AND',fields(0xa00a9218),[51,13,7,14,15,0])
 ck('writer variable SLL',fields(0xa00a922e),[51,13,1,13,18,0])
 ck('writer address LUI',num(0xa00a9220),0x62fcb7b7)
 ck('writer address ADDI',fields(0xa00a9224)[:4]+[num(0xa00a9224)>>20],[19,12,0,15,0x50a])
 ck('clear LUI',num(0xa00a8a1a),0x62fcb7b7)
 ck('vendor bytes retained',raw(0xa00a893a).hex(),'0b37073c')
 ck('vendor field operands',[fields(0xa00a893a)[1],fields(0xa00a893a)[3],num(0xa00a893a)>>26,(num(0xa00a893a)>>20)&63],[14,14,15,0])
 helper=next(x for x in retry['functions'] if x['address']=='0xa0191652')
 h={int(s.split(':',1)[0],16):s.split(':',1)[1].strip() for s in helper['assembly']}
 for pc,expected in [(0xa01916c0,'lbu a0, 0x0, s1'),(0xa01916c8,'addi a0, a0, 0x20'),(0xa01916cc,'andi a0, a0, 0xff'),(0xa01916d0,'c.jalr a5')]:
  ck('inherited notification instruction '+hex(pc),h[pc],expected)
 result={'claim':'P-R05','time_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS','checks':len(checks),'windows':coverage,'total_bytes':sum(x['bytes'] for x in coverage),'author_33_ledger':ledger,'checks_detail':checks,'helper_source':{'path':'reverse/analysis/uart-retry-receive-0041-20261023.json','evidence_id':helper['evidence_id'],'profile_digest':helper['profile_digest']},'limitations':['No execution or ISA simulation; standard-library field extraction only.','Three negative text searches accepted only as bounded author records; not rerun.','No global xref coverage, independent reader, request meaning or latch-specific notification established.','Vendor instruction semantic interpretation inherited from retained profile, raw fields preserved.']}
 (O/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:result[k] for k in ['status','checks','total_bytes','time_utc']}))
