"""F33 independently checks retained rows/contracts. No ROM/target/model access."""
import json
from pathlib import Path

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
COMPLETE=MAIN/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
P4825='4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
P04='04b34bbb41e8ff5d0cbbc2c7471d390693c40fe70f2e21519e2b21d268c9237d'
SHA='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
bundle=json.loads(COMPLETE.read_text(encoding='utf-8'))
checks=[]; used=[]
def check(label,actual,expected):
    assert actual==expected,(label,actual,expected)
    checks.append({'label':label,'actual':actual})
ids={248:'ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a',
195:'ev_9a7e0a186c4ed2b341b4d42187fcb73bebec13d401cd226033d30027d121387d',
309:'ev_f7edb78f19e658d59333a033352ac0d773b5a624c66ecd33e8c823a7d5278ccd',
77:'ev_339445ec35b31491f695197f3dd123d01e24a74489ccc10fde6b5e3f8e1a86c6'}
tables={}
for n,eid in ids.items():
    r=bundle['records'][n]
    check('record'+str(n)+' eid',r['evidence_id'],eid)
    check('record'+str(n)+' profile',r['analysis_profile']['digest'],P4825)
    tables[n]={int(x.split(': ',1)[0],16):x.split(': ',1)[1]
        for x in r['normalized_result']['assembly']}
def row(n,va,op,*args):
    text=tables[n][va]
    actual_op,_,operand_text=text.partition(' ')
    operands=tuple(x.strip() for x in operand_text.split(',')) if operand_text else ()
    check(hex(va),(actual_op,operands),(op,args))
    used.append({'record':n,'eid':ids[n],'va':hex(va),'assembly':text})

# Same-object configuration, destinations and actual 16-byte copy interface.
for va,op,args in [
(0xa0064f4a,'addi',('s7','s1','0x128')),
(0xa00653b8,'lui',('a5','0xa0110')),(0xa00653bc,'addi',('a5','a5','0x788')),
(0xa00653c0,'sw',('a5','-0x124','s0')),
(0xa00653c4,'lui',('a5','0xa0110')),(0xa00653c8,'addi',('a5','a5','-0x67c')),
(0xa00653d4,'sw',('a5','-0x120','s0')),(0xa00653d8,'sw',('s10','-0x11c','s0')),
(0xa00653ec,'lui',('a5','0xa011e')),(0xa00653f0,'addi',('a5','a5','0xac')),
(0xa00653f4,'sw',('a5','0x15c','s1')),(0xa00653f8,'c.li',('a2','0x10')),
(0xa00653fa,'addi',('a1','s0','-0x128')),(0xa00653fe,'sw',('s7','0x160','s1')),
(0xa0065402,'addi',('a0','s1','0x164')),(0xa0065406,'jal',('ra','0xa000589c')),
(0xa006556a,'c.mv',('a4','s7')),(0xa006556c,'addi',('a2','a2','0x3d6')),
(0xa0065574,'auipc',('ra','0x132')),(0xa0065578,'jalr',('ra','ra','-0x66')),
(0xa006557c,'c.beqz',('a0','0xa00655da')),
(0xa0065590,'blt',('s4','a5','0xa00655b8')),
(0xa00655b4,'bge',('s4','a5','0xa006563a')),
(0xa00655b8,'c.mv',('a0','s7')),(0xa00655ba,'jal',('ra','0xa011fd3c')),
(0xa00655be,'c.j',('0xa0064fa2',))]:
    row(248,va,op,*args)
# Actual worker first and second callback parameters.
for va,op,args in [
(0xa011e3ee,'c.mv',('s1','a0')),(0xa011e436,'c.lw',('a4','0x10','s1')),
(0xa011e440,'c.lw',('a5','0x4','a4')),(0xa011e442,'c.beqz',('a5','0xa011e44c')),
(0xa011e444,'c.lw',('a1','0x8','a4')),(0xa011e446,'c.mv',('a0','s1')),
(0xa011e448,'c.jalr',('a5',)),(0xa011e44a,'c.mv',('s2','a0'))]:
    row(195,va,op,*args)
for va,op,args in [
(0xa011e0ac,'c.lw',('a5','0x40','a1')),(0xa011e0ae,'c.beqz',('a5','0xa011e0c8')),
(0xa011e0b8,'c.mv',('a0','a1')),(0xa011e0ba,'c.lw',('a1','0x48','a1')),
(0xa011e0bc,'c.jalr',('a5',)),(0xa011e0c2,'c.li',('a0','0x0')),
(0xa011e0c6,'ret',()),(0xa011e0c8,'c.li',('a0','0x0')),(0xa011e0ca,'ret',())]:
    row(309,va,op,*args)
