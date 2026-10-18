#!/usr/bin/env python3
"""Reconstruct a legacy-compatible bridge or resource-preserving slot-tail image."""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import zlib

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('legacy0031', Path(__file__).with_name('build-ota-channel-0031.py'))
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)
FORMAT = 'ap01-ota-channel-0031-v2'
DIAGNOSTIC_FORMAT = 'ap01-diagnostics-0031-v1'
HTTP_FORMAT = 'ap01-http-0031-v1'
GIF_HTTP_FORMAT = 'ap01-http-gif-0031-v1'
TAIL_OFFSET = 0x67e000
CAPACITY = 0x700000
# miIO.ota descriptor at 0x677390 points to VA 0xa01125b2.
CLOUD_OFFSET = 0x1135b2
CLOUD_ORIGINAL = bytes.fromhex('5971a2d4')


def assemble(base, payload, mode, gif=b'', extra_padding=0):
    offset = legacy.OFFSET if mode in ('bridge','gif-http') else TAIL_OFFSET
    if mode not in ('bridge', 'tail', 'diagnostics', 'http','gif-http') or len(payload) <= 256:
        raise ValueError('invalid build mode/payload')
    if mode in ('bridge','gif-http'):
        if extra_padding:
            raise ValueError('bridge must retain the exact old length')
        data, allowed = legacy.assemble(base, payload, gif,legacy.GIF_START+385834 if mode=='gif-http' else legacy.LIMIT)
        out = bytearray(data)
    else:
        if extra_padding < 0 or extra_padding > CAPACITY:
            raise ValueError('invalid padding')
        end = (offset + len(payload) + 15) & ~15
        length = end + extra_padding + 40
        if length > CAPACITY:
            raise ValueError('image exceeds inactive-slot capacity')
        out = bytearray(base[:-40])
        out.extend(b'\xff' * (length - len(out)))
        out[offset:offset + len(payload)] = payload
        out[-40:] = base[-40:]
        struct.pack_into('>I', out, len(out)-8, len(out))
        if mode == 'tail':
            # Historical layout: the uploaded image was not observed running.
            # Whether this span change caused that outcome remains unverified.
            # Keep reconstruction available, never infer release eligibility.
            struct.pack_into('<I',out,0x84,len(out)-40-0x1000)
            struct.pack_into('<I',out,252,zlib.crc32(out[:252]))
        entry, = struct.unpack_from('<I', payload, 24)
        if not legacy.BASE + offset + 256 <= entry < legacy.BASE + offset + len(payload) or entry & 1:
            raise ValueError('entry outside appended executable')
        struct.pack_into('<I', out, legacy.BUILTIN_ENTRY, entry)
        rcs = b'set +e\nifup wlan0\nmiio_client &\nmible_mesh_common_bt &\nlvgl_ui_main &\nsetlogmask &\nexit\n'
        out[legacy.RCS_OFF:legacy.RCS_OFF+legacy.RCS_LEN] = rcs.ljust(legacy.RCS_LEN,b'\n')
        struct.pack_into('>I',out,legacy.VOL_OFF+12,0)
        words=struct.unpack('>120I',out[legacy.VOL_OFF:legacy.VOL_OFF+legacy.VOL_SIZE])
        struct.pack_into('>I',out,legacy.VOL_OFF+12,(-sum(words)) & 0xffffffff)
        allowed=[(legacy.BUILTIN_ENTRY,legacy.BUILTIN_ENTRY+4),
                 (legacy.RCS_OFF,legacy.RCS_OFF+legacy.RCS_LEN),
                 (legacy.VOL_OFF+12,legacy.VOL_OFF+16)]
        if mode == 'tail':allowed.extend([(0x84,0x88),(252,256)])
        assert out[legacy.GIF_DESC:legacy.GIF_DESC+4] == base[legacy.GIF_DESC:legacy.GIF_DESC+4]
        assert out[legacy.GIF_START:legacy.GIF_START+385834] == base[legacy.GIF_START:legacy.GIF_START+385834]
    if struct.unpack_from('<II',base,0x677390)!=(0xa052a338,legacy.BASE+CLOUD_OFFSET):
        raise ValueError('cloud dispatcher descriptor mismatch')
    if base[0x52b338:0x52b341] != b'miIO.ota\0':
        raise ValueError('cloud dispatcher name mismatch')
    if base[CLOUD_OFFSET:CLOUD_OFFSET+4] != CLOUD_ORIGINAL:
        raise ValueError('cloud dispatcher original bytes mismatch')
    if mode not in ('diagnostics','http','gif-http'):
        out[CLOUD_OFFSET:CLOUD_OFFSET+4] = bytes.fromhex('41558280')
        allowed.append((CLOUD_OFFSET,CLOUD_OFFSET+4))
    struct.pack_into('<I',out,len(out)-4,legacy.recovery_crc(out))
    # Preserve all original bytes except explicitly reviewed hooks/bridge resources.
    comparison_end = len(base) if mode in ('bridge','gif-http') else len(base)-40
    for i in range(comparison_end):
        if out[i] != base[i] and not any(a <= i < b for a,b in allowed):
            raise ValueError(f'unexpected original-byte modification at {i:#x}')
    return bytes(out), allowed


