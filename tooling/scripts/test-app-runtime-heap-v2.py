"""Check file-App allocator bindings without interposing on the host/platform heap."""
import argparse, hashlib, json, re, subprocess
from pathlib import Path
import native_build_0041 as native
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True);p.add_argument('--tool-prefix',required=True);a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
m=Path(__file__).resolve().parents[1]/'firmware-modules'
report=a.out/'runtime-heap-report.json';report.write_text('{"passed":false}\n')
names=['app_runtime_heap_v2.cpp','app_runtime_time_v2.cpp','app_heap_0041.cpp','app_core_0041.cpp','app_files_0041.cpp','app_network_0041.cpp','test_app_runtime_heap_v2.cpp']
binary=a.out.resolve()/'test-runtime-heap'
subprocess.run(['clang++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-DAP01_RUNTIME_HEAP_HOST_TEST',*[str(m/n) for n in names],'-o',str(binary)],check=True)
checks=subprocess.check_output([str(binary)],text=True,timeout=30).strip()
obj=a.out.resolve()/'app-runtime-heap.rv32.o'
flags=[f for f in native.FLAGS if f!='-fno-pic']+['-fpie','-fvisibility=hidden','-mcmodel=medany']
subprocess.run([a.tool_prefix+'g++',*flags,'-Wall','-Wextra','-Werror','-c',str(m/names[0]),'-o',str(obj)],check=True)
time_obj=a.out.resolve()/'app-runtime-time.rv32.o'
subprocess.run([a.tool_prefix+'g++',*flags,'-Wall','-Wextra','-Werror','-c',str(m/'app_runtime_time_v2.cpp'),'-o',str(time_obj)],check=True)
time_symbols=subprocess.check_output([a.tool_prefix+'nm','--defined-only',str(time_obj)],text=True)
assert ' time' in time_symbols
assert 'app_runtime_time_v2.cpp' not in native.PLATFORM_SOURCES
symbols=subprocess.check_output([a.tool_prefix+'nm','--defined-only',str(obj)],text=True)
defined={line.split()[-1] for line in symbols.splitlines() if line.split()}
required={'malloc','calloc','realloc','free','_ZnwjRKSt9nothrow_t','_ZnajRKSt9nothrow_t','_ZdlPv','_ZdaPv','_ZdlPvj','_ZdaPvj','_ZSt7nothrow'}
assert required<=defined,required-defined
undefined=subprocess.check_output([a.tool_prefix+'nm','-u',str(obj)],text=True)
assert {line.split()[-1] for line in undefined.splitlines()}<={'memcpy'},undefined
sections=subprocess.check_output([a.tool_prefix+'readelf','-SW',str(obj)],text=True)
assert not re.search(r'\.(?:init_array|ctors)(?:\s|\.)',sections),sections
assert 'app_runtime_heap_v2.cpp' not in native.PLATFORM_SOURCES
headers=['app_runtime_heap_v2.h','app_heap_client_v2.h','app_heap_abi_v2.h','app_services_0041.h']
result=dict(passed=True,checks=checks,device_accessed=False,host_allocator_interposed=False,rv32_pic=True,
            c_and_cpp_allocator_symbols=sorted(required),undefined=undefined.splitlines(),
            platform_runtime_replaced=False,real_file_app_linked=False,
            rv32_sha256=hashlib.sha256(obj.read_bytes()).hexdigest(),
            time_rv32_sha256=hashlib.sha256(time_obj.read_bytes()).hexdigest(),
            sources={n:hashlib.sha256((m/n).read_bytes()).hexdigest() for n in names+headers})
report.write_text(json.dumps(result,indent=2)+'\n');print(checks)
