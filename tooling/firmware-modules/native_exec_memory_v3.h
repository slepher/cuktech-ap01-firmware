#pragma once
#include "app_boot_v3.h"
#include <stdlib.h>

// One UI loader owns this object for the entire boot. Allocations, including
// failed starts, remain live until reset; there is deliberately no unload API.
class Ap01NativeExecMemoryV3 {
    struct Image {uint32_t base=0,bytes=0;bool published=false;};
    Image images[8]{};
    uint32_t limit,used=0,count=0;
    void *(*allocate)(size_t);
    void (*release)(void *);
    static bool reserve(void *,const Apx2View &,Ap01BootMemoryV3 &);
    static bool publish(void *,const Ap01BootMemoryV3 &,const Apx2View &,Ap01AppEntriesV3 &);
public:
    explicit Ap01NativeExecMemoryV3(uint32_t budget,
        void *(*alloc)(size_t)=malloc,void (*freeRejected)(void *)=free)
        :limit(budget),allocate(alloc),release(freeRejected){}
    Ap01BootPortV3 port(){return {this,nullptr,reserve,publish};}
    uint32_t retainedBytes()const{return used;}
    uint32_t retainedImages()const{return count;}
};
