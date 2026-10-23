"""C17 static byte/bitfield checks. Reads ROM; never executes target code."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
data = ROM.read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []
def raw(pc, n): return data[pc-BASE:pc-BASE+n]
def sx(v, n): return v-(1 << n) if v & (1 << (n-1)) else v
def check(pc, label, got, want):
    assert got == want, (hex(pc), label, got, want)
    checks.append(dict(pc=hex(pc), label=label, decoded=got, expected=want))
def word(pc): return int.from_bytes(raw(pc,4),'little')
def half(pc): return int.from_bytes(raw(pc,2),'little')
def itype(pc, op, rd, f3, rs, imm):
    w=word(pc)
    check(pc,'I fields',[w&127,w>>7&31,w>>12&7,w>>15&31,sx(w>>20,12)],[op,rd,f3,rs,imm])
def cmv(pc, rd, rs):
    h=half(pc); check(pc,'C.MV',[h&3,h>>12,h>>7&31,h>>2&31],[2,8,rd,rs])
def cli(pc, rd, imm):
    h=half(pc); check(pc,'C.LI',[h&3,h>>13,h>>7&31,sx(((h>>12&1)<<5)|(h>>2&31),6)],[1,2,rd,imm])
def rtype(pc, rd, f3, rs1, rs2, f7):
    w=word(pc); check(pc,'R fields',[w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31,w>>25],[51,rd,f3,rs1,rs2,f7])

ranges=[(0xa00ddbf6,0xa00ddc7e),(0xa00ddd82,0xa00ddd90),(0xa0081804,0xa008184e),(0xa00d7446,0xa00d749e)]
windows=[]
for start,end in ranges:
    ins=list(md.disasm(raw(start,end-start),start))
    assert sum(i.size for i in ins)==end-start
    windows.append(dict(start=hex(start),end_exclusive=hex(end),instructions=[dict(pc=hex(i.address),raw=i.bytes.hex(),assembly=i.mnemonic+' '+i.op_str) for i in ins]))

# Machine arguments and saved input; independent fields, not assembly text.
check(0xa00ddbf6,'frame setup bytes',raw(0xa00ddbf6,14).hex(),'1d71a2cc86cea6cacac8cec68010')
w=word(0xa00ddc46)
check(0xa00ddc46,'S word area pointer spill',[w&127,w>>12&7,w>>15&31,w>>20&31,sx((w>>25<<5)|(w>>7&31),12)],[35,2,8,11,-84])
cmv(0xa00ddc4a,9,10)
itype(0xa00ddc58,3,11,2,8,-84)
itype(0xa00ddc5c,19,10,0,8,-80)
cli(0xa00ddc64,11,1)
cmv(0xa00ddc66,10,9)
itype(0xa00ddc70,19,11,0,8,-80)
cmv(0xa00ddc74,10,9)
# Getter fallback, full signed word, and SLT zero < value.
check(0xa0081806,'LUI fallback base',[word(0xa0081806)&127,word(0xa0081806)>>7&31,word(0xa0081806)&0xfffff000],[55,15,0x62fc9000])
itype(0xa008180a,3,10,2,15,0x590)
itype(0xa0081844,3,10,2,10,0x268)
rtype(0xa0081848,10,2,0,10,0)
cli(0xa008183e,10,0)
# Flag word, AND, SUB, SLTIU x,1 (SEQZ).
h=half(0xa00d7492)
check(0xa00d7492,'C.LW flags',[h&3,h>>13,8+(h>>7&7),8+(h>>2&7),(h>>10&7)*8+(h>>6&1)*4+(h>>5&1)*64],[0,2,10,10,36])
for pc,selector in [(0xa00d7494,3),(0xa00d7496,0)]:
    h=half(pc); check(pc,'C.AND/SUB',[h&3,h>>10&7,h>>12&1,h>>5&3,8+(h>>7&7),8+(h>>2&7)],[1,3,0,selector,10,11])
itype(0xa00d7498,19,10,3,10,1)
# Exact epilogue proves no independent status construction after either gate.
check(0xa00ddd82,'shared epilogue bytes',raw(0xa00ddd82,14).hex(),'f6406644d6444649b64925618280')
for pc in [0xa0081842,0xa008184c,0xa00d749c]:
    check(pc,'return JR ra',half(pc),0x8082)

expected={0xa00ddc04:(0xa00ddc46,10,7),0xa00ddc34:(0xa008b51a,1,None),0xa00ddc42:(0xa0019672,1,None),0xa00ddc4c:(0xa00dce2e,1,None),0xa00ddc50:(0xa0081804,1,None),0xa00ddc54:(0xa00ddd82,10,0),0xa00ddc60:(0xa008b43a,1,None),0xa00ddc68:(0xa00d7446,1,None),0xa00ddc6c:(0xa00ddd82,10,1),0xa00ddc76:(0xa00ddab4,1,None),0xa00ddc7a:(0xa00ddd82,10,0),0xa0081804:(0xa0081844,10,7),0xa008180e:(0xa0081844,10,7),0xa0081836:(0xa008b51a,1,None),0xa00d7446:(0xa00d7492,10,7),0xa00d7480:(0xa008b51a,1,None),0xa00d748e:(0xa0019672,1,None)}
targets=[]
for win in windows:
    for row in win['instructions']:
        pc=int(row['pc'],16); b=bytes.fromhex(row['raw']); w=int.from_bytes(b,'little'); got=None
        if len(b)==4 and w&127==111:
            imm=((w>>31&1)<<20)|((w>>21&1023)<<1)|((w>>20&1)<<11)|((w>>12&255)<<12)
            got=(pc+sx(imm,21),w>>7&31,None)
        elif len(b)==4 and w&127==99:
            imm=((w>>31&1)<<12)|((w>>25&63)<<5)|((w>>8&15)<<1)|((w>>7&1)<<11)
            check(pc,'branch rs2',w>>20&31,0)
            got=(pc+sx(imm,13),w>>15&31,w>>12&7)
        elif len(b)==2 and w&3==1 and w>>13 in [6,7]:
            imm=((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
            got=(pc+sx(imm,9),8+(w>>7&7),w>>13)
        if got is not None:
            check(pc,'direct target/register/condition',list(got),list(expected[pc]))
            targets.append(dict(pc=hex(pc),target=hex(got[0])))
assert len(targets)==len(expected)

inventory=json.loads((TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
selected=[]
def visit(x):
    if isinstance(x,dict):
        if x.get('address') in ['0xa00ddbf6','0xa0081804','0xa00d7446','0xa00dce2e'] and 'extent' in x: selected.append(x)
        else:
            for v in x.values(): visit(v)
    elif isinstance(x,list):
        for v in x: visit(v)
visit(inventory)
assert len(selected)==4
for a,end in [('0xa0081804','0xa008184d'),('0xa00d7446','0xa00d749d'),('0xa00ddbf6','0xa00dddf3')]:
    record=next(r for r in selected if r['address']==a)
    assert record['extent']['body']['ranges']==[dict(start=a,end=end)]
    assert not record['dossiers'] and not record['historical_contracts']
strings=[]
for a in [0xa025e3d8,0xa0569130,0xa056a378,0xa025e86c,0xa025f608,0xa05699b4,0xa02645f0]:
    off=a-BASE; strings.append(dict(address=hex(a),text=data[off:data.index(0,off)].decode()))
assert strings[2]['text']=='lv_obj_invalidate_area'
assert strings[4]['text']=='lv_display_is_invalidation_enabled'
assert strings[5]['text']=='lv_obj_has_flag'
result=dict(task='C17',baseline='f482b78',rom=str(ROM),mapping_base=hex(BASE),checks=dict(result='passed',windows=len(windows),bytes=sum(e-s for s,e in ranges),instructions=sum(len(w['instructions']) for w in windows),raw_checks=len(checks),all_direct_targets=len(targets)),windows=windows,raw_checks=checks,targets=targets,strings=strings,inherited_inventory=selected)
(HERE/'instruction-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['checks']))
