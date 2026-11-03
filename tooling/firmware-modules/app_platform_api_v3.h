#ifndef AP01_APP_PLATFORM_API_V3_H
#define AP01_APP_PLATFORM_API_V3_H
#include "app_abi_v3.h"
#include "native_vfs_api_0041.h"
#include "app_network_api_v3.h"
#include "screen_port_0041.h"
#ifdef __cplusplus
extern "C" {
#endif

/* Request strings/body are borrowed for pairing(); reply bytes are borrowed
 * only during emit(). The platform copies them before emit returns. */
typedef struct Ap01HttpRequestV3 {
    const char *method,*path,*token,*device_token,*content_type;
    const char *request_id,*offset,*nonce;
    const uint8_t *body;uint32_t length;
    const char *chunk_sha256,*device_mac;
} Ap01HttpRequestV3;
typedef int32_t (*Ap01ReplyV3)(void *,uint32_t status,const uint8_t *,uint32_t);
typedef struct Ap01AppBindingV3 {
    void *context;
    int32_t (*principal)(void *,const char *,char out[65]);
    int32_t (*pairing)(void *,const Ap01HttpRequestV3 *,uint64_t,Ap01ReplyV3,void *);
    int32_t (*online)(void *);
} Ap01AppBindingV3;

/* The platform owns the sole host/window and assigns one registry slot.
 * These are frozen public C layouts, not C++ private objects. App may read host
 * state on the UI executor; mutation goes through the functions below.
 * All UI calls/callbacks execute on that same executor. Slots/pages/pixels are
 * App-owned and stay alive while registered; attach copies callback pointers.
 */
typedef struct Ap01UiV3 {
    ap01_screen_host *host;ap01_screen_app *app;ap01_window_0041 *window;
    const ap01_lvgl_api_0041 *lvgl;
    const ap01_host_api_0041 *screens;
    int32_t (*attach)(void *app_context,void *instance,ap01_screen_slot *,ap01_page_0041 *,uint32_t,
                      void (*poll)(void *,uint32_t),void (*tick)(void *),void (*event)(void *,void *));
    ap01_screen_slot *(*current)(ap01_screen_host *);
    void (*retire)(ap01_screen_app *);
    void (*poll)(ap01_screen_host *,uint32_t);
    void (*blocked)(ap01_screen_host *,int);
    void (*cancel)(ap01_screen_host *);
    void (*button)(ap01_screen_host *,int,uint32_t);
    int (*rotate)(ap01_screen_host *,int,uint32_t);
    int (*short_press)(ap01_screen_host *);
    unsigned (*active)(ap01_window_0041 *);
    int (*visible)(ap01_window_0041 *),(*awake)(ap01_window_0041 *),(*idle)(ap01_window_0041 *);
    void *(*overlay)(ap01_window_0041 *);
    void (*activity)(void),(*wake)(void);
    unsigned (*event_code)(void *),(*event_key)(void *);
    void *(*event_context)(void *),*(*event_target)(void *);
} Ap01UiV3;

#define AP01_CAP_CORE_V3 UINT64_C(1)
#define AP01_CAP_FILES_V3 UINT64_C(2)
#define AP01_CAP_NETWORK_V3 UINT64_C(4)
#define AP01_CAP_MEMORY_V3 UINT64_C(8)
#define AP01_CAP_UI_V3 UINT64_C(16)
#define AP01_CAP_TASKS_V3 UINT64_C(32)
#define AP01_CAP_BINDING_V3 UINT64_C(64)
#define AP01_CODEX_CAPS_V3 UINT64_C(127)

/* ABI 3.0 frozen RV32 layout; append-only compatible minor revisions. The platform reserves budgets before publishing this table.
 * One immutable table/context per loaded image, lifetime until reboot.
 * allocate/reallocate/release are thread-safe quota wrappers; never UI-wait.
 * task_start is worker-only execution of entry, not an inline call.
 * bind copies binding once; maintenance already exists independently.
 * format uses the frozen RV32 ILP32F varargs ABI and standard snprintf result.
 */
struct Ap01PlatformApiV3 {
    uint32_t abi_major,abi_minor,struct_bytes,reserved;
    uint64_t capabilities,boot_id;
    const char *private_root;
    const char *platform_build,*app_digest;
    uint32_t rom_bytes;
    uint64_t (*now_ms)(void *);
    void (*pause_ms)(void *,uint32_t);
    int32_t (*random)(void *,uint8_t *,uint32_t);
    int32_t (*mac)(void *,char out[13]);
    int64_t (*utc_seconds)(void *);
    void *(*allocate)(void *,uint32_t);
    void *(*reallocate)(void *,void *,uint32_t);
    void (*release)(void *,void *);
    int (*format)(char *,size_t,const char *,...);
    int *(*errno_slot)(void *);
    int32_t (*task_start)(void *,const char *,void *(*)(void *),uint32_t,void *);
    int32_t (*busy)(void *);
    int32_t (*writes_allowed)(void *);
    int32_t (*bind)(void *,const Ap01AppBindingV3 *);
    Ap01VfsOps files;
    Ap01NetworkOpsV3 network;
    Ap01UiV3 ui;
};

#ifdef __cplusplus
}
#endif
#if defined(__riscv) && __riscv_xlen == 32
#ifdef __cplusplus
#define AP01_ABI_ASSERT_V3 static_assert
#else
#define AP01_ABI_ASSERT_V3 _Static_assert
#endif
AP01_ABI_ASSERT_V3(sizeof(Ap01PlatformApiV3)==296,"ABI 3 platform layout");
AP01_ABI_ASSERT_V3(sizeof(Ap01UiV3)==100,"ABI 3 UI layout");
AP01_ABI_ASSERT_V3(sizeof(Ap01AppBindingV3)==16,"ABI 3 binding layout");
AP01_ABI_ASSERT_V3(sizeof(Ap01HttpRequestV3)==48,"ABI 3 HTTP layout");
AP01_ABI_ASSERT_V3(sizeof(Ap01VfsOps)==52,"ABI 3 file layout");
AP01_ABI_ASSERT_V3(sizeof(Ap01NetworkOpsV3)==36,"ABI 3 network layout");
#undef AP01_ABI_ASSERT_V3
#endif
#endif
