#pragma once
#include "app_set_journal_v3.h"
#include "app_manifest_v3.h"
enum class Ap01SetCleanupResultV3 {Ok,State,Identity,Storage,Unknown};
// Single installer worker under maintenance lease. Parsed Manifests must match
// the journal. Retain receipt Manifest metadata; remove only obsolete packages
// in this transaction and its temporary files. No directory sweep.
Ap01SetCleanupResultV3 ap01CleanupSetV3(Ap01SetJournalV3 &,const Ap01VfsOps &,
    const Ap01ManifestV3 *old,const Ap01ManifestV3 &candidate);
