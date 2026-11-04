// D2 Manifest boot composition. Hardware executable-memory admission is not
// established: the default backend refuses reserve, leaving maintenance alive.
// The model supplies an explicit backend to the same resident platform class.
#include "native_app_file_boot_v3.h"
#include "native_io_0041.h"
#include "native_vfs_0041.h"
#include <new>
extern "C" {
__attribute__((section(".ap01_manifest"),used,aligned(1)))
extern const uint8_t ap01_native_manifest[256]={};
}
namespace {
void *monitor(void *p){
    auto &platform=*(Ap01NativeAppFileBootV3 *)p;
    for(;;){platform.monitor(uint32_t(ap01_native0041::nowMs()));ap01_native0041::pause(100);}
}
void *start(void *p){
    auto &platform=*(Ap01NativeAppFileBootV3 *)p;
    uint32_t watcher=0;
    if(ap01_native0041::thread(&watcher,"ap01-watch",monitor,4096,p))platform.workerFailed();
    if(!platform.set().shared().startMaintenance()){platform.workerFailed();return nullptr;}
    // Listening is asynchronous; bounded wait, no App loading before it succeeds.
    for(unsigned i=0;i<500&&!platform.set().shared().listening();++i)ap01_native0041::pause(10);
    platform.stage("/resource/app-store/current.amf3");
    return nullptr;
}
}
extern "C" __attribute__((used))
void ap01Register0041(void *root,void (*callback)(void *),unsigned filter,void *user){
    using namespace ap01_native0041;
    if(!mainHook(callback,filter)){registerStock(root,callback,filter,user);return;}
    if(auto *existing=(Ap01NativeAppSharedV3 *)ap01_window_find(Ap01NativeAppSharedV3::poll)){
        if(existing->root()==root)return;
        if(!existing->bindWindow(root,callback))registerStock(root,callback,filter,user);
        return;
    }
    uint64_t boot=0;
    if(!randomBytes(nullptr,(uint8_t *)&boot,sizeof(boot))||!boot){registerStock(root,callback,filter,user);return;}
    // Provisional model budgets, not a hardware capacity assertion. The staging
    // allocation is additionally charged against RAM by the file composition.
    Ap01ManifestLimitsV3 limits{8,1u<<22,1u<<23,1u<<23,1u<<20,4,32,127,1u<<24,1u<<20};
    auto *platform=new(std::nothrow) Ap01NativeAppFileBootV3(boot,ap01RomVfs(),{},limits,1u<<22);
    if(!platform){registerStock(root,callback,filter,user);return;}
    if(!platform->set().shared().bindWindow(root,callback)){delete platform;registerStock(root,callback,filter,user);return;}
    uint32_t worker=0;if(thread(&worker,"ap01-platform",start,16384,platform))platform->workerFailed();
}
