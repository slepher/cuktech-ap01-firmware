"""Verify collection-client input and reboot confirmation using real artifacts, offline."""
import argparse
import copy
import hashlib
from pathlib import Path
import struct
import app_set_client_v3 as client

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--manifest',type=Path,required=True)
p.add_argument('--package',type=Path,action='append',required=True)
a=p.parse_args()
blob=a.manifest.read_bytes();manifest=client.inspect_manifest(blob)
packages=client.inspect_packages(manifest,[path.read_bytes() for path in a.package])
assert len(packages)==len(manifest['apps'])==2
checks=0

def rejects(fn):
    global checks
    try:fn()
    except (ValueError,UnicodeDecodeError):checks+=1
    else:raise AssertionError('invalid input accepted')

for n in range(len(blob)):
    rejects(lambda n=n:client.inspect_manifest(blob[:n]))
for offset in (0,4,6,8,12,14,16,24,26,32,64,96,128,206,212):
    bad=bytearray(blob);bad[offset]^=1
    if offset in (206,212):
        bad[32:64]=bytes(32);bad[32:64]=hashlib.sha256(bad).digest()
    rejects(lambda:client.inspect_manifest(bad))
rejects(lambda:client.inspect_packages(manifest,list(packages.values())*2))
bad=bytearray(packages[0]);bad[-1]^=1
rejects(lambda:client.inspect_packages(manifest,[bad]))
assert set(client.changed_packages(manifest,packages,1))=={0}
assert set(client.changed_packages(manifest,packages,3))=={0,1}
assert client.changed_packages(manifest,{},0)=={}
rejects(lambda:client.changed_packages(manifest,{0:packages[0]},3))
rejects(lambda:client.changed_packages(manifest,packages,4))
rejects(lambda:client.changed_packages(manifest,packages,True))
running=[{k:app[k] for k in ('index','app_id','version','digest')}|{'health':0}
         for app in sorted(manifest['apps'],key=lambda app:app['order'])]
value=dict(phase='succeeded',candidate_manifest=manifest['digest'],candidate_version=manifest['version'],
           boot_id=12,cleanup_pending=False,runtime_reporting=True,
           runtime=dict(complete=True,boot_state='started',health_state='healthy',manifest=manifest['digest'],
                        version=manifest['version'],running=running))
assert client.verify_running(value,manifest,11)
for field,replacement in [('boot_id',11),('cleanup_pending',True),('runtime_reporting',False),('phase','trial_started')]:
    bad=copy.deepcopy(value);bad[field]=replacement;assert not client.verify_running(bad,manifest,11)
for field,replacement in [('complete',False),('boot_state','partial_failed'),('health_state','fault')]:
    bad=copy.deepcopy(value);bad['runtime'][field]=replacement;assert not client.verify_running(bad,manifest,11)
for health in (None,True,1,-4):
    bad=copy.deepcopy(value);bad['runtime']['running'][0]['health']=health;assert not client.verify_running(bad,manifest,11)
for field,replacement in [('manifest','0'*64),('version',0),('running',running[:1]),('running',list(reversed(running)))]:
    bad=copy.deepcopy(value);bad['runtime'][field]=replacement;rejects(lambda:client.verify_running(bad,manifest,11))
for field in ('index','app_id','version','digest'):
    bad=copy.deepcopy(value);bad['runtime']['running'][1][field]='wrong';rejects(lambda:client.verify_running(bad,manifest,11))
bad=copy.deepcopy(value);bad['candidate_manifest']='0'*64
rejects(lambda:client.verify_running(bad,manifest,11))
caps=dict(protocol=3,app_max=8,limits=dict(package_bytes=1<<32,image_bytes=1<<32,heap_bytes=1<<32,
    stack_bytes=1<<32,tasks=32,pages=256,capabilities=2**64-1,ram_bytes=1<<40,resident_bytes=4096))
totals=client.check_capabilities(manifest,caps)
caps['limits'].update(totals);caps['limits']['ram_bytes']=4096+sum(totals[k] for k in ('image_bytes','heap_bytes','stack_bytes'))
assert client.check_capabilities(manifest,caps)==totals
for key in totals:
    if totals[key]:
        bad=copy.deepcopy(caps);bad['limits'][key]=0 if key=='capabilities' else totals[key]-1
        rejects(lambda:client.check_capabilities(manifest,bad))
for key in caps['limits']:
    bad=copy.deepcopy(caps);del bad['limits'][key];rejects(lambda:client.check_capabilities(manifest,bad))
bad=copy.deepcopy(caps);bad['limits']['ram_bytes']-=1;rejects(lambda:client.check_capabilities(manifest,bad))
bad=copy.deepcopy(caps);bad['limits']['resident_bytes']=bad['limits']['ram_bytes']+1;rejects(lambda:client.check_capabilities(manifest,bad))
bad=copy.deepcopy(caps);bad['app_max']=True;rejects(lambda:client.check_capabilities(manifest,bad))
print(f'collection client: {checks} rejected inputs; real packages, single/batch selection, reboot and exact running-set checks passed; no device access')
