"""Compile and independently link the real codex_status ABI 3 App; no execution/device I/O."""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
from elftools.elf.elffile import ELFFile
import apx2
import native_build_0041 as native

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--app-config',type=Path,required=True)
p.add_argument('--tool-prefix',required=True)
p.add_argument('--app-id',default='codex_status')
p.add_argument('--version',default='d1.0')
p.add_argument('--heap-bytes',type=int,default=2*1024*1024)
p.add_argument('--stack-bytes',type=int,default=40960)
p.add_argument('--capabilities',type=int,default=127)
a=p.parse_args();out=a.out.resolve()
if not out.is_dir() or any(out.iterdir()):p.error('out must be an existing empty directory')
config=native.read_app_config(a.app_config);tool=native.tools(a.tool_prefix);m=native.MODULES
report={'built':False,'executed':False,'hardware_verified':False,'abi_major':3,'objects':[],
        'compiler':subprocess.check_output([tool('g++'),'--version'],text=True).splitlines()[0],
        'app_config_sha256':native.sha(a.app_config),
        'builder_sha256':native.sha(Path(__file__))}
report_path=out/'build-report.json';native.write_json(report_path,report)
# medany direct PC-relative addressing avoids external GOTs; the final ELF
# relocation audit and two-base byte comparison, not this flag, prove rebasing.
flags=native.FLAGS+['-mcmodel=medany','-fvisibility=hidden','-fno-asynchronous-unwind-tables',
                    '-DAP01_FILE_APP_V3=1','-include',str(m/'app_runtime_v3.h')]
flags+=['-I'+str(x) for x in [m,native.ROOT/'tooling/vendor/ArduinoJson/src',*config['include_dirs']]]
flags+=['-D'+x for x in config['defines']]+['-DARDUINOJSON_ENABLE_ARDUINO_STRING=1']
headers=sorted({h for folder in [m,native.ROOT/'tooling/vendor/ArduinoJson/src',*config['include_dirs']]
                for h in folder.rglob('*') if h.is_file() and h.suffix in ('.h','.hpp','.inc')})
report['input_headers']={str(h):native.sha(h) for h in headers}
# Resident ROM manifest/private-layout records are not App payloads.
sources=[s for s in config['plain_sources']+config['sources'] if s.name not in ('abi_budget.cpp','manifest_0041.cpp')]
sources += [m/n for n in ('app_runtime_v3.cpp','runtime_libc_0041.cpp','native_calendar_0041.cpp',
                          'native_sha256_0041.cpp','native_http_transport_0041.cpp')]
objects=[]
for source in sources:
    obj=out/(source.stem+'.o');objects.append(str(obj))
    cmd=[tool('g++'),*flags,'-c',str(source),'-o',str(obj)]
    subprocess.run(cmd,check=True)
    report['objects'].append({'source':str(source),'source_sha256':native.sha(source),
                              'object':obj.name,'sha256':native.sha(obj),'command':cmd})
    native.write_json(report_path,report)
entries=['ap01_app_start_v3','ap01_app_event_v3','ap01_app_health_v3']
script=out/'app.ld'
script.write_text('''OUTPUT_ARCH(riscv)
ENTRY(ap01_app_start_v3)
SECTIONS {
 . = app_base;
 .text : { '''+' '.join('KEEP(*(.text.'+n+'))' for n in entries)+''' *(.text .text.*) }
 . = ALIGN(16);
 .rodata : { *(.rodata .rodata.* .srodata .srodata.* .data.rel.ro*) . = ALIGN(16); }
 .data : { *(.data .data.* .sdata .sdata.*) . = ALIGN(16); }
 .bss (NOLOAD) : { *(.bss .bss.* .sbss .sbss.* COMMON) }
 .forbidden : { *(.got*) *(.init_array*) *(.fini_array*) *(.ctors*) *(.dtors*) *(.tdata*) *(.tbss*) }
 ASSERT(SIZEOF(.forbidden)==0,"Unexpected GOT/initializer/TLS")
 /DISCARD/ : { *(.comment .note* .eh_frame* .riscv.attributes) }
}
''')
libraries=[Path(subprocess.check_output([tool('gcc'),'-march=rv32imafc','-mabi=ilp32f',arg],text=True).strip())
           for arg in ('-print-file-name=libm.a','-print-libgcc-file-name')]
spec=importlib.util.spec_from_file_location('pic',Path(__file__).with_name('test-app-pic-load-0041.py'))
pic=importlib.util.module_from_spec(spec);spec.loader.exec_module(pic)
images=[];offsets=[]
for base in (0x10000,0x100000):
    elf=out/f'app-{base:x}.elf'
    subprocess.run([tool('ld'),'-m','elf32lriscv','--no-relax','--emit-relocs','--gc-sections',
                    f'--defsym=app_base={base}','-T',str(script),*objects,*map(str,libraries),'-o',str(elf)],check=True)
    undefined=subprocess.check_output([tool('nm'),'-u',str(elf)],text=True)
    if undefined.strip():raise ValueError('Unresolved imports: '+undefined)
    elf.with_suffix('.relocations.txt').write_text(subprocess.check_output([tool('readelf'),'-rW',str(elf)],text=True))
    images.append(pic.extract(elf,allow_differences=True))
    with elf.open('rb') as f:
        symbols={s.name:s['st_value']-base for s in ELFFile(f).get_section_by_name('.symtab').iter_symbols()}
        offsets.append([symbols[n] for n in entries])
assert images[0]==images[1] and offsets[0]==offsets[1],'Normalized images differ'
image=images[0];spans=image['spans'];ro=spans['.rodata'];data=spans.get('.data',[ro[0]+ro[1],0])
manifest=dict(abi_major=3,app_id=a.app_id,version=a.version,text_bytes=spans['.text'][1],
              ro_offset=ro[0],ro_bytes=ro[1],data_offset=data[0],data_bytes=data[1],
              bss_bytes=image['memory']-len(image['image']),heap_bytes=a.heap_bytes,stack_bytes=a.stack_bytes,
              entries=offsets[0],data_read_min=1,data_read_max=1,data_write_version=1,
              required_services=a.capabilities,fixups=[[at,struct.unpack_from('<I',image['image'],at)[0]] for at in image['fixups']])
(out/'app.apx2').write_bytes(apx2.package(image['image'],manifest))
native.write_json(out/'app-manifest.json',manifest)
report.update(built=True,normalized_link_bases_identical=True,unresolved_imports=0,
              image_bytes=len(image['image']),memory_bytes=image['memory'],fixup_count=len(image['fixups']),
              package_sha256=native.sha(out/'app.apx2'),package_bytes=(out/'app.apx2').stat().st_size,
              relocations=image['relocations'],entries=offsets[0],
              libraries={str(lib):native.sha(lib) for lib in libraries},
              extractor_sha256=native.sha(Path(pic.__file__)),
              stack_usage={su.name:su.read_text() for su in sorted(out.glob('*.su'))},
              limitations=['Heap/stack are model budgets, not hardware measurements','No execution yet'])
native.write_json(report_path,report)
print(json.dumps({k:v for k,v in report.items() if k not in ('objects','input_headers','stack_usage')}))
