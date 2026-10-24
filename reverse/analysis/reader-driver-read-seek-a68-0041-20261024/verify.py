"""A68 actual reader callbacks; original fields only, no lower IO body/run."""
import json
from pathlib import Path
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
assert ROM.stat().st_size==6769704
BASE=0x9ffff000
d=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
checks=[]
def raw(a,n):
    assert any(lo<=a and a+n<=hi for lo,hi in [(0xa00ef55e,0xa00ef5c8),(0xa00ef632,0xa00ef69c)])
    with ROM.open('rb') as f:f.seek(a-BASE);return f.read(n)
def inst(a,text):
    n=4 if int.from_bytes(raw(a,2),'little')&3==3 else 2
    b=raw(a,n);r=list(d.disasm(b,a))
    assert len(r)==1 and r[0].mnemonic+' '+r[0].op_str==text,(hex(a),text)
    checks.append(dict(address=hex(a),raw=b.hex(),instruction=text))
def sx(x,n):return x-(1<<n) if x&(1<<(n-1)) else x
def jal(a,target):
    w=int.from_bytes(raw(a,4),'little')
    q=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    assert (w&127,(w>>7)&31,a+sx(q,21))==(0x6f,1,target)
    checks.append(dict(address=hex(a),raw=raw(a,4).hex(),kind='independent-JAL-fields',target=hex(target)))
def branch(a,f,r1,r2,target):
    w=int.from_bytes(raw(a,4),'little')
    q=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,a+sx(q,13))==(0x63,f,r1,r2,target)
    checks.append(dict(address=hex(a),raw=raw(a,4).hex(),kind='independent-branch-fields',target=hex(target)))

for a,t in {
 0xa00ef55e:'c.addi sp, -0x20',0xa00ef562:'c.mv s1, a1',
 0xa00ef568:'c.addi4spn s0, sp, 0x20',0xa00ef56a:'c.addi s1, -1',
 0xa00ef56c:'c.mv a1, a2',0xa00ef56e:'c.mv a0, s1',0xa00ef570:'c.mv a2, a3',
 0xa00ef572:'sw a4, -0x14(s0)',0xa00ef57a:'lw a4, -0x14(s0)',
 0xa00ef586:'lw a6, 0(a0)',0xa00ef596:'c.mv a5, s1',
 0xa00ef5a8:'c.li a0, 2',0xa00ef5b2:'c.lw a0, 0(a0)',
 0xa00ef5b8:'c.lwsp ra, 0x1c(sp)',0xa00ef5ba:'c.lwsp s0, 0x18(sp)',
 0xa00ef5bc:'c.lwsp s1, 0x14(sp)',0xa00ef5be:'c.addi16sp sp, 0x20',
 0xa00ef5c0:'c.jr ra',0xa00ef5c2:'c.sw a0, 0(a4)',
 0xa00ef5c4:'c.li a0, 0',0xa00ef5c6:'c.j -0xe',
 0xa00ef632:'c.li a5, 2',0xa00ef634:'c.li a0, 0xb',
 0xa00ef63a:'c.addi sp, -0x10',0xa00ef63e:'c.mv s1, a1',
 0xa00ef644:'c.addi4spn s0, sp, 0x10',0xa00ef646:'c.addi s1, -1',
 0xa00ef648:'c.mv a1, a2',0xa00ef64a:'c.mv a2, a3',0xa00ef64c:'c.mv a0, s1',
 0xa00ef652:'c.mv a5, a0',0xa00ef654:'c.li a0, 0',
 0xa00ef65e:'lw a6, 0(a0)',0xa00ef66e:'c.mv a5, s1',
 0xa00ef680:'c.li a0, 2',0xa00ef68a:'c.lw a0, 0(a0)',
 0xa00ef690:'c.lwsp ra, 0xc(sp)',0xa00ef692:'c.lwsp s0, 8(sp)',
 0xa00ef694:'c.lwsp s1, 4(sp)',0xa00ef696:'c.addi sp, 0x10',
 0xa00ef698:'c.jr ra',0xa00ef69a:'c.jr ra',
}.items():inst(a,t)
for a,t in [(0xa00ef576,0xa003f6a2),(0xa00ef582,0xa00267c0),
            (0xa00ef5aa,0xa008b51a),(0xa00ef5ae,0xa00267c0),(0xa00ef5b4,0xa00ea524),
            (0xa00ef64e,0xa00281d8),(0xa00ef65a,0xa00267c0),
            (0xa00ef682,0xa008b51a),(0xa00ef686,0xa00267c0),(0xa00ef68c,0xa00ea524)]:jal(a,t)
