"""Build/test from a fresh copy with no sibling App or reverse checkout.

Only firmware inputs are copied. The installed compiler and Python are external
tools; no device is accessed. --out must name a new directory.
"""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--tool-prefix')
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    isolated = out / 'firmware'
    for directory in ('tooling/firmware-modules', 'tooling/vendor/ArduinoJson'):
        shutil.copytree(ROOT / directory, isolated / directory)
    scripts = isolated / 'tooling/scripts'
    scripts.mkdir(parents=True)
    for name in ('build-firmware.py', 'native_build.py', 'rom_target.py', 'build-native-app-rom.py', 'test-firmware.py', 'test-rom-target.py'):
        shutil.copyfile(ROOT / 'tooling/scripts' / name, scripts / name)
    original = isolated / 'roms/0055/ap01-1.0.2_0055.bin'
    original.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / 'roms/0055' / original.name, original)
    shutil.copytree(ROOT / 'tooling/rom-targets', isolated / 'tooling/rom-targets')
    output = isolated / 'build/ap01-platform.bin'
    command = [sys.executable, '-B', str(scripts / 'build-firmware.py'), '--output', str(output)]
    if args.tool_prefix:
        command += ['--tool-prefix', args.tool_prefix]
    subprocess.run(command, cwd=isolated, check=True)
    subprocess.run([sys.executable, '-B', str(scripts / 'test-firmware.py'),
                    '--manifest', str(output.with_suffix('.manifest.json'))], cwd=isolated, check=True)
    subprocess.run([sys.executable, '-B', str(scripts / 'test-rom-target.py')], cwd=isolated, check=True)
    report = {'passed': True, 'scope': 'fresh copied platform build and ROM/OTA checks',
              'app_present': False, 'reverse_checkout_present': False, 'device_accessed': False,
              'rom': str(output), 'manifest': str(output.with_suffix('.manifest.json'))}
    (out / 'independence-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
