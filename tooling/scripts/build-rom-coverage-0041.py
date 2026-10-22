"""Index whole-ROM private REA observations without modifying or executing ROM.

Source paths are attribution evidence, never proof of unchanged open-source code.
Queue phases run through the isolated private REA client described in the report.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SHA = '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
BASE = 0x9ffff000
SOURCE = re.compile(r'(^|/)[A-Za-z0-9_.-]+\.(?:c|cpp|cc|cxx)$')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_limits(evidence):
    # Provider-wide policy prose is retained in the source Evidence, not repeated
    # for every graph node. Keep the warnings that can cut a particular body.
    return [s for s in evidence.get('limitations', []) if any(
        word in s.lower() for word in ('terminal call', 'fallthrough', 'truncat', 'bad instruction'))]


def source_family(path):
    if path.startswith(('PogoPinMng/', 'lv_power_ui/', 'SystemSettings/', 'factory_ui/')) or path == 'lvgl_ui_main.c':
        return 'vendor-application'
    if 'miio_sdk/' in path or 'wifi6_private/' in path:
        return 'vendor-sdk-review'
    if '/apps/graphics/lvgl/lvgl/' in path:
        return 'open-source-path-candidate:lvgl'
    if path.startswith('libuv/'):
        return 'open-source-path-candidate:libuv'
    if path.startswith(('subsys/bluetooth/', 'subsys/net/', 'port/kernel/')):
        return 'open-source-path-candidate:zephyr-port'
    # Short NuttX paths identify an origin candidate, not the extent of patches.
    if path.split('/')[0] in {
        'vfs', 'inode', 'socket', 'sched', 'semaphore', 'pthread', 'signal',
        'task', 'group', 'tls', 'environ', 'stdio', 'stream', 'mqueue', 'wqueue',
        'netdev', 'netlink', 'tcp', 'udp', 'icmp', 'local', 'arp', 'devif',
        'procfs', 'romfs', 'tmpfs', 'littlefs', 'tlsf', 'bch', 'pipes', 'mtd',
        'mount', 'wdog', 'netdb', 'iob', 'mmap', 'spawn', 'unistd', 'termios',
        'irq', 'common', 'syslog', 'map', 'ipfrag', 'driver', 'serial', 'loop',
        'efuse', 'timers', 'timer', 'analog', 'ioexpander', 'circbuf', 'init',
    } or path.startswith(('nsh_', 'readline_')) or path == 'boardctl.c':
        return 'open-source-path-candidate:nuttx'
    return 'unresolved-source'


def load_records(directory, inputs):
    for path in sorted(directory.glob('whole-rom-*.json')):
        if not re.search(r'-\d{3,}\.json$', path.name):
            continue
        value = read(path)
        if not isinstance(value, dict) or 'content' not in value:
            continue
        evidence = value.get('structuredContent')
        if not evidence:
            texts = [c['text'] for c in value['content'] if c.get('type') == 'text']
            evidence = json.loads(texts[0]) if texts else {}
        if 'operation' not in evidence:
            continue
        assert evidence['subject']['digest']['sha256'] == SHA, path
        inputs[path.relative_to(ROOT).as_posix()] = digest(path)
        if 'source_bundle' in value:
            bundle = ROOT/value['source_bundle']['path']
            key = bundle.relative_to(ROOT).as_posix()
            if key not in inputs:
                inputs[key] = digest(bundle)
            assert inputs[key] == value['source_bundle']['sha256']
        yield evidence


def build(directory):
    rom = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
    image = rom.read_bytes()
    assert hashlib.sha256(image).hexdigest() == SHA, 'Wrong ROM'
    inputs = {}
    records = load_records(directory, inputs)
    profiles = set()
    xref_records = []
    inputs[rom.relative_to(ROOT).as_posix()] = SHA
    inputs[Path(__file__).relative_to(ROOT).as_posix()] = digest(Path(__file__))
    paths = {}
    for match in re.finditer(rb'[\x20-\x7e]{3,}\x00', image):
        text = match.group()[:-1].decode('ascii')
        if SOURCE.search(text):
            address = hex(BASE + match.start())
            paths[address] = dict(address=address, file_offset=match.start(), text=text,
                                  family=source_family(text), references=[], evidence_ids=[])
    functions = {}
    owners = {}
    dossiers = collections.defaultdict(list)
    extents = {}
    graph = {}
    historical = {}
    legacy = directory/'upper-coverage.json'
    if legacy.exists():
        previous = read(legacy)
        assert previous['source_sha256'] == SHA
        inputs[legacy.relative_to(ROOT).as_posix()] = digest(legacy)
        historical = {f['address']: dict(evidence_id=f['evidence_id'], body=f['body'],
            profile=previous['profile_digest'], source=legacy.relative_to(ROOT).as_posix())
            for f in previous['functions']}
    contracts = collections.defaultdict(list)
    for name in ('upper-miio-a.json', 'upper-miio-b.json'):
        path = directory/name
        if not path.exists():
            continue
        previous = read(path)
        assert previous['source_sha256'] == SHA
        inputs[path.relative_to(ROOT).as_posix()] = digest(path)
        for f in previous['functions']:
            contracts[f['address']].append(dict(source=path.relative_to(ROOT).as_posix(),
                evidence_id=f.get('evidence_id'), role=f.get('role'),
                status='historical-local-contract-dependency-closure-open'))
    for e in records:
        if e.get('analysis_profile'):
            profiles.add(e['analysis_profile']['digest'])
        op = e['operation']
        n = e['normalized_result']
        if op == 'list_procedures':
            for p in n:
                functions[p['address']] = dict(address=p['address'], name=p['value'],
                    classification=p.get('procedure'),
                    inventory_evidence=e['evidence_id'], source_paths=[], families=[], dossiers=[])
        elif op == 'search_strings':
            for s in n:
                if not SOURCE.search(s['value']):
                    continue
                a = s['address']
                off = int(a, 16) - BASE
                raw = s['value'].encode('ascii')
                assert image[off:off+len(raw)] == raw
                paths.setdefault(a, dict(address=a, file_offset=off, text=s['value'],
                    family=source_family(s['value']), references=[], evidence_ids=[]))
                paths[a]['evidence_ids'].append(e['evidence_id'])
        elif op == 'inspect_native_instruction':
            owners[n['address']] = dict(procedure=n['procedure'], evidence_id=e['evidence_id'],
                                        status=n['status'])
        elif op == 'procedure_info':
            extents[n['entrypoint']] = dict(body=n['body'], evidence_id=e['evidence_id'],
                                            limitations=local_limits(e))
        elif op == 'procedure_callees':
            graph[e['parameters']['procedure']] = dict(callees=n, evidence_id=e['evidence_id'],
                                                       limitations=local_limits(e))
        elif op == 'xrefs':
            xref_records.append(dict(parameters=e['parameters'], normalized_result=n,
                                     evidence_id=e['evidence_id']))
        elif op == 'analyze_function':
            dossiers[n['procedure']['address']].append(dict(evidence_id=e['evidence_id'],
                profile=e['analysis_profile']['digest'], body=n['procedure']['body'],
                limitations=n.get('limitations', []),
                unresolved_calls=n.get('unresolved_calls', []),
                opaque_instructions=[a for a in n['assembly'] if 'custom' in a],
                decompiler_warnings=[marker for marker in (
                    'halt_baddata', 'bad instruction', 'unaff_', 'Subroutine does not return')
                    if marker in n['pseudocode']],
                callees=[c['address'] for c in n['callees']],
                review_status='collected-not-implementation-reviewed'))
    for e in xref_records:
        p = paths.get(e['parameters']['address'])
        if p is None:
            continue
        p['evidence_ids'].append(e['evidence_id'])
        for address in e['normalized_result']:
            owner = owners.get(address)
            p['references'].append(dict(address=address, xref_evidence=e['evidence_id'], owner=owner))
            if owner and owner['procedure'] in functions:
                f = functions[owner['procedure']]
                f['source_paths'].append(p['address'])
                f['families'].append(p['family'])
    for address, f in functions.items():
        f['source_paths'] = sorted(set(f['source_paths']))
        f['families'] = sorted(set(f['families']))
        f['dossiers'] = dossiers[address]
        f['historical_dossier'] = historical.get(address)
        f['historical_contracts'] = contracts[address]
        f['extent'] = extents.get(address)
        f['direct_calls'] = graph.get(address)
        f['scope'] = ('external-boundary' if not address.startswith('0xa')
                      else 'vendor-or-mixed' if any(x.startswith('vendor') for x in f['families'])
                      or f['historical_contracts']
                      else 'source-origin-candidate' if f['families'] and all(x.startswith('open-source') for x in f['families'])
                      else 'unresolved')
        f['excluded_as_verified_open_source'] = False
        f['complete'] = False
    intervals = []
    for e in extents.values():
        for r in e['body'].get('ranges', []):
            if r['start'].startswith('0xa') and r['end'].startswith('0xa'):
                lo, hi = int(r['start'], 16), int(r['end'], 16)+1
                assert BASE <= lo < hi <= BASE+len(image)
                intervals.append((lo, hi))
    merged = []
    for lo, hi in sorted(intervals):
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(hi, merged[-1][1])
        else:
            merged.append([lo, hi])
    gaps = []
    cursor = BASE
    for lo, hi in merged + [[BASE+len(image), BASE+len(image)]]:
        if cursor < lo:
            gaps.append(dict(start=hex(cursor), end_exclusive=hex(lo),
                             file_offset=cursor-BASE, length=lo-cursor))
        cursor = hi
    frontier = collections.defaultdict(set)
    for f in functions.values():
        if f['scope'] != 'vendor-or-mixed' or not f['direct_calls']:
            continue
        for callee in f['direct_calls']['callees']:
            target = functions.get(callee)
            if target and target['scope'] == 'unresolved' and not target['dossiers'] and not target['historical_dossier']:
                frontier[callee].add(f['address'])
    return dict(schema=1, rom_sha256=SHA, base_address=hex(BASE), inputs=inputs,
        profiles=sorted(profiles),
        summary=dict(observed_procedures=len(functions), source_path_candidates=len(paths),
            paths_with_resolved_owners=sum(any(r['owner'] and r['owner']['procedure'] for r in p['references']) for p in paths.values()),
            scope_counts=dict(collections.Counter(f['scope'] for f in functions.values())),
            collected_procedures=sum(bool(f['dossiers']) for f in functions.values()),
            historically_collected_procedures=sum(bool(f['historical_dossier']) for f in functions.values()),
            historical_local_contracts=sum(bool(f['historical_contracts']) for f in functions.values()),
            procedures_with_extents=len(extents), procedures_with_direct_calls=len(graph),
            resolved_direct_edges=sum(len(v['callees']) for v in graph.values()),
            provider_body_union_bytes=sum(hi-lo for lo, hi in merged),
            bytes_outside_provider_bodies=sum(g['length'] for g in gaps),
            unresolved_private_direct_frontier=len(frontier),
            verified_open_source_exclusions=0, complete_private_procedures=0),
        source_paths=sorted(paths.values(), key=lambda p: p['address']),
        functions=list(functions.values()),
        private_direct_frontier=[dict(address=a, callers=sorted(frontier[a])) for a in sorted(frontier)],
        ranges_outside_provider_bodies=gaps,
        limitations=['Inventory covers provider-defined procedures, not all executable bytes.',
            'Ranges outside provider bodies include resources, strings, padding and potentially unidentified code; they are not all executable.',
            'Direct C-path xrefs are attribution candidates; inlining, shared assertions and modified library code remain possible.',
            'No source-path candidate is automatically certified as unchanged open source.',
            'Collected dossiers do not imply reviewed implementations or closed indirect-call dependencies.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', type=Path, default=ROOT/'evidence/rea-0041-20261017/evidence')
    parser.add_argument('--queue', choices=['paths', 'owners', 'private-dossiers', 'graph'])
    parser.add_argument('--id')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    value = build(args.evidence_dir)
    if args.queue:
        assert args.id, '--id required for queue'
        if args.queue == 'paths':
            commands = [('xrefs', dict(address=p['address'])) for p in value['source_paths']]
        elif args.queue == 'owners':
            addresses = sorted({r['address'] for p in value['source_paths'] for r in p['references']})
            commands = [('inspect_native_instruction', dict(address=a)) for a in addresses]
        elif args.queue == 'graph':
            commands = []
            for f in value['functions']:
                if not f['extent']:
                    commands.append(('procedure_info', dict(procedure=f['address'])))
                if not f['direct_calls']:
                    commands.append(('procedure_callees', dict(procedure=f['address'])))
        else:
            commands = [('analyze_function', dict(procedure=f['address'])) for f in value['functions']
                        if f['scope'] == 'vendor-or-mixed' and not f['dossiers'] and not f['historical_dossier']]
        value = dict(id=args.id, commands=[dict(name=n, arguments=a) for n, a in commands])
    if args.check:
        assert read(args.out) == value, 'Coverage differs from retained inputs'
        print('PASS: deterministic ROM coverage and input fingerprints')
    else:
        assert not args.out.exists(), 'Refusing to overwrite an existing result'
        args.out.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(value.get('summary', dict(commands=len(value.get('commands', []))))))


if __name__ == '__main__':
    main()
