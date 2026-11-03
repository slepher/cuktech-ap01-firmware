#pragma once
#include "app_abi_v2.h"
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
// App-private state, never linked into the resident platform. Called once by
// the file App start entry, before constructing any business C++ objects.
int ap01_app_runtime_bind_heap_v2(const ap01_app_services_v2 *services);
// Other private runtime modules use the same immutable App-local binding.
int32_t ap01_app_runtime_core_call_v2(uint32_t operation,void *output,uint32_t capacity);
void *ap01_app_malloc_v2(size_t bytes);
void *ap01_app_calloc_v2(size_t count,size_t bytes);
void *ap01_app_realloc_v2(void *old,size_t bytes);
int ap01_app_free_v2(void *old);
// An allocation can legitimately fail. Failed deallocation while running is
// a resource fault; stop-time frees after gate closure are reclaimed by drain.
int ap01_app_runtime_heap_fault_v2(void);
#ifdef __cplusplus
}
#endif
