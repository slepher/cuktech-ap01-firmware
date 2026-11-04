#include "app_set_commit_v3.h"
#include <string.h>
using R=Ap01SetCommitResultV3;using P=Ap01SetPhaseV3;
R Ap01SetCommitV3::commit(const uint8_t transaction[16],const uint8_t expectedCurrent[32],uint64_t expectedVersion,
    const Ap01ManifestV3 &manifest,const Ap01ManifestPackagesV3 &packages,uint32_t now){
    if(!journal.writable())return R::Unknown;
    const auto *r=journal.current();
    if(!r||!transaction||!expectedCurrent||memcmp(transaction,r->transaction,16)||
        memcmp(expectedCurrent,r->oldDigest,32)||expectedVersion!=r->oldVersion||
        memcmp(manifest.digest,r->newDigest,32)||manifest.sequence!=r->newVersion)return R::Conflict;
    if(r->phase!=P::Receiving&&r->phase!=P::Ready&&r->phase!=P::SwitchPending)return R::State;
    if(expired)return R::DrainTimeout;
    if(r->phase!=P::SwitchPending){
        if(manifest.count>8||r->readyMask!=r->changedMask||(unsigned(r->changedMask)>>manifest.count))return R::NotReady;
        uint64_t total=0;
        for(unsigned i=0;i<manifest.count;++i)if(r->changedMask&(1u<<i)){
            if(r->received[i]!=manifest.entries[i].package_bytes)return R::NotReady;
            total+=manifest.entries[i].package_bytes;
        }
        if(total!=r->changedBytes)return R::Conflict;
        // Validate unchanged packages too: Ready bits alone cannot authorize a set.
        if(ap01CheckManifestPackagesV3(manifest,packages)!=Ap01ManifestErrorV3::Ok)return R::Package;
    }
    if(draining&&uint32_t(now-drainAt)>=5000&&r->phase!=P::SwitchPending){expired=true;return R::DrainTimeout;}
    if(!draining){draining=true;drainAt=now;}
    if(!writes.hold(true)){
        if(uint32_t(now-drainAt)>=5000){expired=true;return R::DrainTimeout;}
        return R::Busy;
    }
    // No App writes can enter after this point. Unknown keeps admission closed.
    auto next=*r;
    if(next.phase==P::Receiving){
        next.phase=P::Ready;
        if(journal.save(next)!=Ap01SetJournalResultV3::Ok)return R::Unknown;
    }
    if(next.phase!=P::SwitchPending){
        next.phase=P::SwitchPending;
        if(journal.save(next)!=Ap01SetJournalResultV3::Ok)return R::Unknown;
    }
    reboot.request(now);
    return reboot.state(now)==Ap01RebootStateV3::Failed?R::RebootFailed:R::Pending;
}

R Ap01SetCommitV3::cancel(const uint8_t transaction[16],uint32_t now){
    if(!journal.writable())return R::Unknown;
    const auto *r=journal.current();
    if(!r||!transaction||memcmp(transaction,r->transaction,16))return R::Conflict;
    if(r->phase==P::Cancelled)return R::Cancelled;
    auto next=*r;
    if(r->phase==P::Receiving||r->phase==P::Ready||r->phase==P::SwitchPending){
        // Stop a pending callback before the uncertain write. Never resume it
        // automatically if cancel persistence is Unknown: reconcile first.
        if(!reboot.cancel())return R::RebootInFlight;
        next.phase=P::Cancelled;next.cleanupPending=1;
        return journal.save(next)==Ap01SetJournalResultV3::Ok?R::Cancelled:R::Unknown;
    }
    if(r->phase!=P::TrialStarted&&r->phase!=P::RollbackPending)return R::State;
    if(expired)return R::DrainTimeout;
    if(!draining){draining=true;drainAt=now;}
    if(r->phase!=P::RollbackPending&&uint32_t(now-drainAt)>=5000){expired=true;return R::DrainTimeout;}
    if(!writes.hold(true))return R::Busy;
    if(r->phase==P::TrialStarted){
        next.phase=P::RollbackPending;next.error=7;
        if(journal.save(next)!=Ap01SetJournalResultV3::Ok)return R::Unknown;
    }
    reboot.request(now);
    return reboot.state(now)==Ap01RebootStateV3::Failed?R::RebootFailed:R::Pending;
}
