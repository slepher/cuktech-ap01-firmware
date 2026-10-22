#pragma once
#include "native_wifi_profiles_0041.h"
#include <atomic>
#include <memory>
// Owned by Runtime. UI only enqueues an SSID; the maintenance executor owns I/O.
struct Ap01WifiSwitchPort0041 {
    void *context=nullptr;
    Ap01WifiProfilesPort profiles{};
    int (*apply)(void *, const Ap01WifiProfile0041 &, bool persistent)=nullptr;
    bool (*online)(void *, const char *)=nullptr;
    // Save/remove an encrypted, verified old-network journal; recover is read-only.
    int (*journal)(void *, const Ap01WifiProfile0041 *)=nullptr;
    int (*recover)(void *, Ap01WifiProfile0041 &)=nullptr;
};
class Ap01WifiSwitch0041 {
public:
    enum State {Idle, Queued, Connecting, Saving, Restoring, Connected, Failed, RecoveryFailed, Unavailable, ResultUnknown};
private:
    static const uint32_t budget[2];
    struct Attempt {char ssid[33]={};Ap01WifiProfile0041 previous,target;};
    Ap01WifiSwitchPort0041 port;
    std::atomic<State> phase{Unavailable};
    std::atomic<Attempt *> pending{nullptr};
    std::atomic<uint32_t> submitted{0};
    std::unique_ptr<Attempt> active;
    uint64_t deadline=0;
    bool journaled=false;
    void finish(State);
    void rollback(uint64_t);
public:
    explicit Ap01WifiSwitch0041(Ap01WifiSwitchPort0041 p):port(p){}
    ~Ap01WifiSwitch0041();
    void begin(uint64_t); // Before accepting work; recover interrupted two-key commits.
    int request(const char *ssid,uint32_t now=0); // 0 accepted, negative errno; no driver/PSM calls.
    void tick(uint64_t);
    State state() const {return phase.load(std::memory_order_acquire);}
    State feedback(uint32_t now) const {return busy()&&uint32_t(now-submitted.load(std::memory_order_acquire))>100000?ResultUnknown:state();}
    bool busy() const {auto s=state();return s==Queued||s==Connecting||s==Saving||s==Restoring;}
};
Ap01WifiSwitchPort0041 ap01WifiSwitchNativePort0041(void *,bool (*)(void *));
// UI-facing functions resolve the live Runtime through its existing LVGL timer.
extern "C" int ap01WifiSelect0041(const char *ssid);
extern "C" int ap01WifiSelectionState0041();
