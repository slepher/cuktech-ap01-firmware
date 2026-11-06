#include "native_rom_addresses.h"
#include "screen_port_0041.h"
#include <new>
#include <string.h>
#ifndef ROM
#define ROM(address,type) ((type)(uintptr_t)(address))
#endif
#ifdef __riscv
static_assert(sizeof(ap01_page_tag_0041)==20&&sizeof(ap01_image_0041)==24,"0041 RV32 ABI");

/* Power1's stock DELETE callback passes its optional, uncreated timer to
   lv_timer_delete. The builder redirects that entry here; non-NULL calls
   replay its exact 8-byte prologue and continue at the untouched ROM tail. */
extern "C" __attribute__((naked,used)) void ap01TimerDelete0041(void *) {
    __asm__ volatile(
        "beqz a0, 1f\n"
        "addi sp, sp, -16\n"
        "sw ra, 12(sp)\n"
        "sw s0, 8(sp)\n"
        "sw s1, 4(sp)\n"
        "li t0, " AP01_ROM_STRING(0xa008ae60) "\n"
        "jr t0\n"
        "1: ret\n");
}
#endif

static void *create(void *parent) {
    /* lv_obj_create asserts on allocation failure. Use its two verified leaves. */
    void *obj=ROM(AP01_ROM_ADDR(0xa00d76ae),void *(*)(const void *,void *))((const void *)AP01_ROM_ADDR(0xa0263ef4),parent);
    if(obj)ROM(AP01_ROM_ADDR(0xa00d9110),void (*)(void *))(obj);
    return obj;
}
/* Public lv_obj_delete: DELETE event, children, unlink and free. a00d7806
   only walks class destructors and leaves the object in its parent's list. */
