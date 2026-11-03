#include "apx2.h"
#include "native_integrity_0041.h"
#include <string.h>

namespace {
uint32_t u32(const uint8_t *p) {
    return uint32_t(p[0]) | uint32_t(p[1]) << 8 | uint32_t(p[2]) << 16 | uint32_t(p[3]) << 24;
}
void put32(uint8_t *p, uint32_t v) {
    for (unsigned i=0;i<4;++i) p[i]=uint8_t(v>>(8*i));
}
bool inside(uint32_t at, uint32_t n, uint32_t start, uint32_t size) {
    return at >= start && at - start <= size && n <= size - (at - start);
}
bool identifier(const uint8_t *p) {
    unsigned i=0;
    while(i<32 && p[i]) {
        uint8_t c=p[i++];
        if(!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||
             c=='.'||c=='_'||c=='-'||c=='+')) return false;
    }
    if(!i || i==32) return false;
    while(i<32) if(p[i++]) return false;
    return true;
}
bool read(const Apx2Reader &r,uint32_t offset,uint8_t *out,uint32_t n) {
    return r.read && offset<=r.size && n<=r.size-offset && r.read(r.context,offset,out,n);
}
bool pointer(const Apx2View &v,uint32_t at) {
    return inside(at,1,0,v.text_bytes) || inside(at,1,v.ro_offset,v.ro_bytes) ||
           inside(at,1,v.data_offset,v.data_bytes+v.bss_bytes);
}
bool destination(const Apx2View &v,uint32_t at) {
    return !(at&3) && (inside(at,4,v.ro_offset,v.ro_bytes)||inside(at,4,v.data_offset,v.data_bytes));
}
}

Apx2Error apx2Validate(const Apx2Reader &r,const Apx2Limits &limit,Apx2View &out) {
    out={};
    if(r.size<APX2_HEADER) return Apx2Error::Header;
    if(r.size>limit.package_bytes) return Apx2Error::Budget;
    uint8_t h[APX2_HEADER];
    if(!read(r,0,h,sizeof(h))) return Apx2Error::Read;
    if(memcmp(h,"APX2",4)||u32(h+4)!=2||u32(h+8)!=APX2_HEADER||u32(h+12)!=r.size)
        return Apx2Error::Header;
    for(unsigned i=224;i<APX2_HEADER;++i) if(h[i]) return Apx2Error::Header;
    if(u32(h+16)!=APX2_TARGET_0041||u32(h+20)!=APX2_ISA_RV32IMAFC_ILP32F) return Apx2Error::Target;
    if((limit.abi_major!=APX2_ABI_MAJOR&&limit.abi_major!=APX2_DIRECT_ABI_MAJOR)||
       u32(h+24)!=limit.abi_major||u32(h+28)!=0) return Apx2Error::Abi;
    Apx2View v{};
    v.abi_major=limit.abi_major;
    v.required_services=uint64_t(u32(h+32))|uint64_t(u32(h+36))<<32;
    if(v.required_services & ~limit.services) return Apx2Error::Services;
    v.image_bytes=u32(h+44); v.text_bytes=u32(h+52);
    v.ro_offset=u32(h+56); v.ro_bytes=u32(h+60);
    v.data_offset=u32(h+64); v.data_bytes=u32(h+68); v.bss_bytes=u32(h+72);
    v.heap_bytes=u32(h+80); v.stack_bytes=u32(h+84); v.fixup_count=u32(h+112);
    uint64_t initialized_end=uint64_t(APX2_HEADER)+v.image_bytes;
    uint64_t expected_end=initialized_end+uint64_t(v.fixup_count)*8;
    uint64_t memory=uint64_t(v.image_bytes)+v.bss_bytes;
    if(u32(h+40)!=APX2_HEADER||u32(h+48)!=0||u32(h+76)!=16||!v.text_bytes||
       (v.ro_offset&15)||(v.data_offset&15)||(v.image_bytes&3)||
       !inside(0,v.text_bytes,0,v.image_bytes)||v.ro_offset<v.text_bytes||
       !inside(v.ro_offset,v.ro_bytes,0,v.image_bytes)||uint64_t(v.ro_offset)+v.ro_bytes>v.data_offset||
       uint64_t(v.data_offset)+v.data_bytes!=v.image_bytes||
       initialized_end!=u32(h+108)||expected_end!=r.size||v.fixup_count>v.image_bytes/4||
       memory>UINT32_MAX) return Apx2Error::Bounds;
    if(memory+v.heap_bytes+v.stack_bytes>limit.memory_bytes||v.heap_bytes>limit.heap_bytes||
       v.stack_bytes>limit.stack_bytes||v.stack_bytes<256||(v.stack_bytes&15)) return Apx2Error::Budget;
    if(!identifier(h+128)||!identifier(h+160)) return Apx2Error::Identity;
    memcpy(v.app_id,h+128,32);memcpy(v.version,h+160,32);memcpy(v.digest,h+192,32);
    if(limit.app_id && strcmp(limit.app_id,v.app_id)) return Apx2Error::Identity;
    v.data_read_min=u32(h+116);v.data_read_max=u32(h+120);v.data_write_version=u32(h+124);
    // First release cannot migrate persistent data while rollback remains possible.
    if(v.data_read_min>limit.data_version||v.data_read_max<limit.data_version||
       v.data_write_version!=limit.data_version) return Apx2Error::DataVersion;
    for(unsigned i=0;i<APX2_ENTRY_COUNT;++i) {
        v.entries[i]=u32(h+88+4*i);
        if(v.abi_major==APX2_DIRECT_ABI_MAJOR&&i>=APX2_DIRECT_ENTRY_COUNT) {
            if(v.entries[i]) return Apx2Error::Entry;
            continue;
        }
        if((v.entries[i]&1)||!inside(v.entries[i],2,0,v.text_bytes)) return Apx2Error::Entry;
    }
    uint32_t previous=0;
    for(uint32_t i=0;i<v.fixup_count;++i) {
        uint8_t record[8],word[4];
        if(!read(r,uint32_t(initialized_end)+8*i,record,8)) return Apx2Error::Read;
        uint32_t at=u32(record),target=u32(record+4);
        if(!destination(v,at)||!pointer(v,target)||(i&&at<=previous)) return Apx2Error::Fixup;
        if(!read(r,APX2_HEADER+at,word,4)) return Apx2Error::Read;
        if(u32(word)!=target) return Apx2Error::Fixup;
        previous=at;
    }
    Ap01Sha256 hash;
    memset(h+192,0,32); hash.update(h,sizeof(h));
    uint8_t chunk[256];
    for(uint32_t offset=APX2_HEADER;offset<r.size;) {
        uint32_t n=r.size-offset;if(n>sizeof(chunk))n=sizeof(chunk);
        if(!read(r,offset,chunk,n)) return Apx2Error::Read;
        for(uint32_t i=0;i<n;++i) {
            uint32_t at=offset+i-APX2_HEADER;
            if(at<v.image_bytes && ((at>=v.text_bytes&&at<v.ro_offset)||
               (at>=v.ro_offset+v.ro_bytes&&at<v.data_offset)) && chunk[i]) return Apx2Error::Bounds;
        }
        hash.update(chunk,n); offset+=n;
    }
    uint8_t digest[32];hash.finish(digest);
    unsigned mismatch=0;for(unsigned i=0;i<32;++i)mismatch|=digest[i]^v.digest[i];
    if(mismatch) return Apx2Error::Integrity;
    out=v;return Apx2Error::Ok;
}

