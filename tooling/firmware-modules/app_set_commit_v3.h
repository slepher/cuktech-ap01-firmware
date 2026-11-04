#pragma once
#include "app_set_journal_v3.h"
#include "app_manifest_v3.h"
#include "app_write_gate_v3.h"
#include "app_reboot_v3.h"
enum class Ap01SetCommitResultV3 {Pending,Busy,Conflict,NotReady,Package,Unknown,State,DrainTimeout,RebootFailed,Cancelled,RebootInFlight};
// One transaction worker owns this and the write gate throughout commit.
// Caller authenticates principal/MAC and acquires the platform-wide maintenance
// operation lease before calling; the lease also prevents background reopening.
class Ap01SetCommitV3 {
    Ap01SetJournalV3 &journal;Ap01AppWriteGateV3 &writes;Ap01AppRebootV3 &reboot;
    bool draining=false,expired=false;uint32_t drainAt=0;
public:
    Ap01SetCommitV3(Ap01SetJournalV3 &j,Ap01AppWriteGateV3 &g,Ap01AppRebootV3 &r):journal(j),writes(g),reboot(r){}
    Ap01SetCommitResultV3 cancel(const uint8_t transaction[16],uint32_t now);
    Ap01SetCommitResultV3 commit(const uint8_t transaction[16],const uint8_t expectedCurrent[32],uint64_t expectedVersion,
        const Ap01ManifestV3 &,const Ap01ManifestPackagesV3 &,uint32_t now);
};
