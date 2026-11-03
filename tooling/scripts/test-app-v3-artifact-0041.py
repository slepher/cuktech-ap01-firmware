"""Validate two real App builds, production APX2 loading and strict ELF difference relocations."""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
import native_build_0041 as native

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--build',type=Path,required=True)
p.add_argument('--repeat',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')
reports=[]
for directory in (a.build,a.repeat):
    r=json.loads((directory/'build-report.json').read_text())
    assert r['built'] and r['unresolved_imports']==0 and r['normalized_link_bases_identical']
    assert native.sha(directory/'app.apx2')==r['package_sha256']
    for obj in r['objects']:
        assert native.sha(Path(obj['source']))==obj['source_sha256']
        assert native.sha(directory/obj['object'])==obj['sha256']
    for path,digest in r['input_headers'].items():assert native.sha(Path(path))==digest,path
    reports.append(r)
assert (a.build/'app.apx2').read_bytes()==(a.repeat/'app.apx2').read_bytes()
spec=importlib.util.spec_from_file_location('pic',Path(__file__).with_name('test-app-pic-load-0041.py'))
pic=importlib.util.module_from_spec(spec);spec.loader.exec_module(pic)
elf_path=a.build/'app-10000.elf';blob=elf_path.read_bytes();location=None
with elf_path.open('rb') as f:
    elf=ELFFile(f)
    for section in elf.iter_sections():
        if isinstance(section,RelocationSection) and elf.get_section(section['sh_info'])['sh_flags']&2:
            rels=list(section.iter_relocations())
            for i,rel in enumerate(rels[:-1]):
                if rel['r_info_type']==35 and rels[i+1]['r_info_type']==39:
                    location=section['sh_offset']+i*section['sh_entsize'];break
        if location is not None:break
assert location is not None
offset,info,addend=struct.unpack_from('<IIi',blob,location)
suboffset,subinfo,subaddend=struct.unpack_from('<IIi',blob,location+12)
rejected=[]
for name,at,fmt,value in (
    ('unpaired-sub',location+4,'<I',(info&~255)|39),
    ('missing-sub',location+16,'<I',(subinfo&~255)|35),
    ('incorrect-difference',location+20,'<i',subaddend+1),
    ('external-target',location+4,'<I',35),
    ('unaligned-word',location,'<I',offset+1),
    ('unsupported-got',location+4,'<I',(info&~255)|20),
):
    bad=bytearray(blob);struct.pack_into(fmt,bad,at,value)
    path=a.out/(name+'.elf');path.write_bytes(bad)
    try:pic.extract(path,allow_differences=True)
    except ValueError:rejected.append(name)
    else:raise AssertionError('Accepted '+name)
binary=a.out.resolve()/'test-apx2-v3'
sources=[native.MODULES/n for n in ('apx2.cpp','native_sha256_0041.cpp','test_apx2.cpp')]
subprocess.run(['clang++','-std=c++17','-Wall','-Wextra','-Werror','-g','-fsanitize=address,undefined',
                *map(str,sources),'-o',str(binary)],check=True)
result=subprocess.check_output([str(binary),'--app-v3',str((a.build/'app.apx2').resolve())],text=True)
frames=[]
for filename,usage in reports[0]['stack_usage'].items():
    for line in usage.splitlines():
        fields=line.split('\t')
        if len(fields)==3:frames.append({'function':fields[0],'bytes':int(fields[1]),'kind':fields[2]})
result_report={'passed':True,'executed':False,'hardware_verified':False,
               'package_sha256':reports[0]['package_sha256'],'package_bytes':reports[0]['package_bytes'],
               'independent_builds_identical':True,'rejected_relocations':rejected,
               'production_loader':result.strip(),'largest_static_frames':sorted(frames,key=lambda x:x['bytes'],reverse=True)[:10],
               'limitations':['Static frames are not task high-water marks','Real App instructions have not executed']}
native.write_json(a.out/'artifact-report.json',result_report)
print(json.dumps(result_report))
