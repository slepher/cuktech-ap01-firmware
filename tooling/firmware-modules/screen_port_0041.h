#ifndef AP01_SCREEN_PORT_0041_H
#define AP01_SCREEN_PORT_0041_H
#include "screen_host_0041.h"

typedef struct ap01_page_tag_0041 {uint32_t kind;void *state;uint32_t reserved[3];} ap01_page_tag_0041;
typedef struct ap01_image_header_0041 {uint8_t magic,format;uint16_t flags,width,height,stride,reserved;} ap01_image_header_0041;
typedef struct ap01_image_0041 {ap01_image_header_0041 header;uint32_t size;const uint8_t *data;const void *reserved;} ap01_image_0041;
typedef struct ap01_surface_0041 {
    void *image;
    uint8_t *bytes;
    ap01_image_0041 descriptor;
    uint32_t generation;
    void (*drawn)(void *event);
    void *draw_context;
} ap01_surface_0041;
typedef struct ap01_page_0041 {
    ap01_page_tag_0041 tag;
    ap01_surface_0041 surface;
} ap01_page_0041;
typedef struct ap01_window_0041 {
    void *win;
    void (*stock)(void *);
    void *context;
    void (*event)(void *,void *);
    void (*poll)(void *);
    void *timer;
    void *services; /* Firmware service, retained with this lifetime anchor. */
} ap01_window_0041;
typedef struct ap01_lvgl_api_0041 {
    uint32_t abi_version,struct_bytes;
    void *(*obj_create)(void *parent);
    void (*obj_delete)(void *obj);
    void (*obj_size)(void *obj,int width,int height);
    void (*obj_align)(void *obj,unsigned align,int x,int y);
    void (*obj_hide)(void *obj,int hidden);
    void *(*label)(void *parent,const char *text,int x,int y);
    int (*i4_present)(ap01_surface_0041 *,void *parent,const uint8_t *,const uint16_t *,uint32_t,void (*)(void *),void *);
    void (*i4_retire)(ap01_surface_0041 *);
    void (*on_draw)(void *obj,void (*callback)(void *),void *context);
    void (*label_text)(void *,const char *);
    void (*background)(void *,uint32_t);
    void (*text_color)(void *,uint32_t);
    void (*text_font)(void *,const void *);
} ap01_lvgl_api_0041;

#ifdef __cplusplus
extern "C" {
#endif
extern const ap01_lvgl_api_0041 ap01_lvgl_0041;
int ap01_window_mount(ap01_window_0041 *,ap01_screen_slot *,ap01_page_0041 *,unsigned count);
void ap01_window_unmount(ap01_screen_slot *,ap01_page_0041 *,unsigned count);
int ap01_window_bind(ap01_window_0041 *);
/* UI-thread only: the retained timer is the lifetime anchor across win deletion. */
void *ap01_window_find(void (*poll)(void *));
void *ap01_window_services(void);
void ap01_window_detach(ap01_window_0041 *);
unsigned ap01_window_binding_count(void *win);
void ap01_window_unbind(ap01_window_0041 *);
ap01_screen_port ap01_window_port(ap01_window_0041 *);
unsigned ap01_window_active(ap01_window_0041 *);
int ap01_window_visible(ap01_window_0041 *);
int ap01_window_awake(ap01_window_0041 *);
int ap01_window_idle(ap01_window_0041 *);
void ap01_window_activity(void);
void ap01_window_wake(void);
void *ap01_window_child(ap01_window_0041 *,unsigned index);
unsigned ap01_event_code(void *event);
unsigned ap01_event_key(void *event);
void *ap01_event_context(void *event);
void *ap01_event_target(void *event);
/* Overlay is a child of the active page, never a new screen-level window. */
void *ap01_window_overlay(ap01_window_0041 *);
#ifdef __cplusplus
}
#endif
#endif
