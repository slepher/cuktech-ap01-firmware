"""WSL/Linux host checks of production Wi-Fi core and native adapter API contracts.
Caller precreates --out; no device/network access or App linkage.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess
parser=argparse.ArgumentParser()
parser.add_argument('--app-repo',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
a=parser.parse_args();out=a.out.resolve();assert out.is_dir(),'Precreate output directory with elevation'
modules=Path(__file__).resolve().parents[1]/'firmware-modules'
app=a.app_repo.resolve();json_headers=app/'.pio/libdeps/esp32-s3-epaper-154g/ArduinoJson/src'
assert (json_headers/'ArduinoJson.h').is_file()
flags=['g++','-std=c++17','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
for path in (modules,json_headers,app/'bridge/crates/render/shim'):flags+=['-I',str(path)]
report={'passed':False,'scope':'production core and native adapter with explicit ROM/PSM/VFS fixtures, no RF/App/device','cases':[]}
path=out/'wifi-host-report.json';path.write_text(json.dumps(report),encoding='utf-8')
for name in ('test_native_wifi_switch_0041','test_native_wifi_switch_port_0041','test_native_diagnostic_0041'):
    sources=[modules/x for x in (('native_diagnostic_0041.cpp',name+'.cpp') if name=='test_native_diagnostic_0041' else ('native_wifi_profiles_0041.cpp','native_wifi_switch_0041.cpp',name+'.cpp'))]
    binary=out/name
    subprocess.run(flags+[str(p) for p in sources]+['-o',str(binary)],check=True)
    result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=60)
    (out/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
    assert result.returncode==0,result.stderr
    report['cases'].append({'name':name,'passed':True,'checks':result.stdout.strip(),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()})
inputs=[modules/n for n in ('native_wifi_switch_0041.cpp','native_wifi_switch_0041.h','native_wifi_switch_port_0041.cpp','native_wifi_profiles_0041.cpp','native_wifi_profiles_0041.h','test_native_wifi_switch_0041.cpp','test_native_wifi_switch_port_0041.cpp','native_diagnostic_0041.cpp','native_diagnostic_0041.h','native_wifi_trace_0041.h','test_native_diagnostic_0041.cpp')]
report['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
report['passed']=True;report['device_accessed']=False;path.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'report':str(path)}))
