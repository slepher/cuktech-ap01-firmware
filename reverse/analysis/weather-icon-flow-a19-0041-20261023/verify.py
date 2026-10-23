"""A19 bounded static ROM extraction. No target code execution/emulation."""
import json, struct, zlib
from pathlib import Path
import capstone
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SOURCE=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=SOURCE/'roms/0041/ap01-1.0.2_0041.bin'
image=ROM.read_bytes()
def raw(a,n):
    off=a-0xa0000000+0x1000
    assert off>=0 and off+n<=len(image)
    return image[off:off+n]
def u(a,n=4): return int.from_bytes(raw(a,n),'little')
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
fs={f['address']:f for f in json.loads((ROOT/'analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())['functions']}
entries=[0xa00a5d5c,0xa00a6998,0xa0198946,0xa00d9044,0xa00d8f7c,0xa00dd454,0xa0082e32,0xa0082c8c,0xa00ed560,0xa00ed438,0xa01b1ee6]
vendor={0xa00ed5f8:'th.extu a5,a5,15,0',0xa00ed6c0:'th.extu a5,a5,15,0',0xa00ed748:'th.extu a5,a5,15,0',0xa00ed4f2:'th.mvnez a2,s2,a5'}
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[]; provenance=[]
def window(name,lo,hi):
    rows=[]; p=lo
    while p<hi:
        n=2 if u(p,2)&3!=3 else 4
        b=raw(p,n); ins=list(md.disasm(b,p))
        if p in vendor:
            assert not ins
            text=vendor[p]; decoder='raw fields and retained model'
        else:
            assert len(ins)==1 and ins[0].size==n,(hex(p),b.hex())
            text=ins[0].mnemonic+' '+ins[0].op_str; decoder='Capstone'
        rows.append(dict(address=hex(p),file_offset=p-0xa0000000+0x1000,bytes=b.hex(),instruction=text,decoder=decoder)); p+=n
    assert p==hi
    windows.append(dict(name=name,start=hex(lo),end_exclusive=hex(hi),rows=rows))
for a in entries+[0xa00d7446,0xa00d749e]:
    f=fs[hex(a)]; body=f['extent']['body']; assert len(body['ranges'])==1
    hi=int(body['ranges'][0]['end'],16)+1
    window(hex(a),a,hi)
    provenance.append(dict(address=hex(a),extent=f['extent'],direct_calls=f['direct_calls']))
window('widget constructor call site',0xa00a7f7e,0xa00a7f9e)
window('now.ico producer slice',0xa00aa58a,0xa00aa5e2)
window('callback icon read',0xa00ab6c0,0xa00ab6d4)
window('callback icon consume',0xa00ab710,0xa00ab71c)
checks=[]
def check(a,kind,value,expected):
    assert value==expected,(hex(a),kind,value,expected)
    checks.append(dict(address=hex(a),kind=kind,bytes=raw(a,2 if u(a,2)&3!=3 else 4).hex(),value=value))
def jal(a,target):
    w=u(a); imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    check(a,'JAL opcode/rd/target',[w&127,(w>>7)&31,hex(a+sx(imm,21))],[111,1,hex(target)])
for a,t in [(0xa00aa5d0,0xa0053f46),(0xa00aa5da,0xa0053f46),(0xa00ab714,0xa0198946),(0xa0198956,0xa00a6998),(0xa0198960,0xa00d9044),(0xa0198a20,0xa00ed560),(0xa0198a98,0xa00d8f7c),(0xa00ed5b6,0xa00dddf4),(0xa00ed5bc,0xa00dd454),(0xa00ed62c,0xa0082e32),(0xa0082e54,0xa00dd454),(0xa0082e62,0xa0082c8c),(0xa00ed700,0xa01b1ee6),(0xa00ed706,0xa00ed438),(0xa00ed720,0xa00d89c6),(0xa00ed726,0xa00dddf4),(0xa00ed602,0xa008ab8a),(0xa00ed6ca,0xa008ab8a)]: jal(a,t)
for a,t in [(0xa00a5d74,0xa00ed0a8),(0xa00a5d82,0xa00ed560),(0xa00a5d96,0xa00dbb68),(0xa00a7f96,0xa00a5d5c),(0xa00d8fd2,0xa00d7446),(0xa00d9098,0xa00d749e)]: jal(a,t)
def branch(a,f3,r1,r2,target):
    w=u(a); imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    check(a,'B opcode/funct3/rs1/rs2/target',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,hex(a+sx(imm,13))],[99,f3,r1,r2,hex(target)])
for a,f3,r1,r2,t in [(0xa00a69a6,6,14,15,0xa00a6a28),(0xa00a69b0,0,10,13,0xa00a69d6),(0xa00a69b4,6,13,10,0xa00a69de),(0xa00a69b8,0,10,14,0xa00a6a06),(0xa00a69c4,6,14,10,0xa00a69d6),(0xa00a69e2,0,10,15,0xa00a6a16),(0xa00a69ee,6,14,10,0xa00a69d6),(0xa00a6a30,6,14,15,0xa00a6a9a),(0xa00a6a3c,7,13,14,0xa00a69d6),(0xa00a6a44,6,15,10,0xa00a6a68),(0xa00a6a4c,6,15,10,0xa00a6a86),(0xa00a6a54,7,15,10,0xa00a6a76),(0xa00a6a60,7,14,10,0xa00a69d6),(0xa00a6a6e,1,10,14,0xa00a69d6),(0xa00a6a9e,6,14,15,0xa00a6aec),(0xa00a6aa4,6,14,15,0xa00a6ab6),(0xa00a6aae,1,10,14,0xa00a69d6),(0xa00a6abe,7,13,14,0xa00a69d6),(0xa00a6ac6,0,10,14,0xa00a69d6),(0xa00a6ace,0,10,14,0xa00a69d6),(0xa00a6ad4,6,14,10,0xa00a69d6),(0xa00a6adc,0,10,13,0xa00a6ab2),(0xa00a6ae0,0,10,14,0xa00a69d6),(0xa00ed632,0,10,15,0xa00ed678),(0xa00ed678,1,19,0,0xa00ed72c),(0xa0082d9e,1,10,25,0xa0082e22)]: branch(a,f3,r1,r2,t)
# Independent I/S/C memory decoding; register numbers follow RV32 ABI.
def imem(a,op,f3,reg,base,off):
    w=u(a); value=[w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12)]
    check(a,'I-memory opcode/funct3/rd/base/offset',value,[op,f3,reg,base,off])
def smem(a,f3,reg,base,off):
    w=u(a); imm=((w>>25)<<5)|((w>>7)&31)
    check(a,'S-memory opcode/funct3/rs2/base/offset',[w&127,(w>>12)&7,(w>>20)&31,(w>>15)&31,sx(imm,12)],[35,f3,reg,base,off])
def cmem(a,f3,reg,base,off):
    w=u(a,2); imm=((w>>5)&1)*64+((w>>10)&7)*8+((w>>6)&1)*4
    check(a,'C-memory quadrant/funct3/reg/base/offset',[w&3,w>>13,8+((w>>2)&7),8+((w>>7)&7),imm],[0,f3,reg,base,off])
for a,f3,r,b,o in [(0xa00a7f9a,2,10,18,32),(0xa00aa5d4,2,10,8,-192),(0xa00aa5de,2,10,8,-188),(0xa00ed6ce,2,18,9,44),(0xa00ed612,1,15,9,88),(0xa00ed6fa,0,10,9,88)]: smem(a,f3,r,b,o)
for a,f3,r,b,o in [(0xa00a69cc,4,15,15,95),(0xa00ab6d0,2,19,10,28),(0xa00dd45c,4,14,10,0),(0xa0082d76,2,9,20,276),(0xa00ed6d2,5,15,8,-64),(0xa00ed6e0,5,15,8,-62),(0xa00ed6d6,4,10,8,-67)]: imem(a,3,f3,r,b,o)
for a,f3,r,b,o in [(0xa00ab710,2,10,9,32),(0xa00ed6de,6,15,9,60),(0xa00ed6ea,6,15,9,64),(0xa00d90da,6,15,9,36),(0xa00d8ff4,6,11,9,36)]: cmem(a,f3,r,b,o)
for a in [0xa00ed5f8,0xa00ed6c0,0xa00ed748]:
    w=u(a); check(a,'extu opcode/funct3/rd/rs1/msb/lsb',[w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,w>>26,(w>>20)&63],[11,3,15,15,15,0])
w=u(0xa00ed4f2); check(0xa00ed4f2,'mvnez opcode/funct3/funct7/rd/rs1/rs2',[w&127,(w>>12)&7,w>>25,(w>>7)&31,(w>>15)&31,(w>>20)&31],[11,1,33,12,18,15])
for a,h in [(0xa00ab712,'ce85'),(0xa0082d9c,'8297'),(0xa00ed6da,'93f93900'),(0xa0082e6e,'3335a000')]: check(a,'fixed ABI/width encoding',raw(a,len(bytes.fromhex(h))).hex(),h)
# Resource selection constants: each exact LUI/ADDI pair independently reconstructs a1.
selection={1:(0xa0198a4e,0xa0251da8),2:(0xa0198a58,0xa062ff20),3:(0xa0198a62,0xa062fb30),4:(0xa01989a0,0xa062fd24),5:(0xa0198a26,0xa062f000),6:(0xa0198a16,0xa062eee8),7:(0xa01989c2,0xa062f2bc),8:(0xa0198a30,0xa062f414),9:(0xa0198a3a,0xa062f618),10:(0xa0198a8a,0xa0630838),11:(0xa0198a80,0xa0630658),12:(0xa01989ec,0xa062f9a4),13:(0xa0198a44,0xa062f834),14:(0xa01989fc,0xa062f16c),22:(0xa0198a6c,0xa0630190),23:(0xa0198a76,0xa06303f0)}
resources=[]
for cls,(a,expected) in selection.items():
    w=u(a); v=u(a+4)
    assert w&127==55 and (w>>7)&31==11 and v&127==19 and (v>>7)&31==11 and (v>>15)&31==11
    ptr=((w&0xfffff000)+sx(v>>20,12))&0xffffffff
    check(a,'a1 LUI+ADDI address',hex(ptr),hex(expected))
    hdr=raw(ptr,28); words=list(struct.unpack('<7I',hdr)); size=words[3]; data=words[4]
    assert words==[0x119,0,0,size,data,0,0] and data==ptr+28
    png=raw(data,size); assert png[:8]==b'\x89PNG\r\n\x1a\n'
    off=8; chunks=[]
    while off<len(png):
        n=int.from_bytes(png[off:off+4],'big'); typ=png[off+4:off+8]; payload=png[off+8:off+8+n]; crc=int.from_bytes(png[off+8+n:off+12+n],'big')
        assert zlib.crc32(typ+payload)&0xffffffff==crc
        chunks.append(typ.decode()); off+=12+n
    assert chunks[0]=='IHDR' and chunks[-1]=='IEND' and off==len(png)
    width,height=struct.unpack('>II',png[16:24])
    resources.append(dict(category=cls,constant_instruction=hex(a),descriptor=hex(ptr),descriptor_bytes=hdr.hex(),payload=hex(data),payload_size=size,width=width,height=height,png_chunks=chunks))
model=SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model.read_text().splitlines(); excerpts=[]
for name in [':th.extu rd,rs1,15,0 ',':th.mvnez ']:
    s=next(i for i,l in enumerate(lines) if l.startswith(name)); e=next(i for i in range(s+1,len(lines)) if lines[i]=='}')
    excerpts.append(dict(start_line=s+1,end_line=e+1,text='\n'.join(lines[s:e+1])))
strings=[]
for a in [0xa0269c4c,0xa056af14,0xa056d750,0xa0569848,0xa0569ac8]:
    o=a-0xa0000000+0x1000; end=image.index(b'\0',o); strings.append(dict(address=hex(a),text=image[o:end].decode(errors='replace')))
result=dict(static_only=True,rom=str(ROM),mapping='offset = VA - 0xa0000000 + 0x1000',windows=windows,encoding_checks=checks,resources=resources,strings=strings,model=dict(path=str(model),excerpts=excerpts),historical_provenance=provenance,limitations=['No execution, emulation, input replay or network/device access.','Decoder registration and exact info callback remain unresolved; update conditional on success.','Resource IDs are address identities, not authenticated original symbol names.'])
(OUT/'instruction-evidence.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(OUT/'instructions.txt').write_text('\n\n'.join(w['name']+'\n'+'\n'.join(r['address']+' '+r['bytes']+' '+r['instruction'] for r in w['rows']) for w in windows)+'\n',encoding='utf-8')
summary=dict(result='passed',core_functions=len(entries),necessary_predicate_dependencies=2,windows=len(windows),bytes=sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),instructions=sum(len(w['rows']) for w in windows),independent_encoding_checks=len(checks),vendor_words=len(vendor),resources=len(resources),png_crc_validated=16,unknown_instructions=0)
(OUT/'review-index.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary)); print(json.dumps(resources,ensure_ascii=False)); print(json.dumps(strings,ensure_ascii=False))
