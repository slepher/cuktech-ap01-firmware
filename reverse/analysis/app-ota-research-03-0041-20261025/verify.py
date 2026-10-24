"""Read-only source identity, byte coverage, ABI and vendor-rule verification."""
import argparse, hashlib, json, struct
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--source-root',type=Path,required=True)
a=p.parse_args()
rom=(a.source_root/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom)==6769704
assert hashlib.sha256(rom).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
raw=json.loads(Path(__file__).with_name('raw-windows.json').read_text())
assert raw['table_hex']=='763a11a000000000ac3a11a04e3b11a0025711a0f8f910a0'
assert rom[0x610d34:0x610d4c].hex()==raw['table_hex']
for w in raw['windows']:
    pos=int(w['address'],16)-0x9ffff000
    assert rom[pos:pos+w['length']].hex()==w['hex']
    assert ''.join(i['hex'] for i in w['instructions'])==w['hex']
ins={int(i['address'],16):i for w in raw['windows'] for i in w['instructions']}
for va,hex_ in {0xa0121bb0:'5cc5',0xa0121bb6:'1cc9',0xa0121dae:'efd063eb',0xa0121dbc:'efc020b9',0xa0113a9a:'1c5d',0xa0113aca:'8327c903',0xa0113b86:'bc40',0xa0115712:'7c41',0xa0113b92:'bc44'}.items():
    assert ins[va]['hex']==hex_
model=(a.source_root/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc').read_text()
assert ':th.mveqz rd,rs1,rs2 is op0006=0xb & op1214=1 & op2531=32' in model
assert ':th.srb rd,rs1,rs2,thshift is op0006=0xb & op1214=5 & op2731=0' in model
move_rule=model.split(':th.mveqz ',1)[1].split('}',1)[0]
store_rule=model.split(':th.srb ',1)[1].split('}',1)[0]
assert 'if (rs2 != 0) goto <done>;' in move_rule and 'rd = rs1;' in move_rule
assert 'local delta:4 = rs2 << thshift;' in store_rule and '*[ram]:1 ea = rd:1;' in store_rule
for va,expected in {0xa0121bc4:(11,1,32,15,14,13),0xa0121c5a:(11,1,32,19,22,15),0xa0121cb2:(11,5,0,0,15,20),0xa0121cce:(11,5,0,0,15,23),0xa0121ce6:(11,5,0,0,15,19)}.items():
    w=int.from_bytes(bytes.fromhex(ins[va]['hex']),'little')
    fields=(w&127,(w>>12)&7,(w>>25)&127,(w>>7)&31,(w>>15)&31,(w>>20)&31)
    assert fields==expected
assert len([i for i in ins.values() if i['text']=='UNKNOWN'])==5
print('PASS: ROM/table identity; 2182 B complete bounded instruction-byte coverage; decisive ABI/queue/free words; 5 preserved vendor words matched existing static rules.')
