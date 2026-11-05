#include "native_app_platform_v3.h"
#include "model_platform_v3.h"
#include "native_integrity_0041.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <vector>
using R=Ap01BootResultV3;
static unsigned scenario,starts;
static ap01_screen_slot slots[8];static ap01_page_0041 pages[8];
static void poll(void *,uint32_t){}
static void tick(void *){}
static void event(void *,void *){}
static void *worker(void *){return nullptr;}
static int32_t principal(void *,const char *,char out[65]){strcpy(out,"bound-principal");return 1;}
static int32_t pairing(void *,const Ap01HttpRequestV3 *,uint64_t,Ap01ReplyV3 emit,void *context){
    char body[]="{\"paired\":true}";
    int32_t result=emit(context,200,(const uint8_t *)body,sizeof(body)-1);
    memset(body,'x',sizeof(body)); // The platform must already own a copy.
    if(scenario==9)emit(context,200,nullptr,0);
    return result;
}
static int32_t online(void *){return 1;}
static int32_t start(const Ap01PlatformApiV3 *api,void *context,void **out){
    ++starts;assert(ap01ModelV3.maintenanceStarts==1&&ap01ModelV3.listening);
    assert(api->abi_major==3&&api->capabilities==127&&api->rom_bytes==0x700000);
    assert(api->ui.attach(context,context,slots,pages,8,poll,tick,event)==0);
    assert(api->ui.host->apps==api->ui.app&&api->ui.host->app_count==1&&api->ui.app->capacity==8);
    assert(!strcmp(api->ui.app->app_id,"codex_status")&&ap01ModelV3.mounts==1);
    assert(api->ui.attach(context,context,slots,pages,8,poll,tick,event)!=0);
    assert(api->writes_allowed(context)==0);
    auto *memory=(uint8_t *)api->allocate(context,64);assert(memory);
    memset(memory,0x5a,64);auto *larger=(uint8_t *)api->reallocate(context,memory,128);assert(larger);
    for(unsigned i=0;i<64;++i)assert(larger[i]==0x5a);
    assert(!api->allocate(context,2u<<20)&&!api->reallocate(context,larger,UINT32_MAX));
    assert(larger[0]==0x5a);api->release(context,larger);
    assert(((Ap01NativeAppPlatformV3 *)context)->usedHeap()==0);
    assert(api->task_start(context,"business",worker,32768,context)==0);
    assert(api->task_start(context,"discovery",worker,8192,context)==0);
    assert(api->task_start(context,"over-budget",worker,256,context)!=0&&ap01ModelV3.taskCount==2);
    Ap01AppBindingV3 binding{context,principal,pairing,online};
    assert(api->bind(context,&binding)==0&&api->bind(context,&binding)!=0);
    *out=context;return scenario==1?AP01_APP_V3_FAILED:AP01_APP_V3_OK;
}
static int32_t grantStart(const Ap01PlatformApiV3 *api,void *context,void **out){
    ++starts;*out=context;
    const bool peer=scenario==11;
    assert(!strcmp(api->private_root,peer?"/resource/apps/z_probe":"/resource/codex-status"));
    assert(api->files.prepare(api->files.context,peer?"/resource/codex-status":"/resource/apps/z_probe")<0);
    assert(api->ui.attach(context,context,slots,pages,8,poll,tick,event)!=0);
    assert(api->ui.attach(context,context,slots,pages,1,poll,tick,event)==0);
    assert(!strcmp(api->ui.app->app_id,peer?"z_probe":"codex_status"));
    assert(api->task_start(context,"one",worker,256,context)==(peer?-1:0));
    assert(api->task_start(context,"over-count",worker,256,context)!=0);
    assert(api->network.listen(api->network.context,18080,0)<0);
    assert(api->network.listen(api->network.context,peer?18081:18082,0)<0);
    if(peer)assert(api->network.listen(api->network.context,8767,1)<0);
    if(!peer){
        auto &net=api->network;int fd=net.listen(net.context,18081,0);assert(fd>0);
        uint64_t before=ap01ModelV3.now;ap01ModelV3.clockFailed=true;
        assert(net.wait(net.context,fd,1,before+10)==0&&ap01ModelV3.now==before);
        ap01ModelV3.clockFailed=false;
        assert(net.wait(net.context,fd,1,before+1)==0&&ap01ModelV3.now==before+1);
        assert(!net.close(net.context,fd));
    }
    return AP01_APP_V3_OK;
}
static int32_t appEvent(void *,uint32_t,const void *,uint32_t){return 0;}
static int32_t health(void *){return 0;}
struct Backend {
    std::vector<uint8_t> memory;unsigned reserves=0,publishes=0;
    static bool reserve(void *p,const Apx2View &view,Ap01BootMemoryV3 &out){
        auto &s=*(Backend *)p;++s.reserves;assert(ap01ModelV3.listening);
        if(scenario==3)return false;
        s.memory.assign(view.image_bytes+view.bss_bytes+16,0xa5);
        out={s.memory.data(),view.image_bytes+view.bss_bytes,0xa8000000};return true;
    }
    static bool publish(void *p,const Ap01BootMemoryV3 &memory,const Apx2View &view,Ap01AppEntriesV3 &out){
        auto &s=*(Backend *)p;++s.publishes;
        for(unsigned i=view.image_bytes;i<memory.capacity;++i)assert(!memory.bytes[i]);
        for(unsigned i=memory.capacity;i<s.memory.size();++i)assert(s.memory[i]==0xa5);
        out={scenario>=10?grantStart:start,appEvent,health};return scenario!=2;
    }
    Ap01BootPortV3 port(){return {this,nullptr,reserve,publish};}
};
static bool read(void *p,uint32_t at,uint8_t *out,uint32_t n){
    auto &data=*(std::vector<uint8_t> *)p;if(uint64_t(at)+n>data.size())return false;
    memcpy(out,data.data()+at,n);return true;
}
static const Ap01PlatformApiV3 *sharedApi[2]{};
static ap01_screen_slot sharedSlots[2][1];static ap01_page_0041 sharedPages[2][1];
static unsigned sharedPolls[2]={},sharedTicks[2]={};
static unsigned sharedIndex(void *p){return p==sharedApi[0]?0:1;}
static void sharedPoll(void *p,uint32_t){++sharedPolls[sharedIndex(p)];}
static void sharedTick(void *p){auto *api=(const Ap01PlatformApiV3 *)p;++sharedTicks[sharedIndex(p)];
    api->ui.poll(api->ui.host,100);api->ui.blocked(api->ui.host,0);}
