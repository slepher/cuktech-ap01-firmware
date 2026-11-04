#include "app_set_selection_v3.h"
#include <string.h>
namespace {using P=Ap01SetPhaseV3;using M=Ap01SetBootModeV3;}
bool Ap01SetSelectorV3::persist(Ap01SetRecordV3 &r,P phase,uint32_t error){
    r.phase=phase;if(error&&!r.error)r.error=error;
    return journal.save(r)==Ap01SetJournalResultV3::Ok;
}
Ap01SetSelectionV3 Ap01SetSelectorV3::select(void *context,Check check){
    Ap01SetSelectionV3 out{};
    if(attempted)return out;
    attempted=true;
    if(!boot||!check||!journal.writable()||!journal.current())return out;
    auto r=*journal.current();bool candidate=false,rollback=false;
    switch(r.phase){
    case P::Receiving:case P::Ready:case P::Cancelled:case P::FailedRolledBack:break;
    case P::Succeeded:candidate=true;break;
    case P::SwitchPending:
        // New boot identity must not alias an already consumed execution.
        if(!check(context,r.newDigest,r.newVersion)){
            if(!persist(r,P::RollbackPending,1))return out;
            rollback=true;
        }else{
            r.trialStarts=1;r.trialBoot=boot;
            if(!persist(r,P::TrialStarted))return out;
            candidate=true;mode=M::Trial;
        }
        break;
    case P::TrialStarted:
        if(r.trialBoot==boot)return out;
        if(!persist(r,P::RollbackPending,2))return out;
        rollback=true;break;
    case P::RollbackPending:
        if(r.trialBoot==boot)return out;
        rollback=true;break;
    case P::RollbackStarted:
        if(r.rollbackBoot!=boot)persist(r,P::RecoveryRequired,3);
        return out;
    case P::RecoveryRequired:return out;
    }
    const uint8_t *digest=candidate?r.newDigest:r.oldDigest;
    uint64_t version=candidate?r.newVersion:r.oldVersion;
    // Trial was preflighted above. Empty initial collection requires no file.
    if(mode!=M::Trial&&version&&!check(context,digest,version)){
        // Stable-set failure cannot use a candidate implicitly.
        if(r.phase!=P::Succeeded&&r.phase!=P::FailedRolledBack&&r.phase!=P::Cancelled)
            persist(r,P::RecoveryRequired,4);
        return out;
    }
    if(rollback){
        r.rollbackStarts=1;r.rollbackBoot=boot;
        if(!persist(r,P::RollbackStarted))return out;
        mode=M::Rollback;
    }else if(mode!=M::Trial)mode=version?M::Stable:M::Empty;
    out.mode=mode;out.version=version;memcpy(out.digest,digest,32);authorized=true;return out;
}
bool Ap01SetSelectorV3::accept(){
    if(!authorized||!journal.current())return false;
    auto r=*journal.current();
    if(mode==M::Trial){
        if(r.phase!=P::TrialStarted||r.trialBoot!=boot)return false;
        r.cleanupPending=1;if(!persist(r,P::Succeeded))return false;
    }else if(mode==M::Rollback){
        if(r.phase!=P::RollbackStarted||r.rollbackBoot!=boot)return false;
        r.cleanupPending=1;if(!persist(r,P::FailedRolledBack))return false;
    }else return mode==M::Stable||mode==M::Empty;
    mode=M::Stable;return true;
}
bool Ap01SetSelectorV3::failed(uint32_t error){
    if(!authorized||!error||!journal.current())return false;
    authorized=false;auto r=*journal.current();
    if(mode==M::Trial&&r.phase==P::TrialStarted&&r.trialBoot==boot)
        return persist(r,P::RollbackPending,error);
    if(mode==M::Rollback&&r.phase==P::RollbackStarted&&r.rollbackBoot==boot)
        persist(r,P::RecoveryRequired,error);
    return false;
}
void Ap01SetSelectorV3::beginObservation(uint32_t now){
    if(observing||!authorized)return;
    observing=true;startedAt=lastObservation=now;
}
Ap01SetHealthDecisionV3 Ap01SetSelectorV3::observe(uint32_t now,bool healthy,bool fault){
    using D=Ap01SetHealthDecisionV3;
    if(!observing)return D::Maintenance;
    if(decision!=D::Waiting)return decision;
    uint32_t age=now-startedAt,gap=now-lastObservation;lastObservation=now;
    if(fault||age>40000||(!seenHealthy&&age>10000)){
        decision=failed(fault?5:6)?D::Reboot:D::Maintenance;return decision;
    }
    if(!healthy||gap>1000)continuous=false;
    if(healthy){
        seenHealthy=true;
        if(!continuous){continuous=true;healthyAt=now;}
        if(uint32_t(now-healthyAt)>=30000){
            decision=accept()?D::Approved:D::Maintenance;return decision;
        }
    }
    return D::Waiting;
}
