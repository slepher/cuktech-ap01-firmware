"""A21: static ROM reads and encoding assertions only; no target execution."""
from pathlib import Path
import json
import struct
import capstone

OUT = Path(__file__).resolve().parent
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
blob = ROM.read_bytes()

def read(a, n):
    off = a - 0xa0000000 + 0x1000
    assert 0 <= off <= len(blob) - n
    return blob[off:off+n]

def word(a, n=4):
    return int.from_bytes(read(a, n), 'little')

def signed(v, n):
    return v - (1 << n) if v & (1 << (n-1)) else v

def fields(a):
    w = word(a)
    h = w & 65535
    if h & 3 != 3:
        f = h >> 13
        if h & 3 == 0 and f in (2, 6):
            return ['CM', f, 8+((h>>2)&7), 8+((h>>7)&7), (((h>>5)&1)<<6)|(((h>>10)&7)<<3)|(((h>>6)&1)<<2)]
        if h & 3 == 2 and f == 4:
            return ['CR', (h>>12)&1, (h>>7)&31, (h>>2)&31]
        return ['C', hex(h)]
    op, rd, f3, r1, r2 = w&127, (w>>7)&31, (w>>12)&7, (w>>15)&31, (w>>20)&31
    if op in (3,19,103):
        return ['I', op, f3, rd, r1, signed(w>>20,12)]
    if op == 35:
        return ['S',f3,r2,r1,signed(((w>>25)<<5)|((w>>7)&31),12)]
    if op == 111:
        imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        return ['J',rd,hex(a+signed(imm,21))]
    if op == 99:
        imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
        return ['B',f3,r1,r2,hex(a+signed(imm,13))]
    if op in (23,55):
        return ['U',op,rd,hex(w&0xfffff000)]
    if op == 11:
        return ['THEAD',f3,w>>27,rd,r1,r2,(w>>25)&3]
    return ['R',op,f3,w>>25,rd,r1,r2]

# Initializer/deinitializer are deliberately slices, not whole-function claims.
windows = [
 ('init zero/global base',0xa008e3ac,0xa008e3d8),
 ('init list base register',0xa008e4bc,0xa008e4c4),
 ('init registry node size',0xa008e612,0xa008e628),
 ('init earlier BIN registration',0xa008e6ea,0xa008e768),
 ('init PNG registration',0xa008e82c,0xa008e85a),
 ('decoder create',0xa0082914,0xa0082980),
 ('insert registry head',0xa008aec0,0xa008af14),
 ('set prev link',0xa0089cda,0xa0089cee),
 ('set next link',0xa0089cee,0xa0089d02),
 ('info wrapper',0xa0082e32,0xa0082e76),
 ('info dispatcher',0xa0082c8c,0xa0082e32),
 ('PNG info callback',0xa00eb6fe,0xa00eb7b6),
 ('signature comparator',0xa00501be,0xa0050202),
 ('format bit depth',0xa00897c2,0xa00897ec),
 ('list clear wrapper',0xa008ae42,0xa008ae58),
 ('list clear walker',0xa008adf4,0xa008ae42),
 ('list unlink',0xa0089d02,0xa0089d76),
 ('allocation adapter',0xa008aea0,0xa008aec0),
 ('allocation backend wrapper',0xa008ae8c,0xa008aea0),
 ('free adapter',0xa008ab8a,0xa008abb0),
 ('global deinit registry slice',0xa008beb2,0xa008bee2),
 ('global deinit final flag slice',0xa008bf3c,0xa008bf56),
 ('parent init trigger slice',0xa005cc68,0xa005cc7a),
 ('parent init call slice',0xa005cd36,0xa005cd3c),
 ('parent deinit call slice',0xa005ee9a,0xa005eeba),
]
vendor = {
 0xa0089ce4:'th.srw a2,a1,a5,0',
 0xa0089d3a:'th.lrw a1,a1,a4,0',
 0xa00897de:'th.lrbu a0,a5,a0,0',
 0xa00501ee:'th.lrbu a5,a0,a4,0',
 0xa00501f4:'th.lrbu a3,a1,a4,0',
}
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
retained=[]
for name,lo,hi in windows:
    rows=[]
    a=lo
    while a<hi:
        n=4 if word(a,2)&3==3 else 2
        raw=read(a,n)
        ds=list(md.disasm(raw,a))
        if a in vendor:
            assert not ds
            text=vendor[a]
        else:
            assert len(ds)==1 and ds[0].size==n,hex(a)
            text=ds[0].mnemonic+' '+ds[0].op_str
        rows.append(dict(address=hex(a),file_offset=a-0xa0000000+0x1000,bytes=raw.hex(),instruction=text,fields=fields(a)))
        a+=n
    assert a==hi,(name,hex(a),hex(hi))
    retained.append(dict(name=name,start=hex(lo),end_exclusive=hex(hi),rows=rows))

