#pragma once
#include "native_vfs_api_0041.h"

enum class Ap01SetPhaseV3:uint32_t {Receiving=1,Ready,SwitchPending,TrialStarted,RollbackPending,
    RollbackStarted,Succeeded,FailedRolledBack,RecoveryRequired,Cancelled};
struct Ap01SetRecordV3 {
    uint64_t sequence=0,oldVersion=0,newVersion=0,trialBoot=0,rollbackBoot=0,changedBytes=0;
    Ap01SetPhaseV3 phase=Ap01SetPhaseV3::Receiving;
    uint32_t error=0;
    uint32_t received[8]{};
    uint8_t trialStarts=0,rollbackStarts=0,cleanupPending=0,changedMask=0,readyMask=0;
    uint8_t transaction[16]{},mac[6]{},oldDigest[32]{},newDigest[32]{},requestDigest[32]{};
    char principal[65]{};
};
constexpr uint32_t AP01_SET_RECORD_BYTES_V3=320;
bool ap01EncodeSetRecordV3(const Ap01SetRecordV3 &,uint8_t out[AP01_SET_RECORD_BYTES_V3]);
bool ap01DecodeSetRecordV3(const uint8_t in[AP01_SET_RECORD_BYTES_V3],Ap01SetRecordV3 &);
bool ap01SetTransitionV3(const Ap01SetRecordV3 &,const Ap01SetRecordV3 &);
enum class Ap01SetJournalResultV3 {Ok,Empty,Invalid,Corrupt,Io,Unknown,Legacy,Unsupported};
// One platform transaction worker. No App invocation, package publication or
// reboot here. VFS write must sync before returning; close errors are observed.
class Ap01SetJournalV3 {
    Ap01VfsOps io;uint8_t device[6];
    Ap01SetRecordV3 record{};bool resolved=false,present=false;unsigned slot=0;
    Ap01SetJournalResultV3 read(unsigned,uint8_t *,bool &);
public:
    Ap01SetJournalV3(const Ap01VfsOps &,const uint8_t mac[6]);
    Ap01SetJournalResultV3 load();
    Ap01SetJournalResultV3 save(const Ap01SetRecordV3 &);
    const Ap01SetRecordV3 *current()const{return resolved&&present?&record:nullptr;}
    bool writable()const{return resolved;}
};
