#include "app_lifecycle_0041.h"
#include <assert.h>
#include <stdio.h>
struct App {
    unsigned starts=0,events=0,prepares=0,stops=0;
    bool startFault=false,stopFault=false,prepareFault=false,healthFault=false;
    unsigned pending=0;
    Ap01AppLifecycle0041 *runtime=nullptr;
    static int32_t invoke(void *,uint32_t,uint32_t,uint32_t,const void *,uint32_t,void *,uint32_t,uint32_t *){return -1;}
    static int32_t start(const ap01_app_services_v2 *s,void **state){auto *a=(App *)s->context;*state=a;++a->starts;
        assert(a->runtime->stop(0,10)==Ap01AppLifeResult::Invalid);return a->startFault?-1:0;}
    static int32_t event(void *p,const ap01_app_event_v2 *){++((App *)p)->events;return 0;}
    static int32_t prepare(void *p){auto &a=*(App *)p;++a.prepares;if(a.prepareFault)return -1;if(a.pending){--a.pending;return 1;}return 0;}
    static int32_t stop(void *p){auto &a=*(App *)p;++a.stops;return a.stopFault?-1:0;}
    static int32_t health(void *p,ap01_app_health_v2 *out){out->entry_ready=1;out->reserved=((App *)p)->healthFault;return 0;}
    ap01_app_entries_v2 entries(){return {start,event,prepare,stop,health};}
    ap01_app_services_v2 services(unsigned generation){return {2,sizeof(ap01_app_services_v2),generation,0,0,this,invoke};}
};
int main(){
    using R=Ap01AppLifeResult;
    for(unsigned scenario=0;scenario<6;++scenario){
        Ap01AppGeneration0041 gate;Ap01AppLifecycle0041 life(gate);App app;app.runtime=&life;
        assert(life.releasable());auto bad=app.services(1);bad.reserved=1;assert(life.start(app.entries(),bad)==R::Invalid&&app.starts==0);
        app.startFault=scenario==1;app.stopFault=scenario==2;app.prepareFault=scenario==3;app.pending=scenario==4?100:2;
        assert(life.start(app.entries(),app.services(1))==(app.startFault?R::Fault:R::Ok));
        assert(!life.releasable());ap01_app_event_v2 event{sizeof(event),1,0,0,nullptr,0};
        if(!app.startFault){assert(life.event(1,event)==R::Ok&&life.progress()==1);assert(life.event(2,event)==R::Invalid);}
        ap01_app_health_v2 health{};
        if(!app.startFault){assert(life.health(1,health)==R::Ok&&health.entry_ready);if(scenario!=5){app.healthFault=true;assert(life.health(1,health)==R::Fault&&health.resource_fault);assert(!gate.acquire(1));}}
        if(scenario==5){
            Ap01AppLease0041 callback(gate,1);assert(callback);app.pending=0;
            assert(life.stop(1,20)==R::Pending&&!life.releasable()&&!app.stops);
            assert(life.pollStop(21)==R::RebootRequired&&!app.stops);continue;
        }
        auto stopped=life.stop(1,10);
        assert(life.event(1,event)==R::Invalid&&!gate.acquire(1));
        if(scenario==3){assert(stopped==R::RebootRequired&&!app.stops);continue;}
        assert(stopped==R::Pending);
        assert(life.pollStop(2)==R::Pending);
        stopped=life.pollStop(scenario==4?11:3);
        if(scenario==2||scenario==4){assert(stopped==R::RebootRequired&&!life.releasable());assert(life.start(app.entries(),app.services(2))==R::Invalid);}
        else {
            assert(stopped==R::Ok&&life.releasable()&&app.stops==1);
            app.startFault=false;assert(life.start(app.entries(),app.services(2))==R::Ok);
            assert(!gate.acquire(1)&&life.event(1,event)==R::Invalid&&life.event(2,event)==R::Ok);
            assert(life.stop(10,10)==R::Ok&&life.releasable());
        }
    }
    puts("lifecycle: C ABI guards, reentrancy, partial start cleanup, leased callbacks, stop faults/timeouts, old-generation rejection passed");
}
