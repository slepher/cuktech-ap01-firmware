"""B06 static ROM decoding only; no target execution."""
import json
import sys
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path(sys.argv[1])
BASE = 0x9ffff000
rom = (SOURCE / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
inventory = json.loads((TREE / 'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text(encoding='utf-8'))
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
specs = [('registration',0xa01b28ce,0xa01b291a),('append',0xa008af14,0xa008af68),
         ('link-accessors',0xa0089cda,0xa0089d02),('caller',0xa00a8b50,0xa00a8b62)]
windows = []
decoded = {}
vendor = []
for name,start,end in specs:
    pc = start
    records = []
    while pc < end:
        off = pc-BASE
        n = 4 if rom[off]&3 == 3 else 2
        raw = rom[off:off+n]
        ins = next(md.disasm(raw,pc),None)
        if ins:
            assert ins.size == n
            asm = ins.mnemonic+' '+ins.op_str
            decoded[pc] = ins
        else:
            w = int.from_bytes(raw,'little')
            fields = dict(op=w&127,rd=(w>>7)&31,funct3=(w>>12)&7,rs1=(w>>15)&31,rs2=(w>>20)&31,shift=(w>>25)&3,funct5=w>>27)
            assert fields['op']==11 and fields['funct5']==8 and fields['shift']==0
            assert (pc,fields['funct3'],fields['rd'],fields['rs1'],fields['rs2']) in [
                (0xa01b2912,4,14,14,13),(0xa0089ce4,5,12,11,15)]
            asm = ('th.lrw' if fields['funct3']==4 else 'th.srw')+' '+str(fields)
            vendor.append(dict(address=hex(pc),hex=raw.hex(),fields=fields))
        records.append(dict(address=hex(pc),hex=raw.hex(),decode=asm))
        pc += n
    assert pc==end
    windows.append(dict(name=name,start=hex(start),end_exclusive=hex(end),file_offset=start-BASE,instructions=records))

def target(pc):
    return pc+int(decoded[pc].op_str.split(',')[-1].strip(),0)

targets = {0xa01b28dc:0xa01b290c,0xa01b290e:0xa01b2918,0xa01b2916:0xa01b28dc,
           0xa008af26:0xa008aea0,0xa008af2c:0xa008af5a,0xa008af34:0xa0089cee,
           0xa008af3e:0xa0089cda,0xa008af44:0xa008af4e,0xa008af4a:0xa0089cee,
           0xa008af54:0xa008af5a,0xa0089ce0:0xa0089ce8,0xa0089cf4:0xa0089cfc,
           0xa00a8b60:0xa00a8a88}
for pc,dest in targets.items():
    assert target(pc)==dest,(hex(pc),hex(target(pc)),hex(dest))
assert 0xa01b28f2-0x128000+0x622 == 0xa008af14
assert 0xa00a8b56+0x10a000-0x288 == 0xa01b28ce
assert decoded[0xa01b28f2].op_str=='ra, 0xffed8'
assert decoded[0xa01b28f6].op_str=='ra, ra, 0x622'
assert decoded[0xa00a8b56].op_str=='ra, 0x10a'
assert decoded[0xa00a8b5a].op_str=='ra, ra, -0x288'
assert decoded[0xa01b2918].op_str=='ra'
assert decoded[0xa01b28fa].op_str=='s1, 0(a0)'
assert decoded[0xa01b28fc].op_str=='s2, 4(a0)'
assert decoded[0xa0089cf8].op_str=='a1, a5'
assert decoded[0xa0089cfa].op_str=='a2, 4(a1)'
assert decoded[0xa00a8b52].op_str=='a0, s2, -0x376'
model = SOURCE / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines = model.read_text(encoding='utf-8').splitlines()
excerpts=[]
for prefix in (':th.lrw ',':th.srw '):
    i=next(i for i,l in enumerate(lines) if l.startswith(prefix))
    end=next(j for j in range(i+1,len(lines)) if lines[j]=='}')+1
    excerpts.append(dict(path=str(model),line=i+1,text='\n'.join(lines[i:end])))
functions = [{k:f[k] for k in ('address','extent','direct_calls','scope','excluded_as_verified_open_source')}
             for f in inventory['functions'] if f['address'] in ('0xa01b28ce','0xa008af14','0xa0089cee','0xa0089cda')]
checks=dict(result='passed',windows=len(windows),ordinary_instructions=len(decoded),vendor_words=len(vendor),direct_branch_targets=len(targets),auipc_jalr_targets=2)
out=dict(task='B06',checks=checks,windows=windows,vendor_words=vendor,model_excerpts=excerpts,retained_inventory=functions,
         limits=['Static decoding only; no firmware execution.', 'Vendor meaning uses existing local observation model, not fresh upstream ISA certification.',
                 'List payload size is read from runtime header; its initializer is outside scope.', 'No new hash or baseline copy inventory.'])
(HERE/'instruction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks))
