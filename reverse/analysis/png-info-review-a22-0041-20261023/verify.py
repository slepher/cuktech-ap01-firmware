"""A22 independent static encoding review. Reads ROM; never executes target code."""
from pathlib import Path
import json
import struct
import capstone

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
image = ROM.read_bytes()

def take(va, count):
    offset = va - 0xa0000000 + 0x1000
    assert 0 <= offset <= len(image) - count
    return image[offset:offset + count]

def u(va, count=4):
    return int.from_bytes(take(va, count), 'little')

def sx(value, bits):
    return (value ^ (1 << (bits-1))) - (1 << (bits-1))

checks = []
def equal(label, actual, expected, va=None):
    assert actual == expected, (label, actual, expected)
    checks.append({'check':label, 'address':hex(va) if va else None,
                   'actual':actual, 'expected':expected})

def jal(va, target):
    w = u(va)
    delta = ((w >> 31) << 20) | (((w >> 12) & 255) << 12)
    delta |= (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    equal('JAL opcode/rd/target', [w & 127, (w >> 7) & 31, va + sx(delta,21)],
          [111,1,target], va)

def imem(va, op, f3, reg, base, displacement):
    w = u(va)
    imm = w >> 20 if op != 35 else ((w >> 25) << 5) | ((w >> 7) & 31)
    r = (w >> 7) & 31 if op != 35 else (w >> 20) & 31
    equal('I/S fields', [w & 127,(w >> 12) & 7,r,(w >> 15) & 31,sx(imm,12)],
          [op,f3,reg,base,displacement],va)

def cmem(va, store, reg, base, displacement):
    h = u(va,2)
    offset = (((h >> 5) & 1) << 6) | (((h >> 10) & 7) << 3) | (((h >> 6) & 1) << 2)
    equal('C.LW/C.SW fields', [h & 3,h >> 13,8+((h >> 2)&7),8+((h >> 7)&7),offset],
          [0,6 if store else 2,reg,base,displacement],va)

def branch(va, funct, r1, r2, target):
    w = u(va)
    imm = ((w >> 31) << 12) | (((w >> 7)&1) << 11) | (((w >> 25)&63) << 5) | (((w >> 8)&15) << 1)
    equal('branch fields', [w & 127,(w>>12)&7,(w>>15)&31,(w>>20)&31,va+sx(imm,13)],
          [99,funct,r1,r2,target],va)

def pointer(hi, lo, wanted):
    a,b = u(hi),u(lo)
    equal('LUI+signed ADDI register/opcodes', [a&127,b&127,(b>>12)&7,(a>>7)&31,(b>>7)&31],
          [55,19,0,(b>>15)&31,(b>>15)&31],hi)
    equal('LUI+signed ADDI pointer', ((a&0xfffff000)+sx(b>>20,12))&0xffffffff,wanted,hi)

windows = [
 ('global init base',0xa008e3ac,0xa008e3d8),
 ('global init list anchor',0xa008e4c0,0xa008e4c4),
 ('registry payload size',0xa008e61e,0xa008e624),
 ('BIN create/register',0xa008e6ea,0xa008e764),
 ('PNG create/register',0xa008e82c,0xa008e858),
 ('decoder create',0xa0082914,0xa0082980),
 ('registry prepend',0xa008aec0,0xa008af14),
 ('prev and next setters',0xa0089cda,0xa0089d02),
 ('source wrapper',0xa0082e32,0xa0082e76),
 ('dispatcher',0xa0082c8c,0xa0082e32),
 ('PNG info complete',0xa00eb6fe,0xa00eb7b6),
 ('byte comparator',0xa00501be,0xa0050202),
 ('depth lookup',0xa00897c2,0xa00897ec),
 ('class0 helper null gate',0xa0089bde,0xa0089bf0),
 ('class0 helper return',0xa0089c26,0xa0089c30),
 ('clear wrapper and walker',0xa008adf4,0xa008ae58),
 ('unlink complete',0xa0089d02,0xa0089d76),
 ('allocation adapters',0xa008ae8c,0xa008aec0),
 ('free adapter',0xa008ab8a,0xa008abb0),
 ('deinit prologue to registry clear',0xa008be06,0xa008bed6),
 ('deinit last state',0xa008bf40,0xa008bf56),
 ('parent init guard',0xa005cc68,0xa005cc7a),
 ('parent init call',0xa005cd36,0xa005cd3c),
 ('parent deinit guard/call',0xa005ee9a,0xa005eeba),
 ('A20 flag corrected call',0xa00d8ffa,0xa00d9002),
 ('A20 unsigned state predicate',0xa00d7592,0xa00d759e),
]
vendor = {
 0xa0089ce4: (5,8,12,11,15,0,'th.srw a2,a1,a5,0'),
 0xa0089d3a: (4,8,11,11,14,0,'th.lrw a1,a1,a4,0'),
 0xa00897de: (4,16,10,15,10,0,'th.lrbu a0,a5,a0,0'),
 0xa00501ee: (4,16,15,10,14,0,'th.lrbu a5,a0,a4,0'),
 0xa00501f4: (4,16,13,11,14,0,'th.lrbu a3,a1,a4,0'),
}
md = capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows=[]
for name,start,end in windows:
    a=start
    while a<end:
        width=4 if u(a,2)&3==3 else 2
        raw=take(a,width)
        if a in vendor:
            w=u(a)
            fields=((w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3)
            equal('vendor opcode',w&127,11,a)
            equal('vendor unsigned/indexed fields',fields,vendor[a][:-1],a)
            text=vendor[a][-1]
        else:
            decoded=list(md.disasm(raw,a))
            assert len(decoded)==1 and decoded[0].size==width,(name,hex(a),raw.hex())
            text=decoded[0].mnemonic+' '+decoded[0].op_str
        rows.append({'scope':name,'va':hex(a),'file_offset':a-0xa0000000+0x1000,'bytes':raw.hex(),'asm':text})
        a+=width
    assert a==end,(name,hex(a))

for a,t in [(0xa008e3d0,0xa0080d8e),(0xa008e6ea,0xa0082914),(0xa008e82c,0xa0082914),
 (0xa0082926,0xa008aec0),(0xa0082970,0xa0080d8e),(0xa008aed2,0xa008aea0),
 (0xa008aee0,0xa0089cda),(0xa008aeea,0xa0089cee),(0xa008aef6,0xa0089cda),
 (0xa0082e62,0xa0082c8c),(0xa0082d90,0xa0089bde),(0xa0082e12,0xa00897c2),
 (0xa00eb7aa,0xa00501be),(0xa008bed2,0xa008ae42),(0xa008ae4c,0xa008adf4),
 (0xa008ae2e,0xa0089d02),(0xa008ae34,0xa008ab8a),(0xa005cd36,0xa008e3ac),
 (0xa005eeae,0xa008be06),(0xa00d8ffe,0xa00d7546)]: jal(a,t)

for hi,lo,value in [(0xa008e830,0xa008e834,0xa00eb6fe),(0xa008e83a,0xa008e83e,0xa00eb7b6),
 (0xa008e844,0xa008e848,0xa00eab9a),(0xa008e84e,0xa008e852,0xa02634f0),
 (0xa008291e,0xa0082922,0x62fc968c),(0xa008beca,0xa008bece,0x62fc968c),
 (0xa00eb79e,0xa00eb7a4,0xa059bf2c),(0xa00897d6,0xa00897da,0xa0263724)]:pointer(hi,lo,value)

for args in [(0xa008e620,35,2,15,20,16),(0xa008aefc,35,2,18,9,4),
 (0xa008af02,35,2,18,9,8),(0xa0082e50,35,2,9,8,-80),
 (0xa0082e58,35,0,10,8,-76),(0xa0082cbe,3,2,15,23,16),
 (0xa0082cf4,3,2,24,10,8),
 (0xa0082d76,3,2,9,20,0x114),(0xa0082da2,3,5,15,19,8),
 (0xa0082da8,3,4,10,19,1),(0xa0082dae,3,5,18,19,4),
 (0xa0082db8,35,1,18,19,8),(0xa0082e22,3,2,15,20,0x110),
 (0xa00eb70c,3,4,14,11,16),(0xa00eb7b0,19,0,10,9,16),
 (0xa00eb754,35,0,15,18,1),(0xa00eb768,35,1,15,18,4),
 (0xa00eb77a,35,1,15,18,6),(0xa008ae22,3,2,20,15,4),
 (0xa008bf44,35,0,0,9,0),(0xa00d7592,3,5,10,10,40)]: imem(*args)
for args in [(0xa008e838,True,15,10,0),(0xa008e842,True,15,10,4),
 (0xa008e84c,True,15,10,12),(0xa008e856,True,15,10,20),
 (0xa008aece,False,10,10,0),(0xa0082d82,False,15,9,0),
 (0xa0082d86,False,15,9,4),(0xa0082d94,False,15,9,0),
 (0xa0082e28,False,9,9,4),(0xa00eb792,False,15,11,12),
 (0xa00eb796,False,13,15,12),(0xa00eb79c,False,9,15,16),
 (0xa00eb758,False,14,10,0),(0xa00eb76c,False,14,10,4),
 (0xa0089d24,True,11,10,4),(0xa0089d42,True,11,10,8)]:cmem(*args)
cmem(0xa0089be8,False,15,10,4)
branch(0xa0082d9e,1,10,25,0xa0082e22)
branch(0xa00eb798,7,14,13,0xa00eb782)
branch(0xa00eb714,6,15,14,0xa00eb782)
branch(0xa00eb71c,1,14,15,0xa00eb792)

# These are independent raw halfword checks for ABI moves, shifts, and return gates.
for a,w in [(0xa008296c,0x45f1),(0xa008aed0,0x0521),(0xa008e61e,0x47f1),
 (0xa0082d96,0x864e),(0xa0082d98,0x85da),(0xa0082d9a,0x8526),
 (0xa0082d9c,0x9782),(0xa0082d7e,0x4c85),(0xa00eb752,0x47c1),
 (0xa00eb75a,0x4985),(0xa00eb764,0x8361),(0xa00eb776,0x8361),
 (0xa00eb78a,0x854e),(0xa00eb7b4,0xbf79),(0xa008ae4a,0x4581),
 (0xa008ae38,0x84d2),(0xa008ae3e,0x9982)]: equal('raw RVC ABI/control',u(a,2),w,a)
imem(0xa00eb75c,19,5,15,14,8)
imem(0xa00eb760,19,7,15,15,-256)
imem(0xa00eb76e,19,5,15,14,8)
imem(0xa00eb772,19,7,15,15,-256)
equal('wrapper SNEZ',u(0xa0082e6e),0x00a03533,0xa0082e6e)
equal('signature',take(0xa059bf2c,8).hex(),'89504e470d0a1a0a',0xa059bf2c)
equal('name',take(0xa02634f0,8).hex(),'4c4f4445504e4700',0xa02634f0)
equal('cf10 depth',u(0xa026372e,1),32,0xa026372e)

# A20 addresses are reused only as a resource inventory, never as calculated outputs.
a20=json.loads((HERE.parent/'weather-icon-review-a20-0041-20261023/instruction-review.json').read_text(encoding='utf-8'))
sources=[]
for item in a20['resources']:
    address=int(item['descriptor'],16)
    descriptor=take(address,28)
    size,data=struct.unpack_from('<II',descriptor,12)
    equal('existing descriptor source class',descriptor[0],0x19,address)
    equal('existing source signature',take(data,8).hex(),'89504e470d0a1a0a',data)
    assert size>7
    # Direct byte interpretation independently matches LW/shift/AND/SH low16 formula.
    w,h=struct.unpack('>II',take(data+16,8))
    for loc,value in [(data+16,w),(data+20,h)]:
        v=u(loc)
        equal('observed dimension expression low16',(((v>>8)&0xffffff00)+(v>>24))&65535,value&65535,loc)
    width,height=w&65535,h&65535
    stride=((width*32+7)>>3)&65535
    header=bytes([0,16,0,0])+struct.pack('<HHHH',width,height,stride,0)
    sources.append({'category':item['category'],'descriptor':hex(address),'source_header':descriptor[:12].hex(),
        'size':size,'data':hex(data),'signature':take(data,8).hex(),'dimensions_bytes':take(data+16,8).hex(),
        'conditional_header':header.hex(),'width':width,'height':height,'stride16':stride})

# Preserve the local ISA rule text with its limited provenance; do not change the model.
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model.read_text(encoding='utf-8').splitlines()
rules=[]
for prefix in (':th.srw ',':th.lrw ',':th.lrbu '):
    index=next(n for n,line in enumerate(lines) if line.startswith(prefix))
    rules.append({'line':index+1,'text':'\n'.join(lines[index:index+9])})

summary={'result':'passed','static_only':True,'core_functions':10,'windows':len(windows),
 'bytes':sum(b-a for _,a,b in windows),'instructions':len(rows),'encoding_and_source_assertions':len(checks),
 'vendor_words':len(vendor),'normal_descriptors':len(sources),'unknown_instructions':0,
 'scope':'Initializer/deinitializer are named slices, not full GUI init/shutdown certification.'}
result={'rom':str(ROM),'mapping':'file offset = VA - a0000000 + 1000', 'summary':summary,
 'windows':[{'name':n,'start':hex(a),'end_exclusive':hex(b)} for n,a,b in windows],
 'instructions':rows,'assertions':checks,'conditional_existing_sources':sources,
 'local_isa_model':{'path':str(model),'rules':rules},
 'limits':['No target execution/emulation, network/device access or abnormal input tests.',
 'A20 supplies descriptor addresses only; all source bytes and conditional dimensions freshly read.',
 'No A21 verifier execution, shared REA session or database mutation.',
 'Local ISA rule correspondence does not certify hardware behavior or exact library version.']}
(HERE/'instruction-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'instructions.txt').write_text('\n'.join(r['scope']+' '+r['va']+' '+r['bytes']+' '+r['asm'] for r in rows)+'\n',encoding='utf-8')
(HERE/'review-index.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
