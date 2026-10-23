"""D13: read only the selected local candidate members; never execute target code."""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REMOTE = r'''
import json, zipfile
from pathlib import Path
root = Path('/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl')
selections = {
 'src/draw/lv_draw_buf.c': [(19,21),(52,79),(108,117),(283,313),(361,376),(596,620),(631,662)],
 'src/draw/lv_draw_buf.h': [(78,94)],
 'src/draw/lv_draw_buf_private.h': [(27,34)],
 'src/draw/lv_image_dsc.h': [(25,26),(47,56),(77,98)],
 'src/misc/lv_color.h': [(130,151),(196,201)],
 'src/misc/lv_math.h': [(33,33)],
 'src/lv_conf_internal.h': [(306,313),(1263,1270)],
 'src/misc/cache/lv_cache_lru_rb.c': [(59,68),(216,237),(304,313),(332,342),(441,449),(458,462)],
 'src/misc/cache/lv_cache_private.h': [(170,178)],
 'src/draw/lv_image_decoder_private.h': [(55,64)],
}
out = {'root':str(root), 'archive':str(root.parent/'v9.2.1.zip'),
       'identity_inherited_from':'F07/F08; no new upstream provenance claim', 'members':[]}
with zipfile.ZipFile(root.parent/'v9.2.1.zip') as archive:
 for rel, ranges in selections.items():
  raw = (root/rel).read_bytes()
  lines = raw.decode().splitlines()
  name = 'lvgl-9.2.1/'+rel
  out['members'].append({'path':str(root/rel), 'member':name,
   'equal':raw==archive.read(name), 'excerpts':[
    {'start':a,'end':b,'lines':[f'{i+1}: {lines[i]}' for i in range(a-1,b)]}
    for a,b in ranges]})
assert all(item['equal'] for item in out['members'])
print(json.dumps(out,ensure_ascii=False,indent=2))
'''

if __name__ == '__main__':
    result = subprocess.run(['wsl.exe','-d','Ubuntu-24.04','--exec','python3','-c',REMOTE],capture_output=True)
    if result.returncode:
        raise SystemExit(result.stderr.decode(errors='replace') or result.stdout.decode(errors='replace'))
    data = json.loads(result.stdout.decode())
    assert len(data['members']) == 10 and all(item['equal'] for item in data['members'])
    (HERE/'candidate-evidence.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS: 10 selected local members equal; focused excerpts retained; no ROM reread.')
