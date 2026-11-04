"""Cross-check canonical AMF3 writer with the production parser and APX2 preflight."""
import argparse,importlib.util,json,subprocess
from pathlib import Path
import apx2
import native_build_0041 as native
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
p.add_argument('--package',type=Path,required=True);p.add_argument('--tool-prefix',required=True);a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
spec=importlib.util.spec_from_file_location('manifest',Path(__file__).with_name('app-manifest-v3.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
real=a.package.resolve();blob=real.read_bytes();info=module.package_info(blob)
# A metadata-only second package; not the D2 independently executing peer App.
peer=a.out.resolve()/'manifest-peer.apx2'
peer.write_bytes(apx2.package(bytes(16),dict(abi_major=3,app_id='z_probe',version='1',text_bytes=16,
 ro_offset=16,ro_bytes=0,data_offset=16,data_bytes=0,bss_bytes=0,heap_bytes=128,stack_bytes=256,
 entries=[0,2,4],data_read_min=1,data_read_max=1,data_write_version=1,required_services=0,fixups=[])))
config={'sequence':9,'apps':[
 {'package':str(real),'order':0,'tcp':18081,'udp':8767,'tasks':2,'pages':8,'requires':{}},
 {'package':str(peer),'order':1,'tcp':0,'udp':0,'tasks':1,'pages':1,'requires':{info['app_id']:blob[192:224].hex()}}]}
manifest=module.manifest(config,a.out);path=a.out/'two-apps.amf3';path.write_bytes(manifest)
assert module.manifest(dict(sequence=9,apps=list(reversed(config['apps']))),a.out)==manifest
empty=module.manifest(dict(sequence=1,apps=[]),a.out);assert len(empty)==64
names=['app_manifest_v3.cpp','app_set_boot_v3.cpp','app_boot_v3.cpp','apx2.cpp','native_sha256_0041.cpp','test_app_manifest_v3.cpp']
binary=a.out.resolve()/'test-app-manifest-v3';report=a.out/'manifest-report.json'
native.write_json(report,{'passed':False})
subprocess.run(['clang++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-g',
 *[str(native.MODULES/n) for n in names],'-o',str(binary)],check=True)
result=subprocess.check_output([str(binary),str(path.resolve()),str(real),str(peer)],text=True,timeout=30)
obj=a.out/'app-manifest-v3.rv32.o'
for name in names[:3]:
 subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror','-c',str(native.MODULES/name),'-o',str(a.out/(name+'.rv32.o'))],check=True)
obj=a.out/(names[0]+'.rv32.o')
native.write_json(report,{'passed':True,'checks':result.strip(),'real_package_sha256':native.sha(real),
 'manifest_digest':manifest[32:64].hex(),'manifest_bytes':len(manifest),'rv32_object_sha256':native.sha(obj),
 'sources':{n:native.sha(native.MODULES/n) for n in names},'app_instructions_executed':False,
 'limitations':['Second package is a metadata fixture','Native multi-App platform not yet connected']})
print(result,end='')
