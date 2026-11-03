#include "app_update_record_0041.h"
#include "native_integrity_0041.h"

namespace {
uint32_t u32(const uint8_t *p){return uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16|uint32_t(p[3])<<24;}
void put(uint8_t *p,uint32_t v){for(unsigned i=0;i<4;++i)p[i]=uint8_t(v>>(8*i));}
bool nonzero(const uint8_t *p,unsigned n){while(n--)if(*p++)return true;return false;}
bool valid(const Ap01AppUpdateRecord &r) {
    unsigned phase=unsigned(r.phase);
    if(!r.sequence||phase<1||phase>10||r.total<256||r.received>r.total||
       r.trialStarts>1||r.rollbackStarts>1||r.cleanupPending>1||
       !nonzero(r.transaction,16)||!nonzero(r.mac,6)||!nonzero(r.newDigest,32))return false;
    unsigned length=0;while(length<65&&r.principal[length]) {
        unsigned char c=r.principal[length++];if(c<33||c>126)return false;
    }
    if(!length||length==65)return false;
    while(length<65)if(r.principal[length++])return false;
    bool old=nonzero(r.oldDigest,32);
    if(old&&!memcmp(r.oldDigest,r.newDigest,32))return false;
    if(r.rollbackStarts&&!old)return false;
    if(r.cleanupPending&&r.phase!=Ap01AppUpdatePhase::Succeeded&&
       r.phase!=Ap01AppUpdatePhase::FailedRolledBack&&r.phase!=Ap01AppUpdatePhase::Cancelled&&
       r.phase!=Ap01AppUpdatePhase::RecoveryRequired)return false;
    using P=Ap01AppUpdatePhase;
    if(r.phase!=P::Receiving&&r.phase!=P::Cancelled&&r.phase!=P::RecoveryRequired&&r.received!=r.total)return false;
    switch(r.phase) {
    case P::Receiving:case P::Ready:case P::SwitchPending:case P::Cancelled:
        return !r.trialStarts&&!r.rollbackStarts&&!r.generation;
    case P::TrialStarted:case P::Succeeded:
        return r.trialStarts==1&&!r.rollbackStarts&&r.generation;
    case P::RollbackPending:return old&&!r.rollbackStarts&&!r.generation;
    case P::RollbackStarted:case P::FailedRolledBack:return old&&r.rollbackStarts==1&&r.generation;
    case P::RecoveryRequired:return !r.generation;
    }
    return false;
}
const char *path(unsigned slot){return slot?"/app-update.1":"/app-update.0";}
bool transition(const Ap01AppUpdateRecord &a,const Ap01AppUpdateRecord &b) {
    using P=Ap01AppUpdatePhase;
    if(memcmp(a.transaction,b.transaction,16)) {
        bool terminal=a.phase==P::Succeeded||a.phase==P::FailedRolledBack||
                      a.phase==P::Cancelled||a.phase==P::RecoveryRequired;
        return terminal&&!a.cleanupPending&&b.phase==P::Receiving&&!b.received;
    }
    if(memcmp(a.mac,b.mac,6)||memcmp(a.principal,b.principal,65)||
       memcmp(a.oldDigest,b.oldDigest,32)||memcmp(a.newDigest,b.newDigest,32)||
       a.total!=b.total||b.received<a.received||b.trialStarts<a.trialStarts||
       b.rollbackStarts<a.rollbackStarts)return false;
    if(b.trialStarts!=a.trialStarts+(b.phase==P::TrialStarted&&a.phase!=b.phase)||
       b.rollbackStarts!=a.rollbackStarts+(b.phase==P::RollbackStarted&&a.phase!=b.phase))return false;
    if((b.phase==P::Succeeded||b.phase==P::FailedRolledBack)&&b.generation!=a.generation)return false;
    if(a.phase==b.phase) {
        return a.generation==b.generation&&a.trialStarts==b.trialStarts&&
               a.rollbackStarts==b.rollbackStarts&&b.cleanupPending<=a.cleanupPending;
    }
    switch(a.phase) {
    case P::Receiving:return b.phase==P::Ready||b.phase==P::Cancelled||b.phase==P::RecoveryRequired;
    case P::Ready:return b.phase==P::SwitchPending||b.phase==P::Cancelled||b.phase==P::RecoveryRequired;
    case P::SwitchPending:return b.phase==P::TrialStarted||b.phase==P::RollbackPending||b.phase==P::RecoveryRequired;
    case P::TrialStarted:return b.phase==P::Succeeded||b.phase==P::RollbackPending||b.phase==P::RecoveryRequired;
    case P::RollbackPending:return b.phase==P::RollbackStarted||b.phase==P::RecoveryRequired;
    case P::RollbackStarted:return b.phase==P::FailedRolledBack||b.phase==P::RecoveryRequired;
    default:return false;
    }
}
}
bool ap01EncodeAppUpdate(const Ap01AppUpdateRecord &r,uint8_t out[256]) {
    memset(out,0,256);if(!valid(r))return false;
    memcpy(out,"AUT2",4);put(out+4,1);put(out+8,256);put(out+12,uint32_t(r.phase));
    put(out+16,uint32_t(r.sequence));put(out+20,uint32_t(r.sequence>>32));
    put(out+24,r.total);put(out+28,r.received);put(out+32,r.generation);
    out[36]=r.trialStarts;out[37]=r.rollbackStarts;out[38]=r.cleanupPending;
    memcpy(out+40,r.transaction,16);memcpy(out+56,r.mac,6);
    memcpy(out+64,r.oldDigest,32);memcpy(out+96,r.newDigest,32);memcpy(out+128,r.principal,65);
    put(out+252,ap01_native_crc32(out,252));return true;
}
bool ap01DecodeAppUpdate(const uint8_t in[256],Ap01AppUpdateRecord &out) {
    out={};if(memcmp(in,"AUT2",4)||u32(in+4)!=1||u32(in+8)!=256||
       u32(in+252)!=ap01_native_crc32(in,252)||in[39]||in[62]||in[63])return false;
    for(unsigned i=193;i<252;++i)if(in[i])return false;
    Ap01AppUpdateRecord r{};r.phase=Ap01AppUpdatePhase(u32(in+12));
    r.sequence=uint64_t(u32(in+16))|(uint64_t(u32(in+20))<<32);
    r.total=u32(in+24);r.received=u32(in+28);r.generation=u32(in+32);
    r.trialStarts=in[36];r.rollbackStarts=in[37];r.cleanupPending=in[38];
    memcpy(r.transaction,in+40,16);memcpy(r.mac,in+56,6);memcpy(r.oldDigest,in+64,32);
    memcpy(r.newDigest,in+96,32);memcpy(r.principal,in+128,65);
    if(!valid(r))return false;
    out=r;return true;
}
Ap01AppUpdateJournal0041::Ap01AppUpdateJournal0041(LittleFSClass &storage,const uint8_t mac[6]):fs(storage){memcpy(device,mac,6);}
Ap01AppJournalResult Ap01AppUpdateJournal0041::load() {
    writable=false;exists=false;record={};
    Ap01AppUpdateRecord found[2];bool good[2]={};unsigned present=0;
    uint8_t bytes[2][256];
    for(unsigned i=0;i<2;++i) {
        int status=fs.inspect(path(i));if(status<0)return Ap01AppJournalResult::Io;
        if(!status)continue;
        ++present;
        File f=fs.open(path(i),"r");if(!f)return Ap01AppJournalResult::Io;
        if(f.size()!=256)continue;
        if(f.read(bytes[i],256)!=256)return Ap01AppJournalResult::Io;
        good[i]=ap01DecodeAppUpdate(bytes[i],found[i]);
        if(good[i]&&memcmp(found[i].mac,device,6))return Ap01AppJournalResult::Corrupt;
    }
    if(!present){writable=true;return Ap01AppJournalResult::Empty;}
    if(!good[0]&&!good[1])return Ap01AppJournalResult::Corrupt;
    unsigned selected=good[1]&&(!good[0]||found[1].sequence>found[0].sequence)?1:0;
    if(good[0]&&good[1]) {
        uint64_t a=found[selected].sequence,b=found[selected^1].sequence;
        if((a==b&&memcmp(bytes[0],bytes[1],256))||a-b>1)return Ap01AppJournalResult::Corrupt;
    }
    record=found[selected];slot=selected;exists=true;writable=true;return Ap01AppJournalResult::Ok;
}
Ap01AppJournalResult Ap01AppUpdateJournal0041::save(const Ap01AppUpdateRecord &next) {
    if(!writable)return Ap01AppJournalResult::Unknown;
    if((exists&&record.sequence==UINT64_MAX)||memcmp(next.mac,device,6))return Ap01AppJournalResult::Invalid;
    if(exists?!transition(record,next):next.phase!=Ap01AppUpdatePhase::Receiving||next.received)
        return Ap01AppJournalResult::Invalid;
    Ap01AppUpdateRecord candidate=next;candidate.sequence=exists?record.sequence+1:1;
    uint8_t bytes[256],back[256];if(!ap01EncodeAppUpdate(candidate,bytes))return Ap01AppJournalResult::Invalid;
    // Alternate by committed sequence; never truncate the current committed copy.
    unsigned target=exists?slot^1:0;
    const char *name=path(target);writable=false;
    File f=fs.open(name,"w");if(!f||f.write(bytes,256)!=256)return Ap01AppJournalResult::Unknown;
    f.close();f=fs.open(name,"r");
    if(!f||f.size()!=256||f.read(back,256)!=256||memcmp(bytes,back,256))return Ap01AppJournalResult::Unknown;
    record=candidate;slot=target;exists=true;writable=true;return Ap01AppJournalResult::Ok;
}
