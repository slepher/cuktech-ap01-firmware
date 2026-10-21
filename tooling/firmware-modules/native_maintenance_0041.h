#pragma once
#include "native_firmware_0041.h"
#include "native_wifi_profiles_0041.h"
#include "native_diagnostic_0041.h"
#include "native_http_transport_0041.h"
#include <atomic>

#include "native_app_port_0041.h"
struct Ap01MaintenancePort0041 {
    void *context=nullptr;
    Ap01FirmwarePort firmware{};
    Ap01WifiProfilesPort wifiProfiles{};
    Ap01DiagnosticPort diagnostic{};
    int (*deviceCode)(void *,char out[9])=nullptr;
};
class Ap01Maintenance0041 {
    LittleFSClass &fs;
    Ap01MaintenancePort0041 port;
    Ap01MaintenanceBridge0041 bridge;
    std::unique_ptr<Ap01Firmware> firmware;
    char mac[13];
    uint64_t boot;
    unsigned manualFailures=0;
    uint64_t manualRetryAt=0;
    std::atomic<bool> gate{false};
    bool manualAuth(const Ap01HttpRequest &,uint64_t,Ap01HttpReply &);
public:
    Ap01Maintenance0041(LittleFSClass &,const Ap01MaintenancePort0041 &,
                        const Ap01MaintenanceBridge0041 &,const char *,uint64_t);
    bool begin(uint64_t now=0);
    bool active() const {return gate.load(std::memory_order_acquire);}
    void tick(uint64_t);
    void afterResponse(bool sent) {if(firmware)firmware->afterResponse(sent);}
    Ap01HttpReply handle(const Ap01HttpRequest &,uint64_t);
};
inline bool ap01ServeMaintenanceHttp0041(Ap01Maintenance0041 &service,const Ap01Stream &io,uint64_t now,uint64_t deadline) {
    return ap01ServeNativeHttp0041(&service,[](void *p,const Ap01HttpRequest &r,uint64_t n){return ((Ap01Maintenance0041 *)p)->handle(r,n);},true,io,now,deadline);
}
