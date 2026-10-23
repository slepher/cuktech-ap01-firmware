"""A48 independent normal-path sparse ROM checks. No target/model execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
rows, calls, edges = [], [], []

def read(pc, n):
    with ROM.open('rb') as stream:
        stream.seek(pc - BASE)
        data = stream.read(n)
    assert len(data) == n
    return data

def sx(x, n):
    return x - (1 << n) if x & (1 << (n - 1)) else x

def anchor(pc, raw):
    data = read(pc, len(bytes.fromhex(raw)))
    assert data.hex() == raw, hex(pc)
    ins = next(cs.disasm(data, pc), None)
    assert ins is not None and ins.size == len(data)
    rows.append(dict(pc=hex(pc), raw=raw, instruction=ins.mnemonic+' '+ins.op_str))
    return int.from_bytes(data, 'little')

# Two inherited slots only; no re-export of the ten-word table.
slots = []
for off, want in [(0x18,0xa00ebf7c),(0x1c,0xa00ec084)]:
    assert int.from_bytes(read(0xa0263afc+off,4),'little') == want
    slots.append(dict(table='0xa0263afc', offset=hex(off), target=hex(want)))

# Sparse argument/ownership/ordering anchors, rather than complete functions.
for pc, raw in [
    (0xa00890f6,'b794fc62'),(0xa00890fa,'9384c457'),(0xa0089104,'4e85'),
    (0xa019cfac,'1c41'),(0xa019cfae,'8145'),(0xa019cfb0,'dc4f'),(0xa019cfb2,'8297'),
    (0xa00ec00c,'930a4502'),(0xa00ec010,'aa84'),(0xa00ec012,'5685'),
    (0xa00ec028,'9c4c'),(0xa00ec02a,'4a85'),(0xa00ec02c,'b285'),(0xa00ec02e,'8297'),
    (0xa00ec030,'dc5c'),(0xa00ec032,'4a85'),(0xa00ec034,'8297'),
    (0xa00ec036,'dc44'),(0xa00ec038,'898f'),(0xa00ec03a,'dcc4'),(0xa00ec03c,'dc40'),
    (0xa00ec046,'d854'),(0xa00ec048,'3e99'),(0xa00ec04e,'ce85'),(0xa00ec050,'5685'),
    (0xa00ec052,'ba97'),(0xa00ec05c,'4a85'),(0xa00ec062,'13850403'),
    (0xa00ec066,'d285'),(0xa00ec06c,'5285'),
    (0xa00ec0e4,'aa84'),(0xa00ec0e6,'ae8a'),(0xa00ec0e8,'130a0503'),(0xa00ec0ec,'8149'),
    (0xa00ec12a,'4e89'),(0xa00ec134,'5285'),(0xa00ec160,'dc40'),
    (0xa00ec16a,'e697'),(0xa00ec16c,'3e85'),(0xa00ec17c,'9c4c'),
    (0xa00ec17e,'d685'),(0xa00ec180,'6685'),(0xa00ec182,'8297'),
    (0xa00ec184,'9c58'),(0xa00ec186,'3e99'),(0xa00ec1a6,'8509'),
    (0xa00ec1d4,'4a85'),(0xa00ec1e2,'3e89'),(0xa008ae4a,'8145'),
    (0xa008ae04,'4441'),(0xa008ae06,'2a89'),(0xa008ae08,'ae89'),
    (0xa008ae20,'a697'),(0xa008ae2a,'4a85'),(0xa008ae2c,'a685'),
    (0xa008ae32,'2685'),(0xa008ae38,'d284')]:
    anchor(pc,raw)

# Independent standard word load/store field extraction.
memory = []
for pc, raw, expected in [
    (0xa00890fe,'83a90412',('load',19,9,0x120)),
    (0xa008910e,'03a5c411',('load',10,9,0x11c)),
    (0xa00ec014,'232ec4fc',('store',12,8,-36)),
    (0xa00ec020,'03290501',('load',18,10,0x10)),
    (0xa00ec024,'0326c4fd',('load',12,8,-36)),
    (0xa00ec04a,'83a70901',('load',15,19,0x10)),
    (0xa00ec054,'03aac7ff',('load',20,15,-4)),
    (0xa00ec0e0,'03294503',('load',18,10,0x34)),
    (0xa00ec126,'83a94402',('load',19,9,0x24)),
    (0xa00ec130,'23a20402',('store',0,9,0x24)),
    (0xa00ec13a,'23a60400',('store',0,9,0xc)),
    (0xa00ec158,'83270900',('load',15,18,0)),
    (0xa00ec15c,'83ac0701',('load',25,15,0x10)),
    (0xa00ec188,'03294900',('load',18,18,4)),
    (0xa00ec1aa,'83274900',('load',15,18,4)),
    (0xa00ec1b0,'83298900',('load',19,18,8)),
    (0xa00ec1b8,'83290900',('load',19,18,0)),
    (0xa00ec1c0,'83a74900',('load',15,19,4)),
    (0xa00ec1c8,'23a20900',('store',0,19,4)),
    (0xa00ec1cc,'03250901',('load',10,18,0x10)),
    (0xa00ec1dc,'23a40900',('store',0,19,8)),
    (0xa008ae1c,'83270900',('load',15,18,0)),
    (0xa008ae22,'03aa4700',('load',20,15,4))]:
    w = anchor(pc,raw)
    assert (w >> 12) & 7 == 2
    if w & 127 == 3:
        got = ('load',(w >> 7) & 31,(w >> 15) & 31,sx(w >> 20,12))
    else:
        assert w & 127 == 0x23
        got = ('store',(w >> 20) & 31,(w >> 15) & 31,sx(((w >> 25) << 5) | ((w >> 7) & 31),12))
    assert got == expected, (hex(pc),got,expected)
    memory.append(dict(pc=hex(pc), operation=got[0], value_register=got[1], base_register=got[2], offset=got[3]))

for pc, want in [(0xa0089106,0xa019cf58),(0xa0089112,0xa019cf58),
    (0xa00ec018,0xa00ea832),(0xa00ec058,0xa00ea9a6),(0xa00ec05e,0xa008b6a6),
    (0xa00ec068,0xa0089d02),(0xa00ec06e,0xa008ab8a),(0xa00ec172,0xa008b604),
    (0xa00ec1a2,0xa008b51a),(0xa00ec122,0xa008b51a),
    (0xa00ec1d0,0xa008ab8a),(0xa00ec1d6,0xa008ab8a),(0xa00ec136,0xa008ae42),
    (0xa008ae4c,0xa008adf4),(0xa008ae2e,0xa0089d02),(0xa008ae34,0xa008ab8a)]:
    data = read(pc,4)
    w = int.from_bytes(data,'little')
    if w & 127 == 0x6f:
        assert (w >> 7) & 31 == 1
        imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
        target = (pc + sx(imm,21)) & 0xffffffff
    else:
        data += read(pc+4,4)
        q = int.from_bytes(data[4:],'little')
        assert w & 0xfff == 0x97 and q & 0xfffff == 0x80e7
        target = (pc + sx(w & 0xfffff000,32) + sx(q >> 20,12)) & 0xfffffffe
    assert target == want,(hex(pc),hex(target))
    calls.append(dict(pc=hex(pc),raw=data.hex(),target=hex(target)))

# Direct control edges: nonzero ref warning rejoins traversal; empty traversal
# with/without warnings joins the SAME tree cleanup, then root/list/used reset.
for pc, raw, want in [
    (0xa0089102,'1de1',0xa0089128),(0xa00ec01e,'31c9',0xa00ec072),
    (0xa00ec0fa,'631f0904',0xa00ec158),(0xa00ec0fe,'63840902',0xa00ec126),
    (0xa00ec12c,'631f0906',0xa00ec1aa),(0xa00ec17a,'11e9',0xa00ec18e),
    (0xa00ec18c,'bdb7',0xa00ec0fa),(0xa00ec1a8,'f1bf',0xa00ec184),
    (0xa00ec1ae,'95eb',0xa00ec1e2),(0xa00ec1b4,'e39b09f6',0xa00ec12a),
    (0xa00ec1bc,'63880900',0xa00ec1cc),(0xa00ec1c4,'631cf900',0xa00ec1dc),
    (0xa00ec1da,'81bf',0xa00ec12a),(0xa00ec1e0,'f5b7',0xa00ec1cc),
    (0xa00ec1e4,'a1b7',0xa00ec12c),(0xa008ae26,'639b0900',0xa008ae3c),
    (0xa008ae3a,'c1bf',0xa008ae0a)]:
    w = anchor(pc,raw)
    if len(bytes.fromhex(raw)) == 4:
        assert w & 127 == 0x63
        imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
        target = pc + sx(imm,13)
    elif w >> 13 in (6,7):
        imm = (((w >> 12) & 1) << 8) | (((w >> 10) & 3) << 3) | (((w >> 5) & 3) << 6) | (((w >> 3) & 3) << 1) | (((w >> 2) & 1) << 5)
        target = pc + sx(imm,9)
    else:
        assert w >> 13 == 5
        imm = (((w >> 12) & 1) << 11) | (((w >> 11) & 1) << 4) | (((w >> 9) & 3) << 8) | (((w >> 8) & 1) << 10) | (((w >> 7) & 1) << 6) | (((w >> 6) & 1) << 7) | (((w >> 3) & 7) << 1) | (((w >> 2) & 1) << 5)
        target = pc + sx(imm,12)
    assert target == want,(hex(pc),hex(target),hex(want))
    edges.append(dict(pc=hex(pc),target=hex(target)))

result = dict(task='A48', result='PASS', slots=slots, sparse_instructions=rows,
              memory_fields=memory, call_targets=calls, control_edges=edges,
              limits=['No target/model execution or new REA session.',
                      'A27/A34/A38 helpers and image payload ownership inherited; no source identity authentication.',
                      'Normal valid-object paths only; no application-time ref preconditions or runtime occurrence established.'])
(HERE/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS: {len(rows)} sparse instructions, {len(calls)} call targets, {len(edges)} control edges, 2 inherited slots.')
