"""D16: static byte/ABI review only; never executes target or instruction model."""
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
def raw(a, n):
    return rom[a-BASE:a-BASE+n]

old = json.loads((TREE/'reverse/analysis/buzzer-backlight-round2-20261023/capstone-windows.json').read_text())['windows'][0]
assert raw(int(old['start'], 16), len(bytes.fromhex(old['hex']))) == bytes.fromhex(old['hex'])
d15 = json.loads((TREE/'reverse/analysis/pwm-arithmetic-d15-0041-20261024/review-result.json').read_text())
count = 0
for window in d15['sparse_windows']:
    for i in window['instructions']:
        expected = bytes.fromhex(i['hex'])
        assert raw(int(i['address'],16),len(expected)) == expected
        count += 1
assert struct.unpack('<d', raw(0xa061b5a8,8))[0] == 80000000.0

calls = []
for pc, target in [(0xa0136822,0xa001fa84),(0xa0136832,0xa001d7fc),(0xa013683a,0xa001f042)]:
    auipc,jalr = struct.unpack('<II',raw(pc,8))
    signed = lambda v,n: v-(1<<n) if v & (1<<(n-1)) else v
    assert auipc & 0x7f == 0x17 and (auipc>>7)&31 == 1
    assert jalr & 0x707f == 0x67 and (jalr>>7)&31 == 1 and (jalr>>15)&31 == 1
    actual = (pc+signed(auipc&0xfffff000,32)+signed(jalr>>20,12)) & 0xfffffffe
    assert actual == target
    calls.append({'pc':hex(pc),'target':hex(actual)})

vendor=[]
for a, fields in [(0xa01367e4,(0xb,1,16,13,11,6)),(0xa01368ec,(0xb,1,16,13,11,6)),
                  (0xa01367fa,(0x77,1,7,15,11,15)),(0xa0136900,(0x77,1,7,15,11,15))]:
    w=int.from_bytes(raw(a,4),'little')
    got=(w&127,(w>>12)&7,w>>25,(w>>7)&31,(w>>15)&31,(w>>20)&31)
    assert got==fields
    vendor.append({'address':hex(a),'hex':raw(a,4).hex(),'opcode_f3_f7_rd_rs1_rs2':got})

# Minimal added return-ABI anchor: a1:a0 is not overwritten by the epilogue.
epilogue='99c073a01400b250225492540259f249624ad24a424bb24b224c924c45618280'
assert raw(0xa001dcc4,len(bytes.fromhex(epilogue))).hex()==epilogue
anchors=[]
for a,h,label in [
 (0xa01367b0,'1cc9','conditional frequency cache store'),
 (0xa01367b6,'d8c3','first duty32 cache store'),
 (0xa01367bc,'d8c7','second duty32 cache store'),
 (0xa01367be,'83aa0401','frequency cache reload'),
 (0xa01367ee,'c582','logical shift17 after MULA'),
 (0xa0136844,'63688501','unsigned period comparison'),
 (0xa013685c,'23964401','period16 cache before MMIO'),
 (0xa013687a,'2320f904','stop request RMW store'),
 (0xa01368bc,'2320f904','config0 divider store'),
 (0xa01368cc,'23244905','period register store'),
 (0xa01368f4,'c582','second logical shift17'),
 (0xa0136918,'8bc7e780','channel reload before enable update'),
 (0xa0136926,'fcc2','enable RMW store'),
 (0xa013694c,'b8c3','common stop-bit clear store')]:
    assert raw(a,len(bytes.fromhex(h))).hex()==h
    anchors.append({'address':hex(a),'hex':h,'meaning':label})
out={'method':'read-only byte and register-field checks; no target/model execution',
     'inherited_window_equal':True,'d15_sparse_instructions_equal':count,
     'constant_binary64':80000000.0,'calls':calls,'vendor_fields':vendor,
     'anchors':anchors,'division_return_epilogue':{'start':'0xa001dcc4','end_exclusive':'0xa001dce4','hex':epilogue},
     'new_functionality':0,
     'limits':['No hardware ISA certification or waveform observation.',
               'No source/library version certification.',
               'Byte equality is not a proof of every binary64 division rounding case.']}
(HERE/'review-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: inherited bytes, D15 sparse bytes, constant, call ABI fields, MULA/PKBB16 fields, cache/MMIO anchors, return epilogue')
