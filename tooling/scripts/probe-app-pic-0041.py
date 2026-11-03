"""Compile the audited App as PIE and inventory relocations; no ROM or device writes.

This is an S1 compiler experiment, not an APX2 packager or executable-memory test.
Object section totals include duplicates/dead code and are not a runtime budget.
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import re
import subprocess

import native_build_0041 as native


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--tool-prefix', required=True)
    parser.add_argument('--runtime-heap-object', type=Path, help='Optional private App heap object from test-app-runtime-heap-v2.py')
    parser.add_argument('--support-object', type=Path, action='append', default=[], help='Additional private PIE support object; repeat for libc/calendar/SHA')
    args = parser.parse_args()
    audit = native.validate_audit(args.audit_dir.resolve())
    config = native.read_app_config(Path(audit['app_config']['path']))
    tool = native.tools(args.tool_prefix)
    compiler = subprocess.check_output([tool('g++'), '--version'], text=True).splitlines()[0]
    if compiler != audit['compiler']:
        parser.error('Use the same compiler as the baseline audit')
    out = args.out.resolve()
    if not out.is_dir() or any(out.iterdir()):
        parser.error('--out must be an existing empty directory')
    app_sources = set(config['sources'] + config['plain_sources'])
    records = []
    for item in audit['objects']:
        source = Path(item['source'])
        if source not in app_sources:
            continue
        obj = out / source.with_suffix('.o').name
        flags = [f for f in item['flags'] if f != '-fno-pic']
        flags += ['-fpie', '-fvisibility=hidden', '-mcmodel=medany']
        command = [tool('gcc' if source.suffix == '.c' else 'g++'), *flags,
                   '-c', str(source), '-o', str(obj)]
        subprocess.run(command, check=True)
        relocations = subprocess.check_output([tool('readelf'), '-rW', str(obj)], text=True)
        obj.with_suffix('.relocations.txt').write_text(relocations)
        sizes = subprocess.check_output([tool('size'), '-A', str(obj)], text=True)
        sections = {fields[0]: int(fields[1]) for line in sizes.splitlines()
                    if len(fields := line.split()) == 3 and fields[0].startswith('.')}
        records.append({'source': str(source), 'source_sha256': native.sha(source),
                        'object': str(obj), 'sha256': native.sha(obj), 'command': command,
                        'sections': sections,
                        'relocation_counts': dict(Counter(re.findall(r'R_RISCV_\w+', relocations)))})
    if len(records) != len(app_sources):
        raise ValueError('Baseline audit does not contain every configured App source')
    combined = out / 'app-pic.o'
    subprocess.run([tool('ld'), '-m', 'elf32lriscv', '-r',
                    *[r['object'] for r in records], '-o', str(combined)], check=True)
    allocator = None
    support = []
    if args.support_object:
        linked = out / 'app-with-support.o'
        paths = [p.resolve() for p in args.support_object]
        subprocess.run([tool('ld'), '-m', 'elf32lriscv', '-r', str(combined), *map(str, paths), '-o', str(linked)], check=True)
        support = [{'object': str(p), 'sha256': native.sha(p)} for p in paths]
        combined = linked
    if args.runtime_heap_object:
        runtime = args.runtime_heap_object.resolve()
        linked = out / 'app-with-heap.o'
        subprocess.run([tool('ld'), '-m', 'elf32lriscv', '-r', str(combined), str(runtime), '-o', str(linked)], check=True)
        combined = linked
        allocator = {'object': str(runtime), 'sha256': native.sha(runtime),
                     'combined_sha256': native.sha(combined), 'references_resolved': True}
    undefined = subprocess.check_output([tool('nm'), '-uC', str(combined)], text=True)
    combined_relocations = subprocess.check_output([tool('readelf'), '-rW', str(combined)], text=True)
    (out / 'combined-relocations.txt').write_text(combined_relocations)
    if allocator and re.search(r'\b(?:malloc|calloc|realloc|free)$|operator (?:new|delete)|std::nothrow', undefined, re.MULTILINE):
        raise ValueError('App allocator references remain unresolved')
    (out / 'undefined-imports.txt').write_text(undefined)
    attributes = subprocess.check_output([tool('readelf'), '-hA', str(combined)], text=True)
    (out / 'elf-attributes.txt').write_text(attributes)
    if 'ELF32' not in attributes or 'RISC-V' not in attributes or 'single-float ABI' not in attributes:
        raise ValueError('Expected RV32 single-float ABI')
    counts = Counter()
    for record in records:
        counts.update(record['relocation_counts'])
    report = {'compiled': True, 'final_linked': False, 'hardware_verified': False,
              'file_app_loadable': False, 'compiler': compiler,
              'baseline_audit_sha256': native.sha(args.audit_dir / 'native-core-audit.json'),
              'private_heap_runtime': allocator,
              'private_support_objects': support,
              'script_sha256': native.sha(Path(__file__)), 'objects': records,
              'relocation_counts': dict(sorted(counts.items())),
              'combined_relocation_counts': dict(sorted(Counter(re.findall(r'R_RISCV_\w+', combined_relocations)).items())),
              'undefined_imports': undefined.splitlines(),
              'limitations': ['ET_REL inventory only; compiler relocations are not an APX2 whitelist',
                             'No final layout, bounded fixups, C service ABI or RAM execution verified',
                             'Section sums include duplicate/dead code; not runtime memory measurements']}
    native.write_json(out / 'pic-report.json', report)
    print(json.dumps({'compiled': True, 'objects': len(records), 'relocations': report['relocation_counts'],
                      'undefined_imports': len(report['undefined_imports']),
                      'file_app_loadable': False, 'report': str(out / 'pic-report.json')}))


if __name__ == '__main__':
    main()
