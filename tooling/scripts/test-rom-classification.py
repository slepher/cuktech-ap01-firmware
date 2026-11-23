"""Check official/native/third-party ROM classification without device I/O."""
import argparse
import importlib.util
from pathlib import Path
import struct
import zlib

spec=importlib.util.spec_from_file_location('classify_rom',Path(__file__).with_name('classify-rom.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--base',type=Path,required=True);p.add_argument('--app',type=Path,required=True)
a=p.parse_args();root=Path(__file__).resolve().parents[2]
for version in ('0031','0041','0055'):
    data=(root/'roms'/version/f'ap01-1.0.2_{version}.bin').read_bytes()
    value=m.classify(data);assert value['rom_kind']=='official_'+version
    assert bool(value['warning'])==(version!='0031')
for path,kind in ((a.base,'base'),(a.app,'app_platform')):
    assert m.classify(path.read_bytes())['rom_kind']==kind
    invalid=bytearray(path.read_bytes());invalid[4096]^=1
    try:m.classify(invalid)
    except ValueError:pass
    else:raise AssertionError('damaged upload accepted')
other=bytearray(data);other[4096]^=1
struct.pack_into('<I',other,len(other)-4,zlib.crc32(other[:-4],0xffffffff)^0xffffffff)
value=m.classify(other);assert value['rom_kind']=='third_party' and value['warning']
print('ROM classification: base/App, official 0031/0041/0055, third-party and bad CRC passed')
