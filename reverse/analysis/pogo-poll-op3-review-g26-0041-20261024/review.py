"""G26: independent sparse operand-field checks, no target or author-script use."""
from pathlib import Path
import json

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
BASE=0x9ffff000
SHA='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
assert ROM.stat().st_size==6769704
checks=[];rows=[]
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def bits(v,a,n):return (v>>a)&((1<<n)-1)
def eq(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
def raw(pc):
    assert pc in {0xa009e104,0xa009e108,0xa009e10c,0xa009e10e,0xa009e110,
                  0xa009e1a6,0xa009e1aa,0xa009e1b6,0xa009e1ba,0xa009e1be,
                  0xa009e1c4,0xa009e1ca,0xa009e1ce,0xa009e1d2}
    with ROM.open('rb') as f:
        f.seek(pc-BASE);r=f.read(2)
        if r[0]&3==3:r+=f.read(2)
    rows.append(dict(pc=hex(pc),offset=hex(pc-BASE),raw=r.hex()))
    return int.from_bytes(r,'little')
for pc,rd,src in [(0xa009e104,20,14),(0xa009e108,18,15),
                  (0xa009e10c,21,10),(0xa009e10e,22,13)]:
    v=raw(pc)
    eq(hex(pc)+' C.MV binding',[v&3,v>>12,bits(v,7,5),bits(v,2,5)],[2,8,rd,src])
v=raw(0xa009e110)
imm=(bits(v,31,1)<<12)|(bits(v,7,1)<<11)|(bits(v,25,6)<<5)|(bits(v,8,4)<<1)
eq('nonfallback branch',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),0xa009e110+sx(imm,13)],
   [99,1,14,15,0xa009e168])
v=raw(0xa009e1a6)
eq('fd arithmetic sign word',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),bits(v,20,5),v>>25],
   [19,15,5,20,31,32])
for pc,src,off in [(0xa009e1aa,15,0xc),(0xa009e1b6,21,4),(0xa009e1ba,22,0x18),
                   (0xa009e1be,20,8),(0xa009e1ce,9,0x20),(0xa009e1d2,20,0x24)]:
    v=raw(pc)
    eq(hex(pc)+' SW entry field',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),
                                  sx((bits(v,25,7)<<5)|bits(v,7,5),12)],[35,2,18,src,off])
v=raw(0xa009e1c4)
eq('new submission j shifted2',[v&3,v>>13,bits(v,7,5),bits(v,12,1),bits(v,2,5)],[2,0,9,0,2])
v=raw(0xa009e1ca)
eq('OR preserves op=3 low bits',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),bits(v,20,5),v>>25],
   [51,9,6,9,22,0])

g22_path=MAIN/'reverse/analysis/pogo-poll-submit-review-g22-0041-20261024/review-result.json'
g22=json.loads(g22_path.read_text(encoding='utf8'))
eq('G22 inherited original',g22['original']['inherited_catalog_sha256'],SHA)
old={r['address']:r for r in g22['checks']}
refs=['0xa009e172','0xa009e174','0xa009e18a','0xa009e1a2','0xa009e1ae','0xa009e1b2',
      '0xa009e1e8','0xa009e1f0']
eq('selected common references present',all(a in old for a in refs),True)
eq('conditional tail branch old target',old['0xa009e1e8']['meaning'],'0xa009e1f4')
eq('next-hop old target',old['0xa009e1f0']['meaning'],'0xa009dfcc')
g24_path=MAIN/'reverse/analysis/pogo-poll-ring-consume-review-g24-0041-20261024/review-evidence.json'
g24=json.loads(g24_path.read_text(encoding='utf8'))
eq('G24 inherited original',g24['identity']['sha256_inherited'],SHA)
g24raw={r['address']:r['raw'] for r in g24['raw']}
eq('actual caller sets a3=3',g24raw['0xa009e0de'],'8d46')
caller_refs=['0xa009e0a4','0xa009e0a6','0xa009e0ac','0xa009e0b0',
             '0xa009e0d0','0xa009e0d4','0xa009e0d6','0xa009e0d8','0xa009e0da',
             '0xa009e0dc','0xa009e0de','0xa009e0e0','0xa009e0e2']
eq('old completion index/source/caller anchors present',all(a in g24raw for a in caller_refs),True)

out=dict(status='PASS',task='G26',claim='G19/5',baseline='bd457a6',reviewer='/root/a56',author='/root/g23 G25',
         identity=dict(path=str(ROM),length=6769704,sha256_inherited=SHA,mapping='VA-0x9ffff000',hash_recomputed=False),
         method='Direct independent RV32/RVC operand fields; no Capstone or author-script execution',
         checks=checks,rows=rows,inherited=dict(
             g22=dict(path=str(g22_path),references=refs,rerun=False),
             g24=dict(path=str(g24_path),references=caller_refs,rerun=False)),
         conclusion='Limited acceptance, semantic corrections 0, new op-specific body 0',
         limits=['Valid aligned source/destination and sufficient storage remain conditions',
                 'Old completion index I and new submission j are different definitions, not proven unequal runtime values',
                 'Copy destination address is stored; pointer nonaliasing/independent lifetime not established',
                 'Normal reachability, diagnostics, fallback, other op and recursive/native bodies not expanded',
                 'No target/instruction/model execution or input experiment'])
(OUT/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),new_anchors=len(rows),new_bytes=sum(len(r['raw'])//2 for r in rows))))
