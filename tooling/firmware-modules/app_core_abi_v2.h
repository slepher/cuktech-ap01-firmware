#ifndef AP01_APP_CORE_ABI_V2_H
#define AP01_APP_CORE_ABI_V2_H
#include "app_abi_v2.h"
// Service 1, required-services bit 0. Exact output sizes, no input payload.
// RANDOM uses capacity as requested byte count (1..256). Buffers are borrowed.
#define AP01_APP_SERVICE_CORE 1u
#define AP01_APP_CORE_CAPABILITY UINT64_C(1)
enum { AP01_CORE_MONOTONIC_MS=1,AP01_CORE_RANDOM=2,AP01_CORE_MAC=3,AP01_CORE_YIELD=4,AP01_CORE_UTC_SECONDS=5 };
// UTC_SECONDS returns uint64 seconds since 1970, distinct from monotonic time.
// YIELD has no input/output; resident scheduler sleeps for one millisecond.
enum { AP01_SERVICE_OK=0,AP01_SERVICE_INVALID=-1,AP01_SERVICE_UNAVAILABLE=-2,AP01_SERVICE_IO=-3 };
static inline int32_t ap01_app_core_call(const ap01_app_services_v2 *s,uint32_t operation,void *out,uint32_t n){
    uint32_t written=0;
    if(!s||s->abi_version!=AP01_APP_ABI_V2||s->struct_bytes!=sizeof(*s)||s->reserved||
       !s->generation||!s->invoke||!(s->available_services&AP01_APP_CORE_CAPABILITY))return AP01_SERVICE_UNAVAILABLE;
    int32_t result=s->invoke(s->context,s->generation,AP01_APP_SERVICE_CORE,operation,0,0,out,n,&written);
    if(result)return result;
    return written==n?AP01_SERVICE_OK:AP01_SERVICE_IO;
}
#endif
