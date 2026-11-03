"""Exercise the App update HTTP routes through real parsing and maintenance authentication."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--package',type=Path,required=True,help='golden.apx2 from test-apx2.py')
p.add_argument('--tool-prefix')
a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
m=Path(__file__).resolve().parents[1]/'firmware-modules'
names=['app_heap_0041.cpp','app_network_0041.cpp','app_core_0041.cpp','app_files_0041.cpp','app_http_0041.cpp','app_installer_0041.cpp','app_runner_0041.cpp','app_image_0041.cpp','app_lifecycle_0041.cpp','app_download_0041.cpp','native_maintenance_0041.cpp','native_http_transport_0041.cpp','native_firmware_0041.cpp','native_wifi_profiles_0041.cpp','native_diagnostic_0041.cpp','app_selection_0041.cpp','app_update_record_0041.cpp','apx2.cpp','native_sha256_0041.cpp','test_app_http_0041.cpp']
binary=a.out.resolve()/'test-http'
report_path=a.out/'http-report.json';report_path.write_text('{"passed":false}\n')
ota=a.out.resolve()/'ota.o'
subprocess.run(['clang','-std=c11','-fsanitize=address,undefined','-c',str(m/'native_ota_image_0041.c'),'-o',str(ota)],check=True)
subprocess.run(['clang++','-std=c++17','-g',
                '-fsanitize=address,undefined','-DARDUINOJSON_ENABLE_ARDUINO_STRING=1','-DARDUINOJSON_ENABLE_STD_STRING=0','-DARDUINOJSON_ENABLE_STD_STREAM=0','-I'+str(m),'-I'+str(m.parent/'vendor/ArduinoJson/src'),*[str(m/n) for n in names],str(ota),'-o',str(binary)],check=True)
with tempfile.TemporaryDirectory(prefix='http-',dir=a.out.resolve()) as state:
    result=subprocess.check_output([str(binary),state,str(a.package.resolve())],text=True,timeout=120)
report={'passed':True,'checks':result.strip(),'device_accessed':False,
        'sources':{n:hashlib.sha256((m/n).read_bytes()).hexdigest() for n in names+['app_services_0041.h','app_core_abi_v2.h','app_file_abi_v2.h','app_image_0041.h','app_runner_0041.h']}}
if a.tool_prefix:
    import native_build_0041 as native
    obj=a.out.resolve()/'http.rv32.o'
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror',
                    '-DARDUINOJSON_ENABLE_ARDUINO_STRING=1','-I'+str(m),'-I'+str(m.parent/'vendor/ArduinoJson/src'),'-c',str(m/'app_http_0041.cpp'),'-o',str(obj)],check=True)
    report['rv32_object_sha256']=hashlib.sha256(obj.read_bytes()).hexdigest()
report_path.write_text(json.dumps(report,indent=2)+'\n');print(result,end='')
