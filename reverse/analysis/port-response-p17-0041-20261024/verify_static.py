"""P-17 bounded offline ROM/retained comparison; never executes target code."""
import json
from datetime import datetime, timezone
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
def read_json(rel):
    return json.loads((ROOT/rel).read_text(encoding='utf-8'))
buzz_path = 'reverse/analysis/buzzer-backlight-0041-20261023.json'
uart_path = 'reverse/analysis/uart-response-0041-20261023.json'
n01_path = 'reverse/analysis/mode-interface-n01-0041-20261024/instruction-evidence.json'
buzz = read_json(buzz_path)['functions'][5]
uart = read_json(uart_path)['functions'][0]
helper = next(w for w in read_json(n01_path)['windows'] if w['start']=='0xa01ad024')
assert buzz['address']=='0xa00a8582'
assert buzz['evidence_id']==uart['evidence_id']
assert buzz['profile']['digest']==uart['profile_digest']=='bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279'
assert buzz['profile']['parameters']['language_id']=='RISCV:LE:32:ap01thead3'
retained = {int(x.split(':')[0],16):x.split(': ',1)[1] for x in buzz['assembly']}
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
ranges = [('entry',0xa00a85a0,0xa00a85c0),('return',0xa00a85e4,0xa00a8602),
          ('route_gt57',0xa00a873e,0xa00a874e),('route_61_to68',0xa00a8794,0xa00a87a8),
          ('shared_ack_and_return',0xa00a9cbc,0xa00a9cda),('ack_copy',0xa01ad024,0xa01ad04a),
          ('event24',0xa00a8856,0xa00a8870)]
def raw_slice(record, start, end):
    r = next(r for r in record['raw_ranges'] if int(r['start'],16)<=start and end<=int(r['start'],16)+len(bytes.fromhex(r['hex'])))
    return bytes.fromhex(r['hex'])[start-int(r['start'],16):end-int(r['start'],16)]
windows=[]
for name,start,end in ranges:
    raw=rom[start-BASE:end-BASE]
    ins=list(md.disasm(raw,start))
    assert sum(x.size for x in ins)==end-start
    cursor=start
    rows=[]
    for x in ins:
        assert x.address==cursor
        assert x.size==(4 if int.from_bytes(x.bytes[:2],'little')&3==3 else 2)
        cursor+=x.size
        if name!='ack_copy':
            assert x.address in retained
        rows.append({'address':hex(x.address),'hex':x.bytes.hex(),'decode':x.mnemonic+' '+x.op_str,
                     'retained':retained.get(x.address) if name!='ack_copy' else None})
    if name=='ack_copy':
        assert raw==b''.join(bytes.fromhex(x['hex']) for x in helper['instructions'])
    else:
        assert raw==raw_slice(buzz,start,end)==raw_slice(uart,start,end)
    windows.append({'name':name,'start':hex(start),'end_exclusive':hex(end),'instructions':rows})
def word(pc): return int.from_bytes(rom[pc-BASE:pc-BASE+4],'little')
def sx(v,n): return v-(1<<n) if v>>(n-1) else v
def branch(pc,target,funct3,rs1,rs2):
    w=word(pc)
    assert w&127==0x63 and (w>>12)&7==funct3 and (w>>15)&31==rs1 and (w>>20)&31==rs2
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    assert pc+sx(imm,13)==target
def jal(pc,target):
    w=word(pc)
    assert w&127==0x6f
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    assert pc+sx(imm,21)==target
def pair(pc,target):
    a,b=word(pc),word(pc+4)
    assert a&127==0x17 and b&127==0x67
    assert ((a>>7)&31)==((b>>15)&31)==1
    assert (pc+sx(a&0xfffff000,32)+sx(b>>20,12))&0xffffffff==target
branch(0xa00a85bc,0xa00a873e,6,15,10)
branch(0xa00a8742,0xa00a874a,1,10,15)
branch(0xa00a874a,0xa00a8794,6,15,10)
branch(0xa00a8798,0xa00a87d2,6,15,10)
branch(0xa00a87a0,0xa00a87a8,7,15,10)
branch(0xa00a9cd2,0xa00a9cda,0,18,15)
jal(0xa00a87a4,0xa00a9cbc)
jal(0xa00a9cd6,0xa00a85e4)
pair(0xa00a9cc6,0xa01ad024)
pair(0xa01ad03a,0xa000589c)
expected={0xa00a8794:'li a5, 0x68',0xa00a879c:'li a5, 0x60',0xa00a9cbc:'lui a0, 0x62fcb',
          0xa00a9cc0:'c.li a1, 0x1',0xa00a9cc2:'addi a0, a0, 0x50d',0xa00a9cce:'li a5, 0x62',
          0xa00a85b8:'c.mv s2, a0',0xa00a85a8:'sw a2, -0x4c, s0'}
assert all(retained[k]==v for k,v in expected.items())
# Independently check the only non-stack write in the small copy helper.
w=word(0xa01ad036)
assert w&127==0x23 and (w>>12)&7==0 and (w>>15)&31==14 and (w>>20)&31==0
assert (((w>>25)<<5)|((w>>7)&31))==0x2f0
result={'status':'bounded static PASS; author check, not independent acceptance',
 'observed_at_utc':datetime.now(timezone.utc).isoformat(),
 'identity':{'catalog':'roms/CATALOG.md;0041','length':len(rom),'base':hex(BASE),
             'sha256_inherited':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'},
 'sources':[{'path':buzz_path,'pointer':'/functions/5','evidence_id':buzz['evidence_id'],
             'profile_digest':buzz['profile']['digest'],'language_id':'RISCV:LE:32:ap01thead3','original_source':buzz['source']},
            {'path':uart_path,'pointer':'/functions/0','evidence_id':uart['evidence_id'],'profile_digest':uart['profile_digest'],'original_source':uart['source']},
            {'path':n01_path,'pointer':'/windows[name=ack_copy]','authority':'N01 offline original-byte window, accepted by NR01; no new REA Evidence/profile assigned'}],
 'windows':windows,'bytes_checked':sum(e-s for _,s,e in ranges),
 'instruction_count':sum(len(w['instructions']) for w in windows),
 'checks':['7 windows decode and 2/4-byte boundaries','dispatcher slices match two retained raw records and ROM',
           'helper matches N01 retained instruction bytes and ROM','6 branch fields/targets','2 JAL fields/targets',
           '2 AUIPC/JALR fields/targets','8 route/argument retained texts','helper state-store width/registers/offset'],
 'limitations':['no target/ISA model execution','no complete dispatcher certification','copy semantics inherited from N01/NR01',
                'no result-code meaning, MCU execution, persistence or request identity established']}
(OUT/'static-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('P17_STATIC_PASS windows=%d bytes=%d instructions=%d'%(len(windows),result['bytes_checked'],result['instruction_count']))
