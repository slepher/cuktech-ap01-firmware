"""Independent Q22 static byte/provenance review; never imports author code."""
import hashlib,json,re,sys
from pathlib import Path
import capstone
root=Path(sys.argv[1]); out=Path(__file__).parent
source=root/'reverse/analysis/app-rpc-action-research-01-0041-20261025'
rom=(root/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert len(rom)==6769704 and sha(rom)=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
windows=json.loads((source/'windows.json').read_text())
expected=json.loads((source/'contract.json').read_text())['windows']
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
lines=[]; actual=[]; unknown=[]
for va,n in [(0xa00bec0c,676),(0xa00c5b8c,664),(0xa00bd924,20),(0xa00c0b5a,20),(0xa00bd7fa,278)]:
 b=rom[va-0x9ffff000:va-0x9ffff000+n]
 w={'va':hex(va),'length':n,'offset':va-0x9ffff000,'sha256':sha(b)}
 actual.append(w)
 cached=next(x for x in windows if int(x['va'],16)==va)
 assert bytes.fromhex(cached['hex'])==b
 pos=0
 while pos<n:
  i=next(md.disasm(b[pos:],va+pos,count=1),None)
  if i:
   lines.append(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}')
   pos+=i.size
  else:
   unknown.append(hex(va+pos));lines.append(f'{va+pos:08x} {b[pos:pos+4].hex()} UNKNOWN');pos+=4
 assert pos==n
assert actual==expected and unknown==['0xa00c5d74']
# Compare every author textual instruction encoding directly against immutable ROM.
count=0
for line in (source/'disassembly.txt').read_text().splitlines():
 m=re.match(r'^([0-9a-f]{8}) ([0-9a-f]+)\s',line)
 if m:
  va=int(m[1],16);b=bytes.fromhex(m[2]);assert rom[va-0x9ffff000:va-0x9ffff000+len(b)]==b;count+=1
bundle=json.loads((root/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8'))
parents=json.loads((source/'parent-links.json').read_text())
for parent in parents:
 r=bundle['records'][int(parent['pointer'].split('/')[-1])]
 assert r['analysis_profile']['digest']==parent['profile']
 assert parent['evidence_id'] in json.dumps(r)
 for text in parent['callback_install_assembly']:
  assert text in json.dumps(r),text
strings={0xa01c3280:'id',0xa06124b8:'result',0xa060f238:'did',0xa0564d04:'siid',0xa0564d28:'aiid',0xa0564d4c:'piid',0xa0564dbc:'iid',0xa056bd3c:'code',0xa0259268:'out',0xa0569390:'value',0xa06189f0:'error',0xa0618098:'message',0xa05652b8:'user ack invalid',0xa0564db0:'%lu.%lu.%lu'}
for va,s in strings.items():
 offset=va-0x9ffff000; assert rom[offset:offset+len(s)+1]==s.encode()+b'\0',(hex(va),s)
result={'rom_length':len(rom),'rom_sha256':sha(rom),'windows':actual,'total_bytes':sum(w['length'] for w in actual),'instruction_lines_checked':count,'unknown':unknown,'parents_checked':[p['pointer'] for p in parents],'strings_checked':len(strings),'new_business_bytes':0,'author_code_executed':False,'capstone':capstone.__version__}
(out/'independent-check.json').write_text(json.dumps(result,indent=2)+'\n')
(out/'independent-disassembly.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps(result,indent=2))
