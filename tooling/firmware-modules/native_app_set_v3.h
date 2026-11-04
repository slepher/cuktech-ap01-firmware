#pragma once
#include "native_app_platform_v3.h"
#include "app_set_boot_v3.h"

// Whole-boot owner. Call boot on the UI executor, with immutable package storage.
// Backend reservations and all contexts survive partial failure until reboot.
class Ap01NativeAppSetV3 {
    Ap01NativeAppSharedV3 resident;
    Ap01ManifestPackagesV3 packages;
    Ap01BootPortV3 backend;
    std::unique_ptr<Ap01NativeAppPlatformV3> contexts[AP01_MANIFEST_APPS_V3];
    uint32_t count=0;
    std::atomic<bool> started{false};
    Ap01AppSetBootV3 loader;
    static bool open(void *,const Ap01ManifestEntryV3 &,Apx2Reader &,uint32_t &);
    static void close(void *,Apx2Reader &);
    static bool ready(void *);
    static bool prepare(void *,const Ap01ManifestEntryV3 &,Ap01AppBootV3 *&,
                        const Ap01PlatformApiV3 *&,void *&);
public:
    Ap01NativeAppSetV3(uint64_t,const Ap01ManifestPackagesV3 &,const Ap01BootPortV3 &);
    Ap01NativeAppSharedV3 &shared(){return resident;}
    Ap01AppSetBootV3 &execution(){return loader;}
    Ap01AppSetResultV3 boot(const Apx2Reader &reader,const uint8_t digest[32],const Ap01ManifestLimitsV3 &limits){
        auto result=loader.boot(reader,digest,limits);
        if(result==Ap01AppSetResultV3::Started)started.store(true,std::memory_order_release);
        return result;
    }
    // Platform transaction worker only. Open only after durable approval.
    // Revoke always closes admission; false means existing mutations still run.
    bool writes(bool allow){return (!allow||started.load(std::memory_order_acquire))&&resident.writes(allow);}
    bool writesDrained()const{return resident.writesDrained();}
};
