#include "app_set_download_v3.h"
#include <string.h>
#include <limits.h>
using R=Ap01SetDownloadResultV3;
namespace {
void incomingPath(const uint8_t *transaction,unsigned index,char *path){
    strcpy(path,"/resource/app-store/incoming/");constexpr unsigned prefix=sizeof("/resource/app-store/incoming/")-1;
    const char *hex="0123456789abcdef";
    for(unsigned i=0;i<16;++i){path[prefix+2*i]=hex[transaction[i]>>4];path[prefix+2*i+1]=hex[transaction[i]&15];}
    path[prefix+32]='-';path[prefix+33]=char('0'+index);memcpy(path+prefix+34,".part",6);
}
R compare(const Ap01VfsOps &io,int fd,uint32_t offset,const uint8_t *bytes,uint32_t n){
    if(io.seek(io.context,fd,int32_t(offset),0)!=int32_t(offset))return R::Storage;
    uint8_t scratch[256];
    while(n){unsigned part=n>sizeof(scratch)?sizeof(scratch):n;
        if(io.read(io.context,fd,scratch,part)!=int(part))return R::Storage;
        if(memcmp(scratch,bytes,part))return R::Conflict;
        bytes+=part;n-=part;
    }return R::Ok;
}
}
R Ap01SetDownloadV3::chunk(const uint8_t transaction[16],unsigned index,uint32_t offset,const uint8_t *bytes,uint32_t n){
    if(uncertain||!journal.writable())return R::Unknown;
    const auto *r=journal.current();
    if(!r||!transaction||memcmp(transaction,r->transaction,16)||memcmp(manifest.digest,r->newDigest,32)||manifest.sequence!=r->newVersion)return R::Conflict;
    if(r->phase!=Ap01SetPhaseV3::Receiving)return R::State;
    if(index>=manifest.count||index>=8||!(r->changedMask&(1u<<index)))return R::Bounds;
    uint32_t total=manifest.entries[index].package_bytes,received=r->received[index];
    if(!bytes||!n||n>1024||total>INT32_MAX||offset>total||n>total-offset||received>total)return R::Bounds;
    if(r->readyMask&(1u<<index))return R::State;
    if(offset>received||(offset<received&&n>received-offset))return R::Conflict;
    if(!io.exists||!io.open||!io.close||!io.read||!io.write||!io.size||!io.seek)return R::Storage;
    char path[100];incomingPath(transaction,index,path);
    int exists=io.exists(io.context,path);if(exists<0)return R::Storage;
    uint32_t size=0,overlap=0;
    if(exists){
        int fd=io.open(io.context,path,0);if(fd<0)return R::Storage;
        int32_t length=io.size(io.context,fd);R result=R::Ok;
        if(length<0||uint32_t(length)<received||uint32_t(length)>total)result=R::Storage;
        else {size=uint32_t(length);overlap=offset<size?size-offset:0;if(overlap>n)overlap=n;
            if(overlap)result=compare(io,fd,offset,bytes,overlap);}
        if(io.close(io.context,fd))result=R::Storage;
        if(result!=R::Ok)return result;
    }else if(received)return R::Storage;
    if(offset<received)return R::Ok;
    if(size>offset+n)return R::Conflict;
    // All later failures have potentially mutated storage: freeze this instance.
    uncertain=true;int fd=io.open(io.context,path,2);if(fd<0)return R::Unknown;
    // Zero-byte write re-syncs a complete unacknowledged tail.
    bool okay=io.write(io.context,fd,bytes+overlap,n-overlap)==int(n-overlap);
    if(io.close(io.context,fd))okay=false;
    if(!okay)return R::Unknown;
    fd=io.open(io.context,path,0);if(fd<0)return R::Unknown;
    okay=io.size(io.context,fd)==int32_t(offset+n)&&compare(io,fd,offset,bytes,n)==R::Ok;
    if(io.close(io.context,fd))okay=false;
    if(!okay)return R::Unknown;
    auto next=*r;next.received[index]=offset+n;
    if(journal.save(next)!=Ap01SetJournalResultV3::Ok)return R::Unknown;
    uncertain=false;return R::Ok;
}

R Ap01SetDownloadV3::ready(const uint8_t transaction[16],unsigned index,uint32_t dataVersion){
    if(uncertain||!journal.writable())return R::Unknown;
    const auto *r=journal.current();
    if(!r||!transaction||memcmp(transaction,r->transaction,16)||memcmp(manifest.digest,r->newDigest,32)||manifest.sequence!=r->newVersion)return R::Conflict;
    if(r->phase!=Ap01SetPhaseV3::Receiving&&r->phase!=Ap01SetPhaseV3::Ready)return R::State;
    if(index>=manifest.count||index>=8||!(r->changedMask&(1u<<index)))return R::Bounds;
    if(!io.exists||!io.open||!io.close||!io.size||!io.seek||!io.read||!io.rename)return R::Storage;
    const auto &entry=manifest.entries[index];
    char final[112]="/resource/app-store/packages/";constexpr unsigned prefix=sizeof("/resource/app-store/packages/")-1;
    const char *hex="0123456789abcdef";
    for(unsigned i=0;i<32;++i){final[prefix+2*i]=hex[entry.digest[i]>>4];final[prefix+2*i+1]=hex[entry.digest[i]&15];}
    memcpy(final+prefix+64,".apx2",6);
    auto validate=[&](const char *path){
        int fd=io.open(io.context,path,0);if(fd<0)return R::Storage;
        int32_t size=io.size(io.context,fd);
        struct Reader {const Ap01VfsOps &io;int fd;} context{io,fd};
        Apx2Reader reader{&context,size<0?0:uint32_t(size),[](void *p,uint32_t at,uint8_t *out,uint32_t n){
            auto &s=*(Reader*)p;
            return at<=INT32_MAX&&s.io.seek(s.io.context,s.fd,int32_t(at),0)==int32_t(at)&&
                s.io.read(s.io.context,s.fd,out,n)==int(n);
        }};
        R result=size<0?R::Storage:ap01CheckManifestPackageV3(entry,reader,dataVersion)==Ap01ManifestErrorV3::Ok?R::Ok:R::Package;
        if(io.close(io.context,fd))result=R::Storage;
        return result;
    };
    int exists=io.exists(io.context,final);if(exists<0)return R::Storage;
    if(!exists){
        if(r->received[index]!=entry.package_bytes)return R::Bounds;
        char incoming[100];incomingPath(transaction,index,incoming);
        auto result=validate(incoming);if(result!=R::Ok)return result;
        uncertain=true;
        if(io.rename(io.context,incoming,final))return R::Unknown;
    }
    auto result=validate(final);
    if(result!=R::Ok)return uncertain?R::Unknown:result;
    if(r->readyMask&(1u<<index)){uncertain=false;return R::Ok;}
    auto next=*r;next.received[index]=entry.package_bytes;next.readyMask|=uint8_t(1u<<index);
    uncertain=true;
    if(journal.save(next)!=Ap01SetJournalResultV3::Ok)return R::Unknown;
    uncertain=false;return R::Ok;
}
