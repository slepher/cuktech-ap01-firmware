// Included by the existing model guest after its allocator/scheduler definitions.
#include "native_app_file_boot_v3.h"
#include "native_exec_memory_v3.h"
#include "native_rom_addresses.h"
#ifdef AP01_MODEL_BUSINESS_TEMPLATE
#include "business-bundle.h"
#endif
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
// Only the allocation address source is modeled. Production reserve/publish,
// including the 0041 cache instruction sequence, execute unchanged.
static CollectionModel *execModel=nullptr;
static void *allocateExec(size_t n){
    auto &s=*execModel;if(n>s.limit-s.cursor)return nullptr;
    void *p=(void *)s.cursor;s.cursor+=uint32_t(n);return p;
}
static void freeRejectedExec(void *){__builtin_trap();}
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
#ifdef AP01_MODEL_BUSINESS_RESUME
    const auto *saved=(const uint8_t *)0xa81d0000;
    auto saved32=[](const uint8_t *p){return uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16|uint32_t(p[3])<<24;};
    CHECK(!memcmp(saved,"BFV1",4)&&saved32(saved+4)>=32&&saved32(saved+4)<=0x1f000);
    unsigned savedAt=32;
    for(unsigned i=0;i<6;++i){uint32_t n=saved32(saved+8+4*i);if(n==UINT32_MAX)continue;
        auto &f=ap01ModelV3.files[i];f.capacity=i<2?512:i<4?262144:2048;
        CHECK(n<=f.capacity&&n<=saved32(saved+4)-savedAt);
        f.bytes.reset(new(std::nothrow) uint8_t[f.capacity]);CHECK(f.bytes);
        memcpy(f.bytes.get(),saved+savedAt,n);f.size=n;f.present=true;savedAt+=n;
    }
    CHECK(savedAt==saved32(saved+4)&&ap01ModelV3.files[1].present&&ap01ModelV3.files[3].present&&ap01ModelV3.files[5].present);
    ap01ModelV3.bundleDirectory=true;
    constexpr unsigned restoredMkdirs=0;
#else
    constexpr unsigned restoredMkdirs=1;
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
    execModel=&model;Ap01NativeExecMemoryV3 executable(0x80000,allocateExec,freeRejectedExec);
    auto *boot=new Ap01NativeAppFileBootV3(bootId,io,executable.port(),limits,1u<<22);
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
    CHECK(executable.retainedImages()==2&&executable.retainedBytes()==model.cursor-base);
    CHECK(ap01ModelV3.mounts==2&&ap01ModelV3.taskCount==2);
    CHECK(set->execution().health()==AP01_APP_V3_PENDING);
    ap01ModelV3.pause=pauseTask;
    for(unsigned round=0;round<12;++round){
        for(unsigned i=0;i<ap01ModelV3.taskCount;++i){
            if(i>=initialized){uint32_t stack=ap01ModelV3.tasks[i].stack;auto *p=(uint8_t *)malloc(stack);CHECK(p);memset(p,0xa5,stack);stackBottom[i]=p;workers[i].words[0]=uint32_t(uintptr_t(runTask));workers[i].words[1]=uint32_t(uintptr_t(p+stack));++initialized;}
            CHECK(!done[i]);current=i;ap01ModelV3.threadIdentity=i+2;modelSwitch(&scheduler,&workers[i]);
        }
        Ap01NativeAppSharedV3::poll(&set->shared());
    }
    CHECK(ap01ModelV3.taskCount==3&&set->execution().health()==AP01_APP_V3_OK);
    boot->monitor(uint32_t(ap01ModelV3.now));
    CHECK(boot->status().state==Ap01SupervisorStateV3::Healthy&&boot->status().count==2);
    CHECK(set->execution().event(1,nullptr,0)==AP01_APP_V3_OK);
    CHECK(ap01ModelV3.bridge.online(ap01ModelV3.bridge.context));
#ifndef AP01_MODEL_BUSINESS_RESUME
    // Empty business has no active content page; configured restore does.
    ap01ModelV3.activeChild=7;ap01ModelV3.eventCode=0x11;ap01ModelV3.eventKey=0x13;
    ap01ModelV3.window->event(ap01ModelV3.window->context,(void *)1);
    CHECK(ap01ModelV3.activeChild==AP01_STOCK_SCREEN_COUNT+8); // Native 7 -> peer after eight codex slots.
