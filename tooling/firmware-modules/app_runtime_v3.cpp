#include "app_runtime_v3.h"
#include <stdlib.h>
#include <string.h>
#include <new>
#include <time.h>
namespace {const Ap01PlatformApiV3 *api;void *context;}
extern "C" int ap01BindRuntimeV3(const Ap01PlatformApiV3 *p,void *c){
    if(api||!p||!c||p->abi_major!=3||p->struct_bytes<sizeof(*p)||p->reserved||
       (p->capabilities&AP01_CODEX_CAPS_V3)!=AP01_CODEX_CAPS_V3||!p->private_root||
       !p->platform_build||!p->app_digest||!p->rom_bytes||
       !p->boot_id||!p->now_ms||!p->pause_ms||!p->random||!p->mac||!p->utc_seconds||
       !p->allocate||!p->reallocate||!p->release||!p->format||!p->errno_slot||!p->task_start||
       !p->busy||!p->writes_allowed||!p->bind)return -1;
    const auto &f=p->files;const auto &n=p->network;const auto &u=p->ui;
    if(!f.context||!f.prepare||!f.open||!f.close||!f.read||!f.write||!f.seek||!f.size||
       !f.exists||!f.mkdir||!f.remove||!f.rename||!f.statfs||!n.context||!n.listen||!n.accept||
       !n.close||!n.wait||!n.receive||!n.send||!n.receive_from||!n.send_to||!u.host||!u.app||
       !u.window||!u.lvgl||!u.screens||!u.attach||!u.current||!u.retire||!u.poll||!u.blocked||
       !u.cancel||!u.button||!u.rotate||!u.short_press||!u.active||!u.visible||!u.awake||!u.idle||
       !u.overlay||!u.activity||!u.wake||!u.event_code||!u.event_key||!u.event_context||!u.event_target)return -1;
    if(u.lvgl->abi_version!=1||u.lvgl->struct_bytes<sizeof(*u.lvgl)||
       u.screens->abi_version!=1||u.screens->struct_bytes<sizeof(*u.screens))return -1;
    const auto &l=*u.lvgl;const auto &h=*u.screens;
    if(!u.window->win||!u.window->stock||!l.obj_create||!l.obj_delete||!l.obj_size||!l.obj_align||
       !l.obj_hide||!l.label||!l.i4_present||!l.i4_retire||!l.on_draw||!l.label_text||
       !l.background||!l.text_color||!l.text_font||!h.replace_screen_set||!h.find_screen||
       !h.request_switch_to||!h.enter_ready||!h.is_visible)return -1;
    context=c;api=p;return 0;
}
extern "C" const Ap01PlatformApiV3 *ap01RuntimeApiV3(){return api;}
extern "C" void *ap01RuntimeContextV3(){return context;}
extern "C" {
void *malloc(size_t n) noexcept {return api&&n<=UINT32_MAX?api->allocate(context,uint32_t(n)):nullptr;}
void free(void *p) noexcept {if(api&&p)api->release(context,p);}
void *realloc(void *p,size_t n) noexcept {return api&&n<=UINT32_MAX?api->reallocate(context,p,uint32_t(n)):nullptr;}
void *calloc(size_t count,size_t size) noexcept {
    if(count&&size>SIZE_MAX/count)return nullptr;
    size_t n=count*size;void *p=malloc(n);if(p)memset(p,0,n);return p;
}
time_t time(time_t *out) noexcept {
    int64_t seconds=api?api->utc_seconds(context):-1;
    time_t value=seconds<0||seconds>INT32_MAX?time_t(-1):time_t(seconds);
    if(out)*out=value;
    return value;
}
int *__errno(){return api?api->errno_slot(context):nullptr;}
}
namespace std {const nothrow_t nothrow{};}
void *operator new(size_t n,const std::nothrow_t &) noexcept {return malloc(n);}
void *operator new[](size_t n,const std::nothrow_t &) noexcept {return malloc(n);}
void operator delete(void *p) noexcept {free(p);}
void operator delete[](void *p) noexcept {free(p);}
void operator delete(void *p,size_t) noexcept {free(p);}
void operator delete[](void *p,size_t) noexcept {free(p);}
