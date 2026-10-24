"""A66 mode2 open/close callbacks, static fields only; never performs file IO."""
from pathlib import Path
import json
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin';BASE=0x9ffff000
OUT=Path(__file__).resolve().parent
assert ROM.stat().st_size==6769704
checks=[];rows={}
def bits(v,a,n):return (v>>a)&((1<<n)-1)
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def w(pc):
    assert 0xa00ef468<=pc<0xa00ef55e or 0xa008ab4c<=pc<0xa008ab76
    if pc not in rows:
        with ROM.open('rb') as f:
            f.seek(pc-BASE);r=f.read(2)
            if r[0]&3==3:r+=f.read(2)
        rows[pc]=r
    return int.from_bytes(rows[pc],'little')
def eq(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
def ci(pc,f3,rd,imm):
    v=w(pc);eq(hex(pc)+' CI',[v&3,v>>13,bits(v,7,5),sx((bits(v,12,1)<<5)|bits(v,2,5),6)],
               [1,f3,rd,imm])
def mv(pc,rd,src):
    v=w(pc);eq(hex(pc)+' C.MV',[v&3,v>>12,bits(v,7,5),bits(v,2,5)],[2,8,rd,src])
def it(pc,op,rd,f3,base,imm):
    v=w(pc);eq(hex(pc)+' I-format',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),sx(v>>20,12)],
               [op,rd,f3,base,imm])
def branch(pc,f3,r1,r2,target):
    v=w(pc);i=(bits(v,31,1)<<12)|(bits(v,7,1)<<11)|(bits(v,25,6)<<5)|(bits(v,8,4)<<1)
    eq(hex(pc)+' B-format',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),pc+sx(i,13)],
       [99,f3,r1,r2,target])
def jal(pc,target):
    v=w(pc);i=(bits(v,31,1)<<20)|(bits(v,12,8)<<12)|(bits(v,20,1)<<11)|(bits(v,21,10)<<1)
    eq(hex(pc)+' JAL',[v&127,bits(v,7,5),pc+sx(i,21)],[111,1,target])

def frame(pc,imm):
    v=w(pc);off=(bits(v,11,2)<<4)|(bits(v,7,4)<<6)|(bits(v,6,1)<<2)|(bits(v,5,1)<<3)
    eq(hex(pc)+' s0=sp+frame',[v&3,v>>13,8+bits(v,2,3),off],[0,0,8,imm])
def lwsp(pc,rd,off):
    v=w(pc);im=(bits(v,12,1)<<5)|(bits(v,4,3)<<2)|(bits(v,2,2)<<6)
    eq(hex(pc)+' stack restore',[v&3,v>>13,bits(v,7,5),im],[2,2,rd,off])
frame(0xa00ef476,0x110)
ci(0xa00ef478,2,15,1);mv(0xa00ef47a,13,11)
branch(0xa00ef47e,0,12,15,0xa00ef494);eq('mode2 first compare false',2==1,False)
ci(0xa00ef482,2,15,2);ci(0xa00ef484,2,9,1)
branch(0xa00ef486,0,12,15,0xa00ef494);eq('mode2 branch true',2==2,True)
v=w(0xa00ef494);eq('format literal high',[v&127,bits(v,7,5),v&0xfffff000],[55,12,0xa0637000])
it(0xa00ef498,19,12,0,12,0x1e4);eq('format literal address',0xa0637000+0x1e4,0xa06371e4)
it(0xa00ef49c,19,11,0,0,256);it(0xa00ef4a0,19,10,0,8,-0x110)
jal(0xa00ef4a4,0xa008ab4c)
it(0xa00ef4a8,19,12,0,0,0x1b6);mv(0xa00ef4ac,11,9)
it(0xa00ef4ae,19,10,0,8,-0x110);jal(0xa00ef4b2,0xa003f4f6)
it(0xa00ef4b6,19,15,0,10,1);branch(0xa00ef4ba,5,10,0,0xa00ef4f0)
it(0xa00ef4f0,3,1,2,2,0x10c);it(0xa00ef4f4,3,8,2,2,0x108);it(0xa00ef4f8,3,9,2,2,0x104)
mv(0xa00ef4fc,10,15);eq('open return ra',w(0xa00ef500),0x8082)
# Nonnegative success and the explicit error-to-zero boundary only.
jal(0xa00ef4be,0xa00267c0);it(0xa00ef4c2,3,17,2,10,0)
jal(0xa00ef4ea,0xa008b51a);ci(0xa00ef4ee,2,15,0)

it(0xa00ef50c,19,9,0,11,-1);mv(0xa00ef510,10,9);jal(0xa00ef512,0xa0026888)
mv(0xa00ef516,15,10);ci(0xa00ef518,2,10,0);branch(0xa00ef51a,5,15,0,0xa00ef554)
jal(0xa00ef51e,0xa00267c0);it(0xa00ef522,3,16,2,10,0)
jal(0xa00ef546,0xa008b51a);jal(0xa00ef54a,0xa00267c0)
v=w(0xa00ef54e)
eq('close error rereads returned slot',[v&3,v>>13,8+bits(v,2,3),8+bits(v,7,3),
       (bits(v,10,3)<<3)|(bits(v,6,1)<<2)|(bits(v,5,1)<<6)],[0,2,10,10,0])
