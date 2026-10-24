from pathlib import Path
import hashlib,json,struct
out=Path(__file__).parent
r=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
addrs=[0xa0564af0,0xa02669d0,0xa06189f0,0xa05652e8,0xa02676c0,0xa0564b30,0xa0564b44,0xa0564b5c,0xa0565324,0xa0565334,0xa0565350,0xa056537c,0xa05653a8,0xa05653cc,0xa05653e0,0xa05652f8,0xa0565310,0xa056c058,0xa01c2488]
def st(a):return r[a-0x9ffff000:].split(b'\0',1)[0].decode('ascii')
data={'strings':{hex(a):st(a) for a in addrs},'dispatch':[]}
for a in range(0xa066dbdc,0xa066dce0,20):
 v=struct.unpack_from('<5I',r,a-0x9ffff000)
 data['dispatch'].append({'va':hex(a),'words':[hex(x) for x in v],'method':st(v[0])})
(out/'referenced-data.json').write_text(json.dumps(data,indent=2)+'\n')
w=json.loads((out/'windows.json').read_text())
c={'claim':'Q-30','baseline':'5f50102e56012e2e1e0fa8f9d8010d3c8e8214fd','rom_sha256':hashlib.sha256(r).hexdigest(),'rom_length':len(r),'mapping':'offset=VA-0x9ffff000','windows':[{k:v for k,v in x.items() if k!='hex'} for x in w],'new_body_bytes':sum(x['length'] for x in w),'undecoded_instructions':[],'stopped_apis':['0xa011f43e','0xa01a5268','0xa01990c8','0xa0060cac','0xa0061d20','0xa01b38b6','0xa018fd68','0xa00b5636','0xa00b55e2'],'callback_installs':{'json':{'result':'0xa00bda7c','error':'0xa00bd910'},'text_default':{'result':'0xa00bd938','error':'0xa00bd7fa'}},'artifacts':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'windows.json',out/'disassembly.txt',out/'referenced-data.json']}}
assert c['new_body_bytes']==1610
(out/'contract.json').write_text(json.dumps(c,indent=2)+'\n')
print(json.dumps(c,indent=2))
