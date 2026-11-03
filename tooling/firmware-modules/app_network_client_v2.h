#pragma once
#include "app_network_abi_v2.h"
#include <string.h>
// App-private synchronous adapter. Every retry retains the original deadline;
// only opaque handles and fixed C payloads cross the firmware boundary.
class Ap01AppNetworkClientV2 {
    ap01_app_services_v2 services;
    struct Budget {uint64_t deadline=0,last=0;uint32_t yields=0;};
    bool clock(uint64_t &now){return !ap01_app_core_call(&services,AP01_CORE_MONOTONIC_MS,&now,8);}
    bool budget(uint64_t deadline,Budget &b){
        uint64_t now=0;if(!clock(now)||now>=deadline)return false;
        uint64_t remaining=deadline-now;b={deadline,now,uint32_t(remaining>60000?60000:remaining)};return true;
    }
    bool retry(Budget &b){
        if(!b.yields)return false;
        --b.yields;if(ap01_app_core_call(&services,AP01_CORE_YIELD,nullptr,0))return false;
        uint64_t now=0;if(!clock(now)||now<b.last||now>=b.deadline)return false;
        b.last=now;return true;
    }
    int call(unsigned op,const ap01_app_network_request_v2 &r,void *out,uint32_t capacity,uint32_t &written,const void *data=nullptr){
        written=0;
        if(services.abi_version!=2||services.struct_bytes!=sizeof(services)||services.reserved||!services.generation||
           !services.invoke||!(services.available_services&AP01_APP_NETWORK_CAPABILITY))return AP01_SERVICE_UNAVAILABLE;
        uint8_t input[sizeof(r)+AP01_APP_NETWORK_CHUNK];memcpy(input,&r,sizeof(r));uint32_t length=sizeof(r);
        if(op==AP01_NET_SEND||op==AP01_NET_SEND_TO){
            if(r.argument>AP01_APP_NETWORK_CHUNK||(r.argument&&!data))return AP01_SERVICE_INVALID;
            if(r.argument)memcpy(input+length,data,r.argument);length+=r.argument;
        }
        return services.invoke(services.context,services.generation,3,op,input,length,out,capacity,&written);
    }
    int word(unsigned op,const ap01_app_network_request_v2 &r,const void *data=nullptr){
        uint32_t value=0,written=0;int error=call(op,r,&value,4,written,data);
        return error?error:written!=4||value>INT32_MAX?AP01_SERVICE_IO:int(value);
    }
    static bool temporary(int n){return n==AP01_NET_BUSY||n==AP01_NET_AGAIN;}
public:
    explicit Ap01AppNetworkClientV2(const ap01_app_services_v2 &s):services(s){}
    int listen(uint16_t port,bool udp=false){
        uint64_t now=0;if(!clock(now)||now>UINT64_MAX-5000)return -1;Budget b;if(!budget(now+5000,b))return -1;
        ap01_app_network_request_v2 r{};r.peer.port=port;r.argument=udp;
        do{int n=word(AP01_NET_LISTEN,r);if(!temporary(n))return n;}while(retry(b));return -1;
    }
    int accept(int handle){ap01_app_network_request_v2 r{};r.handle=uint32_t(handle);return word(AP01_NET_ACCEPT,r);}
    bool close(int handle){
        uint64_t now=0;if(!clock(now)||now>UINT64_MAX-1000)return false;Budget b;if(!budget(now+1000,b))return false;
        ap01_app_network_request_v2 r{};r.handle=uint32_t(handle);
        do{uint32_t written=0;int n=call(AP01_NET_CLOSE,r,nullptr,0,written);if(!temporary(n))return !n&&!written;}while(retry(b));return false;
    }
    bool wait(int handle,unsigned events,uint64_t deadline){
        if(!events||(events&~5u))return false;Budget b;if(!budget(deadline,b))return false;
        ap01_app_network_request_v2 r{};r.handle=uint32_t(handle);r.argument=events;
        do{int n=word(AP01_NET_POLL,r);if(n>0)return !(unsigned(n)&~events);if(n<0&&!temporary(n))return false;}while(retry(b));return false;
    }
    int receive(int handle,uint8_t *out,size_t length,uint64_t deadline){
        if(!out||!length)return -1;Budget b;if(!budget(deadline,b))return -1;
        uint32_t capacity=uint32_t(length>AP01_APP_NETWORK_CHUNK?AP01_APP_NETWORK_CHUNK:length);
        ap01_app_network_request_v2 r{};r.handle=uint32_t(handle);
        do{uint32_t written=0;int n=call(AP01_NET_RECEIVE,r,out,capacity,written);
            if(!n)return written<=capacity?int(written):-1;if(!temporary(n))return -1;
        }while(retry(b));return -1;
    }
    int send(int handle,const uint8_t *input,size_t length,uint64_t deadline){
        if(!input||!length)return -1;Budget b;if(!budget(deadline,b))return -1;
        ap01_app_network_request_v2 r{};r.handle=uint32_t(handle);r.argument=uint32_t(length>AP01_APP_NETWORK_CHUNK?AP01_APP_NETWORK_CHUNK:length);
        do{int n=word(AP01_NET_SEND,r,input);if(n>=0)return uint32_t(n)<=r.argument?n:-1;if(!temporary(n))return -1;}while(retry(b));return -1;
    }
    int receiveFrom(int handle,uint8_t *out,size_t length,ap01_app_peer_v2 &peer){
        if(!out||!length)return -1;
        uint8_t bytes[sizeof(peer)+AP01_APP_NETWORK_CHUNK];uint32_t written=0;
        uint32_t capacity=sizeof(peer)+uint32_t(length>AP01_APP_NETWORK_CHUNK?AP01_APP_NETWORK_CHUNK:length);
        ap01_app_network_request_v2 r{};r.handle=uint32_t(handle);
        if(call(AP01_NET_RECEIVE_FROM,r,bytes,capacity,written)||written<sizeof(peer)||written>capacity)return -1;
        memcpy(&peer,bytes,sizeof(peer));if(peer.reserved||!peer.port)return -1;
        memcpy(out,bytes+sizeof(peer),written-sizeof(peer));return int(written-sizeof(peer));
    }
    int sendTo(int handle,const void *input,size_t length,const ap01_app_peer_v2 &peer){
        if((length&&!input)||length>AP01_APP_NETWORK_CHUNK)return -1;
        ap01_app_network_request_v2 r{};r.handle=uint32_t(handle);r.argument=uint32_t(length);r.peer=peer;
        int n=word(AP01_NET_SEND_TO,r,input);return n>=0&&size_t(n)==length?n:-1;
    }
};