def validate_candidate(data, manifest_path):
    m=json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    if m.get('format') not in (FORMAT,DIAGNOSTIC_FORMAT,HTTP_FORMAT,GIF_HTTP_FORMAT):
        raise ValueError('unsupported expanded manifest')
    diagnostic=m['format']==DIAGNOSTIC_FORMAT
    unified=m['format'] in (HTTP_FORMAT,GIF_HTTP_FORMAT)
    if diagnostic != (m['mode']=='diagnostics') or (m['format']==HTTP_FORMAT) != (m['mode']=='http') or (m['format']==GIF_HTTP_FORMAT) != (m['mode']=='gif-http'):
        raise ValueError('manifest format/mode mismatch')
    base=legacy.read_base(Path(m['original']['path']))
    payload=Path(m['payload']['path']).read_bytes()
    if legacy.sha(payload) != m['payload']['sha256']:
        raise ValueError('payload hash mismatch')
    h=bytearray(payload[:256]); stored=struct.unpack_from('<I',h,32)[0];struct.pack_into('<I',h,32,0)
    offset=legacy.OFFSET if m['mode'] in ('bridge','gif-http') else TAIL_OFFSET
    magic=b'AP01HTTP' if unified else b'AP01DIA1' if diagnostic else b'AP01OTA1'
    if payload[:8]!=magic or struct.unpack_from('<I',payload,8)[0]!=1 or zlib.crc32(h)!=stored or struct.unpack_from('<I',payload,16)[0]!=offset:
        raise ValueError('invalid module manifest')
    entry=struct.unpack_from('<I',payload,24)[0]
    if not legacy.BASE+offset+256 <= entry < legacy.BASE+offset+len(payload) or entry & 1:
        raise ValueError('invalid module entry')
    parameters=(8192,18080,2) if unified else (8192,18081,1) if diagnostic else (8192,18080,0)
    if struct.unpack_from('<3I',payload,52)!=parameters or payload[128:256]!=bytes(128):
        raise ValueError('invalid module service parameters')
    if any(c not in b'0123456789abcdefABCDEF' for c in payload[64:128]) or legacy.sha(payload[64:128])!=m['auth_key_sha256']:
        raise ValueError('module auth key identity mismatch')
    if struct.unpack_from('<I',payload,20)[0]!=len(payload) or zlib.crc32(payload[256:])!=struct.unpack_from('<I',payload,28)[0]:
        raise ValueError('code length/CRC mismatch')
    gif=base64.b64decode(m.get('placeholder_gif',''),validate=True)
    expected,_=assemble(base,payload,m['mode'],gif,m['extra_padding'])
    if data!=expected or legacy.sha(data)!=m['image']['sha256'] or struct.unpack_from('<I',payload,12)[0]!=len(data):
        raise ValueError('image differs from full reconstruction')
    if zlib.crc32(data[:252])!=struct.unpack_from('<I',data,252)[0] or struct.unpack_from('>I',data,len(data)-8)[0]!=len(data):
        raise ValueError('header/trailer mismatch')
    if (diagnostic or unified) and (data[:256]!=base[:256] or data[CLOUD_OFFSET:CLOUD_OFFSET+4]!=CLOUD_ORIGINAL or
                       m.get('cloud_ota_dispatch_modified') is not False or m.get('original_gif_preserved') != (m['mode']!='gif-http')):
        raise ValueError('diagnostic image changed stock startup metadata or native OTA entry')
    return m


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('original','payload','elf','output','auth-key-file'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--mode',choices=('bridge','tail','http','gif-http'),required=True)
    p.add_argument('--legacy-manifest',type=Path,help='placeholder GIF provenance for bridge only')
    p.add_argument('--extra-padding',type=int,default=0)
    p.add_argument('--label',required=True)
    a=p.parse_args(); output=a.output.resolve()
    paths=[output,output.with_suffix('.manifest.json'),output.with_suffix('.payload.bin')]
    if not output.parent.is_dir() or any(x.exists() for x in paths):p.error('new output files required')
    base=legacy.read_base(a.original.resolve());payload=bytearray(a.payload.read_bytes())
    if payload[:256]!=bytes(256):p.error('zero-manifest linked input required')
    tool=legacy.ROOT.parent/'cuktech-ap01-firmware-tools/tools/docker/toolchain/bin/riscv64-unknown-elf-nm'
    listing=subprocess.run([str(tool),'-n',str(a.elf)],check=True,capture_output=True,text=True).stdout
    symbols={line.split()[2]:int(line.split()[0],16) for line in listing.splitlines() if len(line.split())==3 and line.split()[0]!='U'}
    offset=legacy.OFFSET if a.mode in ('bridge','gif-http') else TAIL_OFFSET
    if symbols['ota_0031_manifest']!=legacy.BASE+offset:p.error('ELF mapping mismatch')
    length=len(base) if a.mode in ('bridge','gif-http') else ((offset+len(payload)+15)&~15)+a.extra_padding+40
    key=a.auth_key_file.read_text(encoding='ascii').strip()
    if len(key)!=64 or any(c not in '0123456789abcdefABCDEF' for c in key):p.error('64hex key required')
    diagnostic=a.mode=='diagnostics'
    unified=a.mode in ('http','gif-http')
    h=bytearray(256);h[:8]=b'AP01HTTP' if unified else b'AP01DIA1' if diagnostic else b'AP01OTA1'
    struct.pack_into('<7I',h,8,1,length,offset,len(payload),symbols['ota_0031_main'],zlib.crc32(payload[256:]),0)
    h[36:52]=hashlib.sha256(payload[256:]+a.label.encode()).digest()[:16]
    struct.pack_into('<3I',h,52,8192,18081 if diagnostic else 18080,2 if unified else 1 if diagnostic else 0);h[64:129]=key.encode()+b'\0';struct.pack_into('<I',h,32,zlib.crc32(h));payload[:256]=h
    gif=b''
    if a.mode in ('bridge','gif-http'):
        if not a.legacy_manifest:p.error('legacy manifest required for bridge')
        old=json.loads(a.legacy_manifest.read_text());gif=base64.b64decode(old['placeholder_gif']['base64'],validate=True)
    data,allowed=assemble(base,payload,a.mode,gif,a.extra_padding)
    m=dict(format=GIF_HTTP_FORMAT if a.mode=='gif-http' else HTTP_FORMAT if unified else DIAGNOSTIC_FORMAT if diagnostic else FORMAT,mode=a.mode,extra_padding=a.extra_padding,
           original=dict(path=str(a.original.resolve()),sha256=legacy.IMAGE_SHA),
           image=dict(path=str(output),bytes=len(data),sha256=legacy.sha(data)),
           payload=dict(path=str(paths[2]),bytes=len(payload),sha256=legacy.sha(payload),entry=hex(symbols['ota_0031_main']),
                        elf=str(a.elf.resolve()),elf_sha256=legacy.sha(a.elf.read_bytes())),
           build_id=bytes(h[36:52]).hex(),auth_key_sha256=legacy.sha(key.encode()),
           placeholder_gif=base64.b64encode(gif).decode(),cloud_ota_dispatch_modified=not (diagnostic or unified),
           original_gif_preserved=a.mode not in ('bridge','gif-http'),allowed_ranges=allowed,
           flashable=False,physical_device_verified=False)
    if unified:m.update(independent_ota_enabled=True,diagnostic_port=18080,startup_mapping_verified=False)
    if diagnostic:m.update(independent_ota_enabled=False,diagnostic_port=18081,startup_mapping_verified=False)
    for path,content in ((paths[2],bytes(payload)),(output,data)):
        with path.open('xb') as f:f.write(content)
    with paths[1].open('x',encoding='utf-8') as f:json.dump(m,f,indent=2);f.write('\n')
    validate_candidate(data,paths[1]);print(json.dumps(dict(image=str(output),bytes=len(data),sha256=legacy.sha(data),original_gif_preserved=m['original_gif_preserved'])))


if __name__=='__main__':main()
