"""A80 retained-record selector only; no ROM, old script, input or instruction execution."""
import json
from pathlib import Path

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
source=MAIN/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
r=json.loads(source.read_text(encoding='utf-8'))['records'][76]
assert r['evidence_id']=='ev_32725e49dc86c4d072d48e396f5c14986a521284bea8c8ff59cd533fc995a848'
assert r['analysis_profile']['digest']=='4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
assert r['parameters']['procedure']=='0xa000589c'
assembly={int(s.split(':',1)[0],16):s for s in r['normalized_result']['assembly']}
# Only short dispatcher, terminal byte and large-length alignment split, no bulk body export.
selected=[pc for pc in assembly if 0xa000589c<=pc<0xa00058c8 or 0xa000590e<=pc<0xa0005918 or 0xa0005924<=pc<0xa0005956]
checks={
 'n_greater7': assembly[0xa00058a4].endswith('bltu a5, a2, 0xa000592c'),
 'n4':assembly[0xa00058aa].endswith('beq a2, a4, 0xa000591c'),
 'n_greater4':assembly[0xa00058ae].endswith('bltu a4, a2, 0xa00058c8'),
 'n2':assembly[0xa00058b4].endswith('beq a2, a5, 0xa0005920'),
 'dst':assembly[0xa00058ba].endswith('c.mv a5, a0'),
 'n3':assembly[0xa00058bc].endswith('beq a2, a4, 0xa00058fe'),
 'n1':assembly[0xa00058c2].endswith('beq a2, a4, 0xa000590e'),
 'byte_read':assembly[0xa000590e].endswith('lbu a4, 0x0, a1'),
 'byte_write':assembly[0xa0005912].endswith('sb a4, 0x0, a5'),
 'return':assembly[0xa0005916].endswith('ret'),
 'destination_align_loop':assembly[0xa0005934].endswith('c.bnez a5, 0xa0005924'),
 'source_mod2':assembly[0xa0005940].endswith('beq a4, a3, 0xa0005af2'),
 'source_mod3':assembly[0xa0005946].endswith('beq a4, a3, 0xa0005be2'),
 'source_mod0':assembly[0xa000594c].endswith('bne a4, a3, 0xa000599c'),
 'source_mod1_align_down':assembly[0xa0005950].endswith('c.andi a1, -0x4'),
 'source_mod1_word_read':assembly[0xa0005952].endswith('th.lwia a3, a1, 0x4, 0x0')
}
assert all(checks.values()),checks
out={'task':'A80','old_record':'upper-complete.evidence.json#/records/76','EID':r['evidence_id'],'profile':r['analysis_profile']['digest'],
 'old_checks':len(checks)+3,'ROM_bytes':0,'old_rows':[assembly[pc] for pc in selected],
 'raw_gap_n1':['0xa00058ae','0xa00058c6',24],
 'later_seeds':['n2..7 dispatcher/byte arms','n8..255 destination alignment then source%4:0->599c,1->5950,2->5af2,3->5be2'],
 'footprint_limit':'source residue1 old assembly aligns down before word read; extra readable prefix/suffix cannot be inferred from n-byte valid domain; vendor/raw not revalidated here'}
Path(__file__).with_name('retained-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)+3} retained-record checks; {len(selected)} selected old rows; ROM0B')
