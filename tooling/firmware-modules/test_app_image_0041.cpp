#include "app_image_0041.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <vector>
#include <iterator>
using R=Ap01AppImageResult;using L=Ap01AppLifeResult;
struct Backend {
    Ap01AppImage0041 *owner=nullptr;
    std::vector<uint8_t> memory;
    unsigned reserves=0,publishes=0,releases=0,starts=0,stops=0,drains=0;
    bool drainFail=false;
    bool allocationFail=false,publishFail=false,startFail=false,stopFail=false,shortMemory=false,badBase=false;
    bool corruptAfterReserve=false,missingEntry=false;
    std::vector<uint8_t> *package=nullptr;
    static bool reserve(void *p,const Apx2View &v,Ap01AppMemory0041 &out){
        auto &b=*(Backend *)p;++b.reserves;
        if(b.allocationFail)return false;
        b.memory.assign(v.image_bytes+v.bss_bytes,0xaa);
        out={b.memory.data(),uint32_t(b.memory.size())-(b.shortMemory?1:0),b.badBase?0x10001u:0x10000u,&b};
        if(b.corruptAfterReserve)(*b.package)[256]^=1;
        return true;
    }
    static int32_t invoke(void *,uint32_t,uint32_t,uint32_t,const void *,uint32_t,void *,uint32_t,uint32_t *){return -1;}
    static int32_t start(const ap01_app_services_v2 *s,void **out){auto &b=*(Backend *)s->context;
        assert(b.publishes==b.starts+1);++b.starts;*out=&b;
        assert(b.owner->stop(0,10)==L::Invalid);return b.startFail?-1:0;}
    static int32_t event(void *,const ap01_app_event_v2 *){return 0;}
    static int32_t prepare(void *){return 0;}
    static int32_t stop(void *p){auto &b=*(Backend *)p;++b.stops;return b.stopFail?-1:0;}
    static int32_t health(void *,ap01_app_health_v2 *out){out->entry_ready=1;return 0;}
    static bool publish(void *p,const Ap01AppMemory0041 &m,const Apx2View &v,ap01_app_entries_v2 &out){
        auto &b=*(Backend *)p;++b.publishes;assert(m.reservation==&b);
        for(unsigned i=v.image_bytes;i<m.capacity;++i)assert(!m.bytes[i]);
        assert(b.owner->stop(0,10)==L::Invalid);
        out={start,event,prepare,stop,health};if(b.missingEntry)out.stop=nullptr;return !b.publishFail;
    }
    static void release(void *p,const Ap01AppMemory0041 &m){auto &b=*(Backend *)p;
        assert(m.reservation==&b&&b.owner->callbacks().drained());++b.releases;b.memory.clear();}
    static bool drain(void *p){auto &b=*(Backend *)p;++b.drains;
        assert(b.stops==b.starts&&b.owner->callbacks().drained());
        assert(!b.owner->callbacks().acquire(b.owner->callbacks().current()));
        assert(b.owner->stop(0,10)==L::Invalid);
        return !b.drainFail;
    }
    Ap01AppImagePort0041 port(){return {this,reserve,publish,release,drain};}
    ap01_app_services_v2 services(unsigned gen){return {2,sizeof(ap01_app_services_v2),gen,0,~uint64_t(0),this,invoke};}
};
static bool read(void *p,uint32_t at,uint8_t *out,uint32_t n){auto &v=*(std::vector<uint8_t> *)p;
    if(uint64_t(at)+n>v.size())return false;memcpy(out,v.data()+at,n);return true;}
