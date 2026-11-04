#pragma once
#include "app_manifest_v3.h"
#include "app_boot_v3.h"
struct Ap01AppSetPortV3 {
    Ap01ManifestPackagesV3 packages;
    bool (*maintenance_ready)(void *);
    // Resident owner supplies a distinct loader/API/context for each ID. All
    // objects and images survive this boot even on failure; no unload callback.
    bool (*prepare)(void *,const Ap01ManifestEntryV3 &,Ap01AppBootV3 *&,
                    const Ap01PlatformApiV3 *&,void *&);
};
enum class Ap01AppSetResultV3 {Waiting,Started,Invalid,Manifest,Identity,Packages,Prepare,Start,AlreadyAttempted};
// UI executor owns this object; file contents immutable for the whole attempt.
class Ap01AppSetBootV3 {
    Ap01AppSetPortV3 port;
    Ap01ManifestV3 manifest{};
    Ap01AppBootV3 *loaders[AP01_MANIFEST_APPS_V3]{};
    bool attempted=false,ready=false,dispatching=false;
    uint32_t started=0,failed=UINT32_MAX;
    Ap01ManifestErrorV3 error=Ap01ManifestErrorV3::Ok;
public:
    explicit Ap01AppSetBootV3(const Ap01AppSetPortV3 &p):port(p){}
    Ap01AppSetBootV3(const Ap01AppSetBootV3 &)=delete;
    Ap01AppSetBootV3 &operator=(const Ap01AppSetBootV3 &)=delete;
    Ap01AppSetResultV3 boot(const Apx2Reader &,const uint8_t expected[32],const Ap01ManifestLimitsV3 &);
    int32_t event(uint32_t,const void *,uint32_t);
    int32_t health();
    int32_t health(int32_t values[AP01_MANIFEST_APPS_V3]);
    uint32_t startedCount()const{return started;}
    uint32_t failedIndex()const{return failed;}
    Ap01ManifestErrorV3 validationError()const{return error;}
    const Ap01ManifestV3 &selection()const{return manifest;}
};
