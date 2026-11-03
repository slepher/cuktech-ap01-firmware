"""Validate native window binding lifetime without accessing a device."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--tool-prefix');a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
m=Path(__file__).resolve().parents[1]/'firmware-modules';sources=[m/'test_screen_binding_0041.cpp']
binary=a.out.resolve()/'test-screen-binding';report_path=a.out/'screen-binding-report.json';report_path.write_text('{"passed":false}\n')
subprocess.run(['clang++','-std=c++17','-Wall','-Wextra','-Werror','-pthread','-fsanitize=address,undefined',*map(str,sources),'-o',str(binary)],check=True)
result=subprocess.check_output([str(binary)],text=True,timeout=30)
report={'passed':True,'checks':result.strip(),'device_accessed':False,
        'sources':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sources+[m/'screen_port_0041.h',m/'screen_port_0041.cpp']}}
if a.tool_prefix:
    import native_build_0041 as native
    obj=a.out.resolve()/'screen-port.rv32.o'
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror','-c',str(m/'screen_port_0041.cpp'),'-o',str(obj)],check=True)
    report['rv32_sha256']=hashlib.sha256(obj.read_bytes()).hexdigest()
report_path.write_text(json.dumps(report,indent=2)+'\n');print(result,end='')
