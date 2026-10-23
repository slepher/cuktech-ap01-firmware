"""Collect retained static evidence and bounded replay results; never execute firmware."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reverse/analysis/uart-response-0041-20261023.json'
ROUND3 = 'evidence/rea-0041-20261017/round3/'


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def fingerprint(path):
    return dict(path=path, sha256=hashlib.sha256((ROOT / path).read_bytes()).hexdigest())


def collect():
    image = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
    sha = hashlib.sha256(image).hexdigest()
    assert sha == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
    bundle_path = ROUND3 + 'evidence/whole-rom-round3-initial.evidence.json'
    handler = next(r for r in read(bundle_path)['records']
                   if r.get('parameters', {}).get('procedure') == '0xa00a8582')
    helper_path = 'evidence/rea-0041-20261017/evidence/whole-rom-uart-retry-20261023-001.json'
    helper = json.loads(read(helper_path)['content'][0]['text'])
    functions = []
    for record, path in ((handler, bundle_path), (helper, helper_path)):
        normalized = record['normalized_result']
        ranges = []
        for region in normalized['procedure']['body']['ranges']:
            start, end = int(region['start'], 16), int(region['end'], 16)
            raw = image[start - 0x9ffff000:end - 0x9ffff000 + 1]
            assert len(raw) == end - start + 1
            ranges.append(dict(**region, file_offset=start - 0x9ffff000,
                               sha256=hashlib.sha256(raw).hexdigest(), hex=raw.hex()))
        functions.append(dict(evidence_id=record['evidence_id'], source=fingerprint(path),
                              profile_digest=record['analysis_profile']['digest'],
                              raw_ranges=ranges, normalized_result=normalized))
    profile = read(ROUND3 + 'profile.json')
    for item in profile['inputs']:
        assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
    replay_path = ROUND3 + 'evidence/uart-response-replay-v2.json'
    replay = read(replay_path)
    assert replay['passed'] and len(replay['cases']) == 14 and replay['rom_sha256'] == sha
    assert replay['language'] == profile['language']
    assert 'AP01_UART_RESPONSE_REPLAY_PASS cases=14' in (ROOT / (ROUND3 + 'evidence/uart-response-v2.log')).read_text(encoding='utf-8')
    return dict(schema=1, rom_sha256=sha, complete=False,
                report='reverse/reports/ap01/uart-response-0041-20261023.md',
                authority='Retained shipped-artifact observations and bounded synthetic-memory replay; no hardware execution.',
                functions=functions, model=dict(profile=fingerprint(ROUND3 + 'profile.json'),
                                               verified_inputs=len(profile['inputs'])),
                replay=dict(source=fingerprint(replay_path), result=replay,
                            script=fingerprint('tooling/scripts/Ap01UartResponseReplay0041.java'),
                            log=fingerprint(ROUND3 + 'evidence/uart-response-v2.log')),
                open_boundaries=['Physical UART reachability and active-command prerequisites',
                                 'Actual zero-page mapping, fault handling, and device outcome',
                                 'Parser plus response callback end-to-end replay',
                                 'Full dispatcher ownership, callback reentrancy, and teardown'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = collect()
    if args.check:
        assert json.loads(OUT.read_text(encoding='utf-8')) == result, 'Evidence changed'
    else:
        with OUT.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    print('UART_RESPONSE_EVIDENCE_PASS functions=2 replay_cases=14 model_inputs=' + str(result['model']['verified_inputs']))
