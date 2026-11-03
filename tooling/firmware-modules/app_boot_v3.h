#pragma once
#include "apx2.h"
#include "app_platform_api_v3.h"

struct Ap01AppEntriesV3 {Ap01AppStartV3 start=nullptr;Ap01AppEventV3 event=nullptr;Ap01AppHealthV3 health=nullptr;};
struct Ap01BootMemoryV3 {uint8_t *bytes=nullptr;uint32_t capacity=0,base=0;};
// Resident/model execution backend. reserve accounts for image/heap/task stack
// and maintenance reserve. publish synchronizes caches and resolves exactly
// the three image entry offsets, without invoking them. No release/unload API.
struct Ap01BootPortV3 {
    void *context;
    bool (*maintenance_ready)(void *);
    bool (*reserve)(void *,const Apx2View &,Ap01BootMemoryV3 &);
    bool (*publish)(void *,const Ap01BootMemoryV3 &,const Apx2View &,Ap01AppEntriesV3 &);
};
enum class Ap01BootResultV3 {Waiting,Started,Invalid,Package,Identity,Memory,Publish,Failed,AlreadyAttempted};
// UI-executor owned, one attempt per boot. Any reserved image is retained even
// on failure. Hardware executable-memory policy is exclusively in the backend.
class Ap01AppBootV3 {
    Ap01BootPortV3 port;
    Ap01BootMemoryV3 memory{};
    Apx2View view{};
    Ap01AppEntriesV3 entries{};
    void *instance=nullptr;
    bool attempted=false,reserved=false,started=false,dispatching=false;
public:
    explicit Ap01AppBootV3(const Ap01BootPortV3 &p):port(p){}
    Ap01AppBootV3(const Ap01AppBootV3 &)=delete;
    Ap01AppBootV3 &operator=(const Ap01AppBootV3 &)=delete;
    Ap01BootResultV3 boot(const Apx2Reader &,const Apx2Limits &,const uint8_t digest[32],
                          const Ap01PlatformApiV3 &,void *appContext);
    int32_t event(uint32_t,const void *,uint32_t);
    int32_t health();
    bool retained() const {return reserved;}
    bool entered() const {return started;}
    const Apx2View &image() const {return view;}
};
