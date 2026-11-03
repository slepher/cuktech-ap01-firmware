"""Build and exercise the production APX2 core with independent Python SHA/package bytes."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import copy

import apx2


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--tool-prefix', help='Also compile production sources for RV32 with this toolchain')
    args = p.parse_args()
    out = args.out.resolve()
    if not out.is_dir(): p.error('Precreate output directory')
    root = Path(__file__).resolve().parents[1] / 'firmware-modules'
    binary = out / 'test-apx2'
    sources = [root / name for name in ('apx2.cpp', 'native_sha256_0041.cpp', 'test_apx2.cpp')]
    subprocess.run(['clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-g',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    *map(str, sources), '-o', str(binary)], check=True)
    result = subprocess.check_output([str(binary)], text=True)
    print(result, end='')
    for length in (0, 1, 55, 56, 63, 64, 65, 127, 128, 129, 65536):
        blob = bytes(i % 251 for i in range(length))
        path = out / 'sha-input.bin';path.write_bytes(blob)
        got = subprocess.check_output([str(binary), '--sha', str(path)], text=True).strip()
        assert got == hashlib.sha256(blob).hexdigest(), length
    image = bytes(48)
    config = dict(app_id='golden.app', version='1.0.0', text_bytes=16, ro_offset=16, ro_bytes=16,
                  data_offset=32, data_bytes=16, bss_bytes=16, heap_bytes=128, stack_bytes=256,
                  entries=[0, 2, 4, 6, 8], data_read_min=1, data_read_max=3,
                  data_write_version=2, required_services=1, fixups=[[16, 0], [32, 0]])
    golden = apx2.package(image, config)
    bad_configs = [dict(text_bytes=0), dict(ro_offset=15), dict(ro_bytes=17),
                   dict(data_offset=16), dict(data_bytes=15), dict(bss_bytes=0xffffffff),
                   dict(entries=[1, 2, 4, 6, 8]), dict(entries=[16, 2, 4, 6, 8]),
                   dict(stack_bytes=240), dict(stack_bytes=257), dict(data_read_min=3),
                   dict(fixups=[[0, 0]]), dict(fixups=[[16, 64]]),
                   dict(fixups=[[32, 0], [16, 0]]), dict(fixups=[[16, 0], [16, 0]])]
    for change in bad_configs:
        bad = copy.deepcopy(config); bad.update(change)
        try:
            apx2.package(image, bad)
        except ValueError:
            pass
        else:
            raise AssertionError(('accepted invalid manifest', change))
    path = out / 'golden.apx2';path.write_bytes(golden)
    subprocess.run([str(binary), '--package', str(path)], check=True)
    direct_config = dict(config, abi_major=3, entries=[0, 2, 4])
    direct = apx2.package(image, direct_config)
    direct_path = out / 'golden-v3.apx2';direct_path.write_bytes(direct)
    subprocess.run([str(binary), '--package-v3', str(direct_path)], check=True)
    for mode, package_path in (('--package', direct_path), ('--package-v3', path)):
        rejected = subprocess.run([str(binary), mode, str(package_path)], capture_output=True, text=True)
        assert rejected.returncode == 1 and rejected.stdout.strip() == 'abi'
    for change in (dict(abi_major=4), dict(abi_major=True), dict(entries=[0, 2, 4, 0, 0])):
        try:
            apx2.package(image, dict(direct_config, **change))
        except ValueError:
            pass
        else:
            raise AssertionError(('accepted invalid direct manifest', change))
    (out / 'golden.json').write_text(json.dumps(config, indent=2) + '\n')
    report = {'passed': True, 'core_tests': result.strip(), 'python_sha_vectors': 11,
              'writer_rejections': len(bad_configs),
              'golden_bytes': len(golden), 'golden_file_sha256': hashlib.sha256(golden).hexdigest(),
              'golden_content_sha256': golden[192:224].hex(), 'hardware_verified': False,
              'direct_abi': {'major': 3, 'golden_file_sha256': hashlib.sha256(direct).hexdigest(),
                             'cross_abi_rejected': True, 'reserved_entries_rejected': True},
              'sources': {s.name: hashlib.sha256(s.read_bytes()).hexdigest() for s in sources}}
    if args.tool_prefix:
        import native_build_0041 as native
        objects = []
        for source in sources[:2]:
            obj = out / (source.stem + '.rv32.o')
            subprocess.run([args.tool_prefix + 'g++', *native.FLAGS, '-Wall', '-Wextra',
                            '-Werror', '-c', str(source), '-o', str(obj)], check=True)
            objects.append({'name': obj.name, 'sha256': hashlib.sha256(obj.read_bytes()).hexdigest(),
                            'stack_usage': obj.with_suffix('.su').read_text()})
        report['rv32_compile'] = objects
    (out / 'apx2-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
