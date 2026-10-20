"""Authenticated, read-only 0041 maintenance diagnostics. Never print file data."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
import zlib


def request(host, token, mac, operation, body=None):
    url = f'http://{host}/api/diagnostic/{operation}'
    data = None if body is None else json.dumps(dict(body, device_mac=mac)).encode()
    query = urllib.request.Request(url, data=data, headers={
        'Authorization': 'Bearer '+token, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(query, timeout=15) as response:
        if response.status != 200:
            raise ValueError('unexpected HTTP status')
        value = json.loads(response.read(8192))
    if value.get('device_mac') != mac or value.get('protocol') != 'ap01-diagnostic-0041-v1':
        raise ValueError('device identity or protocol mismatch')
    return value


def chunk(value, offset, length, boot):
    if value.get('boot_id') != boot or value.get('offset') != offset:
        raise ValueError('boot changed or offset mismatch')
    raw = bytes.fromhex(value['data_hex'])
    if len(raw) != value['length'] or len(raw) > length or zlib.crc32(raw) != value['crc32']:
        raise ValueError('chunk length/CRC mismatch')
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True, help='IP:port of the maintenance service')
    parser.add_argument('--token-file', type=Path, required=True, help='existing registered device-token JSON')
    parser.add_argument('--mac', default='34F01557210B')
    parser.add_argument('--operation', choices=('status', 'file', 'flash'), default='status')
    parser.add_argument('--path', help='absolute /data or /resource filename, or /dev/ramlog')
    parser.add_argument('--offset', type=lambda s:int(s,0), default=0)
    parser.add_argument('--length', type=lambda s:int(s,0))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    credential = json.loads(args.token_file.read_text(encoding='utf-8-sig'))
    if credential.get('device_mac') != args.mac:
        parser.error('registered MAC mismatch')
    token = credential['token']
    status = request(args.host, token, args.mac, 'status')
    if args.operation == 'status':
        print(json.dumps(status));return
    if not args.output or args.offset < 0 or (args.length is not None and args.length <= 0):
        parser.error('export needs a new output file and a valid range')
    if args.operation == 'file' and not args.path:
        parser.error('file export requires --path')
    if args.operation == 'flash' and (args.length is None or args.offset > 0x1000000 or args.length > 0x1000000-args.offset):
        parser.error('flash export requires an explicit range within 16 MiB')
    partial = args.output.with_name(args.output.name+'.partial')
    metadata = args.output.with_name(args.output.name+'.json')
    if args.output.exists() or partial.exists() or metadata.exists():
        parser.error('output/partial/metadata already exists; never overwrite evidence')
    start = offset = args.offset
    remaining = args.length
    total = None
    digest = hashlib.sha256()
    descriptor = os.open(partial, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as output:
        while remaining is None or remaining:
            size = min(1024,remaining) if remaining is not None else 1024
            body = {'offset':offset,'length':size}
            if args.path:body['path']=args.path
            value = request(args.host,token,args.mac,args.operation,body)
            raw = chunk(value,offset,size,status['boot_id'])
            observed = value.get('total_bytes')
            if total is not None and observed != total:
                raise ValueError('file size changed during export')
            total = observed
            if args.operation == 'flash' and len(raw) != size:
                raise ValueError('short physical read')
            output.write(raw);digest.update(raw);offset+=len(raw)
            if remaining is not None:remaining-=len(raw)
            if observed is None:
                # Nonblocking ramlog is a bounded sample, including an empty sample.
                break
            if value.get('eof'):
                if remaining not in (None,0):raise ValueError('EOF before requested length')
                break
            if not raw:raise ValueError('no progress')
    final = request(args.host,token,args.mac,'status')
    if final['boot_id'] != status['boot_id']:
        raise ValueError('device rebooted during export')
    # Publish without replacing a file created after the initial existence check.
    os.link(partial, args.output)
    partial.unlink()
    result = {'device_mac':args.mac,'boot_id':status['boot_id'],'operation':args.operation,
              'path':args.path,'offset':start,'bytes':offset-start,'total_bytes':total,
              'sha256':digest.hexdigest(),'transport_crc_verified':True,
              'consistency':'per-chunk reads; not an atomic filesystem/Flash snapshot'}
    with metadata.open('x',encoding='utf-8') as output:json.dump(result,output,indent=2)
    print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except (OSError,ValueError,KeyError) as error:
        # HTTP errors can contain private server data; print only the class/status.
        print('Diagnostic stopped:',type(error).__name__,getattr(error,'code',''))
        raise SystemExit(2)
