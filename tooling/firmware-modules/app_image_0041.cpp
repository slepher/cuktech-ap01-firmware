#include "app_image_0041.h"
#include <string.h>
using R=Ap01AppImageResult;
namespace {
struct Busy {bool &flag;explicit Busy(bool &f):flag(f){flag=true;}~Busy(){flag=false;}};
}
void Ap01AppImage0041::release(){
    // Only called before App entry, or after lifecycle/resource drain succeeds.
    port.release(port.context,memory);memory={};view={};reserved=false;
}
R Ap01AppImage0041::start(const Apx2Reader &reader,const Apx2Limits &limits,
                         const uint8_t expected[32],const ap01_app_services_v2 &services){
    // This executor owns the legacy five-entry lifecycle, regardless of caller limits.
    if(limits.abi_major!=APX2_ABI_MAJOR)return R::Unsupported;
    if(busy||!expected||!nextGeneration()||services.generation!=nextGeneration()||
       services.abi_version!=AP01_APP_ABI_V2||services.struct_bytes!=sizeof(services)||
       services.reserved||!services.invoke)return R::Invalid;
    if(!port.reserve||!port.publish||!port.release)return R::Unsupported;
    Busy guard(busy);
    Apx2Limits supported=limits;supported.services&=services.available_services;
    Apx2View checked{};
    if(apx2Validate(reader,supported,checked)!=Apx2Error::Ok)return R::Package;
    if(memcmp(checked.digest,expected,32))return R::Identity;
    if(!port.reserve(port.context,checked,memory)){memory={};return R::Memory;}
    reserved=true;
    // Revalidation protects against I/O errors and changed contents. Exclusivity
    // still belongs to the caller; a hostile concurrent writer is not supported.
    auto result=apx2Load(reader,supported,memory.bytes,memory.capacity,memory.base,view);
    if(result!=Apx2Error::Ok){release();return result==Apx2Error::Memory?R::Memory:R::Package;}
    if(memcmp(view.digest,expected,32)){release();return R::Identity;}
    ap01_app_entries_v2 entries{};
    if(!port.publish(port.context,memory,view,entries)||!entries.start||!entries.event||
       !entries.prepare_stop||!entries.stop||!entries.health){release();return R::Publish;}
    auto started=life.start(entries,services);
    if(started==Ap01AppLifeResult::Ok)return R::Running;
    if(life.releasable())release(); // No App entry occurred.
    // A failed start may own tasks/UI/state. It must use the normal stop path.
    return R::StartFailed;
}
Ap01AppLifeResult Ap01AppImage0041::stop(uint64_t now,uint64_t budget){
    if(busy)return Ap01AppLifeResult::Invalid;
    if(resourceFailure)return Ap01AppLifeResult::RebootRequired;
    Busy guard(busy);
    auto result=life.stop(now,budget);
    if(result==Ap01AppLifeResult::Ok&&reserved&&life.releasable()){
        if(port.drainResources&&!port.drainResources(port.context)){
            resourceFailure=true;return Ap01AppLifeResult::RebootRequired;
        }
        release();
    }
    return result;
}
Ap01AppLifeResult Ap01AppImage0041::event(uint32_t generation,const ap01_app_event_v2 &event){
    if(busy)return Ap01AppLifeResult::Invalid;
    Busy guard(busy);return life.event(generation,event);
}
Ap01AppLifeResult Ap01AppImage0041::health(uint32_t generation,ap01_app_health_v2 &out){
    if(busy){out={sizeof(out),0,1,0};return Ap01AppLifeResult::Invalid;}
    Busy guard(busy);return life.health(generation,out);
}
