"""Verify the private file-App formatter without replacing the platform libc."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
import native_build_0041 as native

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--tool-prefix', required=True)
a = p.parse_args()
if not a.out.is_dir():
    p.error('Precreate output directory')
m = Path(__file__).resolve().parents[1] / 'firmware-modules'
report = a.out / 'runtime-format-report.json'
report.write_text('{"passed":false}\n')
names = ['app_runtime_format_v2.cpp', 'test_app_runtime_format_v2.cpp']
binary = a.out.resolve() / 'test-runtime-format'
subprocess.run(['clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                '-fsanitize=address,undefined', '-DAP01_RUNTIME_FORMAT_HOST_TEST',
                *[str(m / n) for n in names], '-o', str(binary)], check=True)
checks = subprocess.check_output([str(binary)], text=True, timeout=30).strip()
obj = a.out.resolve() / 'app-runtime-format.rv32.o'
flags = [f for f in native.FLAGS if f != '-fno-pic'] + ['-fpie', '-fvisibility=hidden', '-mcmodel=medany']
subprocess.run([a.tool_prefix + 'g++', *flags, '-Wall', '-Wextra', '-Werror',
                '-c', str(m / names[0]), '-o', str(obj)], check=True)
defined = subprocess.check_output([a.tool_prefix + 'nm', '--defined-only', str(obj)], text=True)
assert {'snprintf', 'ap01_app_snprintf_v2'} <= {line.split()[-1] for line in defined.splitlines()}
undefined = subprocess.check_output([a.tool_prefix + 'nm', '-u', str(obj)], text=True)
assert {line.split()[-1] for line in undefined.splitlines()} <= {'__udivdi3', '__umoddi3', '__udivmoddi4'}, undefined
sections = subprocess.check_output([a.tool_prefix + 'readelf', '-SW', str(obj)], text=True)
assert not re.search(r'\.(?:init_array|ctors|got|tdata|tbss)(?:\s|\.)', sections), sections
assert names[0] not in native.PLATFORM_SOURCES
report.write_text(json.dumps(dict(
    passed=True, checks=checks, device_accessed=False, platform_runtime_replaced=False,
    real_file_app_linked=False, undefined=undefined.splitlines(),
    rv32_sha256=hashlib.sha256(obj.read_bytes()).hexdigest(),
    sources={n: hashlib.sha256((m / n).read_bytes()).hexdigest() for n in names}
), indent=2) + '\n')
print(checks)
