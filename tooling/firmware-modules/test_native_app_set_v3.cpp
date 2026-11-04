#include "native_app_set_v3.h"
#include "native_app_file_boot_v3.h"
#include <map>
#include <string>
#include "model_platform_v3.h"
#include <cassert>
#include <cstring>
#include <fstream>
#include <iterator>
#include <vector>

static std::vector<uint8_t> file(const char *path){
    std::ifstream f(path,std::ios::binary);assert(f);
    return {std::istreambuf_iterator<char>(f),{}};
}
static bool read(void *p,uint32_t at,uint8_t *out,uint32_t n){
    auto &v=*(std::vector<uint8_t> *)p;if(uint64_t(at)+n>v.size())return false;
    memcpy(out,v.data()+at,n);return true;
}
static Apx2Reader reader(std::vector<uint8_t> &v){return {&v,uint32_t(v.size()),read};}
struct Instance {
    const Ap01PlatformApiV3 *api=nullptr;void *context=nullptr;
    ap01_screen_slot slots[1]{};ap01_page_0041 pages[1]{};
    unsigned ticks=0,events=0;
};
static Instance instances[2];
static unsigned starts=0,mode=0;
static void pagePoll(void *,uint32_t){}
static void tick(void *p){++((Instance *)p)->ticks;}
static void event(void *,void *){}
static int32_t attach(Instance &s){return s.api->ui.attach(s.context,&s,s.slots,s.pages,1,pagePoll,tick,event);}
static int32_t start(const Ap01PlatformApiV3 *api,void *context,void **out){
    assert(starts<2&&ap01ModelV3.maintenanceStarts==1);
    auto &s=instances[starts++];s.api=api;s.context=context;*out=&s;
    assert(attach(s)==0);
    assert(!strcmp(api->ui.app->app_id,starts==1?"codex_status":"z_probe"));
    return mode==3&&starts==2?AP01_APP_V3_FAILED:AP01_APP_V3_OK;
}
static int32_t appEvent(void *p,uint32_t kind,const void *,uint32_t){
    auto &s=*(Instance *)p;++s.events;
    return kind==3?attach(s):AP01_APP_V3_OK;
}
static int32_t health(void *){return AP01_APP_V3_OK;}
struct Store {
    std::vector<uint8_t> packages[2],images[2];
    unsigned opens=0,closes=0,reserves=0,publishes=0;
    static bool open(void *p,const Ap01ManifestEntryV3 &entry,Apx2Reader &out,uint32_t &version){
        auto &s=*(Store *)p;unsigned i=!strcmp(entry.id,"z_probe");
        out=reader(s.packages[i]);version=1;++s.opens;return true;
    }
    static void close(void *p,Apx2Reader &r){++((Store *)p)->closes;r={};}
    static bool reserve(void *p,const Apx2View &view,Ap01BootMemoryV3 &out){
        auto &s=*(Store *)p;assert(s.reserves<2);unsigned i=s.reserves++;
        auto &v=s.images[i];v.resize(view.image_bytes+view.bss_bytes);
        out={v.data(),uint32_t(v.size()),0xa8000000+i*0x40000};return true;
    }
    static bool publish(void *p,const Ap01BootMemoryV3 &,const Apx2View &,Ap01AppEntriesV3 &out){
        auto &s=*(Store *)p;++s.publishes;out={start,appEvent,health};
        return !(mode==2&&s.publishes==2);
    }
};