static void sharedEvent(void *p,void *e){auto *api=(const Ap01PlatformApiV3 *)p;
    api->ui.window->stock(e);api->ui.rotate(api->ui.host,1,100);}
static int preparePage(void *,ap01_screen_slot *,uint32_t){return AP01_ENTER_READY;}
static int32_t sharedStart(const Ap01PlatformApiV3 *api,void *context,void **out){
    unsigned i=strstr(api->private_root,"z_probe")?1:0;sharedApi[i]=api;
    *out=(void *)api;
    assert(api->ui.attach(context,(void *)api,sharedSlots[i],sharedPages[i],1,sharedPoll,sharedTick,sharedEvent)==0);
    ap01_screen_desc page{1,sizeof(ap01_screen_desc),"page",nullptr,preparePage,nullptr,nullptr,nullptr,nullptr,1};
    assert(api->ui.screens->replace_screen_set(api->ui.app,api->ui.app->revision,&page,1)==0);
    if(i){Ap01AppBindingV3 b{context,principal,pairing,online};assert(api->bind(context,&b)<0);}
    return 0;
}
struct SharedBackend:Backend {
    static bool publish(void *p,const Ap01BootMemoryV3 &m,const Apx2View &v,Ap01AppEntriesV3 &out){
        bool okay=Backend::publish(p,m,v,out);out.start=sharedStart;return okay;}
    Ap01BootPortV3 port(){return {this,nullptr,Backend::reserve,publish};}
};
int main(int argc,char **argv){
    assert(argc==2);std::ifstream f(argv[1],std::ios::binary);
    std::vector<uint8_t> original{std::istreambuf_iterator<char>(f),{}};assert(original.size()>256);
    for(scenario=0;scenario<10;++scenario){
        ap01ModelV3={};starts=0;memset(slots,0,sizeof(slots));memset(pages,0,sizeof(pages));
        auto bytes=original;uint8_t digest[32];memcpy(digest,bytes.data()+192,32);
        if(scenario==4)bytes[24]=2;
        if(scenario==5)digest[0]^=1;
        if(scenario==8)bytes[256]^=1;
        Backend backend;Ap01NativeAppPlatformV3 platform(7,backend.port());
        assert(platform.bindWindow(&platform,ap01ModelStockV3));
        Apx2Limits limits{1u<<22,1u<<23,1u<<21,40960,1,scenario==6?0u:127u,"codex_status",3};
        Apx2Reader reader{&bytes,uint32_t(bytes.size()),read};
        assert(platform.boot(reader,limits,digest)==R::Waiting&&!backend.reserves&&!starts);
        assert(platform.startMaintenance()&&!platform.startMaintenance());
        auto &bridge=ap01ModelV3.bridge;char identity[65]={};
        assert(bridge.principal(bridge.context,"token",identity)==0&&!bridge.online(bridge.context));
        Ap01HttpRequest q{};assert(bridge.pairing(bridge.context,q,100).status==503);
        R result;
        if(scenario==7||scenario==8){
            ap01ModelV3.package=bytes.data();ap01ModelV3.packageBytes=uint32_t(bytes.size());
            assert(platform.stageFile("/resource/app-current.apx2",limits));
            assert(!platform.stageFile("/resource/app-current.apx2",limits));
            Ap01NativeAppPlatformV3::poll(&platform);result=platform.result();
            assert(ap01ModelV3.packageCloses==1&&!ap01ModelV3.packageOpen);
        }else result=platform.boot(reader,limits,digest);
        R expected=scenario==1?R::Failed:scenario==2?R::Publish:scenario==3?R::Memory:
                   scenario==4||scenario==6||scenario==8?R::Package:scenario==5?R::Identity:R::Started;
        assert(result==expected);
        assert(platform.boot(reader,limits,digest)==R::AlreadyAttempted);
        bool reserved=scenario!=3&&scenario!=4&&scenario!=5&&scenario!=6&&scenario!=8;
        assert(platform.execution().retained()==reserved);
        if(starts){
            assert(platform.reservedStack()==40960&&platform.peakHeap()>=192);
            assert(bridge.principal(bridge.context,"token",identity)==1&&!strcmp(identity,"bound-principal"));
            auto reply=bridge.pairing(bridge.context,q,100);
            assert(reply.status==(scenario==9?503:200));
            if(scenario!=9)assert(!strcmp(reply.bytes.c_str(),"{\"paired\":true}"));
        }
        assert(platform.execution().health()==(result==R::Started?0:AP01_APP_V3_FAILED));
    }
    for(scenario=10;scenario<16;++scenario){
        ap01ModelV3={};starts=0;auto bytes=original;
        if(scenario==11){
            memset(bytes.data()+128,0,32);memcpy(bytes.data()+128,"z_probe",7);
            memset(bytes.data()+192,0,32);uint8_t hash[32];syncSha256(bytes.data(),bytes.size(),hash);memcpy(bytes.data()+192,hash,32);
        }
        Apx2Reader reader{&bytes,uint32_t(bytes.size()),read};
        Apx2Limits limits{1u<<22,1u<<23,1u<<21,40960,1,127,nullptr,3};Apx2View view{};
        assert(apx2Validate(reader,limits,view)==Apx2Error::Ok);
        Ap01ManifestEntryV3 grant{};memcpy(grant.id,view.app_id,32);memcpy(grant.digest,view.digest,32);
        grant.image_bytes=view.image_bytes+view.bss_bytes;grant.heap_bytes=view.heap_bytes;grant.stack_bytes=view.stack_bytes;
        grant.capabilities=127;grant.pages=1;grant.tasks=scenario==11?0:1;grant.tcp=scenario==11?18082:18081;
        if(scenario==12)--grant.heap_bytes;
        if(scenario==13)strcpy(grant.id,"../bad");
        if(scenario==14)grant.tcp=18080;
        if(scenario==15)strcpy(grant.id,"other");
        Backend backend;Ap01NativeAppPlatformV3 platform(9,backend.port(),grant);
        assert(platform.bindWindow(&platform,ap01ModelStockV3)&&platform.startMaintenance());
        auto result=platform.boot(reader,limits,view.digest);
        if(scenario<12){assert(result==R::Started&&starts==1&&backend.reserves==1);}
        else {assert((result==R::Memory||result==R::Package||result==R::Invalid)&&!starts&&!backend.reserves);}
    }
    {
        ap01ModelV3={};scenario=20;Ap01NativeAppSharedV3 resident(17,2);
        assert(resident.bindWindow((void *)1,ap01ModelStockV3)&&resident.startMaintenance());
        SharedBackend backends[2];std::unique_ptr<Ap01NativeAppPlatformV3> apps[2];
        for(unsigned i=0;i<2;++i){auto bytes=original;
            if(i){memset(bytes.data()+128,0,32);memcpy(bytes.data()+128,"z_probe",7);
                memset(bytes.data()+192,0,32);uint8_t hash[32];syncSha256(bytes.data(),bytes.size(),hash);memcpy(bytes.data()+192,hash,32);}
            Apx2Reader reader{&bytes,uint32_t(bytes.size()),read};
            Apx2Limits limits{1u<<22,1u<<23,1u<<21,40960,1,127,nullptr,3};Apx2View view{};
            assert(apx2Validate(reader,limits,view)==Apx2Error::Ok);
            Ap01ManifestEntryV3 grant{};memcpy(grant.id,view.app_id,32);memcpy(grant.digest,view.digest,32);
            grant.image_bytes=view.image_bytes+view.bss_bytes;grant.heap_bytes=view.heap_bytes;grant.stack_bytes=view.stack_bytes;
            grant.capabilities=127;grant.pages=1;
            apps[i].reset(new Ap01NativeAppPlatformV3(resident,backends[i].port(),grant));
            assert(!apps[i]->startMaintenance());assert(apps[i]->boot(reader,limits,view.digest)==R::Started);
        }
        assert(resident.registered()==2&&ap01ModelV3.maintenanceStarts==1);
        assert(sharedApi[0]->ui.host==sharedApi[1]->ui.host&&sharedApi[0]->files.context!=sharedApi[1]->files.context);
        assert(sharedApi[0]->ui.app->count==1&&sharedApi[1]->ui.app->count==1);
        Ap01NativeAppSharedV3::poll(&resident);
        assert(sharedTicks[0]==1&&sharedTicks[1]==1&&sharedPolls[0]==1&&sharedPolls[1]==1);
        ap01ModelV3.activeChild=7;ap01ModelV3.eventCode=0x11;ap01ModelV3.eventKey=0x13;
        ap01ModelV3.window->event(ap01ModelV3.window->context,(void *)1);
        assert(ap01ModelV3.activeChild==9&&ap01ModelV3.stockEvents==0);
        Ap01NativeAppSharedV3::poll(&resident);
        ap01ModelV3.window->event(ap01ModelV3.window->context,(void *)1);
        assert(ap01ModelV3.activeChild==10&&ap01ModelV3.stockEvents==0);
        ap01ModelV3.eventKey=99;ap01ModelV3.window->event(ap01ModelV3.window->context,(void *)1);
        assert(ap01ModelV3.stockEvents==1);
    }
    puts("native ABI 3 platform: shared two-App service/registry, single input/poll dispatch; real package/loader/provider/host; 16 boot, maintenance-first, per-App grants, quota, immutable C binding and failure-retention scenarios passed (host App entry substitutes)");
}
