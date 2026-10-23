"""A50: bounded original-ROM consumer ABI/holding evidence, no target execution."""
from pathlib import Path
import json
import capstone

HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=ROOT/'roms/0041/ap01-1.0.2_0041.bin'
data=ROM.read_bytes()
def read(a,n):
    o=a-0x9ffff000
    assert 0<=o<=len(data)-n
    return data[o:o+n]
def word(a):return int.from_bytes(read(a,4),'little')
def sx(v,n):return (v^(1<<(n-1)))-(1<<(n-1))
checks=[]
def eq(label,a,v,e):
    assert v==e,(label,hex(a),v,e)
    checks.append(dict(label=label,address=hex(a),actual=v,expected=e))
def raw(a,b):eq('original encoding',a,read(a,len(bytes.fromhex(b))).hex(),b)
def jal(a,t):
    w=word(a);v=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    eq('JAL target/register',a,[w&127,(w>>7)&31,(a+sx(v,21))&0xffffffff],[111,1,t])
def mem(a,op,f3,reg,base,imm):
    w=word(a);v=w>>20 if op==3 else ((w>>25)<<5)|((w>>7)&31)
    r=(w>>7)&31 if op==3 else (w>>20)&31
    eq('memory fields',a,[w&127,(w>>12)&7,r,(w>>15)&31,sx(v,12)],[op,f3,reg,base,imm])
for a,t in [(0xa010a5ea,0xa008b888),(0xa008b912,0xa008ab76),(0xa008ba00,0xa008aea0),(0xa008ba8e,0xa008ab76),(0xa008b9ce,0xa008ab76)]:jal(a,t)
for args in [(0xa010a5e2,3,4,14,10,16),(0xa008b8aa,35,2,0,13,0),(0xa008b8b4,3,2,20,10,4),(0xa008b8d6,3,2,19,14,8),(0xa008b8dc,3,2,23,14,12),(0xa008ba04,35,2,10,23,12),(0xa008ba0a,3,2,23,15,12),(0xa008ba6c,35,2,19,15,0),(0xa008b980,35,2,15,21,0)]:mem(*args)
for a,b in [(0xa010a5e6,'11cb'),(0xa010a5e8,'8146'),(0xa008b8a0,'aa84'),(0xa008b8a2,'2e8b'),(0xa008b8a4,'3289'),(0xa008b8a6,'b68a'),(0xa008b8ae,'c840'),(0xa008b8b8,'5c49'),(0xa008b8c2,'584d'),(0xa008b8cc,'232404fc'),(0xa008b8d0,'63020a1c'),(0xa008b91a,'9844'),(0xa008b922,'1c47'),(0xa008b926,'1cc7'),(0xa008b934,'c840'),(0xa008b936,'8c40'),(0xa008b93a,'5c4d'),(0xa008b93c,'8146'),(0xa008b940,'8297'),(0xa008b942,'c840'),(0xa008b94c,'8c40'),(0xa008b94e,'5c49'),(0xa008b952,'1307c4fc'),(0xa008b95a,'e286'),(0xa008b95c,'5a86'),(0xa008b95e,'8297'),(0xa008b996,'5285'),(0xa008b9a0,'5e86'),(0xa008b9a2,'8297'),(0xa008ba52,'c840'),(0xa008ba58,'8c40'),(0xa008ba5a,'5c49'),(0xa008ba60,'d286'),(0xa008ba62,'5e86'),(0xa008ba64,'8297'),(0xa008baa0,'2a8a'),(0xa008ba94,'8c40'),(0xa008ba96,'130784fc'),(0xa008ba9a,'ca86'),(0xa008ba9c,'5a86'),(0xa008ba9e,'8297')]:raw(a,b)
vendor={0xa008b96c:('th.mvnez s3,s2,a5',[11,1,33,19,18,15]),0xa008b9c6:('th.mveqz a2,s8,a5',[11,1,32,12,24,15]),0xa008b9ca:('th.extu a2,a2,30,0',[11,3,30,12,12,0]),0xa008ba86:('th.mveqz a2,s2,a5',[11,1,32,12,18,15])}
for a,(name,fields) in vendor.items():
    w=word(a);eq(name,a,[w&127,(w>>12)&7,w>>25,(w>>7)&31,(w>>15)&31,(w>>20)&31],fields)
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
text=model.read_text();rules=[]
for key in [':th.mveqz ',':th.mvnez ',':th.extu rd,rs1,30,0 ']:
    p=text.index(key);rules.append(text[p:text.index('\n}',p)+2])
windows=[('inherited mode consumer call',0xa010a5e2,0xa010a5ee),('reader prefix ABI and slot gates',0xa008b8a0,0xa008b8c6),('cache fields and hit range',0xa008b8d4,0xa008b8fc),('hit consume and cursor update',0xa008b90e,0xa008b928),('seek plus read ABI on partial hit',0xa008b932,0xa008b960),('actual count clamp and out count',0xa008b962,0xa008b984),('cache miss seek and bypass read',0xa008b9d4,0xa008b9f6),('buffer-holding allocation',0xa008b9f6,0xa008ba12),('fill callback and retained bounds/copy',0xa008ba52,0xa008ba94),('uncached read ABI',0xa008ba94,0xa008baa4)]
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows=[]
for name,start,end in windows:
    a=start
    while a<end:
        n=2 if int.from_bytes(read(a,2),'little')&3!=3 else 4
        assert a+n<=end
        b=read(a,n);i=next(cs.disasm(b,a),None)
        asm=i.mnemonic+' '+i.op_str if i else vendor[a][0]
        rows.append(dict(window=name,address=hex(a),bytes=b.hex(),asm=asm));a+=n
# Two vendor words outside exported windows are retained sparsely, not full paths.
for a in [0xa008b9c6,0xa008b9ca]:rows.append(dict(window='cross-cache copy clamp only',address=hex(a),bytes=read(a,4).hex(),asm=vendor[a][0]))
old=json.loads((ROOT/'reverse/rehost/weather-calendar-complete-0041.json').read_text(encoding='utf8'))
reuse=[]
for idx in [1,30]:
    r=old['evidence'][idx];s=r['stdout'].lower()
    reuse.append(dict(record=f'evidence/{idx}',address=r['address'],tool=r['tool'],has_full_callee_body='a008b888:' in s,matching_lines=[l for l in r['stdout'].splitlines() if 'a008b888' in l.lower() or ('a010a5e' in l.lower())],limit='Old objdump contains call sites, not this callee body; record30 stdout explicitly truncated.'))
summary=dict(result='passed',static_only=True,windows=len(windows),bytes=sum(e-s for _,s,e in windows)+8,instructions=len(rows),assertions=len(checks),vendor_words=len(vendor))
(HERE/'evidence.json').write_text(json.dumps(dict(summary=summary,rom=str(ROM),mapping='offset=VA-0x9ffff000',checks=checks,instructions=rows,vendor_rules=dict(path=str(model),rules=rules),reuse= reuse,limitations=['Known source-type1/mode1 is a static alternative, not a verified real photo execution.', 'No concrete D/callback/FS implementation authenticated.', 'No full 544-byte function export, decode algorithm or failed-I/O branch study.']),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary))
