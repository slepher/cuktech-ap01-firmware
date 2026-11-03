#include "app_network_0041.h"
#include <string.h>
static_assert(sizeof(ap01_app_peer_v2)==8&&sizeof(ap01_app_network_request_v2)==16,"network ABI");
namespace {
struct Unlock {std::atomic_flag &lock;~Unlock(){lock.clear(std::memory_order_release);}};
bool emptyPeer(const ap01_app_peer_v2 &p){ap01_app_peer_v2 zero{};return !memcmp(&p,&zero,sizeof(p));}
}
bool Ap01AppNetwork0041::drain(){
    if(lock.test_and_set(std::memory_order_acquire))return false;
    Unlock unlock{lock};if(failed||!gate.drained())return false;
    for(auto &s:slots)if(s.fd>=0){
        if(!io.close||io.close(io.context,s.fd)){failed=true;return false;}
        s={};
    }
    return true;
}
int32_t Ap01AppNetwork0041::invoke(void *context,uint32_t generation,uint32_t service,uint32_t op,
        const void *input,uint32_t length,void *output,uint32_t capacity,uint32_t *written){
    if(!written)return AP01_SERVICE_INVALID;
    *written=0;
    if(!context||service!=AP01_APP_SERVICE_NETWORK||!input||length<16||(capacity&&!output))return AP01_SERVICE_INVALID;
    auto &self=*(Ap01AppNetwork0041 *)context;Ap01AppLease0041 lease(self.gate,generation);
    if(!lease)return AP01_SERVICE_UNAVAILABLE;
    if(self.lock.test_and_set(std::memory_order_acquire))return AP01_NET_BUSY;
    Unlock unlock{self.lock};if(self.failed)return AP01_SERVICE_UNAVAILABLE;
    for(const auto &s:self.slots)if(s.fd>=0&&s.generation!=generation)return AP01_SERVICE_UNAVAILABLE;
    ap01_app_network_request_v2 r;memcpy(&r,input,sizeof(r));
    bool sending=op==AP01_NET_SEND||op==AP01_NET_SEND_TO;
    if(op<AP01_NET_LISTEN||op>AP01_NET_SEND_TO||r.peer.reserved||
       uint64_t(length)!=sizeof(r)+uint64_t(sending?r.argument:0)||
       (sending&&r.argument>AP01_APP_NETWORK_CHUNK))return AP01_SERVICE_INVALID;
    if(op!=AP01_NET_LISTEN&&op!=AP01_NET_SEND_TO&&!emptyPeer(r.peer))return AP01_SERVICE_INVALID;
    if(!sending&&op!=AP01_NET_LISTEN&&op!=AP01_NET_POLL&&r.argument)return AP01_SERVICE_INVALID;
    bool receiving=op==AP01_NET_RECEIVE||op==AP01_NET_RECEIVE_FROM;
    unsigned prefix=op==AP01_NET_RECEIVE_FROM?sizeof(ap01_app_peer_v2):0;
    if(receiving){if(capacity<=prefix||capacity>prefix+AP01_APP_NETWORK_CHUNK)return AP01_SERVICE_INVALID;}
    else if(capacity!=(op==AP01_NET_CLOSE?0u:4u))return AP01_SERVICE_INVALID;
    Slot *slot=nullptr,*available=nullptr;
    for(auto &s:self.slots){if(s.fd<0&&!available)available=&s;if(s.fd>=0&&s.handle==r.handle)slot=&s;}
    auto &io=self.io;int result=-1;
    if(op==AP01_NET_LISTEN||op==AP01_NET_ACCEPT){
        if(!available||self.nextHandle>INT32_MAX)return AP01_NET_LIMIT;
        if(!io.close)return AP01_SERVICE_UNAVAILABLE;
        if(op==AP01_NET_LISTEN){
            // App owns business HTTP/discovery only; maintenance listeners stay resident.
            if(r.handle||r.argument>1||r.peer.ip[0]||r.peer.ip[1]||r.peer.ip[2]||r.peer.ip[3]||
               r.peer.port!=(r.argument?8767:18081))return AP01_SERVICE_INVALID;
            result=io.listen?io.listen(io.context,r.peer.port,r.argument!=0):-1;
        }else{
            if(!slot||slot->kind!=0)return AP01_SERVICE_INVALID;
            int ready=io.poll?io.poll(io.context,slot->fd,1):-1;
            if(ready<0)return AP01_SERVICE_IO;
            if(!(ready&1))return AP01_NET_AGAIN;
            result=io.accept?io.accept(io.context,slot->fd):-1;
        }
        if(result<0)return result==AP01_NET_AGAIN?result:AP01_SERVICE_IO;
        *available={self.nextHandle++,generation,result,op==AP01_NET_ACCEPT?1u:r.argument?2u:0u};
        result=int(available->handle);
    }else{
        if(!slot)return AP01_SERVICE_INVALID;
        if(op==AP01_NET_CLOSE){
            if(!io.close||io.close(io.context,slot->fd)){self.failed=true;return AP01_SERVICE_IO;}
            *slot={};return AP01_SERVICE_OK;
        }
        if(op==AP01_NET_POLL){
            if(!r.argument||(r.argument&~5u))return AP01_SERVICE_INVALID;
            result=io.poll?io.poll(io.context,slot->fd,r.argument):-1;
            if(result>=0&&(unsigned(result)&~r.argument))return AP01_SERVICE_IO;
        }else{
            bool udp=op==AP01_NET_RECEIVE_FROM||op==AP01_NET_SEND_TO;
            if(slot->kind!=(udp?2u:1u))return AP01_SERVICE_INVALID;
            if(sending){
                if(udp&&!r.peer.port)return AP01_SERVICE_INVALID;
                result=io.send?io.send(io.context,slot->fd,(const uint8_t *)input+sizeof(r),r.argument,udp?&r.peer:nullptr):-1;
                if(result>=0&&(uint32_t(result)>r.argument||(udp&&uint32_t(result)!=r.argument)))return AP01_SERVICE_IO;
            }else{
                ap01_app_peer_v2 peer{};
                result=io.receive?io.receive(io.context,slot->fd,(uint8_t *)output+prefix,capacity-prefix,udp?&peer:nullptr):-1;
                if(result>=0){
                    if(uint32_t(result)>capacity-prefix||(udp&&(!peer.port||peer.reserved)))return AP01_SERVICE_IO;
                    if(udp)memcpy(output,&peer,sizeof(peer));
                    *written=prefix+uint32_t(result);return AP01_SERVICE_OK;
                }
            }
        }
    }
    if(result<0)return result==AP01_NET_AGAIN?result:AP01_SERVICE_IO;
    uint32_t value=uint32_t(result);memcpy(output,&value,4);*written=4;return AP01_SERVICE_OK;
}
