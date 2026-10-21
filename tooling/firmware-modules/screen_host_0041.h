#ifndef AP01_SCREEN_HOST_0041_H
#define AP01_SCREEN_HOST_0041_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#define AP01_SCREEN_ABI_0041 1u
#define AP01_SCREEN_ID_BYTES 65u
/* Bounded transaction scratch space; actual slots are supplied by the caller. */
#define AP01_SCREEN_SET_LIMIT 32u
/* Includes a bounded 5s business HTTP request ahead of frame preparation. */
#define AP01_SCREEN_PREPARE_TIMEOUT_MS 10000u
enum { AP01_HOST_OK=0, AP01_HOST_INVALID=-1, AP01_HOST_BUSY=-2,
       AP01_HOST_STALE=-3, AP01_HOST_CAPACITY=-4, AP01_HOST_FAILED=-5 };
enum { AP01_ENTER_FAILED=-1, AP01_ENTER_PENDING=0, AP01_ENTER_READY=1 };
enum { AP01_INPUT_LEFT=1, AP01_INPUT_RIGHT, AP01_INPUT_SHORT, AP01_INPUT_ESCAPE };
enum { AP01_FOCUS_KEEP=0, AP01_FOCUS_LOCK=1, AP01_FOCUS_UNLOCK=2 };
typedef struct ap01_screen_slot ap01_screen_slot;
typedef struct ap01_screen_host ap01_screen_host;
typedef struct ap01_screen_app ap01_screen_app;
typedef struct ap01_screen_desc {
    uint32_t abi_version, struct_bytes;
    const char *screen_id;
    void *context;
    int (*prepare)(void *, ap01_screen_slot *, uint32_t transition);
    void (*entered)(void *, ap01_screen_slot *);
    void (*left)(void *, ap01_screen_slot *);
    void (*unbind)(void *, ap01_screen_slot *);
    int (*input)(void *, ap01_screen_slot *, unsigned event);
    unsigned visible;
} ap01_screen_desc;

struct ap01_screen_slot {
    void *root;
    unsigned child;
    char id[AP01_SCREEN_ID_BYTES];
    ap01_screen_desc desc;
    unsigned order,live;
};
struct ap01_screen_app {
    const char *app_id;
    ap01_screen_host *host;
    ap01_screen_slot *slots;
    unsigned capacity, count;
    uint32_t revision;
    void *context;
    void (*poll)(void *, uint32_t now_ms);
};
typedef struct ap01_screen_port {
    void *context;
    unsigned (*active)(void *);
    int (*idle)(void *);
    int (*available)(void *); /* main browser, awake, no system modal */
    void (*slide)(void *, unsigned child, unsigned direction);
    void (*native_edge)(void *, unsigned source, unsigned target);
} ap01_screen_port;
struct ap01_screen_host {
    ap01_screen_port port;
    ap01_screen_app *apps;
    unsigned app_count;
    ap01_screen_slot *source, *target;
    unsigned source_child, target_child, direction;
    uint32_t transition, deadline, input_revision, pressed_at;
    unsigned phase, locked, pressed, escaped,blocked;
};

int ap01_host_init(ap01_screen_host *, const ap01_screen_port *, ap01_screen_app *, unsigned);
int ap01_host_replace(ap01_screen_app *, uint32_t expected_revision,
                      const ap01_screen_desc *, unsigned count);
ap01_screen_slot *ap01_host_find(ap01_screen_app *, const char *id);
ap01_screen_slot *ap01_host_current(ap01_screen_host *);
int ap01_host_switch(ap01_screen_app *, const char *id, unsigned direction, uint32_t now_ms);
int ap01_host_enter_ready(ap01_screen_host *, uint32_t transition, int ready);
/* Returns 1 only if the host consumed this input; otherwise call stock handler. */
int ap01_host_rotate(ap01_screen_host *, int direction, uint32_t now_ms);
int ap01_host_short(ap01_screen_host *);
void ap01_host_button(ap01_screen_host *, int pressed, uint32_t now_ms);
void ap01_host_poll(ap01_screen_host *, uint32_t now_ms);
void ap01_host_cancel(ap01_screen_host *);
void ap01_host_set_blocked(ap01_screen_host *,int blocked);
int ap01_host_is_visible(ap01_screen_app *,const char *id);
void ap01_host_retire(ap01_screen_app *);
void ap01_host_destroy(ap01_screen_host *);
typedef struct ap01_host_api_0041 {
    uint32_t abi_version,struct_bytes;
    int (*replace_screen_set)(ap01_screen_app *,uint32_t,const ap01_screen_desc *,unsigned);
    ap01_screen_slot *(*find_screen)(ap01_screen_app *,const char *);
    int (*request_switch_to)(ap01_screen_app *,const char *,unsigned,uint32_t);
    int (*enter_ready)(ap01_screen_host *,uint32_t,int);
    int (*is_visible)(ap01_screen_app *,const char *);
} ap01_host_api_0041;
extern const ap01_host_api_0041 ap01_host_api;
#ifdef __cplusplus
}
#endif
#endif
