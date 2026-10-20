"""Attach list-only Wi-Fi management to an isolated diagnostic0041 source tree.

Never flashes a device. Existing native diagnostics and network are preserved.
"""
from pathlib import Path
import argparse,difflib

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root',type=Path,required=True)
parser.add_argument('--diff',type=Path,required=True)
args=parser.parse_args();source=args.source_root.resolve();port=source/'ports/ap01'
platform=Path(__file__).resolve().parents[1]/'firmware-modules';changes=[]

def edit(path,old,new):
    text=path.read_text();assert text.count(old)==1,str(path)
    value=text.replace(old,new)
    changes.extend(difflib.unified_diff(text.splitlines(True),value.splitlines(True),fromfile=str(path.relative_to(source)),tofile=str(path.relative_to(source))))
    path.write_text(value,encoding='utf-8',newline='\n')

for name in ['native_wifi_profiles_0041.h','native_wifi_profiles_0041.cpp','native_wifi_profiles_port_0041.h','native_wifi_profiles_port_0041.cpp']:
    data=(platform/name).read_text()
    if name.endswith('port_0041.cpp'):data=data.replace('#include "native_vfs_0041.h"','#include "vfs_0041.h"')
    (port/name).write_text(data,encoding='utf-8',newline='\n')
header=port/'application.h'
if 'Ap01WifiProfilesPort wifiProfiles' not in header.read_text():
    edit(header,'#include "firmware.h"','#include "firmware.h"\n#include "native_wifi_profiles_0041.h"')
    edit(header,'    Ap01FirmwarePort firmware{};','    Ap01FirmwarePort firmware{};\n    Ap01WifiProfilesPort wifiProfiles{};')
    edit(port/'application.cpp','    if(!strncmp(request.path,"/api/firmware/",14)) {',
         '    if(!strncmp(request.path,"/api/wifi/",10)) {\n'
         '        guard.release();\n'
         '        return ap01WifiProfilesHttp0041(port.wifiProfiles,request,mac);\n'
         '    }\n'
         '    if(!strncmp(request.path,"/api/firmware/",14)) {')
    edit(port/'native_0041.cpp','#include "vfs_0041.h"','#include "vfs_0041.h"\n#include "native_wifi_profiles_port_0041.h"')
    edit(port/'native_0041.cpp','    r.app.reset(new(std::nothrow) Ap01Application',
         '    callbacks.wifiProfiles=ap01WifiProfilesNativePort0041(&r,diagnosticBusy);\n'
         '    r.app.reset(new(std::nothrow) Ap01Application')
    edit(source/'tools/check-ap01-native.py',"repo/'ports/ap01/native_diagnostic_0041.cpp'",
         "repo/'ports/ap01/native_diagnostic_0041.cpp', repo/'ports/ap01/native_wifi_profiles_0041.cpp', repo/'ports/ap01/native_wifi_profiles_port_0041.cpp'")
args.diff.write_text(''.join(changes),encoding='utf-8')
print('Attached passive profiles API; no network mutation callbacks:',source)
