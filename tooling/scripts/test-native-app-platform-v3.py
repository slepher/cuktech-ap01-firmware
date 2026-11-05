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
registry_test=a.out.resolve()/'test-screen-host-v3'
subprocess.run(['clang','-std=c11','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
               str(native.MODULES/'test_screen_host_0041.c'),str(host),'-o',str(registry_test)],check=True)
result+=subprocess.check_output([str(registry_test)],text=True,timeout=30)
sources.extend([native.MODULES/'screen_host_0041.c',native.MODULES/'test_screen_host_0041.c'])
io_test=a.out.resolve()/'test-native-io-0041'
subprocess.run(['clang++','-std=c++17','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
               str(native.MODULES/'test_native_io_0041.cpp'),'-o',str(io_test)],check=True)
result+=subprocess.check_output([str(io_test)],text=True,timeout=30)
sources.extend(native.MODULES/n for n in ('test_native_io_0041.cpp','native_io_0041.cpp','native_io_0041.h'))
http_test=a.out.resolve()/'test-native-http-workspace-0041'
http_sources=[native.MODULES/n for n in ('test_native_http_workspace_0041.cpp','native_http_transport_0041.cpp')]
subprocess.run(['clang++','-std=c++17','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
               *map(str,http_sources),'-o',str(http_test)],check=True)
result+=subprocess.check_output([str(http_test)],text=True,timeout=30)
sources.extend(http_sources+[native.MODULES/'native_http_transport_0041.h'])
json_test=a.out.resolve()/'test-native-json-reply-0041'
subprocess.run(['clang++','-std=c++17','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
               '-DARDUINOJSON_ENABLE_ARDUINO_STRING=1','-DARDUINOJSON_ENABLE_STD_STRING=0',
               '-DARDUINOJSON_ENABLE_STD_STREAM=0','-I'+str(native.MODULES),
               '-I'+str(native.ROOT/'tooling/vendor/ArduinoJson/src'),
               str(native.MODULES/'test_native_json_reply_0041.cpp'),'-o',str(json_test)],check=True)
result+=subprocess.check_output([str(json_test)],text=True,timeout=30)
sources.extend(native.MODULES/n for n in ('test_native_json_reply_0041.cpp','native_json_0041.h','native_string_0041.h'))
native.write_json(report,{'passed':True,'checks':result.strip(),'package_sha256':native.sha(a.package),
                          'app_instructions_executed':False,'device_accessed':False,
                          'sources':{s.name:native.sha(s) for s in sources},
                          'substitutes':['App entries','native maintenance listener','ROM I/O/LVGL/threads']})
print(result,end='')
