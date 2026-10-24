"""Independent bounded static verification for Q-29; never executes ROM."""
import hashlib, json
from pathlib import Path
import capstone
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
AUTHOR=Path('D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/rpc-property02')
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom)==6769704
assert hashlib.sha256(rom).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
expected=json.loads((AUTHOR/'reverse/analysis/app-rpc-property-research-02-0041-20261025/windows.json').read_text())
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
seen={}; result=[]; unknown={}
for va,n in [(0xa00beeb0,468),(0xa00c59d4,440),(0xa00bb0f6,26),(0xa00c0478,26),(0xa00bb80e,114)]:
    raw=rom[va-0x9ffff000:va-0x9ffff000+n]
    source=next(w for w in expected if int(w['va'],16)==va)
    assert bytes.fromhex(source['hex'])==raw
    assert source['offset']==va-0x9ffff000 and source['length']==n
    digest=hashlib.sha256(raw).hexdigest(); assert source['sha256']==digest
    pos=0
    while pos<n:
        ins=next(md.disasm(raw[pos:],va+pos,count=1),None)
        if ins:
            seen[ins.address]=ins.mnemonic+' '+ins.op_str
            width=ins.size
        else:
            width=4 if raw[pos]&3==3 else 2
            unknown[hex(va+pos)]=raw[pos:pos+width].hex()
        pos+=width
    assert pos==n
    result.append({'va':hex(va),'length':n,'offset':va-0x9ffff000,'sha256':digest})
assert unknown=={'0xa00bef08':'0bca2a45','0xa00bef26':'0bcafa44','0xa00bef44':'0bcafa44','0xa00bef62':'8bcb4a45','0xa00bef84':'0bc54a45'}
anchors={0xa00c5a0e:'andi a5, a0, 3',0xa00bb870:'sw zero, 0x4c(s1)',0xa00bb874:'sw zero, 0x48(s1)',0xa00bf048:'c.lw a1, 0x68(s1)',0xa00c5ac2:'lw a1, 0x68(s2)',0xa00bb10a:'c.li a0, -1',0xa00c048c:'c.li a0, -1'}
for address,desc in anchors.items(): assert seen[address]==desc,(hex(address),seen[address])
assert sum(w['length'] for w in result)==1074
out={'rom_sha256':hashlib.sha256(rom).hexdigest(),'windows':result,'unknown':unknown,'anchors':{hex(a):d for a,d in anchors.items()},'instruction_count':len(seen),'scope':'static only; unknown vendor words remain unknown; API ownership unproved'}
Path(__file__).with_name('review-results.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS: ROM identity, five windows/1074 B, independent decode, five preserved unknown words, seven anchors')
metadata=json.loads((ROOT/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text(encoding='utf-8'))['functions']
for w in result:
    item=next(f for f in metadata if f['address']==w['va'])
    body=item['extent']['body']
    assert body['total_bytes']==w['length']
    assert int(body['ranges'][0]['start'],16)==int(w['va'],16)
    assert int(body['ranges'][0]['end'],16)-int(w['va'],16)+1==w['length']
print('PASS: master metadata exact extents; metadata is not body evidence')
