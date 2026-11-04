#include "app_set_http_v3.h"
#include "native_integrity_0041.h"
#include <string.h>
namespace {
bool hex(const char *text,uint8_t *out,unsigned n){
    if(!text||strlen(text)!=2*n)return false;
    for(unsigned i=0;i<2*n;++i){unsigned c=text[i];int v=c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:c>='A'&&c<='F'?c-'A'+10:-1;
        if(v<0)return false;
        if(!(i&1))out[i/2]=uint8_t(v<<4);else out[i/2]|=uint8_t(v);}
    return true;
}
uint32_t u32(const uint8_t *p){return uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16|uint32_t(p[3])<<24;}
bool number(const char *s,uint32_t &out){
    out=0;if(!s||!*s||(*s=='0'&&s[1]))return false;
    for(unsigned i=0;s[i];++i){if(i>=10||s[i]<'0'||s[i]>'9')return false;unsigned digit=s[i]-'0';
        if(out>(UINT32_MAX-digit)/10)return false;
        out=out*10+digit;}
    return true;
}
}
int ap01ParseSetHttpV3(const Ap01HttpRequest &r,const char *mac,Ap01SetHttpCommandV3 &out){
    out={};if(!r.method||!r.path)return 400;
    Ap01SetHttpCommandV3 value{};const char *method=nullptr;
    if(!strcmp(r.path,"/api/app/v3/status")){value.action=Ap01SetHttpActionV3::Status;method="GET";}
    else if(!strcmp(r.path,"/api/app/v3/update/result")){value.action=Ap01SetHttpActionV3::Result;method="GET";}
    else if(!strcmp(r.path,"/api/app/v3/update/begin")){value.action=Ap01SetHttpActionV3::Begin;method="POST";}
    else if(!strcmp(r.path,"/api/app/v3/update/commit")){value.action=Ap01SetHttpActionV3::Commit;method="POST";}
    else if(!strcmp(r.path,"/api/app/v3/update/cancel")){value.action=Ap01SetHttpActionV3::Cancel;method="POST";}
    else {
        constexpr unsigned prefix=sizeof("/api/app/v3/package/")-1;
        if(strncmp(r.path,"/api/app/v3/package/",prefix))return 404;
        if(r.path[prefix]<'0'||r.path[prefix]>'7')return 404;
        value.index=unsigned(r.path[prefix]-'0');
        const char *suffix=r.path+prefix+1;
        if(!strcmp(suffix,"/chunk")){value.action=Ap01SetHttpActionV3::Chunk;method="PUT";}
        else if(!strcmp(suffix,"/ready")){value.action=Ap01SetHttpActionV3::Ready;method="POST";}
        else return 404;
    }
    if(strcmp(r.method,method))return 405;
    if(value.action!=Ap01SetHttpActionV3::Status){
        if(!mac||!r.deviceMac||strcmp(mac,r.deviceMac)||!hex(r.requestId,value.transaction,16))return 400;
        uint8_t any=0;for(auto b:value.transaction)any|=b;if(!any)return 400;
    }
    if(value.action==Ap01SetHttpActionV3::Begin){
        if(r.length>64+3584)return 413;
        if(!r.body||r.length<128||!r.contentType||strcmp(r.contentType,"application/octet-stream"))return 400;
        const auto *p=r.body;
        if(memcmp(p,"ASB3",4)||p[4]!=1||p[5]||p[6]!=64||p[7]||u32(p+48)!=r.length-64)return 400;
        for(unsigned i=52;i<64;++i)if(p[i])return 400;
        memcpy(value.expected,p+8,32);value.expectedVersion=uint64_t(u32(p+40))|uint64_t(u32(p+44))<<32;
        uint8_t any=0;for(auto b:value.expected)any|=b;
        if(bool(any)!=bool(value.expectedVersion))return 400;
        value.bytes=p+64;value.length=uint32_t(r.length-64);
    }else if(value.action==Ap01SetHttpActionV3::Chunk){
        if(r.length>1024)return 413;
        if(!r.body||!r.length||!r.contentType||strcmp(r.contentType,"application/octet-stream")||!number(r.offset,value.offset))return 400;
        if(r.length>UINT32_MAX-value.offset)return 400;
        uint8_t expected[32],actual[32];if(!hex(r.chunkSha256,expected,32))return 400;
        syncSha256(r.body,r.length,actual);if(memcmp(expected,actual,32))return 400;
        value.bytes=r.body;value.length=uint32_t(r.length);
    }else if(r.length)return 400;
    out=value;return 200;
}