int main(int argc,char **argv){
    assert(argc==2);std::ifstream f(argv[1],std::ios::binary);
    std::vector<uint8_t> golden{std::istreambuf_iterator<char>(f),{}};assert(golden.size()>256);
    Apx2Limits limits{1<<20,1<<20,1<<19,1<<16,2,~uint64_t(0),"golden.app"};
    for(unsigned scenario=0;scenario<15;++scenario){
        auto package=golden;Apx2Reader reader{&package,uint32_t(package.size()),read};
        Apx2View view{};assert(apx2Validate(reader,limits,view)==Apx2Error::Ok);
        Backend backend;backend.package=&package;
        Ap01AppImage0041 owner(scenario==1?Ap01AppImagePort0041{}:backend.port());backend.owner=&owner;
        backend.allocationFail=scenario==2;backend.publishFail=scenario==3;backend.startFail=scenario==4;
        backend.stopFail=scenario==5;backend.shortMemory=scenario==6;backend.badBase=scenario==7;
        backend.corruptAfterReserve=scenario==8;backend.missingEntry=scenario==12;
        backend.drainFail=scenario>=13;if(scenario==14)backend.startFail=true;
        uint8_t expected[32];memcpy(expected,view.digest,32);if(scenario==9)expected[0]^=1;
        auto services=backend.services(scenario==11?2:1);if(scenario==10)services.available_services=0;
        auto directLimits=limits;directLimits.abi_major=APX2_DIRECT_ABI_MAJOR;
        assert(owner.start(reader,directLimits,expected,services)==R::Unsupported);
        assert(!backend.reserves&&!backend.publishes&&!backend.starts);
        auto result=owner.start(reader,limits,expected,services);
        if(scenario==10||scenario==11){assert(result==(scenario==10?R::Package:R::Invalid)&&!backend.reserves);continue;}
        if(scenario==1){assert(result==R::Unsupported&&!backend.reserves);continue;}
        if(scenario==2){assert(result==R::Memory&&!owner.retained()&&!backend.releases);continue;}
        if(scenario==3||scenario==6||scenario==7||scenario==8||scenario==12){
            assert(result==(scenario==3||scenario==12?R::Publish:scenario==8?R::Package:R::Memory));
            assert(!owner.retained()&&backend.releases==1&&!backend.starts);continue;
        }
        if(scenario==9){assert(result==R::Identity&&!backend.reserves);continue;}
        assert(result==(backend.startFail?R::StartFailed:R::Running));assert(owner.retained()&&!owner.nextGeneration());
        assert(owner.start(reader,limits,expected,backend.services(2))==R::Invalid);
        if(scenario>=13){
            assert(owner.stop(1,10)==L::RebootRequired&&owner.retained()&&!backend.releases&&backend.drains==1);
            backend.drainFail=false;
            assert(owner.stop(2,10)==L::RebootRequired&&owner.retained()&&backend.drains==1);
            assert(!owner.nextGeneration());continue;
        }
        if(scenario==5){assert(owner.stop(1,10)==L::RebootRequired&&owner.retained()&&!backend.releases);continue;}
        if(scenario==4){assert(owner.stop(1,10)==L::Ok&&!owner.retained()&&backend.stops==1&&backend.releases==1);continue;}
        ap01_app_health_v2 health{};assert(owner.health(1,health)==L::Ok&&health.entry_ready);
        ap01_app_event_v2 event{sizeof(event),1,0,0,nullptr,0};assert(owner.event(1,event)==L::Ok&&owner.progress()==1);
        assert(owner.callbacks().acquire(1));
        assert(owner.stop(1,10)==L::Pending&&owner.retained()&&!backend.releases&&!backend.stops);
        owner.callbacks().release();assert(owner.stop(2,10)==L::Ok&&!owner.retained()&&backend.releases==1&&backend.drains==1);
        assert(owner.nextGeneration()==2);assert(owner.start(reader,limits,expected,backend.services(2))==R::Running);
        assert(owner.event(1,event)==L::Invalid&&!owner.callbacks().acquire(1));
        assert(owner.callbacks().acquire(2));assert(owner.stop(3,10)==L::Pending);
        assert(owner.stop(13,10)==L::RebootRequired&&owner.retained()&&backend.releases==1);
        owner.callbacks().release();assert(owner.stop(14,10)==L::RebootRequired&&owner.retained());
    }
    puts("image owner: 15 scenarios; validation/reservation/publish ordering, immutable digest, partial start, lease drain, resident resource drain with sticky failure, stop failure/timeout retention, reload generation passed (host entries)");
}
