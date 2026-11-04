// Included by the existing model guest after its allocator/scheduler definitions.
#include "native_app_file_boot_v3.h"
struct Input {const uint8_t *bytes;uint32_t size;};
struct CollectionModel {
    Input packages[2],manifest;uint32_t cursor,limit,opens=0,closes=0,position=0;
    Input *file=nullptr;bool worker=true;
    uint8_t journalBytes[2][320]{};Input journals[2]{};
};
static void exportResult(const CollectionModel &model,Ap01NativeAppFileBootV3 &boot,uint64_t bootId){
#ifdef AP01_MODEL_HTTP_SNAPSHOT
    auto *out=(uint8_t *)0xa81ff000;
    for(unsigned i=0;i<2;++i){
        for(unsigned j=0;j<4;++j)out[4*i+j]=uint8_t(model.journals[i].size>>(8*j));
        memcpy(out+8+320*i,model.journalBytes[i],320);
    }
    // Test-only portable snapshot, captured at the same point as the journals.
    out=(uint8_t *)0xa81ff300;memset(out,0,912);memcpy(out,"ARV3",4);
    auto put=[&](unsigned at,uint64_t value,unsigned n=4){for(unsigned i=0;i<n;++i)out[at+i]=uint8_t(value>>(8*i));};
    auto runtime=boot.runtime();const auto *m=runtime.manifest;
    put(4,1);put(8,bootId,8);put(16,m?m->sequence:0,8);put(24,m?m->count:0);
    put(28,runtime.started);put(32,runtime.complete);put(36,unsigned(runtime.health.state));
    put(40,unsigned(runtime.health.fault));put(44,runtime.health.sampled_at);
    if(m){memcpy(out+48,m->digest,32);for(unsigned i=0;i<m->count&&i<8;++i){
        unsigned at=80+104*i;memcpy(out+at,m->entries[i].id,32);memcpy(out+at+32,m->entries[i].version,32);
        memcpy(out+at+64,m->entries[i].digest,32);put(at+96,uint32_t(runtime.health.health[i]));put(at+100,m->order[i]);}}
#else
    (void)model;(void)boot;(void)bootId;
#endif
}
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
#ifdef AP01_MODEL_BOOT_ID
    constexpr uint64_t bootId=AP01_MODEL_BOOT_ID;
#elif defined(AP01_MODEL_MAINTENANCE)
    constexpr uint64_t bootId=44;
#elif defined(AP01_MODEL_ROLLBACK)
    constexpr uint64_t bootId=43;
#else
    constexpr uint64_t bootId=42;
#endif
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
    record.received[0]=bytes;record.received[1]=model.packages[1].size;
#ifdef AP01_MODEL_HTTP_SNAPSHOT
    const auto *saved=(const uint8_t *)0xa81ff000;
    for(unsigned i=0;i<2;++i){
        unsigned size=le32(saved+4*i);CHECK(size==0||size==320);
        memcpy(model.journalBytes[i],saved+8+320*i,size);
        model.journals[i]={model.journalBytes[i],size};
        if(size){Ap01SetRecordV3 decoded;CHECK(ap01DecodeSetRecordV3(model.journalBytes[i],decoded));
            if(decoded.sequence>=record.sequence)record=decoded;}
    }
#ifdef AP01_MODEL_MAINTENANCE
    CHECK(record.phase==Ap01SetPhaseV3::RecoveryRequired&&record.trialStarts==1&&record.rollbackStarts==1);
    CHECK(record.trialBoot&&record.rollbackBoot>record.trialBoot&&record.rollbackBoot<bootId);
#elif defined(AP01_MODEL_ROLLBACK)
    CHECK(record.phase==Ap01SetPhaseV3::RollbackPending&&record.trialStarts==1&&record.trialBoot&&record.trialBoot<bootId&&!record.rollbackStarts);
#ifdef AP01_MODEL_EMPTY_ROLLBACK
    uint8_t emptyDigest[32]{};CHECK(!record.oldVersion&&!memcmp(record.oldDigest,emptyDigest,32));
#else
    CHECK(!memcmp(record.oldDigest,manifest+32,32));
