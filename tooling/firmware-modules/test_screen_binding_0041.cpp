// Production window dispatch with fake native registrations. No ROM execution.
#include <cassert>
#include <cstring>
#include <cstdio>
#include <type_traits>
#include "screen_port_0041.h"
static unsigned registrations, deletions, polls, events;
static bool failTimer;
static void (*nativeEvent)(void *);
static void (*nativeTimer)(void *);
alignas(void *) static unsigned char timerData[32];
static void *makeTimer(void (*cb)(void *),unsigned period,void *ctx) {
    assert(period==50);if(failTimer)return nullptr;
    nativeTimer=cb;memcpy(timerData+12,&ctx,sizeof(ctx));return timerData;
}
static void deleteTimer(void *t){assert(t==timerData);++deletions;}
static void registerEvent(void *,void (*cb)(void *),unsigned filter,void *) {
    assert(filter==0);nativeEvent=cb;++registrations;
}
template<class T,class F>static T checked(F fn) {
    if constexpr(std::is_same_v<T,F>)return fn;
    else {assert(!"native signature mismatch");return nullptr;}
}
template<class T>static T rom(uintptr_t address) {
    switch(address) {
    case 0xa008bc64:return checked<T>(&makeTimer);
    case 0xa008ae58:return checked<T>(&deleteTimer);
    case 0xa01ad654:return checked<T>(&registerEvent);
    default:assert(!"unexpected native call");return nullptr;
    }
}
#define ROM(a,t) rom<t>(a)
#include "screen_port_0041.cpp"
static void pollCallback(void *p) {
    auto *w=(ap01_window_0041 *)p;++polls;
    assert(!ap01_window_unbind(w));assert(!ap01_window_bind(w));
}
static void eventCallback(void *p,void *e) {
    auto *w=(ap01_window_0041 *)p;++events;
    assert(!ap01_window_unbind(w));assert(!ap01_window_bind(w));
    // Nested timer callbacks must not clear the outer dispatch guard.
    nativeTimer(timerData);assert(w->dispatch_depth==1);
    if(ap01_event_code(e)==0x29)w->win=nullptr;
    assert(!ap01_window_unbind(w));
}
static void send(void *target,ap01_window_0041 &w,unsigned code) {
    alignas(void *) unsigned char data[32]={};
    memcpy(data,&target,sizeof(target));memcpy(data+8,&code,4);
    auto *context=&w;memcpy(data+12,&context,sizeof(context));nativeEvent(data);
}
int main() {
    int root,other;ap01_window_0041 w{};
    w.win=&root;w.context=&w;w.poll=pollCallback;w.event=eventCallback;
    failTimer=true;assert(!ap01_window_bind(&w));assert(!w.event_root&&!registrations);
    failTimer=false;assert(ap01_window_bind(&w));assert(ap01_window_bind(&w));assert(registrations==1);
    assert(!ap01_window_unbind(&w));assert(!deletions);
    w.win=&other;assert(!ap01_window_bind(&w));w.win=&root;
    send(&root,w,1);assert(w.event_root==&root&&!w.dispatch_depth);
    // Clearing win alone cannot discard the outstanding native subscription.
    w.win=nullptr;assert(!ap01_window_unbind(&w));w.win=&root;
    send(&other,w,0x29);assert(w.event_root==&root);w.win=&root;
    send(&root,w,0x29);assert(!w.event_root&&!w.win&&!w.dispatch_depth);
    // A retained timer is still protected during its own callback.
    nativeTimer(timerData);assert(ap01_window_unbind(&w));assert(deletions==1&&!w.timer);
    w.win=&other;assert(ap01_window_bind(&w));assert(registrations==2);
    send(&other,w,0x29);assert(ap01_window_unbind(&w));assert(deletions==2);
    assert(ap01_window_unbind(&w));assert(deletions==2);
    assert(events==4&&polls==5);
    puts("window binding: duplicate/rebind, creation failure, live subscription, nested dispatch and DELETE lifetime passed");
}
