"""C24 fixed-range source review. No ROM, formatter, allocator or GUI execution."""
from pathlib import Path
import json
import subprocess

OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
prior=json.loads((TREE/'reverse/analysis/text-entry-source-c23-0041-20261024/candidate-excerpts.json').read_text(encoding='utf8'))
root='/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl'
spans={'src/widgets/label/lv_label.c':[(178,204)],'src/widgets/label/lv_label_private.h':[(31,56)],
       'src/misc/lv_text.c':[(409,448)],'src/core/lv_obj_private.h':[(49,73)]}
remote='spans='+repr(spans)+'\n'+r'''
from pathlib import Path
import json
r=Path('/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl')
out=[]
for rel,rs in spans.items():
 selected=[]
 with (r/rel).open() as f:
  for n,t in enumerate(f,1):
   if any(a<=n<=b for a,b in rs):selected.append(f'{n}: '+t.rstrip('\n'))
   if n==max(b for a,b in rs):break
 out.append(dict(path=str(r/rel),lines=selected))
print(json.dumps(out))
'''
p=subprocess.run(['wsl','-d','Ubuntu-24.04','--','python3','-c',remote],capture_output=True,text=True,encoding='utf8')
assert p.returncode==0,p.stderr
fresh=json.loads(p.stdout)
old={x['path']:[line for e in x['excerpts'] for line in e['lines']] for x in prior}
assert len(fresh)==len(old)==4
maps={};equal=[]
for x in fresh:
 assert x['lines']==old[x['path']]
 rel=x['path'][len(root)+1:]
 maps[rel]={int(s.split(': ',1)[0]):s.split(': ',1)[1].strip() for s in x['lines']}
 equal.append(dict(path=x['path'],ranges=spans[rel],lines=len(x['lines']),equal=True))
assert sum(x['lines'] for x in equal)==118
l=maps['src/widgets/label/lv_label.c'];t=maps['src/misc/lv_text.c'];h=maps['src/widgets/label/lv_label_private.h'];o=maps['src/core/lv_obj_private.h']
checks=[]
def check(label,m,anchors):
 for n,s in anchors.items():assert s in m[n],(label,n,s,m[n])
 checks.append(dict(label=label,lines=list(anchors),result='PASS'))
check('entry signature/invalidate/refresh order',l,{178:'const char * fmt, ...',183:'lv_obj_invalidate(obj)',203:'lv_label_refr_text(obj)'})
check('old owned-text gate, free then clear pointer',l,{192:'label->text != NULL && label->static_txt == 0',193:'lv_free(label->text)',194:'label->text = NULL'})
check('va start/helper direct storage/end then dynamic flag clear',l,{198:'va_start(args, fmt)',199:'label->text = lv_text_set_text_vfmt(fmt, args)',200:'va_end(args)',201:'label->static_txt = 0'})
check('helper first-pass copy and length return',t,{409:'va_list ap',412:'va_list ap_copy',413:'va_copy(ap_copy, ap)',414:'uint32_t len = lv_vsnprintf(NULL, 0, fmt, ap_copy)',415:'va_end(ap_copy)'})
check('ordinary branch allocates len+1, formats with original ap, returns same text',t,{438:'#else',439:'text = lv_malloc(len + 1)',445:'lv_vsnprintf(text, len + 1, fmt, ap)',448:'return text'})
check('Arabic configuration adds raw buffer/conversion/second allocation/free',t,{418:'#if LV_USE_ARABIC_PERSIAN_CHARS',420:'raw_txt = lv_malloc(len + 1)',429:'lv_text_ap_calc_bytes_count',430:'text = lv_malloc(len_ap + 1)',435:'lv_text_ap_proc',437:'lv_free(raw_txt)'})
check('null-format and allocation failure remain separate branches',l,{187:'if(fmt == NULL)',188:'lv_label_refr_text(obj)',189:'return;'})
check('candidate normal allocation failure returns NULL',t,{441:'if(text == NULL)',442:'return NULL'})
check('text follows base with optional label layout fields',h,{32:'lv_obj_t obj',33:'char * text',40:'#if LV_LABEL_LONG_TXT_HINT',44:'#if LV_LABEL_TEXT_SELECTION'})
check('three-bit long mode then one-bit static declaration, no measured mask',h,{51:'lv_label_long_mode_t long_mode : 3',52:'uint8_t static_txt : 1'})
check('base has configuration-dependent fields',o,{54:'#if LV_OBJ_STYLE_CACHE',59:'#if LV_USE_OBJ_ID'})
result=dict(status='PASS',baseline='c44f3bf',source_files=equal,total_lines=118,checks=checks,
 decision='Accept C23 normal source mapping and limitations; no semantic correction',
 inherited_rom=dict(text_offset='0x2c',flags_byte_offset='0x5c',static_mask='0x10',proof='C13/C14; not re-read'),
 boundaries=['candidate field declaration does not measure bit3 or replace ROM mask0x10',
             'pointer-style RV32 va_copy explanation is conditional, not an authenticated typedef or backend contract',
             'non-Arabic branch compatibility is not original build config proof',
             'C23 local ZIP equality inherited, not repeated; no exact ROM version proof'],
 new_rom_functions=0,whole_library_exclusions=0)
(OUT/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',files=4,lines=118,source_contract_checks=len(checks))))
