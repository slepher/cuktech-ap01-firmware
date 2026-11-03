#include "app_heap_0041.h"
#include "app_heap_client_v2.h"
#include "app_services_0041.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <array>
struct Client {
    ap01_app_services_v2 table;
    int call(unsigned op,uint64_t address,uint32_t n,uint64_t &out){
        ap01_app_heap_request_v2 request{address,n,0};uint32_t written=99;out=0;
        int result=table.invoke(table.context,table.generation,4,op,&request,16,
            op==AP01_HEAP_FREE?nullptr:&out,op==AP01_HEAP_FREE?0:8,&written);
        assert(written==(result||op==AP01_HEAP_FREE?0u:8u));return result;
    }
};
struct BusyService {
    unsigned attempts=0,yields=0;
    static int32_t invoke(void *p,uint32_t,uint32_t service,uint32_t operation,const void *,uint32_t,void *,uint32_t,uint32_t *written){
        auto &s=*(BusyService *)p;*written=0;
        if(service==4){++s.attempts;return AP01_HEAP_BUSY;}
        assert(service==1&&operation==AP01_CORE_YIELD);++s.yields;return AP01_SERVICE_OK;
    }
};
int main(){
    alignas(16) uint8_t storage[1056];memset(storage,0xa5,sizeof(storage));
    auto *memory=storage+16;Ap01AppGeneration0041 gate;Ap01AppHeap0041 heap(gate);
    assert(!heap.bind(2,memory,1024)&&!heap.bind(1,memory+1,1024)&&!heap.bind(1,memory,1023));
    assert(heap.bind(1,memory,256)&&!heap.bind(1,memory,256));
    Client client{heap.table(gate.begin())};uint64_t result=0;
    assert(!heap.drain());std::array<uint64_t,8> blocks{};
    for(auto &p:blocks){assert(!client.call(AP01_HEAP_ALLOCATE,0,1,p)&&p&&!(p&15));*(uint8_t *)(uintptr_t)p=0x55;}
    assert(client.call(AP01_HEAP_ALLOCATE,0,1,result)==AP01_HEAP_LIMIT);
    assert(client.call(AP01_HEAP_FREE,blocks[0]+1,0,result)==AP01_SERVICE_INVALID);
    assert(client.call(AP01_HEAP_FREE,0x1234,0,result)==AP01_SERVICE_INVALID);
    assert(client.call(AP01_HEAP_REALLOCATE,blocks[0],UINT32_MAX,result)==AP01_HEAP_LIMIT);
    assert(*(uint8_t *)(uintptr_t)blocks[0]==0x55);
    for(unsigned i=0;i<8;i+=2)assert(!client.call(AP01_HEAP_FREE,blocks[i],0,result));
    assert(client.call(AP01_HEAP_ALLOCATE,0,32,result)==AP01_HEAP_LIMIT);
    assert(client.call(AP01_HEAP_FREE,blocks[0],0,result)==AP01_SERVICE_INVALID);
    for(unsigned i=1;i<8;i+=2)assert(!client.call(AP01_HEAP_FREE,blocks[i],0,result));
    assert(!client.call(AP01_HEAP_ZERO_ALLOCATE,0,240,result));uint64_t whole=result;
    for(unsigned i=0;i<240;++i)assert(!((uint8_t *)(uintptr_t)whole)[i]);
    memset((void *)(uintptr_t)whole,0x42,240);
    assert(!client.call(AP01_HEAP_REALLOCATE,whole,32,result)&&result==whole);
    assert(!client.call(AP01_HEAP_REALLOCATE,whole,240,result)&&result==whole);
    for(unsigned i=0;i<32;++i)assert(((uint8_t *)(uintptr_t)whole)[i]==0x42);
    assert(!client.call(AP01_HEAP_REALLOCATE,whole,0,result)&&!result);
    assert(!client.call(AP01_HEAP_ALLOCATE,0,0,result)&&!result);
    assert(!client.call(AP01_HEAP_FREE,0,0,result));
    assert(gate.acquire(1));gate.close();assert(!heap.drain());gate.release();assert(heap.drain());
    for(unsigned i=0;i<256;++i)assert(memory[i]==0);
    assert(heap.bind(2,memory,1024));auto old=client;client.table=heap.table(gate.begin());
    assert(old.call(AP01_HEAP_ALLOCATE,0,16,result)==AP01_SERVICE_UNAVAILABLE);
    // Deterministic realloc/free stress checks every live payload before and
    // after changes, including fragmentation and failed growth.
    struct Live {uint64_t address=0;uint32_t size=0;uint8_t value=0;};std::array<Live,16> live{};
    uint32_t random=0x12345678;
    for(unsigned iteration=0;iteration<5000;++iteration){
        for(const auto &l:live)for(unsigned i=0;i<l.size;++i)assert(((uint8_t *)(uintptr_t)l.address)[i]==l.value);
        random=random*1664525+1013904223;auto &l=live[(random>>16)%live.size()];
        unsigned n=(random>>8)%301;
        int error=client.call(AP01_HEAP_REALLOCATE,l.address,n,result);
        if(error){assert(error==AP01_HEAP_LIMIT);continue;}
        for(unsigned i=0;i<n&&i<l.size;++i)assert(((uint8_t *)(uintptr_t)result)[i]==l.value);
        l={result,n,uint8_t(iteration)};if(n)memset((void *)(uintptr_t)result,l.value,n);
    }
    gate.close();assert(heap.drain()); // deliberately reclaim outstanding blocks
    for(unsigned i=0;i<1024;++i)assert(memory[i]==0);
    for(unsigned i=0;i<16;++i)assert(storage[i]==0xa5&&storage[1040+i]==0xa5);
    assert(heap.bind(3,memory,1024));client.table=heap.table(gate.begin());memory[12]^=1;
    assert(client.call(AP01_HEAP_ALLOCATE,0,1,result)==AP01_SERVICE_IO);
    gate.close();assert(!heap.drain()&&!heap.bind(4,memory,1024));
    {
        Ap01AppGeneration0041 g;Ap01AppHeap0041 h(g);assert(h.bind(1,memory,1024));
        Ap01AppCore0041 core(g,{});Ap01AppFiles0041 files(g,{},"/unused");
        Ap01AppServices0041 bus(core,files,nullptr,&h);Ap01AppHeapClientV2 client(bus.table(g.begin()));
        auto *p=(uint8_t *)client.zeroAllocate(8,8);assert(p);
        for(unsigned i=0;i<64;++i)assert(!p[i]);memset(p,0x63,64);
        assert(!client.zeroAllocate(SIZE_MAX,2));assert(!client.reallocate(p,UINT32_MAX));
        auto *q=(uint8_t *)client.reallocate(p,256);assert(q);
        for(unsigned i=0;i<64;++i)assert(q[i]==0x63);
        assert(client.free(q)&&!client.free(q)&&client.free(nullptr));
        assert(client.allocate(32));g.close();assert(!client.allocate(16)&&h.drain());
        assert(h.bind(2,nullptr,0));Ap01AppHeapClientV2 empty(bus.table(g.begin()));
        assert(!empty.allocate(1)&&!empty.allocate(0)&&empty.free(nullptr));g.close();assert(h.drain());
    }
    BusyService busy;ap01_app_services_v2 busyTable{2,sizeof(ap01_app_services_v2),1,0,AP01_APP_HEAP_CAPABILITY|AP01_APP_CORE_CAPABILITY,&busy,BusyService::invoke};
    Ap01AppHeapClientV2 waiting(busyTable);assert(!waiting.allocate(16)&&busy.attempts==1000&&busy.yields==1000);
    puts("heap service/client: exact/zero arena budgets, alignment, fragmentation/coalescing, 5000 realloc preservation checks, stale/interior/double free rejection, bounded Busy retries, lease drain, zeroing and corruption retention passed");
}
