#include "native_wifi_switch_0041.h"
#include <errno.h>
#include <new>
#include <string.h>
__attribute__((section(".ap01_wifi_switch_budget"),used))
const uint32_t Ap01WifiSwitch0041::budget[2]={sizeof(Ap01WifiSwitch0041),sizeof(Attempt)};
Ap01WifiSwitch0041::~Ap01WifiSwitch0041(){delete pending.exchange(nullptr);}
void Ap01WifiSwitch0041::finish(State result){
    if(active){memset(active.get(),0,sizeof(Attempt));active.reset();}
    journaled=false;phase.store(result,std::memory_order_release);trace(Finished);
}
void Ap01WifiSwitch0041::begin(uint64_t now){
    if(!port.apply||!port.online||!port.journal||!port.recover)return;
    active.reset(new(std::nothrow) Attempt);if(!active)return;
    int result=port.recover(port.context,active->previous);trace(Recover,result);
    if(result==-ENOENT){finish(Idle);return;}
    if(result){finish(RecoveryFailed);return;}
    journaled=true;rollback(now);
}
int Ap01WifiSwitch0041::request(const char *ssid,uint32_t now){
    if(!ssid||!ssid[0]||strlen(ssid)>32){trace(Requested,-EINVAL);return -EINVAL;}
    State old=state();
    if(old==Unavailable||old==RecoveryFailed){trace(Requested,-EIO);return -EIO;}
    if(busy()||!phase.compare_exchange_strong(old,Queued)){trace(Requested,-EBUSY);return -EBUSY;}
    Attempt *a=new(std::nothrow) Attempt;
    if(!a){phase.store(old,std::memory_order_release);return -ENOMEM;}
    submitted.store(now,std::memory_order_release);strcpy(a->ssid,ssid);pending.store(a,std::memory_order_release);trace(Requested);return 0;
}
void Ap01WifiSwitch0041::rollback(uint64_t now){
    phase.store(Restoring,std::memory_order_release);
    int result=port.apply(port.context,active->previous,journaled);trace(Restore,result);
    if(result){finish(RecoveryFailed);return;}
    if(journaled){
        int cleared=port.journal(port.context,nullptr);trace(JournalClear,cleared);
        if(cleared){finish(RecoveryFailed);return;}
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
        int result=list?ap01WifiProfilesRead0041(port.profiles,*list):-ENOMEM;trace(Profiles,result);
        if(result){finish(Failed);return;}
        bool found=false;
        for(unsigned i=0;i<list->count;++i){auto &row=list->profiles[i];
            if(!strcmp(row.ssid,active->ssid)){active->target=row;found=true;}}
        result=!found?-ENOENT:!port.profiles.current?-ENOSYS:
            port.profiles.current(port.profiles.context,active->previous.ssid,sizeof(active->previous.ssid),
                                  active->previous.password,sizeof(active->previous.password));
        if(!result&&(!memchr(active->previous.ssid,0,sizeof(active->previous.ssid))||
           !memchr(active->previous.password,0,sizeof(active->previous.password))||
           !active->previous.ssid[0]))result=-EILSEQ;
        trace(Current,result);if(result){finish(Failed);return;}
        // Selecting the current configuration never reconnects or rewrites it.
        if(!strcmp(active->previous.ssid,active->ssid)){finish(Connected);return;}
        if(port.profiles.busy&&port.profiles.busy(port.profiles.context)){trace(Blocked,-EBUSY);finish(Failed);return;}
        result=port.apply(port.context,active->target,false);trace(Trial,result);
        if(result){rollback(now);return;}
        deadline=now+45000;phase.store(Connecting,std::memory_order_release);return;
    }
    if(s==Connecting){
        if(port.online(port.context,active->target.ssid)){
            trace(Online);phase.store(Saving,std::memory_order_release);
            // Trial changes only RAM. Persist the old network before either key write.
            int result=port.journal(port.context,&active->previous);trace(JournalSave,result);
            if(result){rollback(now);return;}
            journaled=true;
            result=port.apply(port.context,active->target,true);trace(Persist,result);
            if(result){rollback(now);return;}
            // Cleanup can be ambiguous: both target keys are verified now. Do
            // not start another two-key write after possibly removing the journal.
            result=port.journal(port.context,nullptr);trace(JournalClear,result);
            if(result){finish(RecoveryFailed);return;}
            finish(Connected);
        }else if(now>=deadline){trace(TargetTimeout,-ETIMEDOUT);rollback(now);}
    }else if(s==Restoring){
        if(port.online(port.context,active->previous.ssid)){
            if(journaled){
                int result=port.journal(port.context,nullptr);trace(JournalClear,result);
                if(result){finish(RecoveryFailed);return;}
            }
            finish(Failed);
        }else if(now>=deadline){trace(RestoreTimeout,-ETIMEDOUT);finish(Failed);}
    }
}
