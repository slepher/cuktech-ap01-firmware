#include "app_heap_0041.h"
#include <string.h>
static_assert(sizeof(ap01_app_heap_request_v2)==16,"heap C ABI");
namespace {
constexpr uint32_t magic=0x48415032;
struct Unlock {std::atomic_flag &lock;~Unlock(){lock.clear(std::memory_order_release);}};
uint64_t needed(uint32_t bytes){return (uint64_t(bytes)+31)&~uint64_t(15);}
}
Ap01AppHeap0041::Block Ap01AppHeap0041::read(uint32_t at) const {Block b;memcpy(&b,arena+at,16);return b;}
void Ap01AppHeap0041::write(uint32_t at,const Block &b){memcpy(arena+at,&b,16);}
bool Ap01AppHeap0041::bind(uint32_t next,void *memory,uint32_t bytes){
    if(lock.test_and_set(std::memory_order_acquire))return false;
    Unlock unlock{lock};uintptr_t address=(uintptr_t)memory;
    if(failed||generation||!gate.drained()||gate.current()==UINT32_MAX||next!=gate.current()+1||
       (bytes&&(!memory||bytes<32))||(address&15)||(bytes&15)||bytes>UINTPTR_MAX-address)return false;
    arena=(uint8_t *)memory;capacity=bytes;generation=next;
    if(bytes){memset(arena,0,bytes);write(0,{bytes,0,0,magic});}return true;
}
bool Ap01AppHeap0041::valid(){
    for(uint32_t at=0;at<capacity;){
        if(capacity-at<32){failed=true;return false;}
        Block b=read(at);
        if(b.magic!=magic||b.span<32||(b.span&15)||b.span>capacity-at||b.used>1||
           (!b.used&&b.requested)||(b.used&&(!b.requested||b.requested>b.span-16))){failed=true;return false;}
        at+=b.span;
    }
    return true;
}
uint32_t Ap01AppHeap0041::find(uint64_t address) const {
    for(uint32_t at=0;at<capacity;){Block b=read(at);
        if(b.used&&address==uint64_t((uintptr_t)(arena+at+16)))return at;
        at+=b.span;
    }return UINT32_MAX;
}
void *Ap01AppHeap0041::claim(uint32_t at,uint32_t span,uint32_t bytes){
    uint32_t take=uint32_t(needed(bytes));
    if(span-take>=32)write(at+take,{span-take,0,0,magic});else take=span;
    write(at,{take,1,bytes,magic});return arena+at+16;
}
void *Ap01AppHeap0041::allocate(uint32_t bytes){
    // ponytail: linear first-fit scan; use a bounded segregated free list only
    // if measured App allocation latency exceeds the executor's budget.
    for(uint32_t at=0;at<capacity;){Block b=read(at);
        if(!b.used&&b.span>=needed(bytes))return claim(at,b.span,bytes);
        at+=b.span;
    }return nullptr;
}
void Ap01AppHeap0041::free(uint32_t at){
    Block b=read(at);write(at,{b.span,0,0,magic});
    for(uint32_t pos=0;pos<capacity;){b=read(pos);
        if(!b.used&&pos+b.span<capacity){Block next=read(pos+b.span);
            if(!next.used){b.span+=next.span;write(pos,b);continue;}
        }pos+=b.span;
    }
}
bool Ap01AppHeap0041::drain(){
    if(lock.test_and_set(std::memory_order_acquire))return false;
    Unlock unlock{lock};if(failed||!gate.drained()||!valid())return false;
    if(capacity)memset(arena,0,capacity);
    arena=nullptr;capacity=generation=0;return true;
}
int32_t Ap01AppHeap0041::invoke(void *context,uint32_t g,uint32_t service,uint32_t op,
        const void *input,uint32_t length,void *output,uint32_t outCapacity,uint32_t *written){
    if(!written)return AP01_SERVICE_INVALID;
    *written=0;
    if(!context||service!=AP01_APP_SERVICE_HEAP||!input||length!=16||op<1||op>4||
       outCapacity!=(op==AP01_HEAP_FREE?0u:8u)||(outCapacity&&!output))return AP01_SERVICE_INVALID;
    auto &self=*(Ap01AppHeap0041 *)context;Ap01AppLease0041 lease(self.gate,g);
    if(!lease)return AP01_SERVICE_UNAVAILABLE;
    if(self.lock.test_and_set(std::memory_order_acquire))return AP01_HEAP_BUSY;
    Unlock unlock{self.lock};if(self.failed||self.generation!=g)return AP01_SERVICE_UNAVAILABLE;
    ap01_app_heap_request_v2 r;memcpy(&r,input,16);
    if(r.reserved||r.address>UINTPTR_MAX||(op<AP01_HEAP_REALLOCATE&&r.address)||
       (op==AP01_HEAP_FREE&&r.bytes))return AP01_SERVICE_INVALID;
    if(!self.valid())return AP01_SERVICE_IO;
    uint32_t at=r.address?self.find(r.address):UINT32_MAX;
    if(r.address&&at==UINT32_MAX)return AP01_SERVICE_INVALID;
    if(op==AP01_HEAP_FREE){if(r.address)self.free(at);return AP01_SERVICE_OK;}
    void *result=nullptr;
    if(!r.bytes){if(r.address)self.free(at);}
    else if(r.address){
        Block old=self.read(at);
        uint32_t available=old.span;
        if(at+available<self.capacity){Block next=self.read(at+available);if(!next.used)available+=next.span;}
        if(needed(r.bytes)<=available)result=self.claim(at,available,r.bytes);
        else{
            result=self.allocate(r.bytes);
            if(result){memcpy(result,self.arena+at+16,old.requested);self.free(at);}
        }
    }else result=self.allocate(r.bytes);
    if(r.bytes&&!result)return AP01_HEAP_LIMIT;
    if(op==AP01_HEAP_ZERO_ALLOCATE&&result)memset(result,0,r.bytes);
    uint64_t address=uint64_t((uintptr_t)result);memcpy(output,&address,8);*written=8;return AP01_SERVICE_OK;
}
