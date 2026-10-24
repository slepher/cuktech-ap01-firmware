"""NR03 independent offline field decoder; ROM bytes are data, never executed.

stdlib only. N03 JSON supplies the claimed byte-table inventory, not decoding
or semantic results. No author module is imported or run. New glue expectations
and decoder below were independently written for this review.
"""
import json
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
ROM = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
checks = []

def require(name, actual, expected):
    assert actual == expected, (name, actual, expected)
    checks.append({'name': name, 'actual': actual, 'expected': expected})

def sx(n, bits):
    return n - (1 << bits) if n & (1 << (bits-1)) else n

def read(pc, n):
    return int.from_bytes(ROM[pc-BASE:pc-BASE+n], 'little')

def decode(pc):
    h = read(pc, 2)
    d = {'address': hex(pc), 'file_offset': pc-BASE}
    if h & 3 == 3:
        n = 4
        w = read(pc, 4)
        op, rd, f3, rs1, rs2 = w&127, (w>>7)&31, (w>>12)&7, (w>>15)&31, (w>>20)&31
        d.update(rd=rd, rs1=rs1, rs2=rs2, f3=f3)
        if op in (0x37, 0x17):
            d.update(op='lui' if op==0x37 else 'auipc', imm=w&0xfffff000)
        elif op in (0x13, 0x03, 0x67):
            assert op!=0x13 or f3==0
            d.update(op={0x13:'addi',0x03:'load',0x67:'jalr'}[op], imm=sx(w>>20,12))
        elif op==0x23:
            d.update(op='store', imm=sx(((w>>25)<<5)|((w>>7)&31),12))
            d.pop('rd')
        elif op==0x6f:
            imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
            d.update(op='jal', target=hex((pc+sx(imm,21))&0xffffffff))
        elif op==0x63:
            imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
            d.update(op='branch', target=hex((pc+sx(imm,13))&0xffffffff))
            d.pop('rd')
        else:
            raise AssertionError(('unhandled standard opcode',hex(pc),hex(w)))
    else:
        n=2
        q, f3, rd, rs2 = h&3, h>>13, (h>>7)&31, (h>>2)&31
        ci=sx(((h>>12)&1)*32+((h>>2)&31),6)
        if q==1 and f3 in (0,2,3):
            d.update(op={0:'c.addi',2:'c.li',3:'c.lui'}[f3], rd=rd, imm=ci*(4096 if f3==3 else 1))
        elif q==2 and f3==4 and (h>>12)&1==0 and rs2:
            d.update(op='c.mv', rd=rd, rs2=rs2)
        elif q==1 and f3==4 and ((h>>10)&3)==3 and ((h>>5)&3)==3:
            d.update(op='c.and', rd=8+((h>>7)&7),rs2=8+((h>>2)&7))
        elif q==0 and f3==2:
            off=(((h>>5)&1)<<6)|(((h>>10)&7)<<3)|(((h>>6)&1)<<2)
            d.update(op='c.lw',rd=8+((h>>2)&7),rs1=8+((h>>7)&7),imm=off)
        elif q==2 and f3==6:
            off=(((h>>7)&3)<<6)|(((h>>9)&15)<<2)
            d.update(op='c.swsp',rs1=2,rs2=rs2,imm=off)
        elif q==0 and f3==0:
            off=(((h>>7)&15)<<6)|(((h>>11)&3)<<4)|(((h>>5)&1)<<3)|(((h>>6)&1)<<2)
            d.update(op='c.addi4spn',rd=8+((h>>2)&7),rs1=2,imm=off)
        else:
            raise AssertionError(('unhandled compressed opcode',hex(pc),hex(h)))
    d.update(size=n, hex=ROM[pc-BASE:pc-BASE+n].hex())
    return d

def window(lo,hi):
    rows=[]
    while lo<hi:
        d=decode(lo); rows.append(d);lo+=d['size']
    assert lo==hi
    return rows

claims=json.loads((ROOT/'reverse/analysis/subscription-interface-n03-0041-20261024/static-checks.json').read_text())
for r in claims['retained_anchors']:
    pc=int(r['address'],16); raw=bytes.fromhex(r['hex'])
    require('claimed retained byte '+r['address'],ROM[pc-BASE:pc-BASE+len(raw)].hex(),r['hex'])
require('claimed retained count',len(claims['retained_anchors']),222)

windows=[window(0xa00b075e,0xa00b0774),window(0xa00b0774,0xa00b07c8),window(0xa00f2f38,0xa00f2f54)]
rows={int(d['address'],16):d for w in windows for d in w}
require('new contiguous byte length',sum(d['size'] for w in windows[1:] for d in w),112)
require('no write to s5 in registration/event glue',[d for w in windows[:2] for d in w if d.get('rd')==21],[])

def const_pair(a,b,rd,lui_rd=None):
    lui_rd=rd if lui_rd is None else lui_rd
    x,y=decode(a),decode(b)
    require('constant LUI '+hex(a),(x['op'],x['rd']),('lui',lui_rd))
    require('constant ADDI '+hex(b),(y['op'],y['rd'],y['rs1']),('addi',rd,lui_rd))
    return (x['imm']+y['imm'])&0xffffffff

def call_pair(a,b,target):
    x,y=decode(a),decode(b)
    require('call pair registers '+hex(a),(x['op'],x['rd'],y['op'],y['rd'],y['rs1']),('auipc',1,'jalr',1,1))
    require('call target '+hex(a),hex(((a+x['imm']+y['imm'])&0xffffffff)&~1),hex(target))

