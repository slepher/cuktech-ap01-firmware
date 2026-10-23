"""A25 static original-byte extraction and independent encoding assertions; no ROM execution."""
from pathlib import Path
import json,capstone
OUT=Path(__file__).resolve().parent
ROM=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
b=ROM.read_bytes()
def raw(a,n=4):
 o=a-0xa0000000+0x1000
 assert 0<=o<=len(b)-n
 return b[o:o+n]
def w(a,n=4):return int.from_bytes(raw(a,n),'little')
def s(x,n):return x-(1<<n) if x&(1<<(n-1)) else x
C=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[('app init call',0xa005cd36,0xa005cd3c),('global zero and default handler installation',0xa008e3ac,0xa008e4b8),('object zero allocation wrapper',0xa008e362,0xa008e38c),('raw allocate',0xa007fe60,0xa007fe76),('data align',0xa007fe4e,0xa007fe60),('raw free',0xa007ff40,0xa007ff54),('construct',0xa0081d90,0xa0081eba),('size normal cf10 prefix',0xa0081c6a,0xa0081c92),('size common return',0xa0081c98,0xa0081ca2),('size cf10 bypass',0xa0081ca2,0xa0081cb0),('destroy',0xa0081f26,0xa0081ff6),('allocation adapters',0xa008ae8c,0xa008aec0),('free adapter',0xa008ab8a,0xa008abb0),('zero adapter',0xa0080d8e,0xa0080da6),('PNG explicit output construction',0xa0192ac6,0xa0192af6)]
rows=[]
for name,a,z in windows:
 while a<z:
  n=4 if w(a,2)&3==3 else 2
  ins=next(C.disasm(raw(a,n),a),None)
  assert ins and a+n<=z,(hex(a),raw(a,n).hex())
  rows.append(dict(region=name,va=hex(a),offset=hex(a-0xa0000000+0x1000),raw=raw(a,n).hex(),asm=(ins.mnemonic+' '+ins.op_str).strip()))
  a+=n
idx={int(r['va'],16):r for r in rows};checks=[]
def check(a,label,actual,want):
 assert actual==want,(hex(a),label,actual,want)
 checks.append(dict(va=hex(a),claim=label,actual=actual,expected=want))
def asm(a,v):check(a,'decoded original instruction',idx[a]['asm'],v)
def mem(a,v):
 x=w(a);op=x&127;imm=((x>>25)<<5)|((x>>7)&31) if op==35 else x>>20
 reg=(x>>20)&31 if op==35 else (x>>7)&31
 check(a,'memory opcode width register base signed offset',[op,(x>>12)&7,reg,(x>>15)&31,s(imm,12)],v)
def call(a,t):
 x=w(a)
 if x&127==111:
  q=((x>>31)<<20)|(((x>>12)&255)<<12)|(((x>>20)&1)<<11)|(((x>>21)&1023)<<1);v=a+s(q,21)
 else:
  y=w(a+4);check(a,'AUIPC JALR call registers',[x&127,(x>>7)&31,y&127,(y>>7)&31,(y>>15)&31],[23,1,103,1,1]);v=(a+(x&0xfffff000)+s(y>>20,12))&0xfffffffe
 check(a,'direct target',v,t)
for a,v in [
 (0xa008e3c4,'lui s2, 0x62fc9'),(0xa008e3c8,'addi a1, zero, 0x210'),(0xa008e3cc,'addi a0, s2, 0x57c'),(0xa008e3d4,'addi s1, s2, 0x57c'),(0xa008e43c,'addi s3, s1, 0x80'),(0xa008e440,'addi s4, s4, -0xc0'),(0xa008e444,'addi s7, s7, -0x1a0'),(0xa008e448,'addi s6, s6, -0x1b2'),(0xa008e44c,'addi s5, s5, 0x30'),
 (0xa008e40c,'addi a0, a0, 0x644'),(0xa008e45a,'addi a0, a0, 0x65c'),(0xa008e480,'addi a0, a0, 0x674'),
 (0xa007fe68,'c.addi a0, 3'),(0xa007fe54,'c.beqz a0, 6'),(0xa007fe56,'c.addi a0, 3'),(0xa007fe58,'c.andi a0, -4'),
 (0xa0081daa,'c.li a0, 0x1c'),(0xa0081e16,'lw a5, 0(s5)'),(0xa0081e6c,'c.mv a1, s2'),(0xa0081e6e,'c.jalr a5'),(0xa0081e70,'c.mv s8, a0'),(0xa0081e72,'c.beqz a0, -0x54'),(0xa0081e7a,'c.lui a4, 0x10'),(0xa0081e7c,'addi a4, a4, -0x100'),(0xa0081e82,'lui a4, 0x300'),(0xa0081e86,'c.addi a4, 0x19'),(0xa0081e90,'lui a5, 0x62fc9'),(0xa0081ea2,'c.beqz a4, 8'),(0xa0081ea4,'c.mv a1, s2'),(0xa0081ea6,'c.jalr a4'),(0xa0081eaa,'c.sw a5, 0x10(s1)'),
 (0xa0081f78,'c.andi a5, 0x10'),(0xa0081fba,'c.lw a5, 4(a5)'),(0xa0081fbc,'c.beqz a5, 6'),(0xa0081fbe,'c.lw a0, 0x14(a0)'),(0xa0081fc0,'c.jalr a5'),(0xa0081fc2,'c.mv a0, s1'),
 (0xa0081c76,'c.bnez a3, 0x12'),(0xa0081c8a,'mul a0, a3, s1'),
 (0xa0192ad4,'slli a4, a1, 2'),(0xa0192ad8,'c.li a3, 0x10'),(0xa0192ada,'addi a0, a0, 0x674'),(0xa0192aee,'c.sw a0, 0(a5)'),(0xa0192af0,'c.lw a5, 0xc(a0)'),
 (0xa008aeaa,'jal -0x1e'),(0xa008aeba,'addi a0, a0, 0x5e0'),(0xa0080d96,'c.mv a2, a1'),(0xa0080d98,'c.li a1, 0')]:asm(a,v)
