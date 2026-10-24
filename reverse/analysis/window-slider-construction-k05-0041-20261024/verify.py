"""Sparse read-only construction checks; no target/model/input execution."""
import json
import struct
from pathlib import Path

ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
checks=[]
def sx(n,b): return n-(1<<b) if n>>(b-1) else n
def raw(a,h,meaning):
    actual=rom[a-BASE:a-BASE+len(bytes.fromhex(h))].hex()
    assert actual==h,(hex(a),actual,h)
    checks.append(dict(address=f'{a:08x}',raw=h,meaning=meaning))
def jal(a,target):
    w=struct.unpack_from('<I',rom,a-BASE)[0]
    assert w&127==0x6f and (w>>7)&31==1
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    assert a+sx(imm,21)==target
    checks.append(dict(address=f'{a:08x}',raw=w.to_bytes(4,'little').hex(),jal_target=f'{target:08x}'))
def branch(a,r1,r2,f,target):
    w=struct.unpack_from('<I',rom,a-BASE)[0]
    assert (w&127,(w>>15)&31,(w>>20)&31,(w>>12)&7)==(0x63,r1,r2,f)
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    assert a+sx(imm,13)==target
    checks.append(dict(address=f'{a:08x}',branch_target=f'{target:08x}',rs1=r1,rs2=r2,funct3=f))
def cb(a,r1,nz,target):
    w=struct.unpack_from('<H',rom,a-BASE)[0]
    assert w&3==1 and w>>13==(7 if nz else 6) and ((w>>7)&7)+8==r1
    imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
    assert a+sx(imm,9)==target
    checks.append(dict(address=f'{a:08x}',compressed_branch_target=f'{target:08x}',rs1=r1,nonzero=nz))
def loadstore(a,op,f,base,value,offset):
    w=struct.unpack_from('<I',rom,a-BASE)[0]
    imm=w>>20 if op==3 else ((w>>25)<<5)|((w>>7)&31)
    reg=(w>>7)&31 if op==3 else (w>>20)&31
    assert (w&127,(w>>12)&7,(w>>15)&31,reg,sx(imm,12))==(op,f,base,value,offset)
    checks.append(dict(address=f'{a:08x}',memory_field='PASS',opcode=op,funct3=f,base=base,value=value,offset=offset))

for row in [
 (0xa00a8d2a,'0149','request counter s2 initializes0 after global object publication'),
 (0xa00a8d2c,'83aa0b00','reload parent s5 from same global slot each request'),
 (0xa00a8d68,'5685','a0 receives parent s5'),
 (0xa00a8d6e,'aa84','save child return in s1'),
 (0xa00a8d72,'5145','independent wrapper request size20 bytes'),
 (0xa00a8d78,'2a8d','save wrapper return s10'),
 (0xa00a8d7c,'2685','wrapper-zero path passes child s1 to class walker'),
 (0xa00a8d82,'0509a147','increment request counter and compare to8'),
 (0xa00a8dd4,'2685','wrapper-nonzero path configures same child'),
 (0xa00a8ddc,'2685','next flag call receives same child'),
 (0xa00a8de2,'23a8a401','child.word10 stores wrapper s10'),
 (0xa00a8e5e,'5685','query count of parent s5, not child s1 or request counter'),
 (0xa00a8e64,'8547014693050014','compare1; y=0; provisional x=320'),
 (0xa00a8e70,'81452685','count<=1 gives x0, a0=child'),
 (0xa00d91d0,'aa85374526a0130545ef','ordinary child creator ABI parent to a1, base class a0263ef4 to a0'),
 (0xa00d9220,'aa84','save successfully created child before initialization'),
 (0xa00d922a,'2685924441018280','restore same saved child return after initialization'),
]: raw(*row)
for a,t in [(0xa00a8d6a,0xa00d91c6),(0xa00a8d74,0xa008e362),(0xa00a8d7e,0xa00d7806),(0xa00a8dd6,0xa00d9044),(0xa00a8dde,0xa00d9044),(0xa00a8e5a,0xa00d8e96),(0xa00a8e60,0xa00a491c),(0xa00a8e74,0xa00d8d1e),(0xa00d91da,0xa00d76ae),(0xa00d9222,0xa00d9110)]: jal(a,t)
for args in [(0xa00a8d30,21,0,1,0xa00a8d68),(0xa00a8d86,18,15,1,0xa00a8d2c),(0xa00a8e6c,15,10,6,0xa00a8e72)]: branch(*args)
for args in [(0xa00a8d70,10,False,0xa00a8d82),(0xa00a8d7a,10,True,0xa00a8dd0),(0xa00d91de,10,True,0xa00d9220)]: cb(*args)
loadstore(0xa00a8d2c,3,2,23,21,0)
loadstore(0xa00a8de2,0x23,2,9,26,0x10)
old_path=ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-068.json'
old=json.loads(old_path.read_text(encoding='utf-8'))['structuredContent']
asm=old['normalized_result']['assembly']
direct_setter=[line for line in asm if 'jal' in line and '0xa00a4aa0' in line]
assert direct_setter==[]
result=dict(status='PASS-static-only',baseline='1dcbfe6',mapping='VA-0x9ffff000',checks=checks,old_record=dict(path=str(old_path),evidence_id=old['evidence_id'],finding='No direct JAL a00a4aa0 in old dispatcher assembly; does not exclude indirect/callback effects'),inherited=['K03/K04 class/global/index and count return', 'E05/E06 generic parent append and u16 count', 'H03/H04 class walker differs from public removal'],limits=['Eight requests do not prove eight retained/usable children','No count or lifetime invariant inferred from returned helper calls','No target/input/model execution or resource/whole-function export'])
Path(__file__).with_name('evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} sparse checks; old direct-setter query bounded to retained dispatcher')
