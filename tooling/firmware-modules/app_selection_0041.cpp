#include "app_selection_0041.h"
namespace {
using P=Ap01AppUpdatePhase;using R=Ap01AppSelectionResult;using J=Ap01AppJournalResult;
const char *const paths[]={"/app-current.apx2","/app-incoming.apx2","/app-previous.apx2"};
bool existsDigest(const uint8_t *d){for(unsigned i=0;i<32;++i)if(d[i])return true;return false;}
bool read(void *p,uint32_t at,uint8_t *out,uint32_t n){auto &f=*(File *)p;return f.seek(at)&&f.read(out,n)==n;}
R saveResult(J result){return result==J::Ok?R::Waiting:result==J::Unknown?R::Unknown:R::Invalid;}
}
const char *Ap01AppSelection0041::find(const uint8_t digest[32]) {
    if(!existsDigest(digest))return nullptr;
    for(const char *path:paths){
        File f=fs.open(path,"r");uint32_t n=0;if(!f||!f.length(n))continue;
        Apx2View view{};
        if(apx2Validate({&f,n,read},limits,view)==Apx2Error::Ok&&!memcmp(view.digest,digest,32))return path;
    }return nullptr;
}
R Ap01AppSelection0041::commit(){
    if(!journal.resolved())return R::Unknown;
    const auto *r=journal.current();if(!r||r->phase==P::Receiving)return R::Invalid;
    if(r->phase!=P::Ready)return R::Waiting; // Replay reports the original state.
    auto next=*r;next.phase=P::SwitchPending;return saveResult(journal.save(next));
}
R Ap01AppSelection0041::recover(bool old){
    auto next=*journal.current();next.generation=0;next.cleanupPending=old?0:1;
    next.phase=old?P::RollbackPending:P::RecoveryRequired;
    R saved=saveResult(journal.save(next));return saved==R::Waiting&&!old?R::Recovery:saved;
}
R Ap01AppSelection0041::cancel(){
    if(!journal.resolved())return R::Unknown;
    const auto *r=journal.current();if(!r)return R::Invalid;
    if(r->phase==P::Receiving||r->phase==P::Ready){
        auto next=*r;next.phase=P::Cancelled;next.cleanupPending=1;
        return saveResult(journal.save(next));
    }
    if(r->phase==P::SwitchPending||r->phase==P::TrialStarted){
        observing=selectedGeneration=0;
        return recover(existsDigest(r->oldDigest));
    }
    return R::Waiting; // Repeat, rollback already pending/running, or final result.
}
R Ap01AppSelection0041::select(uint32_t generation,Ap01AppSelection &out,uint64_t now){
    out={};observing=selectedGeneration=0;if(!generation)return R::Invalid;
    if(!journal.resolved())return R::Unknown;
    const auto *r=journal.current();if(!r)return R::Recovery;
    if(r->phase==P::RecoveryRequired)return R::Recovery;
    if(r->phase==P::TrialStarted){
        R result=recover(existsDigest(r->oldDigest));if(result!=R::Waiting)return result;
    }else if(r->phase==P::RollbackStarted)return recover(false);
    r=journal.current();
    if(r->phase==P::SwitchPending&&!find(r->newDigest)){
        R result=recover(existsDigest(r->oldDigest));if(result!=R::Waiting)return result;
    }
    r=journal.current();bool trial=r->phase==P::SwitchPending,rollback=r->phase==P::RollbackPending;
    bool currentNew=trial||r->phase==P::Succeeded;
    const uint8_t *digest=currentNew?r->newDigest:r->oldDigest;
    const char *path=find(digest);
    if(!path){
        // A successful transaction must never silently choose its old package.
        if(rollback)return recover(false);
        return R::Recovery;
    }
    if(trial||rollback){
        auto next=*r;next.generation=generation;
        if(trial){next.phase=P::TrialStarted;next.trialStarts=1;}
        else {next.phase=P::RollbackStarted;next.rollbackStarts=1;}
        R result=saveResult(journal.save(next));if(result!=R::Waiting)return result;
    }
    out.path=path;out.generation=generation;out.trial=trial;out.rollback=rollback;
    memcpy(out.digest,digest,32);
    selectedGeneration=generation;
    if(trial||rollback){
        observing=generation;startedAt=lastAt=now;healthyAt=0;
        entrySeen=sampled=continuous=failed=false;last={};
    }
    return R::Launch;
}
R Ap01AppSelection0041::observe(uint32_t generation,const uint8_t digest[32],
                               uint64_t now,const Ap01AppHealthSample &sample){
    if(!journal.resolved())return R::Unknown;
    const auto *r=journal.current();
    if(!r||!observing||generation!=observing||r->generation!=generation||
       (r->phase!=P::TrialStarted&&r->phase!=P::RollbackStarted)||
       memcmp(digest,r->phase==P::TrialStarted?r->newDigest:r->oldDigest,32))return R::Invalid;
    if(failed)return R::Failed;
    if(now<lastAt||!sample.resourcesOkay||
       (!entrySeen&&now-startedAt>startTimeoutMs)||
       now-startedAt>startTimeoutMs+healthyMs||
       (entrySeen&&!sample.entryReady)) {failed=true;return R::Failed;}
    if(sampled&&now==lastAt)return R::Waiting;
    bool progress=sampled&&now-lastAt<=sampleGapMs&&sample.events!=last.events&&
                  sample.stockScheduler!=last.stockScheduler&&sample.maintenance!=last.maintenance;
    if(sample.entryReady){
        if(!entrySeen){healthyAt=now;continuous=true;entrySeen=true;}
        else if(!progress)continuous=false;
        else if(!continuous){healthyAt=lastAt;continuous=true;}
    }
    last=sample;lastAt=now;sampled=true;
    if(entrySeen&&continuous&&now-healthyAt>=healthyMs){
        R result=confirm(generation,digest);
        if(result==R::Waiting)observing=0;
        return result;
    }
    return R::Waiting;
}
bool Ap01AppSelection0041::businessWritesAllowed(uint32_t generation) const {
    if(!generation||generation!=selectedGeneration||!journal.resolved()||failed)return false;
    const auto *r=journal.current();if(!r)return false;
    return r->phase==P::Receiving||r->phase==P::Ready||r->phase==P::Cancelled||
           r->phase==P::Succeeded||r->phase==P::FailedRolledBack;
}
R Ap01AppSelection0041::confirm(uint32_t generation,const uint8_t digest[32]){
    if(!journal.resolved())return R::Unknown;
    const auto *r=journal.current();if(!r)return R::Invalid;
    bool trial=r->phase==P::TrialStarted,rollback=r->phase==P::RollbackStarted;
    if((!trial&&!rollback)||r->generation!=generation||memcmp(digest,trial?r->newDigest:r->oldDigest,32))return R::Invalid;
    auto next=*r;next.phase=trial?P::Succeeded:P::FailedRolledBack;
    // Always perform namespace reconciliation, including first installation.
    next.cleanupPending=1;return saveResult(journal.save(next));
}
R Ap01AppSelection0041::cleanup(){
    if(!journal.resolved())return R::Unknown;
    const auto *r=journal.current();if(!r||(r->phase!=P::Succeeded&&r->phase!=P::FailedRolledBack&&
       r->phase!=P::Cancelled&&r->phase!=P::RecoveryRequired))return R::Invalid;
    if(!r->cleanupPending)return R::Waiting;
    if(r->phase==P::Cancelled||r->phase==P::RecoveryRequired){
        // Only the incoming package belongs to this aborted download. Preserve
        // current/previous, even if they are missing or fail validation.
        if(find(r->oldDigest)==paths[1])return R::Storage;
        int present=fs.inspect(paths[1]);if(present<0||(present&&!fs.remove(paths[1])))return R::Storage;
        auto next=*r;next.cleanupPending=0;return saveResult(journal.save(next));
    }
    const uint8_t *digest=r->phase==P::Succeeded?r->newDigest:r->oldDigest;
    const char *selected=find(digest);if(!selected)return R::Recovery;
    // Success is already durable. Preserve selected bytes while removing old
    // roles; no package copy and no third complete package are created.
    for(const char *path:paths){
        if(path==selected)continue;
        int present=fs.inspect(path);if(present<0)return R::Storage;
        if(present&&!fs.remove(path))return R::Storage;
    }
    if(selected!=paths[0]&&!fs.rename(selected,paths[0]))return R::Storage;
    // Resolve lost rename replies by retrying cleanup and searching by digest.
    if(find(digest)!=paths[0])return R::Storage;
    auto next=*r;next.cleanupPending=0;return saveResult(journal.save(next));
}
