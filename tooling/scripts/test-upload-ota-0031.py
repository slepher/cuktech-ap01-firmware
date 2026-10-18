#!/usr/bin/env python3
"""Exercise single-attempt updater with fake hello/HTTP; no network/device."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
from unittest.mock import patch


def main():
    root=Path(__file__).resolve().parents[2]
    directory=root/'evidence/private/ota-expansion-20261018'
    spec=importlib.util.spec_from_file_location('updater',Path(__file__).with_name('upload-ota-0031.py'))
    u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
    checks=[];calls=[];scenario='success'
    image=root/'roms/0031/candidates/ota-channel-tail-0031-v2.bin'
    expected=image.read_bytes()

    class Hello:
        def __init__(self,*args,**kwargs):pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def settimeout(self,*args):pass
        def sendto(self,*args):pass
        def recvfrom(self,*args):
            return bytes.fromhex('21310020')+bytes(4)+struct.pack('>II',2232184842,123)+bytes(16),('192.168.3.191',54321)

    class Response:
        @property
        def status(self):return 400 if scenario=='rejected' else 200
        def read(self,*args):
            return json.dumps({'stage':'begin','error':'writer','bytes':0} if scenario=='rejected'
                              else {'stage':'done','error':'ok','bytes':len(expected)}).encode()

    class Connection:
        def __init__(self,*args,**kwargs):pass
        def close(self):pass
        def request(self,method,path,body,headers):
            assert method=='POST' and path=='/firmware' and body==expected
            assert headers['Content-Length']==str(len(body))
            assert headers['X-ROM-CRC32']==f'{u.zlib.crc32(body):08x}'
            calls.append(hashlib.sha256(body).hexdigest())
            if scenario=='lost_response':raise OSError('simulated lost reply')
        def getresponse(self):return Response()

    with tempfile.TemporaryDirectory(prefix='updater-check-',dir=directory) as temporary:
        for scenario in ('success','lost_response','rejected','check_only'):
            task=Path(temporary)/scenario
            argv=['upload','--image',str(image),'--manifest',str(image.with_suffix('.manifest.json')),
                  '--auth-key-file',str(root/'evidence/qemu/0031-20261017/ota-channel-a-0031.auth-key'),
                  '--validation-report',str(directory/'validation-summary.json'),
                  '--task-directory',str(task),'--host','192.168.3.191','--device-id','2232184842',
                  '--expect-version','old','--new-version','new']
            if scenario=='check_only':argv.append('--check-only')
            before=len(calls)
            with patch.object(sys,'argv',argv),patch.object(u.socket,'socket',Hello),patch.object(
                    u.http.client,'HTTPConnection',Connection),patch.object(u,'health',side_effect=['old','new']),contextlib.redirect_stdout(io.StringIO()):
                try:u.main()
                except RuntimeError:assert scenario=='rejected'
                else:assert scenario!='rejected'
            assert len(calls)-before==(0 if scenario=='check_only' else 1)
            if scenario=='check_only':assert not (task/'task.json').exists()
            else:
                result=json.loads((task/'task.json').read_text())
                assert result['state']==('rejected' if scenario=='rejected' else 'new_service_verified')
                with patch.object(sys,'argv',argv),contextlib.redirect_stderr(io.StringIO()):
                    try:u.main()
                    except SystemExit as exc:assert exc.code==2
                    else:raise AssertionError('duplicate task accepted')
                assert len(calls)==before+1
            checks.append(scenario)
    report=dict(passed=True,checks=checks,network_accessed=False,device_accessed=False)
    with (directory/'uploader-tests.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(report))


if __name__=='__main__':main()
