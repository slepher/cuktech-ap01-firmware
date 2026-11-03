// QEMU-only firmware harness. Fixed memory and fence.i do NOT establish the
// physical AP01 cache/permission contract; this is never a production backend.
#include "app_image_0041.h"
#include "app_core_0041.h"
#include "app_services_0041.h"
#include <stddef.h>
extern "C" void *memcpy(void *d,const void *s,size_t n){auto *o=(uint8_t *)d;auto *i=(const uint8_t *)s;while(n--)*o++=*i++;return d;}
extern "C" void *memset(void *d,int c,size_t n){auto *o=(uint8_t *)d;while(n--)*o++=uint8_t(c);return d;}
extern "C" int memcmp(const void *a,const void *b,size_t n){auto *x=(const uint8_t *)a,*y=(const uint8_t *)b;while(n--){if(*x!=*y)return *x-*y;++x;++y;}return 0;}
extern "C" size_t strlen(const char *s){size_t n=0;while(s[n])++n;return n;}
extern "C" int strcmp(const char *a,const char *b){while(*a&&*a==*b){++a;++b;}return (unsigned char)*a-(unsigned char)*b;}
extern "C" void *memchr(const void *s,int c,size_t n){auto *p=(const uint8_t *)s;while(n--){if(*p==uint8_t(c))return (void *)p;++p;}return nullptr;}
struct Backend {uint32_t base,reserves=0,releases=0,publishes=0,calls=0;Ap01AppImage0041 *owner=nullptr;Ap01AppHeap0041 *heap=nullptr;alignas(16) uint8_t arena[512];};
static bool reserve(void *p,const Apx2View &v,Ap01AppMemory0041 &out){auto &b=*(Backend *)p;
    if(v.image_bytes+v.bss_bytes>8192||v.heap_bytes!=sizeof(b.arena)||v.stack_bytes>4096||
       !b.heap->bind(b.owner->callbacks().current()+1,b.arena,v.heap_bytes))return false;
    ++b.reserves;out={(uint8_t *)(uintptr_t)b.base,8192,b.base,&b};return true;
}
static bool publish(void *p,const Ap01AppMemory0041 &m,const Apx2View &v,ap01_app_entries_v2 &e){
    auto &b=*(Backend *)p;++b.publishes;
    __asm__ volatile("fence.i" ::: "memory");
    e.start=(decltype(e.start))(uintptr_t)(m.base+v.entries[0]);
    e.event=(decltype(e.event))(uintptr_t)(m.base+v.entries[1]);
    e.prepare_stop=(decltype(e.prepare_stop))(uintptr_t)(m.base+v.entries[2]);
    e.stop=(decltype(e.stop))(uintptr_t)(m.base+v.entries[3]);
    e.health=(decltype(e.health))(uintptr_t)(m.base+v.entries[4]);return true;
}
static void release(void *p,const Ap01AppMemory0041 &m){auto &b=*(Backend *)p;
    if(!b.owner->callbacks().drained()||!b.heap->drain())b.releases=1000;else ++b.releases;
    memset(m.bytes,0,m.capacity);
}
static bool drain(void *p){return ((Backend *)p)->heap->drain();}
static bool random(void *p,uint8_t *out,uint32_t capacity){
    auto &b=*(Backend *)p;if(capacity!=4)return false;
    ++b.calls;uint32_t value=7;memcpy(out,&value,4);return true;
}
static bool utc(void *,uint64_t *out){*out=1700000000;return true;}
struct Input {const uint8_t *bytes;uint32_t size;};
static bool read(void *p,uint32_t at,uint8_t *out,uint32_t n){auto &i=*(Input *)p;if(uint64_t(at)+n>i.size)return false;memcpy(out,i.bytes+at,n);return true;}
#define CHECK(x) do {if(!(x))return __LINE__;}while(0)
extern "C" __attribute__((section(".text.guest_entry"),used))
uint32_t guest_entry(uint32_t base,const uint8_t *package,uint32_t size){
    Backend backend{base};Ap01AppImage0041 owner({&backend,reserve,publish,release,drain});backend.owner=&owner;
    Ap01AppHeap0041 heap(owner.callbacks());backend.heap=&heap;
    Input input{package,size};Apx2Reader reader{&input,size,read};Apx2Limits limits{8192,8192+512+4096,512,4096,1,9,"abi.probe"};
    Ap01AppCore0041 core(owner.callbacks(),{&backend,nullptr,random,nullptr,nullptr,utc});
    Ap01AppFiles0041 files(owner.callbacks(),{},"/unused");Ap01AppServices0041 router(core,files,nullptr,&heap);
    auto services=router.table(1);
    CHECK(size>=256);uint8_t digest[32];memcpy(digest,package+192,32);
    for(unsigned generation=1;generation<=2;++generation){
        services.generation=generation;
        CHECK(owner.start(reader,limits,digest,services)==Ap01AppImageResult::Running);
        CHECK(backend.calls==generation&&backend.publishes==generation);
        ap01_app_event_v2 event{sizeof(event),1,0,0,nullptr,0};
        CHECK(owner.event(generation,event)==Ap01AppLifeResult::Ok);
        CHECK(owner.event(generation+1,event)==Ap01AppLifeResult::Invalid);
        ap01_app_health_v2 health{};CHECK(owner.health(generation,health)==Ap01AppLifeResult::Ok&&health.entry_ready);
        CHECK(owner.callbacks().acquire(generation));
        CHECK(owner.stop(1,100)==Ap01AppLifeResult::Pending);
        CHECK(owner.stop(2,100)==Ap01AppLifeResult::Pending&&backend.releases==generation-1);
        owner.callbacks().release();
        CHECK(owner.stop(3,100)==Ap01AppLifeResult::Ok&&backend.releases==generation);
        for(auto byte:backend.arena)CHECK(byte==0);
        CHECK(!owner.callbacks().acquire(generation)&&owner.nextGeneration()==generation+1);
    }
    digest[0]^=1;services.generation=3;
    CHECK(owner.start(reader,limits,digest,services)==Ap01AppImageResult::Identity);
    CHECK(backend.reserves==2&&backend.releases==2);
    return 0;
}
