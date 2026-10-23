"""D21: selected local candidate lines and sparse existing ROM anchors only."""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parents[1]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
base = 0x9ffff000
prior = json.loads((REV / 'analysis/backlight-animation-d19-0041-20261024/instruction-windows.json').read_text())
# Only the already recorded local contracts needed for this source comparison.
names = {'exec-byte-argument', 'exec-style-binding', 'init-clear-and-defaults',
         'start-copy-96', 'start-immediate-dispatch', 'tick-completion',
         'tick-repeat', 'query-identity', 'delete-identity', 'delete-node'}
checked = []
for w in prior:
    if w['name'] not in names:
        continue
    a, b = int(w['start'], 16), int(w['end_exclusive'], 16)
    assert rom[a-base:b-base].hex() == w['hex']
    checked.append(w['name'])
assert len(checked) == len(names)
assert rom[0xa018fb46-base:0xa018fb4e-base].hex() == 'b70602009305e003'
assert rom[0xa008c044-base:0xa008c04a-base].hex() == '9c5026858297'
assert rom[0xa008df72-base:0xa008df76-base].hex() == '93e70701'

remote = r'''import json, zipfile
from pathlib import Path
r=Path('/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl')
selected={
 'src/misc/lv_style.h':[(257,260)],
 'src/core/lv_obj.h':[(45,48),(70,78)],
 'src/core/lv_obj_style.h':[(35,35),(41,45)],
 'src/core/lv_obj_style_gen.c':[(485,491)],
 'src/misc/lv_color.h':[(39,54)],
 'src/misc/lv_anim.h':[(26,27),(88,113),(123,154)],
 'src/misc/lv_anim.c':[(75,83),(90,120),(145,165),(174,183),(570,595),(701,706)]}
out=[]
with zipfile.ZipFile(r.parent/'v9.2.1.zip') as z:
 for f,ranges in selected.items():
  data=(r/f).read_bytes()
  match=data==z.read('lvgl-9.2.1/'+f)
  assert match,f
  lines=data.decode().splitlines()
  out.append({'path':str(r/f),'local_zip_member_equal':match,
              'excerpts':[{'first':a,'last':b,'lines':[str(i+1)+': '+lines[i] for i in range(a-1,b)]} for a,b in ranges]})
print(json.dumps(out))
'''
p = subprocess.run(['wsl.exe', '-d', 'Ubuntu-24.04', '--exec', 'python3', '-c', remote], capture_output=True)
assert p.returncode == 0, p.stdout.decode(errors='replace') + p.stderr.decode(errors='replace')
sources = json.loads(p.stdout)
text = '\n'.join(line for s in sources for ex in s['excerpts'] for line in ex['lines'])
for expected in ['LV_STYLE_SHADOW_OPA             = 62', 'LV_PART_INDICATOR    = 0x020000',
                 'LV_STATE_DEFAULT     =  0x0000', 'LV_ANIM_REPEAT_INFINITE      0xFFFFFFFF',
                 'new_anim->exec_cb(new_anim->var, new_anim->start_value);',
                 'if(anim->deleted_cb != NULL) anim->deleted_cb(anim);']:
    assert expected in text

(HERE / 'candidate-excerpts.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
result = {'passed': True, 'existing_rom_windows_compared': checked,
          'selected_candidate_files': len(sources), 'local_zip_equal_members': len(sources),
          'source_identity': 'F07/F08 identity limits inherited; local member equality only',
          'property': {'rom_number': '0x3e', 'candidate_name': 'LV_STYLE_SHADOW_OPA',
                       'selector': '0x20000 = LV_PART_INDICATOR | LV_STATE_DEFAULT',
                       'status': 'local wrapper/enum match supports semantic identification; exact ROM version unknown'},
          'animation_matches': ['RV32 first nine pointer/callback slots +0..+0x20',
                                'values/time/repeat slots +0x24..+0x44',
                                'init defaults; copy-and-self-var adjustment',
                                'get/delete identity pair; remove -> deleted_cb -> free',
                                'finite completion -> completed_cb -> deleted_cb -> free; infinite sentinel'],
          'animation_differences': ['ROM copies 96B; ordinary RV32 candidate declaration yields 88B',
                                    'ROM early_apply byte +0x5c bit4; ordinary RV32 candidate flags +0x54 and fourth declared bit',
                                    'ROM start invokes path(node) before exec; candidate start passes start_value directly',
                                    'ROM repeat reset retains positive elapsed excess; candidate resets to negative repeat_delay'],
          'unknown': ['exact ROM source/version/config', 'rendering visibility and target widget class',
                      'all page DELETE/context release paths', 'query traversal vendor word a00891b2'],
          'new_rom_functionality': 0, 'whole_library_exclusions': 0, 'shared_rea_target': False}
(HERE / 'static-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'passed': True, 'rom_windows':len(checked), 'candidate_members_equal':len(sources), 'new_rom_functionality':0}))
