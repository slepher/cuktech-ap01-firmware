"""A13 bounded offline ROM read and existing local source excerpts. No target execution."""
import json
from pathlib import Path
import subprocess
import capstone

HERE = Path(__file__).resolve().parent
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
with ROM.open('rb') as f:
    f.seek(0xa00272d4 - BASE)
    raw = f.read(248)
assert len(raw) == 248
decoder = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
rows = [dict(pc=hex(i.address), bytes=i.bytes.hex(), asm=i.mnemonic + ' ' + i.op_str)
        for i in decoder.disasm(raw, 0xa00272d4)]
assert sum(len(bytes.fromhex(r['bytes'])) for r in rows) == 248
prior = json.loads((HERE.parent / 'current-object-writer-review-a12-0041-20261023/review-evidence.json').read_text(encoding='utf8'))
assert rows == [r for w in prior['windows'] for r in w['instructions']]
rom_evidence = dict(rom=str(ROM), mapping_base=hex(BASE), start='0xa00272d4',
                    end_exclusive='0xa00273cc', capstone=capstone.__version__,
                    a12_rows_equal=True, instructions=rows)
rom_evidence['diagnostic_strings'] = []
with ROM.open('rb') as f:
    for address in [0xa01bc0b0, 0xa01bc0d0]:
        f.seek(address - BASE)
        data = f.read(64)
        assert b'\x00' in data
        value = data.split(b'\x00', 1)[0]
        rom_evidence['diagnostic_strings'].append(dict(address=hex(address),
            bytes_through_nul=(value+b'\x00').hex(), text=value.decode('ascii')))
(HERE / 'rom-evidence.json').write_text(json.dumps(rom_evidence, indent=2) + '\n', encoding='utf8')

# This Python executes on the local host distribution only; it reads source/Git.
source_reader = r'''
import json, subprocess
from pathlib import Path
root = Path('/home/slepher/nuttx-ap01-sim/nuttx')
ranges = {
 'sched/sched/sched_addreadytorun.c': [(40,117)],
 'sched/sched/sched.h': [(49,78),(356,367),(390,396),(441,518)],
 'include/nuttx/sched.h': [(243,252),(560,575),(593,619)],
 'include/nuttx/arch.h': [(992,994)],
 'include/sys/types.h': [(80,87)],
}
def git(*args):
 p = subprocess.run(['git','-C',str(root),*args],text=True,capture_output=True)
 return dict(args=list(args),exit=p.returncode,stdout=p.stdout,stderr=p.stderr)
checks = [git('rev-parse','HEAD'),git('describe','--tags','--exact-match','HEAD'),
          git('rev-parse','--is-shallow-repository'),
          git('tag','--list'),git('status','--short','--',*ranges),
          git('diff','HEAD','--exit-code','--',*ranges),
          git('ls-tree','-r','--name-only','HEAD','sched/sched/sched_addprioritized.c')]
assert all(x['exit']==0 for x in checks)
assert checks[4]['stdout']=='' and checks[5]['stdout']==''
excerpts = []
for file, spans in ranges.items():
 lines = (root/file).read_text().splitlines()
 excerpts.append(dict(path=str(root/file), spans=[dict(start=a,end=b,
   lines=[dict(line=i,text=lines[i-1]) for i in range(a,b+1)]) for a,b in spans]))
print(json.dumps(dict(root=str(root),git_checks=checks,excerpts=excerpts)))
'''
result = subprocess.run(['wsl','-d','Ubuntu-24.04','--','python3','-c',source_reader],
                        text=True,capture_output=True,encoding='utf8')
assert result.returncode == 0, result.stderr
source = json.loads(result.stdout)
(HERE / 'source-evidence.json').write_text(json.dumps(source, indent=2) + '\n', encoding='utf8')
print(json.dumps(dict(rom_bytes=len(raw), instructions=len(rows), a12_equal=True,
                     local_reference=source['git_checks'][1]['stdout'].strip(),
                     source_files=len(source['excerpts']))))
