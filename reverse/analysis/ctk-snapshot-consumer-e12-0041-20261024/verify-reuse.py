"""Bounded source reuse check; no firmware execution or new function analysis."""
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[3]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
refs = json.loads((ROOT / 'reverse/analysis/ctk-view-dataflow-e03-0041-20261023/references.json').read_text(encoding='utf-8'))
assert refs['evidence_id'] == 'ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5'
assert len(refs['converter_calls']) == 3
assert refs['caller_incoming_references'][0]['source_address'] == '0xa005d142'
old = MAIN / 'reverse/rehost'
complete = json.loads((old / 'charge-complete-0041.json').read_text(encoding='utf-8'))
identities = []
for index, address in ((8, '0xa00f4610'), (9, '0xa00f44e8'), (19, '0xa00f5288')):
    record = complete['records'][index]
    assert record['parameters']['procedure'] == address
    identities.append({'record': index, 'address': address, 'evidence_id': record['evidence_id']})
source_hits = {}
for name in ('charge-0041-round4.json', 'details-0041-round4.json', 'main-knob-0041-round2.json', 'detail-knob-0041-round2.json'):
    data = json.loads((old / name).read_text(encoding='utf-8'))
    text = str(data).lower()
    source_hits[name] = {address: text.count(address) for address in ('a00f4740', 'a00adabc', 'a00ef2da')}
with ZipFile(old / 'ap01-ui-0041-complete-source.zip') as archive:
    charge = archive.read('tools/ap01/ap01-ui-charge.h').decode()
    assert 'bank->battery' in charge and 'bank->remaining_minutes' in charge and 'bank->ports[i]' in charge
    assert archive.getinfo('tools/ap01/ap01-ui-details.h').file_size > 0
report = (ROOT / 'reverse/reports/ap01/ctk-view-review-e04-0041-20261023.md').read_text(encoding='utf-8')
for anchor in ('互斥', 's0-0x94', '0x52 B', 'a00f4610', 'a00ef2da', '没有向持久对象store row/view'):
    assert anchor in report, anchor
result = {'status': 'PASS', 'kind': 'existing-coverage/source-integrity check, not a new technical acceptance',
          'complete_records': identities, 'old_source_exact_address_text_hits': source_hits,
          'converter_calls': 3, 'new_function_exports': 0, 'new_business_recovery': 0,
          'limits': ['exact text absence is not absence of semantic coverage', 'ZIP is service reconstruction', 'no global alias or +34/+38 proof']}
Path(__file__).with_name('reuse-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('PASS: existing E03/E04 closure and selected legacy source identities; no new function analysis')
