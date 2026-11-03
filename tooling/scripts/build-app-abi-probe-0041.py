"""Build a real five-entry APX2 and RV32 production-loader harness; no execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
from elftools.elf.elffile import ELFFile
import apx2
import native_build_0041 as native
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--tool-prefix',required=True);a=p.parse_args()
out=a.out.resolve()
if not out.is_dir() or any(out.iterdir()):p.error('out must be an existing empty directory')
spec=importlib.util.spec_from_file_location('pic',Path(__file__).with_name('test-app-pic-load-0041.py'));pic=importlib.util.module_from_spec(spec);spec.loader.exec_module(pic)
tool=native.tools(a.tool_prefix);m=native.MODULES
names=['app_start','app_event','app_prepare_stop','app_stop','app_health']
ld=out/'app.ld';ld.write_text(pic.SCRIPT.replace('probe_entry','app_start').replace('KEEP(*(.text.app_start))',' '.join('KEEP(*(.text.'+name+'))' for name in names)))
flags=[f for f in native.FLAGS if f!='-fno-pic']+['-fpie','-fvisibility=hidden','-mcmodel=medany','-fno-asynchronous-unwind-tables']
obj=out/'app.o';subprocess.run([tool('g++'),*flags,'-c',str(m/'probe_app_abi_v2.cpp'),'-o',str(obj)],check=True)
runtime=out/'app-runtime.o';subprocess.run([tool('g++'),*flags,'-c',str(m/'app_runtime_heap_v2.cpp'),'-o',str(runtime)],check=True)
runtime_time=out/'app-runtime-time.o';subprocess.run([tool('g++'),*flags,'-c',str(m/'app_runtime_time_v2.cpp'),'-o',str(runtime_time)],check=True)
runtime_format=out/'app-runtime-format.o';subprocess.run([tool('g++'),*flags,'-c',str(m/'app_runtime_format_v2.cpp'),'-o',str(runtime_format)],check=True)
libgcc=subprocess.check_output([tool('gcc'),'-march=rv32imafc','-mabi=ilp32f','-print-libgcc-file-name'],text=True).strip()
probes=[];entries=[]
for base in (0x10000,0x30000):
    elf=out/f'app-{base:x}.elf'
    subprocess.run([tool('ld'),'-m','elf32lriscv','--no-relax','--emit-relocs','--gc-sections',f'--defsym=probe_base={base}','-T',str(ld),str(obj),str(runtime),str(runtime_time),str(runtime_format),libgcc,'-o',str(elf)],check=True)
    probes.append(pic.extract(elf))
    with elf.open('rb') as f:
        symbols={s.name:s['st_value']-base for s in ELFFile(f).get_section_by_name('.symtab').iter_symbols()}
        entries.append([symbols[n] for n in names])
assert probes[0]==probes[1] and entries[0]==entries[1]
probe=probes[0];spans=probe['spans'];data=spans['.data'];ro=spans.get('.rodata',[data[0],0])
config=dict(app_id='abi.probe',version='1',text_bytes=spans['.text'][1],ro_offset=ro[0],ro_bytes=ro[1],data_offset=data[0],data_bytes=data[1],bss_bytes=probe['memory']-len(probe['image']),heap_bytes=512,stack_bytes=4096,entries=entries[0],data_read_min=1,data_read_max=1,data_write_version=1,required_services=9,fixups=[[at,struct.unpack_from('<I',probe['image'],at)[0]] for at in probe['fixups']])
package=apx2.package(probe['image'],config);(out/'app.apx2').write_bytes(package)
(out/'app-manifest.json').write_text(json.dumps(config,indent=2)+'\n')
# Harness has no OS/heap/libc dependency and executes from a fixed model address.
guest_ld=out/'guest.ld';guest_ld.write_text('''OUTPUT_ARCH(riscv)
ENTRY(guest_entry)
SECTIONS { . = 0x62fc0000;
 .text : { KEEP(*(.text.guest_entry)) *(.text .text.*) }
 .rodata : { *(.rodata .rodata.* .srodata*) }
 .data : { *(.data .data.* .sdata*) }
 .bss : { *(.bss .bss.* .sbss* COMMON) }
 /DISCARD/ : { *(.comment .note* .eh_frame* .riscv.attributes) }
}''')
sources=['probe_app_image_guest_0041.cpp','app_image_0041.cpp','app_lifecycle_0041.cpp','app_core_0041.cpp','app_heap_0041.cpp','app_files_0041.cpp','app_network_0041.cpp','apx2.cpp','native_sha256_0041.cpp'];objects=[]
for source in sources:
    obj=out/(source+'.o');objects.append(str(obj))
    subprocess.run([tool('g++'),*native.FLAGS,'-march=rv32imafc_zifencei','-c',str(m/source),'-o',str(obj)],check=True)
elf=out/'guest.elf';subprocess.run([tool('g++'),*native.FLAGS,'-Wl,--no-relax,--gc-sections','-T',str(guest_ld),*objects,'-lgcc','-o',str(elf)],check=True)
assert not subprocess.check_output([tool('nm'),'-u',str(elf)],text=True).strip()
binary=out/'guest.bin';subprocess.run([tool('objcopy'),'-O','binary',str(elf),str(binary)],check=True)
assert binary.stat().st_size<0x8000 and len(package)<=8192 and probe['memory']<=8192
report={'built':True,'executed':False,'guest_base':0x62fc0000,'guest_bytes':binary.stat().st_size,'guest_sha256':native.sha(binary),'package_sha256':native.sha(out/'app.apx2'),'image_bytes':len(probe['image']),'memory_bytes':probe['memory'],'fixups':probe['fixups'],'entries':entries[0],'normalized_link_bases_identical':True,'sources':{s:native.sha(m/s) for s in sources+['probe_app_abi_v2.cpp','app_runtime_heap_v2.cpp','app_runtime_heap_v2.h','app_runtime_time_v2.cpp','app_runtime_format_v2.cpp','app_heap_client_v2.h','app_services_0041.h','app_core_abi_v2.h','app_core_0041.h','app_heap_abi_v2.h','app_heap_0041.h']}}
report['libgcc_sha256']=native.sha(Path(libgcc))
report['extractor_sha256']=native.sha(Path(pic.__file__))
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
