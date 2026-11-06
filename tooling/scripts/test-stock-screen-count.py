"""Compile the real screen host for 0041 and 0055 and test native/App boundaries."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    modules = Path(__file__).resolve().parents[1] / 'firmware-modules'
    sources = [modules / 'test_stock_screen_count_0055.c', modules / 'screen_host_0041.c']
    compiler = shutil.which('clang') or shutil.which('gcc')
    environment = None
    if not compiler:
        vcvars = Path('C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Auxiliary/Build/vcvars64.bat')
        if not vcvars.is_file():
            parser.error('Install a C compiler or run from a Visual Studio developer shell')
        result = subprocess.run(f'cmd.exe /d /u /s /c ""{vcvars}" >nul && set"',
                                encoding='utf-16-le', errors='replace', capture_output=True, check=True)
        environment = os.environ.copy()
        environment.update(line.split('=', 1) for line in result.stdout.splitlines()
                           if '=' in line and not line.startswith('='))
        compiler = shutil.which('cl.exe', path=environment.get('Path', environment.get('PATH')))
        if not compiler:
            parser.error('Visual Studio environment did not provide cl.exe')
    report_path = out / 'stock-screen-count-report.json'
    report = {'passed': False, 'device_accessed': False,
              'sanitizers': False, 'compiler': compiler, 'targets': {},
              'sources': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sources + [modules / 'screen_host_0041.h',
                                              modules / 'native_rom_addresses.h',
                                              modules / 'native_rom_addresses_0055.h']}}
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    msvc = Path(compiler).name.lower() == 'cl.exe'
    for target, count in [('0041', 9), ('0055', 11)]:
        target_dir = out / target
        target_dir.mkdir(exist_ok=True)
        binary = target_dir / ('test-stock-count.exe' if os.name == 'nt' else 'test-stock-count')
        defines = ['AP01_ROM_0055=1'] if target == '0055' else []
        if msvc:
            command = [compiler, '/nologo', '/std:c11', '/W4', '/WX', '/O2', '/D_CRT_SECURE_NO_WARNINGS',
                       *['/D' + d for d in defines], *map(str, sources), '/Fe:' + str(binary)]
        else:
            command = [compiler, '-std=c11', '-Wall', '-Wextra', '-Werror', '-O2',
                       *['-D' + d for d in defines], *map(str, sources), '-o', str(binary)]
        subprocess.run(command, cwd=target_dir, env=environment, check=True)
        result = subprocess.check_output([str(binary)], text=True, timeout=30)
        checks = json.loads(result)
        assert checks['passed'] and checks['stock_count'] == count
        report['targets'][target] = checks
        print(target + ': ' + result.strip())
    report['passed'] = True
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
