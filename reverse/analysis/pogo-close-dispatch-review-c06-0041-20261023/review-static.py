"""C06 independent, bounded ROM review; does not execute target instructions."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
rom = ROM.read_bytes()
prior = json.loads((ROOT / 'reverse/analysis/pogo-close-dispatch-c05-0041-20261023/instruction-evidence.json').read_text())
checked = []

def raw(pc, encoding, meaning):
    expected = bytes.fromhex(encoding)
    observed = rom[pc-BASE:pc-BASE+len(expected)]
    assert observed == expected, hex(pc)
    checked.append(dict(address=hex(pc), hex=observed.hex(), reviewed_meaning=meaning))

# Independently selected path controls, field widths, register transfers and tails.
# Meanings below are manual RV32/RVC decoding, not decompiler output.
for pc, encoding, meaning in [
    (0xa009fbaa,'5c55','c.lw a5,44(a0)'),
    (0xa009fbac,'13f73700','andi a4,a5,3'),
    (0xa009fbb0,'09cb','c.beqz a4,a009fbc2'),
    (0xa009fbc2,'13e71700','ori a4,a5,1'),
    (0xa009fbc6,'58d5','c.sw a4,44(a0)'),
    (0xa009fbc8,'03478500','lbu a4,8(a0)'),
    (0xa009fbcc,'4cc5','c.sw a1,12(a0)'),
    (0xa009fbd0,'2a89','c.mv s2,a0'),
    (0xa009fbd2,'630fd702','beq a4,a3,a009fc10; a3=9'),
    (0xa009fbd6,'63e4e606','bltu a3,a4,a009fc3e; 9<8 is false'),
    (0xa009fbdc,'6304d73e','beq a4,a3,a009ffc4; a3=4'),
    (0xa009fbe0,'63efe600','bltu a3,a4,a009fbfe; 4<8 is true'),
    (0xa009fc00,'6301d70c','beq a4,a3,a009fcc2; a3=7'),
    (0xa009fc04,'a146','c.li a3,8'),
    (0xa009fc06,'630cd73a','beq a4,a3,a009ffbe'),
    (0xa009ffbe,'eff05f9b','jal ra,a009f972; a0 still original handle'),
    (0xa009ffc2,'31bb','c.j a009fcde'),
    (0xa009fcde,'4a85','c.mv a0,s2'),
    (0xa009fce0,'efc08fd4','jal ra,a009c228'),
    (0xa009fce4,'89a6','c.j a00a0026'),
    (0xa009c230,'5c55','c.lw a5,44(a0)'),
    (0xa009c232,'13f71700','andi a4,a5,1'),
    (0xa009c236,'11eb','c.bnez a4,a009c24a'),
    (0xa009c24a,'898b','c.andi a5,2'),
    (0xa009c24c,'89c7','c.beqz a5,a009c256'),
    (0xa009c256,'5c41','c.lw a5,4(a0)'),
    (0xa009c258,'03a7470d','lw a4,212(a5)'),
    (0xa009c25c,'18d5','c.sw a4,40(a0)'),
    (0xa009c25e,'23aaa70c','sw a0,212(a5)'),
    (0xa005c166,'03a5440d','lw a0,212(s1)'),
    (0xa005c16a,'23aa040c','sw zero,212(s1)'),
    (0xa005c16e,'631a0568','bne a0,zero,a005c802'),
    (0xa005c802,'832a8502','lw s5,40(a0); save next before call'),
    (0xa005c806,'ef20f451','jal ra,a009f524'),
    (0xa005c80a,'5685','c.mv a0,s5'),
    (0xa005c80c,'8db2','c.j a005c16e'),
    (0xa009f538,'5c55','c.lw a5,44(a0)'),
    (0xa009f53a,'13f71700','andi a4,a5,1'),
    (0xa009f53e,'11eb','c.bnez a4,a009f552'),
    (0xa009f552,'13f72700','andi a4,a5,2'),
    (0xa009f556,'09c7','c.beqz a4,a009f560'),
    (0xa009f560,'13e72700','ori a4,a5,2'),
    (0xa009f564,'58d5','c.sw a4,44(a0)'),
    (0xa009f566,'03478500','lbu a4,8(a0)'),
    (0xa009f56c,'aa84','c.mv s1,a0'),
    (0xa009f580,'8547','c.li a5,1'),
    (0xa009f582,'3397e700','sll a4,a5,a4'),
    (0xa009f586,'8967','c.lui a5,2'),
    (0xa009f588,'9387e775','addi a5,a5,0x75e'),
    (0xa009f58c,'f98f','c.and a5,a4'),
    (0xa009f58e,'63940732','bne a5,zero,a009f8b6'),
    (0xa009f8b6,'dc54','c.lw a5,44(s1)'),
    (0xa009f8b8,'13f78700','andi a4,a5,8'),
    (0xa009f8bc,'09cf','c.beqz a4,a009f8d6'),
    (0xa009f8be,'13f777ff','andi a4,a5,-9; clear bit3'),
    (0xa009f8c2,'d8d4','c.sw a4,44(s1)'),
    (0xa009f8c4,'13f71700','andi a4,a5,1; old flags bit0'),
    (0xa009f8c8,'19e7','c.bnez a4,a009f8d6'),
    (0xa009f8d6,'13850401','addi a0,s1,16'),
    (0xa009f8da,'ef900fa7','jal ra,a0098b4a'),
    (0xa009f8de,'dc44','c.lw a5,12(s1)'),
    (0xa009f8e0,'e38d07cc','beq a5,zero,a009f5ba'),
    (0xa009f8e4,'2685','c.mv a0,s1'),
    (0xa009f8e6,'8297','c.jalr a5; original handle is a0'),
    (0xa009f8e8,'c9b9','c.j a009f5ba'),
    (0xa009e5f6,'a147','c.li a5,8'),
    (0xa009e5fc,'2384fa00','sb a5,8(s5)'),
    (0xa009e600,'23a6fa02','sw a5,44(s5)'),
    (0xa009e604,'23a23a01','sw s3,4(s5)'),
    (0xa00a3bd0,'0441','c.lw s1,0(a0); context read by callback'),
]:
    raw(pc, encoding, meaning)

count = 0
for window in prior['windows']:
    for ins in window['instructions']:
        pc = int(ins['address'], 16)
        data = bytes.fromhex(ins['hex'])
        assert rom[pc-BASE:pc-BASE+len(data)] == data
        count += len(data)
assert count == 490
assert ((1 << 8) & ((2 << 12) + 0x75e)) == 0x100
# Reconstruct signed branch/JAL destinations directly from architectural bit slots.
targets = []
def signed(value, width):
    return value - (1 << width) if value & (1 << (width-1)) else value

for pc, expected in [
    (0xa009fbd2,0xa009fc10), (0xa009fbd6,0xa009fc3e),
    (0xa009fbdc,0xa009ffc4), (0xa009fbe0,0xa009fbfe),
    (0xa009fc00,0xa009fcc2), (0xa009fc06,0xa009ffbe),
    (0xa009ffbe,0xa009f972), (0xa009fce0,0xa009c228),
    (0xa005c16e,0xa005c802), (0xa005c806,0xa009f524),
    (0xa009f58e,0xa009f8b6), (0xa009f8da,0xa0098b4a),
    (0xa009f8e0,0xa009f5ba),
]:
    word = int.from_bytes(rom[pc-BASE:pc-BASE+4], 'little')
    bits = lambda top, bottom: (word >> bottom) & ((1 << (top-bottom+1))-1)
    if word & 127 == 0x63:
        disp = (bits(31,31)<<12) | (bits(7,7)<<11) | (bits(30,25)<<5) | (bits(11,8)<<1)
        dest = pc + signed(disp,13)
        fields = dict(funct3=bits(14,12), rs1=bits(19,15), rs2=bits(24,20))
    else:
        assert word & 127 == 0x6f
        disp = (bits(31,31)<<20) | (bits(19,12)<<12) | (bits(20,20)<<11) | (bits(30,21)<<1)
        dest = pc + signed(disp,21)
        fields = dict(rd=bits(11,7))
    assert dest == expected
    targets.append(dict(address=hex(pc), target=hex(dest), fields=fields))
result = dict(task='C06', core_functions=['0xa009fb96','0xa009c228','0xa009f524'],
    validation=dict(prior_selected_windows=len(prior['windows']), prior_selected_bytes_match=count,
                    independent_reviewed_encodings=len(checked), independently_extracted_targets=len(targets), type8_mask_result='0x100',
                    firmware_executed=False), reviewed_encodings=checked, extracted_targets=targets,
    result='accepted_with_scope_limits', correction_required=False,
    limitations=['Assert and opaque callees not certified.', 'No scheduling/liveness guarantee.',
                 'No complete event-loop or timer recovery.', 'No source/version identification.'])
(HERE/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result['validation']))
