"""I06 independent static callsite review, no old verifier/model execution."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
REV=HERE.parents[1]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
rom=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
old=json.loads((MAIN/'evidence/wifi-psm-bounded-disassembly-20261021.json').read_text())['ranges'][7]
i05=json.loads((REV/'analysis/wifi-config-cache-i05-0041-20261024/verification.json').read_text())
checks=[]
def raw(pc,n):return rom[pc-BASE:pc-BASE+n]
def word(pc):return int.from_bytes(raw(pc,4),'little')
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def check(label,value,expected):
    assert value==expected,(label,value,expected)
    checks.append(label)

for row in old['instructions']:
    check(row['address']+' old raw',raw(int(row['address'],16),len(bytes.fromhex(row['bytes']))).hex(),row['bytes'])
for row in i05['supplemental_bytes']:
    check(row['address']+' I05 sparse raw',raw(int(row['address'],16),len(bytes.fromhex(row['bytes']))).hex(),row['bytes'])

def i_fields(pc,op,f3,rd,rs1,imm):
    w=word(pc)
    check(hex(pc)+' I fields',(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12)),(op,f3,rd,rs1,imm))
for pc,rd,rs1,imm in [(0xa005acea,27,12,0x19c),(0xa005acf0,12,12,0x19c),
                       (0xa005acf4,11,11,0x58),(0xa005acf8,10,21,0x68)]:
    i_fields(pc,19,0,rd,rs1,imm)
for pc,rd,upper in [(0xa005acc8,12,0x62fc9000),(0xa005acda,11,0xa01c3000),(0xa005acde,21,0xa01c3000)]:
    w=word(pc)
    check(hex(pc)+' LUI fields',(w&127,(w>>7)&31,w&0xfffff000),(55,rd,upper))
for pc,rd in [(0xa005acee,13),(0xa005ad00,15)]:
    w=int.from_bytes(raw(pc,2),'little')
    check(hex(pc)+' C.LI one',(w&3,w>>13,(w>>7)&31,sx((((w>>12)&1)<<5)|((w>>2)&31),6)),(1,2,rd,1))

def jal(pc,rd,target):
    w=word(pc)
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    check(hex(pc)+' JAL target',(w&127,(w>>7)&31,pc+sx(imm,21)),(111,rd,target))
for args in [(0xa005acfc,1,0xa0060946),(0xa005ad24,1,0xa008b51a),
             (0xa005b814,1,0xa008b51a),(0xa005b818,0,0xa005ad2c)]:jal(*args)
w=word(0xa005ad0a)
imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
check('exact a0 == a5(1) branch',(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,0xa005ad0a+sx(imm,13)),(99,0,10,15,0xa005b7fa))
w=word(0xa005ad28)
check('failure SB zero cache',(w&127,(w>>12)&7,(w>>20)&31,(w>>15)&31,sx(((w>>25)<<5)|((w>>7)&31),12)),(35,0,0,27,0))
i_fields(0xa005b7fa,3,4,15,27,0)
for pc,text in [(0xa01c3058,'wifi_configured'),(0xa01c3068,'ck_config')]:
    check(hex(pc)+' exact string',raw(pc,len(text)+1),text.encode()+bytes([0]))

# Old 64B range ends after only the first halfword of a 4B LUI.
tail=old['instructions'][-1]
check('old terminal entry is 2-byte prefix',(tail['address'],tail['bytes'],tail['mnemonic']),('0xa005ad0e','3737','.byte'))
check('complete boundary LUI raw',raw(0xa005ad0e,4).hex(),'37371ca0')
result={'passed':True,'checks':checks,'old_raw_rows':18,'old_complete_instructions':17,
        'old_terminal_partial_bytes':2,'I05_sparse_anchors':len(i05['supplemental_bytes']),
        'boundary_completion':{'pc':'0xa005ad0e','full_raw':'37371ca0','new_tail_bytes':'1ca0','meaning':'LUI a4,a01c3; old raw entry is not a complete instruction'},
        'accepted':['read(ck_config,wifi_configured,62fc919c,1)',
                    'only rc exactly 1 takes successful byte-read/log arm',
                    'other rc logs then caller clears byte with SB; both continue ad2c',
                    'caller success arm does not set cache to one or mask bit0',
                    'same-key/cache getter relation inherited from I01/I02'],
        'precision_correction':'I05 wording 18 old instructions should be 18 raw entries: 17 complete instructions and one 2B prefix.',
        'semantic_corrections':0,'new_functionality':0,
        'unknown':['all cache/bypass writers and their timing','backend complete I/O/locks/config state',
                   'runtime network/hardware readiness'],
        'shared_rea_target':False}
(HERE/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'checks':len(checks),'old_rows':18,'old_complete_instructions':17,'boundary_new_bytes':2,'new_functionality':0}))
