// Run the production service owner, maintenance and Wi-Fi state machines.
// ROM/VFS/thread endpoints are substitutes; no executor or device is started.
#include "native_services_0041.h"
#include "native_io_0041.h"
#include "native_vfs_0041.h"
#include "native_wifi_switch_0041.h"
#include "native_slot_0041.h"
#include "app_files_v3.h"
#include "app_binding_v3.h"
#include "native_maintenance_0041.h"
#include <chrono>
#include <condition_variable>
#include <mutex>
#include <thread>
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
namespace {bool stockBusy=false;unsigned threads=0;}
extern "C" const uint8_t ap01_native_manifest[256]={};
extern "C" void *ap01_window_services(){return nullptr;}
namespace ap01_native0041 {
uint64_t nowMs(){return 100;}
bool firmwareBusy(){return stockBusy;}
bool wifiMac(char (&out)[13]){memcpy(out,"AABBCCDDEEFF",13);return true;}
int thread(uint32_t *id,const char *,void *(*entry)(void *),unsigned stack,void *){
    assert(entry&&stack==16384);*id=++threads;return 0;
}
int listener(unsigned,bool){assert(false);return -1;}
bool waitFd(int,unsigned,uint64_t){assert(false);return false;}
int accept(int){assert(false);return -1;}
int receive(void *,uint8_t *,size_t,uint64_t){assert(false);return -1;}
int send(void *,const uint8_t *,size_t,uint64_t){assert(false);return -1;}
void closeFd(int){assert(false);}
const char *updateSlot(){assert(false);return nullptr;}
int flashOpen(Flash *,uint32_t){assert(false);return -1;}
int flashWrite(Flash *,uint32_t,const void *,uint32_t){assert(false);return -1;}
int flashVerify(Flash *,uint32_t){assert(false);return -1;}
void flashClose(Flash *){assert(false);}
void reboot(){assert(false);}
}
Ap01VfsOps ap01RomVfs(){
    Ap01VfsOps p{};
    p.prepare=[](void *,const char *){return 0;};
    p.exists=[](void *,const char *){return 0;};
    p.open=[](void *,const char *,unsigned mode){assert(!mode);return -1;};
    return p;
}
int ap01SelectedSlot0041(){return 0;}
bool ap01InspectSlot0041(unsigned,bool,Ap01SlotImage &){assert(false);return false;}
int ap01SelectSlot0041(unsigned){assert(false);return -1;}
int ap01DeviceCodeLoad0041(const Ap01VfsOps &,char out[9]){memcpy(out,"01234567",9);return 0;}
int ap01DiagnosticFile0041(void *,const char *,uint32_t,uint8_t *,unsigned,uint32_t *){assert(false);return -1;}
int ap01DiagnosticFlash0041(void *,uint32_t,uint8_t *,unsigned){assert(false);return -1;}
Ap01WifiProfilesPort ap01WifiProfilesNativePort0041(void *context,bool (*busy)(void *)){
    Ap01WifiProfilesPort p{};p.context=context;p.busy=busy;return p;
}
Ap01WifiSwitchPort0041 ap01WifiSwitchNativePort0041(void *context,bool (*busy)(void *)){
    Ap01WifiSwitchPort0041 p{};p.context=context;p.profiles=ap01WifiProfilesNativePort0041(context,busy);
    p.recover=[](void *,Ap01WifiProfile0041 &){return -ENOENT;};
    p.apply=[](void *,const Ap01WifiProfile0041 &,bool){assert(false);return -1;};
    p.online=[](void *,const char *){assert(false);return false;};
    p.journal=[](void *,const Ap01WifiProfile0041 *){assert(false);return -1;};
    return p;
}
int main(){
    Ap01NativeServices0041 services;
    assert(!services.tryAppOperation());
    assert(services.start({},1,nullptr,nullptr)&&threads==1);
    assert(!services.busy());
    Ap01AppWriteGateV3 gate(&services,[](void *p){return ((Ap01NativeServices0041 *)p)->tryAppOperation();},
        [](void *p){((Ap01NativeServices0041 *)p)->endAppOperation();});
    assert(gate.writes(true));
    struct Write {std::mutex mutex;std::condition_variable condition;bool entered=false,release=false;unsigned calls=0;} write;
    Ap01VfsOps disk{};disk.context=&write;
    disk.open=[](void *,const char *,unsigned){return 7;};disk.close=[](void *,int){return 0;};
    disk.mkdir=[](void *,const char *){return 0;};
    disk.write=[](void *p,int,const void *,size_t){auto &w=*(Write *)p;
        std::unique_lock<std::mutex> lock(w.mutex);++w.calls;w.entered=true;w.condition.notify_all();
        assert(w.condition.wait_for(lock,std::chrono::seconds(5),[&]{return w.release;}));return -1;};
    Ap01AppFilesV3 files(disk,"/app");files.bindGate(gate);auto vfs=files.table();
    int fd=vfs.open(vfs.context,"/app/value",1);assert(fd>0);
    std::thread writer([&]{assert(vfs.write(vfs.context,fd,"x",1)==-1);});
    {std::unique_lock<std::mutex> lock(write.mutex);
        assert(write.condition.wait_for(lock,std::chrono::seconds(5),[&]{return write.entered;}));}
    assert(!services.tryAppOperation()&&services.selectWifi("test")==-EBUSY);
    assert(gate.writable()); // Short operation contention never revokes health approval.
    {std::lock_guard<std::mutex> lock(write.mutex);write.release=true;write.condition.notify_all();}writer.join();
    assert(write.calls==1&&gate.writable());
    Ap01AppBindingBridgeV3 binding;
    Ap01AppBindingV3 callbacks{};callbacks.context=&vfs;
    callbacks.principal=[](void *,const char *,char *)->int32_t{return 401;};
    callbacks.online=[](void *)->int32_t{return 1;};
    callbacks.pairing=[](void *p,const Ap01HttpRequestV3 *,uint64_t,
            Ap01ReplyV3 emit,void *reply)->int32_t{
        auto &io=*(Ap01VfsOps *)p;unsigned status=io.mkdir(io.context,"/app/paired")?503:200;
        return emit(reply,status,(const uint8_t *)"{}",2);
    };
    assert(binding.bind(callbacks)==AP01_APP_V3_OK);
    LittleFSClass fs(ap01RomVfs(),"/maintenance");Ap01MaintenancePort0041 port{};port.context=&services;
    port.enterOperation=[](void *p){return ((Ap01NativeServices0041 *)p)->tryAppOperation();};
    port.leaveOperation=[](void *p){((Ap01NativeServices0041 *)p)->endAppOperation();};
    auto bridge=binding.bridge();assert(bridge.coordinatesWrites);
    Ap01Maintenance0041 maintenance(fs,port,bridge,"AABBCCDDEEFF",1);assert(maintenance.begin());
    Ap01HttpRequest pair{};pair.method="POST";pair.path="/api/pairing";
    assert(maintenance.handle(pair,100).status==200);maintenance.afterResponse(true);
    assert(services.tryAppOperation());services.endAppOperation();
    stockBusy=true;
    assert(maintenance.handle(pair,100).status==503);maintenance.afterResponse(false);
    stockBusy=false;
    // Older adapters still hold the outer lock; a nested coordinated writer
    // would fail, proving why the ABI 3 adapter explicitly delegates ownership.
    bridge.coordinatesWrites=false;
    Ap01Maintenance0041 legacy(fs,port,bridge,"AABBCCDDEEFF",1);assert(legacy.begin());
    assert(legacy.handle(pair,100).status==503);legacy.afterResponse(true);
    assert(services.tryAppOperation());
    assert(!gate.enter()&&vfs.open(vfs.context,"/app/other",1)<0);
    assert(!services.tryAppOperation());
    assert(services.selectWifi("test")==-EBUSY);
    services.endAppOperation();
    stockBusy=true;
    assert(services.busy()); // Must agree with the App operation gate.
    assert(!services.tryAppOperation());
    assert(!gate.enter()&&vfs.write(vfs.context,fd,nullptr,0)<0&&write.calls==1);
    assert(services.selectWifi("test")==-EBUSY);
    stockBusy=false;
    assert(!services.busy());
    assert(services.tryAppOperation()); // Rejection must release the lock.
    services.endAppOperation();
    assert(gate.enter());gate.leave();
    assert(services.selectWifi("test")==0);
    assert(services.busy()&&!services.tryAppOperation());
    assert(!gate.enter()&&vfs.open(vfs.context,"/app/other",1)<0);
    assert(vfs.close(vfs.context,fd)==0);
    puts("native services: original OTA busy propagation, operation lock release and queued Wi-Fi exclusion passed (ROM/VFS/thread substitutes)");
}
