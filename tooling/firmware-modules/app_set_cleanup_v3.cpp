#include "app_set_cleanup_v3.h"
#include <string.h>
using R=Ap01SetCleanupResultV3;using P=Ap01SetPhaseV3;
namespace {
void path(char *out,const char *prefix,const uint8_t *digest,unsigned bytes,const char *suffix){
    strcpy(out,prefix);unsigned n=strlen(prefix);const char *hex="0123456789abcdef";
    for(unsigned i=0;i<bytes;++i){out[n+2*i]=hex[digest[i]>>4];out[n+2*i+1]=hex[digest[i]&15];}
    strcpy(out+n+2*bytes,suffix);
}
}
R ap01CleanupSetV3(Ap01SetJournalV3 &journal,const Ap01VfsOps &io,const Ap01ManifestV3 *old,const Ap01ManifestV3 &candidate){
    if(!journal.writable())return R::Unknown;
    const auto *r=journal.current();if(!r)return R::State;
    if(r->phase!=P::Succeeded&&r->phase!=P::FailedRolledBack&&r->phase!=P::Cancelled)return R::State;
    if(candidate.count>8||(old&&old->count>8)||candidate.sequence!=r->newVersion||memcmp(candidate.digest,r->newDigest,32)||
        (old?(old->sequence!=r->oldVersion||memcmp(old->digest,r->oldDigest,32)):r->oldVersion!=0))return R::Identity;
    if(!r->cleanupPending)return R::Ok;
    if(!io.exists||!io.remove)return R::Storage;
    auto record=*r;
    // Overwrite the other slot with the same terminal decision before deletion.
    // A torn later cleanup-clear can only fall back to this same selected set,
    // never to TrialStarted/rollback state that still needed the loser package.
    if(journal.save(record)!=Ap01SetJournalResultV3::Ok)return R::Unknown;
    const auto *keep=record.phase==P::Succeeded?&candidate:old;
    const auto *obsolete=record.phase==P::Succeeded?old:&candidate;
    auto remove=[&](const char *name){
        int exists=io.exists(io.context,name);if(exists<0)return R::Storage;if(!exists)return R::Ok;
        if(io.remove(io.context,name))return R::Unknown;
        exists=io.exists(io.context,name);return exists==0?R::Ok:exists<0?R::Unknown:R::Storage;
    };
    char name[112];
    if(obsolete)for(unsigned i=0;i<obsolete->count;++i){bool referenced=false;
        if(keep)for(unsigned j=0;j<keep->count;++j)if(!memcmp(obsolete->entries[i].digest,keep->entries[j].digest,32)){referenced=true;break;}
        if(referenced)continue;
        path(name,"/resource/app-store/packages/",obsolete->entries[i].digest,32,".apx2");
        auto result=remove(name);if(result!=R::Ok)return result;
    }
    for(unsigned i=0;i<8;++i){char suffix[]="-0.part";suffix[1]=char('0'+i);
        path(name,"/resource/app-store/incoming/",record.transaction,16,suffix);
        auto result=remove(name);if(result!=R::Ok)return result;
    }
    for(unsigned i=0;i<2;++i){if(i&&!old)continue;
        path(name,"/resource/app-store/manifests/",i?old->digest:candidate.digest,32,".part");
        auto result=remove(name);if(result!=R::Ok)return result;
    }
    record.cleanupPending=0;
    return journal.save(record)==Ap01SetJournalResultV3::Ok?R::Ok:R::Unknown;
}
