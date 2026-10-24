"""G19/5 actual-op3 instantiation. Reads original bytes; never runs the target.

Large prior exports stay at their original ignored main-project paths. Only
op/argument-dependent anchors are rechecked; copy/zero/common body is inherited.
"""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
SHA = '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
ROM = MAIN/'roms/0041/ap01-1.0.2_0041.bin'
rom = ROM.read_bytes()
assert len(rom) == 6769704
prior_path = MAIN/'reverse/analysis/pogo-poll-submit-review-g22-0041-20261024/review-result.json'
prior = json.loads(prior_path.read_text(encoding='utf8'))
assert prior['status'] == 'PASS-static-only'
assert prior['original']['inherited_catalog_sha256'] == SHA
assert prior['original']['mapping'] == 'VA-0x9ffff000'
old_rows = {r['address']: r for r in prior['checks']}
d = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []

def ins(a, text):
    lo = a-BASE
    n = 4 if int.from_bytes(rom[lo:lo+2], 'little') & 3 == 3 else 2
    raw = rom[lo:lo+n]
    decoded = list(d.disasm(raw,a))
    assert len(decoded) == 1 and decoded[0].mnemonic+' '+decoded[0].op_str == text
    assert old_rows[hex(a)]['raw'] == raw.hex()
    checks.append(dict(address=hex(a),raw=raw.hex(),decode=text,
                       kind='rechecked-op-dependent-or-binding-anchor'))

for a,t in {
 0xa009e104:'c.mv s4, a4',0xa009e108:'c.mv s2, a5',
 0xa009e10c:'c.mv s5, a0',0xa009e10e:'c.mv s6, a3',
 0xa009e1a6:'srai a5, s4, 0x1f',0xa009e1aa:'sw a5, 0xc(s2)',
 0xa009e1b6:'sw s5, 4(s2)',0xa009e1ba:'sw s6, 0x18(s2)',
 0xa009e1be:'sw s4, 8(s2)',0xa009e1c4:'c.slli s1, 2',
 0xa009e1ca:'or s1, s1, s6',0xa009e1ce:'sw s1, 0x20(s2)',
 0xa009e1d2:'sw s4, 0x24(s2)',
}.items(): ins(a,t)

# Common entry BNE is operand-independent; verify only its selector/target.
a = 0xa009e110
w = int.from_bytes(rom[a-BASE:a-BASE+4],'little')
im = ((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
im = im-(1<<13) if im&(1<<12) else im
assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,a+im) == (0x63,1,14,15,0xa009e168)
checks.append(dict(address=hex(a),raw=w.to_bytes(4,'little').hex(),
                   kind='independent-branch-fields',target='0xa009e168'))

# Necessary old statements are selected references, not copied exports or reruns.
inherited = {
 'copy_source_binding':['0xa009e172','0xa009e174'],
 'copy16_call':['0xa009e18a'],
 'zero64_call':['0xa009e1a2'],
 'conditional_next_hop':['0xa009e1e8','0xa009e1f0'],
}
for addresses in inherited.values():
    for a in addresses: assert a in old_rows
assert old_rows['0xa009e1e8']['meaning'] == '0xa009e1f4'
assert old_rows['0xa009e1f0']['meaning'] == '0xa009dfcc'

result = dict(status='PASS-static-only',task='G25',claim='G19/5',baseline='bd457a6',
 identity=dict(path=str(ROM),length=len(rom),sha256_inherited=SHA,
               digest_recomputed=False,mapping='VA-0x9ffff000'),
 tools=dict(decoder='Capstone 5.0.7 RV32/RVC',branch='independent bit fields',
            shared_REA_changed=False),checks=checks,
 inherited=dict(path=str(prior_path),selected_references=inherited,rerun=False),
 material_delta=['Actual op=3 gives E+0x18=3 and E+0x20=(j<<2)|3',
                 'fd input is prior completion high word, not G19/2 caller fd identity',
                 'record source is local16+(old_completion_index<<4), not known-zero stack16'],
 limits=['No newly discovered op-specific body; common body and copy/zero retained',
         'Non-sentinel branch only; fallback/other op/diagnostics not expanded',
         'Source/destination validity, alignment, nonaliasing and continued storage lifetime remain conditions',
         'Conditional recursive service is a callsite boundary, not expanded execution',
         'No target, instruction, model, old script, SIM, QEMU or device execution'])
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} sparse original-byte anchors; common body inherited, new op-specific body 0')
