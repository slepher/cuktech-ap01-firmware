#include "app_runtime_heap_v2.h"
#include "app_services_0041.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <ctime>
extern "C" time_t ap01_app_time_v2(time_t *) noexcept;
struct Clock {
    uint64_t seconds=1700000000;bool fail=false;
    static bool read(void *p,uint64_t *out){auto &c=*(Clock *)p;*out=c.seconds;return !c.fail;}
};
int main(){
    assert(!ap01_app_malloc_v2(16)&&ap01_app_free_v2(nullptr));
    time_t value=0;assert(ap01_app_time_v2(&value)==-1&&value==-1);
    alignas(16) uint8_t memory[1024];Ap01AppGeneration0041 gate;
    Ap01AppHeap0041 heap(gate);assert(heap.bind(1,memory,sizeof(memory)));
    Clock clock;Ap01AppCore0041 core(gate,{&clock,nullptr,nullptr,nullptr,nullptr,Clock::read});Ap01AppFiles0041 files(gate,{},"/unused");
    Ap01AppServices0041 bus(core,files,nullptr,&heap);auto services=bus.table(gate.begin());
    auto invalid=services;invalid.generation=0;assert(!ap01_app_runtime_bind_heap_v2(&invalid));
    invalid=services;invalid.available_services=0;assert(!ap01_app_runtime_bind_heap_v2(&invalid));
    assert(ap01_app_runtime_bind_heap_v2(&services)&&!ap01_app_runtime_bind_heap_v2(&services));
    assert(ap01_app_time_v2(&value)==1700000000&&value==1700000000);
    clock.seconds=INT32_MAX;assert(ap01_app_time_v2(nullptr)==INT32_MAX);
    clock.seconds=uint64_t(INT32_MAX)+1;assert(ap01_app_time_v2(&value)==-1&&value==-1);
    clock.seconds=0;assert(ap01_app_time_v2(&value)==0&&value==0);
    clock.fail=true;assert(ap01_app_time_v2(&value)==-1&&value==-1);clock.fail=false;
    uint64_t output=99;clock.fail=true;
    assert(ap01_app_runtime_core_call_v2(AP01_CORE_UTC_SECONDS,&output,8)==AP01_SERVICE_IO&&!output);
    clock.fail=false;assert(ap01_app_runtime_core_call_v2(AP01_CORE_UTC_SECONDS,&output,4)==AP01_SERVICE_INVALID);
    auto *p=(uint8_t *)ap01_app_calloc_v2(8,8);assert(p&&!(uintptr_t(p)&15));
    for(unsigned i=0;i<64;++i)assert(!p[i]);memset(p,0x71,64);
    assert(!ap01_app_calloc_v2(SIZE_MAX,2)&&!ap01_app_realloc_v2(p,UINT32_MAX));
    auto *larger=(uint8_t *)ap01_app_realloc_v2(p,128);assert(larger);
    for(unsigned i=0;i<64;++i)assert(larger[i]==0x71);
    assert(!ap01_app_runtime_heap_fault_v2()&&ap01_app_free_v2(larger));
    assert(!ap01_app_free_v2(larger)&&ap01_app_runtime_heap_fault_v2());
    auto *retained=ap01_app_malloc_v2(32);assert(retained);
    gate.close();assert(!ap01_app_malloc_v2(1)&&!ap01_app_free_v2(retained));assert(heap.drain());
    assert(ap01_app_time_v2(&value)==-1&&value==-1);
    for(auto byte:memory)assert(!byte);
    puts("private App runtime: heap bind/overflow/realloc/free/drain; time UTC success, zero, signed-32 limit, overflow, read failure, output clearing and closed generation passed");
}
