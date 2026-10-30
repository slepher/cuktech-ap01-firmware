#!/usr/bin/env python3
"""Reconstruct a stock-resource-preserving 0031 physical-Flash/RAM module image."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess
import zlib

spec=importlib.util.spec_from_file_location('stock0031',Path(__file__).with_name('build-ota-channel-0031.py'))
stock=importlib.util.module_from_spec(spec);spec.loader.exec_module(stock)
FORMAT='ap01-http-ram-0031-v1'
OFFSET=0x67e000
LOADER=0x1060
ENTRY=stock.BASE+LOADER


def assemble(base,payload,loader):
    if not 0<len(loader)<=0x1400-LOADER or any(base[LOADER:LOADER+len(loader)]):
        raise ValueError('loader must fit pinned zero startup padding')
    length=((OFFSET+len(payload)+15)&~15)+40
    if length>0x700000:raise ValueError('slot capacity')
    data=bytearray(base[:-40]);data.extend(b'\xff'*(length-len(data)))
    data[LOADER:LOADER+len(loader)]=loader
    data[OFFSET:OFFSET+len(payload)]=payload;data[-40:]=base[-40:]
    struct.pack_into('>I',data,len(data)-8,len(data))
    struct.pack_into('<I',data,stock.BUILTIN_ENTRY,ENTRY)
    rcs=b'set +e\nifup wlan0\nmiio_client &\nmible_mesh_common_bt &\nlvgl_ui_main &\nsetlogmask &\nexit\n'
    data[stock.RCS_OFF:stock.RCS_OFF+stock.RCS_LEN]=rcs.ljust(stock.RCS_LEN,b'\n')
    struct.pack_into('>I',data,stock.VOL_OFF+12,0)
    checksum=(-sum(struct.unpack('>120I',data[stock.VOL_OFF:stock.VOL_OFF+stock.VOL_SIZE])))&0xffffffff
    struct.pack_into('>I',data,stock.VOL_OFF+12,checksum)
    struct.pack_into('<I',data,len(data)-4,stock.recovery_crc(data))
    allowed=[(LOADER,LOADER+len(loader)),(stock.BUILTIN_ENTRY,stock.BUILTIN_ENTRY+4),
        (stock.RCS_OFF,stock.RCS_OFF+stock.RCS_LEN),(stock.VOL_OFF+12,stock.VOL_OFF+16)]
    for i in range(len(base)-40):
        if data[i]!=base[i] and not any(a<=i<b for a,b in allowed):raise ValueError(f'unexpected change {i:#x}')
    return bytes(data)


def validate_candidate(data,manifest_path):
    m=json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    if m['format']!=FORMAT:raise ValueError('format mismatch')
    base=stock.read_base(Path(m['original']['path']))
    payload=Path(m['payload']['path']).read_bytes();loader=Path(m['loader']['path']).read_bytes()
    if stock.sha(payload)!=m['payload']['sha256'] or stock.sha(loader)!=m['loader']['sha256']:raise ValueError('component identity')
    h=bytearray(payload[:256]);check=struct.unpack_from('<I',h,32)[0];struct.pack_into('<I',h,32,0)
    version,length,offset,size,entry,code_crc=struct.unpack_from('<6I',h,8)
    if h[:8]!=b'AP01RAM1' or length!=len(data) or offset!=OFFSET or size!=len(payload):raise ValueError('manifest layout')
    if not 256<=entry<size<=65536 or entry&1 or struct.unpack_from('<3I',h,52)!=(8192,18080,3):raise ValueError('RAM entry/parameters')
    if zlib.crc32(h)!=check or zlib.crc32(payload[256:])!=code_crc:raise ValueError('module CRC')
    stock.validate_credentials(payload,m,require_menu=False)
    if any(h[128:]):raise ValueError('RAM experiment must not contain menu hooks')
    if version==2 and m.get('requires_preprovisioned_device_code') is not True:raise ValueError('RAM credential prerequisite missing')
    if data!=assemble(base,payload,loader) or stock.sha(data)!=m['image']['sha256']:raise ValueError('reconstruction mismatch')
    if data[:256]!=base[:256] or data[0x677800:len(base)-40]!=base[0x677800:len(base)-40]:raise ValueError('boot/PEC changed')
    if data[stock.GIF_START:stock.GIF_START+385834]!=base[stock.GIF_START:stock.GIF_START+385834] or data[0x1135b2:0x1135b6]!=base[0x1135b2:0x1135b6]:raise ValueError('GIF/native OTA changed')
    return m


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('original','payload','elf','loader','output'):parser.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args();paths=[a.output,a.output.with_suffix('.manifest.json'),a.output.with_suffix('.payload.bin')]
    if any(p.exists() for p in paths):parser.error('new outputs required')
    tool=stock.ROOT.parent/'cuktech-ap01-firmware-tools/tools/docker/toolchain/bin/riscv64-unknown-elf'
    reloc=subprocess.run([str(tool)+'-readelf','-rW',str(a.elf)],check=True,capture_output=True,text=True).stdout
    kinds=set(re.findall(r'R_RISCV_[A-Z0-9_]+',reloc))
    if not kinds or kinds-{'R_RISCV_CALL_PLT','R_RISCV_PCREL_HI20','R_RISCV_PCREL_LO12_I','R_RISCV_PCREL_LO12_S'}:parser.error('module has non-position-independent relocation '+repr(kinds))
    names=subprocess.run([str(tool)+'-nm','-n',str(a.elf)],check=True,capture_output=True,text=True).stdout
    symbols={v[2]:int(v[0],16) for line in names.splitlines() if len(v:=line.split())==3 and v[0]!='U'}
    if symbols['ota_0031_manifest']!=0:parser.error('module must link at zero')
    base=stock.read_base(a.original.resolve());payload=bytearray(a.payload.read_bytes());loader=a.loader.read_bytes()
    if payload[:256]!=bytes(256):parser.error('zero manifest required')
    length=((OFFSET+len(payload)+15)&~15)+40
    h=bytearray(256);h[:8]=b'AP01RAM1'
    struct.pack_into('<6I',h,8,2,length,OFFSET,len(payload),symbols['ota_0031_main'],zlib.crc32(payload[256:]))
    h[36:52]=hashlib.sha256(payload[256:]+loader).digest()[:16]
    struct.pack_into('<3I',h,52,8192,18080,3);struct.pack_into('<I',h,32,zlib.crc32(h));payload[:256]=h
    data=assemble(base,payload,loader)
    m=dict(format=FORMAT,original=dict(path=str(a.original.resolve()),sha256=stock.sha(base)),
        image=dict(path=str(a.output.resolve()),bytes=len(data),sha256=stock.sha(data)),
        payload=dict(path=str(paths[2].resolve()),bytes=len(payload),sha256=stock.sha(payload),entry=hex(symbols['ota_0031_main']),elf=str(a.elf.resolve())),
        loader=dict(path=str(a.loader.resolve()),sha256=stock.sha(loader),bytes=len(loader),entry=hex(ENTRY)),
        role='offline-probe', local_access_menu=False, requires_preprovisioned_device_code=True,
        credential_source='device-menu-8digit',per_device_credential=True,
        credential_setup='First provision and read the persistent code using a menu-enabled 0031 image.',
        build_id=bytes(h[36:52]).hex(),cloud_ota_dispatch_modified=False,
        original_gif_preserved=True,physical_boot_verified=False,flashable=False,relocation_types=sorted(kinds))
    paths[0].write_bytes(data);paths[2].write_bytes(payload);paths[1].write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
    validate_candidate(data,paths[1]);print(json.dumps(dict(bytes=len(data),sha256=stock.sha(data),loader_bytes=len(loader))))


if __name__=='__main__':main()
