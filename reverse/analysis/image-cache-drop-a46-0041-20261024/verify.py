"""A46 bounded static normal-path evidence. Reads original ROM; executes no target."""
from pathlib import Path
import json
import capstone

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
data = ROM.read_bytes()
def read(a, n):
    o = a - 0x9ffff000
    assert 0 <= o <= len(data)-n
    return data[o:o+n]
def word(a): return int.from_bytes(read(a, 4), 'little')
def sx(v,n): return (v ^ (1 << (n-1))) - (1 << (n-1))
checks=[]
def eq(label,a,v,e):
    assert v == e,(label,hex(a),v,e)
    checks.append(dict(label=label,address=hex(a),actual=v,expected=e))
def raw(a,b): eq('original instruction',a,read(a,len(bytes.fromhex(b))).hex(),b)
def jal(a,t):
    w=word(a); v=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    eq('JAL target/register',a,[w&127,(w>>7)&31,(a+sx(v,21))&0xffffffff],[111,1,t])
def pair(a,t):
    x,y=word(a),word(a+4)
    eq('AUIPC/JALR fields',a,[x&127,(x>>7)&31,y&127,(y>>7)&31,(y>>15)&31],[23,1,103,1,1])
    eq('AUIPC/JALR target',a,(a+sx(x&0xfffff000,32)+sx(y>>20,12))&0xfffffffe,t)

# Reuse A27's complete ten-word table by reference; check only the two new slots.
old=json.loads((HERE.parent/'image-cache-cleanup-a27-0041-20261023/evidence.json').read_text())
for off,addr in [(0x18,0xa00ebf7c),(0x1c,0xa00ec084)]:
    eq('inherited slot identity',0xa0263afc+off,word(0xa0263afc+off),int(old['backend_table'][off//4],16))
    eq('new slot target',0xa0263afc+off,word(0xa0263afc+off),addr)
for a,t in [(0xa0089106,0xa019cf58),(0xa0089112,0xa019cf58)]: pair(a,t)
for a,t in [(0xa00ec018,0xa00ea832),(0xa00ec058,0xa00ea9a6),(0xa00ec05e,0xa008b6a6),(0xa00ec068,0xa0089d02),(0xa00ec06e,0xa008ab8a),(0xa00ec172,0xa008b604),(0xa00ec1a2,0xa008b51a),(0xa00ec1d0,0xa008ab8a),(0xa00ec1d6,0xa008ab8a),(0xa00ec136,0xa008ae42),(0xa008ae4c,0xa008adf4),(0xa008ae2e,0xa0089d02),(0xa008ae34,0xa008ab8a)]: jal(a,t)
for a,b in [(0xa0089102,'1de1'),(0xa008910e,'03a5c411'),(0xa019cfac,'1c41'),(0xa019cfae,'8145'),(0xa019cfb0,'dc4f'),(0xa019cfb2,'8297'),(0xa00ec028,'9c4c'),(0xa00ec02a,'4a85'),(0xa00ec02c,'b285'),(0xa00ec02e,'8297'),(0xa00ec030,'dc5c'),(0xa00ec034,'8297'),(0xa00ec03a,'dcc4'),(0xa00ec0e0,'03294503'),(0xa00ec17a,'11e9'),(0xa00ec17c,'9c4c'),(0xa00ec17e,'d685'),(0xa00ec180,'6685'),(0xa00ec182,'8297'),(0xa00ec184,'9c58'),(0xa00ec188,'03294900'),(0xa00ec130,'23a20402'),(0xa00ec13a,'23a60400'),(0xa00ec1cc,'03250901'),(0xa008ae4a,'8145')]: raw(a,b)
windows=[('normal NULL-source all-key API',0xa00890f6,0xa008911a),('generic drop_all dispatch',0xa019cfac,0xa019cfb4),('single drop lookup and cleanup',0xa00ec00c,0xa00ec03e),('single drop remove/delete/unlink',0xa00ec046,0xa00ec072),('all traversal state',0xa00ec0e0,0xa00ec0ee),('all final root/list/used clearing',0xa00ec126,0xa00ec13e),('all ref gate and cleanup/next',0xa00ec158,0xa00ec18e),('nonzero-ref warning branch',0xa00ec18e,0xa00ec1aa),('all tree dismantling',0xa00ec1aa,0xa00ec1e6),('list clear entry',0xa008ae42,0xa008ae50),('list clear ownership loop',0xa008ae04,0xa008ae0c),('list next/remove/free',0xa008ae1c,0xa008ae3c)]
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows=[]
for name,start,end in windows:
    a=start
    while a<end:
        n=2 if int.from_bytes(read(a,2),'little')&3!=3 else 4
        assert a+n<=end
        b=read(a,n); ins=next(cs.disasm(b,a),None)
        assert ins is not None,(hex(a),b.hex())
        rows.append(dict(window=name,address=hex(a),offset=hex(a-0x9ffff000),bytes=b.hex(),asm=ins.mnemonic+' '+ins.op_str))
        a+=n
summary=dict(result='passed',static_only=True,windows=len(windows),bytes=sum(e-s for _,s,e in windows),instructions=len(rows),assertions=len(checks),vendor_words=0)
(HERE/'evidence.json').write_text(json.dumps(dict(summary=summary,rom=str(ROM),mapping='offset=VA-0x9ffff000',table_reused='../image-cache-cleanup-a27-0041-20261023/evidence.json#backend_table',checks=checks,instructions=rows,limitations=['No target execution; no shared REA target opened.', 'Diagnostic/assert bodies and full tree balancing excluded.', 'Function names are analyst mappings, not recovered source.']),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary))
