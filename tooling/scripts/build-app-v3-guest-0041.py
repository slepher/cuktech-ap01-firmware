"""Build model-only guest executing an existing real ABI 3 package."""
import argparse,json,subprocess,shutil,struct,zlib
from pathlib import Path
import native_build_0041 as native
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True);p.add_argument('--package',type=Path);p.add_argument('--snapshot',type=Path,help='Exact HTTP commit snapshot; replaces package/manifest/peer inputs');p.add_argument('--tool-prefix',required=True)
p.add_argument('--boot-id',type=int,help='Explicit nonzero modeled boot identity')
p.add_argument('--boot-mode',choices=['trial','fail-trial','rollback','fail-rollback','maintenance','empty-rollback'],default='trial')
p.add_argument('--resume-journals',type=Path,help='Exact journal export from an earlier RV32 guest')
p.add_argument('--manifest',type=Path);p.add_argument('--peer',type=Path)
a=p.parse_args();out=a.out.resolve()
if bool(a.manifest)!=bool(a.peer):p.error('--manifest and --peer must be supplied together')
if not out.is_dir() or any(out.iterdir()):p.error('Precreate empty output directory')
if (a.boot_mode!='trial' or a.resume_journals) and not a.snapshot:p.error('boot modes and journal resume require --snapshot')
rollback=a.boot_mode in ('rollback','fail-rollback','maintenance','empty-rollback')
empty_rollback=a.boot_mode=='empty-rollback'
if rollback!=bool(a.resume_journals):p.error('rollback/maintenance modes require --resume-journals, and trial modes forbid it')
if a.boot_id is not None and not 0<a.boot_id<2**64:p.error('invalid boot identity')
snapshot_hash=None
if a.snapshot:
    if any((a.package,a.manifest,a.peer)):p.error('--snapshot replaces --package/--manifest/--peer')
    from app_set_client_v3 import inspect_manifest,inspect_packages
    snapshot=json.loads(a.snapshot.read_text());snapshot_hash=native.sha(a.snapshot)
    assert snapshot['captured_before_modeled_reboot'] and snapshot['reply']['phase']=='switch_pending'
    files={name:bytes.fromhex(value) for name,value in snapshot['files'].items()}
    slots=[files.get('/resource/app-store/update.'+str(i),b'') for i in range(2)]
    if a.resume_journals:
        saved=a.resume_journals.read_bytes();assert len(saved)==648
        lengths=struct.unpack_from('<II',saved);assert all(n in (0,320) for n in lengths)
        slots=[saved[8+320*i:8+320*i+n] for i,n in enumerate(lengths)]
    for slot in slots:
        assert not slot or (len(slot)==320 and slot[:4]==b'AUT3' and struct.unpack_from('<II',slot,4)==(2,320)
                            and zlib.crc32(slot[:316])==struct.unpack_from('<I',slot,316)[0])
    current=max((slot for slot in slots if slot),key=lambda slot:struct.unpack_from('<Q',slot,16)[0])
    assert struct.unpack_from('<I',current,12)[0]==(9 if a.boot_mode=='maintenance' else 5 if rollback else 3) and current[80:96].hex()==snapshot['operation_id']
    if empty_rollback:assert current[104:136]==bytes(32) and struct.unpack_from('<Q',current,24)[0]==0
    offset=104 if rollback and not empty_rollback else 136
    digest=current[offset:offset+32].hex();manifest=files['/resource/app-store/manifests/'+digest+'.amf3'];parsed=inspect_manifest(manifest)
    assert parsed['digest']==digest and len(parsed['apps'])==2 and parsed['version']==struct.unpack_from('<Q',current,24 if rollback and not empty_rollback else 32)[0]
    packages=[files['/resource/app-store/packages/'+app['digest']+'.apx2'] for app in parsed['apps']]
    assert len(inspect_packages(parsed,packages))==2
    a.package=out/'app.apx2';a.manifest=out/'set.amf3';a.peer=out/'peer.apx2'
    for path,data in [(a.package,packages[0]),(a.peer,packages[1]),(a.manifest,manifest)]:path.write_bytes(data)
    (out/'journals.bin').write_bytes(struct.pack('<II',*(len(slot) for slot in slots))+b''.join(slot.ljust(320,b'\0') for slot in slots))
