#include "app_tasks_0041.h"
#include <new>
struct Ap01AppTasks0041::Task {
    Ap01AppTasks0041 *owner;
    void *(*entry)(void *);
    void *context;
};
int Ap01AppTasks0041::start(Spawn spawn,uint32_t *id,const char *name,void *(*entry)(void *),unsigned stack,void *context,uint32_t generation){
    if(!spawn||!id||!entry||!name||!stack||!gate.acquire(generation))return -1;
    auto *task=new(std::nothrow) Task{this,entry,context};
    if(!task){gate.release();return -1;}
    // Bound tasks even when an immediately scheduled bootstrap spawns another
    // task before this spawn call returns. Native task exits may race both.
    uint32_t count=active.load(std::memory_order_acquire);
    do {
        if(count>=maxTasks){delete task;gate.release();return -1;}
    }while(!active.compare_exchange_weak(count,count+1,std::memory_order_acq_rel));
    int result=spawn(id,name,run,stack,task);
    if(result){delete task;gate.release();active.fetch_sub(1,std::memory_order_release);}
    return result;
}
void *Ap01AppTasks0041::run(void *p){
    auto *task=(Task *)p;auto *owner=task->owner;
    void *result=task->entry(task->context);
    delete task;
    owner->gate.release();
    // Last owner access. The caller requires BOTH task drain and gate drain
    // before freeing the group, gate, state, or App image.
    owner->active.fetch_sub(1,std::memory_order_release);
    return result;
}
