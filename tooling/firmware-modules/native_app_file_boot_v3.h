#pragma once
#include "app_set_files_v3.h"
#include "native_app_set_v3.h"
#include "app_set_selection_v3.h"
class Ap01SetServiceV3;
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
    Ap01AppRebootV3 reboot;
    std::atomic<Ap01SetServiceV3 *> installer{nullptr};
    std::atomic<uint32_t> journalSnapshot{255};
    static void poll(void *,bool afterApps);
public:
    Ap01NativeAppFileBootV3(uint64_t,const Ap01VfsOps &,const Ap01BootPortV3 &,
                            const Ap01ManifestLimitsV3 &,uint32_t stagingBytes);
    // Worker: requires listening. An unsuccessful attempt is not retried this boot.
    bool stage(const char *path,const uint8_t *expected=nullptr);
    Ap01SetSelectionV3 stageSelected(Ap01SetSelectorV3 &);
    // Transaction worker, after independent monitor has published its status.
    Ap01SetHealthDecisionV3 healthSelected(Ap01SetSelectorV3 &,uint32_t now);
    void monitor(uint32_t now);
    void workerFailed(){supervisor.fail(Ap01SupervisorFaultV3::Worker);}
    Ap01SupervisorSnapshotV3 status()const;
    Ap01RuntimeSnapshotV3 runtime();
    void journalStatus(Ap01SetJournalResultV3 result,const Ap01SetJournalV3 &journal){
        uint32_t phase=journal.current()?uint32_t(journal.current()->phase):0;
        journalSnapshot.store(uint32_t(result)|(phase<<8),std::memory_order_release);
    }
    void attachInstaller(Ap01SetServiceV3 *service){installer.store(service,std::memory_order_release);}
    Ap01SetServiceV3 *installService()const{return installer.load(std::memory_order_acquire);}
    const Ap01ManifestLimitsV3 &installLimits()const{return limits;}
    Ap01AppRebootV3 &installReboot(){return reboot;}
    void dispatchReboot(uint32_t now,void *context,void (*callback)(void *)){reboot.tick(now,context,callback);}
    Ap01NativeAppSetV3 &set(){return apps;}
    Ap01SetFilesResultV3 fileResult()const{return ioResult.load(std::memory_order_acquire);}
    Ap01AppSetResultV3 result()const{return bootResult.load(std::memory_order_acquire);}
};
