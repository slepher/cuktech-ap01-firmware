"""Independent Q06 static review; never imports author collectors or runs target."""
import hashlib
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
image = (SOURCE / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(image) == 6769704
assert hashlib.sha256(image).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
records = json.loads((SOURCE / 'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text())['records']
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
regions = [(248, 0xa006580c, 0xa0065842), (273, 0xa006cdf8, 0xa006ce1c),
           (273, 0xa006d02a, 0xa006d074), (273, 0xa006d0b6, 0xa006d0d8),
           (273, 0xa006d124, 0xa006d16c), (273, 0xa006d1a0, 0xa006d260),
           (252, 0xa0067210, 0xa006726a), (None, 0xa005fac4, 0xa005faec)]
views = []
insns = {}
for rec, first, end in regions:
    raw = image[first-0x9ffff000:end-0x9ffff000]
    decoded = list(decoder.disasm(raw, first))
    assert sum(i.size for i in decoded) == len(raw)
    insns.update({i.address: i for i in decoded})
    view = dict(start=hex(first), end_exclusive=hex(end), raw=raw.hex(),
                instructions=[f'{i.address:#x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in decoded])
    if rec is not None:
        r = records[rec]
        assert r['analysis_profile']['digest'] == '4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
        view.update(record=rec, evidence_id=r['evidence_id'], profile=r['analysis_profile']['digest'],
                    retained=[s for s in r['normalized_result']['assembly'] if first <= int(s.split(':')[0],16) < end])
    views.append(view)

def word(a):
    return int.from_bytes(insns[a].bytes, 'little')

def signed(v, bits):
    return v - (1 << bits) if v & (1 << (bits-1)) else v

def jump(a):
    w = word(a)
    return a + signed(((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1), 21)

checks = []
def require(label, yes):
    assert yes, label
    checks.append(label)

require('N+180 base and cda4 construction', signed(word(0xa0065810)>>20,12)==0x180 and (word(0xa0065824)&0xfffff000)+signed(word(0xa0065828)>>20,12)==0xa006cda4)
for a in range(0xa006580c,0xa0065842,2):
    if a in insns and insns[a].mnemonic in ('sw', 'c.sw'):
        print(f'{a:#x}: {insns[a].op_str}')
require('association API and fd close', jump(0xa006d064)==0xa0075d6a and jump(0xa006d06c)==0xa0026888)
require('s2 association saved independently', insns[0xa006d068].op_str == 's2, a0')
require('s5 request saved independently', insns[0xa006d1a8].op_str == 's5, a0' and jump(0xa006d1a4)==0xa00992d2)
require('signed DHCP >=0 branch', insns[0xa006d1aa].mnemonic in ('bgez','bge'))
require('return moves s2 to a0', any(i.mnemonic in ('mv','c.mv') and i.op_str=='a0, s2' for a,i in insns.items() if 0xa006cdf8<=a<0xa006ce1c))
require('request failure and success both cleanup', jump(0xa006d1f6)==jump(0xa006d24a)==0xa005fac4)
require('down interrupts distinct public API', jump(0xa0067236)==0xa0098a98)
require('cleanup delegates other API then zero store', jump(0xa005fada)==0xa0098af0 and word(0xa005fade)==0x0004a023)
require('same global helper address', (word(0xa005face)&0xfffff000)+signed(word(0xa005fad2)>>20,12)==0x62fc99e4)
require('down has no store instructions', all(i.mnemonic not in ('sw','sb','sh','c.sw','c.swsp') for a,i in insns.items() if 0xa0067210<=a<0xa006726a))
require('down reload address matches DHCP slot', (word(0xa006722c)&0xfffff000)+signed(word(0xa0067230)>>20,12)==0x62fc99e4)
require('DHCP store address matches slot', (word(0xa006d14e)&0xfffff000)+signed(((word(0xa006d152)>>25)<<5)|((word(0xa006d152)>>7)&31),12)==0x62fc99e4)
for addr, offset in [(0xa0065818,0x6c),(0xa0065822,0x70),(0xa006582c,0x78),(0xa0065836,0x7c),(0xa0065840,0x74)]:
    w=word(addr)
    decoded_offset=(((w>>5)&1)<<6)|(((w>>10)&7)<<3)|(((w>>6)&1)<<2)
    require(f'32bit callback slot {addr:#x}', w&0xe003==0xc000 and decoded_offset==offset)
result=dict(checks=checks, views=views, sha256=hashlib.sha256(image).hexdigest(), limits='Static original bytes and retained assembly; no runtime or public API internals')
(OUT/'review-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS: {len(checks)} checks; {sum(b-a for _,a,b in regions)} bytes')
