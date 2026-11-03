#pragma once
#include "app_heap_abi_v2.h"
#include <stddef.h>
// App-private adapter. It never calls platform malloc and never frees an
// address returned by another allocator. Bind once before App constructors.
class Ap01AppHeapClientV2 {
    ap01_app_services_v2 services;
    int call(unsigned op,void *address,size_t bytes,uint64_t &out){
        out=0;
        if(bytes>UINT32_MAX||services.abi_version!=2||services.struct_bytes!=sizeof(services)||services.reserved||
           !services.generation||!services.invoke||!(services.available_services&AP01_APP_HEAP_CAPABILITY))return AP01_SERVICE_INVALID;
        ap01_app_heap_request_v2 r{uint64_t((uintptr_t)address),uint32_t(bytes),0};
        // Busy means no mutation happened. Yield through the same generation;
        // bounded retries cannot keep a closed App alive or silently spin.
        for(unsigned tries=0;tries<1000;++tries){
            uint32_t written=0;unsigned capacity=op==AP01_HEAP_FREE?0:8;
            int result=services.invoke(services.context,services.generation,4,op,&r,sizeof(r),capacity?&out:nullptr,capacity,&written);
            if(result!=AP01_HEAP_BUSY)return result?result:written!=capacity||out>UINTPTR_MAX?AP01_SERVICE_IO:AP01_SERVICE_OK;
            if(ap01_app_core_call(&services,AP01_CORE_YIELD,nullptr,0))return AP01_SERVICE_UNAVAILABLE;
        }
        return AP01_HEAP_BUSY;
    }
public:
    explicit Ap01AppHeapClientV2(const ap01_app_services_v2 &s):services(s){}
    void *allocate(size_t bytes){uint64_t address=0;return call(AP01_HEAP_ALLOCATE,nullptr,bytes,address)?nullptr:(void *)(uintptr_t)address;}
    void *zeroAllocate(size_t count,size_t bytes){
        if(count&&bytes>UINT32_MAX/count)return nullptr;
        uint64_t address=0;return call(AP01_HEAP_ZERO_ALLOCATE,nullptr,count*bytes,address)?nullptr:(void *)(uintptr_t)address;
    }
    void *reallocate(void *old,size_t bytes){uint64_t address=0;return call(AP01_HEAP_REALLOCATE,old,bytes,address)?nullptr:(void *)(uintptr_t)address;}
    bool free(void *old){uint64_t address=0;return !call(AP01_HEAP_FREE,old,0,address);}
};
