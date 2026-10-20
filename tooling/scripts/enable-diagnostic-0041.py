"""Attach read-only diagnostics to an isolated, audit-restored AP01 build34 tree.

No hardware access. Original worktrees and deployed artifacts are left intact.
"""
from pathlib import Path
import argparse
import difflib

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root', type=Path, required=True)
parser.add_argument('--diff', type=Path, required=True)
args = parser.parse_args()
source = args.source_root.resolve()
port = source / 'ports/ap01'
platform = ROOT / 'tooling/firmware-modules'
changes = []


def edit(path, old, new):
    text = path.read_text(encoding='utf-8')
    assert text.count(old) == 1, f'Unexpected source or already patched: {path}'
    result = text.replace(old, new)
    changes.extend(difflib.unified_diff(text.splitlines(True), result.splitlines(True),
                                      fromfile=str(path.relative_to(source)), tofile=str(path.relative_to(source))))
    path.write_text(result, encoding='utf-8', newline='\n')


# Extracted String is byte-for-byte the deployed34 implementation.
assert (port/'Arduino.h').read_text() == (platform/'native_string_0041.h').read_text()
for name in ('native_string_0041.h', 'native_http_0041.h', 'native_json_0041.h',
             'native_diagnostic_0041.h', 'native_diagnostic_0041.cpp'):
    (port/name).write_bytes((platform/name).read_bytes())
edit(port/'Arduino.h', (port/'Arduino.h').read_text(), '#pragma once\n#include "native_string_0041.h"\n')
header = port/'application.h'
text = header.read_text()
start, end = text.index('struct Ap01HttpRequest'), text.index('// One business executor')
edit(header, text[start:end], '')
edit(header, '#include "firmware.h"', '#include "firmware.h"\n#include "native_diagnostic_0041.h"')
edit(header, '    Ap01FirmwarePort firmware{};', '    Ap01FirmwarePort firmware{};\n    Ap01DiagnosticPort diagnostic{};')
edit(port/'application.cpp', '    if(!strncmp(request.path,"/api/firmware/",14)) {',
     '    if(!strncmp(request.path,"/api/diagnostic/",16)) {\n'
     '        guard.release();\n'
     '        return ap01DiagnosticHttp0041(port.diagnostic,request,mac,boot);\n'
     '    }\n'
     '    if(!strncmp(request.path,"/api/firmware/",14)) {')
anchor = '    static bool firmwareBusy(void *) {return *(volatile uint8_t *)(uintptr_t)0x62fc4053!=0;}'
edit(port/'native_0041.cpp', anchor, anchor+'\n'
     '    static bool diagnosticBusy(void *p) {\n'
     '        return firmwareBusy(p) || ((Runtime *)p)->app->maintenanceActive();\n'
     '    }')
edit(port/'native_0041.cpp', '    r.app.reset(new(std::nothrow) Ap01Application',
     '    callbacks.diagnostic={&r,ap01DiagnosticFile0041,ap01DiagnosticFlash0041,diagnosticBusy};\n'
     '    r.app.reset(new(std::nothrow) Ap01Application')
for filename, nativefile, symbol, next_symbol in (
        ('vfs_0041.cpp', 'native_vfs_0041.cpp', 'int ap01DiagnosticFile0041', None),
        ('slot_0041.cpp', 'native_slot_0041.cpp', 'int ap01DiagnosticFlash0041', 'int ap01SelectedSlot0041')):
    text = (platform/nativefile).read_text()
    body = text[text.index(symbol):]
    if next_symbol:
        body = body[:body.index(next_symbol)]
    edit(port/filename, '\nnamespace {', '\n#include "native_diagnostic_0041.h"\nnamespace {')
    with (port/filename).open('a', encoding='utf-8') as output:
        output.write('\n'+body)
build = source/'tools/check-ap01-native.py'
text = build.read_text()
anchor = "repo/'ports/ap01/application.cpp'"
edit(build, anchor, anchor+", repo/'ports/ap01/native_diagnostic_0041.cpp'")
args.diff.write_text(''.join(changes), encoding='utf-8')
print('Patched isolated build34 tree:', source)
