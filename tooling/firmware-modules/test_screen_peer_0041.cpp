#include "test_screen_peer_0041.h"
#include <new>
#include <string.h>

static void drawn(void *event) {
    auto *p=(ap01_test_peer_0041 *)ap01_event_context(event);
    ++p->drawEvents;
    auto *s=ap01_host_current(p->app->host);
    for(unsigned i=0;i<2;++i)if(ap01_event_target(event)==p->pages[i].surface.image) {
        ++p->matchedEvents;
        if(s==&p->slots[i]&&ap01_host_api.is_visible(p->app,s->id))++p->draws;
    }
}
static void release(void *ctx,ap01_screen_slot *slot) {
    auto *p=(ap01_test_peer_0041 *)ctx;
    for(unsigned i=0;i<2;++i)if(slot==&p->slots[i])ap01_lvgl_0041.i4_retire(&p->pages[i].surface);
}
static int prepare(void *ctx,ap01_screen_slot *slot,uint32_t) {
    auto *p=(ap01_test_peer_0041 *)ctx;
    unsigned index=slot==&p->slots[0]?0:1;
    auto *pixels=new(std::nothrow) uint8_t[38400];if(!pixels)return AP01_ENTER_FAILED;
    /* Visibly different, deterministic RGB565 images, no template/Bundle code. */
    memset(pixels,index?0x22:0x11,38400);
    const uint16_t palette[16]={0,0xf800,0x07e0,0xffff};
    int ok=ap01_lvgl_0041.i4_present(&p->pages[index].surface,slot->root,pixels,palette,1,drawn,p);
    delete[] pixels;return ok?AP01_ENTER_READY:AP01_ENTER_FAILED;
}
static int input(void *ctx,ap01_screen_slot *,unsigned event) {
    auto *p=(ap01_test_peer_0041 *)ctx;++p->inputs;
    if(event==AP01_INPUT_ESCAPE){++p->escapes;return AP01_FOCUS_UNLOCK;}
    if(event==AP01_INPUT_SHORT)return p->app->host->locked?AP01_FOCUS_UNLOCK:AP01_FOCUS_LOCK;
    return AP01_FOCUS_KEEP;
}
int ap01_test_peer_replace(ap01_test_peer_0041 *p,unsigned count,int reverse) {
    const char *ids[]={"peer-a","peer-b"};ap01_screen_desc d[2]{};
    if(count>2)return AP01_HOST_CAPACITY;
    for(unsigned i=0;i<count;++i)d[i]={AP01_SCREEN_ABI_0041,sizeof(d[i]),ids[reverse?1-i:i],p,prepare,nullptr,release,release,input,1};
    return ap01_host_api.replace_screen_set(p->app,p->app->revision,d,count);
}
static void poll(void *ctx,uint32_t) {
    auto *p=(ap01_test_peer_0041 *)ctx;++p->polls;
    if(!p->app->count)ap01_test_peer_replace(p,2,0);
    auto *h=p->app->host;
    for(auto &page:p->pages)ap01_lvgl_0041.obj_hide(page.surface.image,h->blocked||!h->port.available(h->port.context));
}
int ap01_test_peer_mount(ap01_test_peer_0041 *p,ap01_screen_app *app,ap01_window_0041 *window) {
    if(!ap01_window_mount(window,p->slots,p->pages,2))return 0;
    p->app=app;*app={"host_probe",nullptr,p->slots,2,0,0,p,poll};return 1;
}
int ap01_test_peer_hidden(ap01_test_peer_0041 *p) {
    auto *image=(uint8_t *)p->pages[0].surface.image;
    return image&&(*(uint32_t *)(image+0x24)&1);
}
unsigned ap01_test_peer_diagnostic(ap01_test_peer_0041 *p,unsigned operation) {
    auto *image=(uint8_t *)p->pages[0].surface.image;
    auto *root=(uint8_t *)p->slots[0].root;
    auto *h=p->app->host;
    switch(operation) {
    case 0:return p->drawEvents;
    case 1:return p->matchedEvents;
    case 2:return ap01_host_api.is_visible(p->app,"peer-a");
    case 3:return image?*(uint32_t *)(image+0x24):~0u;
    case 4:return root?*(uint32_t *)(root+0x24):~0u;
    case 5:return h->port.available(h->port.context);
    case 6:return p->slots[0].live;
    case 7:return p->slots[0].desc.visible;
    case 8:return image?*(uint32_t *)(image+0x14):~0u;
    case 9:return root?*(uint32_t *)(root+0x14):~0u;
    default:return ~0u;
    }
}