elif not a.package:p.error('--package or --snapshot is required')
tool=native.tools(a.tool_prefix)
names=['probe_app_v3_guest.cpp','native_app_platform_v3.cpp','app_boot_v3.cpp','app_binding_v3.cpp','app_files_v3.cpp','app_network_v3.cpp','apx2.cpp','native_sha256_0041.cpp','model_platform_v3.cpp','runtime_libc_0041.cpp','app_runtime_format_v2.cpp','screen_host_0041.c']
if a.manifest:names+=['native_app_set_v3.cpp','app_set_boot_v3.cpp','app_manifest_v3.cpp','app_set_files_v3.cpp','native_app_file_boot_v3.cpp','app_supervision_v3.cpp','app_set_journal_v3.cpp','app_set_selection_v3.cpp']
objects=[]
for name in names:
    obj=out/(name+'.o');objects.append(str(obj))
    flags=[f for f in native.FLAGS if not (name.endswith('.c') and f in ('-std=c++17','-fno-rtti','-fno-exceptions'))]
    subprocess.run([tool('gcc' if name.endswith('.c') else 'g++'),*flags,*([f'-DAP01_MODEL_BOOT_ID={a.boot_id}ULL'] if a.boot_id is not None else []),*(['-DAP01_MODEL_SET_V3=1'] if a.manifest else []),*(['-DAP01_MODEL_HTTP_SNAPSHOT=1'] if a.snapshot else []),*(['-DAP01_MODEL_FAIL_WORKER=1'] if a.boot_mode in ('fail-trial','fail-rollback') else []),*(['-DAP01_MODEL_ROLLBACK=1'] if rollback else []),*(['-DAP01_MODEL_MAINTENANCE=1'] if a.boot_mode=='maintenance' else []),*(['-DAP01_MODEL_EMPTY_ROLLBACK=1'] if empty_rollback else []),'-march=rv32imafc_zifencei',*(['-Wno-invalid-offsetof'] if not name.endswith('.c') else []),'-c',str(native.MODULES/name),'-o',str(obj)],check=True)
ld=out/'guest.ld';ld.write_text('''OUTPUT_ARCH(riscv)
ENTRY(guest_entry)
SECTIONS { . = 0xa8100000;
 .text : { KEEP(*(.text.guest_entry)) *(.text .text.*) }
 .rodata : { *(.rodata .rodata.* .srodata*) }
 .data : { *(.data .data.* .sdata*) }
 .bss : { __guest_bss_start = .; *(.bss .bss.* .sbss* COMMON) __guest_bss_end = .; }
 /DISCARD/ : { *(.comment .note* .eh_frame* .riscv.attributes) }
}''')
elf=out/'guest.elf'
subprocess.run([tool('g++'),*native.FLAGS,'-Wl,--no-relax,--gc-sections','-T',str(ld),*objects,'-lgcc','-o',str(elf)],check=True)
assert not subprocess.check_output([tool('nm'),'-u',str(elf)],text=True).strip()
subprocess.run([tool('objcopy'),'-O','binary',str(elf),str(out/'guest.bin')],check=True)
assert (out/'guest.bin').stat().st_size<0x40000
if a.package.resolve()!=out/'app.apx2':shutil.copyfile(a.package,out/'app.apx2')
report={'built':True,'executed':False,'guest_base':0xa8100000,'package_address':0xa8180000,'stop':0x62fc8000,'sp':0xa8180000,'bases':[0xa8000000,0xa8040000],'guest_sha256':native.sha(out/'guest.bin'),'package_sha256':native.sha(out/'app.apx2'),'sources':{n:native.sha(native.MODULES/n) for n in names},'substitutes':['ROM maintenance listener','ROM VFS/network/LVGL','cooperative model threads','bump allocator without reclamation','ROM integer formatter and UTC clock']}
if a.manifest:
    report['collection']=True;report['extra_inputs']=[]
    for source,name,address,bound in [(a.manifest,'set.amf3',0xa81c0000,0x1000),(a.peer,'peer.apx2',0xa81c1000,0x3e000 if a.snapshot else 0x3f000)]:
        assert source.stat().st_size<=bound
        if source.resolve()!=out/name:shutil.copyfile(source,out/name)
        report['extra_inputs'].append({'name':name,'address':address,'sha256':native.sha(out/name)})
    report['sources']['probe_app_set_v3_guest.h']=native.sha(native.MODULES/'probe_app_set_v3_guest.h')
if a.snapshot:
    report['http_snapshot_sha256']=snapshot_hash
    report['boot_mode']=a.boot_mode
    report['journal_export']={'address':0xa81ff000,'size':648}
    report['runtime_export']={'address':0xa81ff300,'size':912}
    report['boot_id']=a.boot_id
    if a.resume_journals:report['resume_journals_sha256']=native.sha(a.resume_journals)
    report['extra_inputs'].append({'name':'journals.bin','address':0xa81ff000,'sha256':native.sha(out/'journals.bin')})
symbols={line.split()[-1]:int(line.split()[0],16) for line in subprocess.check_output([tool('nm'),str(elf)],text=True).splitlines() if len(line.split())==3}
report['guest_bss']={'address':symbols['__guest_bss_start'],'size':symbols['__guest_bss_end']-symbols['__guest_bss_start']}
native.write_json(out/'build-report.json',report);print(json.dumps(report))
