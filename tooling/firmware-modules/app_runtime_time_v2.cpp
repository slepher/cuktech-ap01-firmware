// File-App private time entry. Resident firmware retains its own RTC adapter.
#include "app_runtime_heap_v2.h"
#include "app_core_abi_v2.h"
#include <time.h>
#if defined(__riscv)
static_assert(sizeof(time_t)==4,"File App keeps the signed 32-bit time ABI");
#endif
extern "C" time_t ap01_app_time_v2(time_t *out) noexcept {
    uint64_t seconds=0;time_t value=time_t(-1);
    if(!ap01_app_runtime_core_call_v2(AP01_CORE_UTC_SECONDS,&seconds,sizeof(seconds))&&seconds<=INT32_MAX)value=time_t(seconds);
    if(out)*out=value;
    return value;
}
#ifndef AP01_RUNTIME_HEAP_HOST_TEST
extern "C" time_t time(time_t *out) noexcept {return ap01_app_time_v2(out);}
#endif