#endif
#else
    CHECK(record.phase==Ap01SetPhaseV3::SwitchPending);
    CHECK(!memcmp(record.newDigest,manifest+32,32));
#endif
#else
    CHECK(ap01EncodeSetRecordV3(record,model.journalBytes[0]));
    CHECK(le32(model.journalBytes[0]+4)==2);
    CHECK(le32(model.journalBytes[0]+268)==bytes&&le32(model.journalBytes[0]+272)==model.packages[1].size);
    model.journals[0]={model.journalBytes[0],320};model.journals[1]={model.journalBytes[1],0};
#endif
    Ap01SetJournalV3 journal(io,record.mac);CHECK(journal.load()==Ap01SetJournalResultV3::Ok);
    CHECK(journal.current()->sequence==record.sequence&&journal.current()->phase==record.phase);
#ifdef AP01_MODEL_ROLLBACK
    constexpr auto selectedMode=Ap01SetBootModeV3::Rollback;
    constexpr auto startedPhase=Ap01SetPhaseV3::RollbackStarted;
    constexpr auto finalPhase=Ap01SetPhaseV3::FailedRolledBack;
    const auto expectedVersion=record.oldVersion;const auto *expectedDigest=record.oldDigest;
#else
    constexpr auto selectedMode=Ap01SetBootModeV3::Trial;
    constexpr auto startedPhase=Ap01SetPhaseV3::TrialStarted;
    constexpr auto finalPhase=Ap01SetPhaseV3::Succeeded;
    const auto expectedVersion=record.newVersion;const auto *expectedDigest=record.newDigest;
#endif
    Ap01SetSelectorV3 selector(journal,bootId);
    auto *boot=new Ap01NativeAppFileBootV3(bootId,io,{&model,nullptr,reserveSet,publish},limits,1u<<22);
    CHECK(boot);auto *set=&boot->set();
    CHECK(set->shared().bindWindow((void *)1,ap01ModelStockV3));
    CHECK(boot->stageSelected(selector).mode==Ap01SetBootModeV3::Maintenance&&!ap01ModelV3.taskCount);
    CHECK(set->shared().startMaintenance());
#ifdef AP01_MODEL_MAINTENANCE
    CHECK(boot->stageSelected(selector).mode==Ap01SetBootModeV3::Maintenance);
    CHECK(journal.current()->phase==Ap01SetPhaseV3::RecoveryRequired&&journal.current()->sequence==record.sequence);
    for(unsigned i=0;i<5;++i){
        Ap01NativeAppSharedV3::poll(&set->shared());
        CHECK(boot->stageSelected(selector).mode==Ap01SetBootModeV3::Maintenance);
    }
    CHECK(!ap01ModelV3.taskCount&&!ap01ModelV3.mounts&&model.cursor==base);
    CHECK(set->shared().listening()&&ap01ModelV3.maintenanceStarts==1);
    CHECK(set->writesDrained()&&journal.load()==Ap01SetJournalResultV3::Ok);
    CHECK(journal.current()->sequence==record.sequence&&journal.current()->phase==Ap01SetPhaseV3::RecoveryRequired);
    CHECK(!memcmp(model.journalBytes[0],saved+8,320)&&!memcmp(model.journalBytes[1],saved+328,320));
    exportResult(model,*boot,bootId);return 0;
#endif
    CHECK(boot->stageSelected(selector).mode==selectedMode);
    CHECK(journal.current()->phase==startedPhase);
