"""B04 bounded ROM/evidence comparison; never executes target code."""
import json
import sys
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path(sys.argv[1])
BASE = 0x9ffff000
rom = (SOURCE / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
f = next(f for f in json.loads((TREE / 'reverse/analysis/usb-interface-ota-0041-20261023.json').read_text(encoding='utf-8'))['functions'] if f['address'] == '0xa00a8582')
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
specs = [('entry', 0xa00a8582, 0xa00a85cc),
         ('cmd55-test', 0xa00a8602, 0xa00a861e),
         ('cmd55-post-cache-gate', 0xa00a88f6, 0xa00a896a),
         ('setup-predecessor-and-writes', 0xa00a8a22, 0xa00a8ab4),
         ('registration-and-reset-loops', 0xa00a8b50, 0xa00a8b72)]
decoded = {}
windows = []
for name, start, end in specs:
    raw = rom[start-BASE:end-BASE]
    retained = next(r for r in f['raw_ranges'] if r['file_offset'] <= start-BASE and r['file_offset'] + len(bytes.fromhex(r.get('bytes_hex', r.get('hex', '')))) >= end-BASE)
    off = start-BASE-retained['file_offset']
    assert raw == bytes.fromhex(retained.get('bytes_hex', retained.get('hex', '')))[off:off+len(raw)]
    records = []
    pc = start
    for line in f['assembly']:
        addr = int(line.split(':')[0], 16)
        if not start <= addr < end:
            continue
        assert pc == addr
        n = 4 if rom[pc-BASE] & 3 == 3 else 2
        b = rom[pc-BASE:pc-BASE+n]
        ins = next(md.disasm(b, pc), None)
        if pc in (0xa00a893a, 0xa00a8b62):
            assert ins is None
            w = int.from_bytes(b, 'little')
            fields = dict(op=w&127, funct3=(w>>12)&7, rd=(w>>7)&31, rs1=(w>>15)&31, rs2=(w>>20)&31)
            if pc == 0xa00a893a:
                assert (fields['op'], fields['funct3'], fields['rd'], fields['rs1'], (w>>26)&63, (w>>20)&63) == (11,3,14,14,15,0)
                assembly = 'th.extu a4,a4,15,0 => a4 & 0xffff'
            else:
                assert (fields['op'], fields['funct3'], fields['rd'], fields['rs1'], fields['rs2'], (w>>25)&3, w>>27) == (11,1,13,12,15,3,0)
                assembly = 'th.addsl a3,a2,a5,3 => a2+(a5<<3)'
        else:
            assert ins is not None and ins.size == n
            assembly = ins.mnemonic + ' ' + ins.op_str
            decoded[pc] = ins
        records.append(dict(address=hex(pc), hex=b.hex(), retained_assembly=line.split(': ',1)[1], independent_decode=assembly))
        pc += n
    assert pc == end
    windows.append(dict(name=name, start=hex(start), end_exclusive=hex(end), file_offset=start-BASE, instructions=records))

target = lambda pc: pc + int(decoded[pc].op_str.split(',')[-1].strip(), 0)
expected_targets = {0xa00a8606:0xa00a88f6, 0xa00a8904:0xa0191652,
                    0xa00a893e:0xa00a8950, 0xa00a894e:0xa00a88e2,
                    0xa00a8966:0xa00a8a22, 0xa00a8a3c:0xa00a8a82,
                    0xa00a8a6c:0xa00a8aca, 0xa00a8a88:0xa00a8b50,
                    0xa00a8aaa:0xa00a8b62, 0xa00a8aae:0xa0191746,
                    0xa00a8ab2:0xa00a85e4, 0xa00a8b60:0xa00a8a88,
                    0xa00a8b70:0xa00a8aa6}
for pc, dest in expected_targets.items():
    assert target(pc) == dest
assert decoded[0xa00a8b52].op_str == 'a0, s2, -0x376'
assert decoded[0xa00a8b56].op_str == 'ra, 0x10a'
assert decoded[0xa00a8b5a].op_str == 'ra, ra, -0x288'
assert 0xa00a8b56 + 0x10a000 - 0x288 == 0xa01b28ce

def store(pc, rs1, rs2, offset):
    w = int.from_bytes(rom[pc-BASE:pc-BASE+4], 'little')
    imm = ((w>>25)<<5) | ((w>>7)&31)
    imm = imm-4096 if imm&2048 else imm
    assert (w&127, (w>>12)&7, (w>>15)&31, (w>>20)&31, imm) == (35,0,rs1,rs2,offset)

store(0xa00a8a98,15,13,5)
store(0xa00a8a9c,15,0,7)
store(0xa00a8b68,13,0,6)
assert decoded[0xa00a8a94].op_str == 'a3, 1'
assert decoded[0xa00a8a88].mnemonic == 'blt'
assert decoded[0xa00a8aaa].mnemonic == 'bltu'
assert decoded[0xa00a8b6c].op_str == 'a5, a5, 0xff'

models = []
model_dir = SOURCE / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages'
for filename, needles in [('ap01thead2.sinc', [':th.addsl ', ':th.extu rd,rs1,15,0 ']), ('ap01thead2.reg.sinc', ['  thshift=', '  thlsb=', '  thmsb='])]:
    lines = (model_dir/filename).read_text(encoding='utf-8').splitlines()
    for needle in needles:
        i = next(i for i,l in enumerate(lines) if l.startswith(needle))
        end = next(j for j in range(i+1,len(lines)) if lines[j] == '}')+1 if filename == 'ap01thead2.sinc' else i+1
        models.append(dict(path=str(model_dir/filename), start_line=i+1, text='\n'.join(lines[i:end])))

checks = dict(windows=len(windows), ordinary_instructions=len(decoded), vendor_words=2,
              raw_ranges_match=True, direct_targets=len(expected_targets), byte_stores=3,
              state_write_order=['phase=1','round_done=0','sent[i]=0','selector'],
              result='passed')
out = dict(task='B04', source=f['source'], evidence_id=f['evidence_id'], windows=windows,
           vendor_model_excerpts=models, checks=checks,
           limits=['One callback local branch; prelude callees are opaque and assumed to return for reachability.',
                   'No target execution, external services, shared REA session or model edits.',
                   'The reset loop reloads count each iteration and uses an 8-bit index.'])
(HERE/'instruction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks))
