"""I05 bounded reuse and static config-cache callsite checks, no execution."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE=0x9ffff000
old=json.loads((MAIN/'evidence/wifi-psm-bounded-disassembly-20261021.json').read_text(encoding='utf8'))
range7=old['ranges'][7]
late=json.loads((MAIN/'evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json').read_text(encoding='utf8'))['records'][5]
norm=late['normalized_result']
checks=[]
def raw(pc,n): return ROM[pc-BASE:pc-BASE+n]
def w(pc,n=4): return int.from_bytes(raw(pc,n),'little')
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
def eq(label,got,expected):
 assert got==expected,(label,got,expected)
 checks.append(label)
def imm(pc,op,f3,rd,r1,value):
 v=w(pc)
 eq(hex(pc)+' I fields',(v&127,(v>>12)&7,(v>>7)&31,(v>>15)&31,sx(v>>20,12)),(op,f3,rd,r1,value))
def lui(pc,rd,value):
 v=w(pc)
 eq(hex(pc)+' LUI',(v&127,(v>>7)&31,v&0xfffff000),(55,rd,value))
def cli(pc,rd,value):
 v=w(pc,2)
 eq(hex(pc)+' C.LI',(v&3,v>>13,(v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6)),(1,2,rd,value))
def jal(pc,rd,target):
 v=w(pc)
 off=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
 eq(hex(pc)+' JAL fields/target',(v&127,(v>>7)&31,pc+sx(off,21)),(111,rd,target))
eq('retained bounded range',range7['start'],'0xa005acd0')
for r in range7['instructions']:
 eq(r['address']+' retained raw',raw(int(r['address'],16),len(bytes.fromhex(r['bytes']))).hex(),r['bytes'])
lui(0xa005acc8,12,0x62fc9000)
lui(0xa005acda,11,0xa01c3000)
lui(0xa005acde,21,0xa01c3000)
imm(0xa005acea,19,0,27,12,0x19c)
cli(0xa005acee,13,1)
imm(0xa005acf0,19,0,12,12,0x19c)
imm(0xa005acf4,19,0,11,11,0x58)
imm(0xa005acf8,19,0,10,21,0x68)
jal(0xa005acfc,1,0xa0060946)
cli(0xa005ad00,15,1)
v=w(0xa005ad0a)
off=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
eq('exact rc one gate',(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,0xa005ad0a+sx(off,13)),(99,0,10,15,0xa005b7fa))
v=w(0xa005ad28)
eq('failure cache byte clear',(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,sx(((v>>25)<<5)|((v>>7)&31),12)),(35,0,27,0,0))
imm(0xa005b7fa,3,4,15,27,0)
jal(0xa005b814,1,0xa008b51a)
jal(0xa005b818,0,0xa005ad2c)
for pc,expected in [(0xa01c3058,'wifi_configured'),(0xa01c3068,'ck_config')]:
 eq(hex(pc)+' config string',raw(pc,len(expected)+1),expected.encode()+b'\0')
refs=norm['outgoing_references']
eq('old initializer procedure',norm['procedure']['address'],'0xa005a736')
for pc,kind in [('0xa005acf0','PARAM'),('0xa005ad28','WRITE'),('0xa005b7fa','READ')]:
 eq(pc+' retained reference',any(r.get('source_address')==pc and r.get('target_address')=='0x62fc919c' and r['kind']['type']==kind for r in refs),True)
eq('old normal pseudocode matches same key','s_wifi_configured_ram_a01c3058' in norm['pseudocode'],True)
supplemental=[(0xa005acc8,'3796fc62'),(0xa005ad28,'23800d00'),(0xa005b7fa,'83c70d00'),(0xa005b818,'6ff04fd1')]
for pc,h in supplemental: eq(hex(pc)+' sparse supplement',raw(pc,len(bytes.fromhex(h))).hex(),h)
reuse=[]
terms=['a005acf0','a005ad28','62fc919c','wifi_configured']
for p in sorted((MAIN/'reverse/rehost').glob('*.json')):
 text=p.read_text(encoding='utf8',errors='replace').lower()
 hits=[t for t in terms if t in text]
 if hits: reuse.append({'file':p.name,'terms':hits})
result={'status':'PASS','static_only':True,'checks':checks,'old_byte_instruction_count':len(range7['instructions']),'normal_source':{'evidence_id':late['evidence_id'],'pointer':'round3 whole-rom-round3-initial.evidence.json#/records/5','procedure':'0xa005a736','meaning':'Initializer reads one-byte persistent configuration into the same cache used by I01; only rc==1 preserves it, otherwise caller clears it.'},'supplemental_bytes':[{'address':hex(pc),'bytes':h} for pc,h in supplemental],'supplemental_byte_count':16,'reuse_main_rehost_json':reuse,'new_rom_functionality':0,'limits':['a005acf0 and a005ad28 are callsite/store addresses, not standalone setter entries.','This initializer path does not call persistent config-write a0061848.','No driver/network/cloud or all-writer/flag-lifetime claims.','I01 getter and legacy PSM interfaces inherited without rerunning them.']}
(OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':'PASS','checks':len(checks),'old_byte_instructions':len(range7['instructions']),'supplemental_bytes':16,'new_rom_functionality':0}))
