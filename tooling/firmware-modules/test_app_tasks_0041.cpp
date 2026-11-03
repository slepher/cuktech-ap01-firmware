#include "app_tasks_0041.h"
#include <assert.h>
#include <thread>
#include <stdio.h>
void *(*pending)(void *)=nullptr;void *argument=nullptr;
int spawn(uint32_t *id,const char *,void *(*entry)(void *),unsigned,void *p){*id=9;pending=entry;argument=p;return 0;}
int fail(uint32_t *,const char *,void *(*)(void *),unsigned,void *){return -1;}
struct App{Ap01AppTasks0041 *tasks;Ap01AppGeneration0041 *gate;unsigned calls=0;
    static void *entry(void *p){auto &a=*(App *)p;++a.calls;assert(!a.tasks->drained()&&!a.gate->drained());return p;}};
int main(){
    Ap01AppGeneration0041 gate;Ap01AppTasks0041 tasks(gate);App app{&tasks,&gate};uint32_t id=0;
    auto gen=gate.begin();assert(gen);
    assert(tasks.start(fail,&id,"failed",App::entry,1024,&app,gen)==-1&&tasks.drained());
    assert(tasks.start(spawn,&id,"app",App::entry,1024,&app,gen)==0&&!tasks.drained());
    gate.close();assert(!gate.drained()&&!tasks.drained());
    assert(tasks.start(spawn,&id,"late",App::entry,1024,&app,gen)==-1);
    std::thread worker([&]{assert(pending(argument)==&app);});worker.join();
    assert(gate.drained()&&tasks.drained()&&app.calls==1);
    auto next=gate.begin();assert(next==gen+1);
    assert(tasks.start(spawn,&id,"stale",App::entry,1024,&app,gen)==-1);
    void *queued[Ap01AppTasks0041::maxTasks];
    for(unsigned i=0;i<Ap01AppTasks0041::maxTasks;++i){assert(tasks.start(spawn,&id,"bounded",App::entry,1024,&app,next)==0);queued[i]=argument;}
    assert(tasks.start(spawn,&id,"overflow",App::entry,1024,&app,next)==-1);
    gate.close();assert(!gate.drained()&&!tasks.drained());
    for(auto *context:queued)assert(pending(context)==&app);
    assert(gate.drained()&&tasks.drained());
    puts("App tasks: spawn failure, delayed native start, lease beyond App return, close admission, next generation passed");
}
