#include "app_download_0041.h"
namespace {
const char *incoming="/app-incoming.apx2";
using R=Ap01AppDownloadResult;using J=Ap01AppJournalResult;using P=Ap01AppUpdatePhase;
R saved(J r){return r==J::Ok?R::Ok:r==J::Unknown?R::Unknown:R::State;}
R compare(File &f,uint32_t at,const uint8_t *data,uint32_t n) {
    if(!f.seek(at))return R::Storage;
    uint8_t scratch[256];
    while(n){uint32_t count=n>sizeof(scratch)?sizeof(scratch):n;
        if(f.read(scratch,count)!=count)return R::Storage;
        if(memcmp(scratch,data,count))return R::Conflict;
        data+=count;n-=count;
    }return R::Ok;
}
bool readPackage(void *p,uint32_t at,uint8_t *out,uint32_t n){auto &f=*(File *)p;return f.seek(at)&&f.read(out,n)==n;}
}
R Ap01AppDownload0041::begin(const Ap01AppUpdateRecord &request) {
    if(!journal.resolved())return R::Unknown;
    if(request.phase!=P::Receiving||request.received||request.total>limits.package_bytes||request.total>INT32_MAX)return R::Bounds;
    const auto *current=journal.current();
    if(current&&!memcmp(current->transaction,request.transaction,16)) {
        // Compare the immutable identity only; retries do not rewind progress.
        if(current->total!=request.total||memcmp(current->mac,request.mac,6)||
           memcmp(current->principal,request.principal,65)||memcmp(current->oldDigest,request.oldDigest,32)||
           memcmp(current->newDigest,request.newDigest,32))return R::Conflict;
        return R::Ok;
    }
    int exists=fs.inspect(incoming);
    if(exists<0)return R::Storage;
    if(exists)return R::Conflict; // Cleanup owns deletion; never truncate unknown bytes.
    return saved(journal.save(request));
}
R Ap01AppDownload0041::chunk(const uint8_t transaction[16],uint32_t offset,const uint8_t *bytes,uint32_t n) {
    if(!journal.resolved())return R::Unknown;
    const auto *current=journal.current();
    if(!current||memcmp(current->transaction,transaction,16))return R::Conflict;
    if(current->phase!=P::Receiving)return R::State;
    if(!bytes||!n||n>chunkMax||offset>current->total||n>current->total-offset)return R::Bounds;
    if(offset>current->received||(offset<current->received&&n>current->received-offset))return R::Conflict;
    int exists=fs.inspect(incoming);if(exists<0)return R::Storage;
    if(!exists) {
        if(current->received)return R::Storage;
        File create=fs.open(incoming,"w");if(!create||!create.sync())return R::Storage;
    }
    File read=fs.open(incoming,"r");uint32_t size=0;
    if(!read||!read.length(size)||size<current->received||size>current->total)return R::Storage;
    uint32_t overlap=offset<size?size-offset:0;if(overlap>n)overlap=n;
    if(overlap){R checked=compare(read,offset,bytes,overlap);if(checked!=R::Ok)return checked;}
    if(offset<current->received)return R::Ok; // Durable identical duplicate.
    read.close();
    File append=fs.open(incoming,"a");if(!append)return R::Storage;
    if(overlap<n&&append.write(bytes+overlap,n-overlap)!=n-overlap)return R::Storage;
    // Re-sync an unacknowledged tail even when all bytes already existed.
    if(!append.sync())return R::Storage;
    append.close();read=fs.open(incoming,"r");
    if(!read||compare(read,offset,bytes,n)!=R::Ok)return R::Storage;
    auto next=*current;next.received=offset+n;
    return saved(journal.save(next));
}
R Ap01AppDownload0041::ready(const uint8_t transaction[16],Apx2Error &detail) {
    detail=Apx2Error::Ok;
    if(!journal.resolved())return R::Unknown;
    const auto *current=journal.current();
    if(!current||memcmp(current->transaction,transaction,16))return R::Conflict;
    if(current->phase!=P::Receiving&&current->phase!=P::Ready)return R::State;
    if(current->received!=current->total)return R::Bounds;
    File file=fs.open(incoming,"r");uint32_t size=0;
    if(!file||!file.length(size)||size!=current->total)return R::Storage;
    Apx2View view{};detail=apx2Validate({&file,size,readPackage},limits,view);
    if(detail!=Apx2Error::Ok)return R::Package;
    if(memcmp(view.digest,current->newDigest,32)){detail=Apx2Error::Integrity;return R::Package;}
    if(current->phase==P::Ready)return R::Ok;
    auto next=*current;next.phase=P::Ready;return saved(journal.save(next));
}
