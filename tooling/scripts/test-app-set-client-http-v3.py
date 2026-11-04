"""Python CLI or Rust coordinator against production C++ HTTP/transactions, offline."""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
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
p.add_argument('--rv32-results',action='store_true',help='Use actual james.local Docker RV32 journals/runtime; TCP models temporary unavailability during execution')
p.add_argument('--tool-prefix')
p.add_argument('--qemu-image')
p.add_argument('--expected-image-id')
p.add_argument('--fail-first',action='store_true',help='Fail the initial install, confirm empty rollback, then retry the identical collection')
p.add_argument('--snapshot-dir',type=Path,help='Existing empty directory for exact post-commit model files, before reboot')
p.add_argument('--tcp',action='store_true',help='Use real urllib and a loopback-only TCP relay')
p.add_argument('--rust-bridge',type=Path,help='Run the Bridge core coordinator test from this bridge workspace (requires --tcp and isolated CARGO_TARGET_DIR)')
p.add_argument('--rust-worker',action='store_true',help='Use the Bridge application worker instead of core single steps')
p.add_argument('--rust-ui',action='store_true',help='Run production page functions through a test IPC adapter to the real Rust worker')
a=p.parse_args()
if a.snapshot_dir and (not a.snapshot_dir.is_dir() or any(a.snapshot_dir.iterdir())):p.error('--snapshot-dir must be existing and empty')
if bool(a.qemu_image)!=bool(a.expected_image_id):p.error('supply --qemu-image and --expected-image-id together')
original=a.manifest.read_bytes();base=inspect_manifest(original)
if a.rv32_results and (not a.snapshot_dir or not a.tool_prefix):p.error('--rv32-results needs --snapshot-dir and --tool-prefix')
if a.rv32_results and a.rust_bridge and not (a.rust_worker or a.rust_ui):p.error('RV32 outages require worker/UI, not the single-step test with one-loss assertion')
if a.fail_first and a.rust_bridge and not a.rust_ui:p.error('--fail-first uses Python CLI or UI UUIDs; fixed-ID core/worker tests cannot retry the same version')
if a.rust_worker and not a.rust_bridge:p.error('--rust-worker requires --rust-bridge')
if a.rust_ui and not a.rust_bridge:p.error('--rust-ui requires --rust-bridge')
if a.rust_bridge and (not a.tcp or not os.environ.get('CARGO_TARGET_DIR')):
    p.error('--rust-bridge requires --tcp and an isolated CARGO_TARGET_DIR')
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
        self.exchange_lock=threading.Lock();self.rebooting=threading.Event();self.reboot_worker=None;self.offline_requests=0
        self.executions=[];self.failed=False;self.snapshots=[];self.lose='';self.calls=[];self.server=None;self.worker=None;self.errors=[]
    def exchange(self,line):
        with self.exchange_lock:
            self.process.stdin.write(line.encode()+b'\n');self.process.stdin.flush()
            if not select.select([self.process.stdout],[],[],10)[0]:raise RuntimeError('C++ peer response timeout')
            out=self.process.stdout.readline()
            if not out:raise RuntimeError('C++ peer exited')
            return out.decode().strip()
    def snapshot(self,endpoint,response):
        if not a.snapshot_dir or endpoint!='update/commit':return
        head,body=response.split(b'\r\n\r\n',1)
        if int(head.split(b' ')[1]) not in (200,202):return
        reply=json.loads(body)
        if reply.get('phase')!='switch_pending':return
        files=json.loads(self.exchange('SNAPSHOT'))
        assert files and all(path.startswith('/resource/app-store/') for path in files)
        value={'operation_id':reply['operation_id'],'reply':reply,'files':files,
               'captured_before_modeled_reboot':True,'physical_durability_verified':False}
        path=a.snapshot_dir/f'commit-{len(self.snapshots)}.json'
        path.write_text(json.dumps(value,indent=2)+'\n')
        self.snapshots.append({'name':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        if a.rv32_results:
            output=a.snapshot_dir/f'rv32-{len(self.executions)}';output.mkdir()
            command=[sys.executable,'-B',str(Path(__file__).with_name('run-app-set-rv32-result-0041.py')),
                     '--snapshot',str(path),'--out',str(output),'--tool-prefix',a.tool_prefix]
            if self.failed:command.append('--failed')
            if a.qemu_image:command+=['--qemu-image',a.qemu_image,'--expected-image-id',a.expected_image_id]
            self.rebooting.set()
            def finish_reboot():
                success=False
                try:
                    subprocess.run(command,check=True,timeout=180)
                    result=json.loads((output/'result.json').read_text());assert result['snapshot_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
                    blobs=[]
                    for kind in ('journals','runtime'):
                        data=Path(result[kind]['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==result[kind]['sha256'];blobs.append(data.hex())
                    assert self.exchange('APPLY '+' '.join(blobs))=='OK'
                    self.executions.append(result)
                    success=True
                except Exception as error:
                    self.errors.append(repr(error))
                    if not a.tcp:raise
                finally:
                    if success:self.rebooting.clear()
            if a.tcp:
                if self.reboot_worker:self.reboot_worker.join(timeout=1)
                assert not self.reboot_worker or not self.reboot_worker.is_alive()
                self.reboot_worker=threading.Thread(target=finish_reboot,daemon=True);self.reboot_worker.start()
            else:finish_reboot()

    def __call__(self,method,endpoint,params=None,body=None,binary=False):
        self.calls.append((method,endpoint,dict(params or {})))
        path='/api/app/v3/'+endpoint
        if params:path+='?'+urllib.parse.urlencode(dict(params,device_mac=mac))
        payload=body or b'';assert not payload or binary
        header=f'{method} {path} HTTP/1.1\r\nAuthorization: Bearer 01234567\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(payload)}\r\n\r\n'
        response=bytes.fromhex(self.exchange((header.encode()+payload).hex()))
        self.snapshot(endpoint,response)
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
                    if peer.rebooting.is_set():
                        peer.offline_requests+=1
                        assert method=='GET' and endpoint=='update/result', 'mutation while rebooting'
                        payload=json.dumps({'protocol':3,'device_mac':mac,'error':'reboot_in_progress'}).encode()
                        self.request.sendall(f'HTTP/1.1 503 Rebooting\r\nContent-Length: {len(payload)}\r\nConnection: close\r\n\r\n'.encode()+payload)
                        return
                    response=bytes.fromhex(peer.exchange((header+b'\r\n\r\n'+body).hex()))
                    peer.snapshot(endpoint,response)
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
        if self.reboot_worker:
            self.reboot_worker.join(timeout=180)
            assert not self.reboot_worker.is_alive(), 'RV32 executor did not finish'
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
        scenarios=([(0,3,'commit',True)] if a.fail_first else [])+[(0,3,'begin',False),(1,1,'chunk',False),(2,3,'commit',False),(3,3,'ready',True)]
        for step,(n,mask,lose,failed) in enumerate(scenarios):
            if failed:assert peer.exchange('FAIL_TRIAL')=='OK'
            peer.failed=failed;peer.lose=lose;manifest,blobs=generation(n,mask);clock=Clock();before=len(peer.calls)
            receipt=Path(folder)/f'{step}.json'
            if a.rust_bridge:
                manifest_path=Path(folder)/f'{n}.amf3';manifest_path.write_bytes(manifest)
                paths=[]
                for i,blob in enumerate(blobs):
                    path=Path(folder)/f'{n}-{i}.apx2';path.write_bytes(blob);paths.append(path)
                result=Path(folder)/f'{n}-result.json'
                env=dict(os.environ,AP01_HTTP_ENDPOINT=host,AP01_MANIFEST=str(manifest_path),
                         AP01_PACKAGE=str(paths[0]),AP01_RECEIPT=str(receipt),AP01_RESULT=str(result),
                         AP01_EXPECT_PHASE='failed_rolled_back' if failed else 'succeeded')
                env.pop('AP01_PEER',None)
                if len(paths)>1:env['AP01_PEER']=str(paths[1])
                target=['-p','bridge-app','ap01_app_update::tests::production_ui_rust_cpp_collection'] if a.rust_ui else ['-p','bridge-app','ap01_app_update::tests::production_cpp_worker_collection'] if a.rust_worker else [
                    '-p','bridge-core','ap01_app_set_install::tests::production_cpp_http_collection','--lib']
                subprocess.run(['cargo','test','--offline',*target,
                                '--','--ignored','--exact'],cwd=a.rust_bridge,env=env,check=True,timeout=180)
                value=json.loads(result.read_text())
            else:
                value=client.Installer(request,mac,host,receipt,180,time.monotonic if a.rv32_results and a.tcp else clock.time,time.sleep if a.rv32_results and a.tcp else clock.sleep).install(manifest,blobs)
            assert value['phase']==('failed_rolled_back' if failed else 'succeeded')
            assert value['changed_mask']==mask and len({params['operation_id'] for _,_,params in peer.calls[before:] if params})==1
            assert len([1 for method,endpoint,_ in peer.calls[before:] if endpoint=='update/commit' and method=='POST'])==1
            if n==1:
                assert all(not endpoint.startswith('package/1/') for _,endpoint,_ in peer.calls[before:])
            if failed and n==0:
                assert value['cleanup_pending'] is False
                assert value['runtime']['complete'] and value['runtime']['health_state']=='healthy'
                assert value['runtime']['manifest']=='00'*32 and value['runtime']['version']==0 and value['runtime']['running']==[]
            if n==3:
                assert value['runtime']['manifest']==results[-1]['candidate_manifest']
                assert value['runtime']['complete'] and value['runtime']['health_state']=='healthy'
                assert value['runtime']['running']==results[-1]['runtime']['running']
            if a.rv32_results:
                raw=Path(peer.executions[-1]['runtime']['path']).read_bytes();runtime=value['runtime']
                assert struct.unpack_from('<Q',raw,8)[0]==value['boot_id']
                assert struct.unpack_from('<Q',raw,16)[0]==runtime['version'] and raw[48:80].hex()==runtime['manifest']
                count,started,complete,state=struct.unpack_from('<IIII',raw,24)
                assert complete==1 and state==1 and count==started==runtime['started_count']==len(runtime['running'])
                for n,app in enumerate(runtime['running']):
                    index=struct.unpack_from('<I',raw,80+104*n+100)[0];at=80+104*index
                    assert app['index']==index and app['app_id']==raw[at:at+32].split(b'\0')[0].decode()
                    assert app['version']==raw[at+32:at+64].split(b'\0')[0].decode() and app['digest']==raw[at+64:at+96].hex()
                    assert app['health']==struct.unpack_from('<i',raw,at+96)[0]==0
            results.append(value)
        b_id=base['apps'][1]['app_id']
        offset=int(a.fail_first)
        if a.fail_first:assert results[0]['operation_id']!=results[1]['operation_id'] and results[0]['candidate_manifest']==results[1]['candidate_manifest']
        before_b=next(app for app in results[offset]['runtime']['running'] if app['app_id']==b_id)
        after_b=next(app for app in results[offset+1]['runtime']['running'] if app['app_id']==b_id)
        assert before_b==after_b
        assert [r['boot_id'] for r in results]==([13,14,15,16,18] if a.fail_first else [12,13,14,16])
finally:peer.close()
assert not peer.errors,peer.errors
if a.rv32_results and a.tcp:assert peer.offline_requests>=len(results)
report=dict(passed=True,device_accessed=False,app_instructions_executed=a.rv32_results,
            health_injected=not a.rv32_results,cpu_reboot_modeled=True,transport='Production UI via test IPC to Rust worker and C++ HTTP' if a.rust_ui else 'Rust application worker over loopback TCP to C++ HTTP' if a.rust_worker else 'Rust core over loopback TCP to C++ HTTP' if a.rust_bridge else 'urllib over loopback TCP to C++ HTTP' if a.tcp else 'HTTP bytes over pipes',
            binary_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),results=results,snapshots=peer.snapshots,first_install_failure_retried=a.fail_first,rv32_results=peer.executions,reboot_query_requests=peer.offline_requests)
a.report.write_text(json.dumps(report,indent=2)+'\n')
print('collection client/C++ HTTP: scenarios passed; '+('actual RV32 journals/runtime returned to the original client' if a.rv32_results else 'modeled reboot/health')+'; no device access')
