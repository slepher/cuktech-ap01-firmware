// Journal-selected Manifest boot with retained RAM images. Hardware cache and
// capacity acceptance remain separate from the non-device candidate build.
#include "native_app_file_boot_v3.h"
#include "native_exec_memory_v3.h"
#include "native_io_0041.h"
#include "native_vfs_0041.h"
#include "app_set_service_v3.h"
#include <new>
extern "C" {
__attribute__((section(".ap01_manifest"),used,aligned(1)))
extern const uint8_t ap01_native_manifest[256]={};
}
namespace {
struct Platform {
    Ap01NativeExecMemoryV3 executable{1u<<22};
    Ap01NativeAppFileBootV3 boot;
    Platform(uint64_t id,const Ap01ManifestLimitsV3 &limits)
        :boot(id,ap01RomVfs(),executable.port(),limits,1u<<22){}
};
void *monitor(void *p){
    auto &platform=*(Ap01NativeAppFileBootV3 *)p;
    for(;;){platform.monitor(uint32_t(ap01_native0041::nowMs()));ap01_native0041::pause(100);}
}
void *start(void *p){
    auto &platform=*(Ap01NativeAppFileBootV3 *)p;
    uint32_t watcher=0;
    if(ap01_native0041::thread(&watcher,"ap01-watch",monitor,4096,p))platform.workerFailed();
    platform.set().shared().appUpdate(&platform,[](void *p,const Ap01HttpRequest &request,const char *principal,uint64_t now){
        auto *service=((Ap01NativeAppFileBootV3 *)p)->installService();
        if(service)return service->handle(request,principal,uint32_t(now));
        Ap01HttpReply reply;reply.status=503;reply.bytes="{\"error_code\":\"installer_not_ready\"}";return reply;
    });
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
    platform.stageSelected(selector);
    // The worker never returns after publication: journal and service live for
    // this boot. HTTP and health both own the same maintenance-operation lease.
    // Res is 1.25 MiB. Keep 256 KiB beyond candidate/Manifest/journal bytes;
    // existing packages and business files are already charged by statfs used.
    Ap01SetServiceV3 service(ap01RomVfs(),journal,platform.set().shared().transactionGate(),
        platform.installReboot(),platform.installLimits(),mac,platform.set().shared().bootIdentity(),1u<<18);
    service.runtime(&platform,[](void *p){return ((Ap01NativeAppFileBootV3 *)p)->runtime();});
    platform.attachInstaller(&service);
    platform.set().shared().endAppOperation();
    for(;;){
        uint32_t now=uint32_t(ap01_native0041::nowMs());
        if(platform.set().shared().tryAppOperation()){
        platform.healthSelected(selector,now);
        service.tick(now);
        platform.journalStatus(journal.writable()?(journal.current()?Ap01SetJournalResultV3::Ok:Ap01SetJournalResultV3::Empty):Ap01SetJournalResultV3::Unknown,journal);
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
    auto *owner=new(std::nothrow) Platform(boot,limits);
    if(!owner){registerStock(root,callback,filter,user);return;}
    auto *platform=&owner->boot;
    if(!platform->set().shared().bindWindow(root,callback)){delete owner;registerStock(root,callback,filter,user);return;}
    uint32_t worker=0;if(thread(&worker,"ap01-platform",start,16384,platform))platform->workerFailed();
}
