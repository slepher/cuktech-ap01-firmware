"""Reconstruct a complete 0041 candidate, preserving every stock resource.
An unverified candidate remains flashable=false. No tool here contacts hardware.
"""
from pathlib import Path
import argparse,hashlib,json,struct,subprocess,zlib,shutil
from rom_target import load_target, profile_identity, validate_original
from importlib.util import spec_from_file_location,module_from_spec
_spec=spec_from_file_location('ap01_native_build',Path(__file__).with_name('native_build_0041.py'))
_native=module_from_spec(_spec);_spec.loader.exec_module(_native)
ROOT=Path(__file__).resolve().parents[2]
BASE=0x9ffff000
OFFSET=0x675000
HOOK=0x5e180
TIMER_DELETE=0x8be58
ORIGINAL_SHA='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
FORMAT='ap01-native-app-0041-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
# AP01MNU1: optional, exact-stock Settings call-site table in spare manifest.
MENU_HOOKS = {0xb262c:(8,'efc08f0281460546'),
              0xb263a:(8,'efc0af0181462d46'),
              0xb2648:(8,'efc0cf00b7450fa0'),
              0xb2754:(10,'ef10ef4a814523a4a900')}
def menu_hooks(payload,rom_target='0041'):
    profile=load_target(rom_target)
    expected={r['offset']:(len(bytes.fromhex(r['original_hex'])),r['original_hex']) for r in profile['menu_hooks']}
    base=profile['mapping_base'];offset_base=profile['payload_offset']
    if payload[192:200] != b'AP01MNU1':
        if any(payload[192:256]):raise ValueError('unknown spare manifest data')
        return []
    if struct.unpack_from('<I',payload,200)[0] != 4:raise ValueError('menu hook count')
    records=[struct.unpack_from('<3I',payload,204+12*i) for i in range(4)]
    if {r[0] for r in records} != set(expected):raise ValueError('menu hook offsets')
    for offset,target,span in records:
        if span != expected[offset][0] or target&1 or not base+offset_base+256 <= target < base+offset_base+len(payload):
            raise ValueError('menu hook bounds')
    if any(payload[252:256]):raise ValueError('menu hook reserved bytes')
    return records

def call(target,site=HOOK,base=BASE):
    delta=target-(base+site)
    hi=(delta+0x800)>>12;lo=delta-(hi<<12)
    return struct.pack('<II',((hi&0xfffff)<<12)|(1<<7)|0x17,((lo&0xfff)<<20)|(1<<15)|(1<<7)|0x67)
def jump(target,site):
    delta=target-site;hi=(delta+0x800)>>12;lo=delta-(hi<<12)
    return struct.pack('<II',((hi&0xfffff)<<12)|(5<<7)|0x17,((lo&0xfff)<<20)|(5<<15)|0x67)

