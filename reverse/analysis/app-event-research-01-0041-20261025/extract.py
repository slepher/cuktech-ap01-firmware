"""Q19 bounded static extraction only; no target execution or shared REA state."""
import json
from pathlib import Path
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
WINDOWS = [(0xa011408a,192),(0xa0113f6c,286),(0xa011c204,428),(0xa01af798,660)]

def main():
    image = ROOT/'roms/0041/ap01-1.0.2_0041.bin'
    assert image.stat().st_size == 6769704
    decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
    result = {'method':'offline bounded static decoding; no firmware execution', 'decoder':capstone.__version__, 'mapping':'file_offset = VA - 0x9ffff000', 'windows':[]}
    with image.open('rb') as stream:
        for start,length in WINDOWS:
            stream.seek(start-BASE); data=stream.read(length); rows=[]; pos=0
            while pos<len(data):
                half=int.from_bytes(data[pos:pos+2],'little'); size=4 if half&3==3 else 2
                raw=data[pos:pos+size]; decoded=list(decoder.disasm(raw,start+pos))
                asm=decoded[0].mnemonic+' '+decoded[0].op_str if len(decoded)==1 and decoded[0].size==size else 'UNDECODED'
                rows.append({'pc':hex(start+pos),'raw':raw.hex(),'asm':asm});pos+=size
            assert pos==length
            result['windows'].append({'start':hex(start),'length':length,'offset':start-BASE,'raw':data.hex(),'rows':rows})
            print('\n'+hex(start))
            for row in rows: print(row['pc'],row['raw'],row['asm'])
    (OUT/'raw.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    bundle_path=ROOT/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
    bundle=json.loads(bundle_path.read_text(encoding='utf-8'))
    root=bundle['records'][233]
    assert root['evidence_id']=='ev_b7f9c05652b41f5486cbdecf96f07079792f9d25bf48dcfb216ec0448259d9a0'
    (OUT/'inherited-root.json').write_text(json.dumps(root,indent=2),encoding='utf-8')
    print('root profile',root['analysis_profile']['digest'])

if __name__=='__main__': main()
