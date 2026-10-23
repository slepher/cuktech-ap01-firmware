"""C26: live selected-source comparison; ROM behavior is inherited from G01/G02."""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parents[1]
prior = json.loads((REV / 'analysis/region-transform-source-c25-0041-20261024/candidate-excerpts.json').read_text(encoding='utf-8'))
expected = {item['path']:{str(row['line']):row['text'] for row in item['lines']} for item in prior['excerpts']}
selection = [{'path':item['path'],'ranges':item['ranges']} for item in prior['excerpts']]
assert len(selection) == 11 and sum(len(lines) for lines in expected.values()) == 271

# Read only retained ranges, compare in memory, do not duplicate source excerpts.
remote = '''import json
from pathlib import Path
selection = ''' + repr(selection) + '''
out={}
for item in selection:
 lines=Path(item['path']).read_text().splitlines()
 out[item['path']]={str(i):lines[i-1] for first,last in item['ranges'] for i in range(first,last+1)}
print(json.dumps(out))
'''
p=subprocess.run(['wsl.exe','-d','Ubuntu-24.04','--exec','python3','-c',remote],capture_output=True)
assert p.returncode == 0, p.stdout.decode(errors='replace')+p.stderr.decode(errors='replace')
current=json.loads(p.stdout)
assert current == expected
src={path.split('/lvgl/lvgl/')[1]:'\n'.join(lines.values()) for path,lines in current.items()}
checks=[]

def require(label, path, *fragments):
    assert all(fragment in src[path] for fragment in fragments), label
    checks.append(label)

require('int32 area/point distinct from precise point','src/misc/lv_area.h',
        'int32_t x;', 'int32_t y;', 'int32_t x1;', 'int32_t y1;',
        'int32_t x2;', 'int32_t y2;', 'lv_value_precise_t x;')
require('float conditional applies to precise type','src/misc/lv_types.h',
        '#if LV_USE_FLOAT','typedef float lv_value_precise_t;', 'typedef int32_t lv_value_precise_t;')
require('four point +1 and direct extrema without -1','src/core/lv_obj_pos.c',
        '{area->x1, area->y1}', '{area->x1, area->y2 + 1}',
        '{area->x2 + 1, area->y1}', '{area->x2 + 1, area->y2 + 1}',
        'lv_obj_transform_point_array(obj, p, 4, flags);',
        'area->x2 = LV_MAX4(p[0].x, p[1].x, p[2].x, p[3].x);')
flags={name:int(value,16) for name,value in re.findall(r'LV_OBJ_POINT_TRANSFORM_FLAG_(\w+)\s*=\s*(0x[0-9a-fA-F]+)',src['src/core/lv_obj_pos.h'])}
assert flags == {'NONE':0,'RECURSIVE':1,'INVERSE':2,'INVERSE_RECURSIVE':3}
checks.append('flags explicit values 0/1/2/3')
require('forward current then parent; inverse parent then current','src/core/lv_obj_pos.c',
        'if(inverse) {\n            if(recursive) lv_obj_transform_point_array(lv_obj_get_parent(obj), points, count, flags);\n            if(do_tranf) transform_point_array(obj, points, count, inverse);',
        'else {\n            if(do_tranf) transform_point_array(obj, points, count, inverse);\n            if(recursive) lv_obj_transform_point_array(lv_obj_get_parent(obj), points, count, flags);')
require('mode enum transform third ordinal','src/core/lv_obj_draw.h',
        'LV_LAYER_TYPE_NONE,\n    LV_LAYER_TYPE_SIMPLE,\n    LV_LAYER_TYPE_TRANSFORM,')
require('safe getters signed positive else one','src/core/lv_obj_style.h',
        'int32_t scale = lv_obj_get_style_transform_scale_x(obj, part);',
        'int32_t scale = lv_obj_get_style_transform_scale_y(obj, part);',
        'return scale > 0 ? scale : 1;')
require('percent and reciprocal pivots remain integer expressions','src/core/lv_obj_pos.c',
        'pivot.x = (LV_COORD_GET_PCT(pivot.x) * lv_area_get_width(&obj->coords)) / 100;',
        'scale_x = (256 * 256 + scale_x - 1) / scale_x;',
        'lv_point_array_transform(p, p_count, angle, scale_x, scale_y, &pivot, !inv);')
require('point width, scale, interpolation, shifts','src/misc/lv_area.c',
        'lv_point_t * points, size_t count, int32_t angle, int32_t scale_x, int32_t scale_y,',
        'uint32_t i;', 'angle_limited > 3600', 'angle_limited < 0',
        'LV_TRANSFORM_TRIGO_SHIFT 10', 'LV_TRANSFORM_TRIGO_SHIFT + 8',
        'return (int32_t)(area_p->x2 - area_p->x1 + 1);')

names=['SCALE_X','SCALE_Y','ROTATION','PIVOT_X','PIVOT_Y']
values={name:int(value) for name,value in re.findall(r'LV_STYLE_TRANSFORM_(\w+)\s*=\s*(\d+)',src['src/misc/lv_style.h'])}
candidate=[values[name] for name in names]
rom=[110,111,112,113,114]  # Inherited certified G02 uses, not a fresh ROM decode.
assert candidate == [108,109,110,111,112]
assert [r-c for r,c in zip(rom,candidate)] == [2]*5
for name in names:
    assert 'LV_STYLE_TRANSFORM_'+name in src['src/core/lv_obj_style_gen.h']
g02=(REV/'reports/ap01/region-transform-review-g02-0041-20261023.md').read_text(encoding='utf-8')
assert 'property=0x6e' in g02 and 'property=0x6f' in g02 and '固定a2=0x70' in g02
assert '依次0x71/0x72' in g02
checks.append('five semantic property pairs have explicit +2 difference')
assert ((1<<29)-1-1)//2 == 0x0fffffff
checks.append('percent boundary constant algebra')

result={'passed':True,'live_source_files':len(selection),'live_source_lines':271,
        'all_retained_source_lines_match':True,'source_checks':checks,
        'property_pairs':[{'name':n,'candidate':c,'inherited_rom':r,'delta':r-c} for n,c,r in zip(names,candidate,rom)],
        'rom_behavior_basis':'G01/G02 inherited; no ROM reread or vendor-rule verification',
        'corrections':0,'new_functionality':0,'whole_library_exclusions':0,
        'limits':['Local source equality is not a version/signature/build certification.',
                  'Explicit enum numeric difference is independent of enum storage size.',
                  'C signed arithmetic is not an all-input RV32 modulo/ASR proof.',
                  'size_t matches word count only under ordinary RV32 ABI assumption.',
                  'Exact config/object ABI, difference provenance and physical refresh remain unknown.']}
(HERE/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'source_files':11,'source_lines':271,'checks':len(checks),'five_property_delta':2,'new_functionality':0}))
