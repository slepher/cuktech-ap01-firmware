"""Exercise the firmware App generation admission gate under concurrent unloads."""
import argparse
from pathlib import Path
import subprocess
import hashlib
import json

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--tool-prefix')
p.add_argument('--thread-sanitizer', action='store_true')
a = p.parse_args()
if not a.out.is_dir():
    p.error('Precreate output directory')
root = Path(__file__).resolve().parents[1] / 'firmware-modules'
binary = a.out.resolve() / 'test-app-generation'
sanitizer = 'thread' if a.thread_sanitizer else 'address,undefined'
subprocess.run(['clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-pthread',
                '-fsanitize=' + sanitizer, '-g', str(root / 'test_app_generation_0041.cpp'),
                '-o', str(binary)], check=True)
result = subprocess.check_output([str(binary)], text=True, timeout=60)
print(result, end='')
report = {'passed': True, 'checks': result.strip(), 'sanitizer': sanitizer,
          'rv32_compiled': False, 'hardware_verified': False,
          'sources': {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                      for name in ('app_generation_0041.h', 'test_app_generation_0041.cpp')}}
if a.tool_prefix:
    # Compile the actual header's atomic operations, without host thread support.
    source = a.out.resolve() / 'gate-rv32.cpp'
    source.write_text('#include "app_generation_0041.h"\n'
                      'bool probe(Ap01AppGeneration0041 &g) {'
                      'auto id=g.begin(); Ap01AppLease0041 lease(g,id); g.close();'
                      'return bool(lease) && !g.drained();}\n')
    obj = source.with_suffix('.o')
    import native_build_0041 as native
    subprocess.run([a.tool_prefix + 'g++', *native.FLAGS, '-I' + str(root), '-c',
                    str(source), '-o', str(obj)], check=True)
    undefined = subprocess.check_output([a.tool_prefix + 'nm', '-u', str(obj)], text=True)
    assert not undefined.strip(), undefined  # No libatomic dependency on target.
    report['rv32_compiled'] = True
    report['rv32_object_sha256'] = hashlib.sha256(obj.read_bytes()).hexdigest()
    print('RV32 gate compiled; no undefined symbols or libatomic requirement')
(a.out / 'generation-report.json').write_text(json.dumps(report, indent=2) + '\n')
