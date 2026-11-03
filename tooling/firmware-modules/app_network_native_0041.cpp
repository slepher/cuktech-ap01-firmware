#include "app_network_0041.h"
#include "native_io_0041.h"
#include <string.h>
#define ROM_FN(address,type) ((type)(uintptr_t)(address))
namespace {
using namespace ap01_native0041;
int result(int n){if(n>=0)return n;int e=*ROM_FN(0xa00267c0,int *(*)())();if(e==4||e==11)return AP01_NET_AGAIN;return AP01_SERVICE_IO;}
int listen(void *,uint16_t port,bool udp){return listener(port,udp);}
int accept(void *,int fd){return result(ap01_native0041::accept(fd));}
int close(void *,int fd){return ROM_FN(0xa0026888,int (*)(int))(fd);}
int poll(void *,int fd,unsigned events){
    PollFd p{};p.fd=fd;p.events=events;
    int n=ROM_FN(0xa003f546,int (*)(PollFd *,unsigned,int))(&p,1,0);
    if(n<0)return result(n)==AP01_NET_AGAIN?0:AP01_SERVICE_IO;
    if(p.revents&events)return int(p.revents&events);
    return p.revents&(8|16|32)?AP01_SERVICE_IO:0;
}
int receive(void *,int fd,uint8_t *bytes,uint32_t n,ap01_app_peer_v2 *peer){
    if(!peer)return result(ROM_FN(0xa010d6f6,int (*)(int,void *,size_t,int))(fd,bytes,n,0x40));
    Address address{};unsigned length=sizeof(address);
    int got=receiveFrom(fd,bytes,n,&address,&length);if(got<0)return result(got);
    if(length!=sizeof(address)||address.family!=2)return AP01_SERVICE_IO;
    memcpy(peer->ip,&address.ip,4);peer->port=uint16_t(address.port>>8|address.port<<8);peer->reserved=0;return got;
}
int send(void *,int fd,const uint8_t *bytes,uint32_t n,const ap01_app_peer_v2 *peer){
    Address address{};
    if(peer){address.family=2;address.port=uint16_t(peer->port>>8|peer->port<<8);memcpy(&address.ip,peer->ip,4);}
    return result(ROM_FN(0xa003949c,int (*)(int,const void *,size_t,int,const void *,unsigned))
        (fd,bytes,n,0x40,peer?&address:nullptr,peer?sizeof(address):0));
}
}
Ap01AppNetworkPort0041 ap01NativeAppNetworkPort0041(){return {nullptr,listen,accept,close,poll,receive,send};}
