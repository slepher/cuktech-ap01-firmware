"""Q23 independent bounded static review. Does not execute author or target code."""
import json, hashlib
from pathlib import Path
import capstone
ROOT=Path("D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware")
ROM=ROOT/"roms/0041/ap01-1.0.2_0041.bin"
OUT=Path(__file__).resolve().parent
WINDOWS=[(0xa01189b8,62),(0xa01189f6,74),(0xa0118a40,200),(0xa0118b8a,76),(0xa0118bd6,74),(0xa0118c20,38),(0xa0118c46,80)]
raw=ROM.read_bytes()
assert len(raw)==6769704
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[]
for va,n in WINDOWS:
 b=raw[va-0x9ffff000:va-0x9ffff000+n]
 ins=list(cs.disasm(b,va))
 assert sum(i.size for i in ins)==n
 windows.append(dict(start=hex(va),size=n,offset=va-0x9ffff000,sha256=hashlib.sha256(b).hexdigest(),raw_hex=b.hex(),instructions=[dict(address=hex(i.address),bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in ins]))
source=ROOT/"evidence/rea-0041-20261017/evidence/upper-complete.evidence.json"
r=json.loads(source.read_text(encoding="utf-8"))["records"][245]
# Read only necessary success interfaces; excluded cleanup/error internals remain inherited.
ranges=[(0xa011630e,0xa0116336),(0xa01163c4,0xa0116440),(0xa011644a,0xa011648c),(0xa01164e2,0xa011651a),(0xa01165a6,0xa0116656),(0xa0116658,0xa01167ea),(0xa01168c2,0xa01168f8)]
assembly=[x for x in r["normalized_result"]["assembly"] if any(a<=int(x.split(":")[0],16)<=b for a,b in ranges)]
result=dict(claim="Q23",method="independent ROM read, Capstone "+capstone.__version__+" RV32+C; retained root assembly only",artifact=str(ROM),artifact_size=len(raw),inherited_sha256="972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9",mapping="offset=VA-0x9ffff000",reviewed_helper_bytes=sum(n for _,n in WINDOWS),windows=windows,root_source=str(source),root_evidence_id=r["evidence_id"],root_ranges=[[hex(a),hex(b)] for a,b in ranges],root_assembly=assembly,limitations=["No target, model, SIM, QEMU, replay, build, device or network execution", "Capstone relative branch operands are displacements; interpret with instruction address", "No new root bytes or inherited bodies counted; no new REA evidence ID"])
(OUT/"static-review.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("PASS: 7 windows, 604 bytes fully decoded; retained root success interfaces",len(assembly))
