"""G18 independent source comparison. Read-only local source; no ROM export."""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
G17 = TREE/'reverse/analysis/fb-source-auth-g17-0041-20261024'
prior = json.loads((G17/'source-evidence.json').read_text(encoding='utf-8'))
remote = r'''
from pathlib import Path
import json, subprocess
r=Path('/home/slepher/nuttx-ap01-sim/nuttx')
spans={
 'drivers/video/fb.c':[(80,95),(182,193),(331,339),(432,467),(493,503),(510,532),(1415,1447)],
 'include/nuttx/fs/fs.h':[(219,242)],
 'include/sys/poll.h':[(79,88),(103,108),(123,131)],
 'include/nuttx/video/fb.h':[(192,192),(720,728)],
 'fs/vfs/fs_poll.c':[(276,306)],
 'include/nuttx/circbuf.h':[(54,58)],
 'libs/libc/misc/lib_circbuf.c':[(190,199),(211,215),(227,230),(272,275)],
 'drivers/video/Kconfig':[(24,26),(54,57)]}
checks=[]
for args in [('rev-parse','HEAD'),('describe','--tags','--exact-match','HEAD'),
             ('status','--short','--',*spans),('diff','HEAD','--exit-code','--',*spans)]:
 p=subprocess.run(['git','-C',str(r),*args],capture_output=True,text=True)
 checks.append({'args':list(args),'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 assert p.returncode==0
assert checks[0]['stdout'].strip()=='6fc5b3e9dc51dcda46d99519f72b7f2ec6db2e64'
assert checks[1]['stdout'].strip()=='nuttx-12.10.0'
assert not checks[2]['stdout'] and not checks[3]['stdout']
out={}
for f,ranges in spans.items():
 ls=(r/f).read_text().splitlines()
 out[f]={str(n):ls[n-1] for a,b in ranges for n in range(a,b+1)}
print(json.dumps({'identity':checks,'lines':out}))
'''
p=subprocess.run(['wsl.exe','-d','Ubuntu-24.04','--exec','python3','-c',remote],capture_output=True)
assert p.returncode==0, p.stdout.decode(errors='replace')+p.stderr.decode(errors='replace')
fresh=json.loads(p.stdout)
lines={f:{int(n):s for n,s in ls.items()} for f,ls in fresh['lines'].items()}
old={f['path'].split('/nuttx/',1)[1]:{x['line']:x['text'] for s in f['spans'] for x in s['lines']}
     for f in prior['excerpts']}
compared=0
new=[]
for f,ls in lines.items():
    for n,s in ls.items():
        if n in old[f]:
            assert old[f][n]==s,(f,n)
            compared+=1
        else:
            new.append({'file':f,'line':n,'text':s})
checks=[]
def check(name,condition):
    assert condition,name
    checks.append(name)
def span(f,a,b):
    return '\n'.join(lines[f][n] for n in range(a,b+1))
fb='drivers/video/fb.c'
check('F declares flink/int overlay/NPOLL array/conditional wait',
      all(t in span(fb,80,95) for t in ['*flink','int overlay','*fds[CONFIG_VIDEO_FB_NPOLLWAITERS]',
                                     '#ifdef CONFIG_FB_SYNC','sem_t wait']))
ops=re.findall(r'\(\*(\w+)\)',span('include/nuttx/fs/fs.h',219,242))
check('eight preceding slots, poll index 8',ops==['open','close','read','write','seek','ioctl','mmap','truncate','poll'])
check('fb ops candidate uses same order',re.findall(r'^\s+(fb_\w+|NULL)',span(fb,182,193),re.M)==
      ['fb_open','fb_close','fb_read','fb_write','fb_seek','fb_ioctl','fb_mmap','NULL','fb_poll'])
check('lower ABI first four slots',re.findall(r'\(\*(\w+)\)',span('include/nuttx/video/fb.h',720,728))==
      ['getvideoinfo','getplaneinfo','open','close'])
check('open signed lower failure before publication; restore then free',
      all(t in span(fb,432,467) for t in ['kmm_zalloc(sizeof(*priv))','return -ENOMEM',
      '(ret = fb->vtable->open(fb->vtable)) < 0','priv->overlay = FB_NO_OVERLAY',
      'priv->flink = fb->head','filep->f_priv = priv','leave_critical_section(flags)',
      'kmm_free(priv)','return ret']))
