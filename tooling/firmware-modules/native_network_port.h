#pragma once
#include "app_network_api_v3.h"
#include <atomic>
enum { AP01_NET_AGAIN=-7, AP01_NET_IO=-3 };
// Trusted resident transport. poll/send/receive must not block. accept must
// have a bounded timeout; the executor retains memory until its lease exits.
// Negative I/O result: AGAIN for retry, IO for a definitive transport failure.
struct Ap01AppNetworkPort0041 {
    void *context=nullptr;
    int (*listen)(void *,uint16_t,bool)=nullptr;
    int (*accept)(void *,int)=nullptr;
    int (*close)(void *,int)=nullptr;
    int (*poll)(void *,int,unsigned)=nullptr;
    int (*receive)(void *,int,uint8_t *,uint32_t,Ap01PeerV3 *)=nullptr;
    int (*send)(void *,int,const uint8_t *,uint32_t,const Ap01PeerV3 *)=nullptr;
};
Ap01AppNetworkPort0041 ap01NativeAppNetworkPort0041();
