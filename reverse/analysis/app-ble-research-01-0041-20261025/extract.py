import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
UPPER = ROOT / 'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'

def select(addresses):
    bundle = json.loads(UPPER.read_text(encoding='utf-8'))
    metadata = []
    for ordinal, record in enumerate(bundle['records']):
        n = record.get('normalized_result', {})
        address = n.get('procedure', {}).get('address')
        if address not in addresses:
            continue
        selected = {k: record[k] for k in ['evidence_id', 'operation', 'parameters', 'analysis_profile', 'subject', 'limitations', 'relationship_coverage']}
        selected['normalized_result'] = {k: n[k] for k in ['procedure', 'pseudocode', 'assembly', 'callees', 'callers', 'incoming_references', 'outgoing_references', 'unresolved_calls']}
        (OUT / (address + '.selected.json')).write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding='utf-8')
        metadata.append({'bundle': str(UPPER.relative_to(ROOT)), 'ordinal': ordinal, 'address': address, 'evidence_id': record['evidence_id'], 'profile': record['analysis_profile']['digest']})
    (OUT / 'metadata-selection.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return metadata

def raw(address, length):
    with (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').open('rb') as stream:
        stream.seek(address-BASE)
        data = stream.read(length)
    decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
    decoder.skipdata = True
    lines = [f'{i.address:08x}: {i.bytes.hex():12s} {i.mnemonic:12s} {i.op_str}' for i in decoder.disasm(data,address)]
    record = {'address': hex(address), 'file_offset': address-BASE, 'length': length, 'bytes_hex': data.hex(), 'decoder': 'Capstone 5.0.7 RISCV32/RVC; .byte marks undecoded bytes; linear listing is not CFG proof', 'listing': lines}
    (OUT / (hex(address)+'.raw.json')).write_text(json.dumps(record, indent=2),encoding='utf-8')
    return '\n'.join(lines)

if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'select':
        print(json.dumps(select(set(sys.argv[2:])),indent=2))
    else:
        print(raw(int(sys.argv[1],0),int(sys.argv[2],0)))
