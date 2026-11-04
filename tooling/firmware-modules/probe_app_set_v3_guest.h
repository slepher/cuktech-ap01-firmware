// Included by the existing model guest after its allocator/scheduler definitions.
#include "native_app_file_boot_v3.h"
struct Input {const uint8_t *bytes;uint32_t size;};
struct CollectionModel {
    Input packages[2],manifest;uint32_t cursor,limit,opens=0,closes=0,position=0;
    Input *file=nullptr;bool worker=true;
};
static int openFile(void *p,const char *path,unsigned flags){
    auto &s=*(CollectionModel *)p;if(!s.worker||flags||s.file)return -1;
    Input *chosen=nullptr;
    if(!strcmp(path,"/resource/app-store/current.amf3"))chosen=&s.manifest;
    else for(auto &v:s.packages){char name[112]="/resource/app-store/packages/";const char *hex="0123456789abcdef";
        for(unsigned i=0;i<32;++i){name[29+2*i]=hex[v.bytes[192+i]>>4];name[30+2*i]=hex[v.bytes[192+i]&15];}
        memcpy(name+93,".apx2",6);if(!strcmp(path,name))chosen=&v;}
    if(!chosen)return -1;
    s.file=chosen;s.position=0;++s.opens;return 10;
}
static int closeFile(void *p,int fd){auto &s=*(CollectionModel *)p;
    if(!s.worker||fd!=10||!s.file)return -1;
    s.file=nullptr;++s.closes;return 0;}
static int32_t fileSize(void *p,int fd){auto &s=*(CollectionModel *)p;
    return s.worker&&s.file&&fd==10?int32_t(s.file->size):-1;}
static int readFile(void *p,int fd,void *out,size_t n){auto &s=*(CollectionModel *)p;
    if(!s.worker||fd!=10||!s.file||n>s.file->size-s.position)return -1;
    memcpy(out,s.file->bytes+s.position,n);s.position+=uint32_t(n);return int(n);}
