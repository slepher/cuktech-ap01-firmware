#!/usr/bin/env python3
"""Check reconstruction, resource preservation and rejection cases; no network/device."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import zlib


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',type=Path,required=True)
    p.add_argument('--original',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--revision',default='v3')
    a=p.parse_args()
    if a.output.exists():p.error('new output required')
    spec=importlib.util.spec_from_file_location('expanded',Path(__file__).with_name('build-ota-expanded-0031.py'))
    b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
    base=b.legacy.read_base(a.original)
    checks=[]
    for name in ('bridge-'+a.revision+'-rom','tail-'+a.revision+'-rom','tail-'+a.revision+'b-rom'):
        path=a.directory/(name+'.bin');data=path.read_bytes();manifest=a.directory/(name+'.manifest.json')
        b.validate_candidate(data,manifest);checks.append(name+' complete reconstruction')
        for location in (0,0x84,0x1f809c,0x1f80ac,len(data)-4):
            bad=bytearray(data);bad[location]^=1
            try:b.validate_candidate(bytes(bad),manifest)
            except ValueError:checks.append(name+f' rejects alteration {location:#x}')
            else:raise AssertionError('altered image accepted')
        if name.startswith('tail'):
            size=struct.unpack_from('<I',base,b.legacy.GIF_DESC)[0]
            assert data[b.legacy.GIF_DESC:b.legacy.GIF_DESC+4]==base[b.legacy.GIF_DESC:b.legacy.GIF_DESC+4]
            assert data[b.legacy.GIF_START:b.legacy.GIF_START+size]==base[b.legacy.GIF_START:b.legacy.GIF_START+size]
            checks.append(name+' original GIF and descriptor identical')
            assert struct.unpack_from('<I',data,0x84)[0]==len(data)-40-0x1000
            assert len(data)<=b.CAPACITY and b.TAIL_OFFSET>=len(base)
            checks.append(name+' native span and slot capacity')
    payload=(a.directory/('tail-'+a.revision+'-rom.payload.bin')).read_bytes()
    try:b.assemble(base,payload,'tail',extra_padding=b.CAPACITY)
    except ValueError:checks.append('over-capacity layout rejected')
    else:raise AssertionError('over-capacity image accepted')
    from PIL import Image
    size=struct.unpack_from('<I',base,b.legacy.GIF_DESC)[0]
    gif=base[b.legacy.GIF_START:b.legacy.GIF_START+size]
    decoded=Image.open(io.BytesIO(gif));frame_hashes=[]
    for index in range(decoded.n_frames):
        decoded.seek(index);frame_hashes.append(hashlib.sha256(decoded.convert('RGBA').tobytes()).hexdigest())
    result=dict(passed=True,checks=len(checks),cases=checks,device_accessed=False,
                gif=dict(bytes=len(gif),sha256=hashlib.sha256(gif).hexdigest(),frames=len(frame_hashes),
                         canvas=list(decoded.size),decoded_frames_digest=hashlib.sha256(''.join(frame_hashes).encode()).hexdigest()))
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result))


if __name__=='__main__':main()
