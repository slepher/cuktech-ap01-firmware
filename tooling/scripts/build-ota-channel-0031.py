#!/usr/bin/env python3
"""Build a bounded 0031 OTA-channel simulation candidate; never flash a device."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import zlib

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BASE = 0x9ffff000
OFFSET = 0x1f9640          # inside the 0031 pet-GIF extent
LIMIT = OFFSET + 0x4a6c    # bounded first OTA code extent
GIF_START = 0x1f80ac
GIF_DESC = 0x1f809c        # u32 pet-GIF length, 0x10 bytes before GIF data
IMAGE_SHA = '8a721fc8ef25458d415b2460e4a251e0503a82f7743fdff85b12612190e5c1cb'
IMAGE_SIZE = 6804520
BUILTIN_ENTRY = 0x1ba8f0   # setlogmask builtin entry field
RCS_OFF = 0x1baf10
RCS_LEN = 97
VOL_OFF = 0x1bada0
VOL_SIZE = 480
TAG = b'0x5245434f56455259544147'
MENU_HOOKS = ((0xbe8da, 'efc0ce7db7450fa0', 'ap01_access_register_hook_0031'),
              (0xbe9e6, 'efa0fd6e814523a4a900', 'ap01_access_list_hook_0031'))


def menu_manifest(header, symbols, required=False):
    present = [name in symbols for _, _, name in MENU_HOOKS]
    if not any(present):
        if required:
            raise ValueError('0031 release requires the local device-code menu')
        return
    if not all(present):
        raise ValueError('incomplete 0031 access menu symbols')
    header[192:200] = b'AP31MNU1'
    struct.pack_into('<I', header, 200, 2)
    for i, (offset, original, name) in enumerate(MENU_HOOKS):
        struct.pack_into('<3I', header, 204+12*i, offset, symbols[name], len(bytes.fromhex(original)))


def menu_hooks(payload):
    if len(payload) <= 256 or any(payload[128:192]) or any(payload[228:256]):
        raise ValueError('invalid 0031 manifest reserved bytes')
    if struct.unpack_from('<I', payload, 8)[0] == 2 and any(payload[64:192]):
        raise ValueError('device-code images cannot contain embedded credentials')
    if not any(payload[192:228]):
        return []  # Historical/probe modules remain reconstructible.
    if payload[192:200] != b'AP31MNU1' or struct.unpack_from('<I', payload, 200)[0] != 2:
        raise ValueError('invalid 0031 menu header')
    start = BASE + struct.unpack_from('<I', payload, 16)[0]
    records = []
    for i, (site, original, _) in enumerate(MENU_HOOKS):
        offset, target, span = struct.unpack_from('<3I', payload, 204+12*i)
        if offset != site or span != len(bytes.fromhex(original)) or target & 1 or not start+256 <= target < start+len(payload):
            raise ValueError('invalid 0031 menu hook bounds')
        records.append((offset, target, span))
    return records


def validate_credentials(payload, manifest, require_menu=True):
    """Version 1 is reconstruction-only; all new builds use device storage."""
    version = struct.unpack_from('<I', payload, 8)[0]
    if version == 1:
        key = payload[64:128]
        if len(key) != 64 or any(c not in b'0123456789abcdefABCDEF' for c in key):
            raise ValueError('historical key encoding mismatch')
        if 'auth_key_sha256' in manifest and sha(key) != manifest['auth_key_sha256']:
            raise ValueError('historical key identity mismatch')
    elif version == 2:
        if any(payload[64:192]) or 'auth_key_sha256' in manifest:
            raise ValueError('embedded credential or credential hash is forbidden')
        if manifest.get('credential_source') != 'device-menu-8digit' or manifest.get('per_device_credential') is not True:
            raise ValueError('device credential metadata missing')
        if require_menu and not menu_hooks(payload):
            raise ValueError('0031 release requires the local device-code menu')
    else:
        raise ValueError('unsupported module version')
    return version


def apply_menu(out, base, payload):
    allowed = []
    for (site, target, span), (_, original, _) in zip(menu_hooks(payload), MENU_HOOKS):
        if base[site:site+span] != bytes.fromhex(original):
            raise ValueError('0031 menu stock callsite mismatch')
        delta = target - (BASE+site)
        hi = (delta+0x800) >> 12
        lo = delta - (hi << 12)
        out[site:site+span] = struct.pack('<II', ((hi & 0xfffff) << 12) | 0x97,
                                        ((lo & 0xfff) << 20) | 0x80e7) + b'\x01\x00' * ((span-8)//2)
        allowed.append((site, site+span))
    return allowed


def sha(data):
    return hashlib.sha256(data).hexdigest()


def recovery_crc(data):
    if len(data) < 4:
        raise ValueError('image shorter than its recovery record')
    return (zlib.crc32(data[:-4], 0xFFFFFFFF) ^ 0xFFFFFFFF) & 0xFFFFFFFF


def image_metadata(data, require_identity=True):
    if len(data) != IMAGE_SIZE:
        raise ValueError(f'image size mismatch: expected {IMAGE_SIZE}, got {len(data)}')
    digest = sha(data)
    if require_identity and digest != IMAGE_SHA:
        raise ValueError('input SHA256 identity mismatch')
    if data[:4] != b'BFNP' or data[8:12] != b'FCFG' or data[0x64:0x68] != b'PCFG':
        raise ValueError('image header markers mismatch')
    header_stored, = struct.unpack_from('<I', data, 0xFC)
    if header_stored != zlib.crc32(data[:0xFC]) & 0xFFFFFFFF:
        raise ValueError('image header CRC mismatch')
    tail = len(data) - 40
    if data[tail:tail + 24] != TAG:
        raise ValueError('recovery tag mismatch')
    stored_len, = struct.unpack_from('>I', data, tail + 32)
    stored_crc, = struct.unpack_from('<I', data, tail + 36)
    if stored_len != len(data) or stored_crc != recovery_crc(data):
        raise ValueError('recovery length/CRC mismatch')
    return dict(bytes=len(data), sha256=digest, header_crc=header_stored,
                recovery=dict(tag=TAG.decode('ascii'), length=stored_len,
                              crc32=f'{stored_crc:08x}'))


def read_base(original):
    data = original.read_bytes()
    return data if sha(data) == IMAGE_SHA else (_ for _ in ()).throw(
        ValueError('requires the exact original 0031 image'))


def assemble(base, payload, gif, payload_limit=LIMIT):
    if payload_limit>GIF_START+385834 or len(payload) <= 256 or OFFSET + len(payload) > payload_limit:
        raise ValueError('payload exceeds the bounded first OTA code extent')
    if len(gif) > OFFSET - GIF_START or gif[:6] not in (b'GIF87a', b'GIF89a') or gif[-1:] != b';':
        raise ValueError('invalid bounded placeholder GIF')
    if struct.unpack_from('<HH', gif, 6) != (320, 240):
        raise ValueError('placeholder GIF must preserve original dimensions')
    entry, = struct.unpack_from('<I', payload, 24)
    if not BASE + OFFSET + 256 <= entry < BASE + OFFSET + len(payload) or entry & 1:
        raise ValueError('builtin entry outside injected code')
    out = bytearray(base)
    # Keep the pet GIF valid and reduce its descriptor length before reuse.
    out[GIF_START:GIF_START + len(gif)] = gif
    struct.pack_into('<I', out, GIF_DESC, len(gif))
    out[OFFSET:OFFSET + len(payload)] = payload
    struct.pack_into('<I', out, BUILTIN_ENTRY, entry)
    # Preserve all original applications; add the independent channel in rcS.
    rcs = b'set +e\nifup wlan0\nmiio_client &\nmible_mesh_common_bt &\nlvgl_ui_main &\nsetlogmask &\nexit\n'
    if len(rcs) > RCS_LEN:
        raise ValueError('rcS exceeds original ROMFS extent')
    out[RCS_OFF:RCS_OFF + RCS_LEN] = rcs.ljust(RCS_LEN, b'\n')
    # ROMFS volume checksum: BE word sum with the checksum field zeroed.
    vol = bytearray(out[VOL_OFF:VOL_OFF + VOL_SIZE])
    struct.pack_into('>I', vol, 12, 0)
    words = struct.unpack('>%dI' % (VOL_SIZE // 4), vol)
    struct.pack_into('>I', out, VOL_OFF + 12, (-sum(words)) & 0xffffffff)
    menu_ranges = apply_menu(out, base, payload)
    struct.pack_into('<I', out, len(out) - 4, recovery_crc(out))
    image_metadata(bytes(out), require_identity=False)
    allowed = [(GIF_START, GIF_START + len(gif)), (GIF_DESC, GIF_DESC + 4),
               (OFFSET, OFFSET + len(payload)), (BUILTIN_ENTRY, BUILTIN_ENTRY + 4),
               (RCS_OFF, RCS_OFF + RCS_LEN), (VOL_OFF + 12, VOL_OFF + 16),
               (len(out) - 4, len(out))] + menu_ranges
    for i, (before, after) in enumerate(zip(base, out)):
        if before != after and not any(a <= i < b for a, b in allowed):
            raise ValueError(f'unexpected modification at {i:#x}')
    return bytes(out), allowed


def validate_candidate(data, manifest_path):
    """Reconstruct every changed byte; a manifest alone cannot bypass identity."""
    m = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    if m.get('format') != 'ap01-ota-channel-0031-v1':
        raise ValueError('unsupported OTA build manifest')
    base = read_base(Path(m['original']['path']))
    payload = Path(m['payload']['path']).read_bytes()
    gif = base64.b64decode(m['placeholder_gif']['base64'], validate=True)
    if sha(payload) != m['payload']['sha256'] or sha(gif) != m['placeholder_gif']['sha256']:
        raise ValueError('payload/GIF identity mismatch')
    header = bytearray(payload[:256])
    stored, = struct.unpack_from('<I', header, 32)
    struct.pack_into('<I', header, 32, 0)
    if payload[:8] != b'AP01OTA1' or zlib.crc32(header) != stored:
        raise ValueError('OTA manifest CRC mismatch')
    validate_credentials(payload, m)
    if struct.unpack_from('<I', payload, 20)[0] != len(payload) or zlib.crc32(payload[256:]) != struct.unpack_from('<I', payload, 28)[0]:
        raise ValueError('OTA code CRC/length mismatch')
    expected, _ = assemble(base, payload, gif)
    if data != expected or sha(data) != m['image']['sha256']:
        raise ValueError('image does not equal the bounded reconstructed OTA build')
    return m


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original', type=Path, required=True)
    p.add_argument('--payload', type=Path, required=True, help='zero-manifest linked binary')
    p.add_argument('--elf', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--label', default='ota0031a')
    a = p.parse_args()
    output = a.output.resolve()
    paths = [output, output.with_suffix('.manifest.json'), output.with_suffix('.payload.bin')]
    if not output.parent.is_dir() or any(x.exists() for x in paths):
        p.error('all outputs must be new files in an existing directory')
    base = read_base(a.original.resolve())
    payload = bytearray(a.payload.read_bytes())
    if payload[:256] != bytes(256):
        p.error('linked input must contain exactly the reserved zero manifest')
    tool = ROOT.parent / 'cuktech-ap01-firmware-tools/tools/docker/toolchain/bin/riscv64-unknown-elf-nm'
    listing = subprocess.run([str(tool), '-n', str(a.elf)], check=True, capture_output=True, text=True, timeout=10).stdout
    symbols = {line.split()[2]: int(line.split()[0], 16) for line in listing.splitlines() if len(line.split()) == 3 and line.split()[0] != 'U'}
    entry = symbols['ota_0031_main']
    if symbols['ota_0031_manifest'] != BASE + OFFSET:
        p.error('ELF manifest mapping mismatch')
    m = bytearray(256)
    m[:8] = b'AP01OTA1'
    struct.pack_into('<7I', m, 8, 2, IMAGE_SIZE, OFFSET, len(payload), entry, zlib.crc32(payload[256:]), 0)
    m[36:52] = hashlib.sha256(payload[256:] + a.label.encode('utf-8')).digest()[:16]
    struct.pack_into('<3I', m, 52, 8192, 18080, 0)
    menu_manifest(m, symbols, required=True)
    struct.pack_into('<I', m, 32, zlib.crc32(m))
    payload[:256] = m
    from PIL import Image
    stream = io.BytesIO()
    Image.new('P', (320, 240), 0).save(stream, format='GIF', optimize=True)
    gif = stream.getvalue()
    decoded = Image.open(io.BytesIO(gif)); decoded.load()
    if decoded.size != (320, 240) or any(decoded.tobytes()):
        raise ValueError('independent placeholder GIF decode mismatch')
    data, allowed = assemble(base, payload, gif)
    manifest = dict(format='ap01-ota-channel-0031-v1', simulation_candidate=True,
                    flashable=False, physical_device_verified=False,
                    original=dict(path=str(a.original.resolve()), sha256=IMAGE_SHA),
                    image=dict(path=str(output), bytes=len(data), sha256=sha(data)),
                    payload=dict(path=str(paths[2]), bytes=len(payload), sha256=sha(payload),
                                 entry=hex(entry), elf=str(a.elf.resolve()), elf_sha256=sha(a.elf.read_bytes())),
                    build_id=bytes(m[36:52]).hex(), credential_source='device-menu-8digit',
                    per_device_credential=True, local_access_menu=True,
                    placeholder_gif=dict(bytes=len(gif), sha256=sha(gif), base64=base64.b64encode(gif).decode('ascii')),
                    allowed_ranges=[dict(start=x, end_exclusive=y) for x, y in allowed],
                    cloud_ota_dispatch_modified=False,
                    assumptions=['original setlogmask builtin replaced; original UI retained with blank pet0 GIF',
                                 'cloud miIO.ota dispatcher unchanged in this candidate (not exclusions-verified)',
                                 'fixed 0031 format/size; future image must retain a valid OTA manifest and startup hook',
                                 'no Boot2 or physical Wi-Fi equivalence claim; no physical flash performed'])
    for path, content in ((paths[2], bytes(payload)), (output, data)):
        with path.open('xb') as f: f.write(content)
    with paths[1].open('x', encoding='utf-8') as f: json.dump(manifest, f, indent=2); f.write('\n')
    validate_candidate(data, paths[1])
    print(json.dumps(dict(image=str(output), bytes=len(data), sha256=sha(data),
                          build_id=manifest['build_id'], manifest=str(paths[1]), flashable=False)))


if __name__ == '__main__':
    main()