#endif
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
            for(unsigned i=0;i<3;++i)if(i!=skip){CHECK(!done[i]);current=i;ap01ModelV3.threadIdentity=i+2;modelSwitch(&scheduler,&workers[i]);}
            Ap01NativeAppSharedV3::poll(&set->shared());
        }return 0;
    };
    auto http=[&](bool mutation,const char *status,const char *error)->int{
        uint8_t input[320]{},output[4608]{};
        const char *headers=mutation?
            "POST /api/bundle/begin HTTP/1.1\r\nAuthorization: Bearer 0123456789abcdef0123456789abcdef\r\nContent-Length: 50\r\nContent-Type: application/vnd.codex-status.frame\r\n\r\n":
            "POST /api/status HTTP/1.1\r\nAuthorization: Bearer 0123456789abcdef0123456789abcdef\r\nContent-Length: 50\r\nContent-Type: application/vnd.codex-status.frame\r\n\r\n";
        unsigned n=strlen(headers);memcpy(input,headers,n);
        input[n]=0xc2;input[n+3]=mutation?10:1;input[n+7]=2;input[n+8]=1;input[n+31]=1;
        input[n+48]='{';input[n+49]='}';
        auto &wire=ap01ModelV3;unsigned closed=wire.httpCloses,mkdirs=wire.mkdirCalls;
        wire.httpInput=input;wire.httpLength=n+50;wire.httpRead=0;
        wire.httpOutput=output;wire.httpCapacity=sizeof(output)-1;wire.httpWritten=0;wire.httpQueued=true;
        for(unsigned i=0;i<30&&wire.httpCloses==closed;++i)CHECK(schedule(3,1)==0);
        CHECK(wire.httpCloses==closed+1&&!wire.httpActive&&!wire.httpQueued);
        CHECK(wire.httpRead==wire.httpLength&&wire.mkdirCalls==mkdirs);
        bool found=false;unsigned errorBytes=strlen(error);
        for(unsigned i=0;i+errorBytes<=wire.httpWritten;++i)if(!memcmp(output+i,error,errorBytes))found=true;
        CHECK(!strncmp((const char *)output,status,strlen(status))&&found);
        wire.httpInput=nullptr;wire.httpOutput=nullptr;return 0;
    };
    CHECK(ap01ModelV3.mkdirCalls==0&&set->writesDrained());
    CHECK(http(true,"HTTP/1.1 503 ","app_trial_readonly")==0);
    #ifdef AP01_MODEL_BUSINESS_RESUME
    CHECK(http(false,"HTTP/1.1 200 ",modelTemplateId)==0);
    CHECK(http(false,"HTTP/1.1 200 ","\"configured\":true")==0);
#else
    CHECK(http(false,"HTTP/1.1 401 ","unauthorized")==0);
#endif
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
#ifdef AP01_MODEL_BUSINESS_RESUME
    CHECK(ap01ModelV3.bindingWrites==0&&ap01ModelV3.bundleWrites==0);
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
    ap01ModelV3.busy=true;
    CHECK(schedule(3,20)==0&&ap01ModelV3.mkdirCalls==0);
    CHECK(set->execution().health()==AP01_APP_V3_OK);
    ap01ModelV3.busy=false;
    CHECK(schedule(3,20)==0&&ap01ModelV3.mkdirCalls==restoredMkdirs);
    CHECK(schedule(3,20)==0&&ap01ModelV3.mkdirCalls==restoredMkdirs);
    ap01ModelV3.busy=true;
    CHECK(http(true,"HTTP/1.1 503 ","maintenance_busy")==0);
    // Busy also takes business offline for status under the existing lifecycle policy.
    CHECK(http(false,"HTTP/1.1 503 ","business_offline")==0);
    ap01ModelV3.busy=false;
    #ifdef AP01_MODEL_BUSINESS_RESUME
    CHECK(http(false,"HTTP/1.1 200 ",modelTemplateId)==0);
    CHECK(http(false,"HTTP/1.1 200 ","\"configured\":true")==0);
#else
    CHECK(http(false,"HTTP/1.1 401 ","unauthorized")==0);
