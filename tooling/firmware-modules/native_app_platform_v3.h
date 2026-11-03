#pragma once
#include "app_boot_v3.h"
#include "app_binding_v3.h"
#include "app_files_v3.h"
#include "app_network_v3.h"
#include "native_services_0041.h"

// One resident platform for D1's fixed codex_status boot entry. D2 replaces the
// one-entry registry with a validated Manifest; screen_host itself is reused.
class Ap01NativeAppPlatformV3 {
    Ap01BootPortV3 executable;
    Ap01AppBindingBridgeV3 binding;
    Ap01NativeServices0041 services;
    ap01_screen_host host{};
    ap01_screen_app app{};
    ap01_window_0041 window{};
    Ap01PlatformApiV3 api{};
    Ap01AppFilesV3 files;
    Ap01AppNetworkV3 network;
    Ap01AppBootV3 loader;
    char build[33]={},digest[65]={};
    void *appInstance=nullptr;
    void (*appTick)(void *)=nullptr;
    void (*appEvent)(void *,void *)=nullptr;
    std::atomic<uint32_t> heartbeat{0},heapUsed{0},heapPeak{0},stackUsed{0},taskCount{0};
    std::atomic<bool> writable{false};
    uint32_t heapLimit=0,stackLimit=0;
    bool maintenanceStarted=false,attached=false;
    Ap01VfsOps bootIo{};
    int bootFd=-1;
    uint32_t bootBytes=0;
    Apx2Limits bootLimits{};
    uint8_t expectedDigest[32]={};
    std::atomic<uint32_t> bootRequest{0}; // 0 absent, 1 preparing, 2 queued, 3 consumed, 4 I/O failure
    std::atomic<Ap01BootResultV3> bootResult{Ap01BootResultV3::Waiting};
    static bool readBootFile(void *,uint32_t,uint8_t *,uint32_t);
    struct alignas(8) Allocation {Ap01NativeAppPlatformV3 *owner;uint32_t bytes;};
    static bool reserve(void *,const Apx2View &,Ap01BootMemoryV3 &);
    static bool publish(void *,const Ap01BootMemoryV3 &,const Apx2View &,Ap01AppEntriesV3 &);
    static bool maintenanceReady(void *);
    static bool healthy(void *);
    static bool clock(void *,uint64_t *);
    static bool yield(void *);
    static void tick(void *);
    static void event(void *,void *);
    static int32_t attach(void *,void *,ap01_screen_slot *,ap01_page_0041 *,uint32_t,
                          void (*)(void *,uint32_t),void (*)(void *),void (*)(void *,void *));
    static void *allocate(void *,uint32_t);
    static void *reallocate(void *,void *,uint32_t);
    static void release(void *,void *);
    static int32_t task(void *,const char *,void *(*)(void *),uint32_t,void *);
public:
    Ap01NativeAppPlatformV3(uint64_t boot,const Ap01BootPortV3 &backend);
    Ap01NativeAppPlatformV3(const Ap01NativeAppPlatformV3 &)=delete;
    Ap01NativeAppPlatformV3 &operator=(const Ap01NativeAppPlatformV3 &)=delete;
    // UI executor; maintenance start belongs on its own worker.
    bool bindWindow(void *root,void (*stock)(void *));
    bool startMaintenance();
    // Worker stages a fixed D1 path, UI tick performs load/start after listening.
    // File stays exclusively open until load returns; no Manifest/trial switch yet.
    bool stageFile(const char *,const Apx2Limits &);
    Ap01BootResultV3 boot(const Apx2Reader &,const Apx2Limits &,const uint8_t expected[32]);
    bool writes(bool allow);
    Ap01AppBootV3 &execution(){return loader;}
    const Ap01PlatformApiV3 &table() const {return api;}
    uint32_t usedHeap() const {return heapUsed.load(std::memory_order_acquire);}
    uint32_t peakHeap() const {return heapPeak.load(std::memory_order_acquire);}
    uint32_t reservedStack() const {return stackUsed.load(std::memory_order_acquire);}
    static void poll(void *context){tick(context);}
    Ap01BootResultV3 result()const{return bootResult.load(std::memory_order_acquire);}
    static const uint32_t platformAbi[4];
};
