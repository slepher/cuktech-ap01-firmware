// Journal-selected Manifest boot. Hardware executable-memory admission is not
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
    if(!platform.set().shared().listening()){platform.workerFailed();return nullptr;}
    char text[13];uint8_t mac[6]{};
    if(!ap01_native0041::wifiMac(text)){platform.workerFailed();return nullptr;}
    for(unsigned i=0;i<12;++i){
        char c=text[i];int n=c>='0'&&c<='9'?c-'0':c>='A'&&c<='F'?c-'A'+10:c>='a'&&c<='f'?c-'a'+10:-1;
        if(n<0){platform.workerFailed();return nullptr;}
        mac[i/2]=uint8_t((mac[i/2]<<4)|n);
    }
    Ap01SetJournalV3 journal(ap01RomVfs(),mac);
    bool admitted=false;
    for(unsigned i=0;i<500&&!admitted;++i){admitted=platform.set().shared().tryAppOperation();if(!admitted)ap01_native0041::pause(10);}
    if(!admitted){platform.workerFailed();return nullptr;}
    auto loaded=journal.load();platform.journalStatus(loaded,journal);
    if(loaded!=Ap01SetJournalResultV3::Ok&&loaded!=Ap01SetJournalResultV3::Empty){platform.set().shared().endAppOperation();platform.workerFailed();return nullptr;}
    Ap01SetSelectorV3 selector(journal,platform.set().shared().bootIdentity());
    platform.stageSelected(selector);platform.set().shared().endAppOperation();
    for(;;){
        uint32_t now=uint32_t(ap01_native0041::nowMs());
        if(platform.set().shared().tryAppOperation()){
        platform.healthSelected(selector,now);
        platform.journalStatus(journal.writable()?loaded:Ap01SetJournalResultV3::Unknown,journal);
        platform.dispatchReboot(now,nullptr,[](void *){ap01_native0041::reboot();});
        platform.set().shared().endAppOperation();
        }
        ap01_native0041::pause(100);
    }
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