struct Disk {
    std::map<std::string,std::vector<uint8_t>> files;
    std::vector<uint8_t> *current=nullptr;
    unsigned position=0,opens=0,closes=0,scenario=0;bool worker=true;
    static int open(void *p,const char *path,unsigned flags){
        auto &s=*(Disk *)p;assert(s.worker&&!flags&&!s.current);
        auto it=s.files.find(path);if(it==s.files.end())return -1;
        s.current=&it->second;s.position=0;++s.opens;return 10;
    }
    static int close(void *p,int fd){auto &s=*(Disk *)p;assert(s.worker&&fd==10&&s.current);
        s.current=nullptr;++s.closes;return s.scenario==6?-1:0;}
    static int32_t size(void *p,int fd){auto &s=*(Disk *)p;assert(s.worker&&fd==10&&s.current);return int32_t(s.current->size());}
    static int read(void *p,int fd,void *out,size_t n){
        auto &s=*(Disk *)p;assert(s.worker&&fd==10&&s.current);
        if(s.scenario==5&&s.position>=40)return -1;
        if(s.scenario==4&&n>7)n=7;
        if(n>s.current->size()-s.position)n=s.current->size()-s.position;
        memcpy(out,s.current->data()+s.position,n);s.position+=unsigned(n);return int(n);
    }
    void add(const std::vector<uint8_t> &v){
        const char *hex="0123456789abcdef";std::string path="/resource/app-store/packages/";
        for(unsigned i=192;i<224;++i){path+=hex[v[i]>>4];path+=hex[v[i]&15];}
        files[path+".apx2"]=v;
    }
    Ap01VfsOps io(){Ap01VfsOps ops{};ops.context=this;ops.open=open;ops.close=close;ops.read=read;ops.size=size;return ops;}
};
int main(int argc,char **argv){
    assert(argc==4);auto manifest=file(argv[1]);auto real=file(argv[2]),peer=file(argv[3]);
    Ap01ManifestLimitsV3 limits{8,1u<<24,1u<<23,1u<<23,1u<<20,16,32,127,1u<<25,1u<<20};
    for(mode=0;mode<4;++mode){
        ap01ModelV3={};starts=0;instances[0]=Instance{};instances[1]=Instance{};
        Store store;store.packages[0]=real;store.packages[1]=peer;
        if(mode==1)store.packages[1].back()^=1;
        Ap01NativeAppSetV3 set(19,{&store,Store::open,Store::close},{&store,nullptr,Store::reserve,Store::publish});
        assert(!set.writes(true)&&set.writesDrained());
        assert(set.shared().bindWindow((void *)1,ap01ModelStockV3));
        assert(set.boot(reader(manifest),manifest.data()+32,limits)==Ap01AppSetResultV3::Waiting);
        assert(!store.opens&&!starts&&!store.reserves);
        assert(set.shared().startMaintenance());
        auto result=set.boot(reader(manifest),manifest.data()+32,limits);
        assert(store.opens==store.closes);
        assert(set.boot(reader(manifest),manifest.data()+32,limits)==Ap01AppSetResultV3::AlreadyAttempted);
        if(mode==1){assert(result==Ap01AppSetResultV3::Packages&&!starts&&!store.reserves);continue;}
        if(mode>=2){
            assert(result==Ap01AppSetResultV3::Start&&set.execution().startedCount()==1);
            assert(store.reserves==2&&!store.images[0].empty()&&!store.images[1].empty());
            assert(set.execution().health()==AP01_APP_V3_FAILED);
            Ap01NativeAppSharedV3::poll(&set.shared());assert(instances[0].ticks==1);
            assert(ap01ModelV3.listening);continue;
        }
        assert(result==Ap01AppSetResultV3::Started&&starts==2&&set.shared().registered()==2);
        assert(set.execution().startedCount()==2&&set.execution().health()==AP01_APP_V3_OK);
        assert(instances[0].api->ui.host==instances[1].api->ui.host);
        assert(set.writes(true));
        for(auto &s:instances){assert(s.api->writes_allowed(s.context)==1);
            assert(!((Ap01NativeAppPlatformV3 *)s.context)->writes(false));}
        assert(set.writes(false)&&set.writesDrained());
        for(auto &s:instances)assert(s.api->writes_allowed(s.context)==0);
        assert(instances[0].api->files.context!=instances[1].api->files.context);
        assert(!strcmp(instances[1].api->private_root,"/resource/apps/z_probe"));
        Ap01NativeAppSharedV3::poll(&set.shared());assert(instances[0].ticks==1&&instances[1].ticks==1);
        ap01ModelV3.eventCode=0x29;ap01ModelV3.eventTarget=(void *)1;
        ap01ModelV3.window->event(ap01ModelV3.window->context,(void *)1);
        assert(!set.shared().root());
        assert(set.shared().bindWindow((void *)2,ap01ModelStockV3));
        assert(set.shared().registered()==2&&instances[0].events==1&&instances[1].events==1);
        assert(instances[0].api->ui.window->win==(void *)2&&instances[1].api->ui.window->win==(void *)2);
        assert(starts==2&&ap01ModelV3.maintenanceStarts==1);
        Ap01NativeAppSharedV3::poll(&set.shared());assert(instances[0].ticks==2&&instances[1].ticks==2);
    }
    for(unsigned fault=0;fault<12;++fault){
        ap01ModelV3={};starts=0;mode=0;instances[0]=Instance{};instances[1]=Instance{};
        Store backend;Disk disk;disk.scenario=fault;
        disk.files["/resource/app-store/current.amf3"]=manifest;disk.add(real);disk.add(peer);
        if(fault==1)disk.files.erase("/resource/app-store/current.amf3");
        if(fault==2)for(auto it=disk.files.begin();it!=disk.files.end();++it)if(it->second==peer){disk.files.erase(it);break;}
        if(fault==3)for(auto &item:disk.files)if(item.second==peer)item.second.back()^=1;
        if(fault==11)disk.files["/resource/app-store/current.amf3"].resize(63);
        auto budget=limits;if(fault==10)budget.ram_bytes=100;
        Ap01BootPortV3 port=fault==9?Ap01BootPortV3{}:Ap01BootPortV3{&backend,nullptr,Store::reserve,Store::publish};
        Ap01NativeAppFileBootV3 boot(29,disk.io(),port,budget,fault==7?1:1u<<22);
        assert(boot.set().shared().bindWindow((void *)1,ap01ModelStockV3));
        assert(!boot.stage("/resource/app-store/current.amf3")&&!disk.opens);
        assert(boot.set().shared().startMaintenance());
        uint8_t expected[32];memcpy(expected,manifest.data()+32,32);if(fault==8)expected[0]^=1;
        bool staged=boot.stage("/resource/app-store/current.amf3",expected);
        assert(!starts&&!backend.reserves&&disk.opens==disk.closes&&!disk.current);
        assert(staged==(fault==0||fault==4||fault==9));
        assert(!boot.stage("/resource/app-store/current.amf3",expected));
        disk.worker=false;disk.files.clear(); // UI must only read the immutable snapshot.
        Ap01NativeAppSharedV3::poll(&boot.set().shared());
        if(staged&&fault!=9)assert(boot.result()==Ap01AppSetResultV3::Started&&starts==2&&backend.reserves==2);
        else assert(!starts&&ap01ModelV3.listening);
        if(fault==9)assert(boot.result()==Ap01AppSetResultV3::Start);
        boot.monitor(uint32_t(ap01ModelV3.now));
        if(starts){
            assert(boot.status().state==Ap01SupervisorStateV3::Healthy&&boot.status().count==2);
            ap01ModelV3.now+=5001;boot.monitor(uint32_t(ap01ModelV3.now));
            assert(boot.status().fault==Ap01SupervisorFaultV3::UiStale);
        }else assert(boot.status().fault==Ap01SupervisorFaultV3::Boot);
        if(!starts){
            ap01ModelV3.busy=true;ap01ModelV3.activeChild=7;ap01ModelV3.eventCode=0x11;ap01ModelV3.eventKey=0x13;
            ap01ModelV3.window->event(ap01ModelV3.window->context,(void *)1);
            assert(ap01ModelV3.stockEvents==1); // Maintenance-only native navigation stays usable.
        }
        assert(disk.opens==disk.closes);
    }
    puts("native collection: Manifest preflight -> per-App C tables -> shared host; root rebuild, partial failure retention, maintenance, reader ownership and 12 worker-file staging scenarios passed (host entries)");
}
