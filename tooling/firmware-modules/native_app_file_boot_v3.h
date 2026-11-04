#pragma once
#include "app_set_files_v3.h"
#include "native_app_set_v3.h"
// One worker stages bounded immutable bytes, one UI executor consumes once.
class Ap01NativeAppFileBootV3 {
    Ap01AppSetFilesV3 files;
    Ap01NativeAppSetV3 apps;
    Ap01ManifestLimitsV3 limits;
    uint32_t stagingBytes;
    std::atomic<uint32_t> phase{0}; // 0 absent, 1 worker, 2 staged, 3 consumed, 4 failed
    std::atomic<Ap01SetFilesResultV3> ioResult{Ap01SetFilesResultV3::Empty};
    std::atomic<Ap01AppSetResultV3> bootResult{Ap01AppSetResultV3::Waiting};
    Ap01AppSupervisionV3 supervisor;
    static void poll(void *,bool afterApps);
public:
    Ap01NativeAppFileBootV3(uint64_t,const Ap01VfsOps &,const Ap01BootPortV3 &,
                            const Ap01ManifestLimitsV3 &,uint32_t stagingBytes);
    // Worker: requires listening. An unsuccessful attempt is not retried this boot.
    bool stage(const char *path,const uint8_t *expected=nullptr);
    void monitor(uint32_t now);
    void workerFailed(){supervisor.fail(Ap01SupervisorFaultV3::Worker);}
    Ap01SupervisorSnapshotV3 status()const{return supervisor.snapshot();}
    Ap01NativeAppSetV3 &set(){return apps;}
    Ap01SetFilesResultV3 fileResult()const{return ioResult.load(std::memory_order_acquire);}
    Ap01AppSetResultV3 result()const{return bootResult.load(std::memory_order_acquire);}
};
