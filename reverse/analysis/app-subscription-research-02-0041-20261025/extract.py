"""Q23 bounded static extraction. Never executes the target or changes REA."""
import hashlib
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
SPANS = [(0xa01189b8,62),(0xa01189f6,74),(0xa0118a40,200),
         (0xa0118b8a,76),(0xa0118bd6,74),(0xa0118c20,38),(0xa0118c46,80)]
rom = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
data = rom.read_bytes()
assert len(data) == 6769704
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = []
for addr, size in SPANS:
    raw = data[addr-0x9ffff000:addr-0x9ffff000+size]
    ins = list(cs.disasm(raw, addr))
    assert sum(i.size for i in ins) == size
    windows.append(dict(start=hex(addr), end_exclusive=hex(addr+size), size=size,
                        offset=addr-0x9ffff000, sha256=hashlib.sha256(raw).hexdigest(),
                        raw_hex=raw.hex(), instructions=[dict(address=hex(i.address),
                        bytes=i.bytes.hex(), mnemonic=i.mnemonic, operands=i.op_str) for i in ins]))
bundle = ROOT / 'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
records = json.loads(bundle.read_text(encoding='utf-8'))['records']
r = records[245]
# Only the already-retained caller interface anchors; no new root disassembly.
ranges = [(0xa011631c,0xa011633a),(0xa01163c4,0xa0116464),
          (0xa0116468,0xa011648c),(0xa01165a6,0xa0116656),
          (0xa01166c0,0xa01167ea),(0xa01168c2,0xa01168fa)]
anchors = [s for s in r['normalized_result']['assembly']
           if any(lo <= int(s.split(':')[0],16) <= hi for lo,hi in ranges)]
result = dict(claim='Q23', artifact=str(rom), size=len(data),
              inherited_artifact_sha256='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
              method='Capstone 5.0.7 RV32+C, static, no target execution',
              new_bytes=sum(n for _,n in SPANS), windows=windows,
              inherited_root=dict(source=str(bundle), pointer='/records/245/normalized_result/assembly',
                                  evidence_id=r['evidence_id'], profile=r['analysis_profile']['digest'],
                                  assembly=anchors),
              inherited_unsub=dict(pointer='/records/48', evidence_id=records[48]['evidence_id']))
(OUT/'static-windows.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Q23: 7 complete static windows, 604 B; retained root anchors:',len(anchors))
