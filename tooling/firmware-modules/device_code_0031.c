#include "device_code_0031.h"
static const char stored[]="/data/ap01_0031.device_code";
static const char temporary[]="/data/ap01_0031.device_code.new";
static uint32_t crc(const unsigned char *p,unsigned n)
{
    uint32_t c=~0u;
    while(n--){c^=*p++;for(unsigned i=0;i<8;i++)c=(c>>1)^(0xedb88320u&(0u-(c&1)));}
    return ~c;
}
static int read_code(const ap01_code_io_0031 *io,const char *path,char out[9])
{
    unsigned char b[16];int r=io->read(io->context,path,b);
    if(r)return r;
    uint32_t check=0;for(unsigned i=0;i<4;i++)check|=(uint32_t)b[12+i]<<(8*i);
    if(memcmp(b,"DVC1",4)||crc(b,12)!=check)return -22;
    for(unsigned i=4;i<12;i++)if(b[i]<'0'||b[i]>'9')return -22;
    memcpy(out,b+4,8);out[8]=0;return 0;
}
int ap01_code_load_0031(const ap01_code_io_0031 *io,char out[9])
{ out[0]=0;return read_code(io,stored,out); }
static int commit(const ap01_code_io_0031 *io,const char code[9],const char *previous,char out[9])
{
    /* A rename error can still mean committed. Read the authoritative name. */
    io->replace(io->context,temporary,stored);
    char actual[9];int r=read_code(io,stored,actual);
    if(!r&&!memcmp(actual,code,9)){memcpy(out,code,9);return 0;}
    if(!r&&previous&&!memcmp(actual,previous,9))return -5;
    return -115;
}
static int generate(const ap01_code_io_0031 *io,const char *previous,char out[9])
{
    for(unsigned attempt=0;attempt<32;attempt++){
        unsigned char bytes[4];if(!io->random(io->context,bytes))return -11;
        uint32_t v=0;for(unsigned i=0;i<4;i++)v|=(uint32_t)bytes[i]<<(8*i);
        if(v>=4200000000u)continue;
        v%=100000000u;
        char code[9];code[8]=0;
        for(unsigned i=8;i;i--){code[i-1]=(char)('0'+v%10);v/=10;}
        if(previous&&!memcmp(previous,code,9))continue;
        unsigned char b[16];memcpy(b,"DVC1",4);memcpy(b+4,code,8);
        uint32_t c=crc(b,12);for(unsigned i=0;i<4;i++)b[12+i]=(unsigned char)(c>>(8*i));
        if(io->write(io->context,temporary,b))return -5;
        char check[9];if(read_code(io,temporary,check)||memcmp(check,code,9))return -5;
        return commit(io,code,previous,out);
    }
    return -11;
}
int ap01_code_ensure_0031(const ap01_code_io_0031 *io,char out[9])
{
    int r=ap01_code_load_0031(io,out);if(r!=-2)return r;
    char pending[9];r=read_code(io,temporary,pending);
    if(!r)return commit(io,pending,NULL,out);
    return r==-2?generate(io,NULL,out):r;
}
int ap01_code_regenerate_0031(const ap01_code_io_0031 *io,char out[9])
{
    char previous[9];out[0]=0;int r=read_code(io,stored,previous);
    if(r&&r!=-2&&r!=-22)return r;
    return generate(io,r?NULL:previous,out);
}
int ap01_code_auth_0031(ap01_code_gate_0031 *gate,const char *actual,
                        const char *token,size_t length,uint64_t now)
{
    if(now<gate->retry_at)return AP01_CODE_LIMITED;
    if(!actual||!actual[0])return AP01_CODE_UNAVAILABLE;
    unsigned mismatch=!token||length!=8;
    if(!mismatch)for(unsigned i=0;i<8;i++)mismatch|=(unsigned char)actual[i]^(unsigned char)token[i];
    if(mismatch){
        if(++gate->failures>=5){gate->failures=0;gate->retry_at=now+30000;}
        return AP01_CODE_DENIED;
    }
    gate->failures=0;gate->retry_at=0;return AP01_CODE_OK;
}
