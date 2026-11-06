"""Save an allowlisted AP01 research checkpoint outside disposable build output."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def verify(directory):
    directory = directory.resolve()
    manifest = json.loads((directory / 'checkpoint.json').read_text(encoding='utf-8'))
    if manifest['format'] != 1:
        raise ValueError('Unknown checkpoint format')
    for item in manifest['files']:
        path = (directory / item['path']).resolve()
        if not path.is_relative_to(directory):
            raise ValueError('Checkpoint path escapes its directory')
        if path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise ValueError('Checkpoint integrity mismatch: ' + item['path'])
    return manifest


def save(directory):
    directory = directory.resolve()
    if not directory.is_relative_to(ROOT / 'evidence') or directory == ROOT / 'evidence':
        raise ValueError('Use a new child directory inside repository evidence/')
    selected = set()
    patterns = (
        'docs/*0055*.md', 'docs/reverse-engineering-quickstart.md',
        'tooling/rom-targets/*.json', 'tooling/firmware-modules/native_rom_addresses*.h',
        'tooling/scripts/*0055*.py', 'tooling/scripts/*rom-target*.py',
        'tooling/scripts/rom_target.py', 'tooling/scripts/save-research-checkpoint.py',
        'tooling/scripts/build-app-v3-0041.py', 'tooling/scripts/build-app-v3-guest-0041.py',
        'tooling/scripts/test-app-abi-qemu-0041.py', 'tooling/scripts/test-app-pic-load-0041.py',
        'tooling/firmware-modules/model_platform_v3.cpp',
        'tooling/firmware-modules/probe_app_v3_guest.cpp',
        'tooling/firmware-modules/probe_app_set_v3_guest.h',
        'build/migration-0055-assessment/compare.py',
        'build/migration-0055-assessment/rea-*.json',
        'build/migration-0055-assessment/services/*.py',
        'build/migration-0055-assessment/services/*.json',
        'build/migration-0055-assessment/ui/*.py',
        'build/migration-0055-assessment/ui/*.json',
        'evidence/0055-address-migration-20261106/*.json',
        'build/qemu-0055-20261106/toolchain-comparison.json',
        'build/qemu-0055-20261106/app-executionreports/*.json',
        'build/qemu-0055-20261106/baseline/model-baseline.json',
        'build/qemu-0055-20261106/guest-collection-input/*.json',
        'build/qemu-0055-20261106/guest-single-0055/*.bin',
        'build/qemu-0055-20261106/guest-single-0055/*.apx2',
        'build/qemu-0055-20261106/guest-single-0055/build-report.json',
        'build/qemu-0055-20261106/guest-collection-0055-fixed/*.bin',
        'build/qemu-0055-20261106/guest-collection-0055-fixed/*.apx2',
        'build/qemu-0055-20261106/guest-collection-0055-fixed/*.amf3',
        'build/qemu-0055-20261106/guest-collection-0055-fixed/build-report.json',
        'build/qemu-0055-20261106/guest-collection-0041/*.bin',
        'build/qemu-0055-20261106/guest-collection-0041/*.apx2',
        'build/qemu-0055-20261106/guest-collection-0041/*.amf3',
        'build/qemu-0055-20261106/guest-collection-0041/build-report.json',
        'build/qemu-0055-20261106/python/elftools/**/*.py',
        'build/qemu-0055-20261106/toolchains/release-*.json',
        'build/qemu-0055-20261106/toolchains/*.tar.gz',
        'build/0055-qemu-verified-20261106/release.json',
        'build/0055-qemu-verified-20261106/qemu-native/*.json',
    )
    for pattern in patterns:
        selected.update(path for path in ROOT.glob(pattern) if path.is_file())
    # Large linear-decode caches are cheap to regenerate and not approved maps.
    selected = {p for p in selected if p.name not in ('decode-cache.json', 'new-disassembly.json')}
    required = [ROOT / 'evidence/0055-address-migration-20261106/rea-0055-snapshot.json',
                ROOT / 'tooling/firmware-modules/native_rom_addresses_0055.h',
                ROOT / 'build/0055-qemu-verified-20261106/release.json']
    if any(path not in selected for path in required):
        raise FileNotFoundError('Missing current research checkpoint inputs')
    directory.mkdir(parents=True, exist_ok=False)
    manifest = {'format': 1, 'scope': '0041 to 0055 research, not a complete source/environment backup',
                'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'files': [], 'roms': {}, 'omitted_caches': ['decode-cache.json', 'new-disassembly.json']}
    for source in sorted(selected):
        source = source.resolve()
        if not source.is_relative_to(ROOT):
            raise ValueError('Research input outside repository')
        target = directory / 'files' / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        method = 'copy'
        if source.name.endswith('.tar.gz'):
            try:
                target.hardlink_to(source)
                method = 'hardlink'
            except OSError:
                shutil.copyfile(source, target)
        else:
            shutil.copyfile(source, target)
        manifest['files'].append({'path': target.relative_to(directory).as_posix(),
                                  'bytes': target.stat().st_size, 'sha256': sha(target), 'storage': method})
    for version in ('0041', '0055'):
        path = ROOT / f'roms/{version}/ap01-1.0.2_{version}.bin'
        manifest['roms'][version] = {'path': path.relative_to(ROOT).as_posix(),
                                    'bytes': path.stat().st_size, 'sha256': sha(path), 'copied': False}
    coverage = ROOT.parent / 'cuktech-ap01-firmware-reverse/reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
    if coverage.is_file():
        old = json.loads(coverage.read_text(encoding='utf-8'))
        if old['rom_sha256'] != manifest['roms']['0041']['sha256']:
            raise ValueError('Historical function coverage belongs to another ROM')
        compact = {'source_sha256': sha(coverage), 'rom_sha256': old['rom_sha256'],
                   'base_address': old['base_address'], 'profiles': old['profiles'],
                   'functions': [{key: row[key] for key in ('address', 'name', 'extent', 'direct_calls')}
                                 for row in old['functions']]}
        target = directory / 'analysis/0041-function-boundaries.json'
        target.parent.mkdir()
        target.write_text(json.dumps(compact, indent=2) + '\n', encoding='utf-8')
        manifest['files'].append({'path': target.relative_to(directory).as_posix(),
                                  'bytes': target.stat().st_size, 'sha256': sha(target), 'storage': 'derived'})
    (directory / 'checkpoint.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return verify(directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--out', type=Path, help='New evidence/ child directory; refuses overwrite')
    mode.add_argument('--verify', type=Path, help='Read-only integrity check of an existing checkpoint')
    args = parser.parse_args()
    try:
        result = verify(args.verify) if args.verify else save(args.out)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps({'passed': True, 'files': len(result['files']),
                      'bytes': sum(item['bytes'] for item in result['files']),
                      'path': str((args.verify or args.out).resolve())}))


if __name__ == '__main__':
    main()
