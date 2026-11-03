#pragma once
#include "app_file_abi_v2.h"
#include "app_generation_0041.h"
#include "native_filesystem_0041.h"
// Firmware-owned bounded descriptor ledger. No mount/format operation is
// exposed. The platform prepares the business root before launching an App.
class Ap01AppFiles0041 {
    struct Slot {uint32_t handle=0,generation=0;int fd=-1;bool writable=false;};
    Ap01AppGeneration0041 &gate;
    Ap01VfsOps io;
    const char *root;
    Slot slots[16];
    uint32_t nextHandle=1,writableGeneration=0;
    std::atomic_flag lock=ATOMIC_FLAG_INIT;
    bool failed=false;
    bool path(const char input[96],char out[224]) const;
    static int32_t invoke(void *,uint32_t,uint32_t,uint32_t,const void *,uint32_t,void *,uint32_t,uint32_t *);
public:
    Ap01AppFiles0041(Ap01AppGeneration0041 &g,const Ap01VfsOps &v,const char *businessRoot):gate(g),io(v),root(businessRoot){}
    ap01_app_services_v2 table(uint32_t generation){return {2,sizeof(ap01_app_services_v2),generation,0,AP01_APP_FILE_CAPABILITY,this,invoke};}
    // Executor-only. False means an in-flight operation/invalid generation:
    // retry before declaring writes frozen. Successful freeze drains writes.
    bool writes(uint32_t generation,bool allow);
    // After gate.close and lease drain, close all remaining handles. Any close
    // error is sticky: do not retry an ambiguous descriptor; require reboot.
    bool drain();
};
