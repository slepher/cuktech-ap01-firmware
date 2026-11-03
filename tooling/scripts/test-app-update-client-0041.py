"""Client fault/replay checks. Injected protocol peer; never contacts a device."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

spec=importlib.util.spec_from_file_location('client',Path(__file__).with_name('app-update-client-0041.py'))
client=importlib.util.module_from_spec(spec);spec.loader.exec_module(client)
import apx2
image=bytes(48)
config=dict(app_id='test.app',version='1',text_bytes=16,ro_offset=16,ro_bytes=16,data_offset=32,data_bytes=16,
            bss_bytes=16,heap_bytes=128,stack_bytes=256,entries=[0,2,4,6,8],data_read_min=1,data_read_max=3,
            data_write_version=2,required_services=1,fixups=[[16,0],[32,0]])
blob=apx2.package(image,config);mac='010203040506';digest=blob[192:224].hex()
class Clock:
    now=0
    def time(self):return self.now
    def sleep(self,n):self.now+=n
class Peer:
    def __init__(self,lose='',terminal='succeeded'):
        self.record=None;self.calls=[];self.lose=lose;self.lost=False;self.commits=0;self.terminal=terminal;self.received=bytearray()
    def __call__(self,method,endpoint,params=None,body=None,binary=False):
        self.calls.append((method,endpoint,dict(params or {})))
        if endpoint=='status':return 200,dict(device_mac=mac,phase='idle',sequence=0,package_max=4096,runtime_reporting=True)
        if endpoint=='update/begin':
            assert body['device_mac']==mac and body['expected_sequence']==0
            if not self.record:self.record=dict(device_mac=mac,phase='receiving',sequence=1,operation_id=params['operation_id'],target_sha256=digest,current_sha256='0'*64,received=0,length=len(blob),chunk_max=64)
            assert params['operation_id']==self.record['operation_id']
        elif endpoint=='update/result':
            if not self.record:return 404,dict(device_mac=mac,error_code='receipt_expired')
            assert params['operation_id']==self.record['operation_id']
            if self.record['phase']=='trial_started':
                self.record['phase']=self.terminal
                if self.terminal=='succeeded':
                    self.record['current_sha256']=digest
                    self.record['runtime']=dict(state='running',generation=1,sha256=digest,version='1',business_writes=True)
        elif endpoint=='update/chunk':
            assert hashlib.sha256(body).hexdigest()==params['sha256']
            assert params['offset']==len(self.received);self.received.extend(body)
            self.record['received']=len(self.received)
        elif endpoint=='update/commit':
            assert bytes(self.received)==blob;self.commits+=1;assert self.commits==1;self.record['phase']='trial_started'
        elif endpoint=='update/cancel':
            self.record['phase']='cancelled'
        else:raise AssertionError(endpoint)
        if endpoint==self.lose and not self.lost:self.lost=True;raise client.Uncertain('lost response')
        return (200 if self.record['phase'] in client.TERMINAL else 202),dict(self.record)

def installer(peer,path,clock,budget=10):return client.Installer(peer,mac,'test:18080',path,budget,clock.time,clock.sleep)
with tempfile.TemporaryDirectory(prefix='app-client-') as folder:
    root=Path(folder)
    for index,lose in enumerate(('', 'update/begin','update/chunk','update/commit')):
        peer=Peer(lose);clock=Clock();path=root/str(index)
        result=installer(peer,path,clock).install(blob)
        assert result['phase']=='succeeded' and peer.commits==1
        assert bytes(peer.received)==blob
        ids={p['operation_id'] for _,_,p in peer.calls if 'operation_id' in p};assert len(ids)==1
        saved=json.loads(path.read_text());assert 'code' not in saved and saved['operation_id'] in ids
        # Resuming a successful receipt only queries; no second begin/commit.
        count=len(peer.calls);assert installer(peer,path,clock).install(blob)['phase']=='succeeded'
        assert [call[1] for call in peer.calls[count:]]==['update/result']
        if lose:
            index=next(i for i,c in enumerate(peer.calls) if c[1]==lose)
            assert peer.calls[index+1][1]=='update/result'
    for phase in ('failed_rolled_back','cancelled','recovery_required'):
        peer=Peer(terminal=phase);assert installer(peer,root/phase,Clock()).install(blob)['phase']==phase
    unsupported_calls=[]
    def unsupported(method,endpoint,*args):
        unsupported_calls.append(endpoint)
        return 200,dict(device_mac=mac,phase='idle',sequence=0,package_max=4096,runtime_reporting=False)
    try:installer(unsupported,root/'unsupported',Clock()).install(blob)
    except ValueError:pass
    else:raise AssertionError('upload started without runtime identity capability')
    assert unsupported_calls==['status'] and not (root/'unsupported').exists()
    # A historical succeeded receipt does not prove the target still runs.
    for index, runtime in enumerate((None, dict(state='recovery',generation=0),
            dict(state='running',generation=True,sha256=digest,version='1',business_writes=True),
            dict(state='running',generation=1,sha256=digest,version='1',business_writes=False))):
        source=json.loads((root/'0').read_text());path=root/('runtime-'+str(index))
        path.write_text(json.dumps(source));calls=[];value=dict(source['result']);value['runtime']=runtime
        def stale(method,endpoint,*args):calls.append((method,endpoint));return 200,value
        clock=Clock()
        try:installer(stale,path,clock,1).install(blob)
        except client.Uncertain:pass
        else:raise AssertionError('historical success accepted without live runtime')
        assert clock.now==1 and set(calls)=={('GET','update/result')}
    for field,bad in (('sha256','0'*64),('version','wrong')):
        source=json.loads((root/'0').read_text());path=root/('wrong-runtime-'+field)
        path.write_text(json.dumps(source));value=source['result'];value['runtime'][field]=bad
        def wrong(*args):return 200,value
        try:installer(wrong,path,Clock()).install(blob)
        except ValueError:pass
        else:raise AssertionError('wrong running identity accepted')
    # Lost query responses exhaust a fixed budget without any mutations.
    path=root/'0';clock=Clock();calls=[]
    def absent(method,endpoint,*args):calls.append(endpoint);raise client.Uncertain('offline')
    try:installer(absent,path,clock,1).install(blob)
    except client.Uncertain:pass
    else:raise AssertionError('unbounded retry')
    assert calls and set(calls)=={'update/result'} and clock.now==1
    before=path.read_bytes()
    try:installer(Peer(),path,Clock()).install(blob[:-1])
    except ValueError:pass
    else:raise AssertionError('corrupt package accepted')
    assert path.read_bytes()==before
    # Cancellation also queries an ambiguous ACK, without another transaction.
    pending=json.loads(path.read_text());pending.pop('result');cancel_path=root/'cancel-pending'
    cancel_path.write_text(json.dumps(pending))
    peer=Peer('update/cancel');peer.record=dict(device_mac=mac,phase='ready',sequence=3,
        operation_id=pending['operation_id'],target_sha256=digest,current_sha256='0'*64,
        received=len(blob),length=len(blob),chunk_max=64)
    assert installer(peer,cancel_path,Clock()).cancel()['phase']=='cancelled'
    assert [c[1] for c in peer.calls]==['update/result','update/cancel','update/result']
    # Resume binds endpoint/device/package, including after process restart.
    try:client.Installer(Peer(),mac,'other:18080',path).install(blob)
    except ValueError:pass
    else:raise AssertionError('foreign endpoint accepted')
print('client: begin/chunk/commit lost ACK query, one operation, receipt resume, terminal distinctions, budget, identity/package fences passed')
