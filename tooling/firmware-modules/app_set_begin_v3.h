#pragma once
#include "app_set_journal_v3.h"
#include "app_manifest_v3.h"
enum class Ap01SetBeginResultV3 {New,Replay,Conflict,Busy,Space,Invalid,Unknown,Storage};
// Pure admission plan. Both Manifests are parsed/validated immutable objects;
// old=nullptr means initial empty installation. No file or journal mutation.
// Caller must reserve this space under the maintenance lease, durably publish
// both referenced Manifests, then journal.save(plan). Never save before publish.
Ap01SetBeginResultV3 ap01PlanSetBeginV3(const Ap01SetJournalV3 &,const Ap01ManifestV3 *old,
    const Ap01ManifestV3 &candidate,const uint8_t transaction[16],const uint8_t mac[6],const char *principal,
    uint64_t freeBytes,uint64_t maintenanceReserve,Ap01SetRecordV3 &plan);

enum class Ap01ManifestPublishResultV3 {Ok,Invalid,Conflict,Storage,Unknown};
// Single installer worker, immutable input. Parent directories already prepared.
// Unknown requires observing/reconciling storage before proceeding to journal.save.
Ap01ManifestPublishResultV3 ap01PublishManifestV3(const Ap01VfsOps &,const Apx2Reader &,
    const Ap01ManifestLimitsV3 &,Ap01ManifestV3 &validated);
// Actual begin under the single platform maintenance-operation lease. Replay
// does not mutate storage. On New, creates store directories, queries capacity,
// publishes both Manifests, and only then persists Receiving. Unknown freezes
// the caller's transaction executor until journal/storage reconciliation.
Ap01SetBeginResultV3 ap01BeginSetV3(Ap01SetJournalV3 &,const Ap01VfsOps &,const Apx2Reader *old,
    const Apx2Reader &candidate,const Ap01ManifestLimitsV3 &,const uint8_t transaction[16],
    const uint8_t mac[6],const char *principal,uint64_t maintenanceReserve,
    Ap01ManifestV3 &validated,Ap01SetRecordV3 &plan);
