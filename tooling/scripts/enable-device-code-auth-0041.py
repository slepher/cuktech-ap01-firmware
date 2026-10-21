"""Gate manual Wi-Fi/diagnostic APIs with the native menu code. No device I/O.

Apply to an isolated candidate04 source, or the current integration source.
Existing business, pairing and firmware/recovery authentication is preserved.
"""
from pathlib import Path
import argparse
import difflib

AUTH = '''bool Ap01Application::manualAuth(const Ap01HttpRequest &request, uint64_t now, Ap01HttpReply &reply) {
    // Maintenance has one executor. No code is cached across requests/rotation.
    if (now < manualRetryAt) {
        reply.status = 429;
        reply.bytes = "{\\"result\\":\\"rejected\\",\\"error\\":\\"device_code_rate_limited\\",\\"stage\\":\\"manual_auth\\",\\"action\\":\\"wait_30_seconds\\"}";
        return false;
    }
    char code[9] = {};
    if (!port.deviceCode || port.deviceCode(port.context, code)) {
        reply.status = 503;
        reply.bytes = "{\\"result\\":\\"rejected\\",\\"error\\":\\"device_code_unavailable\\",\\"stage\\":\\"manual_auth\\",\\"action\\":\\"open_device_code_menu\\"}";
        return false;
    }
    unsigned mismatch = 0;
    if (!request.token || strlen(request.token) != 8) mismatch = 1;
    else for (unsigned i = 0; i < 8; ++i) mismatch |= unsigned(uint8_t(code[i]) ^ uint8_t(request.token[i]));
    memset(code, 0, sizeof(code));
    if (mismatch) {
        if (++manualFailures >= 5) { manualFailures = 0; manualRetryAt = now + 30000; }
        reply.status = 401;
        reply.bytes = "{\\"result\\":\\"rejected\\",\\"error\\":\\"device_code\\",\\"stage\\":\\"manual_auth\\",\\"action\\":\\"enter_current_menu_code\\"}";
        return false;
    }
    manualFailures = 0; manualRetryAt = 0;
    return true;
}
'''

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--diff', type=Path, required=True)
    a = p.parse_args()
    root = a.source_root.resolve()
    changes = []
    edits = []
    def edit(name, old, new):
        path = root/'ports/ap01'/name
        text = next((v for k, v in reversed(edits) if k == path), None)
        if text is None: text = path.read_text(encoding='utf-8')
        assert text.count(old) == 1, ('unexpected source', path, old[:70])
        edits.append((path, text.replace(old, new)))

    edit('application.h', '    Ap01DiagnosticPort diagnostic{};',
         '    Ap01DiagnosticPort diagnostic{};\n    // Reads the committed menu code; never creates/rotates it from HTTP.\n    int (*deviceCode)(void *, char out[9]) = nullptr;')
    edit('application.h', '    bool ready = false;',
         '    bool ready = false;\n    unsigned manualFailures = 0;\n    uint64_t manualRetryAt = 0;\n    bool manualAuth(const Ap01HttpRequest &, uint64_t, Ap01HttpReply &);')
    edit('application.cpp', 'Ap01HttpReply Ap01Application::maintenanceHttp(', AUTH+'Ap01HttpReply Ap01Application::maintenanceHttp(')
    edit('application.cpp', '    maintenanceTick(now);\n    BindingGuard guard(port);', '''    maintenanceTick(now);
    const bool wifi = !strncmp(request.path,"/api/wifi/",10);
    const bool diagnostic = !strncmp(request.path,"/api/diagnostic/",16);
    if (wifi || diagnostic) {
        if (!ready) { error(reply, 503, "maintenance_busy", "lifecycle"); return reply; }
        if (!manualAuth(request, now, reply)) return reply;
        return wifi ? ap01WifiProfilesHttp0041(port.wifiProfiles,request,mac) :
                      ap01DiagnosticHttp0041(port.diagnostic,request,mac,boot);
    }
    BindingGuard guard(port);''')
    for prefix, count, handler, arguments in (
            ('/api/wifi/', 10, 'ap01WifiProfilesHttp0041', 'port.wifiProfiles,request,mac'),
            ('/api/diagnostic/', 16, 'ap01DiagnosticHttp0041', 'port.diagnostic,request,mac,boot')):
        edit('application.cpp', f'    if(!strncmp(request.path,"{prefix}",{count})) {{\n'
             f'        guard.release();\n        return {handler}({arguments});\n    }}\n', '')
    edit('http.cpp', '''            if (authSeen || strncmp(value, "Bearer ", 7) || strlen(value+7) != 32) return fail(io, 401, "authorization", deadline);
            authSeen = true; request.token = value+7;''', '''            if (authSeen || strncmp(value, "Bearer ", 7)) return fail(io, 401, "authorization", deadline);
            const char *token = value+7;
            bool manual = maintenance && (!strncmp(request.path,"/api/wifi/",10) || !strncmp(request.path,"/api/diagnostic/",16));
            if (manual) {
                // Let the common guard count invalid credentials, including missing ones.
                if (strlen(token) > 32) return fail(io, 401, "authorization", deadline);
            } else if (strlen(token) != 32) return fail(io, 401, "authorization", deadline);
            authSeen = true; request.token = token;''')
    edit('native_0041.cpp', '#include "application.h"', '#include "application.h"\n#include "native_device_code_0041.h"')
    edit('native_0041.cpp', '    callbacks.diagnostic={&r,ap01DiagnosticFile0041,ap01DiagnosticFlash0041,diagnosticBusy};',
         '    callbacks.diagnostic={&r,ap01DiagnosticFile0041,ap01DiagnosticFlash0041,diagnosticBusy};\n    callbacks.deviceCode=[](void *,char out[9]) {return ap01DeviceCodeLoad0041(ap01RomVfs(),out);};')
    smoke = root/'ports/ap01/firmware_smoke.cpp'
    smoke_text = smoke.read_text(encoding='utf-8')
    old = '        assert(app.maintenanceHttp(request("GET","/api/diagnostic/status",{},""),1).status==401);'
    if old in smoke_text:
        edit('firmware_smoke.cpp', old, old.replace('==401','==503'))
        edit('firmware_smoke.cpp', '        app.businessOnline(false);\n        assert(app.maintenanceHttp(request("GET","/api/diagnostic/status",{}),1).status==200);',
             '        app.businessOnline(false);\n        assert(app.maintenanceHttp(request("GET","/api/diagnostic/status",{}),1).status==503);')
        edit('firmware_smoke.cpp', '        assert(app.maintenanceHttp(request("GET","/api/diagnostic/status",{}),1).status==200);',
             '        assert(app.maintenanceHttp(request("GET","/api/diagnostic/status",{}),1).status==503);')
    # All anchors must match before writing any source.
    final = dict(edits)
    for path, value in final.items():
        old = path.read_text(encoding='utf-8')
        changes.extend(difflib.unified_diff(old.splitlines(True), value.splitlines(True),
            fromfile=str(path.relative_to(root)), tofile=str(path.relative_to(root))))
        path.write_text(value, encoding='utf-8', newline='\n')
    a.diff.write_text(''.join(changes), encoding='utf-8')
    print('Manual device-code authentication attached:', root)

if __name__ == '__main__': main()
