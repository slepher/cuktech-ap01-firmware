"""Exercise resident ABI 3 platform with a real package and explicit host-only App entries."""
import argparse,json,subprocess
from pathlib import Path
import native_build_0041 as native
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
p.add_argument('--package',type=Path,required=True);a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
names=['native_app_platform_v3.cpp','app_boot_v3.cpp','app_binding_v3.cpp','app_files_v3.cpp',
       'app_network_v3.cpp','apx2.cpp','native_sha256_0041.cpp','model_platform_v3.cpp','test_native_app_platform_v3.cpp']
sources=[native.MODULES/n for n in names];host=a.out/'screen-host-v3.o'
subprocess.run(['clang','-std=c11','-g','-fsanitize=address,undefined','-c',str(native.MODULES/'screen_host_0041.c'),'-o',str(host)],check=True)
binary=a.out.resolve()/'test-native-app-platform-v3';report=a.out/'native-app-platform-v3-report.json'
native.write_json(report,{'passed':False})
subprocess.run(['clang++','-std=c++17','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
                *map(str,sources),str(host),'-o',str(binary)],check=True)
result=subprocess.check_output([str(binary),str(a.package.resolve())],text=True,timeout=30)
native.write_json(report,{'passed':True,'checks':result.strip(),'package_sha256':native.sha(a.package),
                          'app_instructions_executed':False,'device_accessed':False,
                          'sources':{s.name:native.sha(s) for s in sources},
                          'substitutes':['App entries','native maintenance listener','ROM I/O/LVGL/threads']})
print(result,end='')
