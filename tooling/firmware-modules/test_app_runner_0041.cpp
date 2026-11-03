#include "app_runner_0041.h"
#include "app_files_0041.h"
#include "native_integrity_0041.h"
#include "test_app_file_store_0041.h"
#include <fstream>
#include <iterator>
#include <vector>
struct Backend {
    std::vector<uint8_t> bytes;unsigned starts=0,releases=0,stops=0;
    bool failFirst=false,failAll=false,stopFail=false,eventFail=false;
    Ap01AppRunner0041 *runner=nullptr;
    Ap01AppFiles0041 *files=nullptr;
    bool permissionFail=false;
    bool canWrite(){
        auto s=files->table(runner->callbacks().current());
        ap01_app_file_request_v2 request{};request.argument=1;strcpy(request.path,"/probe");
        uint32_t handle=0,written=0;
        int result=s.invoke(s.context,s.generation,2,AP01_FILE_OPEN,&request,sizeof(request),&handle,4,&written);
        if(result){assert(result==AP01_FILE_READ_ONLY||result==AP01_SERVICE_UNAVAILABLE);return false;}
        assert(written==4);request={};request.handle=handle;
        assert(!s.invoke(s.context,s.generation,2,AP01_FILE_CLOSE,&request,sizeof(request),nullptr,0,&written));
        return true;
    }
    static bool permission(void *p,uint32_t gen,bool allow){auto &b=*(Backend *)p;
        return !b.permissionFail&&b.files->writes(gen,allow);
    }
    static bool drain(void *p){return ((Backend *)p)->files->drain();}
    static bool reserve(void *p,const Apx2View &v,Ap01AppMemory0041 &out){auto &b=*(Backend *)p;
        b.bytes.resize(v.image_bytes+v.bss_bytes);out={b.bytes.data(),uint32_t(b.bytes.size()),0x10000,&b};return true;}
    static int32_t invoke(void *,uint32_t,uint32_t,uint32_t,const void *,uint32_t,void *,uint32_t,uint32_t *){return -1;}
    static int32_t start(const ap01_app_services_v2 *s,void **out){auto &b=*(Backend *)s->context;++b.starts;*out=&b;
        assert(!b.canWrite()); // Every start, including restart of committed App.
        // Reentrant stop must not change the enclosing launch's decision.
        auto state=b.runner->status();assert(b.runner->stop(0)==state);
        return b.failAll||(b.failFirst&&b.starts==1)?-1:0;}
    static int32_t event(void *p,const ap01_app_event_v2 *){return ((Backend *)p)->eventFail?-1:0;}
    static int32_t prepare(void *){return 0;}
    static int32_t stop(void *p){auto &b=*(Backend *)p;++b.stops;return b.stopFail?-1:0;}
    static int32_t health(void *,ap01_app_health_v2 *out){out->entry_ready=1;return 0;}
    static bool publish(void *,const Ap01AppMemory0041 &,const Apx2View &,ap01_app_entries_v2 &out){out={start,event,prepare,stop,health};return true;}
    static void release(void *p,const Ap01AppMemory0041 &){auto &b=*(Backend *)p;assert(b.runner->callbacks().drained());++b.releases;b.bytes.clear();}
    Ap01AppImagePort0041 port(){return {this,reserve,publish,release,drain,permission};}
    ap01_app_services_v2 services(){return {2,sizeof(ap01_app_services_v2),0,0,UINT64_MAX,this,invoke};}
};
int main(int argc,char **argv){
    assert(argc==3);std::ifstream input(argv[2],std::ios::binary);
    std::vector<uint8_t> newer{std::istreambuf_iterator<char>(input),{}};assert(newer.size()==320);
    auto old=newer;old[160]='0';memset(old.data()+192,0,32);syncSha256(old.data(),old.size(),old.data()+192);
    uint8_t mac[6]={1,2,3,4,5,6};Apx2Limits limits{4096,4096,1024,1024,2,UINT64_MAX,nullptr};
    using S=Ap01AppRunState;using P=Ap01AppUpdatePhase;using J=Ap01AppJournalResult;using R=Ap01AppSelectionResult;
    ap01_app_event_v2 event{sizeof(event),1,0,0,nullptr,0};
    for(unsigned scenario=0;scenario<10;++scenario){
        std::string root=std::string(argv[1])+"/case"+std::to_string(scenario);assert(!mkdir(root.c_str(),0700));
        Disk disk;auto io=disk.ops();LittleFSClass fs(io,root.c_str());
        {File f=fs.open("/app-incoming.apx2","w");assert(f.write(newer.data(),newer.size())==newer.size());}
        {File f=fs.open("/app-current.apx2","w");assert(f.write(old.data(),old.size())==old.size());}
        Ap01AppUpdateJournal0041 journal(fs,mac);assert(journal.load()==J::Empty);
        Ap01AppUpdateRecord record;memcpy(record.mac,mac,6);record.transaction[0]=1;strcpy(record.principal,"menu");
        record.total=newer.size();memcpy(record.newDigest,newer.data()+192,32);memcpy(record.oldDigest,old.data()+192,32);
        assert(journal.save(record)==J::Ok);record=*journal.current();record.received=record.total;record.phase=P::Ready;assert(journal.save(record)==J::Ok);
        Ap01AppSelection0041 selection(fs,journal,limits);Backend backend;
        Ap01AppRunner0041 runner(fs,selection,limits,backend.port(),backend.services());backend.runner=&runner;
        std::string businessRoot=root+"/business";assert(!mkdir(businessRoot.c_str(),0700));
        Ap01AppFiles0041 files(runner.callbacks(),io,businessRoot.c_str());backend.files=&files;
        backend.failFirst=scenario==1;backend.failAll=scenario==2;
        if(scenario==9){
            assert(runner.launch(0)==S::Running&&backend.canWrite());
            backend.permissionFail=true;disk.loseJournalAck=true;
            assert(selection.commit()==R::Unknown);
            assert(runner.reconcile(1)==S::Recovery);
            assert(!backend.canWrite()&&!runner.businessWritesAllowed()&&backend.releases==1);
            continue;
        }
        if(scenario==7){
            assert(runner.launch(0)==S::Running&&runner.businessWritesAllowed());
            assert(runner.callbacks().acquire(1));assert(runner.stop(1)==S::Stopping);
            assert(journal.current()->phase==P::Ready&&backend.starts==1&&!backend.releases);
            runner.callbacks().release();assert(runner.stop(2)==S::Idle&&backend.releases==1);
        }
        assert(selection.commit()==R::Waiting);
        auto initial=runner.launch(0);assert(initial==(scenario==1||scenario==2?S::Stopping:S::Running));
        assert(!runner.businessWritesAllowed());assert(journal.current()->trialStarts==1);
        assert(!backend.canWrite());
        if(scenario==1||scenario==2){
            auto state=runner.tick(1,1,1);assert(state==(scenario==1?S::Running:S::Stopping));
            assert(journal.current()->rollbackStarts==1&&backend.releases==1);
            if(scenario==2){assert(runner.tick(2,2,2)==S::Recovery);assert(backend.releases==2&&backend.starts==2);continue;}
        }
        if(scenario==3||scenario==4){
            assert(runner.callbacks().acquire(1));backend.eventFail=true;
            assert(runner.event(1,event)==Ap01AppLifeResult::Fault);assert(runner.status()==S::Stopping&&!backend.releases);
            assert(runner.tick(2,2,2)==S::Stopping&&backend.starts==1);
            if(scenario==4){assert(runner.tick(5001,3,3)==S::RebootRequired);runner.callbacks().release();
                assert(runner.tick(5002,4,4)==S::RebootRequired&&!backend.releases&&backend.starts==1);continue;}
            runner.callbacks().release();backend.eventFail=false;assert(runner.tick(3,3,3)==S::Running);
            assert(backend.starts==2&&backend.releases==1&&journal.current()->rollbackStarts==1);
        }
        if(scenario==5){backend.stopFail=true;assert(runner.stop(1)==S::RebootRequired&&!backend.releases);continue;}
        uint64_t base=100;
        for(unsigned tick=0;tick<=30;++tick){
            assert(!backend.canWrite());
            assert(runner.event(base+tick*1000,event)==Ap01AppLifeResult::Ok);
            if(scenario==6&&tick==30)disk.loseJournalAck=true;
            if(scenario==8&&tick==30)backend.permissionFail=true;
            auto state=runner.tick(base+tick*1000,tick,tick);
            assert(state==(scenario==6&&tick==30?S::Unknown:scenario==8&&tick==30?S::Recovery:S::Running));
        }
        if(scenario==6){assert(!runner.businessWritesAllowed()&&backend.releases==1);continue;}
        if(scenario==8){assert(!runner.businessWritesAllowed()&&!backend.canWrite());
            assert(journal.current()->phase==P::Succeeded&&backend.releases==1);continue;}
        assert(runner.businessWritesAllowed());
        assert(backend.canWrite());
        assert(journal.current()->phase==(scenario==1||scenario==3?P::FailedRolledBack:P::Succeeded));
        assert(runner.stop(32000)==S::Idle);assert(!runner.running()&&!runner.businessWritesAllowed());
        assert(!backend.canWrite());
        assert(selection.cleanup()==R::Waiting);assert(runner.launch(33000)==S::Running);
        assert(runner.businessWritesAllowed());assert(runner.stop(34000)==S::Idle);
    }
    puts("runner: 10 scenarios; real file-service writes closed at start/trial/rollback/stop, enabled after durable success, grant/revoke failure stops App; partial-start rollback, callback drain/timeout, uncertain journal passed (host entries)");
}
