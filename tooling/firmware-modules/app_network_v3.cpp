#include "app_network_v3.h"
#include <string.h>
#include <limits.h>
#if defined(__riscv)
static_assert(sizeof(Ap01PeerV3)==8&&sizeof(Ap01NetworkOpsV3)==36,"RV32 direct network layout");
#endif
namespace {
// Internal BUSY is distinct from transport AGAIN; neither crosses the API.
constexpr int Busy=-100;
struct Deadline {
    uint64_t end,last;uint32_t attempts;
    bool (*clock)(void *,uint64_t *);bool (*yield)(void *);void *context;
    Deadline(uint64_t until,void *p,bool (*now)(void *,uint64_t *),bool (*pause)(void *))
        :end(until),last(0),attempts(0),clock(now),yield(pause),context(p){
        if(clock&&yield&&clock(context,&last)&&last<end)
            attempts=uint32_t(end-last>60000?60000:end-last);
    }
    bool retry(){
        if(!attempts||!yield(context))return false;
        --attempts;uint64_t now=0;
        if(!clock(context,&now)||now<last||now>=end)return false;
        last=now;return true;
    }
};
}
Ap01AppNetworkV3::Slot *Ap01AppNetworkV3::slot(int32_t handle){
    for(auto &s:slots)if(s.fd>=0&&s.handle==handle)return &s;
    return nullptr;
}
int32_t Ap01AppNetworkV3::listen(void *p,uint16_t port,uint32_t udp){
    Guard g(p);auto &s=g.self;
    if(!g||udp>1||!port||port!=(udp?s.udpPort:s.tcpPort)||!s.io.listen||!s.io.close||s.nextHandle>INT32_MAX)return -1;
    for(auto &slot:s.slots)if(slot.fd<0){
        int fd=s.io.listen(s.io.context,port,udp!=0);if(fd<0)return -1;
        slot={int32_t(s.nextHandle++),fd,udp?2u:0u};return slot.handle;
    }
    return -1;
}
int32_t Ap01AppNetworkV3::accept(void *p,int32_t handle){
    Guard g(p);auto &s=g.self;
    if(!g||!s.io.accept||!s.io.poll||!s.io.close||s.nextHandle>INT32_MAX)return -1;
    auto *listener=s.slot(handle);if(!listener||listener->kind!=0)return -1;
    for(auto &slot:s.slots)if(slot.fd<0){
        if(s.io.poll(s.io.context,listener->fd,1)!=1)return -1;
        int fd=s.io.accept(s.io.context,listener->fd);if(fd<0)return -1;
        slot={int32_t(s.nextHandle++),fd,1};return slot.handle;
    }
    return -1;
}
int32_t Ap01AppNetworkV3::close(void *p,int32_t handle){
    Guard g(p);auto &s=g.self;if(!g)return -1;
    auto *slot=s.slot(handle);if(!slot)return -1;
    if(s.io.close(s.io.context,slot->fd)){s.failed=true;return -1;}
    *slot={};return 0;
}
int32_t Ap01AppNetworkV3::wait(void *p,int32_t handle,uint32_t events,uint64_t deadline){
    auto &s=*(Ap01AppNetworkV3 *)p;
    if(!events||(events&~5u)||!s.io.poll)return -1;
    Deadline budget(deadline,s.clockContext,s.clock,s.yield);if(!budget.attempts)return 0;
    do {
        {Guard g(p);if(g){
            auto *slot=s.slot(handle);if(!slot)return -1;
            int n=s.io.poll(s.io.context,slot->fd,events);
            if(n<0)return -1;
            if(n)return (uint32_t(n)&~events)?-1:n;
        }else if(g.held)return -1;}
    }while(budget.retry());
    return 0;
}
int32_t Ap01AppNetworkV3::receive(void *p,int32_t handle,uint8_t *out,uint32_t n,uint64_t deadline){
    auto &s=*(Ap01AppNetworkV3 *)p;if(!out||!n||n>INT32_MAX||!s.io.receive)return -1;
    Deadline budget(deadline,s.clockContext,s.clock,s.yield);if(!budget.attempts)return -1;
    do {
        int got=Busy;
        {Guard g(p);if(g){auto *slot=s.slot(handle);if(!slot||slot->kind!=1)return -1;
            got=s.io.receive(s.io.context,slot->fd,out,n,nullptr);
        }else if(g.held)return -1;}
        if(got>=0)return uint32_t(got)>n?-1:got;
        if(got!=Busy&&got!=AP01_NET_AGAIN)return -1;
    }while(budget.retry());return -1;
}
int32_t Ap01AppNetworkV3::send(void *p,int32_t handle,const uint8_t *in,uint32_t n,uint64_t deadline){
    auto &s=*(Ap01AppNetworkV3 *)p;if(!in||!n||n>INT32_MAX||!s.io.send)return -1;
    Deadline budget(deadline,s.clockContext,s.clock,s.yield);if(!budget.attempts)return -1;
    do {
        int got=Busy;
        {Guard g(p);if(g){auto *slot=s.slot(handle);if(!slot||slot->kind!=1)return -1;
            got=s.io.send(s.io.context,slot->fd,in,n,nullptr);
        }else if(g.held)return -1;}
        if(got>=0)return uint32_t(got)>n?-1:got;
        if(got!=Busy&&got!=AP01_NET_AGAIN)return -1;
    }while(budget.retry());return -1;
}
int32_t Ap01AppNetworkV3::receiveFrom(void *p,int32_t handle,uint8_t *out,uint32_t n,Ap01PeerV3 *peer){
    Guard g(p);auto &s=g.self;if(!g||!out||!n||n>INT32_MAX||!peer||!s.io.receive)return -1;
    auto *slot=s.slot(handle);if(!slot||slot->kind!=2)return -1;
    ap01_app_peer_v2 native{};int got=s.io.receive(s.io.context,slot->fd,out,n,&native);
    if(got<0||uint32_t(got)>n||!native.port||native.reserved)return -1;
    memcpy(peer->ip,native.ip,4);peer->port=native.port;peer->reserved=0;return got;
}
int32_t Ap01AppNetworkV3::sendTo(void *p,int32_t handle,const uint8_t *in,uint32_t n,const Ap01PeerV3 *peer){
    Guard g(p);auto &s=g.self;if(!g||(n&&!in)||n>INT32_MAX||!peer||!peer->port||peer->reserved||!s.io.send)return -1;
    auto *slot=s.slot(handle);if(!slot||slot->kind!=2)return -1;
    ap01_app_peer_v2 native{};memcpy(native.ip,peer->ip,4);native.port=peer->port;
    int got=s.io.send(s.io.context,slot->fd,in,n,&native);return got<0||uint32_t(got)!=n?-1:got;
}