def assemble(original,payload,entry,unsigned_ota=False,timer_guard=None,rom_target='0041'):
    profile=load_target(rom_target);validate_original(profile,original)
    base=profile['mapping_base'];offset_base=profile['payload_offset']
    hook=profile['ui_hook']['offset'];timer_delete=profile['timer_delete']['offset']
    expected_menu={r['offset']:r for r in profile['menu_hooks']}
    if payload[:8]!=b'AP01APP1' or len(payload)<=256 or entry&1 or not base+offset_base+256<=entry<base+offset_base+len(payload):raise ValueError('native payload/entry')
    length=((offset_base+len(payload)+15)&~15)+40
    if length>0x700000:raise ValueError('FW slot capacity')
    out=bytearray(original[:-40]);out.extend(b'\xff'*(length-len(out)))
    out[offset_base:offset_base+len(payload)]=payload
    out[hook:hook+8]=call(entry,hook,base)
    stock=bytearray(original)
    stock[hook:hook+8]=out[hook:hook+8]
    for offset,target,span in menu_hooks(payload,rom_target):
        if original[offset:offset+span]!=bytes.fromhex(expected_menu[offset]['original_hex']):raise ValueError("menu stock callsite mismatch")
        patch=call(target,offset,base)+(b"\x01\x00" if span==10 else b"")
        out[offset:offset+span]=patch;stock[offset:offset+span]=patch
    if timer_guard is not None:
        if not base+offset_base+256<=timer_guard<base+offset_base+len(payload) or timer_guard&1:raise ValueError('timer guard bounds')
        if original[timer_delete:timer_delete+8]!=bytes.fromhex(profile['timer_delete']['original_hex']):raise ValueError('timer delete prologue mismatch')
        out[timer_delete:timer_delete+8]=jump(timer_guard,base+timer_delete)
        stock[timer_delete:timer_delete+8]=out[timer_delete:timer_delete+8]
    if unsigned_ota:
        ota=profile['unsigned_ota'];at=ota['offset']
        if stock[at:at+2]!=bytes.fromhex(ota['original_hex']):raise ValueError('unsigned OTA branch mismatch')
        stock[at:at+2]=bytes.fromhex(ota['replacement_hex'])
        out[at:at+2]=stock[at:at+2]
    out[-40:]=original[-40:]
    struct.pack_into('>I',out,length-8,length)
    struct.pack_into('<I',out,length-4,zlib.crc32(out[:-4],0xffffffff)^0xffffffff)
    if out[:0x1000]!=original[:0x1000]:raise ValueError('boot/header region changed')
    if out[:len(original)-40]!=stock[:-40]:raise ValueError('unexpected stock byte modification')
    if unsigned_ota:
        tag=b'0x5245434f56455259544147';positions=[];at=0
        while (at:=out.find(tag,at))>=0:positions.append(at);at+=1
        if len(positions)!=2 or positions[1]!=length-40:raise ValueError('native recovery marker ambiguity')
    return bytes(out)
