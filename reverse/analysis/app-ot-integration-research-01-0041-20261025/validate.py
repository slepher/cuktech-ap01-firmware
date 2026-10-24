from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
d=json.loads((O/'evidence.json').read_text(encoding='utf-8'))
unknown=[{'pc':r['pc'],'raw':r['raw']} for w in d['windows'] for r in w['rows'] if r['asm']=='UNDECODED']
assert len(unknown)==7
assert sum(w['size'] for w in d['windows'])==3658
assert sum(len(w['rows']) for w in d['windows'])==1139
assert d['excluded_gap']['end_exclusive']=='0xa0112b1e'
c={'claim':'Q-31','package':'S-P46','status':'author-static-partial-pending-independent-review','baseline':'5f50102e56012e2e1e0fa8f9d8010d3c8e8214fd','first_utc':'2026-10-24 18:14:37 UTC','rom_sha256':d['rom_sha256'],'body_bytes':3658,'instruction_records':1139,'logical_bodies':7,'contiguous_fragments':8,'unknown_words':unknown,'excluded_gap':d['excluded_gap'],'objects':{'B':'registered owner','C':'B-0xe8','E':'B+0x880=C+0x968'},'events':{'field':'load32(event+0x1c)','ids':[1,5,9,10],'changed_latch':'byte(B+0x1a08)=byte(C+0x1af0)','9':'0->1; schedule periodic and pull with E','10':'nonzero->0; cancel periodic and pull with E; cancel B callbacks; no queue-quiescence guarantee'},'periodic':{'entry':'0xa01137f6','ctx':'E','serializer':'0xa01109d6(C,Q)','method':'_otc.info','callback':'0xa0112260','callback_user':'E','timeout_word':'E+0x1104','returns':1800000},'pull':{'entry':'0xa0110aca','ctx':'E','method':'_otc.pull_ip_list','callback':'0xa01102d8','callback_user':'E','timeout_word':'E+0x1104','returns':'load32(E+0x110c)'},'sdk_ownership':'Inherited F11/F12/Q24: normal positive-length payload copied synchronously; user shallow; submit0 is not delivery','boundaries':['producer numeric event meaning','unknown vendor words','12B nonbody flow','full owner/child lifetime','event API retention','real scheduler and queued cancellation','cloud acceptance','full OTA time expression'],'artifacts':{'evidence.json':'ignored local raw','instructions.txt':'ignored local rendering','extract.py':'tracked bounded static decoder'}}
(O/'contract.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('contract static checks passed')
# Independent ordinary JAL bit extraction, no target execution.
b=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes(); base=0x9ffff000
calls={0xa0112ee6:0xa01ab648,0xa0112fde:0xa01ab648,0xa0112ff4:0xa01ab648,0xa0113008:0xa01196d6,0xa01130b4:0xa01196d6,0xa01131dc:0xa0111ff6,0xa01132be:0xa01ab634,0xa01132d0:0xa01ab634,0xa01132e6:0xa01ab462,0xa01132f8:0xa01ab462,0xa0112afa:0xa0112734,0xa0112b48:0xa0112734,0xa011290a:0xa0111ff6,0xa011383a:0xa01109d6,0xa01138ce:0xa011f9da,0xa011390a:0xa01137d6,0xa0113924:0xa01ab648,0xa0110ba2:0xa011f9da}
for pc,target in calls.items():
 w=int.from_bytes(b[pc-base:pc-base+4],'little'); assert w&127==111
 imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 if imm&(1<<20):imm-=1<<21
 assert (pc+imm)&0xffffffff==target
strings={0xa01c3280:'id',0xa056c058:'method',0xa01c2488:'params',0xa060e49c:'_sync.ota_sync_update',0xa060e4b4:'type_mark',0xa060f238:'did',0xa060e4c0:'sync_firmware',0xa060e4d0:'sync_mcu',0xa0255a58:'gmt_offset',0xa060de60:'_otc.pull_ip_list',0xa060de28:'_otc.info',0xa060e788:'_otc.syncfixedip',0xa0607acc:'version',0xa060e754:'httpdns',0xa0255d9c:'"token"',0xa0255d84:'"bindkey"',0xa025a510:'ota_start_time',0xa025a520:'ota_dura_time',0xa0255a64:'ot_config'}
for address,value in strings.items():
 p=address-base; assert b[p:b.index(0,p)].decode()==value
c['raw_jal_targets_checked']={hex(k):hex(v) for k,v in calls.items()}
c['rom_strings_checked']={hex(k):v for k,v in strings.items()}
(O/'contract.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('18 ordinary JAL and 19 strings checked')
