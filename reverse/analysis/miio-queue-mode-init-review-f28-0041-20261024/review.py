"""F28 independent static check; no target execution or author-script import."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
OUT = Path(__file__).parent / 'review-evidence.json'
assert ROM.stat().st_size == 6769704
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
rows = {}
windows = [(0xa005f10a, 16), (0xa01974de, 48), (0xa010e320, 284)]
with ROM.open('rb') as f:
    for va, size in windows:
        f.seek(va - 0x9ffff000)
        data = f.read(size)
        decoded = list(cs.disasm(data, va))
        assert sum(i.size for i in decoded) == size
        for i in decoded:
            rows[i.address] = dict(va=hex(i.address), offset=hex(i.address-0x9ffff000),
                                  width=i.size, raw=i.bytes.hex(), text=i.mnemonic+' '+i.op_str)

expected = {
 0xa005f10a:'addi a4, s0, -0x50', 0xa005f10e:'addi a3, zero, 0x180',
 0xa005f112:'c.li a2, 7', 0xa005f114:'addi a1, s0, -0x40', 0xa005f118:'c.mv a0, s1',
 0xa01974e6:'c.sw a3, 0xc(s0)', 0xa01974e8:'c.sw a4, 0x10(s0)',
 0xa01974ea:'c.sw a5, 0x14(s0)', 0xa01974ec:'addi a4, s0, 0xc',
 0xa01974f0:'c.li a5, 0', 0xa01974f2:'c.li a3, 0', 0xa01974f4:'c.li a2, 7',
 0xa01974f6:'sw a6, 0x18(s0)', 0xa01974fa:'sw a7, 0x1c(s0)',
 0xa01974fe:'sw a4, -0x14(s0)', 0xa0197506:'c.lwsp ra, 0x1c(sp)',
 0xa0197508:'c.lwsp s0, 0x18(sp)', 0xa019750a:'c.addi16sp sp, 0x40',
 0xa019750c:'c.jr ra', 0xa010e338:'c.mv s5, a5', 0xa010e33a:'lbu a5, 0(a1)',
 0xa010e342:'c.beqz a5, 0x42', 0xa010e344:'c.mv s3, a0', 0xa010e348:'c.mv s6, a2',
 0xa010e35c:'andi s8, s6, 4', 0xa010e368:'lw a4, -0x98(s0)',
 0xa010e36c:'lw s2, 4(a4)', 0xa010e374:'lw a5, 0(s2)', 0xa010e37c:'lw a5, 4(s2)',
 0xa010e38a:'addi a5, zero, 0x2f', 0xa010e38e:'lbu a4, 0(a3)',
 0xa010e392:'beq a4, a5, 0xaa', 0xa010e3d6:'bltz a0, 0x6a',
 0xa010e3da:'lw a5, -0x88(s0)', 0xa010e3de:'c.li a4, 5',
 0xa010e3e0:'sw a5, -0x90(s0)', 0xa010e3e4:'lhu a5, 0xe(a5)',
 0xa010e3e8:'c.andi a5, 0xf', 0xa010e3ea:'bne a5, a4, 0x120',
 0xa010e3ee:'c.li a2, 0x18', 0xa010e3f0:'c.li a1, 0', 0xa010e3f2:'c.mv a0, s3',
 0xa010e3f8:'lw a5, -0x90(s0)', 0xa010e3fc:'sw s6, 0(s3)',
 0xa010e400:'sw a5, 0xc(s3)', 0xa010e404:'beqz s5, 0xa',
 0xa010e40e:'lw a0, -0x78(s0)', 0xa010e412:'c.beqz a0, 0xa',
 0xa010e418:'sw zero, -0x78(s0)', 0xa010e41c:'csrw mstatus, s4',
 0xa010e420:'c.li s1, 0', 0xa010e434:'c.mv a0, s1', 0xa010e43a:'c.jr ra',
}
checks = []
for a, text in expected.items():
    assert rows[a]['text'] == text, (hex(a), rows[a], text)
    checks.append('field:'+hex(a))
def raw(a): return int.from_bytes(bytes.fromhex(rows[a]['raw']), 'little')
def sx(x,n): return x-(1<<n) if x>>(n-1) else x
def branch(a):
    w=raw(a)
    return a+sx(((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1),13)
def jal(a):
    w=raw(a)
    return a+sx(((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1),21)
for a,t in [(0xa0197502,0xa010e320),(0xa010e3d2,0xa01a3772),
            (0xa010e3f4,0xa0024906),(0xa010e414,0xa002e14e)]:
    assert jal(a)==t; checks.append('JAL:'+hex(a))
for a,t in [(0xa010e392,0xa010e43c),(0xa010e3d6,0xa010e440),
            (0xa010e3ea,0xa010e50a),(0xa010e404,0xa010e40e)]:
    assert branch(a)==t; checks.append('branch:'+hex(a))
w=raw(0xa010e3fc)
assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,((w>>25)<<5)|((w>>7)&31)) == (35,2,19,22,0)
checks.append('independent-S-format-Q-word0')
assert 7 & 0x40 == 0
checks.append('write-point-mask40')
# An explicit-register-write scan, not a proof of opaque callee behavior.
nonwriters={'sw','sb','sh','c.sw','c.swsp','beq','bne','bltu','bgeu','blt','bge',
            'beqz','bnez','bltz','bgez','blez','bgtz','c.beqz','c.bnez','jal','c.j','csrw'}
for a,r in rows.items():
    if 0xa010e34a <= a < 0xa010e3fc:
        op,_,args=r['text'].partition(' ')
        if op not in nonwriters:
            assert args.split(',')[0] not in ('s3','s6'), r
checks.append('prefix-explicit-s3-s6-continuity')
# a0/a1 reach wrapper's call unchanged; stack restores after call do not set a0.
for a,r in rows.items():
    if 0xa01974de <= a < 0xa0197502:
        op,_,args=r['text'].partition(' ')
        if op not in nonwriters:
            assert args.split(',')[0] not in ('a0','a1'), r
checks.append('wrapper-a0-a1-continuity')
anchors=set(expected)|{0xa0197502,0xa010e3d2,0xa010e3f4,0xa010e414}
OUT.write_text(json.dumps(dict(task='F28', result='PASS', checks=checks,
    profile='Capstone RV32+RVC; independent S/B/J bitfields; static only',
    inherited_sha256='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
    windows=[dict(va=hex(a),bytes=n) for a,n in windows],
    anchors=[rows[a] for a in sorted(anchors)],
    limits=['same-Q s1 identity inherited F15/F16','normal callee-saved register convention',
            'unread name/creation arms','cleanup alias effects unknown','no post-return mode invariant']),
    ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} checks; {len(anchors)} sparse anchors; 348 bytes bounded reads')
