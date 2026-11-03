#include "app_runner_0041.h"
using S=Ap01AppRunState;using L=Ap01AppLifeResult;using R=Ap01AppSelectionResult;
namespace {
bool read(void *p,uint32_t at,uint8_t *out,uint32_t n){auto &f=*(File *)p;return f.seek(at)&&f.read(out,n)==n;}
struct Dispatch {bool &flag;explicit Dispatch(bool &f):flag(f){flag=true;}~Dispatch(){flag=false;}};
}
bool Ap01AppRunner0041::syncWrites(){
    bool allow=selection.businessWritesAllowed(chosen.generation);
    if(allow==writesEnabled)return true;
    if(resourcePort.writePermission&&!resourcePort.writePermission(resourcePort.context,chosen.generation,allow))return false;
    writesEnabled=allow;return true;
}
S Ap01AppRunner0041::reconcile(uint64_t now){
    if(dispatching||state!=S::Running)return state;
    Dispatch guard(dispatching);
    if(!syncWrites())return fail(now,AfterStop::Recovery);
    return state;
}
S Ap01AppRunner0041::launch(uint64_t now){
    if(dispatching||state==S::Running||state==S::Stopping||state==S::RebootRequired)return state;
    Dispatch guard(dispatching);
    uint32_t generation=image.nextGeneration();if(!generation)return state=S::RebootRequired;
    auto selected=selection.select(generation,chosen,now);
    if(selected!=R::Launch)return state=selected==R::Unknown?S::Unknown:S::Recovery;
    services.generation=generation;
    File f=fs.open(chosen.path,"r");uint32_t size=0;
    auto result=f&&f.length(size)?image.start({&f,size,read},limits,chosen.digest,services):Ap01AppImageResult::Package;
    if(result==Ap01AppImageResult::Running){
        state=S::Running;
        if(!syncWrites())return fail(now,AfterStop::Recovery);
        return state;
    }
    after=chosen.trial||chosen.rollback?AfterStop::Retry:AfterStop::Recovery;
    state=S::Stopping;return state; // Drain even a partially successful start.
}
S Ap01AppRunner0041::drain(uint64_t now){
    writesEnabled=false; // stop closes the service gate before invoking App code.
    auto result=image.stop(now,stopBudgetMs);
    if(result==L::Pending)return state=S::Stopping;
    if(result!=L::Ok)return state=S::RebootRequired;
    chosen={};
    switch(after){
    case AfterStop::Hold:case AfterStop::Retry:return state=S::Idle;
    case AfterStop::Recovery:return state=S::Recovery;
    case AfterStop::Unknown:return state=S::Unknown;
    }
    return state=S::RebootRequired;
}
S Ap01AppRunner0041::fail(uint64_t now,AfterStop next){
    after=next;state=S::Stopping;drain(now);
    if(next==AfterStop::Retry&&state==S::Idle)state=S::Stopping;
    return state;
}
S Ap01AppRunner0041::stop(uint64_t now){
    if(dispatching||state==S::RebootRequired)return state;
    Dispatch guard(dispatching);after=AfterStop::Hold;return drain(now);
}
S Ap01AppRunner0041::tick(uint64_t now,uint32_t stock,uint32_t maintenance){
    if(dispatching)return state;
    if(state==S::Stopping){
        bool retry=after==AfterStop::Retry;
        {Dispatch guard(dispatching);drain(now);}
        if(retry&&state==S::Idle)return launch(now);
        return state;
    }
    if(state!=S::Running)return state;
    Dispatch guard(dispatching);
    if(!syncWrites())return fail(now,AfterStop::Recovery);
    ap01_app_health_v2 health{};
    if(image.health(chosen.generation,health)!=L::Ok||health.resource_fault)
        return fail(now,chosen.trial||chosen.rollback?AfterStop::Retry:AfterStop::Recovery);
    if(chosen.trial||chosen.rollback){
        Ap01AppHealthSample sample{health.entry_ready!=0,true,image.progress(),stock,maintenance};
        auto result=selection.observe(chosen.generation,chosen.digest,now,sample);
        if(result==R::Unknown)return fail(now,AfterStop::Unknown);
        if(result!=R::Waiting)return fail(now,AfterStop::Retry);
        if(selection.businessWritesAllowed(chosen.generation))chosen.trial=chosen.rollback=false;
    }
    if(!syncWrites())return fail(now,AfterStop::Recovery);
    return state;
}
L Ap01AppRunner0041::event(uint64_t now,const ap01_app_event_v2 &event){
    if(dispatching||state!=S::Running)return L::Invalid;
    Dispatch guard(dispatching);
    if(!syncWrites()){fail(now,AfterStop::Recovery);return L::Fault;}
    auto result=image.event(chosen.generation,event);
    if(result==L::Fault)fail(now,chosen.trial||chosen.rollback?AfterStop::Retry:AfterStop::Recovery);
    return result;
}
