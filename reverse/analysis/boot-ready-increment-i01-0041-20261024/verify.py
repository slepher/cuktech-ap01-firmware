"""I01: reuse-first, sparse static ABI/width/return checks. No target execution."""
from pathlib import Path
import json
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=ROOT/'roms/0041/ap01-1.0.2_0041.bin'
data=ROM.read_bytes()
def read(a,n):
    o=a-0x9ffff000
    assert 0<=o<=len(data)-n
    return data[o:o+n]
def word(a):return int.from_bytes(read(a,4),'little')
def sx(v,n):return (v^(1<<(n-1)))-(1<<(n-1))
checks=[]
def eq(label,a,v,e):
    assert v==e,(label,hex(a),v,e)
    checks.append(dict(label=label,address=hex(a),actual=v,expected=e))
def jal(a,t):
    w=word(a);v=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    eq('JAL target/register',a,[w&127,(w>>7)&31,(a+sx(v,21))&0xffffffff],[111,1,t])
def mem(a,op,f3,reg,base,imm):
    w=word(a);v=w>>20 if op==3 else ((w>>25)<<5)|((w>>7)&31)
    r=(w>>7)&31 if op==3 else (w>>20)&31
    eq('memory fields',a,[w&127,(w>>12)&7,r,(w>>15)&31,sx(v,12)],[op,f3,reg,base,imm])
system_path=ROOT/'reverse/rehost/system-complete-0041.json'
system=json.loads(system_path.read_text(encoding='utf8'))
inherited=[]
groups={'0xa009d7b4':[0xa009d7be,0xa009d7c2,0xa009d7ca,0xa009d7d4,0xa009d7d6,0xa009d7da,0xa009d7de,0xa009d7e2,0xa009d7f0,0xa009d80e,0xa009d816], '0xa00a73fe':[0xa00a7488,0xa00a74c8,0xa00a74cc,0xa00a74d0,0xa00a74fa,0xa00a7502,0xa00a751c,0xa00a753a,0xa00a753e,0xa00a7542,0xa00a7544,0xa00a7546,0xa00a754a,0xa00a754c,0xa00a7552,0xa00a7558,0xa00a755a,0xa00a755e,0xa00a7562,0xa00a7586,0xa00a758a,0xa00a758e,0xa00a75ac,0xa00a75b0,0xa00a75b4,0xa00a75b8,0xa00a75dc,0xa00a75e0]}
for key,addresses in groups.items():
    old={int(r['address'],16):r for r in system['local_disassembly'][key]}
    for a in addresses:
        r=old[a];raw=bytes.fromhex(r['bytes'])
        eq('inherited raw matches original',a,read(a,len(raw)).hex(),r['bytes'])
        inherited.append(dict(address=hex(a),source=f'{system_path}#/local_disassembly/{key}',role='Old raw recheck; no new function recovery'))
for a,t in [(0xa009d7e2,0xa0060946),(0xa00a74fa,0xa009d7b4),(0xa00a753e,0xa00a73fe),(0xa00a7546,0xa008c280),(0xa00a754c,0xa008ab8a),(0xa00a75b4,0xa00b2ea6),(0xa00a75b8,0xa00a73ac),(0xa00a75e0,0xa00a5cea),(0xa005ce82,0xa008e362),(0xa005ce98,0xa008bc64)]:jal(a,t)
for args in [(0xa009d7c2,3,0,15,15,-20),(0xa009d80e,35,0,0,9,0x19c),(0xa009d816,3,4,10,9,0x19c),(0xa00a7488,3,2,19,10,12),(0xa00a74d0,3,2,20,21,8),(0xa00a7552,3,4,15,19,0),(0xa00a755e,35,0,15,19,0),(0xa00a75ac,35,0,15,21,0x25),(0xa00a75dc,35,0,15,21,12)]:mem(*args)
# Only missing 2-byte return jump is added to the old getter coverage.
h=int.from_bytes(read(0xa009d83e,2),'little')
v=(((h>>12)&1)<<11)|(((h>>11)&1)<<4)|(((h>>9)&3)<<8)|(((h>>8)&1)<<10)|(((h>>7)&1)<<6)|(((h>>6)&1)<<7)|(((h>>3)&7)<<1)|(((h>>2)&1)<<5)
eq('getter tail C.J',0xa009d83e,[h&3,h>>13,0xa009d83e+sx(v,12)],[1,5,0xa009d812])
eq('timer callback registration address',0xa005ce8c,((word(0xa005ce8c)&0xfffff000)+sx(word(0xa005ce94)>>20,12))&0xffffffff,0xa00a7472)
eq('timer interval immediate',0xa005ce90,sx(word(0xa005ce90)>>20,12),1000)
for a,b in [(0xa005ce80,'0545'),(0xa005ce86,'2a86'),(0xa005ce88,'23000500')]:eq('registration ABI anchor',a,read(a,len(bytes.fromhex(b))).hex(),b)
strings=[]
for a,expected in [(0xa01c3058,'wifi_configured'),(0xa01c3068,'ck_config'),(0xa02690a0,'wifi_pair = %d\n')]:
    o=a-0x9ffff000;s=data[o:data.index(bytes([0]),o)].decode('utf8');eq('literal identity',a,s,expected);strings.append(dict(address=hex(a),text=s))
with zipfile.ZipFile(ROOT/'reverse/rehost/ap01-ui-0041-complete-source.zip') as z:
    member='tools/ap01/ap01-ui-guide.h';lines=z.read(member).decode('utf8').splitlines()
    assert 'lv_tick_elaps(g_ap01_ui_boot_start) < 2000' in lines[298]
    sim=dict(member=member,line=299,text=lines[298],classification='Host SIM replacement, not original readiness predicate')
guide=json.loads((ROOT/'reverse/rehost/guide-complete-0041.json').read_text(encoding='utf8'))
assert 'a009d7b4' in guide['bounded_local_disassembly']['boot_timer_asm']
summary=dict(result='passed',static_only=True,inherited_anchors=len(inherited),checks=len(checks),new_function_recovery=0,new_raw_tail_bytes=2,registration_recheck_bytes=28,vendor_words=0)
(HERE/'evidence.json').write_text(json.dumps(dict(summary=summary,rom=str(ROM),mapping='offset=VA-0x9ffff000',checks=checks,inherited_anchors=inherited,added_windows=[dict(role='missing getter tail',start='0xa009d83e',bytes=read(0xa009d83e,2).hex()),dict(role='old timer attachment ABI recheck',start='0xa005ce80',bytes=read(0xa005ce80,28).hex())],strings=strings,sim=sim,reuse=dict(guide='guide-complete-0041.json#/boot and bounded_local_disassembly/boot_timer_asm,boot_delete_asm',system='system-complete-0041.json#/native_semantics/overview_gates/boot_final and local_disassembly',pass3='0041-ghidra-pass3.txt:2892 already attaches timer(callback,1000,one-byte userdata)',main='main-knob-0041-round2.json#/records/1 ev_daf583e6c481f2d7f53eb8443cd04003d53c22365147ac088957c1415a947da7 has getter callee extent, not a new getter body',round3='whole-rom-round3-initial.evidence.json#/records/5 ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3 has 62fc919c references; not followed into initialization',page_logic='24 records; no exact a00a7472/a009d7b4 token match from bounded query',limit='Existing materials reused; no claim that uncited history never analyzed this path.')),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary))
