"""Compile actual codex_status App sources and verify read-only trial startup."""
import argparse,json,hashlib,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
p.add_argument('--direct-files',action='store_true',help='Exercise real App through direct scoped file and network tables')
p.add_argument('--tool-prefix',help='Also compile the direct resident adapters for RV32')
a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
firmware=Path(__file__).resolve().parents[2];app=firmware.parent/'codex_status';m=firmware/'tooling/firmware-modules'
source=json.loads((app/'tools/test-bridge/templates/codex-status-ap01.json').read_text())
bundle=dict(job_id='readonly-test',firmware_target='cuktech-ap01-0041',render_target='lcd-jd9853-320x240-palette4',compiler_abi=2,
            profile=dict(template_ids=[source['id']],initial_active_id=source['id']),templates=[dict(key=dict(template_id=source['id'],render_target=source['render_target']),source=source)],fonts=[])
payload=a.out.resolve()/'bundle.json';payload.write_text(json.dumps(bundle))
names=['template_engine.cpp','GUI_Paint.cpp','font_asset.cpp','bundle_store.cpp','bundle_payload.cpp','v2_runtime.cpp','v2_data_command.cpp','v2_bundle_command.cpp','v2_activate_command.cpp','v2_command_envelope.cpp','v2_status_snapshot.cpp','ap01_binding.cpp','ap01_pairing.cpp','sha256.cpp']+['font'+str(n)+'.cpp' for n in (8,12,16,20,24)]
sources=[app/'src'/s for s in names]+[app/'ports/ap01/business.cpp',app/'ports/ap01/application.cpp',app/'ports/ap01/http.cpp',m/'native_http_transport_0041.cpp',m/'native_calendar_0041.cpp',m/'app_files_0041.cpp',m/'app_core_0041.cpp',m/'app_network_0041.cpp',m/'app_heap_0041.cpp',m/'test_app_readonly_0041.cpp']
sources.append(m/'app_files_v3.cpp')
if a.direct_files:
    sources=[s for s in sources if s.name not in ('app_files_0041.cpp','app_core_0041.cpp','app_network_0041.cpp','app_heap_0041.cpp')]
    sources.append(m/'app_network_v3.cpp')
flags=['-std=c++17','-O1','-g','-fsanitize=address,undefined','-DCODEX_AP01_NATIVE=1','-DCODEX_RENDER_NOTE4_FONTS=1','-DARDUINOJSON_ENABLE_ARDUINO_STRING=1','-DARDUINOJSON_ENABLE_STD_STRING=0','-DARDUINOJSON_ENABLE_STD_STREAM=0','-Wno-deprecated-declarations']
if a.direct_files:flags+=['-DAP01_TEST_DIRECT_FILES=1']
for folder in (app/'ports/ap01',app/'src',app/'bridge/crates/render/shim',m,firmware/'tooling/vendor/ArduinoJson/src'):flags+=['-I'+str(folder)]
stem='readonly-direct' if a.direct_files else 'readonly'
report=a.out/(stem+'-report.json');report.write_text('{"passed":false}\n');binary=a.out.resolve()/('test-'+stem)
subprocess.run(['clang++',*flags,*map(str,sources),'-o',str(binary)],check=True)
with tempfile.TemporaryDirectory(prefix='readonly-',dir=a.out.resolve()) as state:
    result=subprocess.check_output([str(binary),state,str(payload)],text=True,timeout=60)
dependencies=sources+[m/n for n in ('app_vfs_client_v2.h','app_file_abi_v2.h','app_files_0041.h','app_generation_0041.h','app_abi_v2.h','native_filesystem_0041.h','app_network_client_v2.h','app_network_abi_v2.h','app_services_0041.h','app_core_abi_v2.h')]
dependencies += [m/'native_vfs_api_0041.h',m/'app_files_v3.h']
if a.direct_files:dependencies += [m/n for n in ('app_network_v3.h','app_network_api_v3.h','app_network_client_v3.h')]
evidence=dict(passed=True,checks=result.strip(),device_accessed=False,
              direct_file_network_tables=a.direct_files,
              sources={str(s.relative_to(s.parent.parent)):hashlib.sha256(s.read_bytes()).hexdigest() for s in dependencies})
if a.direct_files:
    symbols=subprocess.check_output(['nm','-C',str(binary)],text=True)
    for name in ('Ap01AppCore0041::invoke','Ap01AppFiles0041::invoke','Ap01AppNetwork0041::invoke','Ap01AppHeap0041::invoke'):
        assert name not in symbols,('legacy invoke linked into direct path',name)
    evidence['legacy_invoke_linked']=False
if a.tool_prefix:
    import native_build_0041 as native
    evidence['rv32_adapters']=[]
    for name in ('app_files_v3','app_network_v3'):
        obj=a.out.resolve()/(name+'.rv32.o')
        subprocess.run([a.tool_prefix+'g++',*native.FLAGS,'-Wall','-Wextra','-Werror',
                        '-c',str(m/(name+'.cpp')),'-o',str(obj)],check=True)
        evidence['rv32_adapters'].append(dict(object=obj.name,sha256=hashlib.sha256(obj.read_bytes()).hexdigest(),
                                              stack_usage=obj.with_suffix('.su').read_text()))
report.write_text(json.dumps(evidence,indent=2)+'\n');print(result,end='')
