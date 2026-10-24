"""P-R08 offline review. Stdlib only; no author code import or execution."""
import json
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704

def u32(a):
    return int.from_bytes(rom[a-BASE:a-BASE+4], 'little')

def sx(x,n):
    return x-(1<<n) if x>>(n-1) else x

def jal(a):
    x=u32(a)
    assert x&127 == 0x6f
    n=((x>>31)<<20)|(((x>>12)&255)<<12)|(((x>>20)&1)<<11)|(((x>>21)&1023)<<1)
    return a+sx(n,21)

def store(a):
    x=u32(a)
    assert x&127 == 0x23
    return ((x>>12)&7,(x>>15)&31,(x>>20)&31,sx(((x>>25)<<5)|((x>>7)&31),12))

def branch(a):
    x=u32(a)
    assert x&127 == 0x63
    n=((x>>31)<<12)|(((x>>7)&1)<<11)|(((x>>25)&63)<<5)|(((x>>8)&15)<<1)
    return ((x>>12)&7,(x>>15)&31,(x>>20)&31,a+sx(n,13))

def cfields(a):
    x=u32(a)&65535
    return x&3,x>>13,(x>>7)&31,(x>>2)&31

def pair(a):
    x,y=u32(a),u32(a+4)
    assert x&127==0x17 and y&127==0x67
    return (a+sx(x&0xfffff000,32)+sx(y>>20,12))&0xffffffff

checks=[]
def ck(name, actual, expected):
    checks.append(dict(name=name,actual=actual,expected=expected,result='PASS' if actual==expected else 'FAIL'))
    assert actual==expected, (name,actual,expected)

# Independently chosen business windows, including full constructor identity bridge.
ranges=[('enter',0xa00a56d4,0xa00a5810),('exit',0xa00a4708,0xa00a4762),
 ('notify',0xa00a3df4,0xa00a3e54),('dispatch',0xa00a3a0e,0xa00a3a58),
 ('subscribe',0xa01b25e8,0xa01b2634),('remove',0xa01b25ae,0xa01b25e8),
 ('D5_exit',0xa00a5b2a,0xa00a5b54),('D4_exit',0xa00a5a2c,0xa00a5a64),
 ('ordinary24',0xa00a8856,0xa00a8870),('rediscover',0xa00a80a8,0xa00a81cc),
 ('constructor',0xa00fcd54,0xa00fd1ac),('appcallback',0xa00f6064,0xa00f61ae),
 ('callsiteA',0xa00b0554,0xa00b0570),('callsiteB',0xa00fed84,0xa00fedc0),
 ('DELETE',0xa00f42c6,0xa00f4378)]
windows=[]
for name,a,b in ranges:
    p=a
    boundaries=[]
    while p<b:
        h=int.from_bytes(rom[p-BASE:p-BASE+2],'little')
        n=4 if h&3==3 else 2
        assert p+n<=b
        boundaries.append(dict(address=hex(p),size=n,raw=rom[p-BASE:p-BASE+n].hex()))
        p+=n
    windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),raw=rom[a-BASE:b-BASE].hex(),boundaries=boundaries))

for a,t in [(0xa00a575e,0xa00a3df4),(0xa00a57b8,0xa01951e2),(0xa00a580a,0xa00a3df4),
 (0xa00a4734,0xa00a3df4),(0xa00a3e44,0xa00a3a0e),(0xa00a5b4e,0xa00a4708),
 (0xa00a5a5e,0xa00a56d4),(0xa00a8864,0xa00a56d4),(0xa00a8150,0xa00a5558),
 (0xa00a818c,0xa01951e2),(0xa00fd16a,0xa01b25e8),(0xa00fd1a6,0xa01ad654),
 (0xa00f433a,0xa01b25ae),(0xa00f4340,0xa008ab8a),
 (0xa00b056a,0xa00a56d4),(0xa00fed98,0xa00a56d4),(0xa00fedb8,0xa00a56d4)]:
    ck('JAL '+hex(a),hex(jal(a)),hex(t))
for a,v in [(0xa00a5768,(0,15,14,0x50c)),(0xa00a5772,(0,15,14,0x4f8)),
 (0xa00a5782,(2,14,15,0x6c0)),(0xa00a4724,(2,14,15,0x6c0)),
 (0xa00a4730,(0,15,14,0x4f8)),(0xa00a4740,(0,15,0,0x50c)),
 (0xa00a474e,(0,15,14,0x51c)),(0xa00fd18e,(2,21,18,4)),
 (0xa00fd196,(2,9,21,16)),(0xa00f4350,(2,18,0,16)),
 (0xa00f616a,(2,9,0,0x34)),(0xa00a3e40,(0,18,9,0)),
 (0xa00a8160,(2,14,15,0x6c0)),(0xa00a816c,(0,15,0,0)),
 (0xa00a8170,(0,15,0,0x30)),(0xa00a8174,(0,15,0,0x60)),
 (0xa00a8178,(0,15,0,0x90))]:
    ck('store '+hex(a),store(a),v)

