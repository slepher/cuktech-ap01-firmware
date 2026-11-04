"""Collection CLI replay/resume checks against an injected peer; no network or device."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from app_set_client_v3 import inspect_manifest

spec=importlib.util.spec_from_file_location('set_cli',Path(__file__).with_name('app-set-client-v3.py'))
client=importlib.util.module_from_spec(spec);spec.loader.exec_module(client)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,required=True)
p.add_argument('--package',type=Path,action='append',required=True);a=p.parse_args()
blob=a.manifest.read_bytes();manifest=inspect_manifest(blob)
packages={b[128:160].split(b'\0')[0].decode():b for b in [x.read_bytes() for x in a.package]}
mac='010203040506';host='offline.invalid:18080'

class Clock:
    now=0
    def time(self):return self.now
    def sleep(self,n):self.now+=n

class Peer:
    def __init__(self,mask=3,lose='',terminal='succeeded'):
        self.mask,self.lose,self.terminal=mask,lose,terminal
        self.record=None;self.calls=[];self.commits=0;self.data=[bytearray(),bytearray()];self.hang=False
    def __call__(self,method,endpoint,params=None,body=None,binary=False):
        self.calls.append((method,endpoint,copy.deepcopy(params)))
        if endpoint=='status':
            return 200,dict(protocol=3,device_mac=mac,phase='succeeded',candidate_manifest='11'*32,
                candidate_version=manifest['version']-1,boot_id=11,runtime_reporting=True,app_max=8,cleanup_pending=False,limits=dict(package_bytes=1<<24,image_bytes=1<<24,heap_bytes=1<<24,stack_bytes=1<<24,tasks=32,pages=256,capabilities=127,ram_bytes=1<<28,resident_bytes=1<<20))
        if endpoint=='update/begin':
            assert binary and body[:8]==b'ASB3\x01\x00\x40\x00' and body[64:]==blob
            assert body[8:40]==bytes.fromhex('11'*32)
            if not self.record:
                self.record=dict(protocol=3,device_mac=mac,operation_id=params['operation_id'],phase='receiving',
                    old_manifest='11'*32,old_version=manifest['version']-1,candidate_manifest=manifest['digest'],
                    candidate_version=manifest['version'],boot_id=11,received=[0]*8,changed_mask=self.mask,
                    ready_mask=0,sequence=1,chunk_max=64,cleanup_pending=False,runtime_reporting=True)
        elif endpoint=='update/result' and not self.record:
            return 404,dict(device_mac=mac,error_code='receipt_expired')
        else:
            assert self.record and params['operation_id']==self.record['operation_id']
            if '/chunk' in endpoint:
                i=int(endpoint.split('/')[1]);assert self.mask&(1<<i)
                assert binary and params['offset']==len(self.data[i]) and hashlib.sha256(body).hexdigest()==params['sha256']
                self.data[i].extend(body);self.record['received'][i]=len(self.data[i]);self.record['sequence']+=1
            elif '/ready' in endpoint:
                i=int(endpoint.split('/')[1]);assert bytes(self.data[i])==packages[manifest['apps'][i]['app_id']]
                self.record['ready_mask']|=1<<i;self.record['sequence']+=1
            elif endpoint=='update/commit':
                assert self.record['ready_mask']==self.mask;self.commits+=1;assert self.commits==1
                self.record['phase']='switch_pending';self.record['sequence']+=1
            elif endpoint=='update/cancel':
                self.record['phase']='cancelled';self.record['sequence']+=1
            elif endpoint=='update/result' and self.record['phase']=='switch_pending' and not self.hang:
                self.record.update(phase=self.terminal,sequence=self.record['sequence']+1,boot_id=12)
                self.record['runtime']=dict(boot_state='started',complete=True,health_state='healthy',manifest=manifest['digest'],
                    version=manifest['version'],running=[{k:app[k] for k in ('index','app_id','version','digest')}|{'health':0}
                        for app in sorted(manifest['apps'],key=lambda x:x['order'])])
        if self.lose and endpoint.endswith(self.lose):
            self.lose='';raise client.Uncertain('injected lost reply')
        return (202 if self.record['phase']=='switch_pending' else 200),copy.deepcopy(self.record)

with tempfile.TemporaryDirectory(prefix='set-client-') as folder:
    root=Path(folder);cases=0
    for mask in (1,3):
        supplied=[packages[app['app_id']] for app in manifest['apps'] if mask&(1<<app['index'])]
        for lose in ('','begin','chunk','ready','commit'):
            clock=Clock();peer=Peer(mask,lose);receipt=root/f'{mask}-{lose}.json'
            installer=client.Installer(peer,mac,host,receipt,180,clock.time,clock.sleep)
            assert installer.install(blob,supplied)['phase']=='succeeded'
            saved=json.loads(receipt.read_text());assert saved['original_boot']==11 and saved['result']['boot_id']==12
            assert peer.commits==1 and len({params['operation_id'] for _,_,params in peer.calls if params})==1
            assert not saved.keys()&{'code','token','authorization'}
            before=len(peer.calls)
            assert client.Installer(peer,mac,host,receipt,180,clock.time,clock.sleep).install(blob,supplied)['phase']=='succeeded'
            assert all(method=='GET' for method,_,_ in peer.calls[before:])
            cases+=1
    peer=Peer();peer.hang=True;clock=Clock();receipt=root/'resume.json'
    installer=client.Installer(peer,mac,host,receipt,1,clock.time,clock.sleep)
    try:installer.install(blob,list(packages.values()))
    except client.Uncertain:pass
    else:raise AssertionError('deadline was ignored')
    before=len(peer.calls);operation=json.loads(receipt.read_text())['operation_id'];peer.hang=False
    assert client.Installer(peer,mac,host,receipt,180,clock.time,clock.sleep).install(blob,list(packages.values()))['phase']=='succeeded'
    assert json.loads(receipt.read_text())['operation_id']==operation and peer.commits==1
    assert all(method=='GET' for method,_,_ in peer.calls[before:])
    peer=Peer(terminal='failed_rolled_back');clock=Clock();receipt=root/'rollback.json'
    assert client.Installer(peer,mac,host,receipt,180,clock.time,clock.sleep).install(blob,list(packages.values()))['phase']=='failed_rolled_back'
    peer=Peer();clock=Clock();receipt=root/'cancel.json'
    installer=client.Installer(peer,mac,host,receipt,180,clock.time,clock.sleep)
    try:installer.install(blob,[])
    except ValueError:pass
    else:raise AssertionError('missing changed packages accepted')
    assert installer.cancel()['phase']=='cancelled' and peer.commits==0
    # Once acknowledged, an expired receipt must never silently begin a new transaction.
    peer.record=None
    try:installer.install(blob,list(packages.values()))
    except ValueError as error:assert 'expired' in str(error)
    else:raise AssertionError('expired acknowledged receipt accepted')
    peer=Peer();clock=Clock();receipt=root/'budget-rejected.json'
    def limited(*args,**kwargs):
        status,value=peer(*args,**kwargs)
        if args[1]=='status':value['limits']['ram_bytes']=0
        return status,value
    try:client.Installer(limited,mac,host,receipt,180,clock.time,clock.sleep).install(blob,list(packages.values()))
    except ValueError as error:assert 'RAM' in str(error)
    else:raise AssertionError('over-budget collection accepted')
    assert not receipt.exists() and [endpoint for _,endpoint,_ in peer.calls]==['status']
print(f'collection CLI: {cases} single/batch lost-reply cases, durable resume, query-only post-commit, rollback, cancel and expired receipt passed; no device access')
