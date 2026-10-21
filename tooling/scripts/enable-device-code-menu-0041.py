"""Attach the native Settings device-code menu to an isolated 0041 source tree.

Copies audited modules and adds four pinned ROM call veneers. Never contacts a
device. Run this again after changing a source module, then rerun audit/link.
"""
from pathlib import Path
import argparse
import difflib

HOOKS = [(0xb262c, 8, 'efc08f0281460546', 'ap01MenuRegisterOne0041'),
         (0xb263a, 8, 'efc0af0181462d46', 'ap01MenuRegisterTwo0041'),
         (0xb2648, 8, 'efc0cf00b7450fa0', 'ap01MenuRegisterThree0041'),
         (0xb2754, 10, 'ef10ef4a814523a4a900', 'ap01MenuList0041')]

VENEERS = '''// Four exact-stock call-site continuations; no writable state.
asm(R"(
.pushsection .text.ap01MenuHooks0041,"ax",@progbits
.balign 2
.global ap01MenuRegisterOne0041
ap01MenuRegisterOne0041:
addi sp,sp,-16
sw ra,12(sp)
call ap01SettingsRegister0041
lw ra,12(sp)
addi sp,sp,16
li a3,0
li a2,1
ret
.global ap01MenuRegisterTwo0041
ap01MenuRegisterTwo0041:
addi sp,sp,-16
sw ra,12(sp)
call ap01SettingsRegister0041
lw ra,12(sp)
addi sp,sp,16
li a3,0
li a2,11
ret
.global ap01MenuRegisterThree0041
ap01MenuRegisterThree0041:
addi sp,sp,-16
sw ra,12(sp)
call ap01SettingsRegister0041
lw ra,12(sp)
addi sp,sp,16
lui a1,0xa00f4
ret
.global ap01MenuList0041
ap01MenuList0041:
addi sp,sp,-16
sw ra,12(sp)
call ap01SettingsList0041
lw ra,12(sp)
addi sp,sp,16
li a1,0
sw a0,8(s3)
ret
.popsection
)");
'''