check('close lower condition is current head next',
      'fb->head->flink == NULL' in lines[fb][493] and
      'fb->vtable->close(fb->vtable)' in lines[fb][497] and 'ret < 0' in lines[fb][498])
check('close restores before optional sem destroy and free',
      'leave_critical_section' in lines[fb][527] and '#ifdef CONFIG_FB_SYNC' in lines[fb][529]
      and 'nxsem_destroy' in lines[fb][530] and 'kmm_free' in lines[fb][532])
check('poll chooses slot, backpointer, local &fds, teardown clears slot then backpointer',
      all(t in span(fb,1415,1447) for t in ['i < CONFIG_VIDEO_FB_NPOLLWAITERS','pollfds = &priv->fds[i]',
      'ret = -EBUSY','*pollfds = fds','fds->priv = pollfds','!circbuf_is_full(panbuf)',
      'poll_notify(&fds, 1, POLLOUT)','*slot = NULL','fds->priv = NULL']))
check('poll events typedef is uint32_t and fields follow fd/events/revents/arg/cb/priv',
      'typedef uint32_t pollevent_t' in lines['include/sys/poll.h'][103] and
      all(t in span('include/sys/poll.h',123,131) for t in ['int          fd','events','revents','*arg','cb','*priv']))
check('notify iteration/mask/error clear/ALWAYS/callback',
      all(t in span('fs/vfs/fs_poll.c',276,306) for t in ['i < nfds && eventset','fds = afds[i]',
      'eventset & (fds->events | POLLERR | POLLHUP)','fds->revents &= ~POLLOUT',
      'fds->events & POLLALWAYS','fds->cb(fds)']))
lib='libs/libc/misc/lib_circbuf.c'
check('circ size/used/space/full chain',
      'return circ->size;' in span(lib,190,199) and 'circ->head - circ->tail' in lines[lib][214]
      and 'circbuf_size(circ) - circbuf_used(circ)' in lines[lib][229]
      and '!circbuf_space(circ)' in lines[lib][274])
check('Kconfig defaults do not establish ROM configuration',
      'config FB_SYNC' in lines['drivers/video/Kconfig'][24] and
      'default n' in lines['drivers/video/Kconfig'][26] and
      'VIDEO_FB_NPOLLWAITERS' in lines['drivers/video/Kconfig'][54] and
      'default 2' in lines['drivers/video/Kconfig'][57])
# Use independently accepted G13/G14/G16 evidence, without reopening the ROM.
g13=json.loads((TREE/'reverse/analysis/display-device-poll-g13-0041-20261024/evidence.json').read_text(encoding='utf-8'))
rows={x['pc']:x for w in g13['windows'] for x in w['rows']}
check('inherited ROM slot argument is s1 not local &fds',
      rows['0xa0132192']['asm']=='c.mv a0, s1' and rows['0xa0132192']['raw']=='2685')
check('inherited ROM slot backpointer store anchor',rows['0xa013217a']['raw']=='c4c9')
result={'status':'PASS','baseline':'ed4735b','identity':fresh['identity'],
        'source_files':len(lines),'old_source_lines_rechecked':compared,
        'semantic_checks':checks,'source_delta_only':new,
        'conditional_layout':{'assumptions':'4-byte int, size_t, data and code pointers with ordinary field alignment; no compile',
                              'file_ops_offsets':dict(zip(ops,range(0,36,4))),
                              'F_if_NPOLL2_and_no_SYNC':{'flink':0,'overlay':4,'fds[0]':8,'fds[1]':12,'size':16},
                              'P':{'fd':0,'events':4,'revents':8,'arg':12,'cb':16,'priv':20}},
        'decision':'accept G17 scoped candidate mapping; clarify eight preceding slots, not nine',
        'new_business_functions':0,'new_full_library_exclusions':0,'ROM_exported':False,
        'unknown':['exact ROM version/configuration','cause of &fds versus F slot difference',
                   'teardown-before-close caller','lower callback implementation and hardware notification']}
(HERE/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','semantic_checks':len(checks),'source_files':len(lines),
                  'old_lines_rechecked':compared,'source_delta_lines':len(new)}))
