#include "app_lifecycle_0041.h"
using R=Ap01AppLifeResult;
R Ap01AppLifecycle0041::start(const ap01_app_entries_v2 &e,const ap01_app_services_v2 &s){
    if(dispatching||phase!=Phase::Empty||!gate.drained()||s.abi_version!=AP01_APP_ABI_V2||s.struct_bytes!=sizeof(s)||
       s.reserved||!s.generation||!s.invoke||!e.start||!e.event||!e.prepare_stop||!e.stop||!e.health)return R::Invalid;
    // Generation allocation precedes exposing any App callback. The caller
    // predicts the next generation for the service table; no generation wraps.
    if(gate.current()==UINT32_MAX||s.generation!=gate.current()+1)return R::Invalid;
    generation=gate.begin();if(!generation)return R::Invalid;
    entries=e;services=s;state=nullptr;eventProgress=0;entered=false;prepared=false;phase=Phase::Running;
    dispatching=true;int32_t result=entries.start(&services,&state);dispatching=false;
    entered=result==0;
    if(!entered){gate.close();phase=Phase::Stopping;stopDeadline=0;return R::Fault;}
    return R::Ok;
}
R Ap01AppLifecycle0041::event(uint32_t id,const ap01_app_event_v2 &event){
    if(dispatching||phase!=Phase::Running||id!=generation||!entered||event.struct_bytes!=sizeof(event)||
       (event.length&&!event.bytes))return R::Invalid;
    Ap01AppLease0041 lease(gate,id);if(!lease)return R::Invalid;
    dispatching=true;int32_t result=entries.event(state,&event);dispatching=false;
    if(result){entered=false;gate.close();return R::Fault;}
    ++eventProgress;return R::Ok;
}
R Ap01AppLifecycle0041::health(uint32_t id,ap01_app_health_v2 &out){
    out={sizeof(out),0,0,0};
    if(dispatching||phase!=Phase::Running||id!=generation||!entered)return R::Invalid;
    Ap01AppLease0041 lease(gate,id);if(!lease)return R::Invalid;
    dispatching=true;int32_t result=entries.health(state,&out);dispatching=false;
    if(result||out.struct_bytes!=sizeof(out)||out.reserved||out.entry_ready>1||out.resource_fault>1){
        entered=false;gate.close();out={sizeof(out),0,1,0};return R::Fault;
    }
    return R::Ok;
}
R Ap01AppLifecycle0041::stop(uint64_t now,uint64_t budget){
    if(dispatching)return R::Invalid;
    if(phase==Phase::Empty)return R::Ok;
    if(phase==Phase::Retained)return R::RebootRequired;
    if(!budget||budget>60000||now>UINT64_MAX-budget)return R::Invalid;
    if(phase==Phase::Running||!stopDeadline){
        gate.close();phase=Phase::Stopping;stopDeadline=now+budget;
    }
    return pollStop(now);
}
R Ap01AppLifecycle0041::pollStop(uint64_t now){
    if(dispatching)return R::Invalid;
    if(phase==Phase::Empty)return R::Ok;
    if(phase==Phase::Retained)return R::RebootRequired;
    if(phase!=Phase::Stopping||!stopDeadline)return R::Invalid;
    if(now>=stopDeadline){phase=Phase::Retained;return R::RebootRequired;}
    if(!prepared){
        dispatching=true;int32_t result=entries.prepare_stop(state);dispatching=false;
        if(result<0){phase=Phase::Retained;return R::RebootRequired;}
        if(result)return R::Pending;
        prepared=true;
    }
    if(!gate.drained())return R::Pending;
    dispatching=true;int32_t result=entries.stop(state);dispatching=false;
    if(result){phase=Phase::Retained;return R::RebootRequired;}
    state=nullptr;entries={};services={};entered=false;phase=Phase::Empty;
    return R::Ok;
}
