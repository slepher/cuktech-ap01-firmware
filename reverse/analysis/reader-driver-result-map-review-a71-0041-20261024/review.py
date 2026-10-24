"""A71 static encoding review only: no input execution or instruction model."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
START = 0xa00ea524
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
data = rom[START-BASE:START-BASE+140]
instructions = list(Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC).disasm(data, START))
assert sum(i.size for i in instructions) == len(data)
fields = []

def sx(x, bits):
    return x - (1 << bits) if x & (1 << (bits-1)) else x

def raw(suffix, size):
    off = 0xa00e0000 + suffix - START
    return int.from_bytes(data[off:off+size], 'little')

def checked(kind, address, actual, expected):
    assert actual == expected, (kind, hex(address), actual, expected)
    fields.append(dict(kind=kind, address=hex(0xa00e0000+address), value=actual))

# Independent B-immediate/register/funct3 extraction; tuples are static edge facts.
branches = [
    (0xa52c,0,10,15,0xa5ac), (0xa530,4,15,10,0xa572),
    (0xa538,0,10,14,0xa556), (0xa53c,4,14,10,0xa55e),
    (0xa544,0,10,14,0xa556), (0xa54c,0,10,14,0xa556),
    (0xa562,0,10,14,0xa556), (0xa56a,1,10,14,0xa556),
    (0xa578,0,10,14,0xa556), (0xa57c,4,14,10,0xa594),
    (0xa584,0,10,14,0xa556), (0xa58c,1,10,14,0xa556),
    (0xa59a,0,10,14,0xa556), (0xa5a4,1,10,14,0xa556)]
for pc,f3,r1,r2,target in branches:
    w=raw(pc,4)
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    checked('B', pc, [w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,pc+sx(imm,13)], [99,f3,r1,r2,target])

# Constant definition sites, not host invocations of the mapper.
constants = [(0xa52a,15,16),(0xa534,14,12),(0xa536,15,10),
 (0xa540,14,2),(0xa542,15,3),(0xa548,14,5),(0xa54a,15,1),
 (0xa550,15,12),(0xa554,15,0),(0xa55e,14,13),(0xa560,15,6),
 (0xa566,14,14),(0xa568,15,12),(0xa56e,15,2),(0xa576,15,9),
 (0xa580,14,22),(0xa582,15,11),(0xa588,14,28),(0xa58a,15,12),
 (0xa590,15,4),(0xa598,15,8),(0xa5a2,15,12),(0xa5a8,15,5),(0xa5ac,15,7)]
for pc,rd,value in constants:
    w=raw(pc,2)
    checked('C.LI',pc,[w&3,w>>13,(w>>7)&31,sx(((w>>2)&31)|(((w>>12)&1)<<5),6)],[1,2,rd,value])
for pc,value in [(0xa572,38),(0xa594,110),(0xa59e,114)]:
    w=raw(pc,4)
    checked('ADDI constant',pc,[w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,sx(w>>20,12)],[19,14,0,0,value])
for pc in [0xa570,0xa592,0xa5aa,0xa5ae]:
    w=raw(pc,2)
    imm=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
    checked('C.J',pc,[w&3,w>>13,pc+sx(imm,12)],[1,5,0xa556])
w=raw(0xa552,2)
imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
checked('C.BNEZ',0xa552,[w&3,w>>13,8+((w>>7)&7),0xa552+sx(imm,9)],[1,7,10,0xa556])
anchors={0xa524:'4111',0xa526:'22c6',0xa528:'0008',0xa556:'3244',0xa558:'3e85',0xa55a:'4101',0xa55c:'8280'}
for pc,expected in anchors.items():
    checked('frame/return raw',pc,raw(pc,2).to_bytes(2,'little').hex(),expected)
# Full finite span decoded only for effect inventory; no control-path execution.
memory=[(hex(i.address),i.mnemonic,i.op_str) for i in instructions if i.mnemonic in ('c.swsp','c.lwsp') or i.mnemonic.startswith(('lw','sw','lb','sb','lh','sh'))]
assert memory == [('0xa00ea526','c.swsp','s0, 0xc(sp)'),('0xa00ea556','c.lwsp','s0, 0xc(sp)')]
assert not any(i.mnemonic in ('jal','jalr','c.jal','c.jalr') for i in instructions)
assert [i.address for i in instructions if i.mnemonic in ('c.jr','ret')] == [0xa00ea55c]
result={'task':'A71','method':'static fields and symbolic leaf review; no mapper/input execution', 'bytes':140,'field_checks':len(fields),'inventory_checks':3,'fields':fields,'memory':memory,'callee':[]}
Path(__file__).with_name('evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f"PASS {len(fields)} field checks + 3 effect checks; 140B; no input enumeration")
