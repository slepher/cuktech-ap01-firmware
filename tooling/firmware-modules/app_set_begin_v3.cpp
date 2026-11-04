#include "app_set_begin_v3.h"
#include "native_integrity_0041.h"
#include <string.h>
using R=Ap01SetBeginResultV3;using P=Ap01SetPhaseV3;
R ap01PlanSetBeginV3(const Ap01SetJournalV3 &journal,const Ap01ManifestV3 *old,const Ap01ManifestV3 &candidate,
    const uint8_t transaction[16],const uint8_t mac[6],const char *principal,uint64_t freeBytes,
    uint64_t maintenanceReserve,Ap01SetRecordV3 &plan){
    plan={};
    if(!journal.writable())return R::Unknown;
    if(!transaction||!mac||!principal||candidate.count>8||(old&&old->count>8))return R::Invalid;
    unsigned length=0;while(length<65&&principal[length]){unsigned char c=principal[length++];if(c<33||c>126)return R::Invalid;}
    if(!length||length>64)return R::Invalid;
    Ap01SetRecordV3 next{};next.sequence=1;
    memcpy(next.transaction,transaction,16);memcpy(next.mac,mac,6);memcpy(next.principal,principal,length);
    if(old){next.oldVersion=old->sequence;memcpy(next.oldDigest,old->digest,32);}
    next.newVersion=candidate.sequence;memcpy(next.newDigest,candidate.digest,32);
    for(unsigned i=0;i<candidate.count;++i){const auto &entry=candidate.entries[i];bool unchanged=false;
        if(old)for(unsigned j=0;j<old->count;++j)if(!strcmp(entry.id,old->entries[j].id)){
            unchanged=!memcmp(entry.digest,old->entries[j].digest,32);break;
        }
        if(!unchanged){next.changedMask|=uint8_t(1u<<i);next.changedBytes+=entry.package_bytes;}
    }
    // Fixed domain and canonical fields; no C++ padding or host-endian integers.
    Ap01Sha256 hash;const uint8_t domain[]="AP01-SET-BEGIN-3";hash.update(domain,sizeof(domain)-1);
    hash.update(mac,6);hash.update(transaction,16);hash.update((const uint8_t*)next.principal,65);
    hash.update(next.oldDigest,32);hash.update(next.newDigest,32);
    uint8_t versions[16];for(unsigned i=0;i<8;++i){versions[i]=uint8_t(next.oldVersion>>(8*i));versions[8+i]=uint8_t(next.newVersion>>(8*i));}
    hash.update(versions,sizeof(versions));hash.finish(next.requestDigest);
    uint8_t encoded[AP01_SET_RECORD_BYTES_V3];if(!ap01EncodeSetRecordV3(next,encoded))return R::Invalid;
    const auto *current=journal.current();
    if(current){
        if(!memcmp(current->transaction,transaction,16)){
            if(memcmp(current->mac,next.mac,6)||memcmp(current->principal,next.principal,65)||
                memcmp(current->requestDigest,next.requestDigest,32)||current->changedMask!=next.changedMask||current->changedBytes!=next.changedBytes)
                return R::Conflict;
            plan=*current;return R::Replay; // Preserve phase, sequence, Ready and received.
        }
        if(current->cleanupPending||(current->phase!=P::Succeeded&&current->phase!=P::FailedRolledBack&&current->phase!=P::Cancelled))return R::Busy;
        if(!ap01SetTransitionV3(*current,next))return R::Conflict;
    }else if(old)return R::Conflict; // Bootstrap cannot claim an unjournaled active set.
    // Worst case: all changed packages, old+candidate canonical Manifests, two
    // temporary Manifest copies, two journal records; don't guess dedup savings.
    constexpr uint64_t manifestMax=64+8*160+56*40;
    uint64_t required=next.changedBytes+4*manifestMax+2*AP01_SET_RECORD_BYTES_V3;
    if(freeBytes<maintenanceReserve||required>freeBytes-maintenanceReserve)return R::Space;
    plan=next;return R::New;
}

