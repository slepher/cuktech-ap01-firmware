#pragma once
#include "app_update_record_0041.h"
#include "apx2.h"

enum class Ap01AppSelectionResult {Launch,Recovery,Waiting,Unknown,Storage,Invalid,Failed};
struct Ap01AppHealthSample {
    bool entryReady=false,resourcesOkay=true;
    // Firmware-observed progress counters, not App-supplied assertions. The
    // maintenance counter is its executor heartbeat, not external HTTP traffic.
    uint32_t events=0,stockScheduler=0,maintenance=0;
};
struct Ap01AppSelection {
    const char *path=nullptr; // Firmware constant; not a pointer into App memory.
    uint32_t generation=0;
    bool trial=false,rollback=false;
    uint8_t digest[32]={};
};
// Single lifecycle executor. Caller must stop/drain all App code before commit
// or select, and own the update mutex throughout. Cleanup only touches package
// files, never running RAM. No hardware calls occur here.
class Ap01AppSelection0041 {
    LittleFSClass &fs;
    Ap01AppUpdateJournal0041 &journal;
    Apx2Limits limits;
    uint32_t observing=0;
    uint32_t selectedGeneration=0;
    uint64_t startedAt=0,lastAt=0,healthyAt=0;
    bool entrySeen=false,sampled=false,continuous=false,failed=false;
    Ap01AppHealthSample last{};
    const char *find(const uint8_t digest[32]);
    Ap01AppSelectionResult recover(bool old);
    Ap01AppSelectionResult confirm(uint32_t generation,const uint8_t digest[32]);
public:
    static constexpr uint64_t startTimeoutMs=10000,healthyMs=30000,sampleGapMs=1000;
    Ap01AppSelection0041(LittleFSClass &f,Ap01AppUpdateJournal0041 &j,const Apx2Limits &l):fs(f),journal(j),limits(l){}
    Ap01AppSelectionResult commit();
    // Caller must stop/drain a trial before cancelling it. Download cancellation
    // does not stop the old App. Terminal transactions remain terminal.
    Ap01AppSelectionResult cancel();
    // Call only when no App is running. Re-entering after a consumed start is a
    // failure/reboot decision, not a query. Status queries read the journal.
    Ap01AppSelectionResult select(uint32_t generation,Ap01AppSelection &,uint64_t now=0);
    // Failed requires stopping/draining before select chooses rollback. Neither
    // missing Bridge traffic nor missing Bundle is a health prerequisite.
    Ap01AppSelectionResult observe(uint32_t generation,const uint8_t digest[32],
                                   uint64_t now,const Ap01AppHealthSample &);
    bool businessWritesAllowed(uint32_t generation) const;
    Ap01AppSelectionResult cleanup();
};