#ifdef AP01_MODEL_EMPTY_ROLLBACK
    CHECK(!model.file&&model.opens==model.closes&&model.cursor==base);
    Ap01SetHealthDecisionV3 emptyDecision=Ap01SetHealthDecisionV3::Waiting;
    for(unsigned i=0;i<400&&emptyDecision==Ap01SetHealthDecisionV3::Waiting;++i){
        ap01ModelV3.now+=100;Ap01NativeAppSharedV3::poll(&set->shared());
        boot->monitor(uint32_t(ap01ModelV3.now));emptyDecision=boot->healthSelected(selector,uint32_t(ap01ModelV3.now));
    }
    CHECK(emptyDecision==Ap01SetHealthDecisionV3::Approved);
    CHECK(journal.current()->phase==Ap01SetPhaseV3::FailedRolledBack&&journal.current()->cleanupPending);
    CHECK(journal.current()->trialStarts==1&&journal.current()->rollbackStarts==1);
    auto emptyRunning=boot->runtime();
    CHECK(emptyRunning.complete&&!emptyRunning.started&&emptyRunning.manifest&&!emptyRunning.manifest->count);
    CHECK(!emptyRunning.manifest->sequence&&!memcmp(emptyRunning.manifest->digest,emptyDigest,32));
    CHECK(emptyRunning.health.state==Ap01SupervisorStateV3::Healthy&&!emptyRunning.health.count);
    CHECK(!ap01ModelV3.taskCount&&!ap01ModelV3.mounts&&model.cursor==base&&ap01ModelV3.maintenanceStarts==1);
    CHECK(journal.load()==Ap01SetJournalResultV3::Ok&&journal.current()->phase==Ap01SetPhaseV3::FailedRolledBack);
    exportResult(model,*boot,bootId);return 0;
#endif
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
#ifdef AP01_MODEL_FAIL_WORKER
    // Stop an actual worker before health acceptance; UI and peers run.
    CHECK(schedule(0,200)==0);boot->monitor(uint32_t(ap01ModelV3.now));
    CHECK(boot->status().fault==Ap01SupervisorFaultV3::AppFailed);
    model.worker=true;
#ifdef AP01_MODEL_ROLLBACK
    constexpr auto failedDecision=Ap01SetHealthDecisionV3::Maintenance;
    constexpr auto failedPhase=Ap01SetPhaseV3::RecoveryRequired;
    constexpr unsigned rollbackStarts=1;
#else
    constexpr auto failedDecision=Ap01SetHealthDecisionV3::Reboot;
    constexpr auto failedPhase=Ap01SetPhaseV3::RollbackPending;
    constexpr unsigned rollbackStarts=0;
#endif
    CHECK(boot->healthSelected(selector,uint32_t(ap01ModelV3.now))==failedDecision);
    CHECK(journal.current()->phase==failedPhase);
    CHECK(journal.current()->trialStarts==1&&journal.current()->rollbackStarts==rollbackStarts&&set->writesDrained());
    CHECK(ap01ModelV3.mkdirCalls==0&&journal.load()==Ap01SetJournalResultV3::Ok);
    CHECK(journal.current()->phase==failedPhase);
    exportResult(model,*boot,bootId);
    for(unsigned i=0;i<initialized;++i)for(unsigned j=0;j<64;++j)CHECK(stackBottom[i][j]==0xa5);
    return 0;
#endif
    ap01ModelV3.allowMkdir=true;
    Ap01SetHealthDecisionV3 decision=Ap01SetHealthDecisionV3::Waiting;
    for(unsigned i=0;i<400&&decision==Ap01SetHealthDecisionV3::Waiting;++i){
        CHECK(schedule(3,1)==0);boot->monitor(uint32_t(ap01ModelV3.now));
        model.worker=true;decision=boot->healthSelected(selector,uint32_t(ap01ModelV3.now));model.worker=false;
        if(decision==Ap01SetHealthDecisionV3::Waiting)CHECK(set->writesDrained());
    }
    CHECK(decision==Ap01SetHealthDecisionV3::Approved);
    CHECK(journal.current()->phase==finalPhase&&journal.current()->cleanupPending);
    CHECK(schedule(3,20)==0&&ap01ModelV3.mkdirCalls==1);
    model.worker=true;CHECK(journal.load()==Ap01SetJournalResultV3::Ok);
    CHECK(journal.current()->phase==finalPhase);model.worker=false;
    CHECK(journal.current()->received[0]==record.received[0]&&journal.current()->received[1]==record.received[1]);
    auto running=boot->runtime();
    CHECK(running.complete&&running.started==2&&running.manifest);
    CHECK(running.manifest->sequence==expectedVersion&&!memcmp(running.manifest->digest,expectedDigest,32));
    CHECK(running.health.state==Ap01SupervisorStateV3::Healthy&&running.health.count==2);
    for(unsigned i=0;i<2;++i)CHECK(!memcmp(running.manifest->entries[i].digest,model.packages[i].bytes+192,32));
    exportResult(model,*boot,bootId);
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
