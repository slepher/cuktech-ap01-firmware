#include "native_rom_addresses.h"
#include "native_io_0041.h"
#ifndef ROM_FN
#define ROM_FN(address,type) ((type)(uintptr_t)(address))
#endif
namespace ap01_native0041 {
#ifdef __riscv
static_assert(sizeof(PollFd)==24,"0041 poll ABI");
#endif
static_assert(sizeof(Address)==16&&sizeof(Clock)==8,"0041 kernel ABI");
uintptr_t threadIdentity(){return (uintptr_t)ROM_FN(AP01_ROM_ADDR(0xa0026784),void *(*)())();}
bool monotonicMs(uint64_t &out) {
    Clock value{};
    if (ROM_FN(AP01_ROM_ADDR(0xa002696a),int (*)(unsigned,Clock *))(1,&value) || value.seconds < 0 || value.nanos < 0 || value.nanos>=1000000000) return false;
    out=uint64_t(value.seconds)*1000+value.nanos/1000000;return true;
}
uint64_t nowMs(){uint64_t out=0;monotonicMs(out);return out;}
void pause(unsigned ms) { ROM_FN(AP01_ROM_ADDR(0xa003f546),int (*)(PollFd *,unsigned,int))(nullptr,0,ms); }
void closeFd(int fd) { if(fd>=0)ROM_FN(AP01_ROM_ADDR(0xa0026888),int (*)(int))(fd); }
bool randomBytes(void *,uint8_t *out,size_t length) {
    int fd=ROM_FN(AP01_ROM_ADDR(0xa003f4f6),int (*)(const char *,int,...))("/dev/urandom",1);
    if(fd<0)return false;
    size_t done=0;
    while(done<length) {int n=ROM_FN(AP01_ROM_ADDR(0xa003f6a2),int (*)(int,void *,size_t))(fd,out+done,length-done);if(n<=0||size_t(n)>length-done)break;done+=n;}
    closeFd(fd);return done==length;
}
bool wifiMac(char (&text)[13]) {
    uint8_t bytes[6]={}; ROM_FN(AP01_ROM_ADDR(0xa005f240),void (*)(uint8_t *))(bytes);
    unsigned any=0,notFF=0;for(unsigned i=0;i<6;++i){any|=bytes[i];notFF|=bytes[i]^255;}
    if(!any||!notFF||(bytes[0]&1))return false;
    const char *hex="0123456789ABCDEF";
    for(unsigned i=0;i<6;++i){text[2*i]=hex[bytes[i]>>4];text[2*i+1]=hex[bytes[i]&15];}text[12]=0;return true;
}
namespace {
bool retryIo(uint64_t deadline){
    uint64_t before,after;
    if(!monotonicMs(before)||before>=deadline)return false;
    pause(1);
    return monotonicMs(after)&&after>before&&after<deadline;
}
}
bool waitFd(int fd,unsigned events,uint64_t deadline) {
    uint64_t previous=0;bool timedOut=false;
    for(;;) {
        uint64_t now;
        if(!monotonicMs(now)||now<previous||(timedOut&&now==previous)||now>=deadline)return false;
        previous=now;
        uint64_t left=deadline-now;PollFd p{};p.fd=fd;p.events=events;
        int n=ROM_FN(AP01_ROM_ADDR(0xa003f546),int (*)(PollFd *,unsigned,int))(&p,1,left>1000?1000:left);
        // A positive poll timeout returning zero must advance the clock. Do not
        // repeat the same deadline forever if that clock has stopped.
        timedOut=n==0;
        if(n<0){int code=*ROM_FN(AP01_ROM_ADDR(0xa00267c0),int *(*)())();if(code!=4||!retryIo(deadline))return false;}
        if(n>0)return (p.revents&events)!=0;
    }
}
int receive(void *p,uint8_t *bytes,size_t length,uint64_t deadline) {
    int fd=*(int *)p;
    while(waitFd(fd,1,deadline)) {
        int n=ROM_FN(AP01_ROM_ADDR(0xa010d6f6),int (*)(int,void *,size_t,int))(fd,bytes,length,0x40);
        if(n>=0)return n;
        int code=*ROM_FN(AP01_ROM_ADDR(0xa00267c0),int *(*)())();if((code!=4&&code!=11)||!retryIo(deadline))return -1;
    }return -1;
}
int send(void *p,const uint8_t *bytes,size_t length,uint64_t deadline) {
    int fd=*(int *)p;
    while(waitFd(fd,4,deadline)) {
        int n=ROM_FN(AP01_ROM_ADDR(0xa003949c),int (*)(int,const void *,size_t,int,const void *,unsigned))(fd,bytes,length,0x40,nullptr,0);
        if(n>=0)return n;
        int code=*ROM_FN(AP01_ROM_ADDR(0xa00267c0),int *(*)())();if((code!=4&&code!=11)||!retryIo(deadline))return -1;
    }return -1;
}
int listener(unsigned port,bool udp) {
    // 0041 socket type bit 11 sets conn.flags bit 3. TCP accept otherwise
    // waits forever even with SO_RCVTIMEO; see audit-native-network-0041.py.
    int fd=ROM_FN(AP01_ROM_ADDR(0xa00268c4),int (*)(int,int,int))(2,(udp?2:1)|0x800,0);if(fd<0)return -1;
    Address address{};address.family=2;address.port=(port>>8)|(port<<8);
    Clock timeout{2,0};
    if(ROM_FN(AP01_ROM_ADDR(0xa010e532),int (*)(int,int,int,const void *,unsigned))(fd,1,10,&timeout,sizeof(timeout)) ||
       ROM_FN(AP01_ROM_ADDR(0xa003f446),int (*)(int,const Address *,unsigned))(fd,&address,sizeof(address)) ||
       (!udp&&ROM_FN(AP01_ROM_ADDR(0xa01a18ce),int (*)(int))(fd))) {closeFd(fd);return -1;}
    return fd;
}

int accept(int fd){return ROM_FN(AP01_ROM_ADDR(0xa01a192a),int (*)(int,void *,void *))(fd,nullptr,nullptr);}
int receiveFrom(int fd,uint8_t *bytes,size_t length,Address *from,unsigned *n){return ROM_FN(AP01_ROM_ADDR(0xa003942c),int (*)(int,void *,size_t,int,Address *,unsigned *))(fd,bytes,length,0x40,from,n);}
int sendTo(int fd,const void *bytes,size_t length,const Address *to,unsigned n){return ROM_FN(AP01_ROM_ADDR(0xa003949c),int (*)(int,const void *,size_t,int,const void *,unsigned))(fd,bytes,length,0x40,to,n);}
int thread(uint32_t *id,const char *name,void *(*entry)(void *),unsigned stack,void *ctx){return ROM_FN(AP01_ROM_ADDR(0xa019750e),int (*)(uint32_t *,const char *,void *(*)(void *),unsigned,void *))(id,name,entry,stack,ctx);}
bool firmwareBusy(){return *(volatile uint8_t *)(uintptr_t)AP01_ROM_ADDR(0x62fc4053)!=0;}
const char *updateSlot(){return ROM_FN(AP01_ROM_ADDR(0xa0026e00),const char *(*)(const char *))("ro.boot.update_slot");}
int flashOpen(Flash *f,uint32_t n){return ROM_FN(AP01_ROM_ADDR(0xa00b4f54),int (*)(Flash *,uint32_t))(f,n);}
int flashWrite(Flash *f,uint32_t at,const void *bytes,uint32_t n){return ROM_FN(AP01_ROM_ADDR(0xa00b5122),int (*)(Flash *,uint32_t,const void *,uint32_t))(f,at,bytes,n);}
int flashVerify(Flash *f,uint32_t n){return ROM_FN(AP01_ROM_ADDR(0xa00b51d8),int (*)(Flash *,uint32_t,uint32_t))(f,0,n);}
void flashClose(Flash *f){ROM_FN(AP01_ROM_ADDR(0xa01addc6),void (*)(Flash *))(f);}
void reboot(){ROM_FN(AP01_ROM_ADDR(0xa0055a14),int (*)(uint32_t,void *))(0xff04,nullptr);}
bool mainHook(void (*callback)(void *),unsigned filter){return (uintptr_t)callback==AP01_ROM_ADDR(0xa00afc88)&&filter==0x11;}
void registerStock(void *root,void (*callback)(void *),unsigned filter,void *user){ROM_FN(AP01_ROM_ADDR(0xa01ad654),void (*)(void *,void (*)(void *),unsigned,void *))(root,callback,filter,user);}
}
