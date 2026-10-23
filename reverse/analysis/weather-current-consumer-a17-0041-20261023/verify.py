"""Bounded static extraction/encoding checks. Never executes target code."""
import json
from pathlib import Path
import capstone

OUT = Path(__file__).resolve().parent
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
MODEL = SOURCE / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
image = ROM.read_bytes()
def raw(a, n=4): return image[a-0xa0000000+0x1000:a-0xa0000000+0x1000+n]
def word(a, n=4): return int.from_bytes(raw(a,n),'little')
def sx(v,n): return v-(1<<n) if v & (1<<(n-1)) else v
checks=[]
def check(a, kind, actual, expected):
    assert actual == expected, (hex(a),kind,actual,expected)
    checks.append(dict(address=hex(a),kind=kind,raw=raw(a,2 if word(a,2)&3!=3 else 4).hex(),value=actual))
def cmem(a,e):
    w=word(a,2); off=((w>>5)&1)*64+((w>>10)&7)*8+((w>>6)&1)*4
    check(a,'C-memory [quadrant,funct3,reg,base,offset]',[w&3,w>>13,8+((w>>2)&7),8+((w>>7)&7),off],e)
for a,e in [(0xa00ab6e6,[0,2,10,9,24]),(0xa00ab6ee,[0,2,10,9,28]),
            (0xa008ce62,[0,2,12,10,64]),(0xa008ce68,[0,2,13,10,72]),
            (0xa008ce72,[0,2,14,10,68]),(0xa008ce80,[0,6,14,10,64])]: cmem(a,e)
w=word(0xa00ab6cc)
check(0xa00ab6cc,'LH [opcode,funct3,rd,rs1,imm]',[w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12)],[3,1,18,10,12])
for a,rd,r1,r2 in [(0xa008ce6a,14,11,13),(0xa008ce74,11,14,13)]:
    w=word(a)
    check(a,'SLT [opcode,funct3,funct7,rd,rs1,rs2]',[w&127,(w>>12)&7,w>>25,(w>>7)&31,(w>>15)&31,(w>>20)&31],[51,2,0,rd,r1,r2])
lines=MODEL.read_text().splitlines()
start=next(i for i,l in enumerate(lines) if l.startswith(':th.mvnez '))
end=next(i for i in range(start+1,len(lines)) if lines[i]=='}')
excerpt='\n'.join(lines[start:end+1])
assert 'op2531=33' in excerpt and 'if (rs2 == 0) goto <done>;' in excerpt and 'rd = rs1;' in excerpt
vendor={0xa008ce6e:'th.mvnez a3,a1,a4',0xa008ce78:'th.mvnez a4,a3,a1'}
for a,rd,r1,r2 in [(0xa008ce6e,13,11,14),(0xa008ce78,14,13,11)]:
    w=word(a)
    check(a,'th.mvnez [opcode,funct3,funct7,rd,rs1,rs2]',[w&127,(w>>12)&7,w>>25,(w>>7)&31,(w>>15)&31,(w>>20)&31],[11,1,33,rd,r1,r2])
for a,r1,r2,target in [(0xa008ce64,12,11,0xa008ce86),(0xa008ce7c,12,14,0xa008ce86)]:
    w=word(a); imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    check(a,'BEQ [opcode,funct3,rs1,rs2,target]',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,hex(a+sx(imm,13))],[99,0,r1,r2,hex(target)])
for a,target in [(0xa00ab6ea,0xa008ce16),(0xa008ce82,0xa008ccd2),(0xa008ce50,0xa008b51a),(0xa008ce5e,0xa0019672)]:
    w=word(a); imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    check(a,'JAL [opcode,rd,target]',[w&127,(w>>7)&31,hex(a+sx(imm,21))],[111,1,hex(target)])
for a,h in [(0xa00ab6e8,'ca85'),(0xa008ce8e,'8280')]: check(a,'fixed ABI encoding',raw(a,2).hex(),h)
w=word(0xa008ce20,2); imm=((w>>12)&1)*256+((w>>10)&3)*8+((w>>5)&3)*64+((w>>3)&3)*2+((w>>2)&1)*32
check(0xa008ce20,'C.BNEZ [quadrant,funct3,rs1,target]',[w&3,w>>13,8+((w>>7)&7),hex(0xa008ce20+sx(imm,9))],[1,7,10,'0xa008ce62'])
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[]
for lo,hi in [(0xa008ce16,0xa008ce90),(0xa00ab6cc,0xa00ab6d0),(0xa00ab6e6,0xa00ab6f0)]:
    rows=[]; a=lo
    while a<hi:
        n=2 if word(a,2)&3!=3 else 4; b=raw(a,n); ins=list(md.disasm(b,a))
        if a in vendor:
            assert not ins
            text=vendor[a]; decoder='raw fields + retained model'
        else:
            assert len(ins)==1 and ins[0].size==n, hex(a)
            text=ins[0].mnemonic+' '+ins[0].op_str; decoder='capstone'
        rows.append(dict(address=hex(a),file_offset=a-0xa0000000+0x1000,bytes=b.hex(),instruction=text,decoder=decoder)); a+=n
    assert a==hi
    windows.append(dict(start=hex(lo),end_exclusive=hex(hi),bytes=hi-lo,rows=rows))
strings=[]
for a,expected in [(0xa0263324,'/home/jiangmingmin/ap01/AP01_BL618/apps/graphics/lvgl/lvgl/src/widgets/arc/lv_arc.c'),(0xa0263884,'lv_arc_set_value'),(0xa0263318,'obj != NULL')]:
    o=a-0xa0000000+0x1000; s=image[o:image.index(b'\0',o)].decode()
    assert s==expected
    strings.append(dict(address=hex(a),file_offset=o,text=s))
evidence=dict(static_only=True,rom=str(ROM),mapping='file_offset = VA - 0xa0000000 + 0x1000',windows=windows,encoding_checks=checks,strings=strings,vendor_model=dict(path=str(MODEL),start_line=start+1,end_line=end+1,text=excerpt),limitations=['No new hash, firmware execution, emulation, input replay, device or service access.','a008ccd2 remains an opaque update call boundary; no dependency body recovered.'])
(OUT/'instruction-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
summary=dict(result='passed',windows=len(windows),bytes=sum(w['bytes'] for w in windows),instructions=sum(len(w['rows']) for w in windows),raw_encoding_checks=len(checks),vendor_words=len(vendor),strings=len(strings),unknown_words=0,scope='setter body and two callback slices only')
(OUT/'review-index.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
