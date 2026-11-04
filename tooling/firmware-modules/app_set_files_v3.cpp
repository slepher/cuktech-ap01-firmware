#include "app_set_files_v3.h"
#include <string.h>
#include <new>
#include <limits.h>
using R=Ap01SetFilesResultV3;
bool Ap01AppSetFilesV3::readFile(const char *path,uint8_t *out,uint32_t capacity,uint32_t &size,bool exact){
    if(!path||!io.open||!io.close||!io.size||!io.read)return false;
    int fd=io.open(io.context,path,0);if(fd<0)return false;
    int32_t bytes=io.size(io.context,fd);bool okay=bytes>=0&&uint32_t(bytes)<=capacity&&(!exact||uint32_t(bytes)==capacity);
    uint32_t at=0;
    while(okay&&at<uint32_t(bytes)){
        uint32_t n=uint32_t(bytes)-at;if(n>1024)n=1024;
        int got=io.read(io.context,fd,out+at,n);
        if(got<=0||uint32_t(got)>n)okay=false;else at+=uint32_t(got);
    }
    if(io.close(io.context,fd))okay=false;
    if(okay)size=at;
    return okay;
}
bool Ap01AppSetFilesV3::readManifest(void *p,uint32_t at,uint8_t *out,uint32_t n){
    auto &s=*(Ap01AppSetFilesV3 *)p;if(at>s.manifestSize||n>s.manifestSize-at)return false;
    memcpy(out,s.manifestBytes+at,n);return true;
}
bool Ap01AppSetFilesV3::readPackage(void *p,uint32_t at,uint8_t *out,uint32_t n){
    auto &s=*(Buffer *)p;if(at>s.size||n>s.size-at)return false;
    memcpy(out,s.bytes.get()+at,n);return true;
}
bool Ap01AppSetFilesV3::open(void *p,const Ap01ManifestEntryV3 &entry,Apx2Reader &out,uint32_t &version){
    auto &s=*(Ap01AppSetFilesV3 *)p;
    for(unsigned i=0;i<s.manifest.count;++i){const auto &e=s.manifest.entries[i];auto &b=s.buffers[i];
        if(!strcmp(e.id,entry.id)&&!memcmp(e.digest,entry.digest,32)&&b.bytes&&b.size==entry.package_bytes){
            out={&b,b.size,readPackage};version=1;return true;}}
    return false;
}
void Ap01AppSetFilesV3::close(void *,Apx2Reader &r){r={};}
void Ap01AppSetFilesV3::discard(){for(auto &b:buffers){b.bytes.reset();b.size=0;}manifestSize=0;manifest={};}
R Ap01AppSetFilesV3::stage(const char *path,const uint8_t *expected,const Ap01ManifestLimitsV3 &limits,uint32_t stagingBytes){
    discard();
    if(!readFile(path,manifestBytes,sizeof(manifestBytes),manifestSize,false))return R::Io;
    if(ap01ReadManifestV3(reader(),limits,manifest)!=Ap01ManifestErrorV3::Ok)return R::Manifest;
    if(expected&&memcmp(expected,manifest.digest,32))return R::Identity;
    uint64_t bytes=0;for(unsigned i=0;i<manifest.count;++i)bytes+=manifest.entries[i].package_bytes;
    if(bytes>stagingBytes)return R::Budget;
    for(unsigned i=0;i<manifest.count;++i){auto &e=manifest.entries[i];auto &b=buffers[i];
        b.bytes.reset(new(std::nothrow) uint8_t[e.package_bytes]);if(!b.bytes){discard();return R::Memory;}
        char path[112]="/resource/app-store/packages/";constexpr unsigned prefix=sizeof("/resource/app-store/packages/")-1;const char *hex="0123456789abcdef";
        for(unsigned j=0;j<32;++j){path[prefix+2*j]=hex[e.digest[j]>>4];path[prefix+2*j+1]=hex[e.digest[j]&15];}
        memcpy(path+prefix+64,".apx2",6);
        if(!readFile(path,b.bytes.get(),e.package_bytes,b.size,true)){discard();return R::Io;}
    }
    if(ap01CheckManifestPackagesV3(manifest,packages())!=Ap01ManifestErrorV3::Ok){discard();return R::Package;}
    return R::Ready;
}
