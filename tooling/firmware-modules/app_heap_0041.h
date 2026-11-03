#pragma once
#include "app_heap_abi_v2.h"
#include "app_generation_0041.h"
// Firmware-owned allocator over an exclusive, pre-reserved data arena. All
// headers/padding are inside heap_bytes; it never falls back to platform malloc.
// This is budget/lifetime management, not memory isolation from App corruption.
class Ap01AppHeap0041 {
    struct Block {uint32_t span,used,requested,magic;};
    Ap01AppGeneration0041 &gate;
    uint8_t *arena=nullptr;uint32_t capacity=0,generation=0;
    std::atomic_flag lock=ATOMIC_FLAG_INIT;
    bool failed=false;
    Block read(uint32_t at) const;
    void write(uint32_t at,const Block &);
    bool valid();
    uint32_t find(uint64_t address) const;
    void *claim(uint32_t at,uint32_t span,uint32_t bytes);
    void *allocate(uint32_t bytes);
    void free(uint32_t at);
    static int32_t invoke(void *,uint32_t,uint32_t,uint32_t,const void *,uint32_t,void *,uint32_t,uint32_t *);
public:
    explicit Ap01AppHeap0041(Ap01AppGeneration0041 &g):gate(g){}
    // Executor-only, before gate.begin. Memory is 16-byte aligned and exclusive
    // until drain; capacity is the package's declared heap budget, not more.
    bool bind(uint32_t nextGeneration,void *memory,uint32_t bytes);
    bool drain(); // closed gate + no leases; corruption requires controlled reboot
    ap01_app_services_v2 table(uint32_t g){return {2,sizeof(ap01_app_services_v2),g,0,AP01_APP_HEAP_CAPABILITY,this,invoke};}
};
