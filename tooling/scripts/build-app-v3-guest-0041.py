"""Build model-only guest executing an existing real ABI 3 package."""
import argparse,json,subprocess,shutil
from pathlib import Path
import native_build_0041 as native
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True);p.add_argument('--package',type=Path,required=True);p.add_argument('--tool-prefix',required=True)
p.add_argument('--manifest',type=Path);p.add_argument('--peer',type=Path)
a=p.parse_args();out=a.out.resolve()
if bool(a.manifest)!=bool(a.peer):p.error('--manifest and --peer must be supplied together')
if not out.is_dir() or any(out.iterdir()):p.error('Precreate empty output directory')
tool=native.tools(a.tool_prefix)
names=['probe_app_v3_guest.cpp','native_app_platform_v3.cpp','app_boot_v3.cpp','app_binding_v3.cpp','app_files_v3.cpp','app_network_v3.cpp','apx2.cpp','native_sha256_0041.cpp','model_platform_v3.cpp','runtime_libc_0041.cpp','app_runtime_format_v2.cpp','screen_host_0041.c']
if a.manifest:names+=['native_app_set_v3.cpp','app_set_boot_v3.cpp','app_manifest_v3.cpp','app_set_files_v3.cpp','native_app_file_boot_v3.cpp','app_supervision_v3.cpp','app_set_journal_v3.cpp','app_set_selection_v3.cpp']
objects=[]
for name in names:
    obj=out/(name+'.o');objects.append(str(obj))
    flags=[f for f in native.FLAGS if not (name.endswith('.c') and f in ('-std=c++17','-fno-rtti','-fno-exceptions'))]
    subprocess.run([tool('gcc' if name.endswith('.c') else 'g++'),*flags,*(['-DAP01_MODEL_SET_V3=1'] if a.manifest else []),'-march=rv32imafc_zifencei',*(['-Wno-invalid-offsetof'] if not name.endswith('.c') else []),'-c',str(native.MODULES/name),'-o',str(obj)],check=True)
ld=out/'guest.ld';ld.write_text('''OUTPUT_ARCH(riscv)
ENTRY(guest_entry)
SECTIONS { . = 0xa8100000;
 .text : { KEEP(*(.text.guest_entry)) *(.text .text.*) }
 .rodata : { *(.rodata .rodata.* .srodata*) }
 .data : { *(.data .data.* .sdata*) }
 .bss : { *(.bss .bss.* .sbss* COMMON) }
 /DISCARD/ : { *(.comment .note* .eh_frame* .riscv.attributes) }
}''')
elf=out/'guest.elf'
subprocess.run([tool('g++'),*native.FLAGS,'-Wl,--no-relax,--gc-sections','-T',str(ld),*objects,'-lgcc','-o',str(elf)],check=True)
assert not subprocess.check_output([tool('nm'),'-u',str(elf)],text=True).strip()
subprocess.run([tool('objcopy'),'-O','binary',str(elf),str(out/'guest.bin')],check=True)
assert (out/'guest.bin').stat().st_size<0x40000
shutil.copyfile(a.package,out/'app.apx2')
report={'built':True,'executed':False,'guest_base':0xa8100000,'package_address':0xa8180000,'stop':0x62fc8000,'sp':0xa8180000,'bases':[0xa8000000,0xa8040000],'guest_sha256':native.sha(out/'guest.bin'),'package_sha256':native.sha(out/'app.apx2'),'sources':{n:native.sha(native.MODULES/n) for n in names},'substitutes':['ROM maintenance listener','ROM VFS/network/LVGL','cooperative model threads','bump allocator without reclamation','ROM integer formatter and UTC clock']}
if a.manifest:
    report['collection']=True;report['extra_inputs']=[]
    for source,name,address,bound in [(a.manifest,'set.amf3',0xa81c0000,0x1000),(a.peer,'peer.apx2',0xa81c1000,0x3f000)]:
        assert source.stat().st_size<=bound
        shutil.copyfile(source,out/name)
        report['extra_inputs'].append({'name':name,'address':address,'sha256':native.sha(out/name)})
    report['sources']['probe_app_set_v3_guest.h']=native.sha(native.MODULES/'probe_app_set_v3_guest.h')
native.write_json(out/'build-report.json',report);print(json.dumps(report))