for args in [(0xa00ef57e,5,10,0,0xa00ef5c2),(0xa00ef636,6,15,13,0xa00ef69a),
             (0xa00ef656,5,15,0,0xa00ef690)]:branch(*args)
for a,op,base,reg,off in [(0xa00ef572,0x23,8,14,-20),(0xa00ef57a,3,8,14,-20)]:
    w=int.from_bytes(raw(a,4),'little');im=((w>>25)<<5)|((w>>7)&31) if op==0x23 else w>>20
    rr=(w>>20)&31 if op==0x23 else (w>>7)&31
    assert (w&127,(w>>12)&7,(w>>15)&31,rr,sx(im,12))==(op,2,base,reg,off)
    checks.append(dict(address=hex(a),raw=raw(a,4).hex(),kind='independent-word-local-fields',offset=off))
h=int.from_bytes(raw(0xa00ef5c2,2),'little')
off=(((h>>10)&7)<<3)|(((h>>6)&1)<<2)|(((h>>5)&1)<<6)
assert (h&3,h>>13,((h>>7)&7)+8,((h>>2)&7)+8,off)==(0,6,14,10,0)
checks.append(dict(address='0xa00ef5c2',raw=raw(0xa00ef5c2,2).hex(),kind='independent-out-word-store',base='a4',source='a0'))

index_path=MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
idx=json.loads(index_path.read_text(encoding='utf8'))
meta=[]
for i,f in enumerate(idx['functions']):
    if f['address'] in ['0xa00ef55e','0xa00ef5c8','0xa003f6a2','0xa00281d8','0xa00ea524']:
        meta.append(dict(pointer='/functions/'+str(i),address=f['address'],extent=f['extent'],
                         direct_calls=f['direct_calls'],dossiers=f['dossiers'],historical_dossier=f['historical_dossier']))
assert not any(f['address']=='0xa00ef632' for f in idx['functions'])

contract=dict(claim='J08/8',task='A68',baseline='bd457a6',review_status='author-awaiting-independent-review',
 read=dict(entry='0xa00ef55e',source_ABI='(D,H,buffer,want_word,out_count_word_pointer)',
  explicit_lower_registers='a0=low32(H-1), a1=original buffer, a2=original want word; no buffer dereference in callback',
  lower='0xa003f6a2',nonnegative='signed32(a0)>=0 -> store32(original out_count,a0), callback returns0; a0=0 uses same arm',
  negative='no callback store to out_count on this arm; getter/read for log, getter/read again -> opaque0xa00ea524; return its a0'),
 seek=dict(entry='0xa00ef632',source_ABI='(D,H,position_word,origin_word)',
  gate='unsigned origin_word>2 returns numeric11 before frame/IO',
  explicit_lower_registers='a0=low32(H-1), a1=original position word, a2=original origin word; a3 remains original origin, not an independently constructed parameter',
  lower='0xa00281d8',nonnegative='signed32(lower a0)>=0 -> callback0; absolute resulting position is not returned',
  negative='two getter reads separated by log; second word -> opaque0xa00ea524; return map a0'),
 limits=['A64 slot and A66 encoded-H bodies pending A65/A67 at task start; this body decodes H independently',
 'No formal off_t/ssize_t definition inferred: callback moves one position/count word and tests a0 signed only; lower ABI may require further proof',
 'No underlying IO, mapper, logger, copy or getter body read; no IO execution',
 'Callback has no direct buffer/H allocation/free or global pointer retention; lower service retention and aliases remain unknown',
 'Error out-count claim is callback-local stores only, not absence of all alias/service side effects'])
(OUT/'contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(OUT/'evidence.json').write_text(json.dumps(dict(status='PASS-static-only',claim='J08/8',task='A68',
 checks=checks,contract=contract,original=dict(path=str(ROM),length=6769704,sha256_inherited=idx['rom_sha256'],
 mapping='VA-0x9ffff000',digest_recomputed=False),metadata=meta,
 boundary=dict(read='old indexed106B callback matches selected entry and normal returns',
 seek='0xa00ef632 not an old index entry; raw entry/stack/forward gate/returns observed through0xa00ef69a, adjacent write body excluded'),
 exploratory_windows=[['0xa00ef55e','0xa00ef59a'],['0xa00ef598','0xa00ef5c8'],
                      ['0xa00ef632','0xa00ef672'],['0xa00ef670','0xa00ef69c']],
 exploratory_requested_bytes=216,exploratory_unique_bytes=212,
 tools='Capstone5.0.7 RV32/RVC; independent JAL/B/S/I/C.SW fields; no new REA/provider run',
 limits=contract['limits']),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} sparse callback checks; no lower IO body')
