#pragma once
#include "native_app_port_0041.h"
#include <memory>
#include <atomic>
#include "app_supervision_v3.h"
// Firmware-owned platform services. App supplies only pairing, identity and
// health callbacks, and observes a single availability gate.
class Ap01NativeServices0041 {
    struct State;
    std::unique_ptr<State> state;
    std::atomic<State *> live{nullptr};
    void *statusContext=nullptr;
    void (*statusSnapshot)(void *,Ap01SupervisorSnapshotV3 &)=nullptr;
public:
    Ap01NativeServices0041();
    ~Ap01NativeServices0041();
    bool start(const Ap01MaintenanceBridge0041 &,uint64_t boot,void *healthContext,bool (*healthy)(void *));
    bool busy() const;
    bool listening() const;
    uint32_t heartbeat() const;
    void appStatus(void *context,void (*snapshot)(void *,Ap01SupervisorSnapshotV3 &)){
        statusContext=context;statusSnapshot=snapshot;
    }
    int selectWifi(const char *);
    int wifiState() const;
    void traceMenu(int,int,int,int,int);
};
