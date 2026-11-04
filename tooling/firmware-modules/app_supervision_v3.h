#pragma once
#include "app_abi_v3.h"
#include "app_manifest_v3.h"
#include <atomic>
#include "app_reboot_v3.h"

enum class Ap01SupervisorStateV3:uint32_t {Starting,Healthy,WindowAbsent,Fault};
enum class Ap01SupervisorFaultV3:uint32_t {None,Boot,StartupTimeout,MaintenanceStale,UiStale,AppFailed,AppTimeout,Worker};
struct Ap01SupervisorSnapshotV3 {
    Ap01SupervisorStateV3 state;Ap01SupervisorFaultV3 fault;
    uint32_t app_index,count,sampled_at;int32_t health[AP01_MANIFEST_APPS_V3];
    Ap01RebootStateV3 reboot=Ap01RebootStateV3::Idle;
    uint32_t journal_result=UINT32_MAX,journal_phase=0;
};
// UI owns publish(); a separate platform worker owns tick(). HTTP only reads.
// Faults latch until reboot. This observer never calls App code or reboots.
class Ap01AppSupervisionV3 {
    std::atomic<uint32_t> revision{0},sampleTime{0},sampleWord{0};
    std::atomic<uint32_t> status{0}; // state low byte, reason next, index high 16
    uint32_t startedAt=0,pendingAt=0;bool begun=false,pending=false,sawMaintenance=false;
    bool sample(uint32_t &,uint32_t &)const;
public:
    void publish(uint32_t now,const int32_t *,uint32_t count);
    // boot: 0 still starting, 1 loaded, -1 failed. All timestamps use uint32 ms.
    void tick(uint32_t now,int boot,bool listening,uint32_t maintenanceBeat,bool windowPresent);
    void fail(Ap01SupervisorFaultV3,uint32_t index=UINT32_MAX);
    Ap01SupervisorSnapshotV3 snapshot()const;
};
