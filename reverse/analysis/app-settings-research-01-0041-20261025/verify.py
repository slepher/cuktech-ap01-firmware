"""Static source-byte and retained-evidence checks; does not execute target code."""
import hashlib,json
from pathlib import Path
ROOT=Path(r"D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware")
OUT=Path(__file__).parent
rom=(ROOT/"roms/0041/ap01-1.0.2_0041.bin").read_bytes()
assert len(rom)==6769704
assert hashlib.sha256(rom).hexdigest()=="972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9"
records=[]
def raw(a,h):
 b=bytes.fromhex(h);assert rom[a-0x9ffff000:a-0x9ffff000+len(b)]==b
 records.append({"address":hex(a),"bytes":h});return int.from_bytes(b,"little")
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def inst(a,h,op,rd=None,f3=None,rs1=None,rs2=None,imm=None):
 x=raw(a,h);assert x&127==op
 for actual,expected in [(x>>7&31,rd),(x>>12&7,f3),(x>>15&31,rs1),(x>>20&31,rs2)]:
  if expected is not None:assert actual==expected
 if imm is not None:
  v=(x>>25<<5 | x>>7&31) if op==0x23 else x>>20
  assert sx(v,12)==imm
 return x
def jal(a,h,target):
 x=inst(a,h,0x6f,rd=1);i=((x>>31)<<20)|((x>>12&255)<<12)|((x>>20&1)<<11)|((x>>21&1023)<<1)
 assert (a+sx(i,21))&0xffffffff==target
def branch(a,h,f3,r1,r2,target):
 x=inst(a,h,0x63,f3=f3,rs1=r1,rs2=r2);i=(x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1
 assert a+sx(i,13)==target
# Registration head and callback argument formation.
assert raw(0xa00ab2fa,"b7b7fc62")>>12==0x62fcb
inst(0xa00ab302,"9387c74e",0x13,15,0,15,imm=0x4ec)
raw(0xa00ab306,"2147");inst(0xa00ab310,"23a20700",0x23,f3=2,rs1=15,rs2=0,imm=4)
inst(0xa00ab314,"23a40700",0x23,f3=2,rs1=15,rs2=0,imm=8);raw(0xa00ab318,"98c3")
assert raw(0xa00ab2fe,"37450aa0")>>12==0xa00a4
inst(0xa00ab30c,"1305450c",0x13,10,0,10,imm=0xc4)
inst(0xa00ab308,"93054006",0x13,11,0,0,imm=100)
x=raw(0xa00ab31a,"97701000");y=inst(0xa00ab31e,"e780a015",0x67,1,0,1,imm=0x15a)
assert 0xa00ab31a+(x&0xfffff000)+sx(y>>20,12)==0xa01b2474
# Reader handle, exact read args and return overwrite.
jal(0xa00ab332,"ef904852",0xa0134856);raw(0xa00ab336,"2a8a")
branch(0xa00ab348,"63080a0c",0,20,0,0xa00ab418)
raw(0xa00ab34c,"d286");raw(0xa00ab34e,"0546");raw(0xa00ab350,"a145")
inst(0xa00ab352,"13058509",0x13,10,0,10,imm=0x98)
jal(0xa00ab356,"ef706877",0xa0132acc);jal(0xa00ab35a,"ef90efb8",0xa00a46e8)
inst(0xa00ab35e,"03d86400",3,16,5,9,imm=6)
raw(0xa00ab362,"aa87");branch(0xa00ab364,"631b0509",1,10,16,0xa00ab3fa)
raw(0xa00ab382,"854a");raw(0xa00ab384,"5285");jal(0xa00ab386,"efd01f26",0xa01a8de6)
branch(0xa00ab38a,"63930a02",1,21,0,0xa00ab3b0)
raw(0xa00ab414,"814a");raw(0xa00ab416,"bdb7");raw(0xa00ab432,"b1bf")
jal(0xa00ab3a8,"ef80efee",0xa00a3a96);jal(0xa00ab3ac,"eff09fec",0xa00ab274)
# Entire newly necessary default helper, not an emulation.
raw(0xa00a3a96,"411122c60008b797fc6223ac070813074016938787092392e700324441018280")
inst(0xa00a3aa0,"23ac0708",0x23,f3=2,rs1=15,rs2=0,imm=0x98)
inst(0xa00a3aa4,"13074016",0x13,14,0,0,imm=0x164)
inst(0xa00a3aa8,"93878709",0x13,15,0,15,imm=0x98)
inst(0xa00a3aac,"2392e700",0x23,f3=1,rs1=15,rs2=14,imm=4)
for a,s in [(0xa026a218,b"wb"),(0xa026a21c,b"/data/sysconfig.bin"),(0xa026a258,b"rb")]:
 assert rom[a-0x9ffff000:a-0x9ffff000+len(s)+1]==s+b"\0"
retained=[]
for stem,eid,entry,size in [("072","ev_85099f331255aab9e146bc35df48bcdbe3e38160b9802c06864c877f036f7d00","0xa00ab2e8",332),("071","ev_cf4c97ae60f1edbe9156a19d0427799c7c068d79ed1d916e7d8cdc3dd61c3c58","0xa00ab274",116)]:
 p=ROOT/f"evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{stem}.json"
 j=json.loads(p.read_text(encoding="utf-8"));n=j["structuredContent"]["normalized_result"];c=json.loads(j["content"][0]["text"])
 assert c["evidence_id"]==eid and n["procedure"]["address"]==entry and n["procedure"]["body"]["total_bytes"]==size
 retained.append({"path":str(p),"evidence_id":eid,"entry":entry,"size":size})
result={"status":"PASS","rom_sha256":hashlib.sha256(rom).hexdigest(),"raw_records":records,"retained":retained,"target_execution":False,"algorithm_evaluations":0}
(OUT/"result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("PASS",len(records),"source-byte records; 2 retained evidence identities; no target execution")
