#pragma once
#include "app_boot_v3.h"
#include "app_manifest_v3.h"
#include "app_binding_v3.h"
#include "app_files_v3.h"
#include "app_network_v3.h"
#include "native_services_0041.h"

class Ap01NativeAppPlatformV3;
// One resident service/window/registry owner, shared by all App contexts.
class Ap01NativeAppSharedV3 {
    friend class Ap01NativeAppPlatformV3;
    Ap01AppBindingBridgeV3 binding;
    Ap01NativeServices0041 services;
    Ap01AppWriteGateV3 writeGate;
    ap01_screen_host host{};
    ap01_window_0041 window{};
    ap01_screen_app apps[AP01_MANIFEST_APPS_V3]{};
    Ap01NativeAppPlatformV3 *contexts[AP01_MANIFEST_APPS_V3]{};
    Ap01NativeAppPlatformV3 *dispatch=nullptr;
    const uint64_t bootId;
    const uint32_t capacity;
    uint32_t count=0;
    bool maintenanceStarted=false;
    void *pollContext=nullptr;
    void (*pollHook)(void *,bool)=nullptr;
    std::atomic<uint32_t> heartbeat{0};
    std::atomic<bool> windowPresent{false};
    static bool healthy(void *);
    static void event(void *,void *);
    static void blocked(ap01_screen_host *,int);
public:
    explicit Ap01NativeAppSharedV3(uint64_t boot,uint32_t appCapacity):bootId(boot),capacity(appCapacity){}
    Ap01NativeAppSharedV3(const Ap01NativeAppSharedV3 &)=delete;
    Ap01NativeAppSharedV3 &operator=(const Ap01NativeAppSharedV3 &)=delete;
    bool bindWindow(void *,void (*)(void *));
    bool startMaintenance();
    bool listening()const{return services.listening();}
    bool tryAppOperation(){return services.tryAppOperation();}
    void endAppOperation(){services.endAppOperation();}
    uint64_t bootIdentity()const{return bootId;}
    uint32_t maintenanceBeat()const{return services.heartbeat();}
    bool attachedWindow()const{return windowPresent.load(std::memory_order_acquire);}
    Ap01AppWriteGateV3 &transactionGate(){return writeGate;}
    bool writes(bool allow){return writeGate.writes(allow);}
    bool writesDrained()const{return writeGate.drained();}
    void appUpdate(void *context,Ap01HttpReply (*handler)(void *,const Ap01HttpRequest &,const char *,uint64_t)){services.appUpdate(context,handler);}
    void appStatus(void *context,void (*snapshot)(void *,Ap01SupervisorSnapshotV3 &)){services.appStatus(context,snapshot);}
    // Set by the resident owner before binding the window; never by an App.
    void onPoll(void *context,void (*hook)(void *,bool)){pollContext=context;pollHook=hook;}
    static void poll(void *);
    unsigned registered()const{return host.app_count;}
    void *root()const{return window.win;}
};
// Per-App context. The D1 convenience constructors own a one-slot shared host;
// the collection constructor borrows the sole resident host for the whole boot.
class Ap01NativeAppPlatformV3 {
    Ap01BootPortV3 executable;
    Ap01ManifestEntryV3 grant{};
    char privateRoot[64]={};
    bool boundedGrant=false,validGrant=false;
    friend class Ap01NativeAppSharedV3;
    Ap01NativeAppPlatformV3(uint64_t,const Ap01BootPortV3 &,const Ap01ManifestEntryV3 &,bool,Ap01NativeAppSharedV3 *);
    std::unique_ptr<Ap01NativeAppSharedV3> ownedShared;
    Ap01NativeAppSharedV3 *shared=nullptr;
    uint32_t registryIndex=UINT32_MAX;
    bool uiBlocked=false;
    ap01_window_0041 appWindow{};
    Ap01PlatformApiV3 api{};
    Ap01AppFilesV3 files;
    Ap01AppNetworkV3 network;
    Ap01AppBootV3 loader;
    char build[33]={},digest[65]={};
    void *appInstance=nullptr;
    void (*appTick)(void *)=nullptr;
    void (*appEvent)(void *,void *)=nullptr;
    std::atomic<uint32_t> heapUsed{0},heapPeak{0},stackUsed{0},taskCount{0};
    uint32_t heapLimit=0,stackLimit=0;
    bool attached=false;
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
    static bool clock(void *,uint64_t *);
    static bool yield(void *);
    static void tick(void *);
    void refreshWindow();
    static int32_t attach(void *,void *,ap01_screen_slot *,ap01_page_0041 *,uint32_t,
                          void (*)(void *,uint32_t),void (*)(void *),void (*)(void *,void *));
    static void *allocate(void *,uint32_t);
    static void *reallocate(void *,void *,uint32_t);
    static void release(void *,void *);
    static int32_t task(void *,const char *,void *(*)(void *),uint32_t,void *);
public:
    Ap01NativeAppPlatformV3(uint64_t boot,const Ap01BootPortV3 &backend);
    // Collection owner supplies a validated immutable Manifest entry. This
    // context enforces that entry's ID, budgets, capabilities and port grants.
    Ap01NativeAppPlatformV3(uint64_t boot,const Ap01BootPortV3 &backend,const Ap01ManifestEntryV3 &);
    Ap01NativeAppPlatformV3(Ap01NativeAppSharedV3 &,const Ap01BootPortV3 &,const Ap01ManifestEntryV3 &);
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
    static void poll(void *context){auto *s=(Ap01NativeAppPlatformV3 *)context;if(s->shared)Ap01NativeAppSharedV3::poll(s->shared);}
    Ap01BootResultV3 result()const{return bootResult.load(std::memory_order_acquire);}
    static const uint32_t platformAbi[4];
};
