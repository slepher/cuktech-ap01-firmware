#include "apx2.h"
#include "native_integrity_0041.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <fstream>
#include <iterator>
#include <vector>

static void put(uint8_t *p,uint32_t v) {for(unsigned i=0;i<4;++i)p[i]=uint8_t(v>>(8*i));}
static uint32_t get(const uint8_t *p) {return uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16|uint32_t(p[3])<<24;}
struct Input {
    std::vector<uint8_t> bytes;
    unsigned calls=0, fail=0, largest=0;
    static bool read(void *p,uint32_t offset,uint8_t *out,uint32_t n) {
        auto &s=*(Input *)p;++s.calls;if(n>s.largest)s.largest=n;
        if(s.fail==s.calls)return false;
        assert(offset<=s.bytes.size()&&n<=s.bytes.size()-offset);
        memcpy(out,s.bytes.data()+offset,n);return true;
    }
    Apx2Reader reader() {return {this,uint32_t(bytes.size()),read};}
};
static void seal(std::vector<uint8_t> &p) {
    memset(p.data()+192,0,32);uint8_t hash[32];syncSha256(p.data(),p.size(),hash);memcpy(p.data()+192,hash,32);
}
static std::vector<uint8_t> fixture() {
    std::vector<uint8_t> p(320);memcpy(p.data(),"APX2",4);
    const uint32_t words[]={2,256,320,1,1,2,0,1,0,256,48,0,16,16,16,32,16,16,16,128,256,
                            0,2,4,6,8,304,2,1,3,2};
    for(unsigned i=0;i<31;++i)put(p.data()+4+4*i,words[i]);
    memcpy(p.data()+128,"test.app",9);memcpy(p.data()+160,"1.0.0",6);
    put(p.data()+288,48);put(p.data()+304,16);put(p.data()+308,0);put(p.data()+312,32);put(p.data()+316,48);
    seal(p);return p;
}
static Apx2Limits limits() {return {4096,4096,1024,1024,2,1,"test.app"};}
static void run() {
    Input input{fixture()};Apx2View view{};auto l=limits();
    assert(apx2Validate(input.reader(),l,view)==Apx2Error::Ok);
    assert(view.image_bytes==48&&view.bss_bytes==16&&input.largest<=256);
    for(uint32_t base:{0x62fc0000u,0xa8000000u}) {
        uint8_t memory[80];memset(memory,0xa5,sizeof(memory));
        assert(apx2Load(input.reader(),l,memory,64,base,view)==Apx2Error::Ok);
        assert(get(memory+16)==base&&get(memory+32)==base+48);
        for(unsigned i=48;i<64;++i)assert(memory[i]==0);
        for(unsigned i=64;i<80;++i)assert(memory[i]==0xa5);
    }
    const struct {unsigned offset;uint32_t value;Apx2Error error;} cases[]={
        {0,0,Apx2Error::Header},{4,1,Apx2Error::Header},{8,112,Apx2Error::Header},
        {12,319,Apx2Error::Header},{16,99,Apx2Error::Target},{20,99,Apx2Error::Target},
        {24,99,Apx2Error::Abi},{28,1,Apx2Error::Abi},{32,2,Apx2Error::Services},
        {36,1,Apx2Error::Services},{40,252,Apx2Error::Bounds},{44,0xffffffff,Apx2Error::Bounds},
        {48,4,Apx2Error::Bounds},{52,0,Apx2Error::Bounds},{56,15,Apx2Error::Bounds},
        {60,32,Apx2Error::Bounds},{64,16,Apx2Error::Bounds},{68,0xffffffff,Apx2Error::Bounds},
        {72,0xffffffff,Apx2Error::Bounds},{76,32,Apx2Error::Bounds},{80,4096,Apx2Error::Budget},
        {84,128,Apx2Error::Budget},{88,1,Apx2Error::Entry},{92,16,Apx2Error::Entry},
        {108,300,Apx2Error::Bounds},{112,0xffffffff,Apx2Error::Bounds},
        {116,3,Apx2Error::DataVersion},{120,1,Apx2Error::DataVersion},{124,3,Apx2Error::DataVersion},
        {128,0,Apx2Error::Identity},{224,1,Apx2Error::Header},{304,0,Apx2Error::Fixup},
        {304,17,Apx2Error::Fixup},{308,64,Apx2Error::Fixup},{312,16,Apx2Error::Fixup},
        {316,0,Apx2Error::Fixup}};
    for(auto c:cases) {
        Input corrupt{fixture()};put(corrupt.bytes.data()+c.offset,c.value);seal(corrupt.bytes);
        uint8_t memory[64];memset(memory,0xa5,sizeof(memory));
        auto got=apx2Load(corrupt.reader(),l,memory,64,0x62fc0000,view);
        if(got!=c.error)fprintf(stderr,"offset %u: got %s expected %s\n",c.offset,apx2ErrorName(got),apx2ErrorName(c.error));
        assert(got==c.error&&view.image_bytes==0);
        for(auto x:memory)assert(x==0xa5);
    }
    for(unsigned n=0;n<320;++n) {
        Input truncated{fixture()};truncated.bytes.resize(n);
        assert(apx2Validate(truncated.reader(),l,view)!=Apx2Error::Ok);
    }
    input.bytes=fixture();input.bytes[260]^=1;
    assert(apx2Validate(input.reader(),l,view)==Apx2Error::Integrity);
    input.bytes=fixture();l.app_id="other";assert(apx2Validate(input.reader(),l,view)==Apx2Error::Identity);l=limits();
    l.package_bytes=319;assert(apx2Validate(input.reader(),l,view)==Apx2Error::Budget);l=limits();
    l.memory_bytes=447;assert(apx2Validate(input.reader(),l,view)==Apx2Error::Budget);l=limits();
    input.calls=0;assert(apx2Validate(input.reader(),l,view)==Apx2Error::Ok);unsigned validation_calls=input.calls;
    for(unsigned fail=1;fail<=validation_calls+3;++fail) {
        input.calls=0;input.fail=fail;uint8_t memory[64];memset(memory,0xa5,64);
        assert(apx2Load(input.reader(),l,memory,64,0x62fc0000,view)==Apx2Error::Read);
        for(auto x:memory)assert(x==(fail<=validation_calls?0xa5:0));
    }
    input.fail=0;uint8_t memory[64];memset(memory,0xa5,64);
    assert(apx2Load(input.reader(),l,memory,63,0x62fc0000,view)==Apx2Error::Memory);
    assert(apx2Load(input.reader(),l,memory,64,0xfffffff0,view)==Apx2Error::Memory);
    assert(apx2Load(input.reader(),l,memory,64,0x62fc0001,view)==Apx2Error::Memory);
    // New boot path refuses legacy five-entry ABI even when the digest is valid.
    l.abi_major=APX2_DIRECT_ABI_MAJOR;
    assert(apx2Load(input.reader(),l,memory,64,0x62fc0000,view)==Apx2Error::Abi);
    input.bytes=fixture();put(input.bytes.data()+24,3);
    put(input.bytes.data()+100,0);put(input.bytes.data()+104,0);seal(input.bytes);
    assert(apx2Load(input.reader(),l,memory,64,0x62fc0000,view)==Apx2Error::Ok);
    assert(view.abi_major==3&&view.entries[2]==4&&view.entries[3]==0&&view.entries[4]==0);
    l.abi_major=2;
    assert(apx2Validate(input.reader(),l,view)==Apx2Error::Abi);
    l.abi_major=3;
    for(unsigned offset:{100u,104u}) {
        put(input.bytes.data()+offset,2);seal(input.bytes);
        memset(memory,0xa5,64);
        assert(apx2Load(input.reader(),l,memory,64,0x62fc0000,view)==Apx2Error::Entry);
        for(auto x:memory)assert(x==0xa5);
        put(input.bytes.data()+offset,0);seal(input.bytes);
    }
    l.abi_major=99;assert(apx2Validate(input.reader(),l,view)==Apx2Error::Abi);
    puts("APX2: two load bases, 36 corrupt fields, every truncation, read faults, integrity and resource limits passed");
}
int main(int argc,char **argv) {
    if(argc==3) {
        std::ifstream file(argv[2],std::ios::binary);assert(file);
        Input input{{std::istreambuf_iterator<char>(file),std::istreambuf_iterator<char>()}};
        if(!strcmp(argv[1],"--sha")) {
            Ap01Sha256 sha;for(auto &c:input.bytes)sha.update(&c,1);
            uint8_t a[32],b[32];sha.finish(a);syncSha256(input.bytes.data(),input.bytes.size(),b);assert(!memcmp(a,b,32));
            for(auto c:a)printf("%02x",c);puts("");return 0;
        }
        bool app=!strcmp(argv[1],"--app-v3");
        bool direct=app||!strcmp(argv[1],"--package-v3");
        assert(direct||!strcmp(argv[1],"--package"));Apx2View view{};auto l=limits();l.app_id=nullptr;l.services=UINT64_MAX;
        if(direct)l.abi_major=APX2_DIRECT_ABI_MAJOR;
        if(app)l={1u<<22,1u<<23,1u<<22,1u<<20,1,UINT64_MAX,"codex_status",APX2_DIRECT_ABI_MAJOR};
        auto error=apx2Validate(input.reader(),l,view);printf("%s\n",apx2ErrorName(error));
        if(app&&error==Apx2Error::Ok){
            for(uint32_t base:{0x62f00000u,0xa8000000u}){
                uint32_t size=view.image_bytes+view.bss_bytes;
                std::vector<uint8_t> memory(size+16,0xa5);
                assert(apx2Load(input.reader(),l,memory.data(),size,base,view)==Apx2Error::Ok);
                for(uint32_t i=view.image_bytes;i<size;++i)assert(memory[i]==0);
                for(uint32_t i=size;i<size+16;++i)assert(memory[i]==0xa5);
                for(uint32_t i=0;i<view.fixup_count;++i){
                    const auto *record=input.bytes.data()+256+view.image_bytes+i*8;
                    assert(get(memory.data()+get(record))==base+get(record+4));
                }
            }
            puts("real ABI 3 package: production loader two synthetic bases, every fixup/BSS/guard checked; no execution");
        }
        return error==Apx2Error::Ok?0:1;
    }
    run();
}
