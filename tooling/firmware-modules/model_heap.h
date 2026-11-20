#pragma once
#include <stdint.h>
#include <atomic>
// QEMU-only arena, not an App service or production allocator.
class Ap01ModelHeap {
    struct Block {uint32_t span,used,requested,magic;};
    uint8_t *arena=nullptr;uint32_t capacity=0;
    std::atomic_flag lock=ATOMIC_FLAG_INIT;
    bool failed=false;
    Block read(uint32_t) const;
    void write(uint32_t,const Block &);
    bool valid();
    uint32_t find(uint64_t) const;
    void *claim(uint32_t,uint32_t,uint32_t);
    void *allocate(uint32_t);
    void free(uint32_t);
public:
    bool bind(void *,uint32_t);
    void *reallocate(void *,uint32_t);
};
