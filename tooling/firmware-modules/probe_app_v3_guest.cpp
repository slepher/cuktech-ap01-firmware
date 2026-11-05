// Model only: real App instructions, production loader/provider/host, fake ROM I/O.
#include "native_app_platform_v3.h"
#include "model_platform_v3.h"
#include "app_heap_0041.h"
#include "app_heap_client_v2.h"
#include <new>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdio.h>
namespace std {const nothrow_t nothrow{};}
// Test-only reuse of the validated arena; production ABI 3 still uses ROM malloc.
// QEMU maps this arena through 0xa83fffff, not the old bump limit 0xa8500000.
static Ap01AppHeapClientV2 &modelHeap(){
    alignas(Ap01AppGeneration0041) static uint8_t gateStorage[sizeof(Ap01AppGeneration0041)];
    alignas(Ap01AppHeap0041) static uint8_t heapStorage[sizeof(Ap01AppHeap0041)];
    alignas(Ap01AppHeapClientV2) static uint8_t clientStorage[sizeof(Ap01AppHeapClientV2)];
    static bool ready=false;
    if(!ready){
        auto *gate=new(gateStorage) Ap01AppGeneration0041;
        auto *heap=new(heapStorage) Ap01AppHeap0041(*gate);
        if(!heap->bind(1,(void *)0xa8200000,0x200000)||gate->begin()!=1)__builtin_trap();
        new(clientStorage) Ap01AppHeapClientV2(heap->table(1));ready=true;
    }
    return *(Ap01AppHeapClientV2 *)clientStorage;
}
extern "C" void *malloc(size_t n){return modelHeap().allocate(n);}
extern "C" void free(void *p){if(p)modelHeap().free(p);}
extern "C" void *realloc(void *p,size_t n){return modelHeap().reallocate(p,n);}
void *operator new(size_t n){return malloc(n);}
void *operator new(size_t n,const std::nothrow_t &) noexcept{return malloc(n);}
void *operator new[](size_t n,const std::nothrow_t &) noexcept{return malloc(n);}
void operator delete[](void *p) noexcept{free(p);}
void operator delete(void *p) noexcept{free(p);}
void operator delete(void *p,size_t) noexcept{free(p);}
extern "C" time_t time(time_t *p){time_t n=1700000000;if(p)*p=n;return n;}
// Cooperative model tasks preserve all ABI callee-saved integer/float registers.
struct Context {uint32_t words[26];};
extern "C" void modelSwitch(Context *,Context *);
asm(".text\n.global modelSwitch\nmodelSwitch:\n"
"sw ra,0(a0)\nsw sp,4(a0)\nsw s0,8(a0)\nsw s1,12(a0)\nsw s2,16(a0)\nsw s3,20(a0)\nsw s4,24(a0)\nsw s5,28(a0)\nsw s6,32(a0)\nsw s7,36(a0)\nsw s8,40(a0)\nsw s9,44(a0)\nsw s10,48(a0)\nsw s11,52(a0)\n"
"fsw fs0,56(a0)\nfsw fs1,60(a0)\nfsw fs2,64(a0)\nfsw fs3,68(a0)\nfsw fs4,72(a0)\nfsw fs5,76(a0)\nfsw fs6,80(a0)\nfsw fs7,84(a0)\nfsw fs8,88(a0)\nfsw fs9,92(a0)\nfsw fs10,96(a0)\nfsw fs11,100(a0)\n"
"lw ra,0(a1)\nlw sp,4(a1)\nlw s0,8(a1)\nlw s1,12(a1)\nlw s2,16(a1)\nlw s3,20(a1)\nlw s4,24(a1)\nlw s5,28(a1)\nlw s6,32(a1)\nlw s7,36(a1)\nlw s8,40(a1)\nlw s9,44(a1)\nlw s10,48(a1)\nlw s11,52(a1)\n"
"flw fs0,56(a1)\nflw fs1,60(a1)\nflw fs2,64(a1)\nflw fs3,68(a1)\nflw fs4,72(a1)\nflw fs5,76(a1)\nflw fs6,80(a1)\nflw fs7,84(a1)\nflw fs8,88(a1)\nflw fs9,92(a1)\nflw fs10,96(a1)\nflw fs11,100(a1)\nret\n");
static uint8_t *stackBottom[4]{};
static Context scheduler{},workers[4]{};static unsigned current=0,initialized=0;static bool done[4]{};
static void pauseTask(uint32_t){
    ap01ModelV3.threadIdentity=1;modelSwitch(&workers[current],&scheduler);
}
static void runTask(){auto &t=ap01ModelV3.tasks[current];t.entry(t.context);done[current]=true;for(;;)pauseTask(0);}
static bool reserve(void *p,const Apx2View &v,Ap01BootMemoryV3 &m){if((v.image_bytes+v.bss_bytes)>0x40000)return false;m={(uint8_t *)p,0x40000,uint32_t(uintptr_t(p))};return true;}
static bool publish(void *,const Ap01BootMemoryV3 &m,const Apx2View &v,Ap01AppEntriesV3 &e){asm volatile("fence.i":::"memory");e={(Ap01AppStartV3)(m.base+v.entries[0]),(Ap01AppEventV3)(m.base+v.entries[1]),(Ap01AppHealthV3)(m.base+v.entries[2])};return true;}
#define CHECK(x) do {if(!(x))return __LINE__;}while(0)
#ifdef AP01_MODEL_SET_V3
#include "probe_app_set_v3_guest.h"
#else
extern "C" __attribute__((section(".text.guest_entry"))) int guest_entry(uint32_t base,const uint8_t *package,uint32_t bytes){
    asm volatile("li t0,0x6000\ncsrs mstatus,t0":::"t0");
    ap01ModelV3=Ap01ModelPlatformV3{};ap01ModelV3.package=package;ap01ModelV3.packageBytes=bytes;
    auto *platform=new Ap01NativeAppPlatformV3(42,{(void *)base,nullptr,reserve,publish});
    CHECK(platform&&platform->bindWindow((void *)1,ap01ModelStockV3));
    Apx2Limits limits{1u<<22,1u<<23,1u<<21,40960,1,AP01_CODEX_CAPS_V3,"codex_status",3};
    CHECK(platform->stageFile("/resource/app-current.apx2",limits));
    platform->poll(platform);CHECK(!platform->execution().entered()&&ap01ModelV3.taskCount==0);
    CHECK(platform->startMaintenance());platform->poll(platform);
    CHECK(platform->result()==Ap01BootResultV3::Started);
    CHECK(ap01ModelV3.mounts==1&&ap01ModelV3.packageCloses==1&&ap01ModelV3.taskCount==1);
    CHECK(platform->table().ui.host->app_count==1);
    ap01ModelV3.pause=pauseTask;
    for(unsigned round=0;round<12;++round){
        for(unsigned i=0;i<ap01ModelV3.taskCount;++i){
            if(i>=initialized){uint32_t stack=ap01ModelV3.tasks[i].stack;auto *p=(uint8_t *)malloc(stack);CHECK(p);memset(p,0xa5,stack);stackBottom[i]=p;workers[i].words[0]=uint32_t(uintptr_t(runTask));workers[i].words[1]=uint32_t(uintptr_t(p+stack));++initialized;}
            CHECK(!done[i]);current=i;ap01ModelV3.threadIdentity=i+2;modelSwitch(&scheduler,&workers[i]);
        }
        platform->poll(platform);
    }
    CHECK(ap01ModelV3.taskCount==2&&platform->reservedStack()==40960);
    CHECK(platform->execution().event(1,nullptr,0)==AP01_APP_V3_OK);
    CHECK(platform->execution().health()==AP01_APP_V3_OK);
    CHECK(platform->peakHeap()>0&&platform->peakHeap()<1u<<21);
    CHECK(ap01ModelV3.bridge.online(ap01ModelV3.bridge.context));
    ap01ModelV3.eventCode=0x29;ap01ModelV3.eventTarget=(void *)1;
    ap01ModelV3.window->event(ap01ModelV3.window->context,(void *)1);
    CHECK(!ap01ModelV3.window->win&&platform->execution().health()==AP01_APP_V3_PENDING);
    ap01ModelV3.eventCode=0;ap01ModelV3.eventTarget=nullptr;
    CHECK(platform->bindWindow((void *)2,ap01ModelStockV3));platform->poll(platform);
    CHECK(ap01ModelV3.mounts==2&&ap01ModelV3.taskCount==2&&ap01ModelV3.maintenanceStarts==1);
    CHECK(platform->execution().health()==AP01_APP_V3_OK);
    for(unsigned i=0;i<initialized;++i)for(unsigned j=0;j<64;++j)CHECK(stackBottom[i][j]==0xa5);
    return 0;
}

#endif
