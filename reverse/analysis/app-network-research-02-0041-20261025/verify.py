"""Q09 static ROM-only inspection. No firmware execution or network."""
import json
from pathlib import Path
from datetime import datetime, timezone
import capstone

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
WINDOWS = [(0xa0067aec,168),(0xa0067b94,82),(0xa0068854,192),(0xa0068914,274)]

def main():
    rom = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
    cs = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'source': str(rom), 'capstone': capstone.__version__, 'windows': []}
    with rom.open('rb') as f:
        for va, length in WINDOWS:
            f.seek(va-BASE)
            data = f.read(length)
            # Two known vendor words are retained opaque in standard Capstone.
            # Their semantics are inherited from the existing SINC, not patched here.
            rows = []
            pos = 0
            while pos < length:
                at = va + pos
                if at in (0xa006895a, 0xa00689ce):
                    word = data[pos:pos+4]
                    assert word.hex() == {0xa006895a:'8bd64758',0xa00689ce:'8b56f944'}[at]
                    rows.append(f'{at:08x} {word.hex()} vendor-word (see existing ap01thead2.sinc)')
                    pos += 4
                else:
                    i = next(cs.disasm(data[pos:], at, count=1))
                    rows.append(f'{i.address:08x} {i.bytes.hex():8s} {i.mnemonic} {i.op_str}')
                    pos += i.size
            assert pos == length
            result['windows'].append({'va':hex(va),'offset':hex(va-BASE),'length':length,'hex':data.hex(),'assembly':rows})
    evidence = ROOT/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
    record = json.loads(evidence.read_text(encoding='utf-8'))['records'][89]
    result['caller'] = {'path':str(evidence),'pointer':'#/records/89','evidence_id':record['evidence_id'],'profile':record['analysis_profile']['digest'],
                        'assembly':[s for s in record['normalized_result']['assembly'] if any(lo<=int(s.split(':')[0],16)<=hi for lo,hi in [(0xa006e350,0xa006e3d0),(0xa006e5ac,0xa006e5b8),(0xa006e6aa,0xa006e6e8),(0xa006e75c,0xa006e86b)])]}
    checks = {0xa0067b10:'23a0b41c',0xa0067b18:'63f8b704',0xa0067bb4:'b947',0xa0067bb8:'63e3b702',0xa006887a:'23a2b418',0xa006887e:'63e6f506',0xa006893a:'b3d7e702',0xa0068946:'63eaf508',0xa006896a:'1cdf',0xa0068970:'63e3e708'}
    with rom.open('rb') as f:
        for va,h in checks.items():
            f.seek(va-BASE)
            assert f.read(len(bytes.fromhex(h))).hex()==h, hex(va)
    result['checks'] = {hex(k):v for k,v in checks.items()}
    result['diagnostic_strings'] = {}
    with rom.open('rb') as f:
        for va in (0xa0258f64,0xa0258f88,0xa025925c,0xa025926c,0xa025927c,0xa025929c,0xa02592c0,0xa02592d4):
            f.seek(va-BASE)
            result['diagnostic_strings'][hex(va)] = f.read(160).split(b'\0')[0].decode('utf-8')
    (OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    for w in result['windows']:
        print('\n'.join(w['assembly']))

if __name__ == '__main__':
    main()
