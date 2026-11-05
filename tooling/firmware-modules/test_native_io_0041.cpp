// Production native adapter with ROM calls replaced; no network or device.
#include "native_io_0041.h"
#include <assert.h>
#include <stdio.h>
#include <vector>
using namespace ap01_native0041;
namespace {
std::vector<uint64_t> times;
size_t clockAt;
int polls, expectedTimeout, pollResult, errorCode;
unsigned returnedEvents;
int socketType, failure, closes, binds, listens, options;
int clockFailure;bool failClockAfterPoll;
int pauses,transferCalls,transferFailures;
int clockCall(unsigned kind, Clock *value){
    if(clockFailure){
        value->seconds=clockFailure==2?-1:0;
        value->nanos=clockFailure==3?-1:clockFailure==4?1000000000:0;
        return clockFailure==1?-1:0;
    }
    assert(kind==1&&clockAt<times.size());auto ms=times[clockAt++];
    value->seconds=ms/1000;value->nanos=(ms%1000)*1000000;return 0;
}
int pollCall(PollFd *fds,unsigned count,int timeout){
    if(!fds){assert(count==0&&timeout==1);++pauses;return 0;}
    assert(count==1&&fds->fd==7&&timeout>0&&timeout<=1000);
    if(expectedTimeout>=0)assert(timeout==expectedTimeout);
    ++polls;if(failClockAfterPoll)clockFailure=1;fds->revents=returnedEvents;return pollResult;
}
int *errnoCall(){return &errorCode;}
int receiveCall(int fd,void *out,size_t n,int flags){
    assert(fd==7&&n&&flags==0x40);++transferCalls;
    if(transferFailures-- >0)return -1;
    *(uint8_t *)out=0x5a;return 1;
}
int sendCall(int fd,const void *,size_t n,int flags,const void *to,unsigned bytes){
    assert(fd==7&&n&&flags==0x40&&!to&&!bytes);++transferCalls;
    return transferFailures-- >0?-1:1;
}
int socketCall(int family,int kind,int protocol){
    assert(family==2&&protocol==0);socketType=kind;return failure==1?-1:7;
}
int optionCall(int fd,int level,int option,const void *value,unsigned size){
    assert(fd==7&&level==1&&option==10&&size==sizeof(Clock));
    const auto &time=*(const Clock *)value;assert(time.seconds==2&&time.nanos==0);
    ++options;return failure==2?-1:0;
}
int bindCall(int fd,const Address *a,unsigned size){
    assert(fd==7&&size==sizeof(Address)&&a->family==2);++binds;return failure==3?-1:0;
}
int listenCall(int fd){assert(fd==7);++listens;return failure==4?-1:0;}
int closeCall(int fd){assert(fd==7);++closes;return 0;}
uintptr_t resolve(uintptr_t address){
    switch(address){
    case 0xa002696a:return (uintptr_t)clockCall;
    case 0xa003f546:return (uintptr_t)pollCall;
    case 0xa00267c0:return (uintptr_t)errnoCall;
    case 0xa00268c4:return (uintptr_t)socketCall;
    case 0xa010e532:return (uintptr_t)optionCall;
    case 0xa003f446:return (uintptr_t)bindCall;
    case 0xa01a18ce:return (uintptr_t)listenCall;
    case 0xa0026888:return (uintptr_t)closeCall;
    case 0xa010d6f6:return (uintptr_t)receiveCall;
    case 0xa003949c:return (uintptr_t)sendCall;
    default:assert(false);return 0;
    }
}
}
#define ROM_FN(address,type) ((type)resolve(address))
#include "native_io_0041.cpp"
#undef ROM_FN

int main(){
    // A single clock sample must determine both expiry and remaining budget.
    // The old two-read implementation sees 100 then 102, underflows and polls 1000 ms.
    times={100,102};clockAt=0;polls=0;expectedTimeout=1;pollResult=0;
    assert(!waitFd(7,1,101)&&polls==1&&clockAt==2);
    times={101};clockAt=0;polls=0;
    assert(!waitFd(7,1,101)&&polls==0);
    times={100};clockAt=0;expectedTimeout=1000;pollResult=1;returnedEvents=1;
    assert(waitFd(7,1,10000));
    times={100};clockAt=0;returnedEvents=8;
    assert(!waitFd(7,1,10000));
    times={100,101};clockAt=0;expectedTimeout=1;polls=0;pollResult=-1;errorCode=4;
    assert(!waitFd(7,1,101)&&polls==1);
    times={100,100,100};clockAt=0;pauses=0;
    assert(!waitFd(7,1,101)&&pauses==1); // EINTR cannot spin on a frozen clock.
    times={100};clockAt=0;errorCode=5;
    assert(!waitFd(7,1,101));
    for(clockFailure=1;clockFailure<=4;++clockFailure){
        uint64_t out=123;polls=0;
        assert(!monotonicMs(out)&&out==123&&!waitFd(7,1,101)&&polls==0);
    }
    clockFailure=0;times={0};clockAt=0;pollResult=1;returnedEvents=1;
    assert(waitFd(7,1,1)); // A valid zero timestamp is not an error.
    for(uint64_t next:{99u,100u}){
        times={100,next};clockAt=0;polls=0;pollResult=0;
        assert(!waitFd(7,1,101)&&polls==1); // Regression or stalled clock.
    }
    times={100};clockAt=0;polls=0;failClockAfterPoll=true;
    assert(!waitFd(7,1,101)&&polls==1);
    failClockAfterPoll=false;clockFailure=0;
    for(bool sending:{false,true})for(bool frozen:{false,true}){
        times=frozen?std::vector<uint64_t>{100,100,100}:std::vector<uint64_t>{100,100,101,101};
        clockAt=0;pauses=transferCalls=0;transferFailures=1;expectedTimeout=-1;
        pollResult=1;returnedEvents=sending?4:1;errorCode=11;int fd=7;uint8_t byte=0;
        int got=sending?send(&fd,&byte,1,102):receive(&fd,&byte,1,102);
        assert(got==(frozen?-1:1)&&pauses==1&&transferCalls==(frozen?1:2));
        if(!sending&&!frozen)assert(byte==0x5a);
    }
    for(bool udp:{false,true})for(failure=0;failure<=4;++failure){
        closes=binds=listens=options=0;socketType=0;
        bool failed=failure!=0&&!(udp&&failure==4);
        assert(listener(18081,udp)==(failed?-1:7));
        assert(socketType==(udp?0x802:0x801));
        assert(closes==int(failed&&failure!=1));
        assert(options==int(failure!=1));
        assert(binds==int(failure!=1&&failure!=2));
        assert(listens==int(!udp&&failure!=1&&failure!=2&&failure!=3));
    }
    puts("native I/O: deadlines, invalid/failed/regressed/frozen clock, bounded EINTR/EAGAIN retry, readiness and nonblocking listener cleanup passed");
}
