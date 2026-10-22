#include "native_wifi_switch_0041.h"
#include <errno.h>
#include <new>
#include <string.h>
__attribute__((section(".ap01_wifi_switch_budget"),used))
const uint32_t Ap01WifiSwitch0041::budget[2]={sizeof(Ap01WifiSwitch0041),sizeof(Attempt)};
Ap01WifiSwitch0041::~Ap01WifiSwitch0041(){delete pending.exchange(nullptr);}
void Ap01WifiSwitch0041::finish(State result){
    if(active){memset(active.get(),0,sizeof(Attempt));active.reset();}
    journaled=false;phase.store(result,std::memory_order_release);
}
void Ap01WifiSwitch0041::begin(uint64_t now){
    if(!port.apply||!port.online||!port.journal||!port.recover)return;
    active.reset(new(std::nothrow) Attempt);if(!active)return;
    int result=port.recover(port.context,active->previous);
    if(result==-ENOENT){finish(Idle);return;}
    if(result){finish(RecoveryFailed);return;}
    journaled=true;rollback(now);
}
int Ap01WifiSwitch0041::request(const char *ssid,uint32_t now){
    if(!ssid||!ssid[0]||strlen(ssid)>32)return -EINVAL;
    State old=state();
    if(old==Unavailable||old==RecoveryFailed)return -EIO;
    if(busy()||!phase.compare_exchange_strong(old,Queued))return -EBUSY;
    Attempt *a=new(std::nothrow) Attempt;
    if(!a){phase.store(old,std::memory_order_release);return -ENOMEM;}
    submitted.store(now,std::memory_order_release);strcpy(a->ssid,ssid);pending.store(a,std::memory_order_release);return 0;
}
void Ap01WifiSwitch0041::rollback(uint64_t now){
    phase.store(Restoring,std::memory_order_release);
    if(port.apply(port.context,active->previous,journaled)){finish(RecoveryFailed);return;}
    if(journaled){
        if(port.journal(port.context,nullptr)){finish(RecoveryFailed);return;}
        journaled=false;
    }
    deadline=now+45000;
}
void Ap01WifiSwitch0041::tick(uint64_t now){
    State s=state();
    if(s==Queued){
        Attempt *a=pending.exchange(nullptr,std::memory_order_acq_rel);if(!a)return;
        active.reset(a);
        std::unique_ptr<Ap01WifiProfiles0041> list(new(std::nothrow) Ap01WifiProfiles0041);
        if(!list||ap01WifiProfilesRead0041(port.profiles,*list)){finish(Failed);return;}
        bool found=false,previous=false;
        for(unsigned i=0;i<list->count;++i){auto &row=list->profiles[i];
            if(row.current){active->previous=row;previous=true;}
            if(!strcmp(row.ssid,active->ssid)){active->target=row;found=true;}}
        if(!found||!previous){finish(Failed);return;}
        // Selecting the current configuration never reconnects or rewrites it.
        if(!strcmp(active->previous.ssid,active->ssid)){finish(Connected);return;}
        if(port.profiles.busy&&port.profiles.busy(port.profiles.context)){finish(Failed);return;}
        if(port.apply(port.context,active->target,false)){rollback(now);return;}
        deadline=now+45000;phase.store(Connecting,std::memory_order_release);return;
    }
    if(s==Connecting){
        if(port.online(port.context,active->target.ssid)){
            phase.store(Saving,std::memory_order_release);
            // Trial changes only RAM. Persist the old network before either key write.
            if(port.journal(port.context,&active->previous)){rollback(now);return;}
            journaled=true;
            if(port.apply(port.context,active->target,true)){rollback(now);return;}
            // Cleanup can be ambiguous: both target keys are verified now. Do
            // not start another two-key write after possibly removing the journal.
            if(port.journal(port.context,nullptr)){finish(RecoveryFailed);return;}
            finish(Connected);
        }else if(now>=deadline)rollback(now);
    }else if(s==Restoring){
        if(port.online(port.context,active->previous.ssid)){
            if(journaled&&port.journal(port.context,nullptr)){finish(RecoveryFailed);return;}
            finish(Failed);
        }else if(now>=deadline)finish(Failed);
    }
}
