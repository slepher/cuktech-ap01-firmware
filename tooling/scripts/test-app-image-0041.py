"""Check APX2 image ownership and lifecycle using a host execution backend."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--package',type=Path,required=True,help='golden.apx2 from test-apx2.py')
p.add_argument('--tool-prefix')
a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
m=Path(__file__).resolve().parents[1]/'firmware-modules'
names=['app_image_0041.cpp','app_lifecycle_0041.cpp','apx2.cpp','native_sha256_0041.cpp','test_app_image_0041.cpp']
binary=a.out.resolve()/'test-image'
report_path=a.out/'image-report.json';report_path.write_text('{"passed":false}\n')
subprocess.run(['clang++','-std=c++17','-Wall','-Wextra','-Werror','-g',
                '-fsanitize=address,undefined',*[str(m/n) for n in names],'-o',str(binary)],check=True)
result=subprocess.check_output([str(binary),str(a.package.resolve())],text=True,timeout=120)
report={'passed':True,'checks':result.strip(),'device_accessed':False,'app_instructions_executed':False,'backend':'host callbacks',
        'sources':{n:hashlib.sha256((m/n).read_bytes()).hexdigest() for n in names+['app_image_0041.h','app_lifecycle_0041.h','app_abi_v2.h','app_generation_0041.h','apx2.h']}}
if a.tool_prefix:
    import native_build_0041 as native
    obj=a.out.resolve()/'image.rv32.o'
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror',
                    '-c',str(m/names[0]),'-o',str(obj)],check=True)
    report['rv32_object_sha256']=hashlib.sha256(obj.read_bytes()).hexdigest()
report_path.write_text(json.dumps(report,indent=2)+'\n');print(result,end='')
