#include "native_exec_memory_v3.h"

bool Ap01NativeExecMemoryV3::reserve(void *p,const Apx2View &v,Ap01BootMemoryV3 &out){
    auto &s=*(Ap01NativeExecMemoryV3 *)p;
    uint64_t bytes=uint64_t(v.image_bytes)+v.bss_bytes;
    if(v.abi_major!=3||!bytes||bytes+15>s.limit-s.used||s.count==8||!s.allocate||!s.release)return false;
    uint32_t charged=uint32_t(bytes)+15;
    void *raw=s.allocate(charged);if(!raw)return false;
    uintptr_t address=uintptr_t(raw);
    // The fixed ROM heap includes smaller SRAM regions as well. Only admit
    // the reviewed 4 MiB external RAM mapping, never an arbitrary malloc result.
    if(address<0xa8000000u||address>=0xa8400000u||charged>0xa8400000u-address){s.release(raw);return false;}
    uint32_t base=(uint32_t(address)+15)&~15u;
    s.images[s.count++]={base,uint32_t(bytes),false};s.used+=charged;
    out={(uint8_t *)uintptr_t(base),uint32_t(bytes),base};return true;
}
bool Ap01NativeExecMemoryV3::publish(void *p,const Ap01BootMemoryV3 &m,const Apx2View &v,Ap01AppEntriesV3 &out){
    auto &s=*(Ap01NativeExecMemoryV3 *)p;
    if(v.abi_major!=3||uintptr_t(m.bytes)!=m.base||!v.text_bytes||v.text_bytes>v.image_bytes||
       uint64_t(v.image_bytes)+v.bss_bytes!=m.capacity)return false;
    for(unsigned i=0;i<3;++i)if((v.entries[i]&1)||uint64_t(v.entries[i])+2>v.text_bytes)return false;
    for(unsigned i=0;i<s.count;++i){auto &image=s.images[i];
        if(image.base!=m.base||image.bytes!=m.capacity||image.published)continue;
#if defined(__riscv) && __riscv_xlen == 32
        // Fixed 0041 ROM 0xa0029db2..0xa0029dce: clean D-cache (not
        // invalidate/discard), invalidate I-cache, then synchronize fetch.
        // Raw encodings keep the existing rv32imafc toolchain contract.
        asm volatile("fence\n.word 0x0010000b\nfence\nfence\n.word 0x0000100f\n"
                     ".word 0x0100000b\nfence\n.word 0x0000100f":::"memory");
        out={(Ap01AppStartV3)(m.base+v.entries[0]),(Ap01AppEventV3)(m.base+v.entries[1]),
             (Ap01AppHealthV3)(m.base+v.entries[2])};
        image.published=true;return true;
#else
        (void)out;return false; // Host policy tests never execute RV32 memory.
#endif
    }
    return false;
}
