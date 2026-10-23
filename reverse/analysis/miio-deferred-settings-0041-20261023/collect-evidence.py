"""Collect retained static evidence and ROM windows; does not execute firmware."""
import hashlib
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = 0x9ffff000
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
digest = lambda b: hashlib.sha256(b).hexdigest()
identity = digest(rom)
assert identity == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)

def save(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

functions = []
for ordinal in [10, 15, 19, 20]:
    rel = f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{ordinal:03}.json'
    raw = (ROOT / rel).read_bytes()
    obj = json.loads(raw)
    e = obj.get('structuredContent') or json.loads(obj['content'][0]['text'])
    n = e['normalized_result']
    ranges = []
    for span in n['procedure']['body']['ranges']:
        a, b = int(span['start'],16), int(span['end'],16)+1
        data = rom[a-BASE:b-BASE]
        ranges.append(dict(start=hex(a), end_exclusive=hex(b), file_offset=a-BASE,
                           hex=data.hex(), sha256=digest(data)))
    functions.append(dict(source=dict(path=rel,sha256=digest(raw)), evidence_id=e['evidence_id'],
                          profile=e['analysis_profile'], normalized_result=n, raw_ranges=ranges))
save('retained-functions.json', dict(rom_sha256=identity, functions=functions,
     scope='Scheduler and callback reviewed; property handlers reviewed only for scheduler submissions, location/city/district and kind-1 mode branch. Other branches remain unreviewed here.'))

windows=[]
for name,a,b in [('callback',0xa00a0bd8,0xa00a0e78),('scheduler',0xa009d286,0xa009d304),
                 ('mode_sink',0xa019537a,0xa01953f6),('weather_restart_bridge',0xa00a5b90,0xa00a5bbe),
                 ('timer_control_prefix',0xa01b2b5c,0xa01b2ba0)]:
    data=rom[a-BASE:b-BASE];pc=a;lines=[]
    while pc<b:
        off=pc-BASE;size=4 if rom[off]&3==3 else 2
        assert pc+size<=b
        i=next(md.disasm(rom[off:off+size],pc),None)
        lines.append(dict(address=hex(pc),hex=rom[off:off+size].hex(),assembly=i.mnemonic+' '+i.op_str if i else '.unknown'+str(size*8)))
        pc+=size
    windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=data.hex(),sha256=digest(data),instructions=lines))
save('instruction-windows.json',dict(rom_sha256=identity,engine=cs_version(),windows=windows,
     limitations=['RV32C instruction windows, not original source', 'timer_control_prefix is only a prefix; no complete function or exact library version claim']))

def sext(v,bits):
    return v-(1<<bits) if v & (1<<(bits-1)) else v

calls=[]
for off in range(0,len(rom)-7,2):
    word=int.from_bytes(rom[off:off+4],'little');pc=BASE+off
    if word & 0x7f == 0x6f:
        imm=((word>>31)<<20)|(((word>>12)&255)<<12)|(((word>>20)&1)<<11)|(((word>>21)&1023)<<1)
        if (pc+sext(imm,21)) & 0xffffffff == 0xa009d286:
            calls.append(dict(address=hex(pc),kind='JAL',rd=(word>>7)&31,hex=rom[off:off+4].hex()))
    if word & 0x7f == 0x17:
        nxt=int.from_bytes(rom[off+4:off+8],'little');rd=(word>>7)&31
        if nxt & 0x707f == 0x67 and (nxt>>15)&31 == rd:
            target=(pc+sext(word&0xfffff000,32)+sext(nxt>>20,12))&0xfffffffe
            if target==0xa009d286:
                calls.append(dict(address=hex(pc+4),kind='adjacent AUIPC/JALR',rd=(nxt>>7)&31,hex=rom[off:off+8].hex()))
save('direct-submission-scan.json',dict(rom_sha256=identity,candidates=calls,
     method='All even offsets across ROM: standard JAL destination and adjacent AUIPC/JALR pair destination',
     limitations=['Non-code can match; original instructions and retained callers require review',
                  'Does not cover indirect calls, non-adjacent construction or RAM-loaded code; not an all-caller proof']))
print(json.dumps(dict(functions=len(functions),windows=len(windows),direct_call_candidates=calls)))
