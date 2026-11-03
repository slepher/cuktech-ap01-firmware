#pragma once
#include "apx2.h"
#include "app_lifecycle_0041.h"

struct Ap01AppMemory0041 {
    uint8_t *bytes=nullptr;
    uint32_t capacity=0,base=0;
    void *reservation=nullptr;
};
// Trusted, firmware-resident execution backend. Reserve includes the declared
// image/bss, heap and stack budgets; false must leave no allocation behind.
// publish synchronizes instruction/data caches before resolving all five entry
// addresses. It must not execute App code. Never use an unverified malloc pool
// as an executable backend. A missing backend explicitly refuses loading.
struct Ap01AppImagePort0041 {
    void *context=nullptr;
    bool (*reserve)(void *,const Apx2View &,Ap01AppMemory0041 &)=nullptr;
    bool (*publish)(void *,const Ap01AppMemory0041 &,const Apx2View &,ap01_app_entries_v2 &)=nullptr;
    void (*release)(void *,const Ap01AppMemory0041 &)=nullptr;
    // After stop and callback drain, before freeing executable memory. Must be
    // resident and synchronous; false is sticky and requires controlled reboot.
    // Required for backends owning App resources (files/UI/etc.). Null is only
    // valid when no resources exist outside the image reservation.
    bool (*drainResources)(void *)=nullptr;
    // Resident business services start write-closed for every new generation.
    // Only the executor may change permission after checking durable state.
    bool (*writePermission)(void *,uint32_t generation,bool allow)=nullptr;
};
enum class Ap01AppImageResult {Running,Invalid,Unsupported,Package,Identity,Memory,Publish,StartFailed};
// Resident owner, serialized with the lifecycle executor. The reader must stay
// immutable during start. The owner/backend/gate outlive all App callbacks;
// destruction is not an implicit force-unload. stop returning RebootRequired
// deliberately retains the reservation until controlled reboot.
class Ap01AppImage0041 {
    Ap01AppImagePort0041 port;
    Ap01AppGeneration0041 gate;
    Ap01AppLifecycle0041 life{gate};
    Ap01AppMemory0041 memory{};
    Apx2View view{};
    bool reserved=false,busy=false,resourceFailure=false;
    void release();
public:
    explicit Ap01AppImage0041(const Ap01AppImagePort0041 &p):port(p){}
    Ap01AppImage0041(const Ap01AppImage0041 &)=delete;
    Ap01AppImage0041 &operator=(const Ap01AppImage0041 &)=delete;
    uint32_t nextGeneration() const {return !reserved&&life.releasable()&&gate.current()!=UINT32_MAX?gate.current()+1:0;}
    Ap01AppImageResult start(const Apx2Reader &,const Apx2Limits &,const uint8_t expected[32],const ap01_app_services_v2 &);
    Ap01AppLifeResult stop(uint64_t now,uint64_t budgetMs);
    Ap01AppLifeResult event(uint32_t generation,const ap01_app_event_v2 &);
    Ap01AppLifeResult health(uint32_t generation,ap01_app_health_v2 &);
    Ap01AppGeneration0041 &callbacks(){return gate;}
    uint32_t progress() const {return life.progress();}
    bool retained() const {return reserved;}
    const Apx2View *loaded() const {return reserved?&view:nullptr;}
};
