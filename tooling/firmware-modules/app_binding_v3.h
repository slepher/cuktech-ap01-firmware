#pragma once
#include "app_platform_api_v3.h"
#include "native_app_port_0041.h"
#include <atomic>

// Resident bridge installed before the App exists. A single immutable binding
// is published by the business worker; maintenance never borrows C++ App state.
class Ap01AppBindingBridgeV3 {
    Ap01AppBindingV3 binding{};
    std::atomic<bool> ready{false};
    std::atomic_flag lock=ATOMIC_FLAG_INIT;
    static int principal(void *,const char *,char [65]);
    static Ap01HttpReply pairing(void *,const Ap01HttpRequest &,uint64_t);
    static bool online(void *);
public:
    int32_t bind(const Ap01AppBindingV3 &);
    Ap01MaintenanceBridge0041 bridge(){return {this,principal,pairing,online,nullptr,0};}
};
