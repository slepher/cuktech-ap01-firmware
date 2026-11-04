#include "app_manifest_v3.h"
#include "native_integrity_0041.h"
#include <string.h>
namespace {
uint16_t u16(const uint8_t *p){return uint16_t(p[0])|uint16_t(p[1])<<8;}
uint32_t u32(const uint8_t *p){return uint32_t(u16(p))|uint32_t(u16(p+2))<<16;}
uint64_t u64(const uint8_t *p){return uint64_t(u32(p))|uint64_t(u32(p+4))<<32;}
bool zero(const uint8_t *p,unsigned n){while(n--)if(*p++)return false;return true;}
bool name(const uint8_t *p){
    unsigned n=0;while(n<32&&p[n]){uint8_t c=p[n++];
        if(!((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='.'||c=='_'||c=='-'||c=='+'))return false;}
    return n&&n<32&&zero(p+n,32-n);
}
bool read(const Apx2Reader &r,uint32_t at,uint8_t *p,uint32_t n){return r.read&&at<=r.size&&n<=r.size-at&&r.read(r.context,at,p,n);}
}
using E=Ap01ManifestErrorV3;
E ap01ReadManifestV3(const Apx2Reader &r,const Ap01ManifestLimitsV3 &limits,Ap01ManifestV3 &out){
    out={};uint8_t h[64];
    if(r.size<64)return E::Header;
    if(!read(r,0,h,64))return E::Read;
    uint32_t count=u16(h+12),deps=u16(h+24);
    if(memcmp(h,"AMF3",4)||u16(h+4)!=1||u16(h+6)!=64||u32(h+8)!=r.size||
       u16(h+14)!=160||!u64(h+16)||!zero(h+26,6)||count>AP01_MANIFEST_APPS_V3||
       deps>AP01_MANIFEST_DEPS_V3||r.size!=64+count*160+deps*40)return E::Header;
    if(count>limits.apps||limits.resident_bytes>limits.ram_bytes)return E::Resource;
    memcpy(out.digest,h+32,32);memset(h+32,0,32);Ap01Sha256 hash;hash.update(h,64);
    out.count=count;out.sequence=u64(h+16);
    uint64_t packages=0,images=0,heap=0,stack=0;uint32_t tasks=0,pages=0,orders=0;
    uint8_t b[160];
    for(uint32_t i=0;i<count;++i){
        if(!read(r,64+i*160,b,160))return E::Read;
        hash.update(b,160);auto &e=out.entries[i];
        if(!name(b)||!name(b+32)||zero(b+64,32))return E::Identity;
        memcpy(e.id,b,32);memcpy(e.version,b+32,32);memcpy(e.digest,b+64,32);
        if(!strcmp(e.id,".")||!strcmp(e.id,"..")||(i&&strcmp(out.entries[i-1].id,e.id)>=0))return E::Identity;
        e.package_bytes=u32(b+96);e.image_bytes=u32(b+100);e.heap_bytes=u32(b+104);e.stack_bytes=u32(b+108);
        e.data_min=u32(b+112);e.data_max=u32(b+116);e.data_write=u32(b+120);e.capabilities=u64(b+124);
        e.tcp=u16(b+132);e.udp=u16(b+134);e.order=u16(b+136);e.tasks=u16(b+138);e.pages=u16(b+140);
        if(u16(b+142)||u32(b+144)!=3||!zero(b+148,12))return E::Header;
        if(e.order>=count||(orders&(1u<<e.order)))return E::Order;
        orders|=1u<<e.order;out.order[e.order]=uint8_t(i);
        if(e.package_bytes<256||!e.image_bytes||e.stack_bytes<256||(e.stack_bytes&15)||
           e.data_min>e.data_write||e.data_write>e.data_max||e.capabilities&~limits.capabilities||
           e.tasks>4||e.pages>32||uint64_t(e.tasks)*256>e.stack_bytes||
           e.tcp==18080||e.udp==18080)return E::Resource;
        for(uint32_t j=0;j<i;++j){const auto &prior=out.entries[j];
            if((e.tcp&&e.tcp==prior.tcp)||(e.udp&&e.udp==prior.udp))return E::Resource;}
        packages+=e.package_bytes;images+=(uint64_t(e.image_bytes)+15)&~uint64_t(15);
        heap+=e.heap_bytes;stack+=e.stack_bytes;tasks+=e.tasks;pages+=e.pages;
    }
    if(packages>limits.package_bytes||images>limits.image_bytes||heap>limits.heap_bytes||stack>limits.stack_bytes||
       tasks>limits.tasks||pages>limits.pages||images+heap+stack>limits.ram_bytes-limits.resident_bytes)return E::Resource;
    uint32_t previous=0;
    for(uint32_t i=0;i<deps;++i){
        if(!read(r,64+count*160+i*40,b,40))return E::Read;
        hash.update(b,40);uint32_t owner=u16(b),target=u16(b+2),key=owner*8+target;
        if(owner>=count||target>=count||owner==target||!zero(b+4,4)||(i&&key<=previous)||
           out.entries[target].order>=out.entries[owner].order||memcmp(b+8,out.entries[target].digest,32))return E::Dependency;
        previous=key;
    }
    uint8_t digest[32];hash.finish(digest);return memcmp(digest,out.digest,32)?E::Integrity:E::Ok;
}
E ap01CheckManifestPackagesV3(const Ap01ManifestV3 &m,const Ap01ManifestPackagesV3 &io){
    if(m.count>AP01_MANIFEST_APPS_V3||!io.open||!io.close)return E::Header;
    for(uint32_t i=0;i<m.count;++i){const auto &e=m.entries[i];Apx2Reader reader{};uint32_t version=0;
        if(!io.open(io.context,e,reader,version))return E::Read;
        uint64_t memory=uint64_t(e.image_bytes)+e.heap_bytes+e.stack_bytes;
        Apx2View view{};Apx2Error result=Apx2Error::Budget;
        if(memory<=UINT32_MAX){Apx2Limits limit{e.package_bytes,uint32_t(memory),e.heap_bytes,e.stack_bytes,version,e.capabilities,e.id,3};
            result=apx2Validate(reader,limit,view);}
        bool same=result==Apx2Error::Ok&&reader.size==e.package_bytes&&
            !strcmp(e.version,view.version)&&!memcmp(e.digest,view.digest,32)&&
            uint64_t(view.image_bytes)+view.bss_bytes==e.image_bytes&&view.heap_bytes==e.heap_bytes&&
            view.stack_bytes==e.stack_bytes&&view.required_services==e.capabilities&&
            view.data_read_min==e.data_min&&view.data_read_max==e.data_max&&view.data_write_version==e.data_write;
        io.close(io.context,reader);if(!same)return E::Package;
    }
    return E::Ok;
}
