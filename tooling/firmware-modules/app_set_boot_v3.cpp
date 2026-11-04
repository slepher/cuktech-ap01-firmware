#include "app_set_boot_v3.h"
#include <string.h>
using R=Ap01AppSetResultV3;
R Ap01AppSetBootV3::boot(const Apx2Reader &reader,const uint8_t expected[32],const Ap01ManifestLimitsV3 &limits){
    if(attempted)return R::AlreadyAttempted;
    if(!expected||!port.maintenance_ready||!port.prepare||!port.packages.open||!port.packages.close)return R::Invalid;
    if(!port.maintenance_ready(port.packages.context))return R::Waiting;
    attempted=true;
    error=ap01ReadManifestV3(reader,limits,manifest);if(error!=Ap01ManifestErrorV3::Ok)return R::Manifest;
    if(memcmp(expected,manifest.digest,32))return R::Identity;
    error=ap01CheckManifestPackagesV3(manifest,port.packages);if(error!=Ap01ManifestErrorV3::Ok)return R::Packages;
    for(uint32_t order=0;order<manifest.count;++order){
        uint32_t i=manifest.order[order];const auto &entry=manifest.entries[i];failed=i;
        const Ap01PlatformApiV3 *api=nullptr;void *context=nullptr;
        if(!port.prepare(port.packages.context,entry,loaders[i],api,context)||!loaders[i]||!api||!context)return R::Prepare;
        for(uint32_t j=0;j<order;++j)if(loaders[manifest.order[j]]==loaders[i])return R::Prepare;
        Apx2Reader package{};uint32_t version=0;
        if(!port.packages.open(port.packages.context,entry,package,version))return R::Packages;
        uint64_t memory=uint64_t(entry.image_bytes)+entry.heap_bytes+entry.stack_bytes;
        // Preflight already checked this sum fits APX2's uint32 limit.
        Apx2Limits budget{entry.package_bytes,uint32_t(memory),entry.heap_bytes,entry.stack_bytes,
                          version,entry.capabilities,entry.id,3};
        auto result=loaders[i]->boot(package,budget,entry.digest,*api,context);
        port.packages.close(port.packages.context,package);
        if(result!=Ap01BootResultV3::Started)return R::Start;
        ++started;
    }
    failed=UINT32_MAX;ready=true;return R::Started;
}
int32_t Ap01AppSetBootV3::event(uint32_t kind,const void *payload,uint32_t bytes){
    if(!ready||dispatching)return AP01_APP_V3_INVALID;
    dispatching=true;int32_t result=AP01_APP_V3_OK;
    for(uint32_t n=0;n<manifest.count;++n){auto r=loaders[manifest.order[n]]->event(kind,payload,bytes);
        if(r<0)result=r;else if(r!=AP01_APP_V3_OK&&result==AP01_APP_V3_OK)result=AP01_APP_V3_PENDING;}
    dispatching=false;return result;
}
int32_t Ap01AppSetBootV3::health(){
    if(!ready)return AP01_APP_V3_FAILED;
    if(dispatching)return AP01_APP_V3_PENDING;
    dispatching=true;int32_t result=AP01_APP_V3_OK;
    for(uint32_t n=0;n<manifest.count;++n){auto r=loaders[manifest.order[n]]->health();
        if(r<0)result=r;else if(r!=AP01_APP_V3_OK&&result==AP01_APP_V3_OK)result=AP01_APP_V3_PENDING;}
    dispatching=false;return result;
}
