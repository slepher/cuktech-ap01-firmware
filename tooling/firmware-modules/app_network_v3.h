#pragma once
#include "app_network_api_v3.h"
#include "app_network_0041.h"

// Resident adapter reuses the existing ROM transport, not its invoke protocol.
class Ap01AppNetworkV3 {
    struct Slot {int32_t handle=0;int fd=-1;unsigned kind=0;};
    Ap01AppNetworkPort0041 io;
    void *clockContext;
    bool (*clock)(void *,uint64_t *);
    bool (*yield)(void *);
    uint16_t tcpPort,udpPort;
    Slot slots[8];uint32_t nextHandle=1;
    std::atomic_flag lock=ATOMIC_FLAG_INIT;
    bool failed=false;
    struct Guard {
        Ap01AppNetworkV3 &self;bool held;
        explicit Guard(void *p):self(*(Ap01AppNetworkV3 *)p),held(!self.lock.test_and_set(std::memory_order_acquire)){}
        ~Guard(){if(held)self.lock.clear(std::memory_order_release);}
        explicit operator bool()const{return held&&!self.failed;}
    };
    Slot *slot(int32_t);
    static int32_t listen(void *,uint16_t,uint32_t);
    static int32_t accept(void *,int32_t);
    static int32_t close(void *,int32_t);
    static int32_t wait(void *,int32_t,uint32_t,uint64_t);
    static int32_t receive(void *,int32_t,uint8_t *,uint32_t,uint64_t);
    static int32_t send(void *,int32_t,const uint8_t *,uint32_t,uint64_t);
    static int32_t receiveFrom(void *,int32_t,uint8_t *,uint32_t,Ap01PeerV3 *);
    static int32_t sendTo(void *,int32_t,const uint8_t *,uint32_t,const Ap01PeerV3 *);
public:
    Ap01AppNetworkV3(const Ap01AppNetworkPort0041 &backend,void *context,
                    bool (*now)(void *,uint64_t *),bool (*pause)(void *),uint16_t tcp,uint16_t udp)
        :io(backend),clockContext(context),clock(now),yield(pause),tcpPort(tcp),udpPort(udp){}
    Ap01AppNetworkV3(const Ap01AppNetworkV3 &)=delete;
    Ap01AppNetworkV3 &operator=(const Ap01AppNetworkV3 &)=delete;
    Ap01NetworkOpsV3 table(){return {this,listen,accept,close,wait,receive,send,receiveFrom,sendTo};}
};
