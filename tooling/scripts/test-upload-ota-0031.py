#!/usr/bin/env python3
"""Single-attempt updater with reconstructed synthetic image and fake transports."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True


def load(name, filename):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(filename))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def main():
    root=Path(__file__).resolve().parents[2]
    u=load('updater','upload-ota-0031.py');b=load('builder','build-ota-expanded-0031.py')
    checks=[];calls=[];scenario='success'
    with tempfile.TemporaryDirectory(prefix='updater-check-',dir=root) as temporary:
        work=Path(temporary);image=work/'image.bin';payload_path=work/'payload.bin'
        original=root/'roms/0031/ap01-1.0.2_0031.bin';base=b.legacy.read_base(original)
        payload=bytearray(512);payload[:8]=b'AP01HTTP'
        length=((b.TAIL_OFFSET+len(payload)+15)&~15)+40
        start=b.legacy.BASE+b.TAIL_OFFSET
        struct.pack_into('<7I',payload,8,2,length,b.TAIL_OFFSET,len(payload),start+256,u.zlib.crc32(payload[256:]),0)
        struct.pack_into('<3I',payload,52,8192,18080,2)
        b.legacy.menu_manifest(payload,{name:start+256+i*16 for i,(_,_,name) in enumerate(b.legacy.MENU_HOOKS)},required=True)
        struct.pack_into('<I',payload,32,u.zlib.crc32(payload[:256]))
        expected,_=b.assemble(base,payload,'http');image.write_bytes(expected);payload_path.write_bytes(payload)
        manifest=dict(format=b.HTTP_FORMAT,mode='http',extra_padding=0,
            original=dict(path=str(original)),payload=dict(path=str(payload_path),sha256=b.legacy.sha(payload)),
            image=dict(path=str(image),sha256=b.legacy.sha(expected)),cloud_ota_dispatch_modified=False,
            original_gif_preserved=True,credential_source='device-menu-8digit',per_device_credential=True)
        manifest_path=work/'manifest.json';manifest_path.write_text(json.dumps(manifest))
        report=work/'validation.json';report.write_text(json.dumps(dict(passed=True,validated_images=[b.legacy.sha(expected)])))
        keyfile=work/'current-code';keyfile.write_text('12345678')

        class Hello:
            def __init__(self,*args,**kwargs):pass
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def settimeout(self,*args):pass
            def sendto(self,*args):pass
            def recvfrom(self,*args):
                return bytes.fromhex('21310020')+bytes(4)+struct.pack('>II',2232184842,123)+bytes(16),('192.0.2.1',54321)

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
                assert headers['Authorization']=='Bearer '+keyfile.read_text()
                calls.append(b.legacy.sha(body))
                if scenario=='lost_response':raise OSError('simulated lost reply')
            def getresponse(self):return Response()

        for scenario in ('success','legacy_migration','lost_response','rejected','check_only'):
            keyfile.write_text('a'*64 if scenario=='legacy_migration' else '12345678')
            task=work/scenario
            argv=['upload','--image',str(image),'--manifest',str(manifest_path),
                  '--auth-key-file',str(keyfile),'--validation-report',str(report),
                  '--task-directory',str(task),'--host','192.0.2.1','--device-id','2232184842',
                  '--expect-version','old','--new-version','new']
            if scenario=='check_only':argv.append('--check-only')
            before=len(calls);stdout=io.StringIO()
            with patch.object(sys,'argv',argv),patch.object(u.socket,'socket',Hello),patch.object(
                    u.http.client,'HTTPConnection',Connection),patch.object(u,'health',side_effect=['old','new']) as health,contextlib.redirect_stdout(stdout):
                try:u.main()
                except RuntimeError:assert scenario=='rejected'
                else:assert scenario!='rejected'
            assert len(calls)-before==(0 if scenario=='check_only' else 1)
            assert health.call_args_list[0].args==('192.0.2.1',18080,keyfile.read_text())
            assert keyfile.read_text() not in stdout.getvalue()
            if scenario=='check_only':assert not (task/'task.json').exists()
            else:
                result=json.loads((task/'task.json').read_text())
                assert result['state']==('rejected' if scenario=='rejected' else 'new_service_observed')
                if scenario!='rejected':
                    assert result['authentication_verified'] is False
                    assert health.call_args_list[1].args==('192.0.2.1',18080)
                with patch.object(sys,'argv',argv),contextlib.redirect_stderr(io.StringIO()):
                    try:u.main()
                    except SystemExit as exc:assert exc.code==2
                    else:raise AssertionError('duplicate task accepted')
                assert len(calls)==before+1
            checks.append(scenario)
    print(json.dumps(dict(passed=True,checks=checks,network_accessed=False,device_accessed=False)))


if __name__=='__main__':main()
