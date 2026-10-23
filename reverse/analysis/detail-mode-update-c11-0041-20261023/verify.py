"""C11: decode ROM data only; no target or business-model execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
rom = ROM.read_bytes()
BASE = 0x9ffff000
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
specs = [('mode_update',0xa00f388c,0xa00f3952),
         ('add_flag',0xa00d8f7c,0xa00d9044),
         ('remove_flag',0xa00d9044,0xa00d9110),
         ('callback_gate_lookup',0xa00f3a5c,0xa00f3a8a),
         ('callback_mode_call',0xa00f3b12,0xa00f3b1e)]
windows, decoded, vendors = [], {}, []
for name,start,end in specs:
    pc, insns = start, []
    while pc < end:
        raw = rom[pc-BASE:pc-BASE+(4 if rom[pc-BASE]&3 == 3 else 2)]
        ins = next(md.disasm(raw,pc),None)
        if ins:
            assert ins.size == len(raw)
            decoded[pc] = ins
            asm = ins.mnemonic + ' ' + ins.op_str
        else:
            assert pc == 0xa00f389e and raw.hex() == '8b34063c'
            w = int.from_bytes(raw,'little')
            fields = dict(op=w&127,rd=(w>>7)&31,funct3=(w>>12)&7,
                          rs1=(w>>15)&31,lsb=(w>>20)&63,msb=w>>26)
            assert fields == dict(op=11,rd=9,funct3=3,rs1=12,lsb=0,msb=15)
            asm = 'th.extu s1,a2,15,0 (existing local model)'
            vendors.append(dict(address=hex(pc),hex=raw.hex(),fields=fields))
        insns.append(dict(address=hex(pc),hex=raw.hex(),assembly=asm))
        pc += len(raw)
    assert pc == end
    windows.append(dict(name=name,start=hex(start),end_exclusive=hex(end),instructions=insns))

targets = {0xa00f38a2:0xa00f38aa,0xa00f38a4:0xa00a5c50,
           **{a:0xa00dcee4 for a in [0xa00f38b2,0xa00f38bc,0xa00f38c6,0xa00f38d0,0xa00f38da,0xa00f38e4]},
           0xa00f38ea:0xa00f38fe,0xa00f38f0:0xa00d9044,0xa00f38f8:0xa00d8f7c,
           0xa00f38fc:0xa00f3914,0xa00f3900:0xa00f391e,0xa00f3908:0xa00d8f7c,
           0xa00f3910:0xa00d9044,0xa00f3918:0xa00d8f7c,0xa00f391c:0xa00f393c,
           0xa00f3924:0xa00f394c,0xa00f3928:0xa00d8f7c,0xa00f3930:0xa00d8f7c,
           0xa00f3938:0xa00d9044,0xa00f394c:0xa00d8f7c,0xa00f3950:0xa00f38f4,
           0xa00d8f8c:0xa00d8fce,0xa00d8fd2:0xa00d7446,0xa00d8fd6:0xa00d9034,
           0xa00d9052:0xa00d9094,0xa00d9098:0xa00d749e,0xa00d909c:0xa00d9102,
           0xa00f3a78:0xa00a72ae,0xa00f3a88:0xa00f3b12,0xa00f3b18:0xa00f388c}
for pc,dest in targets.items():
    assert pc+int(decoded[pc].op_str.split(',')[-1],0) == dest, hex(pc)
critical = {0xa00f389c:'s2, a0',0xa00f38a8:'s1, a0',0xa00f38aa:'s2, 4(s2)',
            0xa00f38ae:'a1, 0',0xa00f38b8:'a1, 1',0xa00f38c2:'a1, 2',
            **{a:'a1, 1' for a in [0xa00f38cc,0xa00f38d4,0xa00f38e0,0xa00f38ec,0xa00f38f4,0xa00f3904,0xa00f390c,0xa00f3914,0xa00f3920,0xa00f392c,0xa00f3934]},
            0xa00d8fce:'s1, a0',0xa00d8fd0:'s3, a1',0xa00d8fee:'a1, 0x24(s1)',
            0xa00d8ff0:'a1, a1, s3',0xa00d8ff4:'a1, 0x24(s1)',
            0xa00d9094:'s1, a0',0xa00d9096:'s2, a1',0xa00d90ce:'a5, 0x24(s1)',
            0xa00d90d0:'a4, s2',0xa00d90d8:'a5, a4',0xa00d90da:'a5, 0x24(s1)',
            0xa00f3a5c:'a5, 0xc(s1)',0xa00f3a60:'a5, 4',0xa00f3a6c:'a1, 0xf',
            0xa00f3b12:'a2, 8(s1)',0xa00f3b16:'a1, 0'}
for pc,ops in critical.items():
    assert decoded[pc].op_str == ops,(hex(pc),decoded[pc].op_str)
inventory=json.loads((TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
entries=[f for f in inventory['functions'] if f['address'] in ['0xa00f388c','0xa00d8f7c','0xa00d9044']]
for f in entries:
    start,end=next((a,b) for _,a,b in specs if a==int(f['address'],16))
    assert f['extent']['body']['ranges']==[dict(start=hex(start),end=hex(end-1))]
for a in [0xa00f394a,0xa00d9042,0xa00d910e]:
    assert decoded[a].mnemonic=='c.jr' and decoded[a].op_str=='ra'
model=SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages'
lines=(model/'ap01thead2.sinc').read_text().splitlines()
i=next(i for i,s in enumerate(lines) if s.startswith(':th.extu rd,rs1,15,0'))
reglines=(model/'ap01thead2.reg.sinc').read_text().splitlines()
strings=[]
for a in [0xa0569130,0xa0569848,0xa0569ac8]:
    off=a-BASE;raw=rom[off:rom.index(b'\0',off)+1]
    strings.append(dict(address=hex(a),hex=raw.hex(),text=raw[:-1].decode()))
prior=json.loads((TREE/'reverse/analysis/ui-total-consumers-0041-20261023/instruction-windows.json').read_text())
pw=next(w for w in prior['windows'] if w['name']=='power_detail_total_cb')
assert bytes.fromhex(pw['hex'])==rom[int(pw['start'],16)-BASE:int(pw['end_exclusive'],16)-BASE]
checks=dict(result='passed',windows=len(windows),bytes=sum(b-a for _,a,b in specs),ordinary_instructions=len(decoded),vendor_words=len(vendors),direct_targets=len(targets),critical_operands=len(critical),inventory_boundaries=3,prior_callback_byte_equal=True)
out=dict(task='C11',rom_path=str(ROM),base=hex(BASE),checks=checks,windows=windows,vendor_words=vendors,inventory_entries=entries,strings=strings,model=dict(path=str(model/'ap01thead2.sinc'),line=i+1,text='\n'.join(lines[i:i+5]),register_path=str(model/'ap01thead2.reg.sinc'),register_excerpt='\n'.join(reglines[1163:1166])),limits=['Static data decoding only; no target execution.','Vendor semantics depend on existing local model.','Nested flag side effects and query helper internals remain boundary calls.'])
(HERE/'instruction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks))
