"""Read-only ROM instruction verification; never executes firmware or a model."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
data = ROM.read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []
def raw(pc,n): return data[pc-BASE:pc-BASE+n]
def sx(v,n): return v-(1<<n) if v & (1<<(n-1)) else v
def check(label,got,want):
    assert got == want, (label,got,want)
    checks.append(dict(label=label,actual=got,expected=want))
def word(pc): return int.from_bytes(raw(pc,4),'little')
def itype(pc,op,rd,f3,rs,imm):
    w=word(pc)
    check(hex(pc)+' I fields',[w&127,w>>7&31,w>>12&7,w>>15&31,sx(w>>20,12)],[op,rd,f3,rs,imm])
def cmv(pc,rd,rs):
    w=int.from_bytes(raw(pc,2),'little')
    check(hex(pc)+' C.MV',[w&3,w>>12,w>>7&31,w>>2&31],[2,8,rd,rs])

vendor={0xa0089304:(16,15,14),0xa0089314:(15,14,13),0xa0089322:(13,14,17),0xa0089330:(14,11,12)}
model_path=SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model_path.read_text().splitlines()
start=next(i for i,s in enumerate(lines) if s.startswith(':th.mvnez '))
end=next(i for i in range(start+1,len(lines)) if lines[i]=='}')
model='\n'.join(lines[start:end+1])
check('existing vendor semantics',model,':th.mvnez rd,rs1,rs2 is op0006=0xb & op1214=1 & op2531=33 & rd & rs1 & rs2\n{\n  if (rs2 == 0) goto <done>;\n  rd = rs1;\n<done>\n}')
windows=[]; targets=[]
for a,e in [(0xa00ddab4,0xa00ddbf6),(0xa00892ac,0xa00892d0),(0xa00892f4,0xa008934a),(0xa00ddc70,0xa00ddc7e),(0xa00ddd82,0xa00ddd90)]:
    rows=[]; pc=a
    while pc<e:
        w=word(pc); n=4 if w&3==3 else 2; bs=raw(pc,n)
        if pc in vendor:
            rd,r1,r2=vendor[pc]
            check(hex(pc)+' vendor fields',[w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31,w>>25],[11,rd,1,r1,r2,33])
            asm=f'th.mvnez x{rd},x{r1},x{r2}'
        else:
            ins=list(md.disasm(bs,pc)); assert len(ins)==1 and ins[0].size==n,hex(pc)
            asm=ins[0].mnemonic+' '+ins[0].op_str
        row=dict(pc=hex(pc),raw=bs.hex(),assembly=asm)
        target=None
        if n==4 and w&127==111:
            imm=((w>>31&1)<<20)|((w>>21&1023)<<1)|((w>>20&1)<<11)|((w>>12&255)<<12)
            target=pc+sx(imm,21); row['rd']=w>>7&31
        elif n==4 and w&127==99:
            imm=((w>>31&1)<<12)|((w>>25&63)<<5)|((w>>8&15)<<1)|((w>>7&1)<<11)
            target=pc+sx(imm,13); row['branch_fields']=[w>>12&7,w>>15&31,w>>20&31]
        elif n==2 and w&3==1 and (w&65535)>>13 in [6,7]:
            h=w&65535; imm=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
            target=pc+sx(imm,9); row['branch_fields']=[h>>13,8+(h>>7&7)]
        elif n==2 and w&3==1 and (w&65535)>>13==5:
            h=w&65535; imm=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
            target=pc+sx(imm,12)
        if target is not None:
            row['target']=hex(target); targets.append(dict(pc=hex(pc),target=hex(target)))
        rows.append(row); pc+=n
    check(hex(a)+' continuous end',pc,e)
    windows.append(dict(start=hex(a),end_exclusive=hex(e),file_offset=a-BASE,instructions=rows))

# Critical ABI, local bases and signed comparisons checked by fields/bytes.
for pc,rd,rs in [(0xa00ddac6,18,11),(0xa00ddac8,9,10),(0xa00ddace,19,10),(0xa00ddad4,20,10),(0xa00ddb06,11,18),(0xa00ddb08,10,18),(0xa00ddb0e,19,10),(0xa00ddb78,11,18),(0xa00ddb7a,10,18),(0xa00ddbe8,10,19),(0xa00ddc74,10,9)]: cmv(pc,rd,rs)
for args in [(0xa00ddae8,19,11,0,9,20),(0xa00ddaec,19,10,0,8,-64),(0xa00ddaf4,3,12,2,8,-68),(0xa00ddaf8,19,10,0,8,-64),(0xa00ddb02,19,12,0,8,-64),(0xa00ddb34,19,11,0,9,20),(0xa00ddb3a,19,10,0,8,-48),(0xa00ddb58,19,10,0,8,-48),(0xa00ddb6a,19,11,0,8,-48),(0xa00ddb74,19,12,0,8,-48),(0xa00ddbf0,3,21,2,21,0x2d0),(0xa00ddc70,19,11,0,8,-80),(0xa0089340,19,10,4,15,1)]:itype(*args)
for pc,rd,r1,r2 in [(0xa0089300,14,16,15),(0xa0089310,13,15,14),(0xa008931e,17,14,13),(0xa008932c,12,11,14),(0xa008933c,15,14,15)]:
    w=word(pc);check(hex(pc)+' signed SLT',[w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31,w>>25],[51,rd,2,r1,r2,0])
expected={0xa00ddada:0xa00ddb84,0xa00ddb10:0xa00ddbda,0xa00ddb1a:0xa00ddb26,0xa00ddb28:0xa00ddbdc,0xa00ddb32:0xa00ddbda,0xa00ddb4c:0xa00ddb60,0xa00ddb66:0xa00ddb74,0xa00ddb80:0xa00ddb26,0xa00ddb82:0xa00ddbda,0xa00ddb86:0xa00ddbf0,0xa00ddb92:0xa00ddbf0,0xa00ddbb8:0xa00ddade,0xa00ddbc2:0xa00ddade,0xa00ddbcc:0xa00ddade,0xa00ddbd6:0xa00ddade,0xa00ddbf4:0xa00ddbb8,0xa0089338:0xa0089344,0xa00ddc7a:0xa00ddd82,0xa00ddc76:0xa00ddab4}
found={int(r['pc'],16):int(r['target'],16) for r in targets}
for pc,t in expected.items():check(hex(pc)+' control target',found[pc],t)
check('initial frame',raw(0xa00ddab4,2).hex(),'5d71')
check('parent word',raw(0xa00ddb26,2).hex(),'c440')
check('failure and return',raw(0xa00ddbda,22).hex(),'8149b640264496440649625ad25a4e85f25961618280')
check('caller unchanged a0 epilogue',raw(0xa00ddd82,14).hex(),'f6406644d6444649b64925618280')
inventory=json.loads((TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
selected=[]
def visit(x):
    if isinstance(x,dict):
        if x.get('address') in ['0xa00ddab4','0xa00892ac','0xa00892f4'] and 'extent' in x:selected.append(x)
        else:
            for v in x.values():visit(v)
    elif isinstance(x,list):
        for v in x:visit(v)
visit(inventory)
check('inventory three cores',len(selected),3)
for record in selected:
    a=int(record['address'],16); win=next(w for w in windows if int(w['start'],16)==a)
    check(hex(a)+' inventory extent',record['extent']['body']['ranges'],[dict(start=hex(a),end=hex(int(win['end_exclusive'],16)-1))])
    calls=sorted(set(r['target'] for r in win['instructions'] if r.get('rd')==1))
    check(hex(a)+' all direct calls',calls,record['direct_calls']['callees'])
strings=[]
for pc in [0xa025e3d8,0xa056a2ac,0xa0569e28]:
    off=pc-BASE; strings.append(dict(address=hex(pc),text=data[off:data.index(0,off)].decode()))
out=dict(rom=str(ROM),mapping='file_offset = address - 0x9ffff000',windows=windows,direct_targets=targets,checks=checks,inventory=selected,strings=strings,vendor_model=dict(path=str(model_path),start_line=start+1,end_line=end+1,text=model))
(HERE/'instruction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(result='passed',windows=len(windows),bytes=sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),instructions=sum(len(w['instructions']) for w in windows),checks=len(checks),direct_targets=len(targets),vendor_words=len(vendor))))