for a,v in [(0xa008e45e,[35,2,23,19,0x48]),(0xa008e454,[35,2,20,19,0x4c]),(0xa008e462,[35,2,22,19,0x50]),(0xa008e46e,[35,2,21,19,0x5c]),(0xa008e484,[35,2,23,19,0x60]),(0xa008e47a,[35,2,20,19,0x64]),(0xa008e488,[35,2,22,19,0x68]),(0xa008e494,[35,2,21,19,0x74]),(0xa008e4a0,[35,2,23,19,0x78]),(0xa008e49c,[35,2,20,19,0x7c]),(0xa008e4b0,[35,2,22,9,0x100]),(0xa008e4b4,[35,2,21,9,0x10c]),(0xa0081e9c,[3,2,14,15,0x64c]),(0xa0081e74,[35,0,18,9,1]),(0xa0081e8c,[35,1,20,9,4]),(0xa0081e94,[35,1,23,9,6]),(0xa0081e98,[35,1,19,9,8]),(0xa0081eac,[35,2,24,9,0x14]),(0xa0081eb0,[35,2,22,9,0xc]),(0xa0081eb4,[35,2,21,9,0x18]),(0xa0081f72,[3,5,15,10,2])]:mem(a,v)
for a,t in [(0xa005cd36,0xa008e3ac),(0xa008e3d0,0xa0080d8e),(0xa008e42c,0xa0080d8e),(0xa008e472,0xa0080d8e),(0xa008e498,0xa0080d8e),(0xa007fe6a,0xa008aea0),(0xa007ff48,0xa008ab8a),(0xa0081db4,0xa008e362),(0xa008e370,0xa002fcc8),(0xa008e37c,0xa0080d8e),(0xa0081e12,0xa0081c6a),(0xa0081e4c,0xa008ab8a),(0xa0081fc4,0xa008ab8a),(0xa008ae94,0xa002fcc8),(0xa008aba2,0xa002e14e),(0xa0080d9a,0xa0024906),(0xa0192ade,0xa0081d90)]:call(a,t)
# Derive addresses from original U/I/S values, not nominal LVGL types.
G=0x62fc957c;S3=G+0x80
install=[]
for slot,va in [(0x644,0xa008e45e),(0x648,0xa008e454),(0x64c,0xa008e462),(0x65c,0xa008e484),(0x660,0xa008e47a),(0x664,0xa008e488),(0x674,0xa008e4a0),(0x678,0xa008e49c),(0x67c,0xa008e4b0)]:
 x=w(va);off=s(((x>>25)<<5)|((x>>7)&31),12);base=G if (x>>15)&31==9 else S3;dest=base+off
 check(va,'derived absolute installation destination',dest,0x62fc9000+slot)
 install.append(dict(va=hex(va),destination=hex(dest),source_register=(x>>20)&31))
summary=dict(result='passed',static_only=True,windows=len(windows),bytes=sum(z-a for _,a,z in windows),instructions=len(rows),checks=len(checks),unknown_instructions=0,core_scope='initializer slice, raw alloc/align/free, construct, cf10 size slice, destroy, alloc adapters, free adapter, real PNG output slice; short zero dependency')
(OUT/'evidence.json').write_text(json.dumps(dict(rom=str(ROM),mapping='offset = VA - a0000000 + 1000',instructions=rows,checks=checks,installation=install,limitations=['No target execution, emulation, replay, device, network or shared REA target.','No exhaustive assertion of all dynamic writers; default init and one explicit PNG path only.','No library source-version certification or full heap/cache/PNG decompression recovery.']),indent=2),encoding='utf8')
(OUT/'instructions.txt').write_text('\n'.join(f"{r['va']} {r['raw']:8} {r['asm']} [{r['region']}]" for r in rows)+'\n',encoding='utf8')
(OUT/'validation.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(summary))
