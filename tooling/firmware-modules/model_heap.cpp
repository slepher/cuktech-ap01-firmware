#include "model_heap.h"
#include <string.h>
namespace {
constexpr uint32_t magic=0x48415032;
struct Unlock {std::atomic_flag &lock;~Unlock(){lock.clear(std::memory_order_release);}};
uint64_t needed(uint32_t bytes){return (uint64_t(bytes)+31)&~uint64_t(15);}
}
Ap01ModelHeap::Block Ap01ModelHeap::read(uint32_t at) const {Block b;memcpy(&b,arena+at,16);return b;}
void Ap01ModelHeap::write(uint32_t at,const Block &b){memcpy(arena+at,&b,16);}
bool Ap01ModelHeap::bind(void *memory,uint32_t bytes){
    if(lock.test_and_set(std::memory_order_acquire))return false;
    Unlock unlock{lock};uintptr_t address=(uintptr_t)memory;
    if(failed||arena||
       (bytes&&(!memory||bytes<32))||(address&15)||(bytes&15)||bytes>UINTPTR_MAX-address)return false;
    arena=(uint8_t *)memory;capacity=bytes;
    if(bytes){memset(arena,0,bytes);write(0,{bytes,0,0,magic});}return true;
}
bool Ap01ModelHeap::valid(){
    for(uint32_t at=0;at<capacity;){
        if(capacity-at<32){failed=true;return false;}
        Block b=read(at);
        if(b.magic!=magic||b.span<32||(b.span&15)||b.span>capacity-at||b.used>1||
           (!b.used&&b.requested)||(b.used&&(!b.requested||b.requested>b.span-16))){failed=true;return false;}
        at+=b.span;
    }
    return true;
}
uint32_t Ap01ModelHeap::find(uint64_t address) const {
    for(uint32_t at=0;at<capacity;){Block b=read(at);
        if(b.used&&address==uint64_t((uintptr_t)(arena+at+16)))return at;
        at+=b.span;
    }return UINT32_MAX;
}
void *Ap01ModelHeap::claim(uint32_t at,uint32_t span,uint32_t bytes){
    uint32_t take=uint32_t(needed(bytes));
    if(span-take>=32)write(at+take,{span-take,0,0,magic});else take=span;
    write(at,{take,1,bytes,magic});return arena+at+16;
}
void *Ap01ModelHeap::allocate(uint32_t bytes){
    // ponytail: linear first-fit scan; use a bounded segregated free list only
    // if measured App allocation latency exceeds the executor's budget.
    for(uint32_t at=0;at<capacity;){Block b=read(at);
        if(!b.used&&b.span>=needed(bytes))return claim(at,b.span,bytes);
        at+=b.span;
    }return nullptr;
}
void Ap01ModelHeap::free(uint32_t at){
    Block b=read(at);write(at,{b.span,0,0,magic});
    for(uint32_t pos=0;pos<capacity;){b=read(pos);
        if(!b.used&&pos+b.span<capacity){Block next=read(pos+b.span);
            if(!next.used){b.span+=next.span;write(pos,b);continue;}
        }pos+=b.span;
    }
}
void *Ap01ModelHeap::reallocate(void *pointer,uint32_t bytes){
    if(lock.test_and_set(std::memory_order_acquire))return nullptr;
    Unlock unlock{lock};if(failed||!valid())return nullptr;
    uint32_t at=pointer?find(uintptr_t(pointer)):UINT32_MAX;
    if(pointer&&at==UINT32_MAX)__builtin_trap();
    if(!bytes){if(pointer)free(at);return nullptr;}
    if(!pointer)return allocate(bytes);
    Block old=read(at);uint32_t available=old.span;
    if(at+available<capacity){Block next=read(at+available);if(!next.used)available+=next.span;}
    if(needed(bytes)<=available)return claim(at,available,bytes);
    void *result=allocate(bytes);
    if(result){memcpy(result,arena+at+16,old.requested);free(at);}
    return result;
}
