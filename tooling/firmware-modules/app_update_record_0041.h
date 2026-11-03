#pragma once
#include "native_filesystem_0041.h"

// Journal metadata only: the two small records are not App package slots.
enum class Ap01AppUpdatePhase : uint32_t {
    Receiving=1, Ready, SwitchPending, TrialStarted, RollbackPending,
    RollbackStarted, Succeeded, FailedRolledBack, RecoveryRequired, Cancelled
};
struct Ap01AppUpdateRecord {
    uint64_t sequence=0;
    Ap01AppUpdatePhase phase=Ap01AppUpdatePhase::Receiving;
    uint32_t total=0,received=0,generation=0;
    uint8_t trialStarts=0,rollbackStarts=0,cleanupPending=0;
    uint8_t transaction[16]={},mac[6]={},oldDigest[32]={},newDigest[32]={};
    char principal[65]={};
};
constexpr unsigned AP01_APP_UPDATE_RECORD_BYTES=256;
bool ap01EncodeAppUpdate(const Ap01AppUpdateRecord &,uint8_t out[256]);
bool ap01DecodeAppUpdate(const uint8_t in[256],Ap01AppUpdateRecord &);

// A write failure is ambiguous, even if the file write actually committed.
// No subsequent save is permitted until reload resolves persistent state.
enum class Ap01AppJournalResult {Ok,Empty,Corrupt,Io,Unknown,Invalid};
class Ap01AppUpdateJournal0041 {
    LittleFSClass &fs;
    uint8_t device[6];
    Ap01AppUpdateRecord record{};
    bool writable=false,exists=false;
    unsigned slot=0;
public:
    Ap01AppUpdateJournal0041(LittleFSClass &storage,const uint8_t mac[6]);
    Ap01AppJournalResult load();
    Ap01AppJournalResult save(const Ap01AppUpdateRecord &next);
    const Ap01AppUpdateRecord *current() const {return exists?&record:nullptr;}
    bool resolved() const {return writable;}
};
