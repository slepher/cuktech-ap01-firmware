// Standalone platform: stock pages plus maintenance, with no business App.
#include "native_services_0041.h"
#include "native_io_0041.h"
#include "screen_port_0041.h"
#include <new>
#include <stddef.h>

namespace {
struct Platform {
    ap01_window_0041 window{};
    Ap01NativeServices0041 services;
    uint64_t boot;
    std::atomic<uint32_t> heartbeat{0};
    explicit Platform(uint64_t id):boot(id) {}
    static void poll(void *p) {
        ((Platform *)p)->heartbeat.store(uint32_t(ap01_native0041::nowMs()),std::memory_order_release);
    }
    static bool healthy(void *p) {
        auto &s=*(Platform *)p;
        return uint32_t(ap01_native0041::nowMs())-s.heartbeat.load(std::memory_order_acquire)<5000;
    }
    static void event(void *p,void *e) {
        auto &s=*(Platform *)p;
        if(ap01_event_code(e)==0x29&&ap01_event_target(e)==s.window.win)
            ap01_window_detach(&s.window);
    }
    static void *start(void *p) {
        auto &s=*(Platform *)p;
        s.services.start({},s.boot,&s,healthy);
        return nullptr;
    }
    bool bind(void *root) {
        window.win=root;window.context=this;window.event=event;
        window.poll=poll;window.services=&services;
        if(ap01_window_bind(&window))return true;
        window.win=nullptr;return false;
    }
};
}

extern "C" {
__attribute__((section(".ap01_manifest"),used,aligned(1)))
extern const uint8_t ap01_native_manifest[256]={};
// ABI 2 describes a platform-only runtime; no App-private layout or symbols.
__attribute__((section(".ap01_abi"),used))
extern const uint32_t ap01_platform_abi[]={2,sizeof(Platform),offsetof(Platform,window),offsetof(Platform,heartbeat)};

__attribute__((used))
void ap01Register0041(void *root,void (*callback)(void *),unsigned filter,void *user) {
    using namespace ap01_native0041;
    registerStock(root,callback,filter,user);
    if(!mainHook(callback,filter))return;
    if(auto *platform=(Platform *)ap01_window_find(Platform::poll)) {
        if(!platform->window.win)platform->bind(root);
        return;
    }
    uint64_t boot=0;
    if(!randomBytes(nullptr,(uint8_t *)&boot,sizeof(boot))||!boot)return;
    auto *platform=new(std::nothrow) Platform(boot);
    if(!platform)return;
    if(!platform->bind(root)){delete platform;return;}
    // The window's retained timer owns the lifetime, including startup failure.
    uint32_t worker=0;
    thread(&worker,"ap01-platform",Platform::start,16384,platform);
}
}
