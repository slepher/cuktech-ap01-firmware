"""Connect AMF3 and resident multi-App ownership using explicit host App substitutes."""
import argparse, subprocess
from pathlib import Path
import native_build_0041 as native
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True);p.add_argument('--package',type=Path,required=True)
p.add_argument('--tool-prefix',required=True);a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
subprocess.run(['python3','-B',str(Path(__file__).with_name('test-app-manifest-v3.py')),
 '--out',str(a.out),'--package',str(a.package),'--tool-prefix',a.tool_prefix],check=True)
names=['app_set_files_v3.cpp','native_app_file_boot_v3.cpp','app_supervision_v3.cpp','native_app_set_v3.cpp','app_set_boot_v3.cpp','app_manifest_v3.cpp','native_app_platform_v3.cpp',
 'app_boot_v3.cpp','app_binding_v3.cpp','app_files_v3.cpp','app_network_v3.cpp','apx2.cpp',
 'native_sha256_0041.cpp','model_platform_v3.cpp','test_native_app_set_v3.cpp']
sources=[native.MODULES/n for n in names];host=a.out/'screen-host.o'
report=a.out/'native-app-set-report.json';native.write_json(report,{'passed':False})
subprocess.run(['clang','-std=c11','-g','-fsanitize=address,undefined','-c',str(native.MODULES/'screen_host_0041.c'),'-o',str(host)],check=True)
binary=a.out.resolve()/'test-native-app-set-v3'
subprocess.run(['clang++','-std=c++17','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
 *map(str,sources),str(host),'-o',str(binary)],check=True)
result=subprocess.check_output([str(binary),str(a.out.resolve()/'two-apps.amf3'),str(a.package.resolve()),
 str(a.out.resolve()/'manifest-peer.apx2')],text=True,timeout=30)
for source in sources[:3]:
 subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror','-c',str(source),
  '-o',str(a.out/(source.stem+'.rv32.o'))],check=True)
observer=a.out.resolve()/'test-app-supervision-v3'
subprocess.run(['clang++','-std=c++17','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-pthread',
 str(native.MODULES/'app_supervision_v3.cpp'),str(native.MODULES/'test_app_supervision_v3.cpp'),'-o',str(observer)],check=True)
result+=subprocess.check_output([str(observer)],text=True,timeout=30)
subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror','-c',str(native.MODULES/'app_supervision_v3.cpp'),
 '-o',str(a.out/'app-supervision-v3.rv32.o')],check=True)
gate_test=a.out.resolve()/'test-app-write-gate-v3'
subprocess.run(['clang++','-std=c++17','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-pthread',
 str(native.MODULES/'app_files_v3.cpp'),str(native.MODULES/'test_app_write_gate_v3.cpp'),'-o',str(gate_test)],check=True)
result+=subprocess.check_output([str(gate_test)],text=True,timeout=30)
sources.append(native.MODULES/'test_app_write_gate_v3.cpp')
sources.append(native.MODULES/'test_app_supervision_v3.cpp')
sources.append(native.MODULES/'screen_host_0041.c')
native.write_json(report,{'passed':True,'checks':result.strip(),'app_instructions_executed':False,
 'sources':{s.name:native.sha(s) for s in sources},'device_accessed':False,
 'limitations':['Host App entries','Second package is metadata fixture','Journal selection not connected']})
print(result,end='')
