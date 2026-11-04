#pragma once
#include "app_set_journal_v3.h"
#include "app_manifest_v3.h"
enum class Ap01SetDownloadResultV3 {Ok,Conflict,Bounds,Storage,Unknown,State,Package};
// Single transaction worker. Manifest was validated and durably published before
// Receiving; authentication, capacity reservation and parent directories belong
// to begin. No deletion or truncation of an existing partial file.
class Ap01SetDownloadV3 {
    Ap01VfsOps io;Ap01SetJournalV3 &journal;const Ap01ManifestV3 &manifest;
    bool uncertain=false;
public:
    Ap01SetDownloadV3(const Ap01VfsOps &v,Ap01SetJournalV3 &j,const Ap01ManifestV3 &m):io(v),journal(j),manifest(m){}
    Ap01SetDownloadResultV3 ready(const uint8_t transaction[16],unsigned index,uint32_t dataVersion);
    // After Unknown reconstruct only after journal.load and revalidate Manifest.
    Ap01SetDownloadResultV3 chunk(const uint8_t transaction[16],unsigned index,uint32_t offset,const uint8_t *,uint32_t size);
};
