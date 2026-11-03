// Small executable APX2 fixture, not the codex_status business App.
#include "app_core_abi_v2.h"
#include "app_runtime_heap_v2.h"
#include <new>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>
// Minimal private libc for this executable fixture; no firmware symbol import.
extern "C" void *memcpy(void *d,const void *s,size_t n) noexcept {auto *o=(uint8_t *)d;auto *i=(const uint8_t *)s;while(n--)*o++=*i++;return d;}
static struct State {uint32_t value,events,preparing;const ap01_app_services_v2 *services;uint8_t *heap;} state;
__attribute__((noinline)) static uint32_t addThree(uint32_t value){return value+3;}
static uint32_t (*volatile transform)(uint32_t)=addThree;
extern "C" {
__attribute__((used)) int32_t app_start(const ap01_app_services_v2 *s,void **out){
    if(!s||s->abi_version!=2||s->struct_bytes!=sizeof(*s)||!s->generation||!s->invoke)return -1;
    *out=&state;state={0,0,0,s,nullptr};
    if(!ap01_app_runtime_bind_heap_v2(s))return -1;
    time_t utc=0;if(time(&utc)!=1700000000||utc!=1700000000)return -1;
    char formatted[32];
    if(snprintf(formatted,sizeof(formatted),"%lld/%02u",(-9223372036854775807LL-1),7u)!=23)return -1;
    const char expected[]="-9223372036854775808/07";
    // Compare the terminating NUL too; this exercises RV32 64-bit varargs/division.
    for(unsigned i=0;i<sizeof(expected);++i)if(formatted[i]!=expected[i])return -1;
    auto *scratch=new(std::nothrow_t{}) uint8_t[16];if(!scratch)return -1;
    scratch[0]=5;delete[] scratch;
    state.heap=(uint8_t *)calloc(16,1);if(!state.heap)return -1;
    for(unsigned i=0;i<16;++i){if(state.heap[i])return -1;state.heap[i]=uint8_t(i+1);}
    auto *larger=(uint8_t *)realloc(state.heap,64);if(!larger)return -1;state.heap=larger;
    if(malloc(4096)||ap01_app_runtime_heap_fault_v2())return -1;
    if(ap01_app_core_call(s,AP01_CORE_RANDOM,&state.value,4)||state.value!=7)return -1;
    state.value=transform(state.value);return state.value==10?0:-1;
}
__attribute__((used)) int32_t app_event(void *p,const ap01_app_event_v2 *e){
    if(p!=&state||!e||e->struct_bytes!=sizeof(*e)||e->kind!=1)return -1;
    for(unsigned i=0;i<16;++i)if(state.heap[i]!=i+1)return -1;
    state.value+=transform(e->kind);++state.events;return 0;
}
__attribute__((used)) int32_t app_prepare_stop(void *p){
    if(p!=&state)return -1;
    return state.preparing++==0?1:0;
}
__attribute__((used)) int32_t app_stop(void *p){if(p!=&state)return -1;
    for(unsigned i=0;i<16;++i)if(state.heap[i]!=i+1)return -1;
    // Intentionally leave the allocation for resident resource drain.
    state={};return 0;}
__attribute__((used)) int32_t app_health(void *p,ap01_app_health_v2 *out){
    if(p!=&state||!out)return -1;
    out->entry_ready=state.value==14&&state.events==1;out->resource_fault=0;return 0;
}
}
