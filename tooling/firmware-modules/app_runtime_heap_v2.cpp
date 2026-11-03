#include "app_runtime_heap_v2.h"
#include "app_heap_client_v2.h"
#include <atomic>
#include <new>
namespace {
ap01_app_services_v2 services{};
std::atomic<bool> bound{false},freeFailed{false};
}
extern "C" int ap01_app_runtime_bind_heap_v2(const ap01_app_services_v2 *s){
    // Lifecycle serialization owns binding; worker threads only read afterward.
    if(bound.load(std::memory_order_acquire)||!s||s->abi_version!=2||s->struct_bytes!=sizeof(*s)||
       s->reserved||!s->generation||!s->invoke||
       (s->available_services&(AP01_APP_HEAP_CAPABILITY|AP01_APP_CORE_CAPABILITY))!=(AP01_APP_HEAP_CAPABILITY|AP01_APP_CORE_CAPABILITY))return 0;
    services=*s;bound.store(true,std::memory_order_release);return 1;
}
extern "C" void *ap01_app_malloc_v2(size_t n){
    if(!bound.load(std::memory_order_acquire))return nullptr;
    return Ap01AppHeapClientV2(services).allocate(n);
}
extern "C" int32_t ap01_app_runtime_core_call_v2(uint32_t operation,void *output,uint32_t capacity){
    if(!bound.load(std::memory_order_acquire))return AP01_SERVICE_UNAVAILABLE;
    return ap01_app_core_call(&services,operation,output,capacity);
}
extern "C" void *ap01_app_calloc_v2(size_t count,size_t n){
    if(!bound.load(std::memory_order_acquire))return nullptr;
    return Ap01AppHeapClientV2(services).zeroAllocate(count,n);
}
extern "C" void *ap01_app_realloc_v2(void *old,size_t n){
    if(!bound.load(std::memory_order_acquire))return nullptr;
    return Ap01AppHeapClientV2(services).reallocate(old,n);
}
extern "C" int ap01_app_free_v2(void *old){
    if(!old)return 1;
    if(bound.load(std::memory_order_acquire)&&Ap01AppHeapClientV2(services).free(old))return 1;
    freeFailed.store(true,std::memory_order_release);return 0;
}
extern "C" int ap01_app_runtime_heap_fault_v2(){return freeFailed.load(std::memory_order_acquire);}

// Host tests call the prefixed functions without interposing on ASan/libc or
// platform allocations. The RV32 file-App object exports these actual symbols.
#ifndef AP01_RUNTIME_HEAP_HOST_TEST
extern "C" {
void *malloc(size_t n) noexcept {return ap01_app_malloc_v2(n);}
void *calloc(size_t count,size_t n) noexcept {return ap01_app_calloc_v2(count,n);}
void *realloc(void *old,size_t n) noexcept {return ap01_app_realloc_v2(old,n);}
void free(void *old) noexcept {(void)ap01_app_free_v2(old);}
}
namespace std {const nothrow_t nothrow{};}
void *operator new(size_t n,const std::nothrow_t &) noexcept {return ap01_app_malloc_v2(n?n:1);}
void *operator new[](size_t n,const std::nothrow_t &) noexcept {return ap01_app_malloc_v2(n?n:1);}
void operator delete(void *p) noexcept {(void)ap01_app_free_v2(p);}
void operator delete[](void *p) noexcept {(void)ap01_app_free_v2(p);}
void operator delete(void *p,size_t) noexcept {(void)ap01_app_free_v2(p);}
void operator delete[](void *p,size_t) noexcept {(void)ap01_app_free_v2(p);}
#endif
