// Included by the existing model guest after its allocator/scheduler definitions.
#include "native_app_file_boot_v3.h"
struct Input {const uint8_t *bytes;uint32_t size;};
struct CollectionModel {
    Input packages[2],manifest;uint32_t cursor,limit,opens=0,closes=0,position=0;
    Input *file=nullptr;bool worker=true;
    uint8_t journalBytes[2][320]{};Input journals[2]{};
};
static int openFile(void *p,const char *path,unsigned flags){
    auto &s=*(CollectionModel *)p;if(!s.worker||s.file)return -1;
    Input *chosen=nullptr;
    char manifestPath[112]="/resource/app-store/manifests/";const char *hex="0123456789abcdef";
    constexpr unsigned prefix=sizeof("/resource/app-store/manifests/")-1;
    for(unsigned i=0;i<32;++i){manifestPath[prefix+2*i]=hex[s.manifest.bytes[32+i]>>4];manifestPath[prefix+2*i+1]=hex[s.manifest.bytes[32+i]&15];}
    memcpy(manifestPath+prefix+64,".amf3",6);
    if(!strcmp(path,"/resource/app-store/update.0"))chosen=&s.journals[0];
    else if(!strcmp(path,"/resource/app-store/update.1"))chosen=&s.journals[1];
    else if(!strcmp(path,manifestPath))chosen=&s.manifest;
    else for(auto &v:s.packages){char name[112]="/resource/app-store/packages/";const char *hex="0123456789abcdef";
        for(unsigned i=0;i<32;++i){name[29+2*i]=hex[v.bytes[192+i]>>4];name[30+2*i]=hex[v.bytes[192+i]&15];}
        memcpy(name+93,".apx2",6);if(!strcmp(path,name))chosen=&v;}
    if(!chosen)return -1;
    if(flags){if(chosen!=&s.journals[0]&&chosen!=&s.journals[1])return -1;chosen->size=0;}
    else if(!chosen->size)return -1;
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
    io.exists=[](void *p,const char *path){auto &s=*(CollectionModel*)p;
        if(!strcmp(path,"/resource/app-store/update.0"))return int(s.journals[0].size!=0);
        if(!strcmp(path,"/resource/app-store/update.1"))return int(s.journals[1].size!=0);
        return 0;};
    io.write=[](void *p,int fd,const void *bytes,size_t size){auto &s=*(CollectionModel*)p;
        if(!s.worker||fd!=10||!s.file||size!=320)return -1;
        for(unsigned i=0;i<2;++i)if(s.file==&s.journals[i]){memcpy(s.journalBytes[i],bytes,size);s.file->size=320;return 320;}
        return -1;};
    Ap01SetRecordV3 record{};record.sequence=1;record.phase=Ap01SetPhaseV3::SwitchPending;
    record.newVersion=uint64_t(le32(manifest+16))|uint64_t(le32(manifest+20))<<32;
    memcpy(record.newDigest,manifest+32,32);record.mac[0]=1;record.transaction[0]=1;record.requestDigest[0]=1;
    strcpy(record.principal,"model-owner");record.changedMask=record.readyMask=3;record.changedBytes=bytes+model.packages[1].size;
    CHECK(ap01EncodeSetRecordV3(record,model.journalBytes[0]));
    model.journals[0]={model.journalBytes[0],320};model.journals[1]={model.journalBytes[1],0};
    Ap01SetJournalV3 journal(io,record.mac);CHECK(journal.load()==Ap01SetJournalResultV3::Ok);
    Ap01SetSelectorV3 selector(journal,42);
    auto *boot=new Ap01NativeAppFileBootV3(42,io,{&model,nullptr,reserveSet,publish},limits,1u<<22);
    CHECK(boot);auto *set=&boot->set();
    CHECK(set->shared().bindWindow((void *)1,ap01ModelStockV3));
    CHECK(boot->stageSelected(selector).mode==Ap01SetBootModeV3::Maintenance&&!ap01ModelV3.taskCount);
    CHECK(set->shared().startMaintenance());
    CHECK(boot->stageSelected(selector).mode==Ap01SetBootModeV3::Trial);
    CHECK(journal.current()->phase==Ap01SetPhaseV3::TrialStarted);
    CHECK(model.opens==model.closes&&!model.file&&!ap01ModelV3.taskCount);
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
    CHECK(ap01ModelV3.mkdirCalls==0&&set->writesDrained());
    ap01ModelV3.allowMkdir=true;
    Ap01SetHealthDecisionV3 decision=Ap01SetHealthDecisionV3::Waiting;
    for(unsigned i=0;i<400&&decision==Ap01SetHealthDecisionV3::Waiting;++i){
        CHECK(schedule(3,1)==0);boot->monitor(uint32_t(ap01ModelV3.now));
        model.worker=true;decision=boot->healthSelected(selector,uint32_t(ap01ModelV3.now));model.worker=false;
        if(decision==Ap01SetHealthDecisionV3::Waiting)CHECK(set->writesDrained());
    }
    CHECK(decision==Ap01SetHealthDecisionV3::Approved);
    CHECK(journal.current()->phase==Ap01SetPhaseV3::Succeeded&&journal.current()->cleanupPending);
    CHECK(schedule(3,20)==0&&ap01ModelV3.mkdirCalls==1);
    model.worker=true;CHECK(journal.load()==Ap01SetJournalResultV3::Ok);
    CHECK(journal.current()->phase==Ap01SetPhaseV3::Succeeded);model.worker=false;
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
    model.worker=true;
    CHECK(boot->healthSelected(selector,uint32_t(ap01ModelV3.now))==Ap01SetHealthDecisionV3::Maintenance);
    CHECK(set->writesDrained());model.worker=false;
    for(unsigned i=0;i<initialized;++i)for(unsigned j=0;j<64;++j)CHECK(stackBottom[i][j]==0xa5);
    return 0;
}
