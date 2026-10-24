"""Q17 bounded static disassembly; does not execute firmware."""
import json
from pathlib import Path
from datetime import datetime, timezone
import capstone

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
WINDOWS = [(0xa0067be6,58),(0xa0067c20,128),(0xa0195ce4,374)]

def main():
    rom = ROOT/'roms/0041/ap01-1.0.2_0041.bin'
    assert rom.stat().st_size == 6769704
    cs = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
    result = {'utc':datetime.now(timezone.utc).isoformat(), 'source':str(rom), 'capstone':capstone.__version__, 'windows':[]}
    with rom.open('rb') as f:
        for va,n in WINDOWS:
            f.seek(va-BASE)
            data=f.read(n)
            rows=[]
            pos=0
            while pos<n:
                i=next(cs.disasm(data[pos:],va+pos,count=1),None)
                if i is None:
                    raise ValueError(hex(va+pos)+': '+data[pos:pos+4].hex())
                rows.append(f'{i.address:08x} {i.bytes.hex():8s} {i.mnemonic} {i.op_str}')
                pos+=i.size
            assert pos==n
            result['windows'].append({'va':hex(va),'offset':hex(va-BASE),'length':n,'hex':data.hex(),'assembly':rows})
    checks = {0xa0067c02:'23a8041c',0xa0067c12:'239af41c',0xa0067c42:'03478900',0xa0067c48:'63f9e702',0xa0067c52:'631bf702',0xa0067c7a:'b7871040',0xa0067c82:'858b',0xa0067c98:'4a85',0xa0195d10:'231c04f6',0xa0195d14:'230d04f6',0xa0195d40:'c145',0xa0195d66:'fd54',0xa0195db4:'a30504f8',0xa0195dc0:'2318e4f8',0xa0195dda:'232ae4f8',0xa0195dde:'232ef4f8',0xa0195de2:'232c44f9',0xa0195e46:'5147',0xa0195e50:'9145',0xa0195e52:'ef3068fe'}
    with rom.open('rb') as f:
        for va,h in checks.items():
            f.seek(va-BASE)
            assert f.read(len(bytes.fromhex(h))).hex()==h, hex(va)
        result['strings']={}
        for va in (0xa0259474,0xa0259484,0xa062c718,0xa0258fbc,0xa0258e08):
            f.seek(va-BASE)
            result['strings'][hex(va)]=f.read(180).split(b'\0')[0].decode('utf-8')
    result['checks']={hex(k):v for k,v in checks.items()}
    result['gate_blocked_values']=[i for i in range(256) if i==50 or (i<=30 and (0x40108000>>i)&1)]
    assert result['gate_blocked_values']==[15,20,30,50]
    source=ROOT/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
    record=json.loads(source.read_text(encoding='utf-8'))['records'][89]
    result['caller']={'source':str(source),'pointer':'#/records/89/normalized_result','evidence_id':record['evidence_id'],'profile':record['analysis_profile']['digest'],'assembly':[s for s in record['normalized_result']['assembly'] if any(lo<=int(s.split(':')[0],16)<=hi for lo,hi in [(0xa006e37c,0xa006e3d0),(0xa006e5a6,0xa006e5b8),(0xa006e6aa,0xa006e6be),(0xa006e75c,0xa006e778),(0xa006e786,0xa006e7cc)])]}
    (OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\n'.join(row for w in result['windows'] for row in w['assembly']))

if __name__=='__main__':
    main()
