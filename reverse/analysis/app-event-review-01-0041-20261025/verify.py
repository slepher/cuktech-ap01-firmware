"""Independent bounded ROM review. Never imports or runs author scripts or firmware."""
import json
from pathlib import Path
from datetime import datetime, timezone
import capstone
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
AUTHOR=Path('D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/event01')
STEM='app-event-research-01-0041-20261025'
source=ROOT if (ROOT/'reverse/analysis'/STEM/'raw.json').exists() else AUTHOR
saved=source/'reverse/analysis'/STEM
out=Path(__file__).resolve().parent
raw=json.loads((saved/'raw.json').read_text())
checks=json.loads((saved/'checks.json').read_text())
image=ROOT/'roms/0041/ap01-1.0.2_0041.bin'
assert image.stat().st_size==6769704
windows=[(0xa011408a,192),(0xa0113f6c,286),(0xa011c204,428),(0xa01af798,660)]
assert [(int(w['start'],16),w['length']) for w in raw['windows']]==windows
rows={}; decoder=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
with image.open('rb') as rom:
 for (va,size),w in zip(windows,raw['windows']):
  rom.seek(va-0x9ffff000); data=rom.read(size)
  assert data.hex()==w['raw']; pos=0
  for row in w['rows']:
   pc=int(row['pc'],16); b=bytes.fromhex(row['raw'])
   assert pc==va+pos and b==data[pos:pos+len(b)]
   assert len(b)==(4 if int.from_bytes(b[:2],'little')&3==3 else 2)
   decoded=list(decoder.disasm(b,pc))
   actual=decoded[0].mnemonic+' '+decoded[0].op_str if len(decoded)==1 and decoded[0].size==len(b) else 'UNDECODED'
   assert actual==row['asm']; rows[pc]=b; pos+=len(b)
  assert pos==size
 def readstr(va,s):
  rom.seek(va-0x9ffff000); assert rom.read(len(s)+1)==s.encode()+b'\0'
 for va,s in {0xa060eb68:'event.%s',0xa01c3280:'id',0xa056c058:'method',0xa01c2488:'params',0xa05658ec:'retry',0xa0627418:'timestamp',0xa059cf1c:'tick'}.items(): readstr(va,s)
def sx(n,b): return n-(1<<b) if n&(1<<(b-1)) else n
def word(pc): return int.from_bytes(rows[pc],'little')
# Reconstruct all twenty retained direct targets independently from ROM-backed words.
for p,t in checks['raw_calls'].items():
 pc=int(p,16); w=word(pc)
 if w&127==0x6f:
  imm=((w>>31)&1)<<20|((w>>12)&255)<<12|((w>>20)&1)<<11|((w>>21)&1023)<<1
  target=(pc+sx(imm,21))&0xffffffff
 else:
  assert w&127==0x17; v=word(pc+4); assert v&127==0x67 and ((w>>7)&31)==((v>>15)&31)
  target=(pc+sx(w&0xfffff000,32)+sx(v>>20,12))&0xfffffffe
 assert target==int(t,16)
assert len(checks['raw_calls'])==20
vendor={0xa0114126:'8bca9b44',0xa0114034:'0bc59a44',0xa0114044:'8bc54a45',0xa0114066:'0bc54a45',0xa0114074:'0bd0a700',0xa0114078:'0b454b58',0xa011c364:'8bc52b45',0xa01af840:'0b99f742',0xa01af9a6:'8bc5f644'}
model=(ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc').read_text()
for pc,hexraw in vendor.items():
 assert rows[pc].hex()==hexraw
 w=word(pc); fields=[(w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3]
 assert fields==checks['vendor_fields'][hex(pc)]
for k,v in checks['model_rules'].items(): assert v in model
assert word(0xa01af840)>>25==33
# Critical state/cleanup branch words anchor the manually reviewed control flow.
anchors={0xa01140a6:'63e3d706',0xa01140c6:'63e3a704',0xa0113fa8:'93058a08',0xa0113ffe:'83274900',0xa0114002:'23a02401',0xa0114006:'23229900',0xa011400a:'dcc0',0xa011400c:'84c3',0xa011c348:'2685',0xa01af830:'6375f51a',0xa01af838:'6356f000',0xa01af90a:'631d0510',0xa01af910:'23aa2b07',0xa01af914:'2388fb06',0xa01af95c:'0dc1',0xa01af96e:'0146',0xa01af97e:'4e85',0xa01afa10:'5e85',0xa01afa1a:'5e85'}
for pc,b in anchors.items(): assert rows[pc].hex()==b
root=json.loads((saved/'inherited-root.json').read_text())
assert root['evidence_id']=='ev_b7f9c05652b41f5486cbdecf96f07079792f9d25bf48dcfb216ec0448259d9a0'
assert root['analysis_profile']['digest']=='4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
result={'status':'PASS independent static review','author_source':str(saved),'author_commit':'1d7890db5a6288260bf576122fdaa01d300e9075','review_baseline':'8782ea6916e6879af8c044af60d2e5aa6988fb74','windows':4,'reread_bytes':1566,'instruction_rows':len(rows),'direct_calls':20,'vendor_words':9,'strings':7,'critical_anchors':len(anchors),'new_business_bytes':0,'semantic_corrections':0,'decoder':capstone.__version__,'started_utc':'2026-10-24 17:29:38 UTC','checked_utc':datetime.now(timezone.utc).isoformat(),'waiting':'Tool wall time only; queue and active compute not separately measured; no intentional sleep','tokens':None}
assert len(rows)==508
(out/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
