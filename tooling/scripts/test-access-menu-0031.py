#!/usr/bin/env python3
"""Offline 0031 menu patch regression; uses synthetic payloads, never a device.

Run the companion C check with:
cc -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined \
  tooling/firmware-modules/test_access_menu_0031.c \
  tooling/firmware-modules/device_code_0031.c \
  tooling/firmware-modules/ota_channel.c -o /tmp/access-menu-check
/tmp/access-menu-check
"""
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "expanded", Path(__file__).with_name("build-ota-expanded-0031.py"))
expanded = importlib.util.module_from_spec(spec)
spec.loader.exec_module(expanded)
legacy = expanded.legacy


def rejects(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("malformed menu accepted")


def payload(offset):
    result = bytearray(512)
    struct.pack_into("<I", result, 8, 2)
    struct.pack_into("<I", result, 16, offset)
    start = legacy.BASE + offset
    struct.pack_into("<I", result, 24, start + 256)
    symbols = {name: start + 256 + 16 * i
               for i, (_, _, name) in enumerate(legacy.MENU_HOOKS)}
    legacy.menu_manifest(result, symbols)
    return result


def patched_target(image, site):
    upper, lower = struct.unpack_from("<II", image, site)
    assert upper & 0xfff == 0x97  # auipc ra
    assert lower & 0xfffff == 0x80e7  # jalr ra,ra
    hi = upper & 0xfffff000
    if hi & 0x80000000:
        hi -= 1 << 32
    lo = lower >> 20
    if lo & 0x800:
        lo -= 0x1000
    return legacy.BASE + site + hi + lo


def main():
    base = legacy.read_base(ROOT / "roms/0031/ap01-1.0.2_0031.bin")
    p = payload(expanded.TAIL_OFFSET)
    records = legacy.menu_hooks(p)
    assert len(records) == 2
    metadata=dict(credential_source='device-menu-8digit',per_device_credential=True)
    assert legacy.validate_credentials(p,metadata)==2
    for byte in (64,127,191):
        bad=bytearray(p);bad[byte]=ord('1')
        rejects(legacy.validate_credentials,bad,metadata)
        rejects(legacy.menu_hooks,bad)
    rejects(legacy.validate_credentials,p,dict(metadata,auth_key_sha256='0'*64))
    rejects(legacy.validate_credentials,p,{})
    old = bytearray(p)
    old[192:228] = bytes(36)
    assert legacy.menu_hooks(old) == []
    rejects(legacy.validate_credentials,old,metadata)
    assert legacy.validate_credentials(old,metadata,False)==2
    historical=bytearray(old);struct.pack_into('<I',historical,8,1)
    historical[64:128]=b'a'*64
    assert legacy.validate_credentials(historical,dict(auth_key_sha256=legacy.sha(b'a'*64)))==1
    unchanged = bytearray(base)
    assert legacy.apply_menu(unchanged, base, old) == [] and unchanged == base
    header = bytearray(256)
    legacy.menu_manifest(header, {})
    assert not any(header)
    rejects(legacy.menu_manifest,header,{},True)
    rejects(legacy.menu_manifest, header, {legacy.MENU_HOOKS[0][2]: 1})
    for pos in (128, 191, 192, 199, 200, 204, 216, 228, 255):
        bad = bytearray(p)
        bad[pos] ^= 1
        rejects(legacy.menu_hooks, bad)
    start = legacy.BASE + expanded.TAIL_OFFSET
    for record in (204, 216):
        for target in (start, start + 254, start + 257, start + len(p), 0xffffffff):
            bad = bytearray(p)
            struct.pack_into("<I", bad, record + 4, target)
            rejects(legacy.menu_hooks, bad)
        for span in (0, 6, 12):
            bad = bytearray(p)
            struct.pack_into("<I", bad, record + 8, span)
            rejects(legacy.menu_hooks, bad)
    rejects(legacy.menu_hooks, bytes(256))
    for site, _, _ in legacy.MENU_HOOKS:
        bad_base = bytearray(base)
        bad_base[site] ^= 1
        rejects(legacy.apply_menu, bytearray(base), bad_base, p)
    # A valid minimal GIF with a 320x240 logical screen and a 1x1 image.
    gif = (b"GIF89a" + struct.pack("<HH", 320, 240) +
           bytes.fromhex("800000000000ffffff2c00000000010001000002024401003b"))
    for mode, offset in (("http", expanded.TAIL_OFFSET), ("gif-http", legacy.OFFSET)):
        p = payload(offset)
        image, allowed = expanded.assemble(base, p, mode, gif)
        for site, target, span in legacy.menu_hooks(p):
            assert patched_target(image, site) == target
            assert (site, site + span) in allowed
            if span == 10:
                assert image[site + 8:site + 10] == b"\x01\x00"
        assert image[:256] == base[:256]  # Original native boot header.
        assert image[expanded.CLOUD_OFFSET:expanded.CLOUD_OFFSET + 4] == expanded.CLOUD_ORIGINAL
        assert image[0x677390:0x677398] == base[0x677390:0x677398]
        # Original PEC region and recovery-tag metadata survive both layouts.
        assert base[0x677800:0x677804] == b"PEC:"
        assert image[0x677800:len(base)-40] == base[0x677800:len(base)-40]
        assert image[-40:-8] == base[-40:-8]
        assert struct.unpack_from(">I", image, len(image)-8)[0] == len(image)
        assert struct.unpack_from("<I", image, len(image)-4)[0] == legacy.recovery_crc(image)
        if mode == "http":
            n = struct.unpack_from("<I", base, legacy.GIF_DESC)[0]
            assert image[legacy.GIF_DESC:legacy.GIF_DESC+4] == base[legacy.GIF_DESC:legacy.GIF_DESC+4]
            assert image[legacy.GIF_START:legacy.GIF_START+n] == base[legacy.GIF_START:legacy.GIF_START+n]
        else:
            assert len(image) == len(base)
            assert image[legacy.GIF_START:legacy.GIF_START+len(gif)] == gif
    # Exercise the real CLI build paths with a synthetic linked binary and nm
    # output. No credential parameter, file, bytes, or hash may be emitted.
    with tempfile.TemporaryDirectory(prefix='0031-menu-build-',dir=ROOT) as temporary:
        work=Path(temporary);raw=work/'linked.bin';raw.write_bytes(bytes(512))
        elf=work/'linked.elf';elf.write_bytes(b'synthetic')
        for builder,offset,name in ((legacy,legacy.OFFSET,'legacy'),(expanded,expanded.TAIL_OFFSET,'http')):
            output=work/(name+'.bin');start=legacy.BASE+offset
            symbols={'ota_0031_manifest':start,'ota_0031_main':start+256}
            symbols.update({symbol:start+272+i*16 for i,(_,_,symbol) in enumerate(legacy.MENU_HOOKS)})
            listing='\n'.join(f'{address:08x} T {symbol}' for symbol,address in symbols.items())
            argv=['build','--original',str(ROOT/'roms/0031/ap01-1.0.2_0031.bin'),
                  '--payload',str(raw),'--elf',str(elf),'--output',str(output),'--label','synthetic']
            if builder is expanded:argv+=['--mode','http']
            with patch.object(sys,'argv',argv),patch.object(builder.subprocess,'run',return_value=SimpleNamespace(stdout=listing)),contextlib.redirect_stdout(io.StringIO()):
                builder.main()
            manifest=json.loads(output.with_suffix('.manifest.json').read_text())
            built=output.with_suffix('.payload.bin').read_bytes()
            assert struct.unpack_from('<I',built,8)[0]==2 and not any(built[64:192])
            assert manifest['credential_source']=='device-menu-8digit' and manifest['per_device_credential'] is True
            assert 'auth_key_sha256' not in manifest and not output.with_suffix('.auth-key').exists()
            assert len(list(work.glob(name+'.*')))==3
            # Removed options must fail before filesystem output or tool work.
            with patch.object(sys,'argv',argv+['--auth-key-file','forbidden']),contextlib.redirect_stderr(io.StringIO()):
                try:builder.main()
                except SystemExit as error:assert error.code==2
                else:raise AssertionError('builder accepted embedded credential option')
        spec=importlib.util.spec_from_file_location('ram',Path(__file__).with_name('build-ram-diagnostics-0031.py'))
        ram=importlib.util.module_from_spec(spec);spec.loader.exec_module(ram)
        loader=work/'loader.bin';loader.write_bytes(b'\x01\x00');output=work/'ram.bin'
        argv=['build','--original',str(ROOT/'roms/0031/ap01-1.0.2_0031.bin'),
              '--payload',str(raw),'--elf',str(elf),'--loader',str(loader),'--output',str(output)]
        results=[SimpleNamespace(stdout='R_RISCV_CALL_PLT'),
                 SimpleNamespace(stdout='00000000 R ota_0031_manifest\n00000100 T ota_0031_main')]
        with patch.object(sys,'argv',argv),patch.object(ram.subprocess,'run',side_effect=results),contextlib.redirect_stdout(io.StringIO()):
            ram.main()
        manifest=json.loads(output.with_suffix('.manifest.json').read_text())
        built=output.with_suffix('.payload.bin').read_bytes()
        assert struct.unpack_from('<I',built,8)[0]==2 and not any(built[64:256])
        assert manifest['per_device_credential'] is True and manifest['requires_preprovisioned_device_code'] is True
        assert manifest['role']=='offline-probe' and 'auth_key_sha256' not in manifest
        with patch.object(sys,'argv',argv+['--auth-key-file','forbidden']),contextlib.redirect_stderr(io.StringIO()):
            try:ram.main()
            except SystemExit as error:assert error.code==2
            else:raise AssertionError('RAM builder accepted embedded credential option')
    print("0031 menu packaging: hooks, malformed tables, legacy compatibility and stock preservation passed")


if __name__ == "__main__":
    main()
