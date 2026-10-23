"""D19 read-only static checks; writes only this task's evidence directory."""
import json
from pathlib import Path
import capstone

ROOT = Path("D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware")
OUT = Path(__file__).resolve().parent
rom = (ROOT / "roms/0041/ap01-1.0.2_0041.bin").read_bytes()
base = 0x9ffff000
cs = capstone.Cs(capstone.CS_ARCH_RISCV,
                 capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
# Small dependency windows, never a new whole-function decompilation/export.
ranges = [
    ("timer-descriptor-writes", 0xa00f441a, 0xa00f447c),
    ("path-math", 0xa00f4382, 0xa00f43b2),
    ("exec-byte-argument", 0xa00f43c4, 0xa00f43cc),
    ("exec-style-binding", 0xa018fb44, 0xa018fb52),
    ("init-clear-and-defaults", 0xa008df46, 0xa008df7a),
    ("clear-wrapper", 0xa0080d96, 0xa0080d9e),
    ("start-copy", 0xa008bf96, 0xa008bfa6),
    ("start-copy-96", 0xa008bfe6, 0xa008bffa),
    ("start-immediate-dispatch", 0xa008c02a, 0xa008c060),
    ("tick-path-exec", 0xa008c184, 0xa008c1b8),
    ("tick-infinite-sentinel", 0xa008c0a2, 0xa008c0a4),
    ("tick-completion", 0xa008c1cc, 0xa008c20a),
    ("tick-repeat", 0xa008c232, 0xa008c24e),
    ("confirm-stop-identity", 0xa00feb74, 0xa00febc4),
    ("query-identity", 0xa00891a6, 0xa00891b8),
    ("delete-identity", 0xa01b2ee0, 0xa01b2f1c),
    ("delete-node", 0xa008ac10, 0xa008ac2e),
    ("node-free-wrapper", 0xa008ab8a, 0xa008aba6),
    ("map-arithmetic", 0xa008a740, 0xa008a776),
]
windows = []
for name, start, end in ranges:
    data = rom[start-base:end-base]
    instructions, at = [], start
    while at < end:
        raw = rom[at-base:end-base]
        ins = next(cs.disasm(raw, at, count=1), None)
        if ins is None:
            size = 2 if int.from_bytes(raw[:2], "little") & 3 != 3 else 4
            assert size <= len(raw), (name, hex(at), "window splits instruction")
            instructions.append({"address": hex(at), "bytes": raw[:size].hex(),
                                 "instruction": "UNKNOWN: retained, not skipped"})
        else:
            size = ins.size
            instructions.append({"address": hex(at), "bytes": ins.bytes.hex(),
                                 "instruction": ins.mnemonic + " " + ins.op_str})
        at += size
    assert at == end
    windows.append({"name": name, "start": hex(start), "end_exclusive": hex(end),
                    "hex": data.hex(), "instructions": instructions})

rehost = ROOT / "reverse/rehost"
reuse_files = [rehost / "system-complete-0041.json", rehost / "guide-complete-0041.json",
               *sorted(rehost.glob("settings-0041*.json")),
               *sorted(rehost.glob("page-logic*.json"))]
terms = ["a00f43d4", "a00f4378", "a00f43bc", "a008bf6e", "a008df3c", "0x8c", "0x84"]
reuse = []
for path in reuse_files:
    text = path.read_text(encoding="utf-8").lower()
    reuse.append({"path": str(path), "term_counts": {t: text.count(t) for t in terms}})
old = ROOT / "evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-125.json"
record = json.loads(old.read_text(encoding="utf-8"))["structuredContent"]
assert record["normalized_result"]["procedure"]["address"] == "0xa00f43d4"
settings = json.loads((rehost / "settings-0041-round2b.json").read_text(encoding="utf-8"))["records"][10]
assert "0xa00febaa: jal ra, 0xa0089184" in settings["normalized_result"]["assembly"]
assert "0xa00febb6: jal ra, 0xa01b2eb4" in settings["normalized_result"]["assembly"]

def instruction(address):
    return next(i for w in windows for i in w["instructions"] if i["address"] == hex(address))

# Anchors for slot, width, repeat sentinel and object/callback identity.
expected = {
    0xa00f443a: "sw a5, -0x40(s0)",
    0xa00f4452: "sw a5, -0x6c(s0)",
    0xa00f4474: "sw s2, -0x2c(s0)",
    0xa00f43c4: "andi a1, a1, 0xff",
    0xa008c232: "beq a4, s3, 0xc",
    0xa00feb9c: "lw s2, 0x10(s3)",
}
for address, expected_text in expected.items():
    assert instruction(address)["instruction"] == expected_text
result = {
    "scope": "static D19; no target execution, shared REA session or model change",
    "capstone": capstone.__version__,
    "reuse": reuse,
    "inherited_records": [
        {"path": str(old), "selector": "structuredContent", "evidence_id": record["evidence_id"],
         "purpose": "existing complete timer descriptor construction, do not re-export"},
        {"path": str(rehost / "settings-0041-round2b.json"), "selector": "records[10]",
         "evidence_id": settings["evidence_id"], "purpose": "existing normal state40 exit stop pair"}],
    "anchor_checks": "passed", "raw_windows": len(windows),
    "unknown_instructions": [i for w in windows for i in w["instructions"] if i["instruction"].startswith("UNKNOWN")],
    "limits": ["userdata semantic typedef not authenticated; only zero slot +1c is established",
               "query traversal vendor word retained; equality pair is direct standard instructions",
               "whole object/page destruction and allocation failure not expanded"]}
(OUT / "instruction-windows.json").write_text(json.dumps(windows, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
(OUT / "review-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps({"anchor_checks": result["anchor_checks"], "windows": len(windows),
                  "unknown_instructions": len(result["unknown_instructions"])}, ensure_ascii=False))
