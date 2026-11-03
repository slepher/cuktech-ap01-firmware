"""Real client HTTP serialization -> C++ parser/auth/journal; framed pipes, no network.

Build test-http first with test-app-http-0041.py. Guest instructions do not run;
the production runner invokes host entries using virtual time and platform counters. No device is contacted.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import select
import struct
import subprocess
import tempfile
import time
import urllib.parse

spec=importlib.util.spec_from_file_location('client',Path(__file__).with_name('app-update-client-0041.py'))
client=importlib.util.module_from_spec(spec);spec.loader.exec_module(client)
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--binary',type=Path,required=True)
p.add_argument('--package',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
if not a.out.is_dir():p.error('Precreate output directory')

class Response(io.BytesIO):
    def __init__(self,code,body):super().__init__(body);self.code=code
class PipePeer:
    def __init__(self,process,lose):self.process=process;self.lose=lose;self.lost=False;self.calls=[]
    def exact(self,n):
        chunks=[];deadline=time.monotonic()+10
        while n:
            remaining=deadline-time.monotonic()
            if remaining<=0 or not select.select([self.process.stdout],[],[],remaining)[0]:
                raise RuntimeError('C++ HTTP fixture timed out')
            part=os.read(self.process.stdout.fileno(),n)
            if not part:raise RuntimeError('C++ HTTP fixture exited unexpectedly')
            chunks.append(part);n-=len(part)
        return b''.join(chunks)
    def open(self,request,timeout):
        assert 0<timeout<=15
        parsed=urllib.parse.urlsplit(request.full_url)
        target=parsed.path+('?' + parsed.query if parsed.query else '')
        body=request.data or b''
        header=request.get_method()+' '+target+' HTTP/1.1\r\n'
        header+=''.join(k+': '+v+'\r\n' for k,v in request.header_items())
        header+='Content-Length: '+str(len(body))+'\r\n\r\n'
        wire=header.encode()+body
        self.process.stdin.write(struct.pack('<I',len(wire))+wire);self.process.stdin.flush()
        length=struct.unpack('<I',self.exact(4))[0];assert length<=8192
        response=self.exact(length);headers,payload=response.split(b'\r\n\r\n',1)
        status=int(headers.split(b' ',2)[1]);endpoint=parsed.path.rsplit('/',1)[-1]
        self.calls.append((request.get_method(),endpoint,urllib.parse.parse_qs(parsed.query)))
        if endpoint==self.lose and not self.lost:
            self.lost=True;raise OSError('injected lost HTTP reply after server commit')
        return Response(status,payload)
class Clock:
    now=0
    def time(self):return self.now
    def sleep(self,n):self.now+=n

report={'passed':False,'network_accessed':False,'app_code_executed':False,'health_clock':'simulated','entry_backend':'host callbacks via production installer','scenarios':[]}
report_path=a.out/'client-http-report.json';report_path.write_text(json.dumps(report)+'\n')
blob=a.package.read_bytes()
for lose in ('','begin','chunk','commit'):
    with tempfile.TemporaryDirectory(prefix='client-http-',dir=a.out.resolve()) as directory:
        root=Path(directory);state=root/'state';state.mkdir()
        with (root/'server.stderr').open('wb') as errors:
            process=subprocess.Popen([str(a.binary.resolve()),str(state),str(a.package.resolve()),'--serve'],
                                     stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors)
            try:
                peer=PipePeer(process,lose);clock=Clock()
                transport=client.Transport('fixture:18080','01234567','010203040506');transport.opener=peer
                receipt=root/'receipt.json'
                installer=client.Installer(transport,'010203040506','fixture:18080',receipt,180,clock.time,clock.sleep)
                result=installer.install(blob)
                assert result['phase']=='succeeded' and result['current_sha256']==blob[192:224].hex()
                assert (state/'app-current.apx2').read_bytes()==blob
                counts=Counter(endpoint for method,endpoint,_ in peer.calls if method!='GET')
                assert counts==dict(begin=1,chunk=1,commit=1),counts
                ids={params['operation_id'][0] for _,_,params in peer.calls if 'operation_id' in params}
                assert len(ids)==1 and json.loads(receipt.read_text())['operation_id'] in ids
                if lose:
                    index=next(i for i,(_,endpoint,_) in enumerate(peer.calls) if endpoint==lose)
                    assert peer.calls[index+1][1]=='result'
                before=len(peer.calls)
                repeated=client.Installer(transport,'010203040506','fixture:18080',receipt,180,clock.time,clock.sleep).install(blob)
                assert repeated['phase']=='succeeded' and len(peer.calls)==before+1 and peer.calls[-1][1]=='result'
                # Upgrade a running instance. prepare_stop returns Pending once;
                # querying Ready must not restart old code before commit retry.
                upgraded=bytearray(blob);upgraded[160]=ord('2');upgraded[192:224]=bytes(32)
                upgraded[192:224]=hashlib.sha256(upgraded).digest();upgraded=bytes(upgraded)
                before_upgrade=len(peer.calls)
                second=client.Installer(transport,'010203040506','fixture:18080',root/'upgrade.json',180,clock.time,clock.sleep).install(upgraded)
                assert second['phase']=='succeeded' and second['current_sha256']==upgraded[192:224].hex()
                assert (state/'app-current.apx2').read_bytes()==upgraded
                assert not (state/'app-incoming.apx2').exists()
                upgrades=Counter(endpoint for method,endpoint,_ in peer.calls[before_upgrade:] if method!='GET')
                assert upgrades==dict(begin=1,chunk=1,commit=2),upgrades
                report['scenarios'].append({'lost_reply':lose or None,'requests':len(peer.calls),'mutations':dict(counts),
                                            'phase':result['phase'],'upgrade_mutations':dict(upgrades),'virtual_client_seconds':clock.now})
            except BaseException:
                print((root/'server.stderr').read_text())
                raise
            finally:
                process.stdin.close()
                try:code=process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill();process.wait();raise
                process.stdout.close()
            assert code==0,(root/'server.stderr').read_text()
report.update(passed=True,binary_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),
              package_sha256=hashlib.sha256(blob).hexdigest(),
              client_sha256=hashlib.sha256(Path(client.__file__).read_bytes()).hexdigest())
report_path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
