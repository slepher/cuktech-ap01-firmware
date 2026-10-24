"""Read-only sparse ROM/retained audit; no firmware/model execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
rom = (MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
base = 0x9ffff000
coverage = json.loads((MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
f = next(x for x in coverage['functions'] if x['address'] == '0xa00abbf6')
assert f['extent']['body']['total_bytes'] == 422
assert f['extent']['body']['ranges'] == [{'start':'0xa00abbf6','end':'0xa00abd9b'}]
assert not f['dossiers'] and not f['source_paths'] and not f['historical_contracts']
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
# Branch gates, output argument and reload slices only, not a full-function export.
spans = [(0xabbfe,0xabc22),(0xabc26,0xabc44),(0xabc44,0xabc6a),
         (0xabc8e,0xabcac),(0xabcbc,0xabcda),(0xabcda,0xabcf8),
         (0xabd00,0xabd1c),(0xabd1c,0xabd34),(0xabd34,0xabd9c)]
rows=[]
for lo,hi in spans:
    lo += 0xa0000000
    hi += 0xa0000000
    data=rom[lo-base:hi-base]
    ins=list(cs.disasm(data,lo))
    assert sum(x.size for x in ins)==len(data)
    for i in ins:
        row={'address':hex(i.address),'bytes':i.bytes.hex(),'assembly':i.mnemonic+' '+i.op_str}
        if i.mnemonic in ('jal','bne','beq','bnez','c.bnez','c.j'):
            row['direct_target']=hex(i.address+int(i.op_str.split(',')[-1],0))
        rows.append(row)
by={x['address']:x for x in rows}
# General-input gates use a positive immediate: high 24 bits are masked away.
for at,raw in ((0xabc00,'13f7d50f'),(0xabd36,'93f5d50f')):
    word=int.from_bytes(bytes.fromhex(by[hex(0xa0000000+at)]['bytes']),'little')
    assert by[hex(0xa0000000+at)]['bytes']==raw
    assert word>>20 == 0xfd  # imm[11]=0, sign extension is 0x000000fd.
targets={0xabc08:0xabd34,0xabc0c:0xabc5c,0xabc1c:0xabcf8,
         0xabc30:0xa5e8e,0xabc40:0xd92ec,0xabca8:0xdfb70,
         0xabcc6:0xa5e8e,0xabcd6:0xd92ec,0xabcf6:0xabca8,
         0xabd08:0xa5e8e,0xabd18:0xd92ec,0xabd32:0xabcf4,
         0xabd3a:0xabcac,0xabd3c:0xabd54,0xabd42:0xabd8c,
         0xabd48:0xd9044,0xabd56:0xabd74,0xabd5c:0xd8f7c,
         0xabd6e:0xdbb68,0xabd78:0xd8f7c,0xabd90:0xd9044}
for at,to in targets.items():
    assert by[hex(0xa0000000+at)]['direct_target']==hex(0xa0000000+to)
resources={}
for a in (0xa0242574,0xa0242808):
    resources[hex(a)]=rom[a-base:a-base+24].hex()
assert resources['0xa0242574']=='19010000000000000000000077020000902524a000000000'
assert resources['0xa0242808']=='1901000000000000000000000e010000242824a000000000'
extra={hex(a):rom[a-base:a-base+4].hex() for a in (0xa00a5eb0,0xa00a5eb4)}
assert extra=={'0xa00a5eb0':'8b37853c','0xa00a5eb4':'0b35055d'}
result={'status':'PASS','rom_identity':'roms/CATALOG.md / 0041',
        'mode_gates':{'image':'(mode & 0x000000fd) == 1',
                      'flag_layout_after_image_false':'((mode - 2) & 0x000000fd) == 0',
                      'arithmetic':'RV32 modulo 2^32; masks are local operations, not a global u8 ABI',
                      'actual_p11_domain':'1/3 image; 2/4 flag_layout; action tables unchanged'},
        'inventory':f,'decoder':'local Capstone RV32+C, standard instructions only',
        'selected_instructions':rows,'resource_headers':resources,
        'opaque_color_adapter_custom_words':extra,
        'limitations':['No REA session/model execution; retained inventory is not a decompilation.',
                      'Not a whole-function export or formal control-flow/dataflow proof.',
                      'Resource headers do not prove image decoding/display or content identity.',
                      'Color adapter and public GUI internals remain inherited/opaque boundaries.']}
(HERE/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
checks={'status':'PASS','spans':len(spans),'bytes':sum(len(bytes.fromhex(x['bytes'])) for x in rows),
        'instructions':len(rows),'branch_call_targets':len(targets),'resource_headers':2,
        'new_function_decompilations':0,'new_target_executions':0}
(HERE/'checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf8')
print(checks)
