#include "native_maintenance_0041.h"
#include <assert.h>
#include <stdio.h>

struct App {
    Ap01AppGeneration0041 gate;
    unsigned principals=0,pairings=0,online=0;
    bool closeInPairing=false;
    static int principal(void *p,const char *,char out[65]) {
        auto &a=*(App *)p;++a.principals;
        assert(!a.gate.drained());strcpy(out,"test-principal");return 200;
    }
    static Ap01HttpReply pairing(void *p,const Ap01HttpRequest &,uint64_t) {
        auto &a=*(App *)p;++a.pairings;
        if(a.closeInPairing){a.gate.close();assert(!a.gate.drained());}
        Ap01HttpReply reply;reply.status=200;reply.bytes="pairing";return reply;
    }
    static bool isOnline(void *p) {++((App *)p)->online;return true;}
};
Ap01HttpRequest request(const char *path,const char *token) {
    Ap01HttpRequest r{};r.method="GET";r.path=path;r.token=token;return r;
}
int main() {
    App app;
    uint32_t first=app.gate.begin();assert(first);
    Ap01MaintenanceBridge0041 bridge{&app,App::principal,App::pairing,App::isOnline,&app.gate,first};
    Ap01VfsOps io{};LittleFSClass fs(io,"unused");
    Ap01MaintenancePort0041 port{};
    port.deviceCode=[](void *,char code[9]){memcpy(code,"01234567",9);return 0;};
    Ap01Maintenance0041 maintenance(fs,port,bridge,"AABBCCDDEEFF",1);
    assert(maintenance.begin());
    const char *owner="0123456789abcdef0123456789abcdef";
    auto health=request("/health","01234567");
    auto pairing=request("/api/pairing",owner);
    auto ownerHealth=request("/health",owner);
    assert(maintenance.handle(ownerHealth,0).status==200 && app.principals==1 && app.online==1);
    app.closeInPairing=true;
    assert(maintenance.handle(pairing,1).status==200 && app.pairings==1);
    assert(app.gate.drained()); // Lease survives callback, releases on return.
    assert(maintenance.handle(pairing,2).status==503 && app.pairings==1);
    assert(maintenance.handle(ownerHealth,3).status==503 && app.principals==1);
    auto response=maintenance.handle(health,4);
    assert(response.status==200 && strstr(response.bytes.c_str(),"\"business_online\":false"));
    assert(app.online==1); // Manual maintenance must not execute stopped App.
    auto next=app.gate.begin();assert(next==first+1);
    assert(maintenance.handle(pairing,5).status==503); // Old snapshot never adopts new generation.
    assert(maintenance.handle(health,6).status==200 && app.online==1);
    app.closeInPairing=false;
    bridge.generation=next;
    Ap01Maintenance0041 replacement(fs,port,bridge,"AABBCCDDEEFF",1);
    assert(replacement.begin() && replacement.handle(pairing,7).status==200 && app.pairings==2);
    app.gate.close();assert(app.gate.drained());
    // Inconsistent binding must fail closed, not become a resident binding.
    bridge.gate=nullptr;
    Ap01MaintenanceCall0041 bad(bridge);assert(!bad);
    Ap01MaintenanceBridge0041 resident{};
    Ap01MaintenanceCall0041 legacy(resident);assert(legacy);
    printf("maintenance gate: pairing/principal/online protected; manual health survives stop; stale bindings rejected\n");
}