static void destroy(void *obj) {if(obj)ROM(AP01_ROM_ADDR(0xa00ded6c),void (*)(void *))(obj);}
static void size(void *obj,int w,int h) {ROM(AP01_ROM_ADDR(0xa00d8e96),void (*)(void *,int,int))(obj,w,h);}
static void align(void *obj,unsigned a,int x,int y) {ROM(AP01_ROM_ADDR(0xa00d92ec),void (*)(void *,unsigned,int,int))(obj,a,x,y);}
static void hide(void *obj,int hidden) {
    if(!obj)return;
    if(hidden)ROM(AP01_ROM_ADDR(0xa00d8f7c),void (*)(void *,uint32_t))(obj,1);
    else ROM(AP01_ROM_ADDR(0xa00d9044),void (*)(void *,uint32_t))(obj,1);
}
static void style(void *obj) {
    ROM(AP01_ROM_ADDR(0xa00d9044),void (*)(void *,uint32_t))(obj,0x400|4|0x10);
    ROM(AP01_ROM_ADDR(0xa00dfb70),void (*)(void *,uint32_t,unsigned))(obj,0,0);
    ROM(AP01_ROM_ADDR(0xa019d5b8),void (*)(void *,int))(obj,0);
    ROM(AP01_ROM_ADDR(0xa00dfbca),void (*)(void *,int,unsigned))(obj,0,0);
    ROM(AP01_ROM_ADDR(0xa00a5c0c),void (*)(void *,int,unsigned))(obj,0,0);
    size(obj,320,240);
}
static void draw(void *obj,void (*cb)(void *),void *ctx) {ROM(AP01_ROM_ADDR(0xa01ad654),void (*)(void *,void (*)(void *),unsigned,void *))(obj,cb,0x1e,ctx);}
static void text(void *obj,const char *value){ROM(AP01_ROM_ADDR(0xa0091b3a),void (*)(void *,const char *))(obj,value);}
static void background(void *obj,uint32_t color){ROM(AP01_ROM_ADDR(0xa00dfb70),void (*)(void *,uint32_t,unsigned))(obj,color,0);}
static void text_color(void *obj,uint32_t color){ROM(AP01_ROM_ADDR(0xa019d0e6),void (*)(void *,uint32_t))(obj,color);}
static void text_font(void *obj,const void *font){ROM(AP01_ROM_ADDR(0xa019d0ae),void (*)(void *,const void *))(obj,font);}
static void *label(void *parent,const char *text,int x,int y) {
    void *obj=ROM(AP01_ROM_ADDR(0xa009090e),void *(*)(void *))(parent);if(!obj)return nullptr;
    ROM(AP01_ROM_ADDR(0xa0091b3a),void (*)(void *,const char *))(obj,text);
    ROM(AP01_ROM_ADDR(0xa019d0ae),void (*)(void *,const void *))(obj,(const void *)AP01_ROM_ADDR(0xa02549f4));
    ROM(AP01_ROM_ADDR(0xa019d0ca),void (*)(void *,unsigned))(obj,0);
    ROM(AP01_ROM_ADDR(0xa019d0e6),void (*)(void *,uint32_t))(obj,0xffffff);
    align(obj,1,x,y);return obj;
}
static void image_event(void *event) {
    auto *s=(ap01_surface_0041 *)ap01_event_context(event);if(!s)return;
    unsigned code=ap01_event_code(event);
    if(code==0x29) {
        ROM(AP01_ROM_ADDR(0xa00890e8),void (*)(const void *))(&s->descriptor);
        delete[] s->bytes;s->bytes=nullptr;s->image=nullptr;s->descriptor={};s->generation=0;
    } else if(code==0x1e&&s->drawn) {
        /* A draw notification is borrowed for this synchronous callback only. */
        uint32_t notification[5];memcpy(notification,event,sizeof(notification));
        notification[3]=(uint32_t)(uintptr_t)s->draw_context;s->drawn(notification);
    }
}
static void retire(ap01_surface_0041 *s) {
    if(!s)return;
    if(s->image){ROM(AP01_ROM_ADDR(0xa00890e8),void (*)(const void *))(&s->descriptor);destroy(s->image);}
    delete[] s->bytes;memset(s,0,sizeof(*s));
}
static int present(ap01_surface_0041 *s,void *parent,const uint8_t *pixels,const uint16_t *palette,
                   uint32_t generation,void (*cb)(void *),void *ctx) {
    if(!s||!parent||!pixels||!palette)return 0;
    uintptr_t cache=*(volatile uint32_t *)(uintptr_t)AP01_ROM_ADDR(0x62fc9698);
    if(!cache||*(uint32_t *)(cache+8)<1280)return 0;
    auto *candidate=new(std::nothrow) uint8_t[38464];if(!candidate)return 0;
    for(unsigned i=0;i<16;++i) {
        unsigned c=palette[i],r=(c>>11)&31,g=(c>>5)&63,b=c&31;
        uint32_t argb=0xff000000|(((r<<3)|(r>>2))<<16)|(((g<<2)|(g>>4))<<8)|(b<<3)|(b>>2);
        memcpy(candidate+4*i,&argb,4);
    }
    memcpy(candidate+64,pixels,38400);
    if(!s->image){s->image=ROM(AP01_ROM_ADDR(0xa00ed0a8),void *(*)(void *))(parent);if(!s->image){delete[] candidate;return 0;}
        s->drawn=cb;s->draw_context=ctx;
        ROM(AP01_ROM_ADDR(0xa01ad654),void (*)(void *,void (*)(void *),unsigned,void *))(s->image,image_event,0,s);}
    ROM(AP01_ROM_ADDR(0xa00890e8),void (*)(const void *))(&s->descriptor);
    ap01_image_0041 old=s->descriptor;
    s->descriptor={{0x19,0x09,0,320,240,160,0},38464,candidate,nullptr};
    ROM(AP01_ROM_ADDR(0xa00ed560),void (*)(void *,const ap01_image_0041 *))(s->image,&s->descriptor);
    if(*(const void **)((uint8_t *)s->image+0x2c)!=&s->descriptor||
       *(uint32_t *)((uint8_t *)s->image+0x3c)!=320||*(uint32_t *)((uint8_t *)s->image+0x40)!=240) {
        s->descriptor=old;
        ROM(AP01_ROM_ADDR(0xa00890e8),void (*)(const void *))(&s->descriptor);
        if(old.data)ROM(AP01_ROM_ADDR(0xa00ed560),void (*)(void *,const ap01_image_0041 *))(s->image,&s->descriptor);
        else {destroy(s->image);s->image=nullptr;}
        delete[] candidate;return 0;
    }
    delete[] s->bytes;s->bytes=candidate;s->generation=generation;return 1;
}
extern "C" const ap01_lvgl_api_0041 ap01_lvgl_0041={1,sizeof(ap01_lvgl_api_0041),create,destroy,size,align,hide,label,present,retire,draw,text,background,text_color,text_font};
extern "C" unsigned ap01_event_code(void *e){return *(uint32_t *)((uint8_t *)e+8)&0xffff7fff;}
extern "C" unsigned ap01_event_key(void *e){return ROM(AP01_ROM_ADDR(0xa00d8af6),unsigned (*)(void *))(e);}
extern "C" void *ap01_event_context(void *e){void *context;memcpy(&context,(uint8_t *)e+12,sizeof(context));return context;}
extern "C" void *ap01_event_target(void *e){return *(void **)e;}
extern "C" unsigned ap01_window_active(ap01_window_0041 *w){return ROM(AP01_ROM_ADDR(0xa00b2ff4),unsigned (*)(void *))(w->win);}
extern "C" int ap01_window_visible(ap01_window_0041 *w){return w->win&&!*(volatile uint8_t *)(uintptr_t)AP01_ROM_ADDR(0x62fc4053)&&
    *(volatile uint32_t *)(uintptr_t)AP01_ROM_ADDR(0x62fc95bc)==*(uint32_t *)((uint8_t *)w->win+0x30)&&!*((uint8_t *)w->win+0x4d);}
