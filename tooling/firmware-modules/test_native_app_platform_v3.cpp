#include "native_app_platform_v3.h"
#include "model_platform_v3.h"
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
        out={start,appEvent,health};return scenario!=2;
    }
    Ap01BootPortV3 port(){return {this,nullptr,reserve,publish};}
};
static bool read(void *p,uint32_t at,uint8_t *out,uint32_t n){
    auto &data=*(std::vector<uint8_t> *)p;if(uint64_t(at)+n>data.size())return false;
    memcpy(out,data.data()+at,n);return true;
}
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
    puts("native ABI 3 platform: real package/loader/provider/host; 10 boot, maintenance-first, quota, immutable C binding and failure-retention scenarios passed (host App entry substitutes)");
}
