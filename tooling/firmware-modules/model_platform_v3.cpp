#include "model_platform_v3.h"
#include "native_services_0041.h"
#include "native_io_0041.h"
#include "native_vfs_0041.h"
#include "app_network_0041.h"
#include <string.h>
#include <new>
Ap01ModelPlatformV3 ap01ModelV3;
extern "C" const uint8_t ap01_native_manifest[256]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x70,0};
namespace {int modelErrno;}
extern "C" int *__errno(){return &modelErrno;}
struct Ap01NativeServices0041::State {};
Ap01NativeServices0041::Ap01NativeServices0041()=default;
Ap01NativeServices0041::~Ap01NativeServices0041()=default;
bool Ap01NativeServices0041::start(const Ap01MaintenanceBridge0041 &bridge,uint64_t,void *,bool (*)(void *)){
    if(state)return false;
    state.reset(new(std::nothrow) State);if(!state)return false;
    ap01ModelV3.bridge=bridge;++ap01ModelV3.maintenanceStarts;ap01ModelV3.listening=true;return true;
}
bool Ap01NativeServices0041::listening() const{return bool(state)&&ap01ModelV3.listening;}
uint32_t Ap01NativeServices0041::heartbeat() const{return uint32_t(ap01ModelV3.now);}
bool Ap01NativeServices0041::tryAppOperation(){return !ap01ModelV3.busy;}
void Ap01NativeServices0041::endAppOperation(){}
bool Ap01NativeServices0041::busy() const{return ap01ModelV3.busy;}
namespace ap01_native0041 {
uintptr_t threadIdentity(){return ap01ModelV3.threadIdentity;}
uint64_t nowMs(){return ap01ModelV3.now;}
bool monotonicMs(uint64_t &out){if(ap01ModelV3.clockFailed)return false;out=ap01ModelV3.now;return true;}
void pause(unsigned n){ap01ModelV3.now+=n;if(ap01ModelV3.pause)ap01ModelV3.pause(n);}
bool randomBytes(void *,uint8_t *out,size_t n){if(!out)return false;memset(out,7,n);return true;}
bool wifiMac(char (&out)[13]){memcpy(out,"AABBCCDDEEFF",13);return true;}
int thread(uint32_t *id,const char *,void *(*entry)(void *),unsigned stack,void *context){
    auto &m=ap01ModelV3;if(!entry||m.taskCount>=4)return -1;
    m.tasks[m.taskCount]={entry,context,stack};*id=++m.taskCount;return 0;
}
}
namespace {
int prepare(void *,const char *){return 0;}
int open(void *,const char *path,unsigned mode){
    auto &m=ap01ModelV3;
    if(mode||strcmp(path,"/resource/app-current.apx2")||!m.package||m.packageOpen)return -1;
    m.packageOpen=true;m.position=0;return 10;
}
int close(void *,int fd){if(fd!=10||!ap01ModelV3.packageOpen)return -1;ap01ModelV3.packageOpen=false;++ap01ModelV3.packageCloses;return 0;}
int read(void *,int fd,void *out,size_t n){
    auto &m=ap01ModelV3;if(fd!=10||!m.packageOpen||n>m.packageBytes-m.position)return -1;
    memcpy(out,m.package+m.position,n);m.position+=uint32_t(n);return int(n);
}
int write(void *,int,const void *,size_t){return -1;}
int32_t seek(void *,int fd,int32_t at,unsigned origin){
    if(fd!=10||!ap01ModelV3.packageOpen||origin||at<0||uint32_t(at)>ap01ModelV3.packageBytes)return -1;
    ap01ModelV3.position=uint32_t(at);return at;
}
int32_t size(void *,int fd){return fd==10&&ap01ModelV3.packageOpen?int32_t(ap01ModelV3.packageBytes):-1;}
int exists(void *,const char *){return 0;}
int pathWrite(void *,const char *){return -1;}
int makeDirectory(void *,const char *){++ap01ModelV3.mkdirCalls;return ap01ModelV3.allowMkdir?0:-1;}
int rename(void *,const char *,const char *){return -1;}
int capacity(void *,const char *,uint64_t *total,uint64_t *used){*total=4u<<20;*used=0;return 0;}
int listen(void *,uint16_t port,bool udp){return port==(udp?8767:18081)?(udp?101:100):-1;}
int accept(void *,int){return -1;}
int netClose(void *,int){return 0;}
int poll(void *,int,unsigned){return 0;}
int receive(void *,int,uint8_t *,uint32_t,ap01_app_peer_v2 *){return AP01_NET_AGAIN;}
int send(void *,int,const uint8_t *,uint32_t,const ap01_app_peer_v2 *){return AP01_NET_AGAIN;}
unsigned active(void *){return ap01ModelV3.activeChild;}
int yes(void *){return 1;}
void slide(void *,unsigned child,unsigned){ap01ModelV3.activeChild=child;}
void edge(void *,unsigned,unsigned){}
void *create(void *parent){return parent;}
void destroy(void *){}
void resize(void *,int,int){}
void align(void *,unsigned,int,int){}
void hide(void *,int){}
void *label(void *parent,const char *,int,int){return parent;}
int present(ap01_surface_0041 *,void *,const uint8_t *,const uint16_t *,uint32_t,void (*)(void *),void *){return 0;}
void retire(ap01_surface_0041 *){}
void onDraw(void *,void (*)(void *),void *){}
void text(void *,const char *){}
void color(void *,uint32_t){}
void font(void *,const void *){}
}
Ap01VfsOps ap01RomVfs(){return {&ap01ModelV3,prepare,open,close,read,write,seek,size,exists,makeDirectory,pathWrite,rename,capacity};}
Ap01AppNetworkPort0041 ap01NativeAppNetworkPort0041(){return {&ap01ModelV3,listen,accept,netClose,poll,receive,send};}
void ap01ModelStockV3(void *){++ap01ModelV3.stockEvents;}
extern "C" {
const ap01_lvgl_api_0041 ap01_lvgl_0041={1,sizeof(ap01_lvgl_api_0041),create,destroy,resize,align,hide,label,present,retire,onDraw,text,color,color,font};
int ap01_window_bind(ap01_window_0041 *w){ap01ModelV3.window=w;ap01ModelV3.mountedPages=0;w->timer=w;w->event_root=w->win;return 1;}
int ap01_window_mount(ap01_window_0041 *,ap01_screen_slot *slots,ap01_page_0041 *pages,unsigned count){
    for(unsigned i=0;i<count;++i){slots[i].root=&pages[i];slots[i].child=9+ap01ModelV3.mountedPages+i;}
    ap01ModelV3.mountedPages+=count;++ap01ModelV3.mounts;return 1;
}
ap01_screen_port ap01_window_port(ap01_window_0041 *w){return {w,active,yes,yes,slide,edge};}
void ap01_window_detach(ap01_window_0041 *w){w->win=nullptr;}
unsigned ap01_window_active(ap01_window_0041 *){return ap01ModelV3.activeChild;}
int ap01_window_visible(ap01_window_0041 *){return 1;}
int ap01_window_awake(ap01_window_0041 *){return 1;}
int ap01_window_idle(ap01_window_0041 *){return 1;}
void *ap01_window_overlay(ap01_window_0041 *w){return w->win;}
void ap01_window_activity(){}
void ap01_window_wake(){}
unsigned ap01_event_code(void *){return ap01ModelV3.eventCode;}
unsigned ap01_event_key(void *){return ap01ModelV3.eventKey;}
void *ap01_event_context(void *){return nullptr;}
void *ap01_event_target(void *){return ap01ModelV3.eventTarget;}
}
