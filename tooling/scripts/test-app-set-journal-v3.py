"""Fault-inject the AUT3 collection journal; storage durability is a port contract."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--tool-prefix')
p.add_argument('--package',type=Path,required=True)
p.add_argument('--manifest',type=Path,required=True)
p.add_argument('--peer',type=Path,required=True)
a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
m=Path(__file__).resolve().parents[1]/'firmware-modules'
sources=[m/'app_set_journal_v3.cpp',m/'test_app_set_journal_v3.cpp',m/'app_set_selection_v3.cpp',m/'app_set_download_v3.cpp',m/'app_set_commit_v3.cpp',m/'app_set_begin_v3.cpp',m/'app_set_cleanup_v3.cpp',m/'app_set_http_v3.cpp',m/'app_set_service_v3.cpp',m/'app_set_files_v3.cpp',m/'app_manifest_v3.cpp',m/'apx2.cpp',m/'native_sha256_0041.cpp']
sources += [m/name for name in ('native_maintenance_0041.cpp','native_firmware_0041.cpp',
    'native_wifi_profiles_0041.cpp','native_diagnostic_0041.cpp','native_http_transport_0041.cpp')]
json_flags=['-I'+str(m),'-I'+str(m.parent/'vendor/ArduinoJson/src'),'-DARDUINOJSON_ENABLE_STD_STRING=0',
            '-DARDUINOJSON_ENABLE_STD_STREAM=0','-DARDUINOJSON_ENABLE_ARDUINO_STRING=1']
binary=a.out.resolve()/'test-set-journal-v3'
report_path=a.out/'set-journal-v3-report.json'
report_path.write_text(json.dumps({'passed':False,'stage':'building'})+'\n')
ota=m/'native_ota_image_0041.c'
ota_object=a.out.resolve()/'set-http-ota.o'
subprocess.run(['clang','-std=c11','-g','-fsanitize=address,undefined','-c',str(ota),'-o',str(ota_object)],check=True)
subprocess.run(['clang++','-std=c++17','-Wall','-Wextra','-Werror','-g',
                '-fsanitize=address,undefined',*json_flags,*map(str,sources),str(ota_object),'-o',str(binary)],check=True)
result=subprocess.check_output([str(binary),str(a.package.resolve()),str(a.manifest.resolve()),str(a.peer.resolve())],text=True,timeout=30)
report={'passed':True,'checks':result.strip(),'device_accessed':False,
        'peer_sha256':hashlib.sha256(a.peer.read_bytes()).hexdigest(),
        'manifest_sha256':hashlib.sha256(a.manifest.read_bytes()).hexdigest(),
        'package_sha256':hashlib.sha256(a.package.read_bytes()).hexdigest(),
        'http_transport_service_integrated':True,'storage_durability_verified':False,'boot_selection_integrated':False,
        'sources':{s.name:hashlib.sha256(s.read_bytes()).hexdigest() for s in sources+[ota,m/'app_set_service_v3.h',m/'app_set_journal_v3.h',m/'app_set_selection_v3.h',m/'app_reboot_v3.h',m/'app_set_download_v3.h',m/'app_set_commit_v3.h',m/'app_set_begin_v3.h',m/'app_set_cleanup_v3.h',m/'app_set_http_v3.h',m/'app_write_gate_v3.h',m/'app_manifest_v3.h',m/'native_vfs_api_0041.h',m/'native_integrity_0041.h']}}
if a.tool_prefix:
    import native_build_0041 as native
    obj=a.out.resolve()/'set-journal-v3.rv32.o'
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror',
                    '-c',str(sources[0]),'-o',str(obj)],check=True)
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror',
                    '-c',str(m/'app_set_selection_v3.cpp'),'-o',str(a.out/'set-selection-v3.rv32.o')],check=True)
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror',
                    '-c',str(m/'app_set_download_v3.cpp'),'-o',str(a.out/'set-download-v3.rv32.o')],check=True)
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror',
                    '-c',str(m/'app_set_commit_v3.cpp'),'-o',str(a.out/'set-commit-v3.rv32.o')],check=True)
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror',
                    '-c',str(m/'app_set_begin_v3.cpp'),'-o',str(a.out/'set-begin-v3.rv32.o')],check=True)
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror',
                    '-c',str(m/'app_set_cleanup_v3.cpp'),'-o',str(a.out/'set-cleanup-v3.rv32.o')],check=True)
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror',
                    '-c',str(m/'app_set_http_v3.cpp'),'-o',str(a.out/'set-http-v3.rv32.o')],check=True)
    subprocess.run([a.tool_prefix+'g++',*native.FLAGS,*json_flags,'-Wall','-Wextra','-Werror',
                    '-c',str(m/'app_set_service_v3.cpp'),'-o',str(a.out/'set-service-v3.rv32.o')],check=True)
    report['rv32_object_sha256']=hashlib.sha256(obj.read_bytes()).hexdigest()
report_path.write_text(json.dumps(report,indent=2)+'\n')
print(result,end='')
