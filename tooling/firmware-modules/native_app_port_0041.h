#pragma once
#include "native_http_0041.h"
// App callbacks expose pairing/identity only. The platform never owns App state.
struct Ap01MaintenanceBridge0041 {
    void *context=nullptr;
    int (*principal)(void *,const char *,char out[65])=nullptr;
    Ap01HttpReply (*pairing)(void *,const Ap01HttpRequest &,uint64_t)=nullptr;
    bool (*online)(void *)=nullptr;
};