extern "C" int ap01_window_awake(ap01_window_0041 *w){return ap01_window_visible(w)&&*(volatile uint8_t *)(uintptr_t)AP01_ROM_ADDR(0x62fc4039)==1;}
extern "C" int ap01_window_idle(ap01_window_0041 *w){return w->win&&*((uint8_t *)w->win+0x4c);}
extern "C" void ap01_window_activity(void){*(volatile uint8_t *)(uintptr_t)AP01_ROM_ADDR(0x62fc403a)=1;}
extern "C" void ap01_window_wake(void){ROM(AP01_ROM_ADDR(0xa00a769a),int (*)())();ap01_window_activity();}
extern "C" void *ap01_window_child(ap01_window_0041 *w,unsigned index){return ROM(AP01_ROM_ADDR(0xa00dcee4),void *(*)(void *,int))(w->win,index);}
static unsigned active(void *p){return ap01_window_active((ap01_window_0041 *)p);}
static int idle(void *p){return ap01_window_idle((ap01_window_0041 *)p);}
static int available(void *p){return ap01_window_awake((ap01_window_0041 *)p);}
static void slide(void *p,unsigned child,unsigned direction){auto *w=(ap01_window_0041 *)p;ROM(AP01_ROM_ADDR(0xa00b3106),void (*)(void *,int,int))(w->win,child,direction);}
static void edge(void *p,unsigned source,unsigned target) {
    auto *w=(ap01_window_0041 *)p;
    if(source==7){void *pet=ap01_window_child(w,7);auto *state=*(void **)(*(uintptr_t *)((uint8_t *)pet+0x10)+4);
        auto *gif=*(uint8_t **)state;ROM(AP01_ROM_ADDR(0xa008bd16),void (*)(void *))(*(void **)(gif+0x60));}
    if(target==6) {
        /* Same argument extraction as the stock Pet -> Settings edge. */
        uint32_t fields[2]={};ROM(AP01_ROM_ADDR(0xa00a68a8),void (*)(void *))(fields);
        unsigned format=ROM(AP01_ROM_ADDR(0xa00a5c94),unsigned (*)())();
        auto *page=(uint8_t *)ap01_window_child(w,6);
        auto *state=*(uint8_t **)(*(uintptr_t *)(page+0x10)+4);
        ROM(AP01_ROM_ADDR(0xa01a516c),void (*)(void *,unsigned,unsigned,unsigned,unsigned))
            (*(void **)(state+4),format,fields[0]&255,(fields[0]>>8)&255,fields[0]>>24);
    }
}
extern "C" ap01_screen_port ap01_window_port(ap01_window_0041 *w){return {w,active,idle,available,slide,edge};}
extern "C" int ap01_window_mount(ap01_window_0041 *w,ap01_screen_slot *slots,ap01_page_0041 *pages,unsigned count) {
    if(!w||!w->win||!slots||!pages||!count)return 0;
    unsigned before=ROM(AP01_ROM_ADDR(0xa00dd144),unsigned (*)(void *))(w->win),made=0;
    if(before<AP01_STOCK_SCREEN_COUNT)return 0;
    void *stock[AP01_STOCK_SCREEN_COUNT];
    for(unsigned i=0;i<AP01_STOCK_SCREEN_COUNT;++i)stock[i]=ap01_window_child(w,i);
    for(;made<count;++made) {
        void *obj=create(w->win);if(!obj)break;
        slots[made].root=obj;slots[made].child=before+made;
        pages[made].tag.kind=0x80+before-AP01_STOCK_SCREEN_COUNT+made;pages[made].tag.state=&pages[made];
        *(void **)((uint8_t *)obj+0x10)=&pages[made].tag;
        style(obj);ROM(AP01_ROM_ADDR(0xa00d8c12),void (*)(void *,int))(obj,320);
    }
    bool intact=made==count&&ROM(AP01_ROM_ADDR(0xa00dd144),unsigned (*)(void *))(w->win)==before+count;
    for(unsigned i=0;i<AP01_STOCK_SCREEN_COUNT;++i)if(ap01_window_child(w,i)!=stock[i])intact=false;
    if(intact)return 1;
    while(made){--made;destroy(slots[made].root);slots[made].root=nullptr;}
    return 0;
}
extern "C" void *ap01_window_overlay(ap01_window_0041 *w) {
    void *obj=create(ap01_window_child(w,ap01_window_active(w)));if(!obj)return nullptr;
    style(obj);ROM(AP01_ROM_ADDR(0xa00d8f7c),void (*)(void *,uint32_t))(obj,(1u<<17)|(1u<<18));align(obj,1,0,0);hide(obj,1);return obj;
}
extern "C" void ap01_window_unmount(ap01_screen_slot *slots,ap01_page_0041 *pages,unsigned count) {
    while(count){--count;retire(&pages[count].surface);destroy(slots[count].root);slots[count].root=nullptr;}
}
static void timer(void *t){
    ap01_window_0041 *w;memcpy(&w,(uint8_t *)t+12,sizeof(w));
    if(w&&w->poll){++w->dispatch_depth;w->poll(w->context);--w->dispatch_depth;}
}
static void event(void *e){
    auto *w=(ap01_window_0041 *)ap01_event_context(e);if(!w)return;
    bool deleting=ap01_event_code(e)==0x29&&ap01_event_target(e)==w->event_root;
    ++w->dispatch_depth;
    if(w->event)w->event(w->context,e);
    if(deleting){w->event_root=nullptr;w->win=nullptr;}
    --w->dispatch_depth;
}
extern "C" void *ap01_window_find(void (*poll)(void *)) {
    /* Verified 0041 lv_ll: node size, head, tail; next follows node+size+4.
       Only inspect our timer callback before interpreting its user_data. */
    auto *list=(uintptr_t *)(uintptr_t)AP01_ROM_ADDR(0x62fc95f0);
    if(list[0]!=24)return nullptr;
    for(auto *t=(uint8_t *)list[1];t;t=*(uint8_t **)(t+28)) {
        if(*(void (**)(void *))(t+8)!=timer)continue;
        auto *w=*(ap01_window_0041 **)(t+12);
        if(w&&w->timer==t&&w->poll==poll)return w->context;
    }
    return nullptr;
}
extern "C" void *ap01_window_services(void) {
    /* Verified 0041 lv_ll: node size, head, tail; next follows node+size+4.
       Only inspect our timer callback before interpreting its user_data. */
    auto *list=(uintptr_t *)(uintptr_t)AP01_ROM_ADDR(0x62fc95f0);
    if(list[0]!=24)return nullptr;
    for(auto *t=(uint8_t *)list[1];t;t=*(uint8_t **)(t+28)) {
        if(*(void (**)(void *))(t+8)!=timer)continue;
        auto *w=*(ap01_window_0041 **)(t+12);
        if(w&&w->timer==t&&w->services)return w->services;
    }
    return nullptr;
}
extern "C" int ap01_window_bind(ap01_window_0041 *w) {
    if(!w||!w->win||!w->event||!w->poll)return 0;
    if(w->dispatch_depth)return 0;
    if(w->event_root)return w->event_root==w->win;
    if(!w->timer)w->timer=ROM(AP01_ROM_ADDR(0xa008bc64),void *(*)(void (*)(void *),unsigned,void *))(timer,50,w);
    if(!w->timer)return 0;
    w->event_root=w->win;
    ROM(AP01_ROM_ADDR(0xa01ad654),void (*)(void *,void (*)(void *),unsigned,void *))(w->win,event,0,w);return 1;
}
static unsigned stock_bindings(void *win,int remove) {
    /* Stock registration deduplicates by callback and never refreshes its
       context. Remove only the four subscriptions owned by this window. */
    static const uintptr_t bindings[][2]={
        {AP01_ROM_ADDR(0x62fcb554),AP01_ROM_ADDR(0xa00ad07e)},{AP01_ROM_ADDR(0x62fcb530),AP01_ROM_ADDR(0xa00adabc)},
        {AP01_ROM_ADDR(0x62fcb548),AP01_ROM_ADDR(0xa00ac93c)},{AP01_ROM_ADDR(0x62fcb4ec),AP01_ROM_ADDR(0xa00abfe6)}};
    unsigned count=0;
    for(auto &binding:bindings) {
        auto *list=(uintptr_t *)binding[0];if(list[0]!=8)continue;
        for(auto *node=(uintptr_t *)list[1];node;) {
            auto *next=*(uintptr_t **)((uint8_t *)node+12);
            if(node[0]==binding[1]&&(void *)node[1]==win) {
                ++count;
                if(remove) {
                    ROM(AP01_ROM_ADDR(0xa0089d02),void (*)(void *,void *))(list,node);
                    ROM(AP01_ROM_ADDR(0xa008ab8a),void (*)(void *))(node);
                }
            }
            node=next;
        }
    }
    return count;
}
extern "C" unsigned ap01_window_binding_count(void *win){return stock_bindings(win,0);}
extern "C" void ap01_window_detach(ap01_window_0041 *w){
    if(w->win&&(*(uint16_t *)((uint8_t *)w->win+0x2a)&0x1000))stock_bindings(w->win,1);
    w->win=nullptr;
}
extern "C" int ap01_window_unbind(ap01_window_0041 *w){
    if(!w||w->event_root||w->dispatch_depth)return 0;
    if(w->timer)ROM(AP01_ROM_ADDR(0xa008ae58),void (*)(void *))(w->timer);
    w->timer=nullptr;w->win=nullptr;return 1;
}
