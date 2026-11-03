"""Fault-inject the App metadata journal; storage durability is a port contract."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--tool-prefix')
a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
m=Path(__file__).resolve().parents[1]/'firmware-modules'
sources=[m/'app_update_record_0041.cpp',m/'test_app_update_record_0041.cpp']
binary=a.out.resolve()/'test-journal'
report_path=a.out/'journal-report.json'
report_path.write_text(json.dumps({'passed':False,'stage':'building'})+'\n')
subprocess.run(['clang++','-std=c++17','-Wall','-Wextra','-Werror','-g',
                '-fsanitize=address,undefined',*map(str,sources),'-o',str(binary)],check=True)
result=subprocess.check_output([str(binary)],text=True,timeout=30)
report={'passed':True,'checks':result.strip(),'device_accessed':False,
        'storage_durability_verified':False,
        'sources':{s.name:hashlib.sha256(s.read_bytes()).hexdigest() for s in sources}}
if a.tool_prefix:
    import native_build_0041 as native
    obj=a.out.resolve()/'journal.rv32.o'
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror',
                    '-c',str(sources[0]),'-o',str(obj)],check=True)
    report['rv32_object_sha256']=hashlib.sha256(obj.read_bytes()).hexdigest()
report_path.write_text(json.dumps(report,indent=2)+'\n')
print(result,end='')
