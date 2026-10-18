#!/usr/bin/env python3
"""Single-attempt authenticated update, gated by reconstructed image and offline evidence."""
import argparse
import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import socket
import struct
import sys
import time
import zlib

sys.dont_write_bytecode = True


def host_path(value):
    if os.name == 'nt' and value.startswith('/mnt/') and len(value)>7 and value[6]=='/':
        return value[5].upper()+':/'+value[7:]
    return value


def health(host, port, key):
    connection=http.client.HTTPConnection(host,port,timeout=4)
    try:
        connection.request('GET','/health',headers={'Authorization':'Bearer '+key,'Connection':'close'})
        response=connection.getresponse();body=response.read(4096)
        if response.status!=200:raise RuntimeError('health rejected')
        return json.loads(body)['version']
    finally:connection.close()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('image','manifest','auth-key-file','validation-report','task-directory'):
        p.add_argument('--'+name,type=Path,required=True)
    for name in ('host','device-id','expect-version','new-version'):
        p.add_argument('--'+name,required=True)
    p.add_argument('--port',type=int,default=18080)
    p.add_argument('--check-only',action='store_true')
    a=p.parse_args();directory=a.task_directory.resolve()
    directory.mkdir(parents=True,exist_ok=True)
    marker=directory/'task.json'
    if marker.exists() and not a.check_only:p.error('existing task; do not redispatch')
    manifest=json.loads(a.manifest.read_text(encoding='utf-8'))
    if manifest.get('format')!='ap01-ota-channel-0031-v2':p.error('expanded format required')
    data=a.image.read_bytes();digest=hashlib.sha256(data).hexdigest()
    evidence=json.loads(a.validation_report.read_text(encoding='utf-8'))
    if not evidence.get('passed') or digest not in evidence.get('validated_images',[]):
        p.error('image not covered by passing upgrade evidence')
    for field in ('original','payload','image'):
        manifest[field]['path']=host_path(manifest[field]['path'])
    relocated=directory/'local.manifest.json'
    relocated.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    spec=importlib.util.spec_from_file_location('builder',Path(__file__).with_name('build-ota-expanded-0031.py'))
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    builder.validate_candidate(data,relocated)
    key=a.auth_key_file.read_text(encoding='ascii').strip()
    if len(key)!=64 or hashlib.sha256(key.encode('ascii')).hexdigest()!=manifest['auth_key_sha256']:
        p.error('authentication key identity mismatch')
    # A valid miIO hello binds the specified address to the selected device ID.
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as probe:
        probe.settimeout(4);probe.sendto(bytes.fromhex('21310020')+b'\xff'*28,(a.host,54321))
        reply,address=probe.recvfrom(1024)
    if address[0]!=a.host or len(reply)!=32 or reply[:4]!=bytes.fromhex('21310020') or str(struct.unpack_from('>I',reply,8)[0])!=a.device_id:
        p.error('device identity mismatch')
    if health(a.host,a.port,key)!=a.expect_version:p.error('running version changed')
    record=dict(host=a.host,device_id=a.device_id,image_sha256=digest,image_bytes=len(data),
                expected_before=a.expect_version,expected_after=a.new_version,
                created_epoch=int(time.time()),state='checked',redispatch_allowed=False)
    if a.check_only:
        print(json.dumps(record));return
    record['state']='sending'
    with marker.open('x',encoding='utf-8') as f:
        json.dump(record,f,indent=2);f.flush();os.fsync(f.fileno())
    connection=http.client.HTTPConnection(a.host,a.port,timeout=300)
    try:
        connection.request('POST','/firmware',body=data,headers={
            'Authorization':'Bearer '+key,'Content-Type':'application/octet-stream',
            'Content-Length':str(len(data)),'X-ROM-CRC32':f'{zlib.crc32(data):08x}',
            'Connection':'close'})
        response=connection.getresponse();body=response.read(8192)
        record['http_status']=response.status;record['response']=json.loads(body)
        if response.status!=200 or record['response']!={'stage':'done','error':'ok','bytes':len(data)}:
            record['state']='rejected'
        else:record['state']='accepted'
    except Exception as e:
        record.update(state='outcome_unknown',exception_type=type(e).__name__)
    finally:
        connection.close();marker.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record),flush=True)
    if record['state']=='rejected':raise RuntimeError('device rejected upload; no retry')
    deadline=time.monotonic()+120
    while time.monotonic()<deadline:
        try:
            version=health(a.host,a.port,key)
            if version==a.new_version:
                record.update(state='new_service_verified',health_version=version,verified_epoch=int(time.time()))
                marker.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
                print(json.dumps(record),flush=True);return
        except (OSError,ValueError,KeyError,http.client.HTTPException,RuntimeError):pass
        time.sleep(3)
    record['state']='outcome_unknown'
    marker.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    raise RuntimeError('new service not verified; observe only, no retry')


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('STOPPED: '+type(exc).__name__,flush=True)
        sys.exit(2)
