#include "app_manifest_v3.h"
#include "app_set_boot_v3.h"
#include "native_integrity_0041.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <vector>
using E=Ap01ManifestErrorV3;
static std::vector<uint8_t> load(const char *path){std::ifstream f(path,std::ios::binary);assert(f);return {std::istreambuf_iterator<char>(f),{}};}
struct File {
    std::vector<uint8_t> bytes;int fail=-1;
    static bool read(void *p,uint32_t at,uint8_t *out,uint32_t n){auto &f=*(File *)p;
        if(f.fail>=0&&at>=unsigned(f.fail))return false;
        if(at>f.bytes.size()||n>f.bytes.size()-at)return false;
        memcpy(out,f.bytes.data()+at,n);return true;}
    Apx2Reader reader(){return {this,uint32_t(bytes.size()),read};}
};
static void put(std::vector<uint8_t> &b,unsigned at,uint32_t n,unsigned bytes=4){for(unsigned i=0;i<bytes;++i)b[at+i]=n>>(8*i);}
static void sign(File &f){memset(f.bytes.data()+32,0,32);uint8_t digest[32];syncSha256(f.bytes.data(),f.bytes.size(),digest);memcpy(f.bytes.data()+32,digest,32);}
struct Packages {
    File files[2];unsigned opened=0,closed=0;int missing=-1;uint32_t data=1;
    static bool open(void *p,const Ap01ManifestEntryV3 &e,Apx2Reader &r,uint32_t &v){auto &s=*(Packages *)p;unsigned i=!strcmp(e.id,"codex_status")?0:1;
        if(int(i)==s.missing)return false;
        ++s.opened;r=s.files[i].reader();v=s.data;return true;}
    static void close(void *p,Apx2Reader &){++((Packages *)p)->closed;}
    Ap01ManifestPackagesV3 port(){return {this,open,close};}
};
struct Boot {
    Packages packages;bool maintenance=false;int fail=-1;unsigned prepared=0,starts=0;
    struct Slot {
        Boot *owner=nullptr;unsigned index=0;std::vector<uint8_t> memory;
        Ap01PlatformApiV3 api{};
        static bool ready(void *p){return ((Slot *)p)->owner->maintenance;}
        static bool reserve(void *p,const Apx2View &v,Ap01BootMemoryV3 &m){auto &s=*(Slot *)p;
            s.memory.resize(v.image_bytes+v.bss_bytes);m={s.memory.data(),uint32_t(s.memory.size()),0xa8000000+s.index*0x40000};return true;}
        static int32_t start(const Ap01PlatformApiV3 *,void *p,void **out){auto &s=*(Slot *)p;
            ++s.owner->starts;*out=p;return s.owner->fail==int(s.index)?AP01_APP_V3_FAILED:AP01_APP_V3_OK;}
        static int32_t event(void *,uint32_t,const void *,uint32_t){return 0;}
        static int32_t health(void *){return 0;}
        static bool publish(void *,const Ap01BootMemoryV3 &,const Apx2View &,Ap01AppEntriesV3 &e){e={start,event,health};return true;}
        Ap01AppBootV3 loader{Ap01BootPortV3{this,ready,reserve,publish}};
    } slots[2];
    Boot(const std::vector<uint8_t> &a,const std::vector<uint8_t> &b){packages.files[0].bytes=a;packages.files[1].bytes=b;
        for(unsigned i=0;i<2;++i){slots[i].owner=this;slots[i].index=i;slots[i].api.abi_major=3;
            slots[i].api.struct_bytes=sizeof(Ap01PlatformApiV3);slots[i].api.capabilities=127;}}
    static bool open(void *p,const Ap01ManifestEntryV3 &e,Apx2Reader &r,uint32_t &v){return Packages::open(&((Boot *)p)->packages,e,r,v);}
    static void close(void *p,Apx2Reader &r){Packages::close(&((Boot *)p)->packages,r);}
    static bool ready(void *p){return ((Boot *)p)->maintenance;}
    static bool prepare(void *p,const Ap01ManifestEntryV3 &e,Ap01AppBootV3 *&l,const Ap01PlatformApiV3 *&a,void *&c){
        auto &b=*(Boot *)p;++b.prepared;unsigned i=!strcmp(e.id,"codex_status")?0:1;auto &s=b.slots[i];l=&s.loader;a=&s.api;c=&s;return true;}
    Ap01AppSetPortV3 port(){return {{this,open,close},ready,prepare};}
};
int main(int argc,char **argv){
    assert(argc==4);File f{load(argv[1])};auto good=f.bytes;
    Ap01ManifestLimitsV3 limits{8,8u<<20,8u<<20,8u<<20,1u<<20,32,32,127,16u<<20,1u<<20};
    Ap01ManifestV3 view;assert(ap01ReadManifestV3(f.reader(),limits,view)==E::Ok&&view.count==2&&view.sequence==9);
    Packages io{{{load(argv[2])},{load(argv[3])}}};assert(ap01CheckManifestPackagesV3(view,io.port())==E::Ok&&io.opened==2&&io.closed==2);
    unsigned checks=1;
    auto reject=[&](unsigned at,uint32_t value,unsigned size,E expected){f.bytes=good;put(f.bytes,at,value,size);sign(f);assert(ap01ReadManifestV3(f.reader(),limits,view)==expected);++checks;};
    reject(4,2,2,E::Header);reject(12,9,2,E::Header);reject(26,1,1,E::Header);
    reject(64+144,2,4,E::Header);reject(64+148,1,1,E::Header);
    reject(64+136,2,2,E::Order);reject(64+160+136,0,2,E::Order);
    reject(64+132,18080,2,E::Resource);reject(64+160+132,18081,2,E::Resource);
    reject(64+138,5,2,E::Resource);reject(64+140,33,2,E::Resource);
    reject(64+124,128,1,E::Resource);reject(64+100,UINT32_MAX,4,E::Resource);
    reject(64+116,0,4,E::Resource);reject(64+160+32,'!',1,E::Identity);
    reject(64+320,0,2,E::Dependency);reject(64+320+2,7,2,E::Dependency);
    reject(64+320+8,0,1,E::Dependency);
    f.bytes=good;f.bytes[32]^=1;assert(ap01ReadManifestV3(f.reader(),limits,view)==E::Integrity);++checks;
    for(size_t n=0;n<good.size();++n){f.bytes.assign(good.begin(),good.begin()+n);assert(ap01ReadManifestV3(f.reader(),limits,view)!=E::Ok);++checks;}
    f.bytes=good;f.bytes.push_back(0);assert(ap01ReadManifestV3(f.reader(),limits,view)==E::Header);++checks;
    f.bytes=good;f.fail=64;assert(ap01ReadManifestV3(f.reader(),limits,view)==E::Read);f.fail=-1;++checks;
    auto low=limits;low.resident_bytes=low.ram_bytes;assert(ap01ReadManifestV3(f.reader(),low,view)==E::Resource);++checks;
    low=limits;low.apps=1;assert(ap01ReadManifestV3(f.reader(),low,view)==E::Resource);++checks;
    assert(ap01ReadManifestV3(f.reader(),limits,view)==E::Ok);
    io.missing=1;io.opened=io.closed=0;assert(ap01CheckManifestPackagesV3(view,io.port())==E::Read&&io.opened==io.closed);++checks;
    io.missing=-1;io.files[1].bytes.back()^=1;io.opened=io.closed=0;assert(ap01CheckManifestPackagesV3(view,io.port())==E::Package&&io.opened==io.closed);++checks;
    io.files[1].bytes.back()^=1;io.data=2;assert(ap01CheckManifestPackagesV3(view,io.port())==E::Package);++checks;
    io.data=1;view.entries[0].image_bytes++;assert(ap01CheckManifestPackagesV3(view,io.port())==E::Package);++checks;
    f.bytes=good;assert(ap01ReadManifestV3(f.reader(),limits,view)==E::Ok);
    using R=Ap01AppSetResultV3;
    for(unsigned scenario=0;scenario<4;++scenario){
        Boot boot(load(argv[2]),load(argv[3]));Ap01AppSetBootV3 set(boot.port());
        assert(set.boot(f.reader(),view.digest,limits)==R::Waiting&&!boot.prepared);
        boot.maintenance=true;if(scenario==1)boot.packages.files[1].bytes.back()^=1;
        if(scenario==2)boot.fail=1;
        auto expected=view; if(scenario==3)expected.digest[0]^=1;
        auto result=set.boot(f.reader(),expected.digest,limits);
        if(scenario==0){assert(result==R::Started&&set.startedCount()==2&&set.health()==0&&set.event(1,nullptr,0)==0);}
        if(scenario==1){assert(result==R::Packages&&!boot.prepared&&!boot.starts);}
        if(scenario==2){assert(result==R::Start&&set.startedCount()==1&&boot.starts==2&&set.failedIndex()==1);
            assert(boot.slots[0].loader.retained()&&boot.slots[1].loader.retained());}
        if(scenario==3){assert(result==R::Identity&&!boot.prepared&&!boot.starts);}
        assert(boot.packages.opened==boot.packages.closed);
        assert(set.boot(f.reader(),view.digest,limits)==R::AlreadyAttempted);++checks;
    }
    f.bytes.assign(good.begin(),good.begin()+64);put(f.bytes,8,64);put(f.bytes,12,0,2);put(f.bytes,24,0,2);sign(f);
    assert(ap01ReadManifestV3(f.reader(),limits,view)==E::Ok&&view.count==0);++checks;
    f.bytes.assign(good.begin(),good.begin()+64);put(f.bytes,8,64+8*160);put(f.bytes,12,8,2);put(f.bytes,24,0,2);
    for(unsigned i=0;i<8;++i){std::vector<uint8_t> entry(good.begin()+224,good.begin()+384);
        memset(entry.data(),0,32);entry[0]='a'+i;put(entry,136,i,2);f.bytes.insert(f.bytes.end(),entry.begin(),entry.end());}
    sign(f);assert(ap01ReadManifestV3(f.reader(),limits,view)==E::Ok&&view.count==8);++checks;
    f.bytes[64+160]='a';sign(f);assert(ap01ReadManifestV3(f.reader(),limits,view)==E::Identity);++checks;
    f.bytes=good;memset(f.bytes.data()+64,0,32);f.bytes[64]='.';sign(f);
    assert(ap01ReadManifestV3(f.reader(),limits,view)==E::Identity);++checks;
    printf("Manifest: %u checks; real package preflight, canonical metadata, dependencies, budgets, truncation, I/O and close ownership passed\n",checks);
}
