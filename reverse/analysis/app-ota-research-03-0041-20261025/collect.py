"""Bounded static original-byte collection; never executes target instructions."""
import argparse, hashlib, json, struct
from pathlib import Path
import capstone

p = argparse.ArgumentParser()
p.add_argument('--source-root', type=Path, required=True)
a = p.parse_args()
rom = (a.source_root / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
def read(va, size): return rom[va-0x9ffff000:va-0x9ffff000+size]
assert struct.unpack('<6I', read(0xa060fd34, 24)) == (0xa0113a76, 0, 0xa0113aac, 0xa0113b4e, 0xa0115702, 0xa010f9f8)
md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
windows = []
for va, size in [(0xa012193c,1158),(0xa0113a76,54),(0xa0113aac,162),(0xa0113b4e,92),(0xa0115702,252),(0xa010f9f8,228),(0xa011398a,236)]:
    raw = read(va,size)
    insns = []
    pos = 0
    while pos < size:
        i = next(md.disasm(raw[pos:],va+pos,count=1),None)
        if i:
            insns.append({'address':hex(i.address),'hex':i.bytes.hex(),'text':i.mnemonic+' '+i.op_str})
            pos += i.size
        else:
            n = 2 if raw[pos]&3 != 3 else 4
            insns.append({'address':hex(va+pos),'hex':raw[pos:pos+n].hex(),'text':'UNKNOWN'})
            pos += n
    windows.append({'address':hex(va),'length':size,'hex':raw.hex(),'instructions':insns})
out = Path(__file__).with_name('raw-windows.json')
out.write_text(json.dumps({'capstone':capstone.__version__,'table_hex':read(0xa060fd34,24).hex(),'windows':windows},indent=2)+'\n',encoding='utf-8')
for w in windows:
    print('\n'+w['address'])
    for i in w['instructions']: print(i['address'],i['hex'],i['text'])
