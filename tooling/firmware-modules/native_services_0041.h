#pragma once
#include "native_app_port_0041.h"
#include <memory>
#include <atomic>
// Firmware-owned platform services. App supplies only pairing, identity and
// health callbacks, and observes a single availability gate.
class Ap01NativeServices0041 {
    struct State;
    std::unique_ptr<State> state;
    std::atomic<State *> live{nullptr};
public:
    Ap01NativeServices0041();
    ~Ap01NativeServices0041();
    bool start(const Ap01MaintenanceBridge0041 &,uint64_t boot,void *healthContext,bool (*healthy)(void *));
    bool busy() const;
    int selectWifi(const char *);
    int wifiState() const;
};
