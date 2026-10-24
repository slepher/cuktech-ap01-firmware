"""Q-10: read-only retained assembly/ROM checks; no firmware execution."""
import hashlib, json
from pathlib import Path
ROOT = Path("D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware")
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
source = ROOT / "reverse/analysis/buzzer-backlight-0041-20261023.json"
f = json.loads(source.read_text(encoding="utf-8"))["functions"][6]
assert f["address"] == "0xa005a736"
assert f["evidence_id"] == "ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3"
rom = (ROOT / "roms/0041/ap01-1.0.2_0041.bin").read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == "972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9"
ranges = [(0xa005ac8c,0xa005ac94),(0xa005acde,0xa005ace2),(0xa005ad02,0xa005ad06),(0xa005ae7c,0xa005aec8),(0xa005b8a4,0xa005b9ae)]
def data(a,n): return rom[a-BASE:a-BASE+n]
def retained(a,n):
    for r in f["raw_ranges"]:
        start=int(r["start"],16); b=bytes.fromhex(r["hex"])
        if start <= a and a+n <= start+len(b): return b[a-start:a-start+n]
    raise AssertionError(hex(a))
windows=[]
for lo,hi in ranges:
    b=data(lo,hi-lo); assert b == retained(lo,hi-lo)
    windows.append(dict(start=hex(lo),end_exclusive=hex(hi),file_offset=lo-BASE,length=len(b),hex=b.hex(),assembly=[s for s in f["assembly"] if lo<=int(s.split(":")[0],16)<hi]))
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
def word(a): return int.from_bytes(data(a,4),"little")
def jal(a):
    w=word(a); assert w&127==0x6f
    return a+sx(((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1),21)
def branch(a):
    w=word(a); assert w&127==0x63
    return a+sx(((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1),13)
assert branch(0xa005ae96)==0xa005b8a4
assert branch(0xa005b90c)==0xa005b990
for a in [0xa005ae90,0xa005b8be,0xa005b8d6,0xa005b8ee,0xa005b906]: assert jal(a)==0xa0060946
for a in [0xa005aec4,0xa005b944]: assert jal(a)==0xa0061848
assert sx(word(0xa005b92c)>>20,12)==0x6a0
assert (0x18<<12)+0x6a0==100000
assert word(0xa005b930)==0x0cfA2023 # sw a5,0xc0(s4)
assert word(0xa005b988)==0xfee78623 # sb a4,-0x14(a5)
keys={0xa01c3068:"ck_config",0xa01c322c:"bind_flag",0xa01c3250:"loc_province",0xa01c3260:"loc_city",0xa01c326c:"loc_district",0xa01c327c:"loc_id"}
for a,s in keys.items(): assert data(a,len(s)+1)==s.encode()+b"\0"
old=json.loads((ROOT/"reverse/analysis/weather-location-request-0041-20261023/retained-functions.json").read_text(encoding="utf-8"))
inherited=[]
for g in old["functions"]:
    if g["address"] not in ["0xa00a0906","0xa00aab1c"]: continue
    inherited.append(dict(address=g["address"],evidence_id=g["evidence_id"],scope="inherited getter/URL, no new body analysis"))
result=dict(claim="Q-10",identity="0041",evidence_id=f["evidence_id"],source=str(source),json_pointer="/functions/6",windows=windows,keys={hex(a):s for a,s in keys.items()},inherited=inherited,checks="PASS: ROM identity, selected raw byte equality, 7 direct-call targets, 2 branches, numeric default, stores and 6 ROM keys",limits=["No config backend inspection or execution", "Text read returns ignored here; NUL guarantees unknown", "Configuration write call does not prove durable success"])
OUT.joinpath("evidence.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(result["checks"])
print("selected startup bytes:",sum(hi-lo for lo,hi in ranges))