def move(pc,rd,rs):
    d=decode(pc);require('move '+hex(pc),(d['op'],d['rd'],d['rs2']),('c.mv',rd,rs))

require('control callback',hex(const_pair(0xa00b075e,0xa00b0768,10)),'0xa00f3952')
require('item callback',hex(const_pair(0xa00b0774,0xa00b077a,10)),'0xa00f5288')
require('delete callback',hex(const_pair(0xa00b07b4,0xa00b07be,11)),'0xa00f2f38')
move(0xa00b0766,11,21);move(0xa00b0778,11,21);move(0xa00b07c2,10,21)
call_pair(0xa00b076c,0xa00b0770,0xa01b29a0)
call_pair(0xa00b077e,0xa00b0782,0xa01b28ce)
for pc in (0xa00b0794,0xa00b07a2,0xa00b07b0,0xa00b07c4):
    require('event registration target '+hex(pc),decode(pc)['target'],'0xa01ad654')
require('event filter',(decode(0xa00b07ba)['rd'],decode(0xa00b07ba)['rs1'],decode(0xa00b07ba)['imm']),(12,0,41))
require('event userdata',(decode(0xa00b07b8)['op'],decode(0xa00b07b8)['rd'],decode(0xa00b07b8)['imm']),('c.li',13,0))
require('event code word load',tuple(decode(0xa00f2f38)[k] for k in ('op','rd','rs1','imm')),('c.lw',15,10,8))
require('filter mask',hex((decode(0xa00f2f3a)['imm']+decode(0xa00f2f3c)['imm'])&0xffffffff),'0xffff7fff')
require('filter AND',tuple(decode(0xa00f2f3e)[k] for k in ('op','rd','rs2')),('c.and',15,14))
require('filter compare',(decode(0xa00f2f44)['f3'],decode(0xa00f2f44)['rs1'],decode(0xa00f2f44)['rs2'],decode(0xa00f2f44)['target']),(1,15,14,'0xa00f2fd0'))
require('original target load',tuple(decode(0xa00f2f54)[k] for k in ('op','rd','rs1','imm')),('c.lw',9,10,4))
require('state word load',tuple(decode(0xa00f2f56)[k] for k in ('op','rd','rs1','f3','imm')),('load',18,9,2,16))
require('state nonzero branch',tuple(decode(0xa00f2f5a)[k] for k in ('f3','rs1','rs2','target')),(1,18,0,'0xa00f2f8c'))
require('delete control key',hex(const_pair(0xa00f2f8c,0xa00f2f90,10)),'0xa00f3952')
require('control unsubscribe',decode(0xa00f2f94)['target'],'0xa01b2966')
require('item head',hex(const_pair(0xa00f2f98,0xa00f2fb6,10)),'0x62fcb530')
require('delete item key',hex(const_pair(0xa00f2fa4,0xa00f2fa8,14)),'0xa00f5288')
require('item unlink',decode(0xa00f2fba)['target'],'0xa0089d02')
move(0xa00f2fbe,10,18)
require('free saved state',decode(0xa00f2fc0)['target'],'0xa008ab8a')
require('clear state word',tuple(decode(0xa00f2fc4)[k] for k in ('op','rs1','rs2','f3','imm')),('store',9,0,2,16))
require('control head',hex(const_pair(0xa01b29a0,0xa01b29be,10,15)),'0x62fcb554')
require('register duplicate compares callback only',tuple(decode(0xa01b29e0)[k] for k in ('f3','rs1','rs2','target')),(0,10,12,'0xa01b29ea'))
require('duplicate hit returns directly',hex(read(0xa01b29ea,2)),'0x8082')
require('new userdata word store',tuple(decode(0xa01b29ce)[k] for k in ('op','rs1','rs2','f3','imm')),('store',10,18,2,4))
move(0xa01b29bc,9,10);move(0xa01b29c2,18,11)
require('notify snapshot reload',tuple(decode(0xa00a5394)[k] for k in ('op','rd','rs1','f3','imm')),('load',11,18,2,0x2cc))
require('notify mask halfword clear',tuple(decode(0xa00a539a)[k] for k in ('op','rs1','rs2','f3','imm')),('store',11,0,1,12))
require('notify callback word load',tuple(decode(0xa00a53ac)[k] for k in ('op','rd','rs1','imm')),('c.lw',15,9,0))
require('notify userdata word load',tuple(decode(0xa00a53b0)[k] for k in ('op','rd','rs1','imm')),('c.lw',10,9,4))
require('notify indirect call raw C.JALR',hex(read(0xa00a53b2,2)),'0x9782')
require('notify postcallback offset reload',tuple(decode(0xa00a53b4)[k] for k in ('op','rd','rs1','f3','imm')),('load',15,19,2,0))

result={'claim':'N03/NR03','status':'PASS','method':'independent stdlib RV32/RVC field extraction; no author code execution',
 'rom_identity_inherited':claims['rom_identity_inherited'],'rom_length':len(ROM),'base':hex(BASE),
 'check_count':len(checks),'retained_byte_rows':len(claims['retained_anchors']),
 'new_glue_bytes':112,'independently_decoded_glue_bytes':134,'windows':windows,'checks':checks,
 'limits':['222 retained rows check bytes, not independent interpretation of every legacy instruction.',
 'Vendor list-walk semantics and event dispatch ABI inherited from E06/E02; no whole-list or allocator re-certification.',
 'Static installation is not runtime delivery, public-delete trigger, synchronization, or reclamation proof.']}
(OUT/'independent-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('status','check_count','retained_byte_rows','new_glue_bytes','independently_decoded_glue_bytes')}))
