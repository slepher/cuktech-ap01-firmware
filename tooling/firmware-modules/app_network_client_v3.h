#pragma once
#include "app_network_api_v3.h"
#include <stddef.h>
#include <limits.h>
// App-local convenience only: calls the resident table directly, no RPC payload,
// retries or copied buffers. Deadline enforcement belongs to the platform.
class Ap01AppNetworkClientV3 {
    Ap01NetworkOpsV3 io;
public:
    explicit Ap01AppNetworkClientV3(const Ap01NetworkOpsV3 &table):io(table){}
    int listen(uint16_t port,bool udp=false){return io.listen(io.context,port,udp);}
    int accept(int fd){return io.accept(io.context,fd);}
    bool close(int fd){return !io.close(io.context,fd);}
    bool wait(int fd,unsigned events,uint64_t deadline){return io.wait(io.context,fd,events,deadline)>0;}
    int receive(int fd,uint8_t *out,size_t n,uint64_t deadline){return n>INT32_MAX?-1:io.receive(io.context,fd,out,uint32_t(n),deadline);}
    int send(int fd,const uint8_t *in,size_t n,uint64_t deadline){return n>INT32_MAX?-1:io.send(io.context,fd,in,uint32_t(n),deadline);}
    int receiveFrom(int fd,uint8_t *out,size_t n,Ap01PeerV3 &peer){return n>INT32_MAX?-1:io.receive_from(io.context,fd,out,uint32_t(n),&peer);}
    int sendTo(int fd,const void *in,size_t n,const Ap01PeerV3 &peer){return n>INT32_MAX?-1:io.send_to(io.context,fd,(const uint8_t *)in,uint32_t(n),&peer);}
};
