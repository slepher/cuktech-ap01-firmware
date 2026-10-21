#pragma once
#include "native_http_0041.h"
struct Ap01Stream {
    void *context;
    // Both calls honor one absolute request deadline. EOF/error/timeout <= 0.
    int (*read)(void *, uint8_t *, size_t, uint64_t deadline);
    int (*write)(void *, const uint8_t *, size_t, uint64_t deadline);
};
using Ap01HttpHandler0041=Ap01HttpReply (*)(void *,const Ap01HttpRequest &,uint64_t);
// One bounded request/connection. System route policies stay in firmware.
bool ap01ServeNativeHttp0041(void *,Ap01HttpHandler0041,bool maintenance,const Ap01Stream &,uint64_t now,uint64_t deadline);
