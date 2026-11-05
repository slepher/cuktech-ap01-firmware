#pragma once
#include "app_set_http_v3.h"
#include "app_set_begin_v3.h"
#include "app_set_download_v3.h"
#include "app_set_commit_v3.h"
#include "app_set_cleanup_v3.h"
#include "app_set_files_v3.h"
#include <memory>
#include "app_supervision_v3.h"
// Called under the platform operation lease, after device-code authentication.
// Journal is shared with the boot worker under that same lease.
class Ap01SetServiceV3 {
    struct ManifestFile {
        uint8_t bytes[3584]{};uint32_t size=0;Ap01ManifestV3 parsed{};
        Apx2Reader reader();
    };
    Ap01VfsOps io;Ap01SetJournalV3 &journal;Ap01AppWriteGateV3 &gate;Ap01AppRebootV3 &reboot;
    Ap01ManifestLimitsV3 limits;uint64_t boot,reserve;uint8_t mac[6];char device[13]{};
    std::unique_ptr<ManifestFile> previous,candidate;
    std::unique_ptr<Ap01SetDownloadV3> download;
    std::unique_ptr<Ap01SetCommitV3> commit;
    uint8_t commitTransaction[16]{};
    void *runtimeContext=nullptr;
    Ap01RuntimeSnapshotV3 (*runtimeSnapshot)(void *)=nullptr;
    bool frozen=false,cleanupAttempted=false;
    uint32_t cleanupAt=0;
    bool readManifest(std::unique_ptr<ManifestFile> &,const uint8_t *,uint64_t);
    bool hydrate();
    Ap01HttpReply reply(int,const char *,bool disclose=true,bool storage=false);
public:
    Ap01SetServiceV3(const Ap01VfsOps &,Ap01SetJournalV3 &,Ap01AppWriteGateV3 &,Ap01AppRebootV3 &,
        const Ap01ManifestLimitsV3 &,const uint8_t mac[6],uint64_t boot,uint64_t maintenanceReserve);
    void runtime(void *context,Ap01RuntimeSnapshotV3 (*snapshot)(void *)){runtimeContext=context;runtimeSnapshot=snapshot;}
    // Boot worker, under the same operation lease as handle().
    void tick(uint32_t now);
    Ap01HttpReply handle(const Ap01HttpRequest &,const char *principal,uint32_t now);
};
