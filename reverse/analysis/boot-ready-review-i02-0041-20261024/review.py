"""Independent I02 sparse field/target review; no callback re-export/execution."""
import json
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
TREE=HERE.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
old=json.loads((MAIN/'reverse/rehost/system-complete-0041.json').read_text(encoding='utf-8'))
producer=json.loads((TREE/'reverse/analysis/boot-ready-increment-i01-0041-20261024/evidence.json').read_text(encoding='utf-8'))
guide=json.loads((MAIN/'reverse/rehost/guide-complete-0041.json').read_text(encoding='utf-8'))
rows={int(r['address'],16):r for k in ['0xa009d7b4','0xa00a73fe'] for r in old['local_disassembly'][k]}
checks=[]
def require(name,actual,expected):
    assert actual==expected,(name,actual,expected)
    checks.append({'check':name,'actual':actual,'expected':expected})
with (MAIN/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as rom:
    def read(pc,n):
        rom.seek(pc-0x9ffff000)
        result=rom.read(n)
        assert len(result)==n
        return result
    def word(pc): return int.from_bytes(read(pc,4),'little')
    def half(pc): return int.from_bytes(read(pc,2),'little')
    def signed(x,b): return x-(1<<b) if x&(1<<(b-1)) else x
    def check_old(pc):
        r=rows[pc]
        require('old original bytes '+hex(pc),read(pc,len(bytes.fromhex(r['bytes']))).hex(),r['bytes'])
    for inherited in producer['inherited_anchors']: check_old(int(inherited['address'],16))
    for w in producer['added_windows']:
        require('I01 retained window '+w['role'],read(int(w['start'],16),len(bytes.fromhex(w['bytes']))).hex(),w['bytes'])
    # Additional rows already present in old system, not new byte windows.
    for pc in [0xa009d7c6,0xa009d7cc,0xa009d7d0,0xa009d7e6,0xa00a74f2,
               0xa00a7556,0xa00a7566,0xa00a757e,0xa00a75aa,0xa00a75bc,0xa00a75da,0xa00a75e4]:check_old(pc)
    def fields(pc):
        x=word(pc)
        return (x&127,(x>>7)&31,(x>>12)&7,(x>>15)&31,(x>>20)&31,x>>25)
    def load(pc,rd,base,disp,funct3):
        x=word(pc)
        require('load width/regs '+hex(pc),[x&127,(x>>7)&31,(x>>12)&7,(x>>15)&31,signed(x>>20,12)],
                [3,rd,funct3,base,disp])
    def store(pc,rs,base,disp,funct3):
        x=word(pc); imm=(x>>25)<<5|((x>>7)&31)
        require('store width/regs '+hex(pc),[x&127,(x>>20)&31,(x>>12)&7,(x>>15)&31,signed(imm,12)],
                [35,rs,funct3,base,disp])
    def branch(pc,rs1,rs2,funct3,target):
        x=word(pc)
        imm=((x>>31)&1)<<12|((x>>7)&1)<<11|((x>>25)&63)<<5|((x>>8)&15)<<1
        require('branch '+hex(pc),[x&127,(x>>15)&31,(x>>20)&31,(x>>12)&7,pc+signed(imm,13)],
                [99,rs1,rs2,funct3,target])
    def compact_jump(pc,target):
        x=half(pc)
        imm=((x>>12)&1)<<11|((x>>11)&1)<<4|((x>>9)&3)<<8|((x>>8)&1)<<10|((x>>7)&1)<<6|((x>>6)&1)<<7|((x>>3)&7)<<1|((x>>2)&1)<<5
        require('C.J '+hex(pc),[x&3,x>>13,pc+signed(imm,12)],[1,5,target])
    def call(pc,target):
        x=word(pc); imm=((x>>31)&1)<<20|((x>>12)&255)<<12|((x>>20)&1)<<11|((x>>21)&1023)<<1
        require('JAL '+hex(pc),[x&127,(x>>7)&31,pc+signed(imm,21)],[111,1,target])
    def compact_li(pc,rd,imm):
        x=half(pc)
        require('C.LI '+hex(pc),[x&3,x>>13,(x>>7)&31,signed(((x>>12)&1)<<5|((x>>2)&31),6)],
                [1,2,rd,imm])
    def compact_move(pc,rd,rs):
        x=half(pc)
        require('C.MV '+hex(pc),[x&3,x>>12,(x>>7)&31,(x>>2)&31],[2,8,rd,rs])
    load(0xa009d7c2,15,15,-20,0)  # LB, zero/nonzero branch only.
    x=half(0xa009d7ca)
    imm=((x>>12)&1)<<8|((x>>10)&3)<<3|((x>>5)&3)<<6|((x>>3)&3)<<1|((x>>2)&1)<<5
    require('cache bypass C.BNEZ', [x&3,x>>13,8+((x>>7)&7),0xa009d7ca+signed(imm,9)],
            [1,7,15,0xa009d812])
    require('bypass flag address',(word(0xa009d7be)&0xfffff000)-20,0x62fc3fec)
    compact_li(0xa009d7d4,13,1)
    call(0xa009d7e2,0xa0060946)
    compact_li(0xa009d7e6,15,1)
    branch(0xa009d7f0,10,15,0,0xa009d820)
    store(0xa009d80e,0,9,0x19c,0)
    load(0xa009d816,10,9,0x19c,4)
    require('cache address',(word(0xa009d7c6)&0xfffff000)+0x19c,0x62fc919c)
    compact_jump(0xa009d83e,0xa009d812)
    require('tail is exact I01 two-byte addition',read(0xa009d83e,2).hex(),'d1bf')
    # Getter literal pointers are built before call, not sourced from rc.
    for pc,upper,reg,imm in [(0xa009d7d6,0xa009d7cc,11,0x58),(0xa009d7de,0xa009d7d0,10,0x68),
                             (0xa009d7da,0xa009d7c6,12,0x19c)]:
        op,rd,f3,rs1,_,_=fields(pc)
        require('argument ADDI '+hex(pc),[op,rd,f3,rs1,signed(word(pc)>>20,12)],
                [19,reg,0,reg if pc!=0xa009d7da else 9,imm])
    for address,value in [(0xa01c3058,b'wifi_configured\0'),(0xa01c3068,b'ck_config\0')]:
        require('literal '+hex(address),read(address,len(value)).hex(),value.hex())
    load(0xa00a7488,19,10,12,2)
    load(0xa00a74d0,20,21,8,2)
    require('port snapshot effective address',(word(0xa00a74c8)&0xfffff000)+signed(word(0xa00a74cc)>>20,12)+8,0x62fc4034)
    call(0xa00a74fa,0xa009d7b4)
    compact_move(0xa00a7502,23,10)
    branch(0xa00a751c,23,0,0,0xa00a7568)
    branch(0xa00a753a,20,0,0,0xa00a7552)
    load(0xa00a7552,15,19,0,4)
    compact_li(0xa00a7556,14,1)
    require('increment C.ADDI',half(0xa00a7558),0x0785)
    require('ANDI counter 255',[word(0xa00a755a)&127,(word(0xa00a755a)>>7)&31,
                               (word(0xa00a755a)>>12)&7,(word(0xa00a755a)>>15)&31,word(0xa00a755a)>>20],
                              [19,15,7,15,255])
    store(0xa00a755e,15,19,0,0)
    branch(0xa00a7562,14,15,7,0xa00a74b2)
    compact_jump(0xa00a7566,0xa00a753e)
    compact_move(0xa00a74f2,22,10)  # Timer before first normal-path log call.
    call(0xa00a753e,0xa00a73fe)
    compact_move(0xa00a7542,10,22)
    compact_li(0xa00a7544,11,0)
    call(0xa00a7546,0xa008c280)
    compact_move(0xa00a754a,10,19)
    call(0xa00a754c,0xa008ab8a)
    compact_jump(0xa00a75bc,0xa00a7542)
    compact_li(0xa00a75aa,15,1)
    store(0xa00a75ac,15,21,0x25,0)
    load(0xa00a75b0,10,20,5,4)
    compact_li(0xa00a75da,15,1)
    store(0xa00a75dc,15,21,12,0)
    compact_jump(0xa00a75e4,0xa00a75b0)
    for pc,target in [(0xa00a75b4,0xa00b2ea6),(0xa00a75b8,0xa00a73ac),
                      (0xa00a75e0,0xa00a5cea),(0xa005ce82,0xa008e362),(0xa005ce98,0xa008bc64)]:call(pc,target)
    compact_li(0xa005ce80,10,1)
    compact_move(0xa005ce86,12,10)
    store(0xa005ce88,0,10,0,0)
    require('timer callback address',(word(0xa005ce8c)&0xfffff000)+signed(word(0xa005ce94)>>20,12),0xa00a7472)
    require('timer interval immediate',signed(word(0xa005ce90)>>20,12),1000)

with zipfile.ZipFile(MAIN/'reverse/rehost/ap01-ui-0041-complete-source.zip') as z:
    sim=z.read('tools/ap01/ap01-ui-guide.h').decode().splitlines()
    require('SIM fixed 2s is replacement only', 'lv_tick_elaps(g_ap01_ui_boot_start) < 2000' in sim[298],True)
require('old boot deletion separately targets window helper',
        'a00a73f8' in guide['bounded_local_disassembly']['boot_delete_asm'] and
        'a00ded6c' in guide['bounded_local_disassembly']['boot_delete_asm'],True)
result={'status':'PASS','baseline':'46fa469','checks':checks,'new_function_recovery':0,
        'new_function_exports':0,'new_byte_windows':0,
        'inherited_original_source':'main reverse/rehost/system-complete-0041.json local_disassembly getter and boot keys',
        'I01_reused':{'old_anchors':len(producer['inherited_anchors']),
                      'existing_windows':[{'role':w['role'],'start':w['start'],'bytes_count':len(bytes.fromhex(w['bytes']))}
                                          for w in producer['added_windows']]},
        'decision':'accept getter rc/cache U8, snapshot, 2B return tail, timer userdata ownership and SIM boundary',
        'limits':['wifi_configured is persisted/cache UI input, not hardware ready',
                  'repeat_count zero is not direct timer free; boot-window deletion has separate target',
                  'no configuration service, hardware initialization or timer finalizer expansion']}
(HERE/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','checks':len(checks),'I01_old_anchors':len(producer['inherited_anchors']),
                  'new_byte_windows':0,'function_recovery':0}))