static bool reserveSet(void *p,const Apx2View &v,Ap01BootMemoryV3 &out){
    auto &s=*(CollectionModel *)p;uint32_t n=(v.image_bytes+v.bss_bytes+15)&~15u;
    if(n>s.limit-s.cursor)return false;
    out={(uint8_t *)s.cursor,n,s.cursor};s.cursor+=n;return true;
}
extern "C" __attribute__((section(".text.guest_entry"))) int guest_entry(uint32_t base,const uint8_t *package,uint32_t bytes){
    asm volatile("li t0,0x6000\ncsrs mstatus,t0":::"t0");
    ap01ModelV3=Ap01ModelPlatformV3{};
    const auto *manifest=(const uint8_t *)0xa81c0000;
    auto le32=[](const uint8_t *p){return uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16|uint32_t(p[3])<<24;};
    Input selected{manifest,le32(manifest+8)};
    const auto *peer=(const uint8_t *)0xa81c1000;
    CollectionModel model{{{package,bytes},{peer,le32(peer+12)}},selected,base,base+0x80000};
    Ap01ManifestLimitsV3 limits{8,1u<<24,1u<<23,1u<<23,1u<<20,4,16,127,1u<<25,1u<<20};
    Ap01VfsOps io{};io.context=&model;io.open=openFile;io.close=closeFile;io.read=readFile;io.size=fileSize;
    auto *boot=new Ap01NativeAppFileBootV3(42,io,{&model,nullptr,reserveSet,publish},limits,1u<<22);
    CHECK(boot);auto *set=&boot->set();
    CHECK(set->shared().bindWindow((void *)1,ap01ModelStockV3));
    CHECK(!boot->stage("/resource/app-store/current.amf3")&&!model.opens&&!ap01ModelV3.taskCount);
    CHECK(set->shared().startMaintenance());
    CHECK(boot->stage("/resource/app-store/current.amf3",manifest+32));
    CHECK(model.opens==3&&model.closes==3&&!model.file&&!ap01ModelV3.taskCount);
    model.worker=false;Ap01NativeAppSharedV3::poll(&set->shared());
    CHECK(boot->result()==Ap01AppSetResultV3::Started&&set->shared().registered()==2);
    CHECK(ap01ModelV3.mounts==2&&ap01ModelV3.taskCount==2);
    CHECK(set->execution().health()==AP01_APP_V3_PENDING);
    ap01ModelV3.pause=pauseTask;
    for(unsigned round=0;round<12;++round){
        for(unsigned i=0;i<ap01ModelV3.taskCount;++i){
            if(i>=initialized){uint32_t stack=ap01ModelV3.tasks[i].stack;auto *p=(uint8_t *)malloc(stack);CHECK(p);memset(p,0xa5,stack);stackBottom[i]=p;workers[i].words[0]=uint32_t(uintptr_t(runTask));workers[i].words[1]=uint32_t(uintptr_t(p+stack));++initialized;}
            CHECK(!done[i]);current=i;modelSwitch(&scheduler,&workers[i]);
        }
        Ap01NativeAppSharedV3::poll(&set->shared());
    }
    CHECK(ap01ModelV3.taskCount==3&&set->execution().health()==AP01_APP_V3_OK);
    boot->monitor(uint32_t(ap01ModelV3.now));
    CHECK(boot->status().state==Ap01SupervisorStateV3::Healthy&&boot->status().count==2);
    CHECK(set->execution().event(1,nullptr,0)==AP01_APP_V3_OK);
    CHECK(ap01ModelV3.bridge.online(ap01ModelV3.bridge.context));
    ap01ModelV3.activeChild=7;ap01ModelV3.eventCode=0x11;ap01ModelV3.eventKey=0x13;
    ap01ModelV3.window->event(ap01ModelV3.window->context,(void *)1);
    CHECK(ap01ModelV3.activeChild==17); // Native 7 -> peer's one page after codex's eight slots.
    ap01ModelV3.eventCode=0x29;ap01ModelV3.eventTarget=(void *)1;
    ap01ModelV3.window->event(ap01ModelV3.window->context,(void *)1);
    CHECK(!set->shared().root()&&set->execution().health()==AP01_APP_V3_PENDING);
    boot->monitor(uint32_t(ap01ModelV3.now));CHECK(boot->status().state==Ap01SupervisorStateV3::WindowAbsent);
    ap01ModelV3.eventCode=0;ap01ModelV3.eventTarget=nullptr;
    CHECK(set->shared().bindWindow((void *)2,ap01ModelStockV3));
    Ap01NativeAppSharedV3::poll(&set->shared());
    CHECK(ap01ModelV3.mounts==4&&ap01ModelV3.taskCount==3&&ap01ModelV3.maintenanceStarts==1);
    CHECK(set->shared().registered()==2&&set->execution().health()==AP01_APP_V3_OK);
    boot->monitor(uint32_t(ap01ModelV3.now));CHECK(boot->status().state==Ap01SupervisorStateV3::Healthy);
    CHECK(ap01ModelV3.tasks[0].stack==32768&&ap01ModelV3.tasks[1].stack==2048&&ap01ModelV3.tasks[2].stack==8192);
    auto schedule=[&](unsigned skip,unsigned rounds)->int{
        for(unsigned round=0;round<rounds;++round){
            ap01ModelV3.now+=100;
            for(unsigned i=0;i<3;++i)if(i!=skip){CHECK(!done[i]);current=i;modelSwitch(&scheduler,&workers[i]);}
            Ap01NativeAppSharedV3::poll(&set->shared());
        }return 0;
    };
    // Freeze one worker while UI and both other workers continue. A cumulative
    // "has run once" counter or UI-only heartbeat must not pass these checks.
    for(unsigned stopped=0;stopped<3;++stopped){
        CHECK(schedule(stopped,200)==0);
        int32_t health[AP01_MANIFEST_APPS_V3]{};
        CHECK(set->execution().health(health)==AP01_APP_V3_FAILED);
        unsigned failedApp=stopped==1?1:0;
        CHECK(health[failedApp]==AP01_APP_V3_FAILED&&health[failedApp^1]==AP01_APP_V3_OK);
        if(stopped==2){boot->monitor(uint32_t(ap01ModelV3.now));
            CHECK(boot->status().fault==Ap01SupervisorFaultV3::AppFailed&&boot->status().app_index==0);}
        CHECK(schedule(3,20)==0);
        CHECK(set->execution().health()==AP01_APP_V3_OK);
    }
    boot->monitor(uint32_t(ap01ModelV3.now));CHECK(boot->status().fault==Ap01SupervisorFaultV3::AppFailed);
    // Explicit model approval; not a durable D3 commit. The actual worker must
    // observe the C-table flag, initialize writable state once, then revoke.
    CHECK(ap01ModelV3.mkdirCalls==0);
    ap01ModelV3.allowMkdir=true;CHECK(set->writes(true));CHECK(schedule(3,20)==0);
    CHECK(ap01ModelV3.mkdirCalls==1&&set->execution().health()==AP01_APP_V3_OK);
    CHECK(schedule(3,20)==0&&ap01ModelV3.mkdirCalls==1);
    CHECK(set->writes(false)&&set->writesDrained());CHECK(schedule(3,20)==0);
    ap01ModelV3.allowMkdir=false;CHECK(set->writes(true));CHECK(schedule(3,20)==0);
    CHECK(ap01ModelV3.mkdirCalls==2&&set->execution().health()==AP01_APP_V3_FAILED);
    CHECK(schedule(3,20)==0&&ap01ModelV3.mkdirCalls==2); // Failed restore is never retried in place.
    CHECK(set->writes(false));
    for(unsigned i=0;i<initialized;++i)for(unsigned j=0;j<64;++j)CHECK(stackBottom[i][j]==0xa5);
    return 0;
}
