"""F23: existing caller bytes/metadata only, no ROM or callee-body access."""
from pathlib import Path
import json
import re
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
F13=MAIN/'reverse/analysis/miio-native-queue-f13-0041-20261024/evidence.json'
j=json.loads(F13.read_text(encoding='utf8'))
old={int(r['pc'],16):r for r in j['rows']}
checks=[]
def bits(v,a,n):return (v>>a)&((1<<n)-1)
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def w(pc):return int.from_bytes(bytes.fromhex(old[pc]['raw']),'little')
def eq(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
def ci(pc,rd,src):
    v=w(pc);eq(hex(pc)+' C.MV',[v&3,v>>12,bits(v,7,5),bits(v,2,5)],[2,8,rd,src])
def cb(pc,f3,reg,target):
    v=w(pc);i=(bits(v,12,1)<<8)|(bits(v,10,2)<<3)|(bits(v,5,2)<<6)|(bits(v,3,2)<<1)|(bits(v,2,1)<<5)
    eq(hex(pc)+' compressed gate',[v&3,v>>13,8+bits(v,7,3),pc+sx(i,9)],[1,f3,reg,target])
def jal(pc,target):
    v=w(pc);i=(bits(v,31,1)<<20)|(bits(v,12,8)<<12)|(bits(v,20,1)<<11)|(bits(v,21,10)<<1)
    eq(hex(pc)+' direct call',[v&127,bits(v,7,5),pc+sx(i,21)],[111,1,target])
v=w(0xa0197ac2)
eq('caller flag LUI',[v&127,bits(v,7,5),v&0xfffff000],[55,15,0x62fc6000])
v=w(0xa0197ac6)
eq('caller flag word load',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),sx(v>>20,12)],
   [3,15,2,15,0x34])
eq('exact flag address',0x62fc6000+0x34,0x62fc6034)
cb(0xa0197aca,6,15,0xa0197ae8)
for pc,rd,off in [(0xa0197ae8,14,0x22),(0xa0197aec,15,0x20)]:
    v=w(pc);eq(hex(pc)+' signed halfword load',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),sx(v>>20,12)],
               [3,rd,1,9,off])
v=w(0xa0197af0);i=(bits(v,31,1)<<12)|(bits(v,7,1)<<11)|(bits(v,25,6)<<5)|(bits(v,8,4)<<1)
eq('signed compare routes to quick getter',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),0xa0197af0+sx(i,13)],
   [99,4,14,15,0xa0197acc])
v=w(0xa0197af4)
eq('actual a1 is word(Q)',[v&3,v>>13,8+bits(v,2,3),8+bits(v,7,3),
       (bits(v,10,3)<<3)|(bits(v,6,1)<<2)|(bits(v,5,1)<<6)],[0,2,11,10,0])
ci(0xa0197af6,10,9);jal(0xa0197af8,0xa0131920)
cb(0xa0197afc,6,10,0xa0197acc)
jal(0xa0197acc,0xa01318de);cb(0xa0197ad0,7,10,0xa0197b12)
ci(0xa0197ab8,20,12);ci(0xa0197aba,19,11)
ci(0xa0197b12,11,10);ci(0xa0197b14,13,20);ci(0xa0197b16,12,19);ci(0xa0197b18,10,9)
jal(0xa0197b1a,0xa01949f0)
defs=[r for r in j['rows'] if 0xa0197a8e<=int(r['pc'],16)<0xa0197acc and re.match(
      r'(?:c\.)?(?:mv|addi|li|lui|lw|add|sub) a0,',r['asm'])]
eq('direct flag-zero route retains original a0=Q until af6',defs,[])
eq('no retained rows in quick-getter-zero fallthrough interval',
   [p for p in old if 0xa0197ad2<=p<0xa0197ae8],[])
eq('direct nonzero callee result goes to restore',old[0xa0197afe]['asm'],'csrw mstatus, s2')
f14_path=MAIN/'reverse/analysis/miio-native-queue-review-f14-0041-20261024/review-result.json'
f14=json.loads(f14_path.read_text(encoding='utf8'))
eq('F14 no retained missing interval assertions',
   [x for x in f14['checks'] if isinstance(x,dict) and isinstance(x.get('address'),str)
    and 0xa0197ad2<=int(x['address'],16)<0xa0197ae8],[])
index_path=MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
idx=json.loads(index_path.read_text(encoding='utf8'));f=next(x for x in idx['functions'] if x['address']=='0xa0131920')
eq('callee old dossier absent',f['historical_dossier'],None);eq('callee dossier list absent',f['dossiers'],[])
eq('callee historical contract absent',f['historical_contracts'],[])
pcs=[0xa0197ab8,0xa0197aba,0xa0197abc,0xa0197abe,0xa0197ac2,0xa0197ac6,0xa0197aca,
     0xa0197acc,0xa0197ad0,0xa0197ae8,0xa0197aec,0xa0197af0,0xa0197af4,0xa0197af6,
     0xa0197af8,0xa0197afc,0xa0197afe,0xa0197b12,0xa0197b14,0xa0197b16,0xa0197b18,0xa0197b1a]
out=dict(status='PASS-old-caller-only',task='F23',claim='F11/8',baseline='bd457a6',
    identity=j['identity'],sources=dict(f13=str(F13),f14=str(f14_path),index=str(index_path)),
    checks=checks,selected_rows=[old[p] for p in pcs],callee_metadata=dict(
    address=f['address'],extent=f['extent'],direct_calls=f['direct_calls']),
    actual_call=dict(callsite='0xa0197af8',target='0xa0131920',a0='K',a1='word(Q)',
         a2='n still present on direct flag-zero route; formal use unknown',
         a4='sign-extended LH(K+0x22) used by caller compare; formal use unknown',
         a5='sign-extended LH(K+0x20) used by caller compare; formal use unknown',
         a3_a6_a7='not assigned by selected caller route; formal argument count unknown',
         outM='No explicit output-M pointer or direct returned-M-to-copy edge established'),
    return_connection='a0131920 returns zero -> retry a01318de; nonzero -> restore mstatus and return same a0. Only nonzero a01318de result goes to copy call.',
    source_length='s3=original source, s4=n, forwarded later as a2/a3 under normal callee-preserved register ABI; callee memory retention/access unknown',
    limits=['No ROM/new decompilation/target/model/old-script execution',
            'No body of a0131920, timed send a0197b32, scheduler or quick getter expansion',
            'No outM, wait semantics, real flag/thread state or memory lifetime inferred',
            'Quick-getter-zero fallthrough [a0197ad2,a0197ae8) missing in selected old rows; not a global absence proof'])
(OUT/'evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status=out['status'],checks=len(checks),selected_old_rows=len(pcs),new_rom_bytes=0)))
