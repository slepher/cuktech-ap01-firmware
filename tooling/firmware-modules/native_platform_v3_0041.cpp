// D1 fixed-file boot composition. Hardware executable-memory admission is not
// established: the default backend refuses reserve, leaving maintenance alive.
// The model supplies an explicit backend to the same resident platform class.
#include "native_app_platform_v3.h"
#include "native_io_0041.h"
#include <new>
extern "C" {
__attribute__((section(".ap01_manifest"),used,aligned(1)))
extern const uint8_t ap01_native_manifest[256]={};
}
namespace {
void *start(void *p){
    auto &platform=*(Ap01NativeAppPlatformV3 *)p;
    if(!platform.startMaintenance())return nullptr;
    // Model limits, not hardware capacity claims; H admission remains separate.
    Apx2Limits limits{1u<<22,1u<<23,1u<<21,40960,1,AP01_CODEX_CAPS_V3,"codex_status",3};
    platform.stageFile("/resource/app-current.apx2",limits);
    return nullptr;
}
}
extern "C" __attribute__((used))
void ap01Register0041(void *root,void (*callback)(void *),unsigned filter,void *user){
    using namespace ap01_native0041;
    if(!mainHook(callback,filter)){registerStock(root,callback,filter,user);return;}
    if(auto *existing=(Ap01NativeAppPlatformV3 *)ap01_window_find(Ap01NativeAppPlatformV3::poll)){
        if(existing->table().ui.window->win==root)return;
        if(!existing->bindWindow(root,callback))registerStock(root,callback,filter,user);
        return;
    }
    uint64_t boot=0;
    if(!randomBytes(nullptr,(uint8_t *)&boot,sizeof(boot))||!boot){registerStock(root,callback,filter,user);return;}
    auto *platform=new(std::nothrow) Ap01NativeAppPlatformV3(boot,{});
    if(!platform){registerStock(root,callback,filter,user);return;}
    if(!platform->bindWindow(root,callback)){delete platform;registerStock(root,callback,filter,user);return;}
    uint32_t worker=0;thread(&worker,"ap01-platform",start,16384,platform);
}
