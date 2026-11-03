#pragma once
#include "app_core_abi_v2.h"
#include "app_generation_0041.h"
struct Ap01AppCorePort0041 {
    void *context=nullptr;
    bool (*clock)(void *,uint64_t *)=nullptr;
    bool (*random)(void *,uint8_t *,uint32_t)=nullptr;
    bool (*mac)(void *,char out[13])=nullptr;
    bool (*yield)(void *)=nullptr;
    bool (*utc)(void *,uint64_t *)=nullptr;
};
// Firmware-resident. The port and gate outlive any service-table snapshot.
// No mutable generation binding: each invocation leases its captured generation.
class Ap01AppCore0041 {
    Ap01AppGeneration0041 &gate;
    Ap01AppCorePort0041 port;
    static int32_t invoke(void *,uint32_t,uint32_t,uint32_t,const void *,uint32_t,void *,uint32_t,uint32_t *);
public:
    Ap01AppCore0041(Ap01AppGeneration0041 &g,const Ap01AppCorePort0041 &p):gate(g),port(p){}
    ap01_app_services_v2 table(uint32_t generation){return {2,sizeof(ap01_app_services_v2),generation,0,AP01_APP_CORE_CAPABILITY,this,invoke};}
};
Ap01AppCorePort0041 ap01NativeAppCorePort0041();
