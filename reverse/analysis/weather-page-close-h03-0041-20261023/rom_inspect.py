"""Read-only ROM inspection helper; never imports or executes firmware."""
import json,sys
from pathlib import Path
import capstone
HERE=Path(__file__).resolve().parent
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE=0x9ffff000
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
def decode(lo,hi):
    result=[]; pc=lo
    while pc<hi:
        raw=ROM[pc-BASE:pc-BASE+4]; w=int.from_bytes(raw,'little')
        if w&127==11:
            size=4; t=f'vendor word=0x{w:08x} rd={(w>>7)&31} rs1={(w>>15)&31} rs2={(w>>20)&31} f3={(w>>12)&7} high={w>>27} shift={(w>>25)&3}'
        else:
            ins=next(md.disasm(raw,pc,count=1),None)
            if not ins: size=2 if w&3!=3 else 4; t='unknown'
            else:
                size=ins.size; t=ins.mnemonic+' '+ins.op_str
                if ins.mnemonic in ['jal','j','beq','bne','beqz','bnez','blt','bge','bltu','bgeu','c.j','c.jal','c.beqz','c.bnez']:
                    rel=int(ins.op_str.split(',')[-1].strip(),0)
                    t+=' ; target=0x%08x'%((pc+rel)&0xffffffff)
        result.append(dict(address=f'0x{pc:08x}',offset=pc-BASE,bytes=raw[:size].hex(),text=t.strip()))
        pc+=size
    assert pc==hi,(hex(lo),hex(hi),hex(pc))
    return result
if __name__=='__main__':
    lo,hi=map(lambda x:int(x,16),sys.argv[1:3]); d=decode(lo,hi)
    p=HERE/f'{lo:08x}-{hi:08x}.txt'
    p.write_text('\n'.join(f"{x['address']} {x['bytes']:8} {x['text']}" for x in d))
    print(p, len(d))
