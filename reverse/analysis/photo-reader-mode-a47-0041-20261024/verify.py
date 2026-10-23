"""A47 bounded offline ROM checks, no target execution."""
from pathlib import Path
import json
import sys

OUT = Path(__file__).resolve().parent
TREE = OUT.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
sys.dont_write_bytecode = True
sys.path.insert(0, str(TREE/'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr

windows = [(0xa00ed876, 0xa00ed884), (0xa0107da2, 0xa0107dd4),
           (0xa019d6ec, 0xa019d708),
           (0xa019d798, 0xa019d7c6), (0xa019d80e, 0xa019d82e),
           (0xa019d864, 0xa019d86e), (0xa01b2e44, 0xa01b2e84)]
rows = [r for a,z in windows for r in rr.rows(a,z)]
D = {int(r['pc'],16): r for r in rows}
expected = {
 0xa00ed876:'c.li a5, 1', 0xa00ed87c:'c.mv a0, s3',
 0xa0107da2:'c.mv s1, a0', 0xa0107db2:'c.li a5, 1',
 0xa0107db4:'c.mv a1, s1', 0xa0107db6:'addi a0, s0, -0x674',
 0xa0107dba:'sw zero, -0x660(s0)', 0xa0107dbe:'sw zero, -0x668(s0)',
 0xa0107dc2:'sb a5, -0x664(s0)', 0xa0107dca:'c.bnez a0, 0x1c',
 0xa0107dcc:'addi a0, s0, -0x674',
 0xa019d6ec:'lbu a2, 0(a1)', 0xa019d6f0:'c.mv s2, a0',
 0xa019d6f2:'c.mv a5, a1', 0xa019d6f4:'c.beqz a2, 0x14',
 0xa019d6f6:'lbu a3, 1(a1)', 0xa019d6fa:'addi a4, zero, 0x3a',
 0xa019d6fe:'c.addi a1, 2', 0xa019d704:'addi a1, a5, 1',
 0xa019d798:'sw s1, 4(s2)', 0xa019d79c:'c.lw a3, 4(s1)',
 0xa019d7bc:'sw a0, 8(s2)', 0xa019d80e:'c.lw a4, 0xc(s1)',
 0xa019d810:'c.li a2, 2', 0xa019d812:'c.mv a0, s1',
 0xa019d818:'c.jalr a4', 0xa019d828:'sw a0, 0(s2)',
 0xa019d864:'c.lw a4, 8(s1)', 0xa019d86a:'c.lw a4, 0xc(s1)',
 0xa01b2e44:'c.mv s1, a0', 0xa01b2e46:'c.lw a0, 4(a0)',
 0xa01b2e4a:'c.lw a5, 0x10(a0)', 0xa01b2e4e:'c.lw a1, 0(s1)',
 0xa01b2e50:'c.jalr a5', 0xa01b2e52:'c.lw a5, 4(s1)',
 0xa01b2e54:'c.lw a4, 4(a5)', 0xa01b2e58:'c.lw a5, 8(s1)',
 0xa01b2e5c:'c.li a3, -1', 0xa01b2e62:'c.lw a0, 0xc(a5)',
 0xa01b2e6e:'c.lw a0, 8(s1)', 0xa01b2e78:'sw zero, 0(s1)',
 0xa01b2e7c:'sw zero, 4(s1)', 0xa01b2e80:'sw zero, 8(s1)',
}
checks = []
for pc,asm in expected.items():
 assert D[pc]['asm'] == asm, (hex(pc),D[pc])
 checks.append({'pc':hex(pc),'asm':asm})

def word(pc): return int.from_bytes(rr.rom[pc-rr.BASE:pc-rr.BASE+4], 'little')
def sx(v,b): return v-(1<<b) if v&(1<<(b-1)) else v
for pc,target in [(0xa00ed87e,0xa0107d8e),(0xa0107dae,0xa0024906),
                  (0xa0107dc6,0xa019d6a4),(0xa0107dd0,0xa010a65a)]:
 w=word(pc)
 imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 assert (w&127,(w>>7)&31)==(0x6f,1) and pc+sx(imm,21)==target
 checks.append({'pc':hex(pc),'direct_call':hex(target)})
for pc in [0xa01b2e66,0xa01b2e70]:
 w,v=word(pc),word(pc+4)
 assert w&127==0x17 and v&127==0x67
 assert (pc+sx(w&0xfffff000,32)+sx(v>>20,12))&0xffffffff==0xa008ab8a
 checks.append({'pc':hex(pc),'direct_call':'0xa008ab8a'})
for pc,target in [(0xa01b2e48,0xa01b2e84),(0xa01b2e4c,0xa01b2e84),
                  (0xa01b2e56,0xa01b2e78),(0xa01b2e5a,0xa01b2e78),
                  (0xa01b2e64,0xa01b2e6e)]:
 w=word(pc)&65535
 imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
 assert w&3==1 and w>>13==6 and pc+sx(imm,9)==target
 checks.append({'pc':hex(pc),'zero_branch':hex(target)})
w=word(0xa01b2e5e)
imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31)==(99,0,14,13)
assert 0xa01b2e5e+sx(imm,13)==0xa01b2e6e
checks.append({'pc':'0xa01b2e5e','semantics':'D+4 == 0xffffffff skips buffer free, retains cache-struct free'})
w=word(0xa0107dc2)
assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31)==(35,0,8,15)
assert sx(((w>>25)<<5)|((w>>7)&31),12)==-0x664
checks.append({'pc':'0xa0107dc2','semantics':'one-byte W+0x10=1, W=s0-0x674'})
reuse=[]
for p in sorted((MAIN/'reverse/rehost').glob('*.json')):
 t=p.read_text(encoding='utf8', errors='replace').lower()
 hits=[s for s in ['a0107d8e','a019d6a4','a01b2e3a'] if s in t]
 if hits: reuse.append({'file':p.name,'terms':hits})
strings={hex(a):rr.rom[a-rr.BASE:a-rr.BASE+120].split(b'\0')[0].decode('ascii')
         for a in [0xa063137c,0xa02631a8]}
assert strings['0xa063137c']=='lv_fs_open' and strings['0xa02631a8'].endswith('/lv_fs.c')
result=dict(status='PASS',baseline='e2991b9',static_only=True,checks=checks,rows=rows,
            source_strings=strings,reuse_search=dict(boundary='main reverse/rehost/*.json address text, including photo/late round3/complete',hits=reuse),
            limitations=['No concrete driver callback target or actual photo mode1 observation',
                         'Ordinary driver open path only; no filesystem implementation or all failure arms',
                         'Whole-ROM listing provides extent/call inventory, not historical recovered body'])
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),windows=len(windows))))
