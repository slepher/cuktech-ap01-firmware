"""Source-text checks only: ROM behavior and vendor words inherited from G01/G02."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
evidence=json.loads((HERE/'candidate-excerpts.json').read_text(encoding='utf-8'))
items=evidence['excerpts']
assert len(items)==11
assert sum(len(item['lines']) for item in items)==271
source={item['path'].split('/lvgl/lvgl/')[1]:{x['line']:x['text'] for x in item['lines']} for item in items}
for item in items:
    assert [x['line'] for x in item['lines']]==[n for a,b in item['ranges'] for n in range(a,b+1)]
checks=[]
def exact(label,path,lines):
    for n,want in lines:
        assert source[path][n].strip()==want,(path,n,source[path][n],want)
    checks.append({'label':label,'path':path,'lines':[n for n,_ in lines],'result':'PASS'})

exact('four corners plus one and bounding rectangle without minus one','src/core/lv_obj_pos.c',[
    (798,'lv_point_t p[4] = {'),(799,'{area->x1, area->y1},'),
    (800,'{area->x1, area->y2 + 1},'),(801,'{area->x2 + 1, area->y1},'),
    (802,'{area->x2 + 1, area->y2 + 1},'),(805,'lv_obj_transform_point_array(obj, p, 4, flags);'),
    (807,'area->x1 = LV_MIN4(p[0].x, p[1].x, p[2].x, p[3].x);'),
    (808,'area->x2 = LV_MAX4(p[0].x, p[1].x, p[2].x, p[3].x);'),
    (809,'area->y1 = LV_MIN4(p[0].y, p[1].y, p[2].y, p[3].y);'),
    (810,'area->y2 = LV_MAX4(p[0].y, p[1].y, p[2].y, p[3].y);')])
exact('recursive and inverse flags','src/core/lv_obj_pos.h',[
    (28,'LV_OBJ_POINT_TRANSFORM_FLAG_NONE = 0x00,'),
    (31,'LV_OBJ_POINT_TRANSFORM_FLAG_RECURSIVE = 0x01,'),
    (34,'LV_OBJ_POINT_TRANSFORM_FLAG_INVERSE = 0x02,'),
    (37,'LV_OBJ_POINT_TRANSFORM_FLAG_INVERSE_RECURSIVE = 0x03,')])
exact('current then parent in forward direction, reverse in inverse direction','src/core/lv_obj_pos.c',[
    (780,'if(obj) {'),(782,'bool do_tranf = layer_type == LV_LAYER_TYPE_TRANSFORM;'),
    (785,'if(inverse) {'),
    (786,'if(recursive) lv_obj_transform_point_array(lv_obj_get_parent(obj), points, count, flags);'),
    (787,'if(do_tranf) transform_point_array(obj, points, count, inverse);'),
    (790,'if(do_tranf) transform_point_array(obj, points, count, inverse);'),
    (791,'if(recursive) lv_obj_transform_point_array(lv_obj_get_parent(obj), points, count, flags);')])
exact('layer enum ordinal two','src/core/lv_obj_draw.h',[
    (32,'LV_LAYER_TYPE_NONE,'),(33,'LV_LAYER_TYPE_SIMPLE,'),(34,'LV_LAYER_TYPE_TRANSFORM,')])
exact('identity gate, percent pivots and inverse formulas','src/core/lv_obj_pos.c',[
    (1159,'if(angle == 0 && scale_x == LV_SCALE_NONE && scale_y == LV_SCALE_NONE) return;'),
    (1167,'pivot.x = (LV_COORD_GET_PCT(pivot.x) * lv_area_get_width(&obj->coords)) / 100;'),
    (1170,'pivot.y = (LV_COORD_GET_PCT(pivot.y) * lv_area_get_height(&obj->coords)) / 100;'),
    (1173,'pivot.x = obj->coords.x1 + pivot.x;'),(1174,'pivot.y = obj->coords.y1 + pivot.y;'),
    (1177,'angle = -angle;'),(1178,'scale_x = (256 * 256 + scale_x - 1) / scale_x;'),
    (1179,'scale_y = (256 * 256 + scale_y - 1) / scale_y;'),
    (1182,'lv_point_array_transform(p, p_count, angle, scale_x, scale_y, &pivot, !inv);')])
exact('safe scale getters keep positive or one','src/core/lv_obj_style.h',[
    (293,'return scale > 0 ? scale : 1;'),(299,'return scale > 0 ? scale : 1;')])
exact('area and point int32 fields','src/misc/lv_area.h',[
    (32,'int32_t x;'),(33,'int32_t y;'),(43,'int32_t x1;'),(44,'int32_t y1;'),
    (45,'int32_t x2;'),(46,'int32_t y2;')])
exact('pct constants and sentinel boundary','src/misc/lv_area.h',[
    (206,'#define LV_COORD_TYPE_SHIFT    (29U)'),
    (227,'#define LV_PCT_STORED_MAX       (LV_COORD_MAX - 1)'),
    (231,'#define LV_PCT_POS_MAX          (LV_PCT_STORED_MAX / 2)'),
    (233,'#define LV_COORD_IS_PCT(x)      ((LV_COORD_IS_SPEC(x) && LV_COORD_PLAIN(x) <= LV_PCT_STORED_MAX))')])
exact('point transform interpolation and scaling order','src/misc/lv_area.c',[
    (441,'#define LV_TRANSFORM_TRIGO_SHIFT 10'),
    (472,'if(angle_limited > 3600) angle_limited -= 3600;'),
    (473,'if(angle_limited < 0) angle_limited += 3600;'),
    (485,'int32_t sinma = (s1 * (10 - angle_rem) + s2 * angle_rem) / 10;'),
    (487,'int32_t cosma = (c1 * (10 - angle_rem) + c2 * angle_rem) / 10;'),
    (498,'if(zoom_first) {'),(499,'x *= scale_x;'),(500,'y *= scale_y;'),
    (505,'points[i].x = (((cosma * x - sinma * y) * scale_x) >> (LV_TRANSFORM_TRIGO_SHIFT + 8)) + pivot->x;'),
    (514,'return (int32_t)(area_p->x2 - area_p->x1 + 1);'),
    (519,'return (int32_t)(area_p->y2 - area_p->y1 + 1);')])

names=['SCALE_X','SCALE_Y','ROTATION','PIVOT_X','PIVOT_Y']
candidate=[]
for number,name in zip(range(305,310),names):
    text=source['src/misc/lv_style.h'][number].strip()
    assert text.startswith('LV_STYLE_TRANSFORM_'+name)
    candidate.append(int(text.split('=')[1].strip().rstrip(',')))
rom_ids=[0x6e,0x6f,0x70,0x71,0x72] # inherited G01/G02, not re-read from ROM
assert candidate==[108,109,110,111,112]
assert [rom-cand for rom,cand in zip(rom_ids,candidate)]==[2]*5
result={'task':'C25','result':'PASS','files':11,'selected_lines':271,'checks':checks,
        'property_id_difference':{'names':names,'candidate':candidate,'inherited_rom':rom_ids,'rom_minus_candidate':2},
        'limits':['No ROM/model/candidate execution; checks cover retained local source text only.',
                  'Signed C expressions are not an all-input proof of RV32 modulo arithmetic or ASR.',
                  'Property IDs differ; exact ROM version/build/provenance remain unknown.']}
(HERE/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: 11 files / 271 selected lines / 9 source checks; five property IDs differ by +2 in ROM.')