for a,v in [(0xa00a56e6,(1,15,0,0xa00a5808)),(0xa00a5790,(1,14,15,0xa00a57f4)),
 (0xa00a3e0c,(0,15,10,0xa00a3e48)),(0xa00a5b44,(1,14,15,0xa00a5b58)),
 (0xa00a5a4a,(0,13,0,0xa00a5b4e)),(0xa00a8860,(1,14,15,0xa00a886a)),
 (0xa00f42d2,(1,15,14,0xa00f4376)),(0xa00f60da,(1,21,15,0xa00f60f6)),
 (0xa00f60fa,(0,14,15,0xa00f60e2)),(0xa00f6124,(1,14,15,0xa00f60c0))]:
    got=branch(a)
    ck('branch '+hex(a),[got[0],got[1],got[2],hex(got[3])],[v[0],v[1],v[2],hex(v[3])])
for a,t in [(0xa00a574c,0xa01b25e8),(0xa00a4752,0xa01b25ae)]:
    ck('AUIPC/JALR '+hex(a),hex(pair(a)),hex(t))
# RV32 compressed moves: opcode10/funct3=100, destination then source.
for a,rd,rs in [(0xa00fcdb6,18,10),(0xa00fd164,11,18),(0xa00fd1a4,10,9),
 (0xa00f433e,10,9),(0xa00f6078,9,10),(0xa00f607a,21,11),(0xa00f607c,22,12),
 (0xa00a3a48,12,20),(0xa00a3a4a,11,19)]:
    ck('c.mv '+hex(a),cfields(a),(2,4,rd,rs))

# Only after independent ROM bitfield checks, compare the author's DATA artifact.
author=json.loads((ROOT/'reverse/analysis/dock-ota-lifecycle-p08-0041-20261024/static-evidence.json').read_text())
for w in author['windows']:
    a=int(w['start'],16); b=int(w['end_exclusive'],16)
    ck('author window raw '+w['name'],rom[a-BASE:b-BASE].hex(),w['bytes_hex'])

# Old retained sources, not the author's script, establish semantic/profile provenance.
selected={}
cache={}
for address,s in author['sources'].items():
    path=s['retained']
    if path not in cache:
        cache[path]=json.loads((ROOT/path).read_text())
    obj=cache[path]
    for part in s['pointer'].strip('/').split('/'):
        obj=obj[int(part)] if isinstance(obj,list) else obj[part]
    isrecord='normalized_result' in obj
    eid=obj['evidence_id']
    profile=obj['analysis_profile']['digest'] if isrecord else obj['profile_digest']
    ck('source evidence '+address,eid,s['evidence_id'])
    ck('source profile '+address,profile,s['profile_digest'])
    body=obj['normalized_result'] if isrecord else obj
    if address in ['0xa00a56d4','0xa00a4708','0xa00a3df4','0xa00a3a0e','0xa01b25e8','0xa01b25ae']:
        for raw in body.get('raw_ranges',[]):
            off=raw['file_offset']; data=bytes.fromhex(raw['bytes_hex'])
            ck('old retained ROM raw '+address,rom[off:off+len(data)].hex(),data.hex())
    asm=[]
    for line in body.get('assembly',[]):
        loc=int(line.split(':')[0],16)
        if any(start<=loc<end for _,start,end in ranges):
            asm.append(line)
    small=address in ['0xa00a56d4','0xa00a4708','0xa00a3df4','0xa00a3a0e','0xa01b25e8','0xa01b25ae','0xa00f6064']
    selected[address]=dict(path=path,pointer=s['pointer'],evidence_id=eid,profile=profile,
      assembly=asm,pseudocode=body.get('pseudocode') if small else None,limitations=obj.get('limitations'))
    if isrecord:
        selected[address]['language']=obj['analysis_profile']['parameters']['language_id']
        ck('source ROM identity '+address,obj['subject']['digest']['sha256'],author['rom']['sha256_inherited'])

constructor=selected['0xa00fcd54']['assembly']
bridge=[line for line in constructor if 0xa00fcdb6<=int(line.split(':')[0],16)<=0xa00fd16a]
# Retain the necessary identity bridge; no decompiler-only identity.
selected['0xa00fcd54']['identity_bridge']=bridge
payload=dict(claim='P-R08',rom=dict(size=len(rom),mapping='VA-0x9ffff000',sha256_inherited=author['rom']['sha256_inherited']),
 windows=windows,checks=checks,sources=selected,
 limitations=['No execution or instruction simulation; standard bitfield extraction only.',
 'RV instruction length framing is not full semantic disassembly.',
 'th.lrw traversal semantics inherited, not independently decoded.',
 'No new REA session or evidence/profile; DELETE is raw-ROM/binding evidence.'])
(OUT/'independent-review.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
lines=[]
for address,s in selected.items():
    lines.extend([address+' '+s['evidence_id']+' '+s['profile'],s['path']+s['pointer']])
    asm=s.get('assembly') or []
    for line in asm:
        try: a=int(line.split(':')[0],16)
        except (ValueError,AttributeError): continue
        if any(start<=a<end for _,start,end in ranges): lines.append(line)
(OUT/'retained-selected.txt').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(dict(checks=len(checks),failures=sum(c['result']!='PASS' for c in checks),windows=len(windows),bytes=sum(b-a for _,a,b in ranges),framed_instructions=sum(len(w['boundaries']) for w in windows)),indent=2))
