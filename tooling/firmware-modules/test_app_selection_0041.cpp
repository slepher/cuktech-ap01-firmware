#include "app_selection_0041.h"
#include "native_integrity_0041.h"
#include "test_app_file_store_0041.h"
#include <string>
#include <vector>
#include <fstream>
#include <iterator>
void healthy(Ap01AppSelection0041 &selector,const Ap01AppSelection &launch) {
    for(unsigned tick=0;tick<=30;++tick){
        assert(!selector.businessWritesAllowed(launch.generation));
        Ap01AppHealthSample sample{true,true,tick,tick,tick};
        assert(selector.observe(launch.generation,launch.digest,uint64_t(tick)*1000,sample)==Ap01AppSelectionResult::Waiting);
    }
    assert(selector.businessWritesAllowed(launch.generation));
    assert(!selector.businessWritesAllowed(launch.generation+1));
}
int main(int argc,char **argv){
    assert(argc==3);std::ifstream in(argv[2],std::ios::binary);
    std::vector<uint8_t> newer{std::istreambuf_iterator<char>(in),{}};assert(newer.size()==320);
    auto old=newer;old[160]='0';memset(old.data()+192,0,32);syncSha256(old.data(),old.size(),old.data()+192);
    uint8_t mac[6]={1,2,3,4,5,6};Apx2Limits limits{4096,4096,1024,1024,2,UINT64_MAX,nullptr};
    using R=Ap01AppSelectionResult;using P=Ap01AppUpdatePhase;using J=Ap01AppJournalResult;
    for(unsigned scenario=0;scenario<15;++scenario){
        std::string root=std::string(argv[1])+"/case"+std::to_string(scenario);assert(!mkdir(root.c_str(),0700));
        Disk disk;auto io=disk.ops();LittleFSClass fs(io,root.c_str());
        bool first=scenario==3;
        {File f=fs.open("/app-incoming.apx2","w");assert(f.write(newer.data(),newer.size())==newer.size());}
        if(!first){File f=fs.open("/app-current.apx2","w");assert(f.write(old.data(),old.size())==old.size());}
        Ap01AppUpdateJournal0041 journal(fs,mac);assert(journal.load()==J::Empty);
        Ap01AppUpdateRecord record;memcpy(record.mac,mac,6);record.transaction[0]=1;
        strcpy(record.principal,"menu-maintenance");record.total=newer.size();memcpy(record.newDigest,newer.data()+192,32);
        if(!first)memcpy(record.oldDigest,old.data()+192,32);
        assert(journal.save(record)==J::Ok);record=*journal.current();record.received=record.total;record.phase=P::Ready;assert(journal.save(record)==J::Ok);
        Ap01AppSelection0041 selector(fs,journal,limits);Ap01AppSelection launch;
        assert(selector.select(1,launch)==(first?R::Recovery:R::Launch));assert(!launch.trial);
        assert(selector.businessWritesAllowed(1)==!first);
        assert(selector.commit()==R::Waiting);
        assert(!selector.businessWritesAllowed(1));
        uint64_t committed=journal.current()->sequence;
        assert(selector.commit()==R::Waiting&&journal.current()->sequence==committed);
        if(scenario==4){assert(fs.remove("/app-incoming.apx2"));}
        if(scenario==5){disk.loseJournalAck=true;assert(selector.select(2,launch)==R::Unknown&&!launch.path);disk.loseJournalAck=false;assert(journal.load()==J::Ok);}
        assert(selector.select(2,launch)==R::Launch);
        if(scenario==4||scenario==5){
            assert(launch.rollback&&!launch.trial&&journal.current()->rollbackStarts==1);
            assert(selector.select(3,launch)==R::Recovery);continue;
        }
        assert(launch.trial&&journal.current()->trialStarts==1);
        assert(selector.observe(99,launch.digest,0,{})==R::Invalid);
        if(scenario>=7){
            Ap01AppHealthSample sample{true,true,1,1,1};
            if(scenario==7){
                sample.entryReady=false;
                assert(selector.observe(2,launch.digest,10001,sample)==R::Failed);
            }else if(scenario>=8&&scenario<=10){
                for(unsigned tick=0;tick<=40;++tick){
                    sample.events=scenario==8?0:tick;
                    sample.stockScheduler=scenario==9?0:tick;
                    sample.maintenance=scenario==10?0:tick;
                    assert(selector.observe(2,launch.digest,tick*1000,sample)==R::Waiting);
                    assert(journal.current()->phase==P::TrialStarted);
                }
                assert(selector.observe(2,launch.digest,40001,sample)==R::Failed);
            }else if(scenario==11){
                assert(selector.observe(2,launch.digest,1000,sample)==R::Waiting);
                assert(selector.observe(2,launch.digest,999,sample)==R::Failed);
            }else if(scenario==12){
                sample.resourcesOkay=false;
                assert(selector.observe(2,launch.digest,0,sample)==R::Failed);
            }else if(scenario==13){
                for(unsigned tick=0;tick<=20;++tick){
                    sample.events=sample.stockScheduler=sample.maintenance=tick;
                    assert(selector.observe(2,launch.digest,tick*2000,sample)==R::Waiting);
                    assert(journal.current()->phase==P::TrialStarted);
                }
                assert(selector.observe(2,launch.digest,40001,sample)==R::Failed);
            }else {
                uint8_t wrong[32]={9};assert(selector.observe(2,wrong,0,sample)==R::Invalid);
                healthy(selector,launch);assert(journal.current()->phase==P::Succeeded);continue;
            }
            // Failure is sticky, never repaired by a later healthy sample.
            assert(selector.observe(2,launch.digest,50000,{true,true,99,99,99})==R::Failed);
            assert(journal.current()->phase==P::TrialStarted);
            assert(selector.select(3,launch,50000)==R::Launch&&launch.rollback);
            continue;
        }
        if(scenario==0||scenario==6){
            healthy(selector,launch);assert(journal.current()->phase==P::Succeeded);
            disk.failRemove=true;assert(selector.cleanup()==R::Storage&&journal.current()->cleanupPending);
            disk.failRemove=false;disk.loseRename=true;assert(selector.cleanup()==R::Storage);
            disk.loseRename=false;assert(journal.load()==J::Ok);
            assert(selector.select(3,launch)==R::Launch&&!launch.trial&&!launch.rollback);
            assert(!memcmp(launch.digest,newer.data()+192,32));
            assert(selector.cleanup()==R::Waiting&&!journal.current()->cleanupPending);
            assert(fs.inspect("/app-incoming.apx2")==0&&fs.inspect("/app-current.apx2")==1);
            if(scenario==6){assert(fs.remove("/app-current.apx2"));assert(selector.select(4,launch)==R::Recovery);}
        }else{
            assert(journal.load()==J::Ok); // Reboot after trial start, before success.
            auto result=selector.select(3,launch);
            if(first){assert(result==R::Recovery);continue;}
            assert(result==R::Launch&&launch.rollback&&!launch.trial);
            assert(journal.current()->trialStarts==1&&journal.current()->rollbackStarts==1);
            if(scenario==1){
                healthy(selector,launch);
                assert(journal.current()->phase==P::FailedRolledBack);
                assert(selector.cleanup()==R::Waiting);
                assert(selector.select(4,launch)==R::Launch&&!launch.rollback);
                assert(!memcmp(launch.digest,old.data()+192,32));
            }else assert(selector.select(4,launch)==R::Recovery);
        }
    }
    for(unsigned scenario=0;scenario<7;++scenario){
        std::string root=std::string(argv[1])+"/cancel"+std::to_string(scenario);assert(!mkdir(root.c_str(),0700));
        Disk disk;auto io=disk.ops();LittleFSClass fs(io,root.c_str());
        bool first=scenario==4;
        {File f=fs.open("/app-incoming.apx2","w");assert(f.write(newer.data(),newer.size())==newer.size());}
        if(!first){File f=fs.open("/app-current.apx2","w");assert(f.write(old.data(),old.size())==old.size());}
        Ap01AppUpdateJournal0041 journal(fs,mac);assert(journal.load()==J::Empty);
        Ap01AppUpdateRecord record;memcpy(record.mac,mac,6);record.transaction[0]=1;
        strcpy(record.principal,"menu-maintenance");record.total=newer.size();memcpy(record.newDigest,newer.data()+192,32);
        if(!first)memcpy(record.oldDigest,old.data()+192,32);
        assert(journal.save(record)==J::Ok);
        if(scenario){record=*journal.current();record.received=record.total;record.phase=P::Ready;assert(journal.save(record)==J::Ok);}
        Ap01AppSelection0041 selector(fs,journal,limits);Ap01AppSelection launch;
        if(scenario>=2&&scenario<=5){
            assert(selector.commit()==R::Waiting);
            if(scenario>=3){assert(selector.select(2,launch)==R::Launch);if(scenario==5)healthy(selector,launch);}
        }
        if(scenario==6)disk.loseJournalAck=true;
        auto cancelled=selector.cancel();
        if(scenario==6){
            assert(cancelled==R::Unknown);disk.loseJournalAck=false;
            assert(selector.cleanup()==R::Unknown);assert(journal.load()==J::Ok);
            cancelled=selector.cancel();
        }
        assert(cancelled==(first?R::Recovery:R::Waiting));
        uint64_t sequence=journal.current()->sequence;assert(selector.cancel()==R::Waiting&&journal.current()->sequence==sequence);
        if(scenario<=1||scenario==6){
            assert(journal.current()->phase==P::Cancelled&&journal.current()->cleanupPending);
            auto another=record;another.transaction[0]=2;another.phase=P::Receiving;another.received=0;
            assert(journal.save(another)==J::Invalid); // Cleanup must finish first.
            disk.failRemove=true;assert(selector.cleanup()==R::Storage);disk.failRemove=false;
            assert(selector.cleanup()==R::Waiting);
            assert(fs.inspect("/app-current.apx2")==1&&fs.inspect("/app-incoming.apx2")==0);
            assert(selector.select(3,launch)==R::Launch&&!memcmp(launch.digest,old.data()+192,32));
            assert(journal.save(another)==J::Ok);
        }else if(first){
            assert(journal.current()->phase==P::RecoveryRequired&&journal.current()->cleanupPending);
            assert(selector.cleanup()==R::Waiting&&fs.inspect("/app-incoming.apx2")==0);
            auto retry=record;retry.transaction[0]=2;retry.phase=P::Receiving;retry.received=0;
            assert(journal.save(retry)==J::Ok); // Recovery remains installable without an old App.
        }
        else if(scenario==5){assert(journal.current()->phase==P::Succeeded&&fs.inspect("/app-incoming.apx2")==1);}
        else {
            assert(journal.current()->phase==P::RollbackPending);
            assert(selector.select(3,launch)==R::Launch&&launch.rollback);
            sequence=journal.current()->sequence;assert(selector.cancel()==R::Waiting&&journal.current()->sequence==sequence);
        }
    }
    puts("selection: durable trial/rollback, health deadlines/faults, write gating, cleanup replay, seven cancellation/replay scenarios passed");
}
