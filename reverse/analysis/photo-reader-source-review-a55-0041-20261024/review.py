"""A55 independent read-only source review. Does not import/run A54 collector."""
from pathlib import Path
import json
import subprocess

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'photo-reader-source-a54-0041-20261024/candidate-evidence.json'
saved=json.loads(OLD.read_text(encoding='utf8'))
prefix='/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl/'
expected={f['path'].removeprefix(prefix):{r['line']:r['text'] for s in f['snippets'] for r in s['lines']} for f in saved['files']}
# Declared fixed ranges, not discovery or a diff scan.
scopes={'src/misc/lv_fs.c':[(76,118),(121,137),(154,184),(391,417),(509,535)],'src/misc/lv_fs.h':[(25,25),(34,47),(53,56),(69,92)],'src/misc/lv_fs_private.h':[(27,39)],'src/libs/gif/gifdec.h':[(28,33)],'src/libs/gif/gifdec.c':[(52,60),(773,788),(816,821)]}
remote='''from pathlib import Path
import json,zipfile
root=Path(%r)
expected=%r
scopes=%r
files={}
out={'static_only':True,'files':[],'clauses':[]}
with zipfile.ZipFile(root.parent/'v9.2.1.zip') as z:
 for rel,spans in scopes.items():
  raw=(root/rel).read_bytes(); lines=raw.decode('utf8').splitlines();files[rel]=lines
  member='lvgl-9.2.1/'+rel; archived=z.read(member);archive_text=archived.decode('utf8')
  matches=all(lines[n-1]==s for n,s in expected[rel].items())
  assert matches,rel
  snippets=[{'start':a,'end':b,'same_contiguous_text_in_archive':'\\n'.join(lines[a-1:b]) in archive_text} for a,b in spans]
  out['files'].append({'file':rel,'member':member,'whole_bytes_equal':raw==archived,'old_excerpt_lines_rechecked':len(expected[rel]),'A54_lines_match_live':matches,'snippets':snippets})
def line(rel,n,token):
 assert token in files[rel][n-1],(rel,n,token)
 out['clauses'].append({'file':rel,'line':n,'contains':token})
h='src/misc/lv_fs.h'; c='src/misc/lv_fs.c'; gh='src/libs/gif/gifdec.h';gc='src/libs/gif/gifdec.c';cp='src/misc/lv_fs_private.h'
for n,t in [(25,'UINT32_MAX'),(55,'LV_FS_MODE_RD = 0x02'),(70,'char letter'),(71,'uint32_t cache_size'),(72,'bool (*ready_cb)(lv_fs_drv_t * drv)'),(74,'(*open_cb)(lv_fs_drv_t * drv, const char * path, lv_fs_mode_t mode)'),(75,'(*close_cb)(lv_fs_drv_t * drv, void * file_p)'),(89,'void * file_d'),(90,'lv_fs_drv_t * drv'),(91,'lv_fs_file_cache_t * cache')]:line(h,n,t)
for n,t in [(29,'lv_fs_file_t fd'),(30,'const char * data'),(31,'uint8_t is_file'),(32,'uint32_t f_rw_p')]:line(gh,n,t)
for n,t in [(28,'uint32_t start'),(29,'uint32_t end'),(30,'uint32_t file_position'),(31,'void * buffer')]:line(cp,n,t)
for n,t in [(93,'drv->ready_cb(drv) == false'),(106,'file_p->drv = drv'),(113,'drv->open_cb(drv, resolved_path.real_path, mode)'),(118,'file_p->file_d = file_d'),(122,'lv_malloc_zeroed(sizeof(lv_fs_file_cache_t))'),(156,'if(file_p->drv == NULL)'),(160,'if(file_p->drv->close_cb == NULL)'),(166,'file_p->drv->close_cb(file_p->drv, file_p->file_d)'),(168,'file_p->drv->cache_size && file_p->cache'),(170,'file_p->drv->cache_size != LV_FS_CACHE_FROM_BUFFER && file_p->cache->buffer'),(171,'lv_free(file_p->cache->buffer)'),(174,'lv_free(file_p->cache)'),(177,'file_p->file_d = NULL'),(178,'file_p->drv    = NULL'),(179,'file_p->cache  = NULL'),(183,'return res'),(400,'lv_ll_ins_head(fsdrv_ll_p)'),(404,'*new_drv = drv_p'),(412,'(*drv)->letter == letter'),(513,'LV_FS_DEFAULT_DRIVE_LETTER !='),(514,"('A' <= path[0]) && (path[0] <= 'Z') && (path[1] == ':')"),(518,'resolved.real_path = path + 2'),(522,'resolved.real_path = path'),(524,'Lean rules for backward compatibility'),(525,'resolved.drive_letter = path[0]'),(528,'path++'),(529,"if(*path == ':') path++")]:line(c,n,t)
for n,t in [(55,'memset(&gif_base, 0, sizeof(gif_base))'),(57,'f_gif_open(&gif_base, fname, true)'),(60,'gif_open(&gif_base)'),(775,'gif->f_rw_p = 0'),(776,'gif->data = NULL'),(777,'gif->is_file = is_file'),(780,'lv_fs_open(&gif->fd, path, LV_FS_MODE_RD)'),(781,'if(res != LV_FS_RES_OK) return false'),(818,'if(gif->is_file)'),(819,'lv_fs_close(&gif->fd)')]:line(gc,n,t)
print(json.dumps(out))
'''%(prefix.rstrip('/'),expected,scopes)
result=subprocess.run(['wsl.exe','-d','Ubuntu-24.04','--exec','python3','-c',remote],capture_output=True)
assert result.returncode==0,(result.stdout+result.stderr).decode('utf8',errors='replace')
out=json.loads(result.stdout)
verdict={f['file']:f for f in out['files']}
assert sum(f['whole_bytes_equal'] for f in out['files'])==4
assert not verdict['src/libs/gif/gifdec.c']['whole_bytes_equal']
assert len(verdict['src/libs/gif/gifdec.c']['snippets'])==3
assert all(s['same_contiguous_text_in_archive'] for s in verdict['src/libs/gif/gifdec.c']['snippets'])
out.update(status='PASS',baseline='46fa469',independence='New read-only validator; A54 collect.py neither run nor imported; no ROM read',conditional_RV32_layout={'assumptions':'4-byte data/code pointers; 4-byte uint32 alignment; ordinary struct padding, not compiled','file':{'H':0,'D':4,'C':8,'size':12},'driver':{'letter':0,'cache_size':4,'ready_cb':8,'open_cb':12,'close_cb':16},'cache':{'start':0,'end':4,'position':8,'buffer':12,'size':16},'GIF_prefix':{'fd':0,'data':12,'is_file_u8':16,'f_rw_p':20}},accepted=['A47/A49 ROM callback(D,H) and conditional cache ownership; candidate ABI cannot replace ROM evidence','mode byte is_file=1 distinct from driver mode RD=2','lean suffix source+1/optional colon compatible; actual macro config unknown','candidate registration preserves driver pointer; no concrete ROM D binding','4 whole files equal local archive; gifdec.c whole different and only 3 selected snippets equal'],not_certified=['ROM exact version/build/unchanged library','actual type1 photo/D/callback/H instance','candidate close return inserted into ROM full return ABI','all GIF, filesystem, driver registration/ownership or special sentinel initialization','A50/A52 internal read source mapping'],new_functions=0,whole_library_exclusions=0)
(HERE/'review-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status=out['status'],files=len(out['files']),whole_equal=4,gif_selected_equal=3,old_excerpt_lines_rechecked=sum(f['old_excerpt_lines_rechecked'] for f in out['files']),source_clauses=len(out['clauses']),new_functions=0,ROM_read=False)))
