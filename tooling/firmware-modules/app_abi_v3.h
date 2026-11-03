#ifndef AP01_APP_ABI_V3_H
#define AP01_APP_ABI_V3_H
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* RV32IM AFC / ILP32F, little endian. No C++ objects cross this boundary.
 * API/context/instance and every published callback remain valid until reboot.
 * Start/event execute on the platform UI executor, must return without waiting
 * for I/O, and must not recursively dispatch events. Health is a nonblocking
 * snapshot callable by the supervisor concurrently with App work.
 * A failed start may already have published callbacks: never free its image.
 */
#define AP01_APP_ABI_MAJOR_V3 3u
#define AP01_APP_ABI_MINOR_V3 0u
enum {
    AP01_APP_V3_OK = 0,
    AP01_APP_V3_PENDING = 1,
    AP01_APP_V3_INVALID = -1,
    AP01_APP_V3_UNSUPPORTED = -2,
    AP01_APP_V3_RESOURCE = -3,
    AP01_APP_V3_FAILED = -4
};
enum {
    AP01_APP_V3_ENTRY_START = 0,
    AP01_APP_V3_ENTRY_EVENT = 1,
    AP01_APP_V3_ENTRY_HEALTH = 2,
    AP01_APP_V3_ENTRY_COUNT = 3
};

/* Frozen table definition is in app_platform_api_v3.h. */
typedef struct Ap01PlatformApiV3 Ap01PlatformApiV3;
typedef int32_t (*Ap01AppStartV3)(const Ap01PlatformApiV3 *api,
                                void *app_context, void **out_instance);
/* Payload is borrowed for this call; retain only an App-owned copy. Event IDs
 * for ABI 3.0: 1=tick (null/0), 2=native UI event (borrowed pointer/0),
 * 3=window rebound (null/0, platform window already bound). UI capability required.
 * An App with no event handling still supplies a no-op entry returning OK.
 */
typedef int32_t (*Ap01AppEventV3)(void *instance, uint32_t event,
                                const void *payload, uint32_t payload_bytes);
/* OK = ready/healthy, PENDING = starting, negative = failed. */
typedef int32_t (*Ap01AppHealthV3)(void *instance);

#ifdef __cplusplus
}
#endif
#endif
