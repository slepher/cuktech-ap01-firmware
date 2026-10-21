#include "native_services_0041.h"
#include "native_maintenance_0041.h"
#include "native_wifi_switch_0041.h"
#include "native_wifi_profiles_port_0041.h"
#include "native_device_code_0041.h"
#include "native_slot_0041.h"
#include "native_io_0041.h"
#include "native_vfs_0041.h"
#include "screen_port_0041.h"
#include <new>
extern "C" const uint8_t ap01_native_manifest[256];
using namespace ap01_native0041;
struct Ap01NativeServices0041::State {
    static const uint32_t budget[5];
    Flash updateFlash;
    char firmwareBuild[33]={};
    int bootSlot=-1;
    LittleFSClass fs{ap01RomVfs(),"/resource/codex-status"};
    std::unique_ptr<Ap01Maintenance0041> maintenance;
    Ap01WifiSwitch0041 wifi{ap01WifiSwitchNativePort0041(this,wifiBlocked)};
    std::atomic<bool> listening{false},stop{false},ready{false};
    void *healthContext=nullptr;
    bool (*healthy)(void *)=nullptr;
    static bool wifiBlocked(void *p) {auto &s=*(State *)p;return ap01_native0041::firmwareBusy()||(s.maintenance&&s.maintenance->active());}
    static bool firmwareBusy(void *p) {return ap01_native0041::firmwareBusy()||((State *)p)->wifi.busy();}
    static bool diagnosticBusy(void *p) {return firmwareBusy(p)||wifiBlocked(p);}
    static void firmwareClose(void *p) {
        Flash &f=((State *)p)->updateFlash;
        if(f.fd>=0){flashClose(&f);f.fd=-1;}
    }
    static bool firmwareOpen(void *p,uint32_t length) {
        Flash &f=((State *)p)->updateFlash;if(f.fd>=0)return false;
        const char *slot=updateSlot();
        if(!slot||(strcmp(slot,"/dev/fw1")&&strcmp(slot,"/dev/fw2")))return false;
        State &r=*(State *)p;
        if(r.bootSlot<0||ap01SelectedSlot0041()!=r.bootSlot||strcmp(slot,r.bootSlot?"/dev/fw1":"/dev/fw2"))return false;
        f.flip=0;
        int result=flashOpen(&f,length);
        if(result||f.fd<=0){firmwareClose(p);return false;}return true;
    }
    static bool firmwareWrite(void *p,uint32_t offset,const uint8_t *bytes,size_t length) {
        Flash &f=((State *)p)->updateFlash;if(f.fd<0||!length||length>32768)return false;
        uint8_t scratch[1024];
        while(length){unsigned n=length>sizeof(scratch)?sizeof(scratch):length;memcpy(scratch,bytes,n);
            if(flashWrite(&f,offset,scratch,n))return false;
            offset+=n;bytes+=n;length-=n;
        }return true;
    }
    static bool firmwareVerify(void *p,uint32_t length) {
        Flash &f=((State *)p)->updateFlash;
        return f.fd>=0&&!flashVerify(&f,length);
    }
    static int firmwareCommit(void *p) {int slot=((State *)p)->bootSlot;return slot<0?-1:ap01SelectSlot0041(unsigned(slot)^1);}
    static void firmwareReboot(void *) {reboot();}
    static int runningSlot(void *p) {return ((State *)p)->bootSlot;}
    static bool inspectSlot(void *p,unsigned slot,Ap01SlotImage &out) {return ap01InspectSlot0041(slot,int(slot)==((State *)p)->bootSlot,out);}
    static int selectSlot(void *,unsigned slot) {return ap01SelectSlot0041(slot);}
    static bool bootHealthy(void *p) {
        auto &s=*(State *)p;
        return s.listening.load(std::memory_order_acquire)&&s.healthy&&s.healthy(s.healthContext);
    }

