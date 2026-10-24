"""Read-only sparse ROM field checks; never executes firmware or an input model."""
import json
import struct
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
data = ROM.read_bytes()
checks = []

def raw(address, expected, meaning):
    actual = data[address - BASE:address - BASE + len(bytes.fromhex(expected))]
    assert actual.hex() == expected, (hex(address), actual.hex(), expected)
    checks.append(dict(address=f'{address:08x}', raw=expected, meaning=meaning))

def sign(value, bits):
    return value - (1 << bits) if value >> (bits - 1) else value

def jal(address, expected):
    w = struct.unpack_from('<I', data, address-BASE)[0]
    assert w & 0x7f == 0x6f and (w >> 7) & 31 == 1
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    assert address + sign(imm, 21) == expected
    checks.append(dict(address=f'{address:08x}', raw=w.to_bytes(4,'little').hex(), jal_target=f'{expected:08x}'))

def branch(address, rs1, rs2, funct3, expected):
    w = struct.unpack_from('<I', data, address-BASE)[0]
    assert (w & 127, (w>>15)&31, (w>>20)&31, (w>>12)&7) == (0x63,rs1,rs2,funct3)
    imm = ((w >> 31) << 12) | (((w >> 7)&1) << 11) | (((w >> 25)&63) << 5) | (((w >> 8)&15) << 1)
    assert address + sign(imm,13) == expected
    checks.append(dict(address=f'{address:08x}', raw=w.to_bytes(4,'little').hex(), branch_target=f'{expected:08x}', rs1=rs1,rs2=rs2,funct3=funct3))

