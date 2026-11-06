#include "native_rom_addresses.h"
// Freestanding support for the frozen RV32/ilp32f 0041 imports. All mutable
// allocations carry their length and are owned by the application, not XIP.
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <new>
#include <time.h>
#include <stdio.h>
#define ROM_FN(address,type) ((type)(uintptr_t)(address))
extern "C" {
void *malloc(size_t n) noexcept {
    if (n > SIZE_MAX-8) return nullptr;
    uint32_t *p = ROM_FN(AP01_ROM_ADDR(0xa002fcc8), uint32_t *(*)(size_t))(n+8);
    if (!p) return nullptr;
    p[0] = n; p[1] = 0x4130314d; return p+2;
}
void free(void *p) noexcept {
    if (p) ROM_FN(AP01_ROM_ADDR(0xa002e14e), void (*)(void *))((uint32_t *)p-2);
}
void *realloc(void *p, size_t n) noexcept {
    if (!p) return malloc(n);
    if (!n) { free(p); return nullptr; }
    size_t old = ((uint32_t *)p)[-2];
    if (n <= old) return p;
    void *next = malloc(n); if (!next) return nullptr;
    memcpy(next, p, old); free(p); return next;
}
void *calloc(size_t count,size_t n) noexcept {
    if (count && n > SIZE_MAX/count) return nullptr;
    n *= count; void *p = malloc(n); if (p) memset(p,0,n); return p;
}
// Newlib's libm may set errno. Use the running NuttX thread's real errno slot.
int *__errno() { return ROM_FN(AP01_ROM_ADDR(0xa00267c0),int *(*)())(); }
time_t time(time_t *out) noexcept {
    int32_t value=ROM_FN(AP01_ROM_ADDR(0xa019fc3e),int32_t (*)())();
    // The AP01 RTC stores Hong Kong civil seconds. Shared rendering expects
    // UTC epochs, including device.date; timestamp fields are already UTC.
    if(value>=8*60*60)value-=8*60*60;
    if(out)*out=value;return value;
}

}
namespace std { const nothrow_t nothrow{}; }
void *operator new(size_t n,const std::nothrow_t &) noexcept { return malloc(n); }
void *operator new[](size_t n,const std::nothrow_t &) noexcept { return malloc(n); }
void operator delete(void *p) noexcept {free(p);}
void operator delete[](void *p) noexcept {free(p);}
void operator delete(void *p,size_t) noexcept {free(p);}
void operator delete[](void *p,size_t) noexcept {free(p);}
