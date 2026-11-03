"""Check the network C service ABI and generation gate; no device access."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--tool-prefix');a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
(a.out/'network-report.json').write_text('{"passed":false}\n')
m=Path(__file__).resolve().parents[1]/'firmware-modules'
sources=[m/'app_heap_0041.cpp',m/'app_network_0041.cpp',m/'app_core_0041.cpp',m/'app_files_0041.cpp',m/'test_app_network_0041.cpp'];binary=a.out.resolve()/'test-network'
subprocess.run(['clang++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*map(str,sources),'-o',str(binary)],check=True)
result=subprocess.check_output([str(binary)],text=True,timeout=30)
c=a.out.resolve()/'abi-check.c';c.write_text('#include "app_network_abi_v2.h"\nint abi(void){return AP01_APP_ABI_V2;}\n')
subprocess.run(['clang','-std=c11','-Wall','-Werror','-I'+str(m),'-c',str(c),'-o',str(c.with_suffix('.o'))],check=True)
report={'passed':True,'checks':result.strip(),'c_header':True,'device_accessed':False,
        'sources':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sources+[m/'app_network_abi_v2.h',m/'app_network_0041.h',m/'app_network_native_0041.cpp',m/'app_network_client_v2.h',m/'app_services_0041.h',m/'app_core_abi_v2.h']}}
if a.tool_prefix:
    import native_build_0041 as native
    obj=a.out.resolve()/'network.rv32.o'
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror','-c',str(m/'app_network_0041.cpp'),'-o',str(obj)],check=True)
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror','-c',str(m/'app_network_native_0041.cpp'),'-o',str(a.out.resolve()/'network-native.rv32.o')],check=True)
    report['rv32_sha256']=hashlib.sha256(obj.read_bytes()).hexdigest()
    report['rv32_native_sha256']=hashlib.sha256((a.out/'network-native.rv32.o').read_bytes()).hexdigest()
(a.out/'network-report.json').write_text(json.dumps(report,indent=2)+'\n');print(result,end='')
