"""C23 static source/contract comparison; no formatter or firmware execution."""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parents[1]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
old = json.loads((REV / 'analysis/text-update-entry-review-c14-0041-20261023/review-evidence.json').read_text())
compared = 0
for window in old['windows']:
    # Compare retained byte strings without another function export.
    for item in window['instructions']:
        pc = int(item['pc'], 16)
        raw = bytes.fromhex(item['raw'])
        assert rom[pc-BASE:pc-BASE+len(raw)] == raw
        compared += 1

remote = r'''import json, zipfile
from pathlib import Path
r=Path('/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl')
selected={'src/widgets/label/lv_label.c':[(178,204)],
          'src/widgets/label/lv_label_private.h':[(31,56)],
          'src/misc/lv_text.c':[(409,448)],
          'src/core/lv_obj_private.h':[(49,73)]}
out=[]
with zipfile.ZipFile(r.parent/'v9.2.1.zip') as z:
 for rel,ranges in selected.items():
  raw=(r/rel).read_bytes()
  equal=raw==z.read('lvgl-9.2.1/'+rel)
  assert equal,rel
  lines=raw.decode().splitlines()
  out.append({'path':str(r/rel),'local_zip_member_equal':equal,
              'excerpts':[{'first':a,'last':b,'lines':[str(i+1)+': '+lines[i] for i in range(a-1,b)]} for a,b in ranges]})
print(json.dumps(out))
'''
p = subprocess.run(['wsl.exe', '-d', 'Ubuntu-24.04', '--exec', 'python3', '-c', remote], capture_output=True)
assert p.returncode == 0, p.stdout.decode(errors='replace')+p.stderr.decode(errors='replace')
sources = json.loads(p.stdout)
text = '\n'.join(line for s in sources for ex in s['excerpts'] for line in ex['lines'])
for literal in ['if(label->text != NULL && label->static_txt == 0)',
                'label->text = lv_text_set_text_vfmt(fmt, args);',
                'label->static_txt = 0;', 'va_copy(ap_copy, ap);',
                'uint32_t len = lv_vsnprintf(NULL, 0, fmt, ap_copy);',
                'lv_vsnprintf(text, len + 1, fmt, ap);',
                'lv_label_long_mode_t long_mode : 3;', 'uint8_t static_txt : 1;']:
    assert literal in text

# Bounded source overlap check in later local reports, not a new ROM search.
later = ['text-precondition-c15-0041-20261023.md',
         'text-precondition-review-c16-0041-20261023.md',
         'invalidation-gates-review-c18-0041-20261023.md',
         'region-gating-review-c22-0041-20261023.md',
         'display-source-auth-f07-0041-20261023.md',
         'display-source-review-f08-0041-20261023.md']
for name in later:
    content = (REV / 'reports/ap01' / name).read_text(encoding='utf-8')
    assert 'lv_text_set_text_vfmt' not in content

(HERE / 'candidate-excerpts.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
result = {'passed': True, 'existing_c14_instructions_match_original': compared,
          'local_source_zip_members_equal': len(sources),
          'later_source_overlap_scope': later,
          'normal_source_matches': ['free old non-static text before allocation',
                                    'format length then allocate len+1 then second format',
                                    'return allocated buffer; label retains it and clears static flag',
                                    'invalidate before mutation, refresh after storage'],
          'limits_or_differences': ['ROM static flag is byte+0x5c mask0x10; candidate declares three long_mode bits then static_txt; exact bitfield ABI not certified',
                                   'candidate lv_obj and label layouts have config-dependent fields; ROM config not certified',
                                   'ROM normal single-buffer branch matches non-Arabic candidate shape, not all source configurations',
                                   'candidate copies va_list for first pass; same ROM argument address alone does not certify backend advancement or all format semantics',
                                   'candidate null-fmt refresh and allocation-failure returns are outside accepted normal non-null domain'],
          'inherited_followup': 'a00dddf4/a00ddbf6 already covered by C15-C22/G01-G04; do not reopen',
          'unknown': ['exact ROM source/version/config', 'full label layout and field ABI',
                      'formatter/allocator internals and complete text lifecycle'],
          'new_rom_functionality': 0, 'whole_library_exclusions': 0, 'shared_rea_target': False}
(HERE / 'static-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'passed': True, 'retained_instruction_bytes_compared': compared, 'source_members_equal': len(sources), 'new_rom_functionality': 0}))