checks=[]
def expect(a,want,meaning):
    actual=fields(a)
    assert actual==want,(hex(a),actual,want)
    checks.append(dict(address=hex(a),fields=actual,meaning=meaning))

for a,target in [(0xa008e3d0,0xa0080d8e),(0xa008e6ea,0xa0082914),(0xa008e82c,0xa0082914),
 (0xa0082926,0xa008aec0),(0xa0082970,0xa0080d8e),(0xa008aed2,0xa008aea0),
 (0xa008aee0,0xa0089cda),(0xa008aeea,0xa0089cee),(0xa008aef6,0xa0089cda),
 (0xa0082e62,0xa0082c8c),(0xa0082d90,0xa0089bde),(0xa0082e12,0xa00897c2),
 (0xa00eb748,0xa00501be),(0xa00eb7aa,0xa00501be),(0xa008bed2,0xa008ae42),
 (0xa008ae4c,0xa008adf4),(0xa008ae2e,0xa0089d02),(0xa008ae34,0xa008ab8a),
 (0xa005cd36,0xa008e3ac),(0xa005eeae,0xa008be06)]:
    expect(a,['J',1,hex(target)],'direct call target')

for a,want,meaning in [
 (0xa008e620,['S',2,15,20,16],'1c registry size at global+110; s4=global+100'),
 (0xa008e834,['I',19,0,15,15,0x6fe],'PNG info low address'),
 (0xa008e838,['CM',6,15,10,0],'register info callback node+0'),
 (0xa008e83e,['I',19,0,15,15,0x7b6],'PNG open low address'),
 (0xa008e842,['CM',6,15,10,4],'register open callback node+4'),
 (0xa008e84c,['CM',6,15,10,12],'register close callback node+c'),
 (0xa008e856,['CM',6,15,10,20],'register name node+14'),
 (0xa008296c,['C','0x45f1'],'clear decoder payload size 1c'),
 (0xa008aece,['CM',2,10,10,0],'load list node data size'),
 (0xa008aed0,['C','0x521'],'allocate data size plus two links'),
 (0xa008aefc,['S',2,18,9,4],'publish new registry head'),
 (0xa008af02,['S',2,18,9,8],'empty registry publishes tail'),
 (0xa0082cbe,['I',3,2,15,23,16],'class0 data pointer guard'),
 (0xa0082d76,['I',3,2,9,20,0x114],'registry head'),
 (0xa0082d82,['CM',2,15,9,0],'info callback gate'),
 (0xa0082d86,['CM',2,15,9,4],'open callback gate'),
 (0xa0082d94,['CM',2,15,9,0],'reload info callback'),
 (0xa0082d9c,['CR',1,15,0],'indirect call after a0=node,a1=dsc,a2=header'),
 (0xa0082d9e,['B',1,10,25,'0xa0082e22'],'only callback result 1 accepts'),
 (0xa0082e22,['I',3,2,15,20,0x110],'node link offset from list data size'),
 (0xa0082e28,['CM',2,9,9,4],'next node at node+size+4'),
 (0xa00eb70c,['I',3,4,14,11,16],'source class unsigned byte'),
 (0xa00eb792,['CM',2,15,11,12],'class0 source descriptor pointer'),
 (0xa00eb796,['CM',2,13,15,12],'source data_size'),
 (0xa00eb79c,['CM',2,9,15,16],'source payload pointer'),
 (0xa00eb7b0,['I',19,0,10,9,16],'IHDR dimension pointer'),
 (0xa00eb754,['S',0,15,18,1],'out cf=10 byte'),
 (0xa00eb768,['S',1,15,18,4],'out width low16'),
 (0xa00eb77a,['S',1,15,18,6],'out height low16'),
 (0xa0089ce4,['THEAD',5,8,12,11,15,0],'prev: store32(node+size,value)'),
 (0xa0089d3a,['THEAD',4,8,11,11,14,0],'unlink reads prev at node+size'),
 (0xa00897de,['THEAD',4,16,10,15,10,0],'byte depth table index cf-6'),
 (0xa00501ee,['THEAD',4,16,15,10,14,0],'comparator unsigned lhs byte'),
 (0xa00501f4,['THEAD',4,16,13,11,14,0],'comparator unsigned rhs byte'),
 (0xa008ae1c,['I',3,2,15,18,0],'clear reloads data size'),
 (0xa008ae22,['I',3,2,20,15,4],'clear saves next before unlink/free'),
 (0xa008ae4a,['C','0x4581'],'clear wrapper callback NULL'),
]:expect(a,want,meaning)

