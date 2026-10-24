"""F16 independent field checks plus selected prior object-identity rows."""
from pathlib import Path
import json
import re
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
OUT=Path(__file__).resolve().parent
BASE=0x9ffff000
assert ROM.stat().st_size==6769704
checks=[];rows={}
def b(v,a,n):return (v>>a)&((1<<n)-1)
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def w(pc):
    assert 0xa005f0c0<=pc<0xa005f14e or 0xa01ab564<=pc<0xa01ab634
    if pc not in rows:
        with ROM.open('rb') as f:
            f.seek(pc-BASE);r=f.read(2)
            if r[0]&3==3:r+=f.read(2)
        rows[pc]=r
    return int.from_bytes(rows[pc],'little')
def eq(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
def mv(pc,rd,src):
    v=w(pc);eq(hex(pc)+' C.MV',[v&3,v>>12,b(v,7,5),b(v,2,5)],[2,8,rd,src])
def li(pc,rd,imm):
    v=w(pc);eq(hex(pc)+' C.LI',[v&3,v>>13,b(v,7,5),sx((b(v,12,1)<<5)|b(v,2,5),6)],
               [1,2,rd,imm])
def sw(pc,src,base,off):
    v=w(pc);eq(hex(pc)+' SW',[v&127,b(v,12,3),b(v,15,5),b(v,20,5),sx((b(v,25,7)<<5)|b(v,7,5),12)],
               [35,2,base,src,off])
def it(pc,op,rd,f3,rs1,imm):
    v=w(pc);eq(hex(pc)+' I-format',[v&127,b(v,7,5),b(v,12,3),b(v,15,5),sx(v>>20,12)],
               [op,rd,f3,rs1,imm])
def branch(pc,f3,r1,r2,target):
    v=w(pc);i=(b(v,31,1)<<12)|(b(v,7,1)<<11)|(b(v,25,6)<<5)|(b(v,8,4)<<1)
    eq(hex(pc)+' B-format',[v&127,b(v,12,3),b(v,15,5),b(v,20,5),pc+sx(i,13)],
       [99,f3,r1,r2,target])
def cb(pc,reg,target):
    v=w(pc);i=(b(v,12,1)<<8)|(b(v,10,2)<<3)|(b(v,5,2)<<6)|(b(v,3,2)<<1)|(b(v,2,1)<<5)
    eq(hex(pc)+' C.BNEZ',[v&3,v>>13,8+b(v,7,3),pc+sx(i,9)],[1,7,reg,target])
def cj(pc,target):
    v=w(pc);i=(b(v,12,1)<<11)|(b(v,11,1)<<4)|(b(v,9,2)<<8)|(b(v,8,1)<<10)
    i|=(b(v,7,1)<<6)|(b(v,6,1)<<7)|(b(v,3,3)<<1)|(b(v,2,1)<<5)
    eq(hex(pc)+' C.J',[v&3,v>>13,pc+sx(i,12)],[1,5,target])
mv(0xa005f0c0,18,10);mv(0xa005f0c4,20,11);mv(0xa005f0c6,19,12)
cb(0xa005f0cc,10,0xa005f0e4);mv(0xa005f0e4,9,10)
sw(0xa005f11a,20,8,-0x50);sw(0xa005f11e,19,8,-0x4c)
branch(0xa005f12a,5,10,0,0xa005f136)
li(0xa005f142,10,0);sw(0xa005f144,19,9,0x18);sw(0xa005f148,9,18,0)
mv(0xa01ab564,9,11);mv(0xa01ab568,18,10)
li(0xa01ab56a,12,12);li(0xa01ab56c,11,0);mv(0xa01ab56e,10,9)
it(0xa01ab586,3,15,2,18,12);branch(0xa01ab58a,0,15,10,0xa01ab5d4)
it(0xa01ab5d4,3,15,2,18,0x1c);cb(0xa01ab5d8,15,0xa01ab5e6)
sw(0xa01ab5da,9,18,0x1c);sw(0xa01ab5de,18,9,4)
mv(0xa01ab5e4,15,14);branch(0xa01ab5e6,1,9,15,0xa01ab628)
v=w(0xa01ab628)
eq('tail next C.LW',[v&3,v>>13,8+b(v,2,3),8+b(v,7,3),
    (b(v,10,3)<<3)|(b(v,6,1)<<2)|(b(v,5,1)<<6)],[0,2,14,15,0])
cb(0xa01ab62a,14,0xa01ab5e4);sw(0xa01ab62c,0,9,0)
v=w(0xa01ab630)
eq('tail publication C.SW',[v&3,v>>13,8+b(v,2,3),8+b(v,7,3),
    (b(v,10,3)<<3)|(b(v,6,1)<<2)|(b(v,5,1)<<6)],[0,6,9,15,0])
cj(0xa01ab632,0xa01ab5de)

source=MAIN/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
j=json.loads(source.read_text(encoding='utf8'));selected=[];old={}
spec={248:[0xa0064da6,0xa0064f4a,0xa0065438,0xa006543a,0xa0065448,0xa006544c,0xa0065450,
           0xa00653ac,0xa00653b0,0xa00653b4,0xa00653d8,0xa00653e0,0xa00653e4,
           0xa00653e8,0xa00653f8,0xa00653fa,0xa00653fe,0xa0065402,
           0xa0065406,0xa006548e,0xa006549e,0xa006556a,0xa006556c],
      195:[0xa011e3f8,0xa011e3fc,0xa011e428,0xa011e42a,0xa011e42c],
      96:[0xa011e08e,0xa011e09a,0xa011e09c,0xa011e09e],
      27:[0xa0110700,0xa0110702,0xa0110706,0xa0110708,0xa011070c,0xa011070e,0xa0110712,
          0xa0110714,0xa0110716,0xa0110718]}
for idx,pcs in spec.items():
    r=j['records'][idx];n=r['normalized_result']
    eq('old record '+str(idx)+' profile',r['analysis_profile']['digest'],
       '4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621')
    asm={int(s.split(':')[0],16):s for s in n['assembly']}
    for pc in pcs:old[pc]=asm[pc]
    selected.append(dict(record=idx,procedure=n['procedure']['address'],evidence_id=r['evidence_id'],
                         profile=r['analysis_profile']['digest'],assembly=[asm[p] for p in pcs]))
for pc,text in [(0xa0064f4a,'addi s7, s1, 0x128'),(0xa0065438,'c.li a2, 0x4'),
                (0xa0065448,'addi a0, s1, 0x140'),(0xa006544c,'jal ra, 0xa005f0b0'),
                (0xa0064da6,'addi s10, s1, 0xe8'),(0xa00653d8,'sw s10, -0x11c, s0'),
                (0xa00653ac,'lui a5, 0xa0110'),(0xa00653b0,'addi a5, a5, 0x6f2'),
                (0xa00653b4,'sw a5, -0x128, s0'),(0xa00653e0,'lui a5, 0xa011e'),
                (0xa00653e4,'addi a5, a5, 0x8e'),(0xa00653e8,'sw a5, 0x158, s1'),
                (0xa00653f8,'c.li a2, 0x10'),(0xa00653fa,'addi a1, s0, -0x128'),
                (0xa00653fe,'sw s7, 0x160, s1'),(0xa006548e,'addi a5, s1, 0x158'),
                (0xa006549e,'sw a5, 0x138, s1'),(0xa006556a,'c.mv a4, s7'),
                (0xa006556c,'addi a2, a2, 0x3d6'),
                (0xa0065402,'addi a0, s1, 0x164'),(0xa0065406,'jal ra, 0xa000589c'),
                (0xa011e3f8,'c.lw a4, 0x10, s1'),(0xa011e3fc,'c.lw a5, 0x0, a4'),
                (0xa011e428,'c.lw a1, 0x8, a4'),(0xa011e42a,'c.mv a0, s1'),
                (0xa011e42c,'c.jalr a5'),(0xa011e08e,'c.lw a5, 0x3c, a1'),
                (0xa011e09a,'c.mv a0, a1'),(0xa011e09c,'c.lw a1, 0x48, a1'),
                (0xa011e09e,'c.jalr a5'),(0xa0110700,'c.mv s1, a1'),
                (0xa0110702,'addi a1, a1, 0x8c'),(0xa0110706,'c.mv s2, a0'),
                (0xa0110708,'jal ra, 0xa01ab55a'),(0xa011070c,'c.lui a5, 0x1'),
                (0xa011070e,'addi a5, a5, -0x780'),
                (0xa0110712,'c.add s1, a5'),(0xa0110714,'c.mv a1, s1'),
                (0xa0110716,'c.mv a0, s2'),(0xa0110718,'jal ra, 0xa01ab55a')]:
    eq('old '+hex(pc),old[pc],hex(pc)+': '+text)
eq('L queue output identity',0x128+0x18,0x140)
eq('ctx0 identity',0xe8+0x8c,0x174);eq('ctx1 identity',0xe8+(0x1000-0x780),0x968)
eq('callback destination identity',0x128+0x3c,0x164)
eq('vtable user points L offset',0x158+8,0x160)
defs=[s for s in j['records'][248]['normalized_result']['assembly']
      if 0xa0064f4a<int(s.split(':')[0],16)<=0xa0065578 and re.match(
      r'0x[0-9a-f]+: (?:c\.)?(?:addi|mv|lw|lui|add|sub|li) s7,',s)]
eq('no selected ordinary s7 overwrite in old master interval',defs,[])

out=dict(status='PASS',task='F16',claim='F11/4',baseline='bd457a6',reviewer='/root/a56',author='F15 /root/f12',
    identity=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
    sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',hash_recomputed=False),
    checks=checks,rows=[dict(address=hex(p),offset=hex(p-BASE),raw=r.hex()) for p,r in sorted(rows.items())],
    inherited=dict(path=str(source),records=selected,author_scripts_run=False),
    conclusion='Limited acceptance: same-M normal setup and matching-thread attach bind both ctx+4 to L and L+18 to Q with initial Q+18=4',
    limits=['Normal creator/indirect-config/thread/attach outcomes are conditions, not observed execution',
            'No later-writer absence, all queues size4, lifecycle or actual send certification',
            'Copy16 configuration inherits validity/alignment; no copy4/allocator/callback expansion',
            'No shared REA, target, instruction, model, old-script, or input execution'])
(OUT/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),new_instructions=len(rows),new_bytes=sum(map(len,rows.values())))))
