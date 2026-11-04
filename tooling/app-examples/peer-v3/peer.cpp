// Independently linked ABI 3 example: one page and one background task. No ROM imports.
#include "app_platform_api_v3.h"
#include <atomic>
#include <new>
struct Peer {
    const Ap01PlatformApiV3 *api;void *context;
    ap01_screen_slot slot[1]{};ap01_page_0041 page[1]{};
    std::atomic<uint32_t> beats{0},lastBeat{0};std::atomic<uint32_t> ticks{0};std::atomic<bool> attached{false};
    Peer(const Ap01PlatformApiV3 *a,void *c):api(a),context(c){}
};
static int prepare(void *,ap01_screen_slot *,uint32_t){return AP01_ENTER_READY;}
static void poll(void *,uint32_t){}
static void tick(void *p){++((Peer *)p)->ticks;}
static void event(void *p,void *e){
    auto &s=*(Peer *)p;
    if(s.api->ui.event_code(e)==0x29&&s.api->ui.event_target(e)==s.api->ui.window->win)s.attached=false;
}
static int attach(Peer &s){
    if(s.api->ui.attach(s.context,&s,s.slot,s.page,1,poll,tick,event))return AP01_APP_V3_FAILED;
    ap01_screen_desc desc{1,sizeof(ap01_screen_desc),"peer",nullptr,prepare,nullptr,nullptr,nullptr,nullptr,1};
    if(s.api->ui.screens->replace_screen_set(s.api->ui.app,s.api->ui.app->revision,&desc,1))return AP01_APP_V3_FAILED;
    s.attached=true;return AP01_APP_V3_OK;
}
static void *worker(void *p){
    auto &s=*(Peer *)p;
    for(;;){s.lastBeat.store(uint32_t(s.api->now_ms(s.context)),std::memory_order_release);s.beats.fetch_add(1,std::memory_order_release);s.api->pause_ms(s.context,10);}
}
extern "C" int32_t ap01_app_start_v3(const Ap01PlatformApiV3 *api,void *context,void **out){
    if(!api||api->abi_major!=3||api->struct_bytes<sizeof(*api)||!out)return AP01_APP_V3_INVALID;
    void *memory=api->allocate(context,sizeof(Peer));if(!memory)return AP01_APP_V3_FAILED;
    auto *s=new(memory) Peer(api,context);*out=s;
    if(attach(*s)||api->task_start(context,"peer",worker,2048,s))return AP01_APP_V3_FAILED;
    return AP01_APP_V3_OK;
}
extern "C" int32_t ap01_app_event_v3(void *p,uint32_t kind,const void *,uint32_t){
    if(!p)return AP01_APP_V3_INVALID;
    return kind==3?attach(*(Peer *)p):AP01_APP_V3_OK;
}
extern "C" int32_t ap01_app_health_v3(void *p){
    if(!p)return AP01_APP_V3_FAILED;
    auto &s=*(Peer *)p;
    bool ran=s.beats.load(std::memory_order_acquire)!=0;
    uint32_t last=s.lastBeat.load(std::memory_order_acquire),now=uint32_t(s.api->now_ms(s.context));
    if(ran&&uint32_t(now-last)>5000)return AP01_APP_V3_FAILED;
    return s.attached&&s.ticks&&s.beats.load(std::memory_order_acquire)?AP01_APP_V3_OK:AP01_APP_V3_PENDING;
}