for va,op,args in [
(0xa011fd3c,'c.lw',('a5','0x18','a0')),(0xa011fd3e,'beq',('a5','zero','0xa011fe74')),
(0xa011fd52,'c.mv',('s1','a0')),(0xa011fdc2,'c.lw',('a0','0x18','s1')),
(0xa011fdc4,'c.bnez',('a0','0xa011fe12')),(0xa011fdc6,'c.lw',('a0','0x18','s1')),
(0xa011fdd0,'jal',('ra','0xa01b3c64')),(0xa011fdd4,'sw',('zero','0x18','s1'))]:
    row(77,va,op,*args)

# Address construction/offset arithmetic is static bookkeeping, not ISA simulation.
check('second config target',hex(0xa0110000+0x788),'0xa0110788')
check('third config target',hex(0xa0110000-0x67c),'0xa010f984')
check('vtable second function',hex(0xa011e000+0xac),'0xa011e0ac')
check('config and vtable offsets',tuple(x-0x128 for x in (0x164,0x158,0x15c,0x160,0x140)),
      (0x3c,0x30,0x34,0x38,0x18))
check('16B config slot offsets',tuple(0x3c+i for i in (4,8,12)),(0x40,0x44,0x48))
check('nested ctx identities',(0xe8+0x8c,0xe8+0x880),(0x174,0x968))

local=json.loads((MAIN/'evidence/rea-0041-20261017/evidence/upper-miio-b.json').read_text(encoding='utf-8'))
contracts=[]
for addr,eid in [('0xa011e0ac','ev_9a6f1939371027a133a36f527343d421d82247d825be42acd324c72a304de0f8'),
 ('0xa011e3d6','ev_d6ca150724daa7644ed5506256c6a95b1a2139c22f4d49cf6923fd6bf288bbea'),
 ('0xa0110788','ev_fed264e8febd84155f55a3ea96b02d2f198fbc22194ca0bf56d1850b312f38df'),
 ('0xa010f984','ev_0e30a891adc06e823abfad79fbef5207569374ee6db7fbe1b4ead46340cce0e2')]:
    c=next(x for x in local['functions'] if x['address']==addr)
    check(addr+' local contract eid',c['evidence_id'],eid)
    check(addr+' distinct profile',c['profile_digest'],P04)
    check(addr+' subject',c['source_sha256'],SHA)
    contracts.append({k:c[k] for k in ('address','evidence_id','profile_digest','role','unresolved_boundary')})
f15=json.loads((MAIN/'reverse/analysis/miio-queue-size-gap-f15-0041-20261024/contract.json').read_text(encoding='utf-8'))
check('inherited L identity',f15['identity']['L'],'M+0x128')
check('inherited user identity',f15['identity']['user'],'M+0xe8')
f16=(MAIN/'reverse/reports/ap01/miio-queue-size-review-f16-0041-20261024.md').read_text(encoding='utf-8')
check('F16 limited acceptance exists','限定接受F15' in f16,True)
routing=(MAIN/'evidence/rea-0041-20261017/evidence/upper-routing.md').read_text(encoding='utf-8')
check('routing storage boundary','caller-owned group storage is not freed by this function' in routing,True)
author=json.loads((MAIN/'reverse/analysis/miio-loop-exit-gap-f32-0041-20261024/contract.json').read_text(encoding='utf-8'))
check('author other role remains distinct',author['configuration']['L+0x44'],
      '0xa010f984 (other callback role; not exit slot)')
check('author excludes actual quit','actual quit or worker finished' in author['not_proved'],True)
check('author excludes drain','queued I objects drained/returned' in author['not_proved'],True)
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'review-evidence.json').write_text(json.dumps({'reviewer':'F33 nonauthor','result':'PASS',
    'checks':checks,'check_count':len(checks),'retained_rows':used,'old_local_contracts':contracts,
    'rom_bytes_read':0,'limits':['selected failure path only; conditional logging branch retained',
    'no actual quit or queued-I/final-free closure','normal callee-save/config/field compatibility required']},
    ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('F33 PASS',len(checks),'independent retained-field/reference checks; ROM0B')
