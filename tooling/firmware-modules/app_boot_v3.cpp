#include "app_boot_v3.h"
#include <string.h>
using Result=Ap01BootResultV3;
Result Ap01AppBootV3::boot(const Apx2Reader &reader,const Apx2Limits &limits,const uint8_t digest[32],
                         const Ap01PlatformApiV3 &api,void *context){
    if(attempted)return Result::AlreadyAttempted;
    if(!digest||!context||limits.abi_major!=3||api.abi_major!=3||api.struct_bytes<sizeof(api)||
       api.reserved||!port.maintenance_ready||!port.reserve||!port.publish)return Result::Invalid;
    if(!port.maintenance_ready(port.context))return Result::Waiting;
    attempted=true;
    auto available=limits;available.services&=api.capabilities;
    if(apx2Validate(reader,available,view)!=Apx2Error::Ok)return Result::Package;
    if(memcmp(digest,view.digest,32))return Result::Identity;
    if(!port.reserve(port.context,view,memory))return Result::Memory;
    reserved=true;
    if(apx2Load(reader,available,memory.bytes,memory.capacity,memory.base,view)!=Apx2Error::Ok)return Result::Package;
    if(memcmp(digest,view.digest,32))return Result::Identity;
    if(!port.publish(port.context,memory,view,entries)||!entries.start||!entries.event||!entries.health)return Result::Publish;
    dispatching=true;
    int32_t result=entries.start(&api,context,&instance);
    dispatching=false;
    started=result==AP01_APP_V3_OK&&instance;
    return started?Result::Started:Result::Failed;
}
int32_t Ap01AppBootV3::event(uint32_t kind,const void *payload,uint32_t bytes){
    if(!started||dispatching)return AP01_APP_V3_INVALID;
    dispatching=true;int32_t result=entries.event(instance,kind,payload,bytes);dispatching=false;
    return result;
}
int32_t Ap01AppBootV3::health(){
    if(!started)return AP01_APP_V3_FAILED;
    if(dispatching)return AP01_APP_V3_PENDING;
    dispatching=true;int32_t result=entries.health(instance);dispatching=false;return result;
}
