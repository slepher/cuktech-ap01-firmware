#include "model_platform_v3.h"
#include "native_rom_addresses.h"
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
int fileIndex(const char *path){
    const char *names[]={"/bindings.pending","/bindings.bin","/bundle/incoming.bin",
                         "/bundle/content.bin","/bundle/state.tmp","/bundle/state.bin"};
    size_t length=strlen(path);
    for(unsigned i=0;i<6;++i){size_t n=strlen(names[i]);if(length>=n&&!strcmp(path+length-n,names[i]))return int(i);}
    return -1;
}
Ap01ModelPlatformV3::Handle *handle(int fd){
    if(fd<20||fd>=36)return nullptr;
    auto &h=ap01ModelV3.handles[fd-20];return h.file<0?nullptr:&h;
}
bool opened(int index){for(auto &h:ap01ModelV3.handles)if(h.file==index)return true;return false;}
int open(void *,const char *path,unsigned mode){
    auto &m=ap01ModelV3;int index=fileIndex(path);
    if(index>=0){auto &f=m.files[index];
        if(mode>2||(!mode&&!f.present)||(mode&&m.threadIdentity==1))return -1;
        for(unsigned i=0;i<16;++i)if(m.handles[i].file<0){
            if(mode&&!f.bytes){f.capacity=index<2?512:index<4?262144:2048;
                f.bytes.reset(new(std::nothrow) uint8_t[f.capacity]);if(!f.bytes)return -1;}
            if(mode==1)f.size=0;if(mode)f.present=true;
            m.handles[i]={index,mode==2?f.size:0,mode!=0};return int(20+i);
        }
        return -1;
    }
    if(mode||strcmp(path,"/resource/app-current.apx2")||!m.package||m.packageOpen)return -1;
    m.packageOpen=true;m.position=0;return 10;
}
int close(void *,int fd){if(auto *h=handle(fd)){*h={};return 0;}
    if(fd!=10||!ap01ModelV3.packageOpen)return -1;ap01ModelV3.packageOpen=false;++ap01ModelV3.packageCloses;return 0;}
int read(void *,int fd,void *out,size_t n){auto &m=ap01ModelV3;
    if(auto *h=handle(fd)){auto &f=m.files[h->file];
        if(h->position>=f.size)return 0;
        if(n>f.size-h->position)n=f.size-h->position;
        if(n)memcpy(out,f.bytes.get()+h->position,n);h->position+=n;return int(n);}
    if(fd!=10||!m.packageOpen||n>m.packageBytes-m.position)return -1;
    memcpy(out,m.package+m.position,n);m.position+=uint32_t(n);return int(n);
}
int write(void *,int fd,const void *bytes,size_t n){auto &m=ap01ModelV3;auto *h=handle(fd);
    if(!h||!h->writable||m.threadIdentity==1)return -1;
    auto &f=m.files[h->file];if(n>f.capacity-h->position)return -1;
    if(n)memcpy(f.bytes.get()+h->position,bytes,n);h->position+=n;
    if(h->position>f.size)f.size=h->position;
    if(h->file<2)++m.bindingWrites;else ++m.bundleWrites;return int(n);
}
int32_t seek(void *,int fd,int32_t at,unsigned origin){auto &m=ap01ModelV3;
    if(auto *h=handle(fd)){auto &f=m.files[h->file];if(origin>2)return -1;
        int64_t next=int64_t(origin==0?0:origin==1?h->position:f.size)+at;
        if(next<0||next>f.size)return -1;h->position=uint32_t(next);return int32_t(next);}
    if(fd!=10||!m.packageOpen||origin||at<0||uint32_t(at)>m.packageBytes)return -1;
    m.position=uint32_t(at);return at;
}
int32_t size(void *,int fd){if(auto *h=handle(fd))return int32_t(ap01ModelV3.files[h->file].size);
    return fd==10&&ap01ModelV3.packageOpen?int32_t(ap01ModelV3.packageBytes):-1;}
bool directory(const char *path){size_t n=strlen(path);return n>=7&&!strcmp(path+n-7,"/bundle");}
int exists(void *,const char *path){int i=fileIndex(path);
    return i>=0?int(ap01ModelV3.files[i].present):directory(path)&&ap01ModelV3.bundleDirectory?1:0;}
int pathWrite(void *,const char *path){int i=fileIndex(path);auto &m=ap01ModelV3;
    if(i<0||m.threadIdentity==1||opened(i)||!m.files[i].present)return -1;
    m.files[i].present=false;m.files[i].size=0;return 0;}
int makeDirectory(void *,const char *){auto &m=ap01ModelV3;++m.mkdirCalls;
    if(!m.allowMkdir)return -1;m.bundleDirectory=true;return 0;}
int rename(void *,const char *a,const char *b){auto &m=ap01ModelV3;int from=fileIndex(a),to=fileIndex(b);
    if(from<0||to<0||from==to||m.threadIdentity==1||opened(from)||opened(to)||!m.files[from].present)return -1;
    m.files[to]=std::move(m.files[from]);m.files[from]={};
    if(from<2)++m.bindingRenames;else ++m.bundleRenames;return 0;
}
int capacity(void *,const char *,uint64_t *total,uint64_t *used){*total=4u<<20;*used=0;return 0;}
int listen(void *,uint16_t port,bool udp){return port==(udp?8767:18081)?(udp?101:100):-1;}
int accept(void *,int fd){auto &m=ap01ModelV3;
    if(fd!=100||!m.httpQueued||m.httpActive)return -1;
    m.httpQueued=false;m.httpActive=true;return 102;
}
int netClose(void *,int fd){auto &m=ap01ModelV3;
    if(fd==102&&m.httpActive){m.httpActive=false;++m.httpCloses;}return 0;
}
int poll(void *,int fd,unsigned events){auto &m=ap01ModelV3;
    return (fd==100&&m.httpQueued)||(fd==102&&m.httpActive)?int(events):0;
}
int receive(void *,int fd,uint8_t *out,uint32_t n,ap01_app_peer_v2 *){auto &m=ap01ModelV3;
    if(fd!=102||!m.httpActive||!m.httpInput)return AP01_NET_AGAIN;
    if(n>7)n=7;if(n>m.httpLength-m.httpRead)n=m.httpLength-m.httpRead;
    memcpy(out,m.httpInput+m.httpRead,n);m.httpRead+=n;return int(n);
}
int send(void *,int fd,const uint8_t *in,uint32_t n,const ap01_app_peer_v2 *){auto &m=ap01ModelV3;
    if(fd!=102||!m.httpActive||!m.httpOutput)return AP01_NET_AGAIN;
    if(n>11)n=11;if(n>m.httpCapacity-m.httpWritten)return -1;
    memcpy(m.httpOutput+m.httpWritten,in,n);m.httpWritten+=n;return int(n);
}
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
void onDraw(void *,void (*callback)(void *),void *context){ap01ModelV3.drawCallback=callback;ap01ModelV3.drawContext=context;}
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
    for(unsigned i=0;i<count;++i){slots[i].root=&pages[i];slots[i].child=AP01_STOCK_SCREEN_COUNT+ap01ModelV3.mountedPages+i;}
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
void *ap01_event_context(void *){return ap01ModelV3.drawContext;}
void *ap01_event_target(void *){return ap01ModelV3.eventTarget;}
}
