"""Q06 bounded original-word verification; offline, no target execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = 0x9FFFF000
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
SOURCE = ROOT / 'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
windows = [
    (248, 0xA006580C, 0xA0065842, 'callback_slots'),
    (273, 0xA006CDB8, 0xA006CDCC, 'entry_gate'),
    (273, 0xA006D02A, 0xA006D074, 'association_handoff'),
    (273, 0xA006D0B6, 0xA006D0D8, 'association_return_stage'),
    (273, 0xA006D124, 0xA006D16C, 'dhcp_handle'),
    (273, 0xA006D1A0, 0xA006D1B8, 'request_signed_return'),
    (273, 0xA006D1EC, 0xA006D260, 'ipv4_and_cleanup'),
    (252, 0xA0067210, 0xA006723A, 'same_handle_down'),
    (252, 0xA0067260, 0xA006726A, 'down_event'),
    (None, 0xA005FAC4, 0xA005FAEC, 'handle_cleanup_helper'),
]
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []
records = json.loads(SOURCE.read_text(encoding='utf-8'))['records']
assert ROM.stat().st_size == 6769704
for idx in (248, 273, 252, 89):
    assert records[idx]['analysis_profile']['digest'] == '4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
results = []
with ROM.open('rb') as image:
    for idx, start, end, label in windows:
        image.seek(start - BASE)
        raw = image.read(end - start)
        instructions = list(md.disasm(raw, start))
        assert sum(i.size for i in instructions) == len(raw), label
        entry = dict(label=label, start=hex(start), end_exclusive=hex(end),
                     bytes=raw.hex(), instructions=[dict(address=hex(i.address),
                     bytes=i.bytes.hex(), mnemonic=i.mnemonic, operands=i.op_str)
                     for i in instructions])
        if idx is not None:
            rec = records[idx]
            entry.update(record=idx, evidence_id=rec['evidence_id'],
                         profile=rec['analysis_profile']['digest'],
                         retained_assembly=[s for s in rec['normalized_result']['assembly']
                         if start <= int(s.split(':')[0], 16) < end])
        else:
            entry['provenance'] = 'new bounded original-ROM read; no REA ID/profile assigned'
        results.append(entry)

raw_by_address = {int(i['address'], 16): bytes.fromhex(i['bytes'])
                  for w in results for i in w['instructions']}

def word(address):
    return int.from_bytes(raw_by_address[address], 'little')

def imm_i(w):
    v = w >> 20
    return v - 4096 if v & 2048 else v

def imm_s(w):
    v = ((w >> 25) << 5) | ((w >> 7) & 31)
    return v - 4096 if v & 2048 else v

def jal_target(address):
    w = word(address)
    v = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    return address + (v - (1 << 21) if v & (1 << 20) else v)

def check(label, condition):
    assert condition, label
    checks.append(label)

check('callback construct a006d000-25c=a006cda4',
      (word(0xA0065824) & 0xFFFFF000) + imm_i(word(0xA0065828)) == 0xA006CDA4)
check('callback slot base N+180', imm_i(word(0xA0065810)) == 0x180)
check('entry LBU N+1e4', (word(0xA006CDC6) >> 12) & 7 == 4 and imm_i(word(0xA006CDC6)) == 0x1E4)
check('association call', jal_target(0xA006D064) == 0xA0075D6A)
check('temporary fd close call', jal_target(0xA006D06C) == 0xA0026888)
check('DHCP handle SW global offset -61c', imm_s(word(0xA006D152)) == -0x61C)
check('DHCP request call', jal_target(0xA006D1A4) == 0xA00992D2)
w = word(0xA006D1A8)
check('request result retained separately in s5',
      w & 0xF003 == 0x8002 and (w >> 7) & 31 == 21 and (w >> 2) & 31 == 10)
check('helper on normal success', jal_target(0xA006D24A) == 0xA005FAC4)
check('down reload LW same offset -61c', imm_i(word(0xA0067230)) == -0x61C)
check('down interrupt API call', jal_target(0xA0067236) == 0xA0098A98)
check('helper address construct same global', (word(0xA005FACE) & 0xFFFFF000) + imm_i(word(0xA005FAD2)) == 0x62FC99E4)
check('helper delegates handle to API a0098af0', jal_target(0xA005FADA) == 0xA0098AF0)
w = word(0xA005FADE)
check('helper clears entire 32bit global slot after API return',
      w & 0x7F == 0x23 and (w >> 12) & 7 == 2 and (w >> 20) & 31 == 0 and imm_s(w) == 0)

result = dict(claim='Q-06', status='author checks; pending non-author review',
              source=str(ROM), source_identity='inherited CATALOG SHA256; not rehashed',
              mapping='offset = VA - 0x9ffff000', retained_source=str(SOURCE),
              capstone='5.0.7 RV32/RVC', checks=checks, windows=results,
              limits=['No runtime observation', 'No secret values read',
                      'Public DHCP/network API internals not followed',
                      'Capstone aliases/PC-relative formatting are not retained REA syntax'])
(OUT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'{len(checks)} checks; {len(windows)} bounded windows; '+str(sum((b-a) for _,a,b,_ in windows))+' bytes; PASS')
