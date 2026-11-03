#pragma once
#include "app_network_abi_v2.h"
#include "app_generation_0041.h"
// Trusted resident transport. poll/send/receive must not block. accept must
// have a bounded timeout; the executor retains memory until its lease exits.
// Negative I/O result: AGAIN for retry, IO for a definitive transport failure.
struct Ap01AppNetworkPort0041 {
    void *context=nullptr;
    int (*listen)(void *,uint16_t,bool)=nullptr;
    int (*accept)(void *,int)=nullptr;
    int (*close)(void *,int)=nullptr;
    int (*poll)(void *,int,unsigned)=nullptr;
    int (*receive)(void *,int,uint8_t *,uint32_t,ap01_app_peer_v2 *)=nullptr;
    int (*send)(void *,int,const uint8_t *,uint32_t,const ap01_app_peer_v2 *)=nullptr;
};
Ap01AppNetworkPort0041 ap01NativeAppNetworkPort0041();
class Ap01AppNetwork0041 {
    struct Slot {uint32_t handle=0,generation=0;int fd=-1;unsigned kind=0;}; // 0 listener, 1 TCP, 2 UDP
    Ap01AppGeneration0041 &gate;
    Ap01AppNetworkPort0041 io;
    Slot slots[8];uint32_t nextHandle=1;
    std::atomic_flag lock=ATOMIC_FLAG_INIT;
    bool failed=false;
    static int32_t invoke(void *,uint32_t,uint32_t,uint32_t,const void *,uint32_t,void *,uint32_t,uint32_t *);
public:
    Ap01AppNetwork0041(Ap01AppGeneration0041 &g,const Ap01AppNetworkPort0041 &p):gate(g),io(p){}
    ap01_app_services_v2 table(uint32_t generation){return {2,sizeof(ap01_app_services_v2),generation,0,AP01_APP_NETWORK_CAPABILITY,this,invoke};}
    // Gate must be closed and drained. Ambiguous close failure is sticky.
    bool drain();
};
