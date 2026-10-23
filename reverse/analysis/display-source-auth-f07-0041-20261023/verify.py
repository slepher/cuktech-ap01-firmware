"""Validate reused F06 raw instructions against ROM, plus F07 source evidence."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVERSE = HERE.parents[1]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
F06 = REVERSE/'analysis/display-exit-review-f06-0041-20261023/independent-evidence.json'
anchors = {
    '0xa0084de8':'93054032', # display zero length
    '0xa0084e26':'13058005', # layer allocation length
    '0xa0084e2e':'23a8a42a', # layer pointer
    '0xa0084e72':'83a7442b', # init slot
    '0xa01b93c2':'3145',     # descriptor size
    '0xa01b9438':'90c7',     # filter offset
    '0xa01b9456':'23882401', # ROM array+0x10 byte, absent in candidate struct
    '0xa008152a':'0546',     # preprocess phase
    '0xa0081538':'6318f500', # exact return=1 gate
    '0xa008ad26':'5146',     # ROM event-list snapshot length 0x14
    '0xa008ad32':'83474901', # event-list+0x14 state
    '0xa008ad48':'230af900', # event-list+0x14 state write
    '0xa008ad72':'b3f68701', # bit16 gate
    '0xa008ad78':'8bb6f73c', # preprocess bit15
    '0xa008ad80':'b3f75701', # full ~0x8000 mask
    '0xa008ad92':'23a6f900', # event userdata
    '0xa008ad98':'8297',     # event* callback ABI
    '0xa0081570':'93059002', # ROM DELETE event=0x29
    '0xa00815e8':'83a7842b', # delete slot
    '0xa00815f6':'03a5042b', # layer reload after callback
}

rom = ROM.read_bytes()
previous = json.loads(F06.read_text(encoding='utf-8'))
count = 0
instructions = {}
for window in previous['windows']:
    for insn in window['instructions']:
        pc = int(insn['pc'],16)
        raw = bytes.fromhex(insn['raw'])
        assert rom[pc-0x9ffff000:pc-0x9ffff000+len(raw)] == raw, insn['pc']
        instructions[insn['pc']] = insn
        count += 1
for pc, raw in anchors.items():
    assert instructions[pc]['raw'] == raw, pc
source = json.loads((HERE/'source-evidence.json').read_text(encoding='utf-8'))
assert len(source['sources']) == 13
assert all(s['equals_local_archive_member'] for s in source['sources'])
assert source['git']['apps_head']['stdout'].strip() == '8ff533beb37eeef1f288c467acd7c50b542464eb'
assert source['candidate_event_enum']['LV_EVENT_DELETE'] == 38
assert source['candidate_event_enum']['LV_EVENT_REFR_REQUEST'] == 53
result = {
 'mode':'static read only; no target execution or build',
 'rom_path':str(ROM), 'mapping':'VA-0x9ffff000',
 'reused_F06_path':str(F06), 'reused_instruction_raw_matches':count,
 'selected_source_auth_anchors':[instructions[pc] for pc in anchors],
 'candidate_package_selected_members_equal':13,
 'boundary':'Local package equality is not upstream provenance or ROM version authentication; no new hash manifest.'
}
(HERE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS: {count} reused F06 raw instruction matches; {len(anchors)} source-comparison anchors; 13 local package members equal.')
