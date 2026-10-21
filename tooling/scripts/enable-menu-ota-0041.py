"""Extend candidate05 application maintenance with the current menu code.

No rescue source/ROM edits, no device access, no Bridge binding creation.
"""
from pathlib import Path
import argparse,difflib

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source-root',type=Path,required=True)
p.add_argument('--diff',type=Path,required=True)
a=p.parse_args();root=a.source_root.resolve();edits={};changes=[]
def edit(name,old,new):
    path=root/'ports/ap01'/name
    s=edits.get(path,path.read_text(encoding='utf-8'))
    assert s.count(old)==1,(path,old[:70])
    edits[path]=s.replace(old,new)
edit('application.cpp','    BindingGuard guard(port);\n    if (!ready || !guard) { error(reply, 503, "maintenance_busy", "bindings"); return reply; }', '''    const bool localMaintenance = (!strncmp(request.path,"/api/firmware/",14) ||
        !strcmp(request.path,"/health") || !strcmp(request.path,"/api/maintenance/status")) &&
        (!request.token || strlen(request.token) != 32);
    if (localMaintenance && !manualAuth(request, now, reply)) return reply;
    BindingGuard guard(port);
    if (!ready || (!localMaintenance && !guard)) { error(reply, 503, "maintenance_busy", "bindings"); return reply; }''')
edit('application.cpp','    bindings.maintenance=maintenanceGate.load(std::memory_order_acquire);\n    if (!strncmp(request.path, "/api/pairing", 12))',
     '    if (guard) bindings.maintenance=maintenanceGate.load(std::memory_order_acquire);\n    if (!strncmp(request.path, "/api/pairing", 12))')
edit('application.cpp','    const char *bound=ap01BindingPrincipal(&bindings, request.token);', '''    // A local maintenance credential never creates a Bridge binding or owner.
    // The namespace survives code rotation so the current physical owner can
    // query/resume the original maintenance transaction instead of resending it.
    const char *bound=localMaintenance ? "ap01-menu-maintenance" : ap01BindingPrincipal(&bindings, request.token);''')
edit('application.cpp','            maintenanceGate.store(true,std::memory_order_release);bindings.maintenance=true;',
     '            maintenanceGate.store(true,std::memory_order_release);if (guard) bindings.maintenance=true;')
edit('http.cpp','bool manual = maintenance && (!strncmp(request.path,"/api/wifi/",10) || !strncmp(request.path,"/api/diagnostic/",16));',
     'bool manual = maintenance && (!strncmp(request.path,"/api/wifi/",10) || !strncmp(request.path,"/api/diagnostic/",16) ||\n                !strncmp(request.path,"/api/firmware/",14) || !strcmp(request.path,"/health") || !strcmp(request.path,"/api/maintenance/status"));')
for path,s in edits.items():
    old=path.read_text(encoding='utf-8');changes.extend(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile=str(path.relative_to(root)),tofile=str(path.relative_to(root))))
    path.write_text(s,encoding='utf-8',newline='\n')
a.diff.write_text(''.join(changes),encoding='utf-8')
print('Application menu-code OTA/slot authorization attached; rescue untouched')