def cj(address, expected):
    w = struct.unpack_from('<H',data,address-BASE)[0]
    assert w & 3 == 1 and w >> 13 == 5
    imm = (((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
    assert address+sign(imm,12)==expected
    checks.append(dict(address=f'{address:08x}',raw=w.to_bytes(2,'little').hex(),compressed_jump_target=f'{expected:08x}'))

def cb(address, rs1, nonzero, expected):
    w=struct.unpack_from('<H',data,address-BASE)[0]
    assert w&3==1 and w>>13==(7 if nonzero else 6) and ((w>>7)&7)+8==rs1
    imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
    assert address+sign(imm,9)==expected
    checks.append(dict(address=f'{address:08x}',compressed_branch_target=f'{expected:08x}',rs1=rs1,nonzero=nonzero))

def memory(address, opcode, funct3, base_reg, value_reg, offset):
    w=struct.unpack_from('<I',data,address-BASE)[0]
    imm=(w>>20) if opcode==3 else (((w>>25)<<5)|((w>>7)&31))
    reg=((w>>7)&31) if opcode==3 else ((w>>20)&31)
    assert (w&127,(w>>12)&7,(w>>15)&31,reg,sign(imm,12))==(opcode,funct3,base_reg,value_reg,offset)
    checks.append(dict(address=f'{address:08x}',memory_field_check='PASS',opcode=opcode,funct3=funct3,base_reg=base_reg,value_reg=value_reg,offset=offset))

anchors = [
 (0xa00d81f8,'15e9','nonzero class skips current-target class discovery to base load at822c'),
 (0xa00d81fa,'9c418843','zero class uses event.current_target then object.class'),
 (0xa00d81fe,'0dc9','null class returns1 at8230'),
 (0xa00d8200,'5c458dc7','read class+c; empty callback follows base at822c'),
 (0xa00d820e,'23a60500','clear event.user_data word+c'),
 (0xa00d8212,'5c45','reload class+c callback'),
 (0xa00d8214,'ae848297','save event and indirect class_event(class,event)'),
 (0xa00d8218,'03c58401','reload event flags byte+18, overwriting callback a0'),
 (0xa00d8220,'1345f5ff','invert flags'),
 (0xa00d8226,'0589','return inverted flags bit0'),
 (0xa00d822c,'0841c1bf','load class.base and loop to81fe'),
 (0xa00d8230,'05458280','no ancestor callback yields1'),
 (0xa00a4cb8,'372537a01305c55c','construct class constant a03725cc'),
 (0xa00a4cc0,'2e89','event is incoming a1, class callback ABI'),
 (0xa00a4cc6,'8547','exact success comparison constant1'),
 (0xa00a4ccc,'83278900','event.code word+8'),
 (0xa00a4cd0,'61777d17f98f','mask constructed as ffff8000-1 and AND'),
 (0xa00a4cd6,'13071003','event comparison constant31h'),
 (0xa00a4cfe,'4547','event comparison constant11h'),
 (0xa00a4cda,'83240900','object is current_target word+0'),
 (0xa00a4ce8,'aa8501462685','current index to a1; direction0; object to a0'),
 (0xa00a4d0a,'cd47','key constant decimal19'),
 (0xa00a4d1a,'9305f5ff0946','index-1 and direction2'),
 (0xa00a4d2a,'d147','key constant decimal20'),
 (0xa00a4d36,'93051500','index+1 word arithmetic'),
 (0xa00a4d44,'8325c4fe','reload candidate after count call'),
 (0xa00a4d4c,'81450546','failed unsigned comparison: index0 direction1'),
 (0xa00a4d52,'a947','key constant decimal10'),
 (0xa00a4d58,'9c5c81c7','read object+38; zero goes4d62'),
 (0xa00a4d5c,'01468145','nonzero index requests index0 direction0'),
 (0xa00a4d62,'2685','delete receives same current_target object'),
 (0xa00a4d68,'b7b7fc6223a8076a','after delete clear word62fcb6b0'),
 (0xa00a4c40,'23ac040223ae0402','class constructor initializes +38/+3c to zero'),
 (0xa00a8b90,'b7bbfc6283a70b6b','old dispatcher reads same global'),
 (0xa00a8b9c,'938b0b6b','s7 becomes62fcb6b0'),
 (0xa00a8cbc,'372537a01305c55c','creator passes same class'),
 (0xa00a8cc8,'2a89','save creator return as s2'),
 (0xa00a8d1e,'23289902','store group handle in object+30'),
 (0xa00a8d22,'23a02b01','store created object s2 into global through s7'),
 (0xa00a8d2c,'83aa0b00','subsequent child construction rereads global object'),
 (0xa00d76c0,'aa89','generic factory saves incoming class in s3'),
 (0xa00d76de,'aa84','save allocated object'),
 (0xa00d76e0,'31c1','allocation zero bypasses stores'),
 (0xa00d76e2,'23203501','factory stores class s3 into object.word0'),
 (0xa00dd190,'1c45014599c303d507038280','extra pointer; absent=>0 otherwise LHU extra+30 count'),
 (0xa00a495e,'b240224441018280','count wrapper epilogue does not replace a0'),
 (0xa00a4af4,'29cd9c5c638b4705','setter gates count!=0 and old index!=requested; no range comparison here'),
]
for a,b,m in anchors:
    raw(a,b,m)
for a,t in [(0xa00a4cc2,0xa00d81f8),(0xa00a4ce4,0xa00a4116),(0xa00a4cee,0xa00a4aa0),(0xa00a4d06,0xa00d8af6),(0xa00a4d12,0xa00a4116),(0xa00a4d24,0xa00a491c),(0xa00a4d32,0xa00a4116),(0xa00a4d40,0xa00a491c),(0xa00a4d64,0xa00ded6c),(0xa00a8cc4,0xa00d76ae),(0xa00a8cca,0xa00d9110),(0xa00a495a,0xa00dd144),(0xa00a4af0,0xa00a491c)]:
    jal(a,t)
for a,r1,r2,f,t in [(0xa00a4cc8,10,15,1,0xa00a4cf2),(0xa00a4cde,15,14,1,0xa00a4cfe),(0xa00a4d00,15,14,1,0xa00a4cf2),(0xa00a4d16,0,10,5,0xa00a4d22),(0xa00a4d48,11,10,6,0xa00a4d4e),(0xa00a4d54,10,15,1,0xa00a4cf2),(0xa00a8ba0,15,0,0,0xa00a91a8)]:
    branch(a,r1,r2,f,t)
for a,t in [(0xa00d822e,0xa00d81fe),(0xa00a4d20,0xa00a4cec),(0xa00a4d28,0xa00a4d1a),(0xa00a4d50,0xa00a4cec),(0xa00a4d60,0xa00a4cec),(0xa00a4d70,0xa00a4cf2)]:
    cj(a,t)
for args in [(0xa00d81f8,10,True,0xa00d822c),(0xa00d81fe,10,False,0xa00d8230),(0xa00d8202,15,False,0xa00d822c),(0xa00a4d5a,15,False,0xa00a4d62),(0xa00a4af4,10,False,0xa00a4b4e),(0xa00d76e0,10,False,0xa00d7724)]:
    cb(*args)
for args in [(0xa00d820e,0x23,2,11,0,12),(0xa00d8218,3,4,9,10,24),(0xa00a4ccc,3,2,18,15,8),(0xa00a4cda,3,2,18,9,0),(0xa00a4d6c,0x23,2,15,0,0x6b0),(0xa00d76e2,0x23,2,10,19,0),(0xa00a8d22,0x23,2,23,18,0),(0xa00dd196,3,5,15,10,0x30)]:
    memory(*args)
table = struct.unpack_from('<4I',data,0xa03725cc-BASE)
assert table == (0xa0263ef4,0xa00a4bdc,0xa00a4c54,0xa00a4cac)
assert ((0xffff8 << 12) - 1) & 0xffffffff == 0xffff7fff
result = dict(status='PASS-static-only',baseline='565dc6e',mapping='VA-0x9ffff000',checks=checks,class_table=dict(address='a03725cc',base=f'{table[0]:08x}',constructor=f'{table[1]:08x}',destructor=f'{table[2]:08x}',event_callback=f'{table[3]:08x}'),inherited=['K01 sparse entry', 'H03/H04 event/key/delete/dispatch contracts', 'old whole-rom private036/043/047 callee bodies', 'old private068 creator seed'],limitations=['Author static checks; independent acceptance still required','No execution of firmware/model/classification or unusual inputs','No proof of runtime installation success or global exclusivity/count invariants','No entire-function/body/resource/source exports'])
Path(__file__).with_name('evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS: {len(checks)} sparse checks; 4 class words; independent JAL/branch fields')