def validate_candidate(data,manifest_path):
    m=json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    rom_target=m.get('rom_target','0041');profile=load_target(rom_target)
    if m['format']!=f'ap01-native-app-{rom_target}-v1' or m['firmware_target']!=f'cuktech-ap01-{rom_target}':raise ValueError('manifest format/target')
    if rom_target!='0041' and m.get('target_profile_sha256')!=profile_identity(rom_target):raise ValueError('ROM profile changed')
    original=Path(m['original']['path']).read_bytes();payload=Path(m['payload']['path']).read_bytes()
    if sha(payload)!=m['payload']['sha256']:raise ValueError('payload identity')
    h=bytearray(payload[:256]);stored=struct.unpack_from('<I',h,32)[0];struct.pack_into('<I',h,32,0)
    if zlib.crc32(h)!=stored or struct.unpack_from('<I',h,28)[0]!=zlib.crc32(payload[256:]):raise ValueError('payload checksums')
    if struct.unpack_from('<4I',h,8)!=(1,len(data),profile['payload_offset'],len(payload)):raise ValueError('payload bounds')
    entry=struct.unpack_from('<I',h,24)[0]
    if data!=assemble(original,payload,entry,m.get('unsigned_ota',False),int(m['timer_delete_guard']['entry'],16) if m.get('timer_delete_guard') else None,rom_target) or sha(data)!=m['image']['sha256']:raise ValueError('candidate reconstruction mismatch')
    return m
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--original',type=Path);p.add_argument('--tool-prefix',required=True);p.add_argument('--target',choices=('0041','0055'),default='0041');a=p.parse_args()
    profile=load_target(a.target);base=profile['mapping_base'];offset_base=profile['payload_offset']
    output=a.output.resolve();out=a.source_dir.resolve()
    if not output.parent.is_dir():p.error('precreate output directory with elevation')
    original_path=(a.original or ROOT/profile['original']['path']).resolve()
    original=original_path.read_bytes();payload=bytearray((out/'ap01-native-0041.module.bin').read_bytes())
    linked=json.loads((out/'native-link-report.json').read_text(encoding='utf-8'))
    audit=_native.validate_audit(out)
    if audit.get('rom_target','0041')!=a.target: p.error('compiled objects target differs from packaging target')
    if not linked.get('linked') or sha(payload)!=linked.get('module_sha256') or sha((out/'native-core-audit.json').read_bytes())!=linked.get('audit_sha256'):
        p.error('current module/audit/link fingerprints do not agree')
    if sha((out/'ap01-native-0041.elf').read_bytes())!=linked['elf']['sha256']:
        p.error('linked ELF changed: rerun link')
    if 'linker_script' in linked and sha(Path(linked['linker_script']['path']).read_bytes())!=linked['linker_script']['sha256']:
        p.error('linker script changed: rerun link')
    if payload[:256]!=bytes(256):p.error('linked module must have a zero manifest')
    tool=a.tool_prefix
    nm=str(tool)+'nm';nm=nm+'.exe' if not Path(nm).is_file() and Path(nm+'.exe').is_file() else nm
    objcopy=str(tool)+'objcopy';objcopy=objcopy+'.exe' if not Path(objcopy).is_file() and Path(objcopy+'.exe').is_file() else objcopy
    listing=subprocess.check_output([nm,'-n',str(out/'ap01-native-0041.elf')],text=True)
    symbols={line.split()[2]:int(line.split()[0],16) for line in listing.splitlines() if len(line.split())==3 and line.split()[0]!='U'}
    entry=symbols['ap01Register0041'];assert symbols['ap01_native_manifest']==base+offset_base
    abi_file=out/'native-runtime-abi.bin'
    subprocess.run([objcopy,'-O','binary','--only-section=.abi',str(out/'ap01-native-0041.elf'),str(abi_file)],check=True)
    abi_raw=abi_file.read_bytes();abi=struct.unpack('<'+str(len(abi_raw)//4)+'I',abi_raw)
    if not ((len(abi)==23 and abi[0]==1) or (len(abi)==4 and abi[0] in (2,3))):
        p.error('unsupported runtime ABI (expected App ABI 1 or platform diagnostics ABI 2/3)')
    if abi[0] in (2,3):
        runtime_metadata={'runtime':'platform','applications':[],
            'platform_abi':{'version':2,'runtime_bytes':abi[1],'window_offset':abi[2],'heartbeat_offset':abi[3]}}
        if abi[0]==3:
            runtime_metadata['platform_abi']={'version':3,'context_bytes':abi[1],'shared_pointer_offset':abi[2],'shared_owner_bytes':abi[3]}
        if audit.get('boot_app_v3'):
            runtime_metadata['app_loader']={'abi_major':3,'manifest_path':'/resource/app-store/manifests/<content-digest>.amf3',
                'package_path':'/resource/app-store/packages/<content-digest>.apx2','staging_bytes':1<<22,
                'file_io_executor':'worker','app_start_executor':'ui','journal_selection':True,
                'maintenance_before_app':True,'hardware_backend':'rom-heap-retained-ram','cache_publish':a.target+'-dcache-clean-icache-invalidate-fence-i','executable_backend_verified':False}
    else:
        runtime_metadata={'runtime':'application',
            'screen_host':{'abi':1,'roots_per_template':True,'timer_context_direct':True,'host_offset':abi[17],'phase_offset':abi[18],'slot_bytes':abi[19],'slot_root_offset':abi[20],'slot_child_offset':abi[21],'slots_offset':abi[22],'template_capacity':8},
            'native_abi':{'calendar':hex(symbols['_Z12ap01CalendarlR2tm']),'wall_time':hex(symbols['time']),
                'ui_timer':hex(symbols['_ZN12_GLOBAL__N_17Runtime5timerEPv']),
                'ui_event':hex(symbols['_ZN12_GLOBAL__N_17Runtime13eventCallbackEPvS1_']),
                'lv_obj_send_event':'0xa00d831a',
                'instance_bytes':dict(zip(('runtime','business','bundle_store','application'),abi[1:5])),
                'runtime_offsets':dict(zip(('root','content','dialog','image','pairPending','pairWoken','focused','shownGeneration','templateCount','retired','ready','uiStage'),abi[5:17]))}}
    length=((offset_base+len(payload)+15)&~15)+40
    h=bytearray(256);h[:8]=b'AP01APP1';struct.pack_into('<7I',h,8,1,length,offset_base,len(payload),entry,zlib.crc32(payload[256:]),0)
    h[36:52]=hashlib.sha256(payload[256:]).digest()[:16];struct.pack_into('<3I',h,52,7,18080,18081)
    target_name=f'cuktech-ap01-{a.target}'.encode();h[64:64+len(target_name)]=target_name
    h[96:96+len(b'lcd-jd9853-320x240-palette4')]=b'lcd-jd9853-320x240-palette4'
    h[128:160]=bytes.fromhex(profile['original']['sha256'])
    h[160:192]=hashlib.sha256((out/'native-core-audit.json').read_bytes()).digest()
    h[192:200]=b'AP01MNU1';struct.pack_into('<I',h,200,4)
    settings_hooks=[(r['offset'],len(bytes.fromhex(r['original_hex'])),r['symbol']) for r in profile['menu_hooks']]
    for i,(offset,span,name) in enumerate(settings_hooks):struct.pack_into('<3I',h,204+12*i,offset,symbols[name],span)
    struct.pack_into('<I',h,32,zlib.crc32(h));payload[:256]=h
    image=assemble(original,bytes(payload),entry,True,symbols['ap01TimerDelete0041'],a.target)
    payload_path=output.with_suffix('.payload.bin');manifest_path=output.with_suffix('.manifest.json')
    elf_path=output.with_suffix('.elf');audit_path=output.with_suffix('.audit.json');link_path=output.with_suffix('.link.json');map_path=output.with_suffix('.map')
    if any(path.exists() for path in (output,payload_path,manifest_path,elf_path,audit_path,link_path,map_path)):p.error('candidate outputs must be new files')
    for source,destination in ((out/'ap01-native-0041.elf',elf_path),(out/'ap01-native-0041.map',map_path),
                               (out/'native-core-audit.json',audit_path),(out/'native-link-report.json',link_path)):
        shutil.copyfile(source,destination)
    payload_path.write_bytes(payload);output.write_bytes(image)
    manifest={'format':f'ap01-native-app-{a.target}-v1','firmware_target':target_name.decode(),'build_id':h[36:52].hex(),
        'rom_target':a.target,'target_profile_sha256':profile_identity(a.target),
        'rom_versions':audit.get('rom_versions'), 'supports_app':bool(audit.get('boot_app_v3')),
        'flashable':False,'hardware_verified':False,'simulator_verified':False,'unsigned_ota':True,
        'native_recovery_compatible':True,'recovery_marker_count':2,
        'timer_delete_guard':{'entry':hex(symbols['ap01TimerDelete0041']),'offset':hex(profile['timer_delete']['offset']),'bytes':8,'null_is_noop':True,'nonnull_tail':hex(profile['timer_delete']['nonnull_tail'])},
        'original':{'path':str(original_path.resolve()),'sha256':profile['original']['sha256'],'bytes':len(original)},
        'payload':{'path':str(payload_path),'sha256':sha(payload),'bytes':len(payload),'entry':hex(entry)},
        'elf':{'path':str(elf_path),'sha256':sha(elf_path.read_bytes()),'bytes':elf_path.stat().st_size},
        'audit':{'path':str(audit_path),'sha256':sha(audit_path.read_bytes())},
        'link':{'path':str(link_path),'sha256':sha(link_path.read_bytes())},
        **runtime_metadata,
        'settings_menu_hooks':[{'offset':hex(offset),'target':hex(target),'span':span,'original_hex':next(r['original_hex'] for r in profile['menu_hooks'] if r['offset']==offset)} for offset,target,span in menu_hooks(payload,a.target)],
        'image':{'path':str(output),'sha256':sha(image),'bytes':len(image)},
        'preserved':['boot header/entry','original ROMFS and rcS','all five pet GIFs','all original bytes outside UI hook, NULL-safe timer-delete hook, four pinned Settings calls and unsigned OTA branch'],
        'limitations':['native application/update/recovery/resource acceptance pending',f'physical BSP/LCD and first {a.target} hardware boot unverified']}
    if 'ap01HostProbe0041' in symbols:manifest['screen_host_probe']={'entry':hex(symbols['ap01HostProbe0041']),'original_window_replay':True}
    manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    validate_candidate(image,manifest_path)
    print(json.dumps(manifest['image']))
if __name__=='__main__':main()