Ap01ManifestPublishResultV3 ap01PublishManifestV3(const Ap01VfsOps &io,const Apx2Reader &input,
    const Ap01ManifestLimitsV3 &limits,Ap01ManifestV3 &validated){
    using Result=Ap01ManifestPublishResultV3;
    if(ap01ReadManifestV3(input,limits,validated)!=Ap01ManifestErrorV3::Ok)return Result::Invalid;
    if(!io.exists||!io.open||!io.close||!io.size||!io.read||!io.write||!io.rename)return Result::Storage;
    char final[112]="/resource/app-store/manifests/",temporary[112];
    constexpr unsigned prefix=sizeof("/resource/app-store/manifests/")-1;const char *hex="0123456789abcdef";
    for(unsigned i=0;i<32;++i){final[prefix+2*i]=hex[validated.digest[i]>>4];final[prefix+2*i+1]=hex[validated.digest[i]&15];}
    memcpy(final+prefix+64,".amf3",6);memcpy(temporary,final,prefix+64);memcpy(temporary+prefix+64,".part",6);
    auto compare=[&](const char *path,bool exact,uint32_t &size){
        int fd=io.open(io.context,path,0);if(fd<0)return Result::Storage;
        int32_t length=io.size(io.context,fd);Result result=Result::Ok;
        if(length<0)result=Result::Storage;
        else if(uint32_t(length)>input.size||(exact&&uint32_t(length)!=input.size))result=Result::Conflict;
        else {
            size=uint32_t(length);uint8_t actual[256],expected[256];
            for(uint32_t at=0;at<size;){uint32_t n=size-at;if(n>256)n=256;
                if(!input.read(input.context,at,expected,n)||io.read(io.context,fd,actual,n)!=int(n)){result=Result::Storage;break;}
                if(memcmp(actual,expected,n)){result=Result::Conflict;break;}at+=n;
            }
        }
        if(io.close(io.context,fd))result=Result::Storage;
        return result;
    };
    uint32_t size=0;int exists=io.exists(io.context,final);if(exists<0)return Result::Storage;
    if(exists)return compare(final,true,size); // Never overwrite a content-addressed file.
    exists=io.exists(io.context,temporary);if(exists<0)return Result::Storage;
    if(exists){auto result=compare(temporary,false,size);if(result!=Result::Ok)return result;}
    int fd=io.open(io.context,temporary,2);if(fd<0)return Result::Unknown;
    bool okay=true;uint8_t buffer[256];
    for(uint32_t at=size;at<input.size;){uint32_t n=input.size-at;if(n>256)n=256;
        if(!input.read(input.context,at,buffer,n)||io.write(io.context,fd,buffer,n)!=int(n)){okay=false;break;}at+=n;
    }
    // Re-sync even an already complete tail whose previous write lost its ACK.
    if(okay&&io.write(io.context,fd,buffer,0)!=0)okay=false;
    if(io.close(io.context,fd))okay=false;
    if(!okay||compare(temporary,true,size)!=Result::Ok)return Result::Unknown;
    if(io.rename(io.context,temporary,final))return Result::Unknown;
    return compare(final,true,size)==Result::Ok?Result::Ok:Result::Unknown;
}

#include <memory>
#include <new>
Ap01SetBeginResultV3 ap01BeginSetV3(Ap01SetJournalV3 &journal,const Ap01VfsOps &io,const Apx2Reader *old,
    const Apx2Reader &candidate,const Ap01ManifestLimitsV3 &limits,const uint8_t transaction[16],
    const uint8_t mac[6],const char *principal,uint64_t maintenanceReserve,
    Ap01ManifestV3 &validated,Ap01SetRecordV3 &plan){
    if(!journal.writable())return R::Unknown;
    if(ap01ReadManifestV3(candidate,limits,validated)!=Ap01ManifestErrorV3::Ok)return R::Invalid;
    std::unique_ptr<Ap01ManifestV3> previous;
    if(old){
        previous.reset(new(std::nothrow) Ap01ManifestV3);if(!previous)return R::Invalid;
        if(ap01ReadManifestV3(*old,limits,*previous)!=Ap01ManifestErrorV3::Ok)return R::Invalid;
    }
    auto result=ap01PlanSetBeginV3(journal,previous.get(),validated,transaction,mac,principal,UINT64_MAX,0,plan);
    if(result!=R::New)return result;
    if(!io.statfs||!io.exists||!io.mkdir)return R::Storage;
    uint64_t total=0,free=0;
    if(io.statfs(io.context,"/resource",&total,&free)||free>total)return R::Storage;
    result=ap01PlanSetBeginV3(journal,previous.get(),validated,transaction,mac,principal,free,maintenanceReserve,plan);
    if(result!=R::New)return result;
    const char *directories[]={"/resource/app-store","/resource/app-store/manifests","/resource/app-store/packages","/resource/app-store/incoming"};
    for(auto path:directories){int exists=io.exists(io.context,path);if(exists<0)return R::Storage;
        if(!exists&&io.mkdir(io.context,path))return R::Unknown;}
    if(old){auto published=ap01PublishManifestV3(io,*old,limits,*previous);
        if(published!=Ap01ManifestPublishResultV3::Ok)return published==Ap01ManifestPublishResultV3::Unknown?R::Unknown:R::Storage;}
    auto published=ap01PublishManifestV3(io,candidate,limits,validated);
    if(published!=Ap01ManifestPublishResultV3::Ok)return published==Ap01ManifestPublishResultV3::Unknown?R::Unknown:R::Storage;
    auto saved=journal.save(plan);
    if(saved!=Ap01SetJournalResultV3::Ok)return saved==Ap01SetJournalResultV3::Unknown?R::Unknown:R::Invalid;
    plan=*journal.current();return R::New;
}
