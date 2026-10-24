"""Independent static ROM checks for Q14; no author code is executed."""
from pathlib import Path
import hashlib,json
ROOT=Path("D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware")
OUT=Path(__file__).parent
rom=(ROOT/"roms/0041/ap01-1.0.2_0041.bin").read_bytes()
assert len(rom)==6769704
assert hashlib.sha256(rom).hexdigest()=="972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9"
f=json.loads((ROOT/"reverse/analysis/uart-response-0041-20261023.json").read_text(encoding="utf-8"))["functions"][0]
assert f["evidence_id"]=="ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c"
assert f["profile_digest"]=="bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279"
base=0x9ffff000
def read(a,n=4): return rom[a-base:a-base+n]
def word(a): return int.from_bytes(read(a),"little")
r=f["raw_ranges"][0]; raw=bytes.fromhex(r["hex"])
assert read(int(r["start"],16),len(raw))==raw
assert hashlib.sha256(raw).hexdigest()==r["sha256"]
rows=[]; asm=f["normalized_result"]["assembly"]
for n,line in enumerate(asm):
 a=int(line.split(":")[0],16)
 if 0xa00a874e<=a<0xa00a875a or 0xa00a973e<=a<0xa00a983e:
  end=int(asm[n+1].split(":")[0],16); b=read(a,end-a)
  assert end-a==(4 if b[0]&3==3 else 2)
  rows.append({"va":hex(a),"offset":a-base,"hex":b.hex(),"assembly":line})
assert len(rows)==74
indexed=[]
for a,expect in [(0xa00a97bc,(11,4,16,16,18,23,3)),(0xa00a97f4,(11,4,16,16,25,23,3)),(0xa00a9828,(11,5,8,17,22,21,0))]:
 w=word(a); got=(w&127,w>>12&7,w>>27,w>>7&31,w>>15&31,w>>20&31,w>>25&3)
 assert got==expect
 indexed.append({"va":hex(a),"word":hex(w),"fields":got})
for a,imm in [(0xa00a97ce,20),(0xa00a9800,21)]:
 w=word(a)
 assert (w&127,w>>12&7,w>>15&31,w>>20&31,(w>>25)*32+(w>>7&31))==(35,0,6,16,imm)
calls=[]
for a,t in [(0xa00a975c,0xa0191652),(0xa00a9792,0xa0191746),(0xa00a9830,0xa00a389c),(0xa00a8756,0xa00a973e)]:
 w=word(a); delta=(w>>31)*1048576+(w>>12&255)*4096+(w>>20&1)*2048+(w>>21&1023)*2
 if delta&1048576: delta-=2097152
 assert w&127==111 and a+delta==t
 assert (w>>7&31)==(0 if a==0xa00a8756 else 1)
 calls.append({"va":hex(a),"target":hex(t)})
# Critical expression and pointer reload instructions checked as exact original words.
for a,h in {0xa00a9742:"83c5c701",0xa00a974e:"03250900",0xa00a9752:"8e05",0xa00a9758:"93f5850f",0xa00a976a:"03290900",0xa00a9786:"03a7c42c",0xa00a978a:"83466700",0xa00a97b8:"032b0700",0xa00a982c:"13f5fb0f"}.items():
 assert read(a,len(bytes.fromhex(h)))==bytes.fromhex(h),(hex(a),read(a).hex())
result={"evidence_id":f["evidence_id"],"profile_digest":f["profile_digest"],"full_raw_match":True,"boundaries":rows,"indexed":indexed,"jal":calls}
(OUT/"instruction-evidence.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("PASS: ROM, retained raw, 74 boundaries, 3 indexed, 2 SB, 3 JAL plus dispatch, critical original words")
