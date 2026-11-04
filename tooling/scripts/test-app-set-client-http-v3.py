"""Python v3 CLI against production C++ HTTP/transaction code over pipes, offline."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import select
import socketserver
import threading
import struct
import subprocess
import tempfile
import urllib.parse
from app_set_client_v3 import inspect_manifest

spec=importlib.util.spec_from_file_location('set_cli',Path(__file__).with_name('app-set-client-v3.py'))
client=importlib.util.module_from_spec(spec);spec.loader.exec_module(client)
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--binary',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True)
p.add_argument('--package',type=Path,action='append',required=True);p.add_argument('--report',type=Path,required=True)
p.add_argument('--tcp',action='store_true',help='Use real urllib and a loopback-only TCP relay')
a=p.parse_args();original=a.manifest.read_bytes();base=inspect_manifest(original)
packages={b[128:160].split(b'\0')[0].decode():b for b in [x.read_bytes() for x in a.package]}
mac='010203040506';host='offline.invalid:18080'
a.report.write_text(json.dumps({'passed':False,'stage':'running'})+'\n')

class Clock:
    now=0
    def time(self):return self.now
    def sleep(self,n):self.now+=n

class Peer:
    def __init__(self):
        self.process=subprocess.Popen([str(a.binary.resolve()),'--http-peer'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        self.lose='';self.calls=[];self.server=None;self.worker=None;self.errors=[]
    def exchange(self,line):
        self.process.stdin.write(line.encode()+b'\n');self.process.stdin.flush()
        if not select.select([self.process.stdout],[],[],10)[0]:raise RuntimeError('C++ peer response timeout')
        out=self.process.stdout.readline()
        if not out:raise RuntimeError('C++ peer exited')
        return out.decode().strip()
    def __call__(self,method,endpoint,params=None,body=None,binary=False):
        self.calls.append((method,endpoint,dict(params or {})))
        path='/api/app/v3/'+endpoint
        if params:path+='?'+urllib.parse.urlencode(dict(params,device_mac=mac))
        payload=body or b'';assert not payload or binary
        header=f'{method} {path} HTTP/1.1\r\nAuthorization: Bearer 01234567\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(payload)}\r\n\r\n'
        response=bytes.fromhex(self.exchange((header.encode()+payload).hex()))
        head,data=response.split(b'\r\n\r\n',1);status=int(head.split(b' ')[1]);value=json.loads(data)
        if self.lose and endpoint.endswith(self.lose):
            self.lose='';raise client.Uncertain('injected lost response after C++ handling')
        return status,value
    def start_tcp(self):
        peer=self
        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                try:
                    self.request.settimeout(5);raw=bytearray()
                    while b'\r\n\r\n' not in raw:
                        block=self.request.recv(1024)
                        if not block:raise RuntimeError('incomplete test request')
                        raw.extend(block)
                        if len(raw)>8192:raise RuntimeError('test header bound')
                    header,body=bytes(raw).split(b'\r\n\r\n',1)
                    lines=header.decode('ascii').split('\r\n');method,path,_=lines[0].split(' ')
                    headers=dict(line.split(':',1) for line in lines[1:])
                    length=int(next((v for k,v in headers.items() if k.lower()=='content-length'),'0'))
                    if not 0<=length<=4096:raise RuntimeError('test body bound')
                    while len(body)<length:
                        block=self.request.recv(length-len(body))
                        if not block:raise RuntimeError('incomplete test body')
                        body+=block
                    parsed=urllib.parse.urlsplit(path);endpoint=parsed.path.removeprefix('/api/app/v3/')
                    params=dict(urllib.parse.parse_qsl(parsed.query));peer.calls.append((method,endpoint,params))
                    response=bytes.fromhex(peer.exchange((header+b'\r\n\r\n'+body).hex()))
                    if peer.lose and endpoint.endswith(peer.lose):
                        peer.lose=''
                        if endpoint.endswith(('chunk','ready')):
                            self.request.sendall(response[:-8])  # Declared Content-Length is not fulfilled.
                        return  # Close TCP only after the production handler has executed.
                    for offset in range(0,len(response),53):self.request.sendall(response[offset:offset+53])
                except Exception as error:
                    peer.errors.append(repr(error))
        self.server=socketserver.TCPServer(('127.0.0.1',0),Handler)
        self.worker=threading.Thread(target=self.server.serve_forever,daemon=True);self.worker.start()
        return '127.0.0.1:'+str(self.server.server_address[1])
    def close(self):
        if self.server:
            self.server.shutdown();self.server.server_close();self.worker.join(timeout=5)
        self.process.stdin.close()
        try:assert self.process.wait(timeout=10)==0
        finally:
            if self.process.poll() is None:self.process.kill();self.process.wait()
            self.process.stdout.close()


def generation(number,mask):
    manifest=bytearray(original);struct.pack_into('<Q',manifest,16,base['version']+number)
    supplied=[]
    for entry in base['apps']:
        i=entry['index'];package=bytearray(packages[entry['app_id']])
        # Generation 2+ changes both; generation 1 changes A only.
        version_number=number if mask&(1<<i) else 0
        if version_number:
            version=f'cross-{version_number}'.encode();package[160:192]=version+bytes(32-len(version))
            package[192:224]=bytes(32);package[192:224]=hashlib.sha256(package).digest()
        manifest[64+160*i+32:64+160*i+96]=package[160:224]
        if mask&(1<<i):supplied.append(bytes(package))
    deps=struct.unpack_from('<H',manifest,24)[0]
    for i in range(deps):
        at=64+160*len(base['apps'])+40*i;target=struct.unpack_from('<H',manifest,at+2)[0]
        manifest[at+8:at+40]=manifest[64+160*target+64:64+160*target+96]
    manifest[32:64]=bytes(32);manifest[32:64]=hashlib.sha256(manifest).digest()
    return bytes(manifest),supplied

peer=Peer();results=[]
try:
    if a.tcp:host=peer.start_tcp()
    request=client.Transport(host,'01234567',mac) if a.tcp else peer
    with tempfile.TemporaryDirectory(prefix='set-http-client-') as folder:
        for n,mask,lose in ((0,3,'begin'),(1,1,'chunk'),(2,3,'commit'),(3,3,'ready')):
            if n==3:assert peer.exchange('FAIL_TRIAL')=='OK'
            peer.lose=lose;manifest,blobs=generation(n,mask);clock=Clock();before=len(peer.calls)
            receipt=Path(folder)/f'{n}.json'
            value=client.Installer(request,mac,host,receipt,180,clock.time,clock.sleep).install(manifest,blobs)
            assert value['phase']==('failed_rolled_back' if n==3 else 'succeeded')
            assert value['changed_mask']==mask and len({params['operation_id'] for _,_,params in peer.calls[before:] if params})==1
            assert len([1 for method,endpoint,_ in peer.calls[before:] if endpoint=='update/commit' and method=='POST'])==1
            if n==1:
                assert all(not endpoint.startswith('package/1/') for _,endpoint,_ in peer.calls[before:])
            if n==3:
                assert value['runtime']['manifest']==results[-1]['candidate_manifest']
                assert value['runtime']['complete'] and value['runtime']['health_state']=='healthy'
                assert value['runtime']['running']==results[-1]['runtime']['running']
            results.append(value)
        b_id=base['apps'][1]['app_id']
        before_b=next(app for app in results[0]['runtime']['running'] if app['app_id']==b_id)
        after_b=next(app for app in results[1]['runtime']['running'] if app['app_id']==b_id)
        assert before_b==after_b
        assert [r['boot_id'] for r in results]==[12,13,14,16]
finally:peer.close()
assert not peer.errors,peer.errors
report=dict(passed=True,device_accessed=False,app_instructions_executed=False,
            health_injected=True,cpu_reboot_modeled=True,transport='urllib over loopback TCP to C++ HTTP' if a.tcp else 'HTTP bytes over pipes',
            binary_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),results=results)
a.report.write_text(json.dumps(report,indent=2)+'\n')
print('collection CLI/C++ HTTP: first install, A-only with B untouched, A+B, lost replies and whole-set rollback passed; modeled reboot/health, no device access')
