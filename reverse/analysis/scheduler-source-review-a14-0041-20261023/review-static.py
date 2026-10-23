"""Bounded independent A14 checks. Reads ROM/source evidence; never runs firmware."""
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / 'scheduler-source-a13-0041-20261023'
source = json.loads((PRIOR / 'source-evidence.json').read_text(encoding='utf8'))
rom = json.loads((PRIOR / 'rom-evidence.json').read_text(encoding='utf8'))

if '--local-source' in sys.argv:
    # Local host Python/Git only, no SIM launch and no network commands.
    reader = """
import json, subprocess, sys
from pathlib import Path
s=json.load(sys.stdin)
root=Path(s['root'])
checks=[]
for c in s['git_checks']:
 p=subprocess.run(['git','-C',str(root),*c['args']],capture_output=True,text=True)
 assert (p.returncode,p.stdout)==(c['exit'],c['stdout']), c['args']
 checks.append({'args':c['args'],'matches_retained':True})
count=0
for e in s['excerpts']:
 lines=Path(e['path']).read_text().splitlines()
 for span in e['spans']:
  for line in span['lines']:
   assert lines[line['line']-1]==line['text'],(e['path'],line['line'])
   count+=1
print(json.dumps({'git_checks':checks,'source_lines_match':count,'files':len(s['excerpts'])}))
"""
    p = subprocess.run(['wsl','-d','Ubuntu-24.04','--','python3','-c',reader],
                       input=json.dumps(source),capture_output=True,text=True,encoding='utf8')
    assert p.returncode == 0, p.stderr
    result = json.loads(p.stdout)
    (HERE / 'local-source-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result))
    sys.exit(0)

rows = rom['instructions']
with Path(rom['rom']).open('rb') as f:
    f.seek(int(rom['start'],16)-int(rom['mapping_base'],16))
    raw = f.read(248)
assert raw == b''.join(bytes.fromhex(r['bytes']) for r in rows)
pc = int(rom['start'],16)
for row in rows:
    assert int(row['pc'],16)==pc
    pc += len(bytes.fromhex(row['bytes']))
assert pc == int(rom['end_exclusive'],16)
with Path(rom['rom']).open('rb') as f:
    for s in rom['diagnostic_strings']:
        expected=bytes.fromhex(s['bytes_through_nul'])
        f.seek(int(s['address'],16)-int(rom['mapping_base'],16))
        assert f.read(len(expected))==expected
        assert expected[:-1].decode('ascii')==s['text'] and expected[-1]==0

by_pc = {int(r['pc'],16):int.from_bytes(bytes.fromhex(r['bytes']),'little') for r in rows}
checks=[]
def sext(value,bits):
    return value-(1<<bits) if value>>(bits-1) else value
def field(pc,kind,expected):
    w=by_pc[pc]
    if kind=='I':
        actual=(w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,sext(w>>20,12))
    elif kind=='B':
        imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
        actual=(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,pc+sext(imm,13))
    elif kind=='J':
        imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        actual=(w&127,(w>>7)&31,pc+sext(imm,21))
    elif kind=='CB':
        imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
        actual=(w&3,(w>>13)&7,8+((w>>7)&7),pc+sext(imm,9))
    elif kind=='CSW':
        imm=(((w>>10)&7)<<3)|(((w>>6)&1)<<2)|(((w>>5)&1)<<6)
        actual=(w&3,(w>>13)&7,8+((w>>7)&7),8+((w>>2)&7),imm)
    assert actual==expected,(hex(pc),kind,actual,expected)
    checks.append(dict(pc=hex(pc),kind=kind,fields=list(actual)))

for pc,kind,expected in [
 (0xa00272d4,'I',(3,14,4,10,16)),
 (0xa00272d8,'CB',(1,7,14,0xa00272f4)),
 (0xa00272e8,'I',(19,11,0,0,74)),
 (0xa00272ec,'I',(19,10,0,10,176)),
 (0xa00272f0,'J',(111,1,0xa0019672)),
 (0xa00272fc,'B',(99,7,13,14,0xa0027310)),
 (0xa002730c,'CSW',(0,6,11,10,0)),
 (0xa0027338,'CSW',(0,6,11,10,0)),
 (0xa002733a,'CSW',(0,6,11,10,4)),
 (0xa0027350,'I',(3,18,2,11,-1000)),
 (0xa0027356,'I',(3,15,1,18,32)),
 (0xa002735a,'B',(99,5,0,15,0xa002738a)),
 (0xa0027366,'B',(99,7,14,15,0xa002738a)),
 (0xa002736e,'I',(19,11,0,11,-1012)),
 (0xa0027372,'J',(111,1,0xa00272d4)),
 (0xa002738a,'I',(19,11,0,11,-1000)),
 (0xa0027390,'J',(111,1,0xa00272d4)),
 (0xa0027394,'CB',(1,6,10,0xa00273c4)),
 (0xa0027396,'I',(3,15,1,18,32)),
 (0xa002739a,'CB',(1,7,15,0xa00273a2)),
 (0xa002739e,'B',(99,4,0,15,0xa00273b4)),
 (0xa00273a8,'I',(19,11,0,0,98)),
 (0xa00273ac,'I',(19,10,0,10,208)),
 (0xa00273b0,'J',(111,1,0xa0019672)),
]: field(pc,kind,expected)

result=dict(rom_bytes=248,instructions=len(rows),all_retained_bytes_match=True,
            diagnostic_strings=rom['diagnostic_strings'],independent_encoding_checks=checks,
            source_reference='../scheduler-source-a13-0041-20261023/source-evidence.json',
            method='ROM exact reads; direct RISC-V bitfields without disassembler; manual source comparison in report')
(HERE / 'review-evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(rom_bytes=248,instructions=len(rows),encoding_checks=len(checks),strings=2)))