TABLE = '''
# AP01MNU1: optional, exact-stock Settings call-site table in spare manifest.
MENU_HOOKS = {0xb262c:(8,'efc08f0281460546'),
              0xb263a:(8,'efc0af0181462d46'),
              0xb2648:(8,'efc0cf00b7450fa0'),
              0xb2754:(10,'ef10ef4a814523a4a900')}
def menu_hooks(payload):
    if payload[192:200] != b'AP01MNU1':
        if any(payload[192:256]):raise ValueError('unknown spare manifest data')
        return []
    if struct.unpack_from('<I',payload,200)[0] != 4:raise ValueError('menu hook count')
    records=[struct.unpack_from('<3I',payload,204+12*i) for i in range(4)]
    if {r[0] for r in records} != set(MENU_HOOKS):raise ValueError('menu hook offsets')
    for offset,target,span in records:
        if span != MENU_HOOKS[offset][0] or target&1 or not BASE+OFFSET+256 <= target < BASE+OFFSET+len(payload):
            raise ValueError('menu hook bounds')
    if any(payload[252:256]):raise ValueError('menu hook reserved bytes')
    return records
'''

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--diff', type=Path, required=True)
    args = parser.parse_args()
    source = args.source_root.resolve()
    port = source/'ports/ap01'
    modules = Path(__file__).resolve().parents[1]/'firmware-modules'
    changes = []

    def write(path, value):
        old = path.read_text(encoding='utf-8') if path.exists() else ''
        changes.extend(difflib.unified_diff(old.splitlines(True), value.splitlines(True),
            fromfile=str(path.relative_to(source)), tofile=str(path.relative_to(source))))
        path.write_text(value, encoding='utf-8', newline='\n')

    def edit(path, old, new):
        value = path.read_text(encoding='utf-8')
        assert value.count(old) == 1, (path, old)
        write(path, value.replace(old, new))

    names = [p for p in modules.glob('native_device_code*') if p.suffix in ('.h','.cpp','.inc')]
    assert len(names) >= 7, 'device-code storage, font and menu modules are required'
    for path in names:
        value = path.read_text(encoding='utf-8')
        value = value.replace('#include "native_filesystem_0041.h"', '#include "LittleFS.h"')
        value = value.replace('#include "native_vfs_0041.h"', '#include "vfs_0041.h"')
        write(port/path.name, value)
    write(port/'native_device_code_hooks_0041.cpp', VENEERS)

    audit = source/'tools/check-ap01-native.py'
    if 'native_device_code_menu_0041.cpp' not in audit.read_text(encoding='utf-8'):
        edit(audit, "sources += [repo/'ports/ap01/firmware.cpp'", "sources += [repo/'ports/ap01'/name for name in ['native_device_code_0041.cpp', 'native_device_code_font_0041.cpp', 'native_device_code_menu_0041.cpp', 'native_device_code_hooks_0041.cpp']]\nsources += [repo/'ports/ap01/firmware.cpp'")
        edit(audit, "p.suffix in ('.h','.hpp')", "p.suffix in ('.h','.hpp','.inc')")
    linker = port/'native_0041.ld'
    if 'KEEP(*(.text.ap01MenuHooks0041))' not in linker.read_text(encoding='utf-8'):
        edit(linker, 'KEEP(*(.text.ap01Register0041))',
             'KEEP(*(.text.ap01Register0041)) KEEP(*(.text.ap01MenuHooks0041))')

    builder = source/'tools/build-ap01-rom.py'
    if 'def menu_hooks(payload):' not in builder.read_text(encoding='utf-8'):
        edit(builder, 'def call(target):\n    delta=target-(BASE+HOOK)',
             TABLE+'\ndef call(target,site=HOOK):\n    delta=target-(BASE+site)')
        edit(builder, '    stock=bytearray(original)\n',
             '    stock=bytearray(original)\n    stock[HOOK:HOOK+8]=out[HOOK:HOOK+8]\n'
             '    for offset,target,span in menu_hooks(payload):\n'
             '        if original[offset:offset+span]!=bytes.fromhex(MENU_HOOKS[offset][1]):raise ValueError("menu stock callsite mismatch")\n'
             '        patch=call(target,offset)+(b"\\x01\\x00" if span==10 else b"")\n'
             '        out[offset:offset+span]=patch;stock[offset:offset+span]=patch\n')
        edit(builder, "    if out[HOOK+8:len(original)-40]!=stock[HOOK+8:-40] or out[:HOOK]!=stock[:HOOK]:raise ValueError('unexpected stock byte modification')",
             "    if out[:len(original)-40]!=stock[:-40]:raise ValueError('unexpected stock byte modification')")
        symbols = repr([(offset, span, name) for offset, span, _, name in HOOKS])
        edit(builder, "    struct.pack_into('<I',h,32,zlib.crc32(h));payload[:256]=h",
             "    h[192:200]=b'AP01MNU1';struct.pack_into('<I',h,200,4)\n"
             f"    settings_hooks={symbols}\n"
             "    for i,(offset,span,name) in enumerate(settings_hooks):\n"
             "        struct.pack_into('<3I',h,204+12*i,offset,symbols[name],span)\n"
             "    struct.pack_into('<I',h,32,zlib.crc32(h));payload[:256]=h")
        edit(builder, "        'image':{'path':str(output)",
             "        'settings_menu_hooks':[{'offset':hex(offset),'target':hex(target),'span':span,'original_hex':MENU_HOOKS[offset][1]} for offset,target,span in menu_hooks(payload)],\n        'image':{'path':str(output)")
        edit(builder, 'all original bytes outside one 8-byte UI hook and 2-byte unsigned OTA branch',
             'all original bytes outside the main UI hook, four pinned Settings calls and the unsigned OTA branch')
    args.diff.write_text(''.join(changes), encoding='utf-8')
    print('Attached native device-code menu and four pinned Settings call veneers:', source)

if __name__ == '__main__':
    main()
