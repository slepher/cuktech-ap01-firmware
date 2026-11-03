#ifndef AP01_APP_ABI_V2_H
#define AP01_APP_ABI_V2_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define AP01_APP_ABI_V2 2u
// All buffers are borrowed for the call only. No C++ objects/exceptions cross
// this boundary. Resource handles returned by services belong to generation.
typedef struct ap01_app_services_v2 {
    uint32_t abi_version,struct_bytes,generation,reserved;
    uint64_t available_services;
    void *context;
    int32_t (*invoke)(void *context,uint32_t generation,uint32_t service,uint32_t operation,
                      const void *input,uint32_t input_bytes,void *output,uint32_t capacity,uint32_t *written);
} ap01_app_services_v2;
typedef struct ap01_app_event_v2 {
    uint32_t struct_bytes,kind,resource,flags;
    const void *bytes;
    uint32_t length;
} ap01_app_event_v2;
typedef struct ap01_app_health_v2 {
    uint32_t struct_bytes,entry_ready,resource_fault,reserved;
} ap01_app_health_v2;
// APX2 offsets 88..104 correspond exactly to these five signatures.
// Start sets state even on failure if stop must dispose partial initialization.
// prepare_stop: 0 ready, 1 still cancelling, negative irrecoverable stop failure.
// stop: 0 has disposed App state, nonzero retains code/state for controlled reboot.
// App service state, buffers and handles are released by their allocating side.
typedef struct ap01_app_entries_v2 {
    int32_t (*start)(const ap01_app_services_v2 *,void **state);
    int32_t (*event)(void *state,const ap01_app_event_v2 *);
    int32_t (*prepare_stop)(void *state);
    int32_t (*stop)(void *state);
    int32_t (*health)(void *state,ap01_app_health_v2 *);
} ap01_app_entries_v2;
#ifdef __cplusplus
}
#if defined(__riscv)
static_assert(sizeof(void *)==4&&sizeof(ap01_app_services_v2)==32,"APX2 ILP32 service layout");
static_assert(sizeof(ap01_app_event_v2)==24&&sizeof(ap01_app_entries_v2)==20,"APX2 ILP32 event/entry layout");
#endif
#endif

#endif
