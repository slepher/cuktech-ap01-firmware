"""Build canonical AMF3 full-set manifests from independently built ABI 3 packages.

Input JSON: {sequence, apps:[{package, order, tcp, udp, tasks, pages,
requires:{app_id: APX2_content_sha256}}]}. Paths resolve relative to the JSON.
Resource admission is performed by the target's production manifest reader.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import apx2


def integer(value, maximum):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError('Integer outside declared encoding range')
    return value


def package_info(blob):
    if len(blob) < 256 or blob[:4] != b'APX2':
        raise ValueError('Not APX2')
    u = lambda at: struct.unpack_from('<I', blob, at)[0]
    if u(24) != 3 or u(44) > len(blob)-256 or 256+u(44)+u(112)*8 != len(blob):
        raise ValueError('ABI 3 and exact package bounds required')
    config = dict(abi_major=3, app_id=blob[128:160].split(b'\0')[0].decode('ascii'),
        version=blob[160:192].split(b'\0')[0].decode('ascii'), text_bytes=u(52),
        ro_offset=u(56), ro_bytes=u(60), data_offset=u(64), data_bytes=u(68),
        bss_bytes=u(72), heap_bytes=u(80), stack_bytes=u(84), entries=[u(at) for at in (88,92,96)],
        data_read_min=u(116), data_read_max=u(120), data_write_version=u(124),
        required_services=struct.unpack_from('<Q',blob,32)[0],
        fixups=[list(struct.unpack_from('<II',blob,at)) for at in range(256+u(44),len(blob),8)])
    if apx2.package(blob[256:256+u(44)],config) != blob:
        raise ValueError('Package integrity or canonical encoding mismatch')
    return config


def manifest(config, root):
    if set(config) != {'sequence','apps'} or not isinstance(config['apps'],list):
        raise ValueError('Exact manifest fields required')
    sequence=integer(config['sequence'],2**64-1)
    if not sequence or len(config['apps']) > 8:
        raise ValueError('Nonzero sequence and at most eight format entries required')
    apps=[]
    for item in config['apps']:
        if set(item) != {'package','order','tcp','udp','tasks','pages','requires'}:
            raise ValueError('Exact App fields required')
        blob=(root/item['package']).read_bytes();info=package_info(blob)
        apps.append((info['app_id'],item,blob,info))
    apps.sort(key=lambda a:a[0]);ids=[a[0] for a in apps]
    if len(set(ids)) != len(ids) or any(i in ('.','..') for i in ids):raise ValueError('Duplicate or path-special App ID')
    if sorted(integer(a[1]['order'],7) for a in apps) != list(range(len(apps))):
        raise ValueError('Startup order must be a permutation')
    for protocol in ('tcp','udp'):
        ports=[integer(a[1][protocol],65535) for a in apps if a[1][protocol]!=0]
        if 18080 in ports or len(set(ports))!=len(ports):raise ValueError('Reserved or duplicate port')
    entries=bytearray();dependencies=[]
    for index,(_,item,blob,info) in enumerate(apps):
        b=bytearray(160);b[:96]=blob[128:224]
        values=[len(blob),len(blob)-256-len(info['fixups'])*8+info['bss_bytes'],
                info['heap_bytes'],info['stack_bytes'],info['data_read_min'],info['data_read_max'],info['data_write_version']]
        struct.pack_into('<7IQ5HHI',b,96,*values,info['required_services'],
            integer(item['tcp'],65535),integer(item['udp'],65535),integer(item['order'],7),
            integer(item['tasks'],4),integer(item['pages'],32),0,3)
        if item['tasks']*256>info['stack_bytes']:raise ValueError('Task stack budget')
        entries+=b
        if not isinstance(item['requires'],dict):raise ValueError('requires must map IDs to exact package digests')
        for target,digest in item['requires'].items():
            if target not in ids or target==info['app_id']:raise ValueError('Missing/self dependency')
            n=ids.index(target);expected=bytes.fromhex(digest)
            if len(expected)!=32 or expected!=apps[n][2][192:224] or apps[n][1]['order']>=item['order']:
                raise ValueError('Dependency identity/order mismatch')
            dependencies.append((index,n,expected))
    dependencies.sort();body=entries+b''.join(struct.pack('<HHI',i,j,0)+d for i,j,d in dependencies)
    h=bytearray(64);h[:4]=b'AMF3'
    struct.pack_into('<HHIHHQH',h,4,1,64,64+len(body),len(apps),160,sequence,len(dependencies))
    result=h+body;result[32:64]=hashlib.sha256(result).digest();return bytes(result)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    blob=manifest(json.loads(a.config.read_text()),a.config.resolve().parent)
    with a.output.open('xb') as f:f.write(blob)
    print(json.dumps({'bytes':len(blob),'manifest_digest':blob[32:64].hex(),'hardware_verified':False}))

if __name__=='__main__':main()