#endif
#if !defined(AP01_MODEL_HTTP_SNAPSHOT) && !defined(AP01_MODEL_BUSINESS_RESUME)
    CHECK(bootId==42&&ap01ModelV3.bridge.pairing&&ap01ModelV3.bridge.principal);
    const char pairingBody[]=R"({"device_mac":"AABBCCDDEEFF","bridge_id":"rv32-test","name":"worker-test","display_code":"1234","binding_token":"0123456789abcdef0123456789abcdef","request_id":"rv32-pair","boot_id":42,"pairing_revision":0})";
    Ap01HttpRequest pair{};pair.method="POST";pair.path="/api/pairing";pair.token="";
    pair.deviceToken="";pair.contentType="application/json";pair.body=(const uint8_t *)pairingBody;pair.length=sizeof(pairingBody)-1;
    auto &bridge=ap01ModelV3.bridge;
    CHECK(bridge.pairing(bridge.context,pair,ap01ModelV3.now).status==202);
    Ap01NativeAppSharedV3::poll(&set->shared());
    CHECK(ap01ModelV3.drawCallback);
    ap01ModelV3.drawCallback((void *)1); // Explicit modeled draw completion, not physical LVGL.
    ap01ModelV3.eventCode=1;ap01ModelV3.window->event(ap01ModelV3.window->context,(void *)1);
    ap01ModelV3.eventCode=0xb;ap01ModelV3.window->event(ap01ModelV3.window->context,(void *)1);
    ap01ModelV3.eventCode=0;
    CHECK(ap01ModelV3.bindingWrites==0&&ap01ModelV3.bindingRenames==0);
    char principal[65]{};
    CHECK(bridge.principal(bridge.context,"0123456789abcdef0123456789abcdef",principal)==401);
    ap01ModelV3.busy=true;CHECK(schedule(3,20)==0);
    CHECK(ap01ModelV3.bindingWrites==0&&ap01ModelV3.bindingRenames==0);
    ap01ModelV3.busy=false;CHECK(schedule(3,20)==0);
    pair.method="GET";pair.path="/api/pairing/rv32-pair";pair.token="0123456789abcdef0123456789abcdef";pair.length=0;
    auto pairResult=bridge.pairing(bridge.context,pair,ap01ModelV3.now);
    if(strstr(pairResult.bytes.c_str(),"pending_display"))return 1001;
    if(strstr(pairResult.bytes.c_str(),"awaiting_confirmation"))return 1002;
    if(strstr(pairResult.bytes.c_str(),"binding_storage"))return 1003;
    if(strstr(pairResult.bytes.c_str(),"owner_changed"))return 1004;
    CHECK(ap01ModelV3.bindingWrites>0&&ap01ModelV3.bindingRenames==1);
    CHECK(bridge.principal(bridge.context,"0123456789abcdef0123456789abcdef",principal)==200);
    CHECK(!strcmp(principal,"rv32-test")&&!memcmp(ap01ModelV3.files[1].bytes.get(),"APB1",4));
    CHECK(http(false,"HTTP/1.1 200 ","session_nonce")==0);
    CHECK(ap01ModelV3.bindingRenames==1);
    uint8_t session[16]={8};unsigned requestNo=0;char nonce[33]{},replyJson[4096]{};
    auto command=[&](unsigned op,const char *path,const char *payload,bool replay=false)->int{
        uint8_t input[2048]{},output[4608]{},saved[4608]{};unsigned payloadBytes=strlen(payload);
        int n=snprintf((char *)input,sizeof(input),"POST %s HTTP/1.1\r\nAuthorization: Bearer 0123456789abcdef0123456789abcdef\r\nX-Device-Token: 0123456789abcdef0123456789abcdef\r\nContent-Type: application/vnd.codex-status.frame\r\nContent-Length: %u\r\n\r\n",path,48+payloadBytes);
        CHECK(n>0&&unsigned(n)+48+payloadBytes<sizeof(input));
        auto *frame=input+n;frame[0]=0xc2;frame[3]=op;frame[6]=payloadBytes>>8;frame[7]=payloadBytes;
        memcpy(frame+8,session,16);frame[31]=++requestNo;memcpy(frame+48,payload,payloadBytes);
        unsigned savedBytes=0,writes=0,renames=0;
        for(unsigned attempt=0;attempt<(replay?2u:1u);++attempt){
            auto &wire=ap01ModelV3;unsigned closed=wire.httpCloses;
            memset(output,0,sizeof(output));wire.httpInput=input;wire.httpLength=n+48+payloadBytes;wire.httpRead=0;
            wire.httpOutput=output;wire.httpCapacity=sizeof(output)-1;wire.httpWritten=0;wire.httpQueued=true;
            for(unsigned i=0;i<60&&wire.httpCloses==closed;++i)CHECK(schedule(3,1)==0);
            CHECK(wire.httpCloses==closed+1&&wire.httpRead==wire.httpLength);
            if(strncmp((const char *)output,"HTTP/1.1 200 ",13))return 2000+op;
            char *body=strstr((char *)output,"\r\n\r\n");CHECK(body);body+=4;
            CHECK(uint8_t(body[0])==0xc2&&uint8_t(body[1])==1&&uint8_t(body[3])==op);
            unsigned bytes=(uint8_t(body[6])<<8)|uint8_t(body[7]);CHECK(bytes<sizeof(replyJson));
            CHECK(body+48+bytes==(char *)output+wire.httpWritten);
            memcpy(replyJson,body+48,bytes);replyJson[bytes]=0;memcpy(session,body+8,16);
            if(attempt){CHECK(wire.httpWritten==savedBytes&&!memcmp(saved,output,savedBytes));
                CHECK(wire.bundleWrites==writes&&wire.bundleRenames==renames);}
            else {savedBytes=wire.httpWritten;memcpy(saved,output,savedBytes);writes=wire.bundleWrites;renames=wire.bundleRenames;}
            wire.httpInput=nullptr;wire.httpOutput=nullptr;
        }return 0;
    };
    CHECK(command(1,"/api/status","{}")==0);
    const char *nonceAt=strstr(replyJson,"\"session_nonce\":\"");CHECK(nonceAt);memcpy(nonce,nonceAt+17,32);
    CHECK(command(4,"/claim",R"({"bridge_id":"rv32-test","device_mac":"AABBCCDDEEFF"})")==0);
