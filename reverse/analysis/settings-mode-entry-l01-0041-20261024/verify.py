"""L01 fixed caller/helper checks; no target, NVS, network or GUI execution."""
from pathlib import Path
import json,sys
OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
sys.dont_write_bytecode=True
sys.path.insert(0,str(TREE/'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr
windows=[(0xa00feac4,0xa00feaf2),(0xa00ab478,0xa00ab4a8),(0xa00a5bf4,0xa00a5c02)]
rows=[r for a,z in windows for r in rr.rows(a,z)]
D={int(r['pc'],16):r for r in rows}
checks=[]
for pc,asm in {0xa00feac4:'lbu a0, 1(s4)',0xa00feacc:'lw a5, -0x58(s0)',
 0xa00fead0:'c.li a1, 0',0xa00fead2:'c.lw a0, 8(a5)',0xa00feadc:'c.li a0, 3',
 0xa00feae2:'lw a5, -0x58(s0)',0xa00feae6:'c.li a1, 1',0xa00feae8:'c.lw a0, 8(a5)',
 0xa00ab478:'lui a5, 0x62fc9',0xa00ab47c:'addi a5, a5, 0x98',
 0xa00ab480:'lbu a4, 2(a5)',0xa00ab490:'sb a0, 2(a5)',0xa00ab494:'c.li a0, 3',
 0xa00a5bf4:'c.lw a5, 0(s1)',0xa00a5bf8:'c.lw a0, 4(s1)',
 0xa00a5bfa:'c.mv a2, s3',0xa00a5bfc:'addi a1, s4, 0x98',0xa00a5c00:'c.jalr a5'}.items():
 assert D[pc]['asm']==asm,(hex(pc),D[pc])
 checks.append(dict(pc=hex(pc),asm=asm))
def word(a):return int.from_bytes(rr.rom[a-rr.BASE:a-rr.BASE+4],'little')
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def jal(a,target):
 w=word(a);imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 assert (w&127,(w>>7)&31)==(0x6f,1) and a+sx(imm,21)==target
 checks.append(dict(pc=hex(a),target=hex(target)))
for pc,t in [(0xa00feac8,0xa00ab478),(0xa00feade,0xa00ab478),
 (0xa00fead4,0xa018f232),(0xa00feaea,0xa018f232),
 (0xa00ab496,0xa00a5bbe),(0xa00ab49a,0xa00ab274),
 (0xa00ab28e,0xa0134856),(0xa00ab2c2,0xa00a46e8),
 (0xa00ab2dc,0xa0134adc),(0xa00ab2e2,0xa01a8de6)]:jal(pc,t)
w=word(0xa00ab484);imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31)==(99,0,14,10)
assert 0xa00ab484+sx(imm,13)==0xa00ab4a6
checks.append(dict(pc='0xa00ab484',semantics='unsigned-byte old value compared to full a0; equal returns before store/calls'))
for pc,funct3,rs2,rs1,imm in [(0xa00ab480,4,0,15,2),(0xa00ab490,0,10,15,2),(0xa00ab2ce,1,10,14,6)]:
 w=word(pc)
 if pc==0xa00ab480:assert (w&127,(w>>12)&7,(w>>15)&31,w>>20)==(3,funct3,rs1,imm)
 else:assert (w&127,(w>>12)&7,(w>>20)&31,(w>>15)&31,((w>>25)<<5)|((w>>7)&31))==(35,funct3,rs2,rs1,imm)
 checks.append(dict(pc=hex(pc),width='LBU' if pc==0xa00ab480 else ('SH' if funct3==1 else 'SB')))
# Existing caller base and the service ABI need isolated anchors only.
sparse={0xa00fd1d0:'375afc62',0xa00fd1e8:'130aca02'}
for pc,h in sparse.items():assert rr.rom[pc-rr.BASE:pc-rr.BASE+len(bytes.fromhex(h))].hex()==h
service=list(rr.rows(0xa00ab2c0,0xa00ab2e6))
S={int(r['pc'],16):r for r in service}
for pc,asm in {0xa00ab2ce:'sh a0, 6(a4)',0xa00ab2d2:'c.mv a3, s1',0xa00ab2d4:'c.li a2, 1',0xa00ab2d6:'c.li a1, 8',0xa00ab2d8:'addi a0, a5, 0x98',0xa00ab2e0:'c.mv a0, s1'}.items():
 assert S[pc]['asm']==asm;checks.append(dict(pc=hex(pc),asm=asm))
strings={hex(a):rr.rom[a-rr.BASE:a-rr.BASE+64].split(b'\0')[0].decode('ascii') for a in [0xa026a218,0xa026a21c,0xa026a51c]}
assert list(strings.values())==['wb','/data/sysconfig.bin','SysSettingsWrite']
ret=json.loads((MAIN/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-071.json').read_text(encoding='utf8'))['structuredContent']
assert ret['parameters']['procedure']=='0xa00ab274'
result=dict(status='PASS',baseline='75f977a',checks=checks,rows=rows,
            sparse_base_anchors={hex(k):v for k,v in sparse.items()},writer_service_anchors=[S[p] for p in [0xa00ab2ce,0xa00ab2d2,0xa00ab2d4,0xa00ab2d6,0xa00ab2d8,0xa00ab2dc,0xa00ab2e0,0xa00ab2e2]],
            strings=strings,existing_writer_evidence=ret['evidence_id'],
            source_refs=['settings-0041-round2b.json#/records/10','system-complete-0041.json#/cached_evidence/settings_a00fd1ac'],
            limits=['Only two normal callers and local helper/service interface','No filesystem/allocator/transport internals or durable-success claim',
                    'a00a46e8 return stored low16; no checksum algorithm named','No actual settings instance or subscriber lifetime observed'])
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),caller_helper_windows=3,existing_writer_dossier=True)))
