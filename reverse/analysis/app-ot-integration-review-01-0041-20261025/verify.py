from pathlib import Path
import hashlib,json,re
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
AUTHOR=Path('D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/ot-integration01/reverse/analysis/app-ot-integration-research-01-0041-20261025')
OUT=Path(__file__).resolve().parent
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes(); base=0x9ffff000
assert len(rom)==6769704
assert hashlib.sha256(rom).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
d=json.loads((AUTHOR/'evidence.json').read_text()); c=json.loads((AUTHOR/'contract.json').read_text())
records=0; total=0; jal=0; unknown=[]
for win in d['windows']:
    start=int(win['start'],16); end=int(win['end_exclusive'],16); cursor=start
    data=rom[start-base:end-base]
    assert len(data)==win['size'] and hashlib.sha256(data).hexdigest()==win['sha256']
    total+=len(data)
    for row in win['rows']:
        pc=int(row['pc'],16); raw=bytes.fromhex(row['raw']); assert pc==cursor
        assert rom[pc-base:pc-base+len(raw)]==raw
        assert len(raw)==(2 if int.from_bytes(raw[:2],'little')&3!=3 else 4)
        if row['asm']=='UNDECODED': unknown.append({'pc':row['pc'],'raw':row['raw']})
        if row['asm'].startswith('jal '):
            word=int.from_bytes(raw,'little'); assert word&127==0x6f
            imm=((word>>31)<<20)|(((word>>12)&255)<<12)|(((word>>20)&1)<<11)|(((word>>21)&1023)<<1)
            if imm&0x100000: imm-=0x200000
            assert imm==int(row['asm'].split()[-1],16)
            if row['pc'] in c['raw_jal_targets_checked']: assert (pc+imm)&0xffffffff==int(c['raw_jal_targets_checked'][row['pc']],16)
            jal+=1
        cursor+=len(raw); records+=1
    assert cursor==end
assert total==3658 and records==1139 and len(d['windows'])==8
assert unknown==c['unknown_words'] and len(unknown)==7
assert rom[0xa0112b12-base:0xa0112b1e-base].hex()=='771925c31305803e33052503'
for addr,value in c['rom_strings_checked'].items():
    off=int(addr,16)-base; assert rom[off:rom.index(0,off)].decode()==value
# Independently extract ordinary I immediates/registers for object identities.
for pc,rd,rs,imm in [(0xa010fd64,18,11,-0xe8),(0xa01129d0,18,11,-0xe8),(0xa0112748,18,10,-0xe8),(0xa0112dcc,21,19,0x780),(0xa0112dd0,19,19,0x698),(0xa0113806,9,9,0x698),(0xa0110ada,10,10,0x698)]:
    w=int.from_bytes(rom[pc-base:pc-base+4],'little'); actual=w>>20
    if actual&0x800: actual-=0x1000
    assert w&127==0x13 and (w>>7)&31==rd and (w>>15)&31==rs and actual==imm
result={'claim':'Q-31','review':'S-P49','author_commit':'a5abd029fc1a59b550c4c20b5a45ab73892e2fb2','review_baseline':'5a5b732235c5b0d1654c8bc543b92c9cc5331e0b','result':'bounded acceptance; no semantic correction','body_bytes':total,'records':records,'fragments':8,'logical_bodies':7,'ordinary_jal_checked':jal,'target_checks':len(c['raw_jal_targets_checked']),'strings_checked':len(c['rom_strings_checked']),'object_immediate_checks':7,'unknown_words':unknown,'excluded_gap':d['excluded_gap'],'execution':'static ROM reads only; no author script executed','limits':['vendor ISA unknown','OTA complete time expression','syncfixedip unknown sources','full owner lifetime','event framework retention','actual queue cancellation and concurrency','cloud acceptance']}
(OUT/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['unknown_words','limits']},ensure_ascii=False))
