#include "app_set_journal_v3.h"
#include "native_integrity_0041.h"
#include <string.h>
#include <initializer_list>
namespace {
using P=Ap01SetPhaseV3;using R=Ap01SetJournalResultV3;
uint32_t u32(const uint8_t *p){return uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16|uint32_t(p[3])<<24;}
uint64_t u64(const uint8_t *p){return uint64_t(u32(p))|uint64_t(u32(p+4))<<32;}
void put(uint8_t *p,uint64_t n,unsigned bytes=4){for(unsigned i=0;i<bytes;++i)p[i]=uint8_t(n>>(8*i));}
bool any(const uint8_t *p,unsigned n){while(n--)if(*p++)return true;return false;}
bool terminal(P p){return p==P::Succeeded||p==P::FailedRolledBack||p==P::Cancelled||p==P::RecoveryRequired;}
bool valid(const Ap01SetRecordV3 &r){
    unsigned phase=unsigned(r.phase);
    if(!r.sequence||phase<1||phase>10||!r.newVersion||r.newVersion<=r.oldVersion||
       any(r.oldDigest,32)!=(r.oldVersion!=0)||!any(r.newDigest,32)||!memcmp(r.oldDigest,r.newDigest,32)||
       !any(r.transaction,16)||!any(r.mac,6)||!any(r.requestDigest,32)||r.trialStarts>1||r.rollbackStarts>1||
       r.cleanupPending>1||(!terminal(r.phase)&&r.cleanupPending)||
       (r.readyMask&~r.changedMask)||bool(r.trialBoot)!=bool(r.trialStarts)||
       bool(r.rollbackBoot)!=bool(r.rollbackStarts)||(r.rollbackBoot&&r.rollbackBoot==r.trialBoot))return false;
    unsigned changes=0;for(unsigned i=0;i<8;++i)changes+=(r.changedMask>>i)&1;
    if((!changes&&r.changedBytes)||(changes&&r.changedBytes<uint64_t(changes)*256))return false;
    unsigned n=0;while(n<65&&r.principal[n]){unsigned char c=r.principal[n++];if(c<33||c>126)return false;}
    if(!n||n==65)return false;
    while(n<65)if(r.principal[n++])return false;
    if(r.phase!=P::Receiving&&r.phase!=P::Cancelled&&r.phase!=P::RecoveryRequired&&r.readyMask!=r.changedMask)return false;
    switch(r.phase){
    case P::Receiving:case P::Ready:case P::SwitchPending:
        return !r.trialStarts&&!r.rollbackStarts&&!r.error;
    case P::TrialStarted:case P::Succeeded:return r.trialStarts==1&&!r.rollbackStarts&&!r.error;
    case P::RollbackPending:return !r.rollbackStarts&&r.error;
    case P::RollbackStarted:case P::FailedRolledBack:return r.rollbackStarts==1&&r.error;
    case P::Cancelled:return !r.trialStarts&&!r.rollbackStarts;
    case P::RecoveryRequired:return r.error!=0;
    }
    return false;
}
const char *path(unsigned i){return i?"/resource/app-store/update.1":"/resource/app-store/update.0";}
}
bool ap01EncodeSetRecordV3(const Ap01SetRecordV3 &r,uint8_t *out){
    memset(out,0,AP01_SET_RECORD_BYTES_V3);if(!valid(r))return false;
    memcpy(out,"AUT3",4);put(out+4,1);put(out+8,AP01_SET_RECORD_BYTES_V3);put(out+12,uint32_t(r.phase));
    put(out+16,r.sequence,8);put(out+24,r.oldVersion,8);put(out+32,r.newVersion,8);
    put(out+40,r.trialBoot,8);put(out+48,r.rollbackBoot,8);
    out[56]=r.trialStarts;out[57]=r.rollbackStarts;out[58]=r.cleanupPending;out[59]=r.changedMask;out[60]=r.readyMask;
    put(out+64,r.changedBytes,8);put(out+72,r.error);
    memcpy(out+80,r.transaction,16);memcpy(out+96,r.mac,6);memcpy(out+104,r.oldDigest,32);
    memcpy(out+136,r.newDigest,32);memcpy(out+168,r.requestDigest,32);memcpy(out+200,r.principal,65);
    put(out+316,ap01_native_crc32(out,316));return true;
}
bool ap01DecodeSetRecordV3(const uint8_t *in,Ap01SetRecordV3 &out){
    out={};if(memcmp(in,"AUT3",4)||u32(in+4)!=1||u32(in+8)!=AP01_SET_RECORD_BYTES_V3||u32(in+316)!=ap01_native_crc32(in,316))return false;
    if(any(in+61,3)||any(in+76,4)||any(in+102,2)||any(in+265,51))return false;
    Ap01SetRecordV3 r{};r.phase=P(u32(in+12));r.sequence=u64(in+16);r.oldVersion=u64(in+24);r.newVersion=u64(in+32);
    r.trialBoot=u64(in+40);r.rollbackBoot=u64(in+48);r.trialStarts=in[56];r.rollbackStarts=in[57];
    r.cleanupPending=in[58];r.changedMask=in[59];r.readyMask=in[60];r.changedBytes=u64(in+64);r.error=u32(in+72);
    memcpy(r.transaction,in+80,16);memcpy(r.mac,in+96,6);memcpy(r.oldDigest,in+104,32);
    memcpy(r.newDigest,in+136,32);memcpy(r.requestDigest,in+168,32);memcpy(r.principal,in+200,65);
    if(!valid(r))return false;
    out=r;return true;
}
bool ap01SetTransitionV3(const Ap01SetRecordV3 &a,const Ap01SetRecordV3 &b){
    if(!valid(a)||!valid(b)||memcmp(a.mac,b.mac,6))return false;
    if(memcmp(a.transaction,b.transaction,16)){
        if((a.phase!=P::Succeeded&&a.phase!=P::FailedRolledBack&&a.phase!=P::Cancelled)||a.cleanupPending||
           b.phase!=P::Receiving||b.readyMask)return false;
        const uint8_t *active=a.phase==P::Succeeded?a.newDigest:a.oldDigest;
        uint64_t version=a.phase==P::Succeeded?a.newVersion:a.oldVersion;
        return !memcmp(b.oldDigest,active,32)&&b.oldVersion==version;
    }
    if(memcmp(a.principal,b.principal,65)||memcmp(a.requestDigest,b.requestDigest,32)||
       memcmp(a.oldDigest,b.oldDigest,32)||memcmp(a.newDigest,b.newDigest,32)||
       a.oldVersion!=b.oldVersion||a.newVersion!=b.newVersion||a.changedMask!=b.changedMask||a.changedBytes!=b.changedBytes||
       (b.readyMask&a.readyMask)!=a.readyMask||(a.error&&a.error!=b.error))return false;
    bool trial=b.phase==P::TrialStarted&&a.phase!=b.phase,rollback=b.phase==P::RollbackStarted&&a.phase!=b.phase;
    if(b.trialStarts!=a.trialStarts+trial||b.rollbackStarts!=a.rollbackStarts+rollback||
       (!trial&&a.trialBoot!=b.trialBoot)||(!rollback&&a.rollbackBoot!=b.rollbackBoot))return false;
    if(a.phase==b.phase)return b.cleanupPending<=a.cleanupPending&&a.error==b.error;
    switch(a.phase){
    case P::Receiving:return b.phase==P::Ready||b.phase==P::Cancelled||b.phase==P::RecoveryRequired;
    case P::Ready:return b.phase==P::SwitchPending||b.phase==P::Cancelled||b.phase==P::RecoveryRequired;
    case P::SwitchPending:return b.phase==P::TrialStarted||b.phase==P::RollbackPending||b.phase==P::RecoveryRequired;
    case P::TrialStarted:return b.phase==P::Succeeded||b.phase==P::RollbackPending||b.phase==P::RecoveryRequired;
    case P::RollbackPending:return b.phase==P::RollbackStarted||b.phase==P::RecoveryRequired;
    case P::RollbackStarted:return b.phase==P::FailedRolledBack||b.phase==P::RecoveryRequired;
    default:return false;
    }
}
Ap01SetJournalV3::Ap01SetJournalV3(const Ap01VfsOps &ops,const uint8_t mac[6]):io(ops){memcpy(device,mac,6);}
R Ap01SetJournalV3::read(unsigned i,uint8_t *out,bool &found){
    int exists=io.exists(io.context,path(i));if(exists<0)return R::Io;
    found=exists!=0;if(!found)return R::Empty;
    int fd=io.open(io.context,path(i),0);if(fd<0)return R::Io;
    int32_t size=io.size(io.context,fd);R result=R::Ok;
    if(size<0)result=R::Io;
    else if(size!=int32_t(AP01_SET_RECORD_BYTES_V3))result=R::Corrupt;
    if(result==R::Ok&&io.read(io.context,fd,out,AP01_SET_RECORD_BYTES_V3)!=int(AP01_SET_RECORD_BYTES_V3))result=R::Io;
    if(io.close(io.context,fd))result=R::Io;
    if(result==R::Ok&&!memcmp(out,"AUT2",4))return R::Legacy;
    if(result==R::Ok&&!memcmp(out,"AUT3",4)&&u32(out+4)!=1)return R::Unsupported;
    return result;
}
R Ap01SetJournalV3::load(){
    resolved=false;present=false;record={};
    if(!io.exists||!io.open||!io.close||!io.read||!io.size||!io.write)return R::Io;
    for(const char *old:{"/resource/codex-status/app-update.0","/resource/codex-status/app-update.1"}){
        int exists=io.exists(io.context,old);if(exists<0)return R::Io;if(exists)return R::Legacy;
    }
    uint8_t bytes[2][AP01_SET_RECORD_BYTES_V3]{};Ap01SetRecordV3 records[2];bool found[2]{},good[2]{};
    for(unsigned i=0;i<2;++i){auto result=read(i,bytes[i],found[i]);
        if(result==R::Io||result==R::Legacy||result==R::Unsupported)return result;
        good[i]=result==R::Ok&&ap01DecodeSetRecordV3(bytes[i],records[i]);
        if(good[i]&&memcmp(records[i].mac,device,6))return R::Corrupt;
    }
    if(!found[0]&&!found[1]){resolved=true;return R::Empty;}
    if(!good[0]&&!good[1])return R::Corrupt;
    unsigned selected=good[1]&&(!good[0]||records[1].sequence>records[0].sequence)?1:0;
    if(good[0]&&good[1]){
        auto &newer=records[selected];auto &older=records[selected^1];uint64_t gap=newer.sequence-older.sequence;
        if(gap>1||(!gap&&memcmp(bytes[0],bytes[1],AP01_SET_RECORD_BYTES_V3))||
           (gap&&!ap01SetTransitionV3(older,newer)))return R::Corrupt;
    }
    record=records[selected];slot=selected;resolved=true;present=true;return R::Ok;
}
R Ap01SetJournalV3::save(const Ap01SetRecordV3 &next){
    if(!resolved)return R::Unknown;
    if((present&&record.sequence==UINT64_MAX)||memcmp(next.mac,device,6))return R::Invalid;
    Ap01SetRecordV3 candidate=next;candidate.sequence=present?record.sequence+1:1;
    uint8_t bytes[AP01_SET_RECORD_BYTES_V3],back[AP01_SET_RECORD_BYTES_V3];
    if(!ap01EncodeSetRecordV3(candidate,bytes)||(present?!ap01SetTransitionV3(record,candidate):
       candidate.phase!=P::Receiving||candidate.readyMask))return R::Invalid;
    unsigned target=present?slot^1:0;resolved=false;
    int fd=io.open(io.context,path(target),1);if(fd<0)return R::Unknown;
    bool okay=io.write(io.context,fd,bytes,sizeof(bytes))==int(sizeof(bytes));
    if(io.close(io.context,fd))okay=false;
    if(!okay)return R::Unknown;
    bool found=false;if(read(target,back,found)!=R::Ok||!found||memcmp(bytes,back,sizeof(bytes)))return R::Unknown;
    record=candidate;slot=target;present=true;resolved=true;return R::Ok;
}
