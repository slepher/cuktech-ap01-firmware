#include "app_supervision_v3.h"
namespace {
bool stale(uint32_t now,uint32_t beat,uint32_t limit){
    uint32_t age=now-beat;
    // A concurrent publisher can be newer than the worker's sampled clock.
    // Supported deadlines are below half the uint32 clock range.
    return age<0x80000000u&&age>limit;
}
}
void Ap01AppSupervisionV3::publish(uint32_t now,const int32_t *values,uint32_t count){
    if(count>AP01_MANIFEST_APPS_V3||(!values&&count))return;
    uint32_t word=count<<16;
    for(unsigned i=0;i<count;++i)word|=(values[i]<0?2u:values[i]==AP01_APP_V3_OK?0u:1u)<<(2*i);
    revision.fetch_add(1,std::memory_order_seq_cst);
    sampleWord.store(word,std::memory_order_seq_cst);sampleTime.store(now,std::memory_order_seq_cst);
    revision.fetch_add(1,std::memory_order_seq_cst);
}
bool Ap01AppSupervisionV3::sample(uint32_t &word,uint32_t &time)const{
    for(unsigned i=0;i<3;++i){uint32_t before=revision.load(std::memory_order_seq_cst);if(!before||(before&1))continue;
        word=sampleWord.load(std::memory_order_seq_cst);time=sampleTime.load(std::memory_order_seq_cst);
        if(before==revision.load(std::memory_order_seq_cst))return true;}
    return false;
}
void Ap01AppSupervisionV3::fail(Ap01SupervisorFaultV3 fault,uint32_t index){
    if(fault==Ap01SupervisorFaultV3::None)return;
    uint32_t old=status.load(std::memory_order_acquire);
    uint32_t next=uint32_t(Ap01SupervisorStateV3::Fault)|(uint32_t(fault)<<8)|((index&0xffff)<<16);
    while(((old&255)!=uint32_t(Ap01SupervisorStateV3::Fault)||
           (uiRecoveryAllowed.load(std::memory_order_acquire)&&((old>>8)&255)==uint32_t(Ap01SupervisorFaultV3::UiStale)&&fault!=Ap01SupervisorFaultV3::UiStale))&&
          !status.compare_exchange_weak(old,next,std::memory_order_acq_rel)){}
}
void Ap01AppSupervisionV3::tick(uint32_t now,int boot,bool listening,uint32_t maintenanceBeat,bool windowPresent){
    if(!begun){begun=true;startedAt=now;}
    uint32_t observed=status.load(std::memory_order_acquire);
    bool recovering=uiRecoveryAllowed.load(std::memory_order_acquire)&&
        (observed&255)==uint32_t(Ap01SupervisorStateV3::Fault)&&
        ((observed>>8)&255)==uint32_t(Ap01SupervisorFaultV3::UiStale);
    if((observed&255)==uint32_t(Ap01SupervisorStateV3::Fault)&&!recovering)return;
    if(boot<0){fail(Ap01SupervisorFaultV3::Boot);return;}
    if(listening)sawMaintenance=true;
    else if(sawMaintenance){fail(Ap01SupervisorFaultV3::MaintenanceStale);return;}
    if(listening&&stale(now,maintenanceBeat,10000)){fail(Ap01SupervisorFaultV3::MaintenanceStale);return;}
    if(!listening||!boot){if(uint32_t(now-startedAt)>=30000)fail(Ap01SupervisorFaultV3::StartupTimeout);return;}
    uint32_t old=status.load(std::memory_order_acquire),next=uint32_t(Ap01SupervisorStateV3::Starting);
    if(!windowPresent){pending=false;next=uint32_t(Ap01SupervisorStateV3::WindowAbsent);}
    else {
        uint32_t word=0,time=0;
        if(!sample(word,time)){
            // A preempted seqlock publisher is not proof of a stalled UI.
            // Retain the last coherent sample's deadline; retries never renew it.
            if(stale(now,haveUiSample?lastUiSampleAt:startedAt,5000))fail(Ap01SupervisorFaultV3::UiStale);
            return;
        }
        lastUiSampleAt=time;haveUiSample=true;
        if(stale(now,time,5000)){
            if(uint32_t(now-startedAt)>5000)fail(Ap01SupervisorFaultV3::UiStale);
            return;
        }
        uint32_t first=UINT32_MAX;
        for(unsigned i=0;i<(word>>16);++i){unsigned health=(word>>(2*i))&3;
            if(health==2){fail(Ap01SupervisorFaultV3::AppFailed,i);return;}
            if(health&&first==UINT32_MAX)first=i;}
        if(first!=UINT32_MAX){
            if(!pending){pending=true;pendingAt=now;}
            if(uint32_t(now-pendingAt)>=30000){fail(Ap01SupervisorFaultV3::AppTimeout,first);return;}
        }else {pending=false;next=uint32_t(Ap01SupervisorStateV3::Healthy);}
    }
    // A concurrent initialization failure must not be overwritten by a healthy observation.
    if((old&255)!=uint32_t(Ap01SupervisorStateV3::Fault)||
       (recovering&&old==observed&&next==uint32_t(Ap01SupervisorStateV3::Healthy)))
        status.compare_exchange_strong(old,next,std::memory_order_acq_rel);
}
Ap01SupervisorSnapshotV3 Ap01AppSupervisionV3::snapshot()const{
    uint32_t value=status.load(std::memory_order_acquire),word=0,time=0;
    Ap01SupervisorSnapshotV3 out{};out.state=Ap01SupervisorStateV3(value&255);
    out.fault=Ap01SupervisorFaultV3((value>>8)&255);out.app_index=out.fault==Ap01SupervisorFaultV3::None?UINT32_MAX:value>>16;
    if(out.app_index==0xffff)out.app_index=UINT32_MAX;
    if(sample(word,time)){out.count=word>>16;out.sampled_at=time;
        for(unsigned i=0;i<out.count;++i){unsigned h=(word>>(2*i))&3;out.health[i]=h==2?AP01_APP_V3_FAILED:h==1?AP01_APP_V3_PENDING:AP01_APP_V3_OK;}}
    return out;
}
