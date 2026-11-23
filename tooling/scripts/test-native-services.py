"""Run ABI 3 service ownership and independent maintenance routing; no device I/O."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--rom',type=Path,help='Also run the existing independent maintenance regression')
a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
root=Path(__file__).resolve().parents[2]
modules=root/'tooling/firmware-modules'
sources=['native_maintenance.cpp',
         'native_firmware.cpp','native_wifi_profiles.cpp','native_diagnostic.cpp',
         'native_ota_image.c','native_sha256.cpp']
objects=[]
for name in sources:
    obj=a.out.resolve()/(name+'.o');objects.append(obj)
    subprocess.run(['clang' if name.endswith('.c') else 'clang++',
                    '-std=c11' if name.endswith('.c') else '-std=c++17',
                    '-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',
                    '-I'+str(modules),'-I'+str(root/'tooling/vendor/ArduinoJson/src'),
                    '-DARDUINOJSON_ENABLE_STD_STRING=0','-DARDUINOJSON_ENABLE_STD_STREAM=0',
                    '-DARDUINOJSON_ENABLE_ARDUINO_STRING=1',
                    '-c',str(modules/name),'-o',str(obj)],check=True)
result=''
service_names=['test_native_services.cpp','native_services.cpp',
               'native_wifi_switch.cpp','native_http_transport.cpp','app_files_v3.cpp','app_binding_v3.cpp']
service_objects=[]
for name in service_names:
    obj=a.out.resolve()/(name+'.o');service_objects.append(obj)
    subprocess.run(['clang++','-std=c++17','-g','-fsanitize=address,undefined',
                    '-fno-omit-frame-pointer','-I'+str(modules),
                    '-c',str(modules/name),'-o',str(obj)],check=True)
service_test=a.out.resolve()/'test-native-services'
subprocess.run(['clang++','-fsanitize=address,undefined',*map(str,objects+service_objects),
                '-o',str(service_test)],check=True)
result+=subprocess.check_output([str(service_test)],text=True,timeout=30)
sources.extend(service_names+['app_write_gate_v3.h','app_binding_v3.h','native_app_port.h'])
report={'passed':True,'checks':result.strip(),'device_accessed':False,
        'sources':{name:hashlib.sha256((modules/name).read_bytes()).hexdigest() for name in sources}}
if a.rom:
    extra=[]
    for name in ('test_native_maintenance.cpp','native_http_transport.cpp'):
        obj=a.out.resolve()/(name+'.o');extra.append(obj)
        subprocess.run(['clang++','-std=c++17','-g','-fsanitize=address,undefined',
                        '-DAP01_MAINTENANCE_ONLY_TEST=1',
                        '-DARDUINOJSON_ENABLE_ARDUINO_STRING=1',
                        '-DARDUINOJSON_ENABLE_STD_STRING=0','-DARDUINOJSON_ENABLE_STD_STREAM=0',
                        '-I'+str(modules),'-I'+str(root/'tooling/vendor/ArduinoJson/src'),
                        '-c',str(modules/name),'-o',str(obj)],check=True)
    regression=a.out.resolve()/'test-maintenance-independent'
    subprocess.run(['clang++','-fsanitize=address,undefined',*map(str,objects+extra),
                    '-o',str(regression)],check=True)
    # Host checkout paths can exceed the production VFS's 128-byte path bound.
    # Keep the fixture root short; do not relax the firmware boundary for tests.
    with tempfile.TemporaryDirectory(prefix='ap01-maint-') as state:
        assert len(str(Path(state)/'f21/firmware.pending'))<128
        (Path(state)/'f21').mkdir()
        regression_result=subprocess.check_output([str(regression),state,str(a.rom.resolve())],
                                                 text=True,timeout=120)
    recovery_obj=a.out.resolve()/'test_native_maintenance_recovery.cpp.o'
    subprocess.run(['clang++','-std=c++17','-g','-fsanitize=address,undefined',
                    '-DARDUINOJSON_ENABLE_ARDUINO_STRING=1',
                    '-DARDUINOJSON_ENABLE_STD_STRING=0','-DARDUINOJSON_ENABLE_STD_STREAM=0',
                    '-I'+str(modules),'-I'+str(root/'tooling/vendor/ArduinoJson/src'),
                    '-c',str(modules/'test_native_maintenance_recovery.cpp'),'-o',str(recovery_obj)],check=True)
    recovery=a.out.resolve()/'test-maintenance-recovery'
    subprocess.run(['clang++','-fsanitize=address,undefined',*map(str,objects),
                    str(extra[1]),str(recovery_obj),'-o',str(recovery)],check=True)
    with tempfile.TemporaryDirectory(prefix='ap01-recovery-') as state:
        for n in range(6):(Path(state)/('maintenance-'+str(n))).mkdir()
        recovery_result=subprocess.check_output([str(recovery),state],text=True,timeout=120)
    report['recovery_and_rom_policy']=recovery_result.strip()
    print(recovery_result,end='')
    report['independent_maintenance']=regression_result.strip()
    report['rom_sha256']=hashlib.sha256(a.rom.read_bytes()).hexdigest()
    for name in ('test_native_maintenance.cpp','native_http_transport.cpp',
                 'native_http_transport.h','native_maintenance.h'):
        report['sources'][name]=hashlib.sha256((modules/name).read_bytes()).hexdigest()
    print(regression_result,end='')
(a.out/'native-services-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(result,end='')
