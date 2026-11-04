#include "native_app_platform_v3.h"
#include "native_vfs_0041.h"
#include "native_io_0041.h"
#include <stdlib.h>
#include <new>
#include <string.h>
#include <stdio.h>
#include <time.h>
extern "C" const uint8_t ap01_native_manifest[256];
extern "C" int *__errno();
namespace {
Ap01ManifestEntryV3 defaultGrant(){
    Ap01ManifestEntryV3 entry{};strcpy(entry.id,"codex_status");entry.capabilities=AP01_CODEX_CAPS_V3;
    entry.tcp=18081;entry.udp=8767;entry.tasks=4;entry.pages=8;return entry;
}
bool validId(const char (&id)[32]){
    unsigned n=0;for(;n<32&&id[n];++n){char c=id[n];
        if(!((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='.'||c=='_'||c=='-'||c=='+'))return false;}
    if(!n||n==32||!strcmp(id,".")||!strcmp(id,".."))return false;
    for(;n<32;++n)if(id[n])return false;
    return true;
}
bool charge(std::atomic<uint32_t> &used,uint32_t amount,uint32_t limit){
    uint32_t previous=used.load(std::memory_order_acquire);
    do {if(previous>limit||amount>limit-previous)return false;}
    while(!used.compare_exchange_weak(previous,previous+amount,std::memory_order_acq_rel));
    return true;
}
}
bool Ap01NativeAppPlatformV3::clock(void *,uint64_t *out){*out=ap01_native0041::nowMs();return true;}
bool Ap01NativeAppPlatformV3::yield(void *){ap01_native0041::pause(1);return true;}
Ap01NativeAppPlatformV3::Ap01NativeAppPlatformV3(uint64_t boot,const Ap01BootPortV3 &backend)
    :Ap01NativeAppPlatformV3(boot,backend,defaultGrant(),false,nullptr){}
Ap01NativeAppPlatformV3::Ap01NativeAppPlatformV3(uint64_t boot,const Ap01BootPortV3 &backend,const Ap01ManifestEntryV3 &entry)
    :Ap01NativeAppPlatformV3(boot,backend,entry,true,nullptr){}
Ap01NativeAppPlatformV3::Ap01NativeAppPlatformV3(Ap01NativeAppSharedV3 &host,const Ap01BootPortV3 &backend,const Ap01ManifestEntryV3 &entry)
    :Ap01NativeAppPlatformV3(host.bootId,backend,entry,true,&host){}
Ap01NativeAppPlatformV3::Ap01NativeAppPlatformV3(uint64_t boot,const Ap01BootPortV3 &backend,const Ap01ManifestEntryV3 &entry,bool bounded,Ap01NativeAppSharedV3 *owner)
    :executable(backend),grant(entry),boundedGrant(bounded),files(ap01RomVfs(),privateRoot),
     network(ap01NativeAppNetworkPort0041(),this,clock,yield,entry.tcp,entry.udp),
     loader({this,maintenanceReady,reserve,publish}){
    validGrant=validId(grant.id)&&grant.tasks<=4&&grant.pages<=AP01_SCREEN_SET_LIMIT&&
        !(grant.capabilities&~AP01_CODEX_CAPS_V3)&&grant.tcp!=18080&&grant.udp!=18080;
    if(validGrant){
        // Preserve existing business data. Other IDs cannot claim this root.
        if(!strcmp(grant.id,"codex_status"))strcpy(privateRoot,"/resource/codex-status");
        else snprintf(privateRoot,sizeof(privateRoot),"/resource/apps/%s",grant.id);
    }
    if(owner)shared=owner;
    else {ownedShared.reset(new(std::nothrow) Ap01NativeAppSharedV3(boot,1));shared=ownedShared.get();}
    if(!shared||!validGrant||!shared->capacity||shared->capacity>AP01_MANIFEST_APPS_V3||shared->count>=shared->capacity){validGrant=false;return;}
    for(unsigned i=0;i<shared->count;++i){const auto &other=shared->contexts[i]->grant;
        if(!strcmp(grant.id,other.id)||(grant.tcp&&grant.tcp==other.tcp)||(grant.udp&&grant.udp==other.udp)){validGrant=false;return;}}
    registryIndex=shared->count;shared->contexts[shared->count++]=this;
    files.bindGate(shared->writeGate);
    refreshWindow();
    const char *hex="0123456789abcdef";
    for(unsigned i=0;i<16;++i){uint8_t v=ap01_native_manifest[36+i];build[i*2]=hex[v>>4];build[i*2+1]=hex[v&15];}
    api.abi_major=3;api.struct_bytes=sizeof(api);api.capabilities=validGrant?grant.capabilities:0;api.boot_id=boot;
    api.private_root=privateRoot;api.platform_build=build;api.app_digest=digest;
    const uint8_t *n=ap01_native_manifest+12;
    api.rom_bytes=uint32_t(n[0])|uint32_t(n[1])<<8|uint32_t(n[2])<<16|uint32_t(n[3])<<24;
    api.now_ms=[](void *){return ap01_native0041::nowMs();};
    api.pause_ms=[](void *,uint32_t n){ap01_native0041::pause(n);};
    api.random=[](void *,uint8_t *out,uint32_t n)->int32_t{return out&&n&&n<=256&&ap01_native0041::randomBytes(nullptr,out,n)?0:-1;};
    api.mac=[](void *,char out[13])->int32_t {
        if(!out)return -1;
        char mac[13];if(!ap01_native0041::wifiMac(mac))return -1;memcpy(out,mac,13);return 0;
    };
    api.utc_seconds=[](void *)->int64_t{return time(nullptr);};
    api.allocate=allocate;api.reallocate=reallocate;api.release=release;api.format=snprintf;
    api.errno_slot=[](void *){return __errno();};api.task_start=task;
    api.busy=[](void *p)->int32_t {auto &s=*(Ap01NativeAppPlatformV3 *)p;return !s.shared->services.listening()||s.shared->services.busy();};
    api.writes_allowed=[](void *p)->int32_t{return ((Ap01NativeAppPlatformV3 *)p)->shared->writeGate.writable()?1:0;};
    api.bind=[](void *p,const Ap01AppBindingV3 *b)->int32_t{auto &s=*(Ap01NativeAppPlatformV3 *)p;
        return b&&!strcmp(s.grant.id,"codex_status")?s.shared->binding.bind(*b):-1;};
    api.files=files.table();api.network=network.table();
    api.ui={&shared->host,&shared->apps[registryIndex],&appWindow,&ap01_lvgl_0041,&ap01_host_api,attach,
        ap01_host_current,ap01_host_retire,ap01_host_poll,ap01_host_set_blocked,ap01_host_cancel,
        ap01_host_button,ap01_host_rotate,ap01_host_short,ap01_window_active,ap01_window_visible,
        ap01_window_awake,ap01_window_idle,ap01_window_overlay,ap01_window_activity,ap01_window_wake,
        ap01_event_code,ap01_event_key,ap01_event_context,ap01_event_target};
    if(shared->capacity>1){
        api.ui.poll=[](ap01_screen_host *,uint32_t){};api.ui.blocked=Ap01NativeAppSharedV3::blocked;
        api.ui.cancel=[](ap01_screen_host *){};api.ui.button=[](ap01_screen_host *,int,uint32_t){};
        api.ui.rotate=[](ap01_screen_host *,int,uint32_t){return 1;};api.ui.short_press=[](ap01_screen_host *){return 1;};
    }
}
void Ap01NativeAppPlatformV3::refreshWindow(){
    appWindow=shared->window;
    if(shared->capacity>1)appWindow.stock=[](void *){};
}
bool Ap01NativeAppPlatformV3::bindWindow(void *root,void (*stock)(void *)){
    return shared&&shared->bindWindow(root,stock);
}
bool Ap01NativeAppPlatformV3::startMaintenance(){return shared&&shared->startMaintenance();}
bool Ap01NativeAppPlatformV3::maintenanceReady(void *p){auto *s=(Ap01NativeAppPlatformV3 *)p;return s->shared&&s->shared->services.listening();}
bool Ap01NativeAppSharedV3::bindWindow(void *root,void (*stock)(void *)){
    if(!root||!stock||window.win)return false;
    window.win=root;window.stock=stock;window.context=this;window.poll=poll;window.event=event;window.services=&services;
    auto port=ap01_window_port(&window);
    if(ap01_host_init(&host,&port,apps,0)!=AP01_HOST_OK||!ap01_window_bind(&window))return false;
    for(unsigned i=0;i<count;++i){auto &app=*contexts[i];app.refreshWindow();
        if(app.loader.entered()&&app.loader.event(3,nullptr,0)!=AP01_APP_V3_OK){ap01_window_detach(&window);return false;}}
    windowPresent.store(true,std::memory_order_release);return true;
}
bool Ap01NativeAppSharedV3::startMaintenance(){
    if(maintenanceStarted)return false;
    maintenanceStarted=services.start(binding.bridge(),bootId,this,healthy);return maintenanceStarted;
}
bool Ap01NativeAppSharedV3::healthy(void *p){auto &s=*(Ap01NativeAppSharedV3 *)p;
    return uint32_t(ap01_native0041::nowMs())-s.heartbeat.load(std::memory_order_acquire)<5000;
}
void Ap01NativeAppSharedV3::blocked(ap01_screen_host *h,int blocked){
    auto *w=(ap01_window_0041 *)h->port.context;auto *s=(Ap01NativeAppSharedV3 *)w->context;
    if(s&&s->dispatch)s->dispatch->uiBlocked=blocked!=0;
}
void Ap01NativeAppSharedV3::poll(void *p){
    auto &s=*(Ap01NativeAppSharedV3 *)p;s.heartbeat.store(uint32_t(ap01_native0041::nowMs()),std::memory_order_release);
    if(s.pollHook&&s.window.win)s.pollHook(s.pollContext,false);
    bool blocked=s.services.busy();
    for(unsigned i=0;i<s.count;++i){s.dispatch=s.contexts[i];Ap01NativeAppPlatformV3::tick(s.dispatch);blocked|=s.dispatch->uiBlocked;}
    s.dispatch=nullptr;
    if(s.capacity>1){ap01_host_set_blocked(&s.host,blocked);ap01_host_poll(&s.host,uint32_t(ap01_native0041::nowMs()));}
    if(s.pollHook&&s.window.win)s.pollHook(s.pollContext,true);
}
void Ap01NativeAppSharedV3::event(void *p,void *e){
    auto &s=*(Ap01NativeAppSharedV3 *)p;unsigned code=ap01_event_code(e);
    bool deleting=code==0x29&&ap01_event_target(e)==s.window.win;
    if(s.capacity>1&&(code==1||code==0xb))ap01_host_button(&s.host,code==1,uint32_t(ap01_native0041::nowMs()));
    bool delivered=false;
    for(unsigned i=0;i<s.count;++i){auto &app=*s.contexts[i];s.dispatch=&app;if(app.appEvent){app.appEvent(app.appInstance,e);delivered=true;}}
    s.dispatch=nullptr;
    if(!delivered&&s.capacity==1&&s.window.stock)s.window.stock(e);
    if(deleting){s.windowPresent.store(false,std::memory_order_release);ap01_host_destroy(&s.host);ap01_window_detach(&s.window);
        for(unsigned i=0;i<s.count;++i){s.contexts[i]->attached=false;s.contexts[i]->appWindow.win=nullptr;}return;}
    if(s.capacity>1&&code==0x11){
        if(s.services.busy()||s.host.blocked){
            ap01_host_cancel(&s.host);
            if(!ap01_host_current(&s.host)&&s.window.stock)s.window.stock(e);
            return;
        }
        unsigned key=ap01_event_key(e);int consumed=key==0x13?ap01_host_rotate(&s.host,1,uint32_t(ap01_native0041::nowMs())):
            key==0x14?ap01_host_rotate(&s.host,-1,uint32_t(ap01_native0041::nowMs())):key==10?ap01_host_short(&s.host):0;
        if(!consumed&&s.window.stock)s.window.stock(e);
    }else if(!delivered&&s.capacity>1&&s.window.stock)s.window.stock(e);
}
void Ap01NativeAppPlatformV3::tick(void *p){
    auto &s=*(Ap01NativeAppPlatformV3 *)p;
    if(s.bootRequest.load(std::memory_order_acquire)==2){
        auto result=s.boot({&s,s.bootBytes,readBootFile},s.bootLimits,s.expectedDigest);
        s.bootResult.store(result,std::memory_order_release);
        if(result!=Ap01BootResultV3::Waiting){s.bootRequest.store(3,std::memory_order_release);
            s.bootIo.close(s.bootIo.context,s.bootFd);s.bootFd=-1;}
    }
    if(s.appTick)s.appTick(s.appInstance);
}
bool Ap01NativeAppPlatformV3::readBootFile(void *p,uint32_t at,uint8_t *out,uint32_t n){
    auto &s=*(Ap01NativeAppPlatformV3 *)p;
    return at<=s.bootBytes&&n<=s.bootBytes-at&&at<=INT32_MAX&&
        s.bootIo.seek(s.bootIo.context,s.bootFd,int32_t(at),0)==int32_t(at)&&
        s.bootIo.read(s.bootIo.context,s.bootFd,out,n)==int(n);
}
bool Ap01NativeAppPlatformV3::stageFile(const char *path,const Apx2Limits &limits){
    uint32_t empty=0;if(!bootRequest.compare_exchange_strong(empty,1,std::memory_order_acq_rel))return false;
    bootIo=ap01RomVfs();
    if(path&&limits.abi_major==3&&bootIo.open&&bootIo.close&&bootIo.read&&bootIo.seek&&bootIo.size){
        bootFd=bootIo.open(bootIo.context,path,0);
        if(bootFd>=0){
            int32_t bytes=bootIo.size(bootIo.context,bootFd);
            if(bytes>=int32_t(APX2_HEADER)&&uint32_t(bytes)<=limits.package_bytes){
                bootBytes=uint32_t(bytes);uint8_t header[APX2_HEADER];
                if(readBootFile(this,0,header,sizeof(header))){
                    memcpy(expectedDigest,header+192,32);bootLimits=limits;
                    bootRequest.store(2,std::memory_order_release);return true;
                }
            }
            bootIo.close(bootIo.context,bootFd);bootFd=-1;
        }
    }
    bootResult.store(Ap01BootResultV3::Package,std::memory_order_release);
    bootRequest.store(4,std::memory_order_release);return false;
}
int32_t Ap01NativeAppPlatformV3::attach(void *p,void *instance,ap01_screen_slot *slots,ap01_page_0041 *pages,uint32_t count,
                                     void (*poll)(void *,uint32_t),void (*tick)(void *),void (*event)(void *,void *)){
    auto &s=*(Ap01NativeAppPlatformV3 *)p;
    if(s.attached||!s.shared->services.listening()||!instance||!slots||!pages||!count||count>s.grant.pages||!poll||!tick||!event)return -1;
    if(s.shared->host.app_count!=s.registryIndex)return -1;
    if(!ap01_window_mount(&s.shared->window,slots,pages,count))return -1;
    auto &app=s.shared->apps[s.registryIndex];uint32_t revision=app.revision+1;
    app={s.grant.id,nullptr,slots,count,0,0,instance,poll};
    if(ap01_host_append(&s.shared->host,s.shared->apps,s.shared->capacity)!=AP01_HOST_OK)return -1;
    app.revision=revision?revision:1;
    s.appInstance=instance;s.appTick=tick;s.appEvent=event;s.attached=true;return 0;
}
bool Ap01NativeAppPlatformV3::reserve(void *p,const Apx2View &view,Ap01BootMemoryV3 &memory){
    auto &s=*(Ap01NativeAppPlatformV3 *)p;
    if(!s.validGrant||!s.executable.reserve||!s.executable.publish||strcmp(view.app_id,s.grant.id))return false;
    if(s.boundedGrant&&(uint64_t(view.image_bytes)+view.bss_bytes!=s.grant.image_bytes||
       view.heap_bytes!=s.grant.heap_bytes||view.stack_bytes!=s.grant.stack_bytes||
       view.required_services!=s.grant.capabilities||memcmp(view.digest,s.grant.digest,32)))return false;
    if(!s.executable.reserve(s.executable.context,view,memory))return false;
    s.heapLimit=view.heap_bytes;s.stackLimit=view.stack_bytes;
    const char *hex="0123456789abcdef";
    for(unsigned i=0;i<32;++i){s.digest[2*i]=hex[view.digest[i]>>4];s.digest[2*i+1]=hex[view.digest[i]&15];}
    return true;
}
bool Ap01NativeAppPlatformV3::publish(void *p,const Ap01BootMemoryV3 &memory,const Apx2View &view,Ap01AppEntriesV3 &entries){
    auto &s=*(Ap01NativeAppPlatformV3 *)p;
    return s.executable.publish(s.executable.context,memory,view,entries);
}
Ap01BootResultV3 Ap01NativeAppPlatformV3::boot(const Apx2Reader &reader,const Apx2Limits &limits,const uint8_t expected[32]){
    return loader.boot(reader,limits,expected,api,this);
}
bool Ap01NativeAppPlatformV3::writes(bool allow){
    return shared&&shared->capacity==1&&shared->writes(allow);
}
void *Ap01NativeAppPlatformV3::allocate(void *p,uint32_t bytes){
    auto &s=*(Ap01NativeAppPlatformV3 *)p;
    if(bytes>UINT32_MAX-sizeof(Allocation))return nullptr;
    uint32_t chargeBytes=bytes+sizeof(Allocation);
    if(!charge(s.heapUsed,chargeBytes,s.heapLimit))return nullptr;
    auto *allocation=(Allocation *)malloc(chargeBytes);
    if(!allocation){s.heapUsed.fetch_sub(chargeBytes,std::memory_order_acq_rel);return nullptr;}
    allocation->owner=&s;allocation->bytes=chargeBytes;
    uint32_t current=s.heapUsed.load(std::memory_order_acquire),peak=s.heapPeak.load(std::memory_order_acquire);
    while(peak<current&&!s.heapPeak.compare_exchange_weak(peak,current,std::memory_order_acq_rel)){}
    return allocation+1;
}
void Ap01NativeAppPlatformV3::release(void *p,void *memory){
    if(!memory)return;
    auto &s=*(Ap01NativeAppPlatformV3 *)p;auto *a=(Allocation *)memory-1;
    if(a->owner!=&s)return;
    uint32_t bytes=a->bytes;a->owner=nullptr;free(a);s.heapUsed.fetch_sub(bytes,std::memory_order_acq_rel);
}
void *Ap01NativeAppPlatformV3::reallocate(void *p,void *memory,uint32_t bytes){
    if(!memory)return allocate(p,bytes);
    if(!bytes){release(p,memory);return nullptr;}
    auto *a=(Allocation *)memory-1;if(a->owner!=p)return nullptr;
    uint32_t old=a->bytes-sizeof(Allocation);if(bytes<=old)return memory;
    void *next=allocate(p,bytes);if(!next)return nullptr;
    memcpy(next,memory,old);release(p,memory);return next;
}
int32_t Ap01NativeAppPlatformV3::task(void *p,const char *name,void *(*entry)(void *),uint32_t stack,void *context){
    auto &s=*(Ap01NativeAppPlatformV3 *)p;
    if(!name||!name[0]||strlen(name)>31||!entry||stack<256||(stack&15)||!charge(s.taskCount,1,s.grant.tasks))return -1;
    if(!charge(s.stackUsed,stack,s.stackLimit)){s.taskCount.fetch_sub(1,std::memory_order_acq_rel);return -1;}
    uint32_t id=0;
    if(ap01_native0041::thread(&id,name,entry,stack,context)){
        s.stackUsed.fetch_sub(stack,std::memory_order_acq_rel);s.taskCount.fetch_sub(1,std::memory_order_acq_rel);return -1;
    }
    // Whole-boot reservation: even an exited task doesn't enable online replacement.
    return 0;
}
#ifdef __riscv
// Existing platform-only diagnostics layout, unrelated to the loaded App ABI.
__attribute__((section(".ap01_abi"),used))
const uint32_t Ap01NativeAppPlatformV3::platformAbi[4]={3,sizeof(Ap01NativeAppPlatformV3),
    offsetof(Ap01NativeAppPlatformV3,shared),sizeof(Ap01NativeAppSharedV3)};
#endif
