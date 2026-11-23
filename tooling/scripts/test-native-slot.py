"""Test production slot inspection against a packaged ROM; no device access."""
import argparse
from pathlib import Path
import subprocess
import tempfile

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--rom',type=Path,required=True)
a=p.parse_args()
modules=Path(__file__).resolve().parents[1]/'firmware-modules'
data=a.rom.read_bytes()
assert data[0x675000:0x675008]==b'AP01APP1'
with tempfile.TemporaryDirectory(prefix='ap01-slot-') as folder:
    out=Path(folder)
    flags=['-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    subprocess.run(['clang','-std=c11',*flags,'-c',str(modules/'native_ota_image.c'),'-o',str(out/'ota.o')],check=True)
    subprocess.run(['clang++','-std=c++17',*flags,'-I'+str(modules),'-I'+str(out),str(modules/'test_native_slot.cpp'),str(out/'ota.o'),'-o',str(out/'test-slot')],check=True)
    subprocess.run([str(out/'test-slot'),str(a.rom.resolve())],check=True)
