"""L03: static ROM fields and retained-evidence checks; no target execution."""
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
TREE = OUT.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
sys.path.insert(0, str(TREE / 'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr

checks = []
anchors = []

def raw(pc, expected, meaning):
    b = bytes.fromhex(expected)
    assert rr.rom[pc-rr.BASE:pc-rr.BASE+len(b)] == b, hex(pc)
    anchors.append(dict(pc=hex(pc), raw=expected, meaning=meaning))
    checks.append(meaning)

def sx(v, n):
    return v - (1 << n) if v & (1 << (n-1)) else v

def word(pc):
    return int.from_bytes(rr.rom[pc-rr.BASE:pc-rr.BASE+4], 'little')

def jal(pc, target):
    w = word(pc)
    im = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    assert (w & 127, (w >> 7) & 31) == (0x6f, 1)
    assert pc + sx(im, 21) == target
    anchors.append(dict(pc=hex(pc), raw=w.to_bytes(4, 'little').hex(), call=hex(target)))
    checks.append(f'{pc:x} JAL ra {target:x}')

def btarget(pc, f3, rs1, rs2, target):
    w = word(pc)
    im = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    assert (w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31) == (0x63, f3, rs1, rs2)
    assert pc + sx(im, 13) == target
    checks.append(f'{pc:x} branch fields and target {target:x}')

for pc, h, meaning in [
    (0xa00fd1d0, '374afc62', 'caller s4 high base 62fc4000'),
    (0xa00fd1e8, '130aca02', 'caller s4 base 62fc402c'),
    (0xa00feac4, '03451a00', 'LBU a0,1(s4): unsigned input byte 62fc402d'),
    (0xa00feacc, '832784fa81458847', 'first caller overwrites a0 from local58+8 and sets a1=0'),
    (0xa00feadc, '0d45', 'second caller a0=3'),
    (0xa00feae2, '832784fa85458847', 'second caller overwrites a0 from local58+8 and sets a1=1'),
    (0xa00ab478, 'b797fc6293878709', 'setter base G=62fc9098'),
    (0xa00ab480, '03c72700', 'LBU old byte G+2'),
    (0xa00ab490, '2381a700', 'SB incoming a0 to G+2 before callbacks'),
    (0xa00ab494, '0d45', 'notification reason a0=3'),
    (0xa00ab49e, 'b2402244410182808280', 'both setter exits return without success-value assignment'),
    (0xa00a5bcc, 'b7b7fc62', 'notification list high base'),
    (0xa00a5bd2, '1387c74e4443aa891389c74e379afc62', 'list base62fcb4ec; first node+4; save reason; G high base'),
    (0xa00a5bf4, '9c4091c7c8404e8693058a098297', 'optional node callback(node.word4,G,reason) before advancing'),
    (0xa00a5c02, '83270900be94c440e1bf', 're-read list link offset then node.next and loop'),
    (0xa00ab27e, 'b7a526a037a526a0938585211305c521', 'writer a0=path at a026a21c; a1=mode at a026a218'),
    (0xa00ab292, '1de5', 'writer open-result nonzero branch'),
    (0xa00ab2b6, 'b2402244924441018280', 'writer shared epilogue; no explicit success result'),
    (0xa00ab2c0, 'aa84', 'save nonzero handle in s1'),
    (0xa00ab2c6, 'b797fc6213878709', 'writer G=62fc9098'),
    (0xa00ab2ce, '2313a700', 'SH low16 helper result to G+6'),
    (0xa00ab2d2, 'a6860546a14513858709', 'write service (G,8,1,handle)'),
    (0xa00ab2e0, '2685', 'overwrite write result with handle for close service'),
    (0xa00ab2e6, 'c1bf', 'unconditional jump to common writer epilogue'),
]: raw(pc, h, meaning)

for pc, target in [
    (0xa00feac8,0xa00ab478),(0xa00feade,0xa00ab478),
    (0xa00fead4,0xa018f232),(0xa00feaea,0xa018f232),
    (0xa00ab496,0xa00a5bbe),(0xa00ab49a,0xa00ab274),
    (0xa00ab28e,0xa0134856),(0xa00ab2b2,0xa008b51a),
    (0xa00ab2c2,0xa00a46e8),(0xa00ab2dc,0xa0134adc),(0xa00ab2e2,0xa01a8de6),
]: jal(pc,target)
btarget(0xa00ab484,0,14,10,0xa00ab4a6)

# Decode compressed branch bit fields independently of printed disassembly.
def cb(pc, f3, register, target):
    w = int.from_bytes(rr.rom[pc-rr.BASE:pc-rr.BASE+2], 'little')
    im = (((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
    assert (w&3,w>>13,8+((w>>7)&7)) == (1,f3,register)
    assert pc+sx(im,9)==target
    checks.append(f'{pc:x} compressed branch {target:x}')
cb(0xa00ab292,7,10,0xa00ab2c0)
cb(0xa00a5be2,7,9,0xa00a5bf4)
cb(0xa00a5bf6,6,15,0xa00a5c02)

strings = {}
for pc, expected in [(0xa026a218,'wb'),(0xa026a21c,'/data/sysconfig.bin'),(0xa026a51c,'SysSettingsWrite')]:
    actual = rr.rom[pc-rr.BASE:pc-rr.BASE+64].split(b'\0')[0].decode('ascii')
    assert actual == expected
    strings[hex(pc)] = actual
    checks.append('literal '+actual)

writer_path = MAIN/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-071.json'
writer = json.loads(writer_path.read_text(encoding='utf8'))['structuredContent']
assert writer['parameters']['procedure']=='0xa00ab274'
old = writer['normalized_result']['assembly']
assert '0xa00ab2dc: jal ra, 0xa0134adc' in old
caller = json.loads((MAIN/'reverse/rehost/settings-0041-round2b.json').read_text(encoding='utf8'))['records'][10]
parent = json.loads((MAIN/'reverse/rehost/system-complete-0041.json').read_text(encoding='utf8'))['cached_evidence']['settings_a00fd1ac']
assert 'a00ab478' in parent
checks.append('old writer/caller/parent exact identity retained')

result = dict(status='PASS', baseline='565dc6e', checks=checks, anchors=anchors, strings=strings,
    inherited=dict(writer_evidence=writer['evidence_id'], writer_file=str(writer_path),
      caller_evidence=caller['evidence_id'], caller='settings-0041-round2b.json#/records/10',
      parent='system-complete-0041.json#/cached_evidence/settings_a00fd1ac'),
    limits=['Static only; no target/input execution', 'No subscriber registration/lifetime or file-service internals',
      'Writer service results ignored here; no durable-success or rollback claim',
      'No checksum algorithm named from a00a46e8 result', 'No firmware/SIM/build/replay/device/network/model changes'])
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS', checks=len(checks), sparse_anchors=len(anchors), new_full_function_exports=0)))
