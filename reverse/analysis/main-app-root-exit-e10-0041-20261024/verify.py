"""E10 bounded static recheck; never executes ROM or retained scripts."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
MAIN = Path("D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware")
OUT = Path(__file__).resolve().parent
rom = (MAIN / "roms/0041/ap01-1.0.2_0041.bin").read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
# All these windows are rechecks of retained meanings, not new business recovery.
windows = [
    ("parent_call_and_main_window_alias", 0xa005cd68, 0xa005cd82),
    ("active_screen_wrapper", 0xa0081856, 0xa0081862),
    ("nullable_display_branch", 0xa0080ec4, 0xa0080ed2),
    ("active_screen_return_join", 0xa0080ef4, 0xa0080f06),
    ("old_guide_wake_main_branch", 0xa00a7642, 0xa00a764c),
    ("old_guide_wake_other_window_delete", 0xa00a7660, 0xa00a766e),
    ("old_guide_wake_delete_call", 0xa00a7694, 0xa00a769a),
    ("old_main_window_selection_tail", 0xa00b2dc4, 0xa00b2dde),
    ("old_slider_state_writes", 0xa019d4ae, 0xa019d4be),
    ("inherited_display_screen_delete_loop", 0xa008163a, 0xa0081646),
]
anchors = {
    0xa005cd68: "ef40722e", 0xa005cd78: "032584c3", 0xa005cd80: "2a8a",
    0xa0081856: "b797fc62", 0xa008185a: "03a50759", 0xa0080ec6: "0ded",
    0xa0080ecc: "83a40759", 0xa0080f00: "83a4842c", 0xa0080ef8: "2685",
    0xa00a7642: "a84f", 0xa00a7660: "a945", 0xa00a7668: "0325c4fe",
    0xa00b2dc4: "8145", 0xa00b2dce: "8d45", 0xa00b2dd6: "9945",
    0xa019d4b4: "23aa2403", 0xa019d4b8: "9cdc", 0xa019d4ba: "23860404",
    0xa008163a: "83a7c42b", 0xa008163e: "8843",
}
checks=[]
for pc, expect in anchors.items():
    got=rom[pc-0x9ffff000:pc-0x9ffff000+len(bytes.fromhex(expect))].hex()
    assert got==expect,(hex(pc),got,expect)
    checks.append({"pc":hex(pc),"kind":"raw-anchor","raw":got})
def jal_target(pc):
    w=int.from_bytes(rom[pc-0x9ffff000:pc-0x9ffff000+4],"little")
    assert w&0x7f==0x6f
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    if imm&(1<<20):imm-=1<<21
    return (pc+imm)&0xffffffff
for pc,target in [(0xa005cd68,0xa008184e),(0xa005cd7c,0xa00b2f6c),
                  (0xa008185e,0xa0080eba),(0xa00a7648,0xa00b2d6a),
                  (0xa00a7694,0xa00ded6c),(0xa00b2dd8,0xa019d422),
                  (0xa0081640,0xa00ded6c)]:
    assert jal_target(pc)==target
    checks.append({"pc":hex(pc),"kind":"jal-target","target":hex(target)})
selected=[]
for name,start,end in windows:
    ins=list(md.disasm(rom[start-0x9ffff000:end-0x9ffff000],start))
    assert sum(i.size for i in ins)==end-start
    selected.append({"name":name,"start":hex(start),"end_exclusive":hex(end),
      "classification":"old-conclusion-recheck", "instructions":[
       {"pc":hex(i.address),"raw":i.bytes.hex(),"asm":i.mnemonic+" "+i.op_str} for i in ins]})
# Retained relationships are inherited; do not rerun a ROM incoming scan.
bundle=json.loads((MAIN/"evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json").read_text())
refs=[]
for r in bundle["records"]:
    s=r["normalized_result"]
    if not isinstance(s,dict) or not isinstance(s.get("procedure"),dict):continue
    a=s["procedure"].get("address")
    if a in ["0xa00b2d6a","0xa019d422"]:
        refs.append({"address":a,"evidence_id":r["evidence_id"],"source":"whole-rom-private-20261023.evidence.json", "role":"inherited-dossier-no-export"})
assert len(refs)==2
result={"task":"E10","scope":"bounded static reuse and callsite recheck", "mapping":"offset=VA-0x9ffff000", "new_exit_closures":0,"windows":selected,"checks":checks,"inherited_references":refs,
 "limitations":["Capstone branch operands are relative displacements; JAL targets above are independently normalized.","No runtime execution, whole-ROM incoming scan, model changes, or full function export.","Default display and its active screen are read at creation; no claim they remain unchanged throughout execution.","A conditional display deletion path does not identify a normal business action that causes loop return."]}
OUT.joinpath("bounded-recheck.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"PASS {len(checks)} checks; {len(windows)} narrow windows; {sum(len(w['instructions']) for w in selected)} instructions; new exit closures 0")
