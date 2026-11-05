#pragma once
#include "native_http_0041.h"
#include "app_generation_0041.h"
// App callbacks expose pairing/identity only. The platform never owns App state.
struct Ap01MaintenanceBridge0041 {
    void *context=nullptr;
    int (*principal)(void *,const char *,char out[65])=nullptr;
    Ap01HttpReply (*pairing)(void *,const Ap01HttpRequest &,uint64_t)=nullptr;
    bool (*online)(void *)=nullptr;
    // Immutable firmware-owned snapshot. Null/zero is only for resident XIP
    // bindings; file-loaded Apps must supply their gate and captured generation.
    Ap01AppGeneration0041 *gate=nullptr;
    uint32_t generation=0;
    // Resident ABI 3 adapter only: its VFS mutations take the platform lease.
    // Legacy bindings retain the maintenance handler's outer operation lock.
    bool coordinatesWrites=false;
};

class Ap01MaintenanceCall0041 {
    Ap01AppGeneration0041 *gate;
    bool admitted;
public:
    explicit Ap01MaintenanceCall0041(const Ap01MaintenanceBridge0041 &b)
        :gate(b.gate),admitted(gate?gate->acquire(b.generation):b.generation==0) {}
    ~Ap01MaintenanceCall0041(){if(gate&&admitted)gate->release();}
    explicit operator bool() const {return admitted;}
    Ap01MaintenanceCall0041(const Ap01MaintenanceCall0041 &)=delete;
    Ap01MaintenanceCall0041 &operator=(const Ap01MaintenanceCall0041 &)=delete;
};
