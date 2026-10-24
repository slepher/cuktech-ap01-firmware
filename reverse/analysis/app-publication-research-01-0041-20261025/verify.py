"""Independent encoding checks for Q24; reads only the authorized ROM windows."""
import json
from pathlib import Path
from extract import ROOT, OUT, WINDOWS

def sx(v,b):return v-(1<<b) if v>>(b-1) else v
def jal_target(pc,w):
 imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 return (pc+sx(imm,21))&0xffffffff
CALLS={0xa011c10a:0xa005f3d8,0xa011c10e:0xa011bffe,0xa011c160:0xa0118a40,0xa011c1cc:0xa011f86c,0xa0113372:0xa011f9da,0xa0116b90:0xa0060cac,0xa0116bb6:0xa0061d20,0xa0116bec:0xa01b38b6,0xa0116c08:0xa0116ad0,0xa0116b36:0xa006929a,0xa0116b54:0xa002e14e}
EXACT={0xa011c18a:'13060003',0xa011c1a4:'832784fa',0xa011c1aa:'2146',0xa011c1c2:'8147',0xa011c1c4:'1307007d',0xa011c1ee:'054b',0xa0116b9e:'9387874b',0xa0116bb2:'230004fc',0xa0116bfa:'83a50900',0xa0116c02:'0946',0xa0116c04:'91c0',0xa0116c06:'0146',0xa0116b14:'fc58',0xa0116b1a:'23884407',0xa0116b22:'83a74408',0xa0116b28:'23a2f408'}
def main():
 raw=json.loads((OUT/'raw.json').read_text());assert sum(n for _,n in WINDOWS)==784
 rows={int(r['pc'],16):r for w in raw['windows'] for r in w['rows']}
 assert len(raw['windows'])==5 and all(r['asm']!='UNDECODED' for r in rows.values())
 with (ROOT/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as f:
  for w,(a,n) in zip(raw['windows'],WINDOWS):
   assert int(w['start'],16)==a and w['length']==n
   f.seek(a-0x9ffff000);assert f.read(n).hex()==w['raw']
   assert sum(len(bytes.fromhex(r['raw'])) for r in w['rows'])==n
  for pc,dest in CALLS.items():
   w=int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little');assert w&0x7f==0x6f and jal_target(pc,w)==dest
  for pc,h in EXACT.items():assert rows[pc]['raw']==h
  f.seek(0xa06124b8-0x9ffff000);assert f.read(7)==b'result\0'
 result=dict(status='PASS',bytes=784,instructions=len(rows),jal_checks=len(CALLS),exact_checks=len(EXACT),strings=1,unknown=0,execution='host static checks only; firmware never executed')
 (OUT/'checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
