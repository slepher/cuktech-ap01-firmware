"""Independent bounded static review; reads bytes, never executes target code."""
import hashlib,json
from pathlib import Path
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom)==6769704
base=0x9ffff000
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
author=json.loads((ROOT/'reverse/analysis/app-property-research-01-0041-20261025/bounded-evidence.json.tmp').read_text())
records=[]
for no,va,n in [('144',0xa0195034,176),('159',0xa01b5d70,764),('021',0xa00a116e,354)]:
 s=json.loads((ROOT/f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{no}.json').read_text(encoding='utf-8-sig'))['structuredContent']
 r=s['normalized_result'];assert int(r['procedure']['address'],16)==va and r['procedure']['body']['total_bytes']==n
 raw=rom[va-base:va-base+n]
 assert raw.hex()==next(w['hex'] for w in author['windows'] if int(w['start'],16)==va)
 # Independently retain each original instruction and ordinary decoder result, including custom gaps.
 lines=[]
 for line in r['assembly']:
  a=int(line.split(':')[0],16);data=rom[a-base:a-base+4];size=4 if data[0]&3==3 else 2
  i=next(md.disasm(data[:size],a),None)
  lines.append({'retained':line,'hex':data[:size].hex(),'host_decode':f'{i.mnemonic} {i.op_str}' if i else None})
 records.append({'record':no,'evidence_id':s['evidence_id'],'profile_digest':s['analysis_profile']['digest'],'assembly':lines,'raw_sha256':hashlib.sha256(raw).hexdigest()})
wrappers=[]
for va,n,typ in [(0xa01950e4,34,1),(0xa0195106,28,0),(0xa0195122,34,4),(0xa0195144,34,2)]:
 data=rom[va-base:va-base+n];ins=list(md.disasm(data,va));assert sum(i.size for i in ins)==n
 calls=[i for i in ins if i.mnemonic=='jal'];assert len(calls)==1 and calls[0].address+int(calls[0].op_str,0)==0xa0195034
 wrappers.append({'va':hex(va),'type':typ,'hex':data.hex(),'assembly':[f'{i.address:#x}: {i.mnemonic} {i.op_str}' for i in ins]})
strings=[]
for w in author['strings']:
 a=int(w['start'],16);data=bytes.fromhex(w['hex']);assert rom[a-base:a-base+len(data)]==data
 strings.append({'va':hex(a),'text':data[:-1].decode('ascii'),'hex':data.hex()})
s=json.loads((ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-024.json').read_text(encoding='utf-8-sig'))['structuredContent']
a=s['normalized_result']['assembly'];sites=[]
for k,line in enumerate(a[:-1]):
 if ': auipc ra,' not in line:continue
 pc=int(line.split(':')[0],16);hi=int(line.rsplit(', ',1)[1],0);nextline=a[k+1]
 if ': jalr ra, ra,' not in nextline:continue
 lo=int(nextline.rsplit(', ',1)[1],0)
 if (pc+(hi<<12)+lo)&0xffffffff==0xa01b5d70:
  assert 'c.li a0, 0x0' in a[k-1]
  sites.append({'callsite':hex(pc),'context':a[k-1:k+2]})
assert len(sites)==2
result={'checks':{'body_bytes':1294,'wrapper_bytes':130,'author_raw_and_strings_match':True,'consumer_zero_calls_024':len(sites),'static_only':True},'records':records,'wrappers':wrappers,'strings':strings,'seed024':{'evidence_id':s['evidence_id'],'sites':sites},'manual_review':'See report: ABI, branches, widths, borrowing, length gates, API boundary; no target execution.'}
(OUT/'independent-evidence.json.tmp').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checks':result['checks'],'seed024':result['seed024'],'custom_instructions':[x for r in records for x in r['assembly'] if x['host_decode'] is None]},ensure_ascii=False,indent=2))
