#pragma once
#include "app_generation_0041.h"
#include <atomic>
// Firmware trampoline retains the lease until AFTER the App entry returns.
// A flag written at the end of an App function is not sufficient: its epilogue
// and return address still execute from App code.
class Ap01AppTasks0041 {
    struct Task;
    Ap01AppGeneration0041 &gate;
    std::atomic<uint32_t> active{0};
    static void *run(void *);
public:
    static constexpr uint32_t maxTasks=4;
    using Spawn=int (*)(uint32_t *,const char *,void *(*)(void *),unsigned,void *);
    explicit Ap01AppTasks0041(Ap01AppGeneration0041 &g):gate(g){}
    int start(Spawn,uint32_t *id,const char *name,void *(*entry)(void *),unsigned stack,void *context,uint32_t generation);
    bool drained() const {return active.load(std::memory_order_acquire)==0;}
};
