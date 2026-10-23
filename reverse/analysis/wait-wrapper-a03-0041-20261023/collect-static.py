"""A03 bounded static ROM windows; never executes target instructions."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
HERE=Path(__file__).resolve().parent
ROM=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE=0x9ffff000
raw=ROM.read_bytes()
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
def window(lo,hi):
    start=lo; out=[]
    while lo<hi:
        b=raw[lo-BASE:lo-BASE+4]
        i=next(md.disasm(b,lo,1),None)
        size=i.size if i else (4 if b[0]&3==3 else 2)
        out.append(dict(pc=hex(lo),bytes=b[:size].hex(),asm=i.mnemonic+' '+i.op_str if i else 'unknown; no semantics assigned'))
        lo+=size
    assert lo==hi
    return dict(start=hex(start),end_exclusive=hex(hi),instructions=out)
windows=[window(0xa00b8bfc,0xa00b8cc0),window(0xa0126946,0xa0126cea)]
out=dict(task='A03',method='bounded original ROM byte decode; inventory selects caller; no ROM-wide scan, no target execution',windows=windows)
(HERE/'instruction-evidence.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
for w in windows:
    print(w['start'])
    for i in w['instructions']: print(i['pc'],i['bytes'],i['asm'])

# Only local checks: the selected caller and the wrapper, never a full-ROM search.
prior=json.loads((HERE.parent/'buzzer-stop-review-a02-0041-20261023'/'verification.json').read_text())
old=next(w for w in prior['parameter_windows'] if w['start']=='0xa00b8bfc')
assert windows[0]['instructions'][:len(old['instructions'])]==old['instructions']
def jal_target(pc):
    w=int.from_bytes(raw[pc-BASE:pc-BASE+4],'little')
    assert w&0xfff==0xef
    imm=((w>>21&1023)<<1)|((w>>20&1)<<11)|((w>>12&255)<<12)|((w>>31)<<20)
    imm=(imm^(1<<20))-(1<<20)
    return (pc+imm)&0xffffffff
expected={0xa01269f6:0xa00b8bfc,0xa00b8c36:0xa0028b0a,0xa00b8c52:0xa002696a,0xa00b8ca8:0xa0028bfc,0xa00b8cb6:0xa00267c0}
assert all(jal_target(pc)==dest for pc,dest in expected.items())
strings=[]
for a in (0xa025668c,0xa0561b6c,0xa0617798):
    b=raw[a-BASE:a-BASE+128].split(b'\0')[0]
    strings.append(dict(address=hex(a),bytes=b.hex(),text=b.decode('ascii')))
out['checks']=dict(prior_A02_prefix_equal=True,independent_jal_targets={hex(k):hex(v) for k,v in expected.items()},unknown_vendor_words=[i for w in windows for i in w['instructions'] if i['asm'].startswith('unknown')])
out['strings']=strings
out['limits']=['Only two selected inventory body windows decoded; not a full RPC recovery or caller search.', 'Input pointer and member non-nullness is not established by the caller window.', 'Vendor word at a00b8c78 is retained without semantics, preventing exact timeout arithmetic reconstruction.', 'No pointer identity with buzzer exited_sem is established.']
(HERE/'instruction-evidence.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print(json.dumps(out['checks']))
