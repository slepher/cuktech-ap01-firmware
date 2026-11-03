"""Verify pure runtime support and calendar against independent host libc."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import native_build_0041 as native
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--tool-prefix',required=True);a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
m=native.MODULES;report=a.out/'libc-report.json';report.write_text('{"passed":false}\n')
sources=['runtime_libc_0041.cpp','native_calendar_0041.cpp','test_runtime_libc_0041.cpp'];binary=a.out.resolve()/'test-libc'
subprocess.run(['clang++','-std=c++17','-O1','-g','-fno-builtin','-fsanitize=address,undefined','-DAP01_RUNTIME_LIBC_HOST_TEST',*[str(m/n) for n in sources],'-o',str(binary)],check=True)
checks=subprocess.check_output([str(binary)],text=True,timeout=60).strip();objects={}
for name in sources[:2]+['native_sha256_0041.cpp']:
 obj=a.out.resolve()/(name+'.o')
 flags=[f for f in native.FLAGS if f!='-fno-pic']+['-fpie','-fvisibility=hidden','-mcmodel=medany']
 subprocess.run([a.tool_prefix+'g++',*flags,'-c',str(m/name),'-o',str(obj)],check=True)
 objects[name]=hashlib.sha256(obj.read_bytes()).hexdigest()
report.write_text(json.dumps(dict(passed=True,checks=checks,device_accessed=False,host_libc_interposed=False,rv32_pic_objects=objects,sources={n:hashlib.sha256((m/n).read_bytes()).hexdigest() for n in sources+['native_sha256_0041.cpp']}),indent=2)+'\n');print(checks)
