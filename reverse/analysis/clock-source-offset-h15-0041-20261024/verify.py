import json, subprocess
from pathlib import Path
from capstone import *
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
rom=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
c=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
a,b=0xa0026460,0xa002648c
raw=rom[a-BASE:b-BASE]; ins=list(c.disasm(raw,a)); assert sum(x.size for x in ins)==len(raw)
expected={0xa0026464:'83a747c6',0xa002646c:'b3d6e702',0xa0026470:'b3f7e702',0xa002647c:'14c1',0xa002647e:'b387e702',0xa0026482:'5cc1',0xa0026486:'0145',0xa002648a:'8280'}
for pc,h in expected.items():assert rom[pc-BASE:pc-BASE+len(h)//2].hex()==h
assert 0x62fc7000-0x39c==0x62fc6c64
assert (0xf4<<12)+0x240==1000000
for pc,funct3 in [(0xa002646c,5),(0xa0026470,7),(0xa002647e,0)]:
 w=int.from_bytes(rom[pc-BASE:pc-BASE+4],'little');assert w&127==0x33 and w>>25==1 and (w>>12)&7==funct3
# Read only selected source lines in existing local candidate; no build, model or target execution.
remote="""import json
from pathlib import Path
root=Path('/home/slepher/nuttx-ap01-sim/nuttx')
sel={'sched/clock/clock_systime_timespec.c':[(45,59),(62,89)],'sched/clock/clock_gettime.c':[(88,115)],'sched/clock/clock_settime.c':[(73,85)],'include/nuttx/clock.h':[(340,351)]}
out=[]
for rel,ranges in sel.items():
 lines=(root/rel).read_text().splitlines()
 out.append({'path':str(root/rel),'excerpts':[{'start':a,'end':b,'lines':[f'{i+1}: {lines[i]}' for i in range(a-1,b)]} for a,b in ranges]})
print(json.dumps(out))
"""
p=subprocess.run(['wsl.exe','-d','Ubuntu-24.04','--exec','python3','-c',remote],capture_output=True)
if p.returncode:raise SystemExit(p.stderr.decode(errors='replace'))
source=json.loads(p.stdout)
(HERE/'candidate-excerpts.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Bounded retained-text search only, never scan ROM fields or infer absent writers.
scopes=[MAIN/'reverse/analysis/0041-20261013',MAIN/'evidence/rea-0041-20261017/round3/evidence',MAIN/'reverse/raw']
search=[]
for scope in scopes:
 p=subprocess.run(['rg','-l','-i','a002645a|62fc5c74|62fc5c78|62fc6c64',str(scope)],capture_output=True)
 assert p.returncode in [0,1]
 search.append({'root':str(scope),'query':'a002645a|62fc5c74|62fc5c78|62fc6c64','matching_files':p.stdout.decode().splitlines(),'exit_code':p.returncode})
result={'scope':'static normal lower output only; no time replay','source_address':'0x62fc6c64','window':{'start':hex(a),'end_exclusive':hex(b),'hex':raw.hex(),'instructions':[f'{i.address:08x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in ins]},'validated_arithmetic':'out[0]=u32(load)/1000; out[1]=(u32(load)%1000)*1000000; a0=0','bounded_search':search,'offset_writer_seed_found':False,'new_rea_target':False,'unknown':['counter writer/cadence/origin','ROM offset writer','ROM exact source/version','epoch and calibration policy']}
(HERE/'static-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'byte_anchors':len(expected),'candidate_files':len(source),'bounded_search':search},ensure_ascii=False))
