"""P-03: bounded static ROM/evidence cross-check; executes no firmware or model.
Run with Python 3 from any directory. Outputs only beside this script.
"""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
IDENTITY = '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)

def read(rel):
    return json.loads((ROOT/rel).read_text(encoding='utf-8'))

def save(name, value):
    (HERE/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

sources = {
 'total': 'reverse/analysis/theme-total-state-0041-20261023/instruction-windows.json',
 'item': 'reverse/analysis/ctk-view-dataflow-e03-0041-20261023/instruction-windows.json',
 'complete': 'reverse/analysis/window-history-0041-20261023/instruction-windows.json',
 'dispatch': 'reverse/analysis/mode-control-0041-20261023/instruction-windows.json',
 'converter': 'reverse/analysis/uiiface-item-ownership-e01-0041-20261023/instruction-windows.json',
}
# Only windows required to join already recovered interface stages.
spans = [
 ('total', 'total_guards', 0xa00ad100, 0xa00ad176),
 ('total', 'total_current_values', 0xa00ad176, 0xa00ad1a0),
 ('total', 'total_power_guard', 0xa00ad230, 0xa00ad240),
 ('total', 'total_mode_guard', 0xa00ad270, 0xa00ad280),
 ('total', 'total_temp_guard', 0xa00ad2c8, 0xa00ad2d8),
 ('total', 'total_end', 0xa00ad3f4, 0xa00ad402),
 ('item', 'item_guards', 0xa00adb54, 0xa00adbbc),
 ('item', 'item_prepare', 0xa00aef4a, 0xa00aef6a),
 ('item', 'item_values_guard', 0xa00af0cc, 0xa00af0e4),
 ('item', 'item_soc_guard', 0xa00af10c, 0xa00af11e),
 ('item', 'item_end', 0xa00af250, 0xa00af262),
 ('item', 'port2_prepare', 0xa00af12e, 0xa00af18e),
 ('item', 'item_dispatch', 0xa00a38c0, 0xa00a3902),
 ('complete', 'complete', 0xa00ab628, 0xa00ab6b0),
 ('dispatch', 'total_dispatch', 0xa00a5384, 0xa00a53be),
 ('converter', 'converter_soc', 0xa00f4938, 0xa00f4942),
 ('converter', 'converter_time', 0xa00f4970, 0xa00f497a),
 ('converter', 'converter_rows', 0xa00f49e0, 0xa00f49f0),
]
windows = []
index = {}
for kind, name, start, end in spans:
    old = read(sources[kind])
    if 'rom_sha256' in old:
        assert old['rom_sha256'] == IDENTITY
    # Older E01/E03 windows omit identity; the byte comparison below is authoritative.
    rows = [i for w in old['windows'] for i in w['instructions'] if start <= int(i['address'],16) < end]
    assert rows and int(rows[0]['address'],16) == start
    pc = start
    retained = []
    for row in rows:
        assert int(row['address'],16) == pc
        raw = bytes.fromhex(row['hex'])
        assert rom[pc-BASE:pc-BASE+len(raw)] == raw
        size = 4 if raw[0] & 3 == 3 else 2
        assert len(raw) == size
        ins = next(cs.disasm(raw,pc),None)
        vendor = size == 4 and int.from_bytes(raw,'little') & 127 == 11
        assert vendor or (ins and ins.size == size)
        rec = dict(address=hex(pc), file_offset=pc-BASE, hex=raw.hex(), retained_assembly=row['assembly'])
        rec['standard_decode'] = ins.mnemonic+' '+ins.op_str if ins else None
        rec['vendor_semantics'] = 'inherited E02 private SLEIGH; not independently ISA-certified' if vendor else None
        retained.append(rec)
        index[pc] = rec
        pc += size
    assert pc == end
    windows.append(dict(name=name, source=sources[kind], start=hex(start), end_exclusive=hex(end), instructions=retained))

# Fixed byte and operand anchors are review aids, not an executable behavior model.
expected = {
 0xa00ad11c:('83d7c900','lhu a5, 0xc(s3)'),
 0xa00ad128:('2328f904','sw a5, 0x50(s2)'),
 0xa00ad15e:('8347c904','lbu a5, 0x4c(s2)'),
 0xa00ad192:('83db4900','lhu s7, 4(s3)'),
 0xa00ad19c:('838a7900','lb s5, 7(s3)'),
 0xa00ad238:('83270905','lw a5, 0x50(s2)'),
 0xa00ad3fc:('23280904','sw zero, 0x50(s2)'),
 0xa00adb5c:('83270900','lw a5, 0(s2)'),
 0xa00adb60:('232afb04','sw a5, 0x54(s6)'),
 0xa00adba4:('8347cb04','lbu a5, 0x4c(s6)'),
 0xa00af0da:('03274b05','lw a4, 0x54(s6)'),
 0xa00af116:('03274b05','lw a4, 0x54(s6)'),
 0xa00af25a:('232a0b04','sw zero, 0x54(s6)'),
 0xa00ab632:('444d','c.lw s1, 0x1c(a0)'),
 0xa00ab638:('2386f404','sb a5, 0x4c(s1)'),
 0xa00a5394:('8325c92c','lw a1, 0x2cc(s2)'),
 0xa00a539a:('23960500','sh zero, 0xc(a1)'),
 0xa00a53b0:('c840','c.lw a0, 4(s1)'),
 0xa00a53b2:('8297','c.jalr a5'),
 0xa00a38f2:('c840','c.lw a0, 4(s1)'),
 0xa00a38f4:('d685','c.mv a1, s5'),
 0xa00a38f6:('8297','c.jalr a5'),
 0xa00f4938:('03270900','lw a4, 0(s2)'),
 0xa00f4970:('03270900','lw a4, 0(s2)'),
 0xa00f49e0:('03270900','lw a4, 0(s2)'),
}
for pc,(raw,asm) in expected.items():
    assert index[pc]['hex'] == raw and index[pc]['standard_decode'] == asm, hex(pc)

def branch_target(pc):
    w=int.from_bytes(bytes.fromhex(index[pc]['hex']),'little')
    if w & 3 != 3:
        ins=next(cs.disasm(bytes.fromhex(index[pc]['hex']),pc))
        assert ins.mnemonic=='c.beqz'
        return pc+int(ins.op_str.split(',')[-1].strip(),0)
    assert w & 127 == 99
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    if imm & (1<<12): imm-=1<<13
    return pc+imm

assert branch_target(0xa00aef66)==0xa00af12e
assert branch_target(0xa00af180)==0xa00af250

def jal_target(pc):
    w = int.from_bytes(bytes.fromhex(index[pc]['hex']),'little')
    assert w & 127 == 111
    imm = ((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    if imm & (1<<20): imm -= 1<<21
    return pc+imm
calls = {0xa00ad116:0xa00891b8,0xa00adb54:0xa00891b8,0xa00aef62:0xa00f4740,
         0xa00ab646:0xa00dcee4,0xa00ab672:0xa008b51a,0xa00ab69a:0xa008b51a,0xa00ab6aa:0xa008bd70}
for pc,target in calls.items(): assert jal_target(pc)==target
complete_calls = {hex(int(i['address'],16)):hex(jal_target(int(i['address'],16)))
 for w in windows if w['name']=='complete' for i in w['instructions']
 if len(bytes.fromhex(i['hex']))==4 and int.from_bytes(bytes.fromhex(i['hex']),'little')&127==111}
assert set(complete_calls.values()) == {'0xa00dcee4','0xa008b51a','0xa008bd70'}
profiles = []
for rel, addresses in [
 ('reverse/analysis/theme-total-state-0041-20261023/retained-function.json',{'0xa00ad07e'}),
 ('reverse/analysis/window-history-0041-20261023/retained-functions.json',{'0xa00ab628'}),
 ('reverse/analysis/uiiface-item-ownership-e01-0041-20261023/retained-consumer.json',{'0xa00f4740'}),
]:
    j=read(rel)
    for f in j.get('functions',[j]):
        addr=f['normalized_result']['procedure']['address']
        if addr in addresses:
            p=f['profile']; assert p['parameters']['language_id']=='RISCV:LE:32:ap01thead2'
            profiles.append(dict(address=addr,source=rel,evidence_id=f['evidence_id'],profile=p['digest'],language=p['parameters']['language_id'],provider=p['provider']))
# Focused callback record, without changing shared REA state.
rel='evidence/rea-0041-20261017/evidence/whole-rom-retained-private-20261023-001.json'
j=read(rel);e=j.get('structuredContent') or json.loads(j['content'][0]['text'])
assert e['normalized_result']['procedure']['address']=='0xa00adabc'
p=e['analysis_profile'];assert p['parameters']['language_id']=='RISCV:LE:32:ap01thead2'
profiles.append(dict(address='0xa00adabc',source=rel,evidence_id=e['evidence_id'],profile=p['digest'],language=p['parameters']['language_id'],provider=p['provider']))
save('evidence.json',dict(identity=IDENTITY,mapping='file_offset=VA-0x9ffff000',profiles=profiles,windows=windows,
 limitations=['Static retained evidence and selected original bytes only; no observed execution','No whole-ROM reader/writer scan, library-internal analysis, or global absence proof','Vendor dispatch mask-clear semantics inherited E02; no modified model']))
save('checks.json',dict(status='PASS',selected_windows=len(windows),selected_bytes=sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),
 instructions=sum(len(w['instructions']) for w in windows),fixed_byte_operand_anchors=len(expected),direct_call_targets=len(calls),converter_failure_branches={'0xa00aef66':'0xa00af12e','0xa00af180':'0xa00af250'},
 complete_direct_calls=complete_calls,profile_records=profiles,
 acceptance='Author static consistency check; independent acceptance pending'))
print(json.dumps(dict(status='PASS',windows=len(windows),anchors=len(expected),calls=len(calls))))