#ifdef AP01_MODEL_BUSINESS_TEMPLATE
    const auto &bundle=modelBundle;const auto &envelope=modelEnvelope;
    const char *templateId=modelTemplateId;
#else
    const char *templateId="rv32-bundle";
    // Frozen minimal valid Bundle fixture; length/CRC in envelope cover exact UTF-8 bytes.
    const char bundle[]=R"BUNDLE({"job_id":"rv32-bundle","firmware_target":"cuktech-ap01-0041","render_target":"lcd-jd9853-320x240-palette4","compiler_abi":2,"profile":{"template_ids":["rv32-bundle"],"initial_active_id":"rv32-bundle"},"templates":[{"key":{"template_id":"rv32-bundle","render_target":"lcd-jd9853-320x240-palette4"},"source":{"schema":1,"id":"rv32-bundle","version":9,"min_fw":"1.0.2_0041","render_target":"lcd-jd9853-320x240-palette4","canvas":{"w":320,"h":240},"elements":[{"type":"rect","rect":[0,0,320,240],"fill":true,"color":"black"}]}}],"fonts":[]})BUNDLE";
    const char envelope[]=R"BUNDLE({"bridge_id":"rv32-test","device_mac":"AABBCCDDEEFF","request_id":"rv32-install","length":537,"content_crc":"85b15118"})BUNDLE";
#endif
    CHECK(command(10,"/api/bundle/begin",envelope)==0);
    for(unsigned at=0;at<sizeof(bundle)-1;){
        unsigned count=sizeof(bundle)-1-at;if(count>1024)count=1024;
        char chunk[1025]{},chunkPath[192];memcpy(chunk,bundle+at,count);
        snprintf(chunkPath,sizeof(chunkPath),"/api/bundle/chunk?request_id=rv32-install&offset=%u&session_nonce=%s",at,nonce);
        int result=command(11,chunkPath,chunk,true);if(result)return result;at+=count;
    }
    int committed=command(12,"/api/bundle/commit",envelope,true);if(committed)return committed;
    CHECK(ap01ModelV3.files[3].present&&ap01ModelV3.files[5].present&&!ap01ModelV3.files[2].present);
    CHECK(ap01ModelV3.files[3].size>sizeof(bundle)-1&&ap01ModelV3.files[5].size>0);
    CHECK(command(1,"/api/status","{}")==0);
    CHECK(strstr(replyJson,"\"configured\":true")&&strstr(replyJson,templateId));
#endif
#ifdef AP01_MODEL_BUSINESS_RESUME
    unsigned originalAt=32;
    for(unsigned i=0;i<6;++i){uint32_t n=saved32(saved+8+4*i);if(n==UINT32_MAX)continue;
        if(i==1||i==3){const auto &f=ap01ModelV3.files[i];CHECK(f.present&&f.size==n&&!memcmp(f.bytes.get(),saved+originalAt,n));}
        originalAt+=n;
    }
    CHECK(ap01ModelV3.bindingWrites==0&&ap01ModelV3.bindingRenames==0&&ap01ModelV3.bundleWrites>0);
#endif
#ifdef AP01_MODEL_BUSINESS_TEMPLATE
    // Portable test snapshot: six explicit lengths, then exact file bytes.
    auto *exported=(uint8_t *)0xa81d0000;memcpy(exported,"BFV1",4);
    auto put32=[](uint8_t *p,uint32_t value){for(unsigned i=0;i<4;++i)p[i]=uint8_t(value>>(8*i));};
    unsigned exportAt=32;
    for(unsigned i=0;i<6;++i){const auto &f=ap01ModelV3.files[i];put32(exported+8+4*i,f.present?f.size:UINT32_MAX);
        if(f.present){CHECK(f.size<=0x1f000-exportAt);memcpy(exported+exportAt,f.bytes.get(),f.size);exportAt+=f.size;}}
    put32(exported+4,exportAt);
#endif
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