Apx2Error apx2Load(const Apx2Reader &r,const Apx2Limits &limits,uint8_t *memory,
                   uint32_t capacity,uint32_t base,Apx2View &out) {
    out={};Apx2View v{};
    Apx2Error error=apx2Validate(r,limits,v);if(error!=Apx2Error::Ok)return error;
    uint32_t bytes=v.image_bytes+v.bss_bytes;
    if(!memory||(base&15)||uint64_t(base)+bytes>uint64_t(UINT32_MAX)+1||capacity<bytes)
        return Apx2Error::Memory;
    // Reader is exclusively owned and immutable until return; no execution yet.
    for(uint32_t offset=0;offset<v.image_bytes;) {
        uint32_t n=v.image_bytes-offset;if(n>256)n=256;
        if(!read(r,APX2_HEADER+offset,memory+offset,n)) {memset(memory,0,bytes);return Apx2Error::Read;}
        offset+=n;
    }
    memset(memory+v.image_bytes,0,v.bss_bytes);
    for(uint32_t i=0;i<v.fixup_count;++i) {
        uint8_t record[8];
        if(!read(r,APX2_HEADER+v.image_bytes+8*i,record,8)) {memset(memory,0,bytes);return Apx2Error::Read;}
        uint32_t at=u32(record),target=u32(record+4);
        // Recheck even the immutable reader contract before writing a pointer.
        if(!destination(v,at)||!pointer(v,target)) {memset(memory,0,bytes);return Apx2Error::Fixup;}
        put32(memory+at,base+target);
    }
    out=v;return Apx2Error::Ok;
}
const char *apx2ErrorName(Apx2Error error) {
    switch(error) {
    case Apx2Error::Ok:return "ok";case Apx2Error::Read:return "read";
    case Apx2Error::Header:return "header";case Apx2Error::Bounds:return "bounds";
    case Apx2Error::Target:return "target";case Apx2Error::Abi:return "abi";
    case Apx2Error::Services:return "services";case Apx2Error::Budget:return "budget";
    case Apx2Error::Identity:return "identity";case Apx2Error::DataVersion:return "data_version";
    case Apx2Error::Entry:return "entry";case Apx2Error::Fixup:return "fixup";
    case Apx2Error::Integrity:return "integrity";case Apx2Error::Memory:return "memory";
    }
    return "unknown";
}