jal(0xa00ef550,0xa00ea524)
lwsp(0xa00ef554,1,12);lwsp(0xa00ef556,8,8);lwsp(0xa00ef558,9,4)
ci(0xa00ef55a,0,2,16)
eq('close return ra',w(0xa00ef55c),0x8082)

# Specifically registered literal and argument-forwarding wrapper only.
with ROM.open('rb') as f:
    f.seek(0xa06371e4-BASE);literal=bytearray()
    for _ in range(64):
        z=f.read(1);literal+=z
        if z==b'\x00':break
eq('registered NUL format literal',bytes(literal).hex(),'2f257300')
eq('formatter wrapper stack allocation',w(0xa008ab4c),0x7139)
v=w(0xa008ab52)
frame_imm=(bits(v,11,2)<<4)|(bits(v,7,4)<<6)|(bits(v,6,1)<<2)|(bits(v,5,1)<<3)
eq('formatter wrapper s0 frame',[v&3,v>>13,8+bits(v,2,3),frame_imm],[0,0,8,32])
for pc,src,off in [(0xa008ab54,13,12),(0xa008ab5a,14,16),(0xa008ab5c,15,20)]:
    v=w(pc)
    eq(hex(pc)+' save argument word',[v&3,v>>13,8+bits(v,2,3),8+bits(v,7,3),
        (bits(v,10,3)<<3)|(bits(v,6,1)<<2)|(bits(v,5,1)<<6)],[0,6,src,8,off])
it(0xa008ab56,19,13,0,8,12)
for pc,src,off in [(0xa008ab5e,16,24),(0xa008ab62,17,28),(0xa008ab66,13,-20)]:
    v=w(pc)
    eq(hex(pc)+' save varargs pointer/word',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),
       sx((bits(v,25,7)<<5)|bits(v,7,5),12)],[35,2,8,src,off])
jal(0xa008ab6a,0xa0053252)
lwsp(0xa008ab6e,1,28);lwsp(0xa008ab70,8,24)
v=w(0xa008ab72)
im=(bits(v,12,1)<<9)|(bits(v,6,1)<<4)|(bits(v,5,1)<<6)|(bits(v,3,2)<<7)|(bits(v,2,1)<<5)
eq('formatter stack restore leaves a0',[v&3,v>>13,bits(v,7,5),sx(im,10)],[1,3,2,64])
eq('formatter wrapper return ra',w(0xa008ab74),0x8082)

idx_path=MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
idx=json.loads(idx_path.read_text(encoding='utf8'));meta=[]
for address in ['0xa00ef468','0xa00ef502','0xa008ab4c','0xa003f4f6','0xa0026888']:
    f=next(f for f in idx['functions'] if f['address']==address)
    meta.append(dict(address=address,extent=f['extent'],direct_calls=f['direct_calls'],
                     historical_dossier=f['historical_dossier']))
eq('callback owners known from old source path',
   all(any(r.get('owner',{}).get('procedure')==a for r in idx['source_paths'][321]['references'])
       for a in ['0xa00ef468','0xa00ef502']),True)
out=dict(status='PASS',task='A66',claim='J08/7',baseline='bd457a6',
    identity=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
    sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',hash_recomputed=False),
    checks=checks,rows=[dict(address=hex(p),offset=hex(p-BASE),raw=r.hex()) for p,r in sorted(rows.items())],
    inherited=dict(index=str(idx_path),metadata=meta,
        interface='A47/A49 (D,pathSuffix,2)/(D,H); cache/reload/clear inherited, not rerun',
        slot_binding='A64 pending A65 at dispatch; callback bodies seeded independently by ROM source owners'),
    literal=dict(address='0xa06371e4',bytes=bytes(literal).hex(),text='/%s',read_limit=64,bytes_read=len(literal),stop_at_nul=True),
    format_bridge='a008ab4c saves pathSuffix as first vararg at its frame s0+0xc; passes original buf/256/format and a3=&saved-varargs to a0053252; lower formatter output bytes remain unverified',
    contract='mode2 passes flags word1, literal /%s and pathSuffix/buffer256 through registered argument wrapper, calls open wrapper(buf,1,0x1b6); signed fd>=0 -> H=low32(fd+1), negative normal logging ->H0. close decodes H-1 to wrapper, nonnegative result ->0; negative rereads error slot after log and returns conversion service result.',
    limits=['Only registered formatting wrapper/literal inspected; no lower formatter/open/close/allocator/error-map body or real file/device IO',
            'H is encoded word value, not FILE pointer or separately allocated object',
            'Same open/close runtime handle and no fd reuse/intervening close remain conditions',
            'No concrete filesystem/version/actual default photo mode1 observation',
            'No target/instruction/model/old-script/input execution or shared REA change'])
(OUT/'evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),sample_instructions=len(rows),sample_bytes=sum(map(len,rows.values())))))
