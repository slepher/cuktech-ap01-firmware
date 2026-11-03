#ifndef AP01_APP_HEAP_ABI_V2_H
#define AP01_APP_HEAP_ABI_V2_H
#include "app_core_abi_v2.h"
#define AP01_APP_SERVICE_HEAP 4u
#define AP01_APP_HEAP_CAPABILITY UINT64_C(8)
enum {AP01_HEAP_ALLOCATE=1,AP01_HEAP_ZERO_ALLOCATE,AP01_HEAP_REALLOCATE,AP01_HEAP_FREE};
enum {AP01_HEAP_BUSY=-4,AP01_HEAP_LIMIT=-6};
// Address is an unsigned fixed-width integer, never a serialized C++ pointer.
// RV32 requires the upper 32 bits to be zero. Host verification can use native
// addresses; every input is matched against this generation's allocation list.
// ALLOCATE/ZERO_ALLOCATE require address=0. FREE requires bytes=0, no output.
// Others output uint64 address; zero-size allocation returns zero. Realloc
// failure preserves the old allocation. Realloc(address,0) frees it.
typedef struct ap01_app_heap_request_v2 {uint64_t address;uint32_t bytes,reserved;} ap01_app_heap_request_v2;
#endif
