"""A54 read-only source and local archive comparison; no ROM/read algorithm."""
import json
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
remote=r'''
from pathlib import Path
import json,zipfile
root=Path('/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl')
spans={
 'src/misc/lv_fs.c':[(76,118),(121,137),(154,184),(391,417),(509,535)],
 'src/misc/lv_fs.h':[(25,25),(34,47),(53,56),(69,92)],
 'src/misc/lv_fs_private.h':[(27,39)],
 'src/libs/gif/gifdec.h':[(28,33)],
 'src/libs/gif/gifdec.c':[(52,60),(773,788),(816,821)]}
out={'root':str(root),'identity':'F07/F08 inherited; local archive consistency only','files':[]}
with zipfile.ZipFile(root.parent/'v9.2.1.zip') as z:
 for f,ranges in spans.items():
  data=(root/f).read_bytes()
  member='lvgl-9.2.1/'+f
  archived=z.read(member)
  archive_text=archived.decode()
  ls=data.decode().splitlines()
  out['files'].append({'path':str(root/f),'member':member,'local_member_equal':data==archived,
       'snippets':[{'start':a,'end':b,'same_contiguous_text_in_archive':'\n'.join(ls[a-1:b]) in archive_text,
                    'lines':[{'line':n,'text':ls[n-1]} for n in range(a,b+1)]} for a,b in ranges]})
print(json.dumps(out))
'''
p=subprocess.run(['wsl.exe','-d','Ubuntu-24.04','--exec','python3','-c',remote],capture_output=True)
assert p.returncode==0,p.stdout.decode(errors='replace')+p.stderr.decode(errors='replace')
candidate=json.loads(p.stdout)
files={f['path'].split('/nuttx-ap01-sim/apps/graphics/lvgl/lvgl/',1)[1]:
       {x['line']:x['text'] for s in f['snippets'] for x in s['lines']} for f in candidate['files']}
anchors={
 'src/misc/lv_fs.h':{25:'LV_FS_CACHE_FROM_BUFFER   UINT32_MAX',55:'LV_FS_MODE_RD = 0x02',
     70:'char letter',71:'uint32_t cache_size',72:'(*ready_cb)(lv_fs_drv_t * drv)',
     74:'(*open_cb)(lv_fs_drv_t * drv, const char * path, lv_fs_mode_t mode)',
     75:'(*close_cb)(lv_fs_drv_t * drv, void * file_p)',89:'void * file_d',
     90:'lv_fs_drv_t * drv',91:'lv_fs_file_cache_t * cache'},
 'src/misc/lv_fs.c':{93:'drv->ready_cb(drv) == false',106:'file_p->drv = drv',
     110:'file_p->file_d = file_p',113:'drv->open_cb(drv, resolved_path.real_path, mode)',
     114:'file_d == NULL || file_d == (void *)(-1)',118:'file_p->file_d = file_d',
     122:'lv_malloc_zeroed(sizeof(lv_fs_file_cache_t))',156:'file_p->drv == NULL',
     160:'file_p->drv->close_cb == NULL',166:'close_cb(file_p->drv, file_p->file_d)',
     168:'file_p->drv->cache_size && file_p->cache',
     170:'file_p->drv->cache_size != LV_FS_CACHE_FROM_BUFFER && file_p->cache->buffer',
     171:'lv_free(file_p->cache->buffer)',174:'lv_free(file_p->cache)',
     177:'file_p->file_d = NULL',178:'file_p->drv    = NULL',179:'file_p->cache  = NULL',
     183:'return res',393:'lv_memzero(drv, sizeof(lv_fs_drv_t))',400:'lv_ll_ins_head(fsdrv_ll_p)',
     404:'*new_drv = drv_p',412:'(*drv)->letter == letter',
     513:'LV_FS_DEFAULT_DRIVE_LETTER',518:'resolved.real_path = path + 2',
     522:'resolved.real_path = path',525:'resolved.drive_letter = path[0]',529:"if(*path == ':') path++"},
 'src/misc/lv_fs_private.h':{28:'uint32_t start',29:'uint32_t end',30:'uint32_t file_position',31:'void * buffer'},
 'src/libs/gif/gifdec.h':{29:'lv_fs_file_t fd',30:'const char * data',31:'uint8_t is_file',32:'uint32_t f_rw_p'},
 'src/libs/gif/gifdec.c':{55:'memset(&gif_base, 0, sizeof(gif_base))',57:'f_gif_open(&gif_base, fname, true)',
     58:'if(!res) return NULL',60:'return gif_open(&gif_base)',775:'gif->f_rw_p = 0',
     776:'gif->data = NULL',777:'gif->is_file = is_file',780:'lv_fs_open(&gif->fd, path, LV_FS_MODE_RD)',
     781:'if(res != LV_FS_RES_OK) return false',818:'if(gif->is_file)',819:'lv_fs_close(&gif->fd)'}}
checks=[]
for f,expected in anchors.items():
    for line,token in expected.items():
        assert token in files[f][line],(f,line,token)
        checks.append({'file':f,'line':line,'contains':token})
equal=sum(f['local_member_equal'] for f in candidate['files'])
result={'status':'PASS','baseline':'aabdfcd','source_checks':checks,'candidate_members_equal':equal,
        'conditional_RV32_layout':{'assumptions':'4B data/code pointers and uint32 alignment; no compile',
          'file':{'H':0,'D':4,'C':8,'size':12},
          'driver_prefix':{'letter':0,'cache_size':4,'ready_cb':8,'open_cb':12,'close_cb':16},
          'cache':{'start':0,'end':4,'file_position':8,'buffer':12,'size':16},
          'GIF_prefix':{'fd':0,'data':12,'is_file_byte':16,'f_rw_p':20}},
        'inherited_ROM':['A47/A49 callback(D,H), conditional buffer/C free, prefix clear',
                         'A37/A39 W to O copying','A41/A42 outer free(O)','A33/A35 five normal photos mode0'],
        'partial_only':['driver registry source role not bound to a concrete ROM registration instance',
                        'path suffix compatible with lean default-letter-zero branch, not actual config proof',
                        'candidate close returns callback res; ROM full return ABI not authenticated'],
        'unknown':['exact ROM version/build','selected D and driver callbacks','real H/resource identity',
                   'all failure paths and mapped-buffer branch','actual execution'],
        'new_business_functions':0,'full_library_exclusions':0,'new_ROM_read_or_export':False,
        'A50_read_algorithm_expanded':False}
(HERE/'candidate-evidence.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','members_equal':equal,'checks':len(checks),'ROM_read':False,
                  'scoped_differences':[{'file':f['path'],'whole_equal':f['local_member_equal'],
                       'snippets':[s['same_contiguous_text_in_archive'] for s in f['snippets']]} for f in candidate['files']]}))
