"""G17 read-only local source authentication; does not run firmware or SIM."""
from pathlib import Path
import json
import subprocess

OUT = Path(__file__).resolve().parent
TREE = OUT.parents[2]
reader = r'''
from pathlib import Path
import subprocess,json
r=Path('/home/slepher/nuttx-ap01-sim/nuttx')
spans={
 'drivers/video/fb.c':[(80,95),(110,118),(182,193),(331,339),(419,468),(474,534),(1394,1453),(1960,1969)],
 'include/nuttx/fs/fs.h':[(219,250)],
 'include/sys/poll.h':[(73,88),(98,108),(119,132)],
 'include/nuttx/video/fb.h':[(192,192),(714,728)],
 'fs/vfs/fs_poll.c':[(276,306)],
 'include/nuttx/circbuf.h':[(52,59)],
 'libs/libc/misc/lib_circbuf.c':[(199,215),(227,230),(272,275)],
 'drivers/video/Kconfig':[(24,26),(54,57)]}
def git(*args):
 p=subprocess.run(['git','-C',str(r),*args],text=True,capture_output=True)
 return dict(args=list(args),exit=p.returncode,stdout=p.stdout,stderr=p.stderr)
checks=[git('rev-parse','HEAD'),git('describe','--tags','--exact-match','HEAD'),
        git('status','--short','--',*spans),git('diff','HEAD','--exit-code','--',*spans)]
assert all(c['exit']==0 for c in checks)
assert checks[0]['stdout'].strip()=='6fc5b3e9dc51dcda46d99519f72b7f2ec6db2e64'
assert checks[1]['stdout'].strip()=='nuttx-12.10.0'
assert checks[2]['stdout']==checks[3]['stdout']==''
paths={r,r.parent,r.parent.parent,r.parent.parent.parent}
for f in spans:
 p=(r/f).parent
 while p!=r:
  paths.add(p);p=p.parent
guidance=[str(p/'AGENTS.md') for p in sorted(paths) if (p/'AGENTS.md').exists()]
assert not guidance, guidance
excerpts=[]
for f,rs in spans.items():
 ls=(r/f).read_text().splitlines()
 excerpts.append(dict(path=str(r/f),spans=[dict(start=a,end=b,lines=[dict(line=i,text=ls[i-1]) for i in range(a,b+1)]) for a,b in rs]))
print(json.dumps(dict(root=str(r),git_checks=checks,applicable_agents=guidance,excerpts=excerpts)))
'''
p = subprocess.run(['wsl','-d','Ubuntu-24.04','--','python3','-c',reader],capture_output=True,text=True,encoding='utf8')
assert p.returncode == 0, p.stderr
d=json.loads(p.stdout)
(OUT/'source-evidence.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

byfile={x['path'].split('/nuttx/',1)[1]:{y['line']:y['text'] for s in x['spans'] for y in s['lines']} for x in d['excerpts']}
anchors={
 'drivers/video/fb.c':{84:'struct fb_priv_s *flink',86:'int overlay',90:'CONFIG_VIDEO_FB_NPOLLWAITERS',
  184:'fb_open',185:'fb_close',192:'fb_poll',432:'kmm_zalloc(sizeof(*priv))',449:'FB_NO_OVERLAY',
  456:'priv->flink = fb->head',459:'filep->f_priv = priv',493:'fb->head->flink == NULL',
  497:'fb->vtable->close(fb->vtable)',520:'prev->flink = priv->flink',524:'fb->head = priv->flink',
  532:'kmm_free(priv)',1417:'CONFIG_VIDEO_FB_NPOLLWAITERS',1428:'-EBUSY',1432:'*pollfds = fds',
  1433:'fds->priv = pollfds',1436:'!circbuf_is_full(panbuf)',1438:'poll_notify(&fds, 1, POLLOUT)',
  1446:'*slot = NULL',1447:'fds->priv = NULL'},
 'include/sys/poll.h':{79:'(0x04)',83:'(0x08)',84:'(0x10)',88:'(0x10000)',103:'uint32_t pollevent_t',
  124:'events',125:'revents',129:'arg',130:'cb',131:'priv'},
 'include/nuttx/fs/fs.h':{223:'(*open)',230:'(*close)',241:'(*poll)'},
 'include/nuttx/video/fb.h':{192:'-1',727:'(*open)',728:'(*close)'},
 'fs/vfs/fs_poll.c':{283:'i < nfds && eventset',290:'eventset & (fds->events | POLLERR | POLLHUP)',
  295:'&= ~POLLOUT',298:'fds->events & POLLALWAYS',302:'fds->cb(fds)'},
 'libs/libc/misc/lib_circbuf.c':{214:'circ->head - circ->tail',229:'circbuf_size(circ) - circbuf_used(circ)',274:'!circbuf_space(circ)'},
 'drivers/video/Kconfig':{24:'FB_SYNC',26:'default n',54:'VIDEO_FB_NPOLLWAITERS',57:'default 2'},
}
checked=[]
for f,lines in anchors.items():
 for n,s in lines.items():
  assert s in byfile[f][n],(f,n,s)
  checked.append(dict(file=f,line=n,contains=s))
# Reuse byte-authenticated ROM contracts; only reread the key ABI/difference anchors.
rom=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
base=0x9ffff000
anchors_rom={0xa0132192:'2685',0xa0132194:'efc0c090',0xa013217a:'c4c9',
             0xa012faf2:'4145',0xa012fb3e:'dcc0',0xa012f468:'4a85'}
with rom.open('rb') as f:
 for a,h in anchors_rom.items():
  f.seek(a-base);assert f.read(len(bytes.fromhex(h))).hex()==h
ops={}
with rom.open('rb') as f:
 for off,target in [(0,0xa012fabc),(4,0xa012f3e0),(0x20,0xa0132116)]:
  f.seek(0xa01c1368+off-base);v=int.from_bytes(f.read(4),'little');assert v==target
  ops[hex(off)]=hex(v)
result=dict(status='PASS',baseline='df35f44',source_anchor_checks=checked,
            rom_anchor_checks={hex(k):v for k,v in anchors_rom.items()},ops=ops,
            inherited=['G13/G14 poll/notify ABI and byte semantics','G15/G16 F allocation/link/lower/close','A13/A14 local tree identity'],
            comparison=dict(matches=['open/close lifecycle','uint32 poll fields/masks and notify logic','poll two slots under configuration'],
                            difference='candidate poll_notify(&fds,1,POLLOUT), ROM poll_notify(F slot,1,4)',
                            configuration=['RV32 int/pointer widths','CONFIG_VIDEO_FB_NPOLLWAITERS=2','CONFIG_FB_SYNC absent-compatible'],
                            unknown=['exact ROM source revision/build configuration','teardown-before-close caller','lower callback implementation']))
(OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',source_anchors=len(checked),rom_anchors=len(anchors_rom)+len(ops),files=len(d['excerpts']))))