    static void *run(void *p) {
        auto &s=*(State *)p;
        int fd=listener(18080);if(fd<0)return nullptr;
        s.listening.store(true,std::memory_order_release);
        while(!s.stop.load(std::memory_order_acquire)) {
            s.maintenance->tick(nowMs());s.wifi.tick(nowMs());
            if(!waitFd(fd,1,nowMs()+1000))continue;
            int client=ap01_native0041::accept(fd);if(client<0)continue;
            Ap01Stream io{&client,receive,send};uint64_t now=nowMs();
            bool sent=ap01ServeMaintenanceHttp0041(*s.maintenance,io,now,now+5000);
            closeFd(client);s.maintenance->afterResponse(sent);
        }
        s.listening.store(false,std::memory_order_release);closeFd(fd);return nullptr;
    }
};
__attribute__((section(".ap01_platform_budget"),used))
const uint32_t Ap01NativeServices0041::State::budget[5]={sizeof(State),sizeof(Ap01Maintenance0041),sizeof(Ap01NativeServices0041),sizeof(Ap01WifiSwitch0041),sizeof(LittleFSClass)};
Ap01NativeServices0041::Ap01NativeServices0041()=default;
Ap01NativeServices0041::~Ap01NativeServices0041()=default;
bool Ap01NativeServices0041::start(const Ap01MaintenanceBridge0041 &bridge,uint64_t boot,void *context,bool (*healthy)(void *)) {
    if(state)return false;
    auto s=std::unique_ptr<State>(new(std::nothrow) State);if(!s)return false;
    char mac[13];if(!wifiMac(mac)||!s->fs.begin(false,"/resource",10,"resource"))return false;
    s->healthContext=context;s->healthy=healthy;s->bootSlot=ap01SelectedSlot0041();
    const char *hex="0123456789abcdef";
    for(unsigned i=0;i<16;++i){uint8_t v=ap01_native_manifest[36+i];s->firmwareBuild[2*i]=hex[v>>4];s->firmwareBuild[2*i+1]=hex[v&15];}
    Ap01MaintenancePort0041 port{s.get(),
        {s.get(),State::firmwareBusy,State::firmwareOpen,State::firmwareWrite,State::firmwareVerify,State::firmwareCommit,State::firmwareClose,s->firmwareBuild,State::firmwareReboot,State::runningSlot,State::inspectSlot,State::selectSlot,State::bootHealthy},
        ap01WifiProfilesNativePort0041(s.get(),State::diagnosticBusy),
        {s.get(),ap01DiagnosticFile0041,ap01DiagnosticFlash0041,State::diagnosticBusy},
        [](void *,char out[9]){return ap01DeviceCodeLoad0041(ap01RomVfs(),out);}};
    s->maintenance.reset(new(std::nothrow) Ap01Maintenance0041(s->fs,port,bridge,mac,boot));
    if(!s->maintenance||!s->maintenance->begin(nowMs()))return false;
    s->wifi.begin(nowMs());s->ready.store(true,std::memory_order_release);
    uint32_t worker=0;
    // Publish before the executor starts; UI only reads the published State.
    state=std::move(s);
    if(thread(&worker,"ap01-maint",State::run,16384,state.get())) {state.reset();return false;}
    live.store(state.get(),std::memory_order_release);return true;
}
bool Ap01NativeServices0041::busy() const {auto *s=live.load(std::memory_order_acquire);return s&&(!s->ready.load(std::memory_order_acquire)||s->maintenance->active()||s->wifi.busy());}
int Ap01NativeServices0041::selectWifi(const char *ssid) {
    auto *s=live.load(std::memory_order_acquire);if(!s||!s->ready.load(std::memory_order_acquire)||State::wifiBlocked(s))return -16;
    return s->wifi.request(ssid,uint32_t(nowMs()));
}
int Ap01NativeServices0041::wifiState() const {auto *s=live.load(std::memory_order_acquire);return s?int(s->wifi.feedback(uint32_t(nowMs()))):int(Ap01WifiSwitch0041::Unavailable);}
extern "C" int ap01WifiSelect0041(const char *ssid) {
    auto *services=(Ap01NativeServices0041 *)ap01_window_services();return services?services->selectWifi(ssid):-16;
}
extern "C" int ap01WifiSelectionState0041() {
    auto *services=(Ap01NativeServices0041 *)ap01_window_services();return services?services->wifiState():int(Ap01WifiSwitch0041::Unavailable);
}