# Pointer constants established by instruction pairs, not inferred from PNG bytes.
def lui_add(a,wanted,add_offset=4):
    w,v=word(a),word(a+add_offset)
    assert w&127==55 and v&127==19 and ((w>>7)&31)==((v>>15)&31)==((v>>7)&31)
    value=((w&0xfffff000)+signed(v>>20,12))&0xffffffff
    assert value==wanted,(hex(a),hex(value),hex(wanted))
    checks.append(dict(address=hex(a),bytes=read(a,add_offset+4).hex(),value=hex(value),meaning='LUI/ADDI constant'))
for a,v in [(0xa008e830,0xa00eb6fe),(0xa008e83a,0xa00eb7b6),(0xa008e844,0xa00eab9a),
 (0xa008e84e,0xa02634f0),(0xa008291e,0x62fc968c),(0xa008beca,0x62fc968c),
 (0xa00897d6,0xa0263724)]:lui_add(a,v)
lui_add(0xa00eb79e,0xa059bf2c,6)

assert read(0xa059bf2c,8)==b'\x89PNG\r\n\x1a\n'
assert read(0xa02634f0,8)==b'LODEPNG\0'
assert word(0xa026372e,1)==32
strings=[]
for a,suffix in [(0xa025ebf4,'/src/draw/lv_image_decoder.c'),(0xa056b1a4,'/src/libs/lodepng/lv_lodepng.c')]:
    raw=read(a,256).split(b'\0',1)[0]
    text=raw.decode('ascii')
    assert text.endswith(suffix)
    strings.append(dict(address=hex(a),bytes=raw.hex(),text=text))
old=json.loads((OUT.parent/'weather-icon-review-a20-0041-20261023/instruction-review.json').read_text())
resources=[]
for r in old['resources']:
    a=int(r['descriptor'],16)
    raw=read(a,28)
    size,payload=struct.unpack_from('<II',raw,12)
    assert payload==a+28 and size>7 and read(payload,8)==read(0xa059bf2c,8)
    # Static reconstruction of the observed loads/shifts/stores; not invocation.
    def dimension(p):
        v=word(p)
        return (((v>>8)&0xffffff00)+(v>>24))&65535
    w,h=dimension(payload+16),dimension(payload+20)
    stride=((w*32+7)>>3)&65535
    out=bytes([0,0x10,0,0])+struct.pack('<HHHH',w,h,stride,0)
    assert w==r['ihdr_width'] and h==r['ihdr_height']
    resources.append(dict(category=r['category'],descriptor=hex(a),source_bytes=raw.hex(),data=hex(payload),data_size=size,dimension_loads=read(payload+16,8).hex(),static_width=w,static_height=h,static_stride=stride,expected_output_header=out.hex(),callback_return=1,wrapper_return=1,condition='normal initialized registry; no later shadowing registration; ROM bytes unchanged; static conditional result only'))

index=json.loads((OUT.parent/'whole-rom-coverage-0041-20261023-round1.json').read_text())
seeds=['0xa0082914','0xa008e3ac','0xa008be06']
refs={a:[dict(caller=f['address'],evidence=f['direct_calls']['evidence_id']) for f in index['functions'] if a in f['direct_calls']['callees']] for a in seeds}
model=SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model.read_text().splitlines()
excerpts=[]
for prefix in (':th.srw ',':th.lrw ',':th.lrbu '):
    i=next(i for i,line in enumerate(lines) if line.startswith(prefix));excerpts.append('\n'.join(lines[i:i+9]))
result=dict(static_only=True,rom=str(ROM),mapping='file offset = VA - a0000000 + 1000',windows=retained,encoding_checks=checks,resources=resources,strings=strings,registry=dict(address='0x62fc968c',global_base='0x62fc957c',size=28,head_offset=4,tail_offset=8,allocated_node_size=36),bounded_inventory_refs=refs,inventory_scope='6487 provider procedures; direct-call inventory only; no exhaustive indirect-reference claim',model=dict(path=str(model),excerpts=excerpts),limitations=['No firmware execution/emulation/replay/network/device access.','Open/decode/close pixel algorithms are explicit boundaries.','Library source path/name are candidates, not exact-version certification.','Initializer and global deinitializer analyzed as named slices; parent command/GUI shutdown trigger remains outside scope.','Local ISA model correspondence is not independent hardware certification.'])
(OUT/'instruction-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'instructions.txt').write_text('\n\n'.join(w['name']+'\n'+'\n'.join(r['address']+' '+r['bytes']+' '+r['instruction']+' | '+str(r['fields']) for r in w['rows']) for w in retained)+'\n',encoding='utf-8')
summary=dict(result='passed',core_functions=10,core_scope='2 initializer/deinitializer slices + create/insert/dispatcher/wrapper/PNG-info/clear-wrapper/clear-walker/unlink',necessary_dependencies=8,windows=len(retained),bytes=sum(b-a for _,a,b in windows),instructions=sum(len(w['rows'])for w in retained),encoding_checks=len(checks),vendor_words=len(vendor),normal_rom_descriptors=len(resources),unknown_instructions=0)
(OUT/'review-index.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
