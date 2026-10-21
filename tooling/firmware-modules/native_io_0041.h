#ifndef AP01_NATIVE_IO_0041_H
#define AP01_NATIVE_IO_0041_H
#include <stddef.h>
#include <stdint.h>
namespace ap01_native0041 {
struct PollFd {int32_t fd;uint32_t events,revents;void *privateFields[3];};
struct Address {uint16_t family,port;uint32_t ip;uint8_t padding[8];};
struct Clock {int32_t seconds,nanos;};
struct Flash {int32_t fd=-1,flip=0;};
uint64_t nowMs();
void pause(unsigned ms);
void closeFd(int fd);
bool randomBytes(void *,uint8_t *,size_t);
bool wifiMac(char (&text)[13]);
bool waitFd(int fd,unsigned events,uint64_t deadline);
int receive(void *,uint8_t *,size_t,uint64_t);
int send(void *,const uint8_t *,size_t,uint64_t);
int listener(unsigned port,bool udp=false);
int accept(int fd);
int receiveFrom(int fd,uint8_t *,size_t,Address *,unsigned *);
int sendTo(int fd,const void *,size_t,const Address *,unsigned);
int thread(uint32_t *,const char *,void *(*)(void *),unsigned,void *);
bool firmwareBusy();
const char *updateSlot();
int flashOpen(Flash *,uint32_t);
int flashWrite(Flash *,uint32_t,const void *,uint32_t);
int flashVerify(Flash *,uint32_t);
void flashClose(Flash *);
void reboot();
bool mainHook(void (*)(void *),unsigned);
void registerStock(void *,void (*)(void *),unsigned,void *);
}
#endif
