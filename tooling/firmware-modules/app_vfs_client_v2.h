#pragma once
#include "app_file_abi_v2.h"
#include "native_filesystem_0041.h"
// App-private adapter: these C++ callbacks stay inside the App. Only the stable
// invoke service table crosses into firmware; no native fd or VFS table does.
class Ap01AppVfsClientV2 {
    ap01_app_services_v2 services;
    const char *prefix;
    int call(unsigned op,const ap01_app_file_request_v2 &r,void *out,uint32_t capacity,uint32_t &written,const void *data=nullptr){
        written=0;
        if(services.abi_version!=2||services.struct_bytes!=sizeof(services)||services.reserved||
           !services.generation||!services.invoke||!(services.available_services&AP01_APP_FILE_CAPABILITY))return -1;
        if(op==AP01_FILE_WRITE){
            if(r.argument>AP01_APP_FILE_CHUNK||(r.argument&&!data))return -1;
            uint8_t input[sizeof(r)+AP01_APP_FILE_CHUNK];memcpy(input,&r,sizeof(r));
            if(r.argument)memcpy(input+sizeof(r),data,r.argument);
            return services.invoke(services.context,services.generation,2,op,input,sizeof(r)+r.argument,out,capacity,&written);
        }
        return services.invoke(services.context,services.generation,2,op,&r,sizeof(r),out,capacity,&written);
    }
    int32_t word(unsigned op,const ap01_app_file_request_v2 &r,const void *data=nullptr){
        uint32_t value=0,written=0;
        return call(op,r,&value,4,written,data)||written!=4||value>INT32_MAX?-1:int32_t(value);
    }
    bool path(const char *absolute,char (&out)[96]) const {
        if(!absolute||!prefix)return false;
        size_t n=strlen(prefix);if(strncmp(absolute,prefix,n)||absolute[n]!='/')return false;
        size_t length=strlen(absolute+n);if(!length||length>=sizeof(out))return false;
        memcpy(out,absolute+n,length+1);return true;
    }
    static int capacity(void *p,const char *root,uint64_t *total,uint64_t *used){
        auto &c=*(Ap01AppVfsClientV2 *)p;if(!root||!c.prefix||strcmp(root,c.prefix)||!total||!used)return -1;
        ap01_app_file_request_v2 r{};uint64_t sizes[2]={};uint32_t written=0;
        if(c.call(AP01_FILE_CAPACITY,r,sizes,16,written)||written!=16||sizes[1]>sizes[0])return -1;
        *total=sizes[0];*used=sizes[1];return 0;
    }
    static int prepare(void *p,const char *root){uint64_t total,used;return capacity(p,root,&total,&used);}
    static int open(void *p,const char *path,unsigned mode){
        auto &c=*(Ap01AppVfsClientV2 *)p;ap01_app_file_request_v2 r{};r.argument=mode;
        return mode>2||!c.path(path,r.path)?-1:c.word(AP01_FILE_OPEN,r);
    }
    static int close(void *p,int fd){
        if(fd<0)return -1;
        ap01_app_file_request_v2 r{};r.handle=uint32_t(fd);uint32_t written=0;
        return ((Ap01AppVfsClientV2 *)p)->call(AP01_FILE_CLOSE,r,nullptr,0,written)||written?-1:0;
    }
    static int read(void *p,int fd,void *output,size_t length){
        if(fd<0||length>INT32_MAX||(length&&!output))return -1;
        auto &c=*(Ap01AppVfsClientV2 *)p;ap01_app_file_request_v2 r{};r.handle=uint32_t(fd);
        size_t done=0;while(done<length){
            uint32_t n=uint32_t(length-done>AP01_APP_FILE_CHUNK?AP01_APP_FILE_CHUNK:length-done),written=0;
            if(c.call(AP01_FILE_READ,r,(uint8_t *)output+done,n,written)||written>n)return -1;
            done+=written;if(written<n)break;
        }
        return int(done);
    }
    static int write(void *p,int fd,const void *input,size_t length){
        if(fd<0||length>INT32_MAX||(length&&!input))return -1;
        auto &c=*(Ap01AppVfsClientV2 *)p;ap01_app_file_request_v2 r{};r.handle=uint32_t(fd);
        size_t done=0;do {
            r.argument=uint32_t(length-done>AP01_APP_FILE_CHUNK?AP01_APP_FILE_CHUNK:length-done);
            int32_t n=c.word(AP01_FILE_WRITE,r,input?(const uint8_t *)input+done:nullptr);
            if(n<0||uint32_t(n)!=r.argument)return -1;
            done+=r.argument;
        }while(done<length);
        return int(done);
    }
    static int32_t seek(void *p,int fd,int32_t at,unsigned origin){
        if(fd<0)return -1;
        ap01_app_file_request_v2 r{};r.handle=uint32_t(fd);r.offset=at;r.origin=origin;
        return ((Ap01AppVfsClientV2 *)p)->word(AP01_FILE_SEEK,r);
    }
    static int32_t size(void *p,int fd){
        if(fd<0)return -1;
        ap01_app_file_request_v2 r{};r.handle=uint32_t(fd);return ((Ap01AppVfsClientV2 *)p)->word(AP01_FILE_SIZE,r);
    }
    int pathOperation(unsigned op,const char *path,const char *destination=nullptr){
        ap01_app_file_request_v2 r{};if(!this->path(path,r.path)||(destination&&!this->path(destination,r.destination)))return -1;
        if(op==AP01_FILE_EXISTS){int32_t value=word(op,r);return value<=1?value:-1;}
        uint32_t written=0;return call(op,r,nullptr,0,written)||written?-1:0;
    }
    static int exists(void *p,const char *path){return ((Ap01AppVfsClientV2 *)p)->pathOperation(AP01_FILE_EXISTS,path);}
    static int mkdir(void *p,const char *path){return ((Ap01AppVfsClientV2 *)p)->pathOperation(AP01_FILE_MKDIR,path);}
    static int remove(void *p,const char *path){return ((Ap01AppVfsClientV2 *)p)->pathOperation(AP01_FILE_REMOVE,path);}
    static int rename(void *p,const char *a,const char *b){return ((Ap01AppVfsClientV2 *)p)->pathOperation(AP01_FILE_RENAME,a,b);}
public:
    Ap01AppVfsClientV2(const ap01_app_services_v2 &table,const char *privateRoot):services(table),prefix(privateRoot){}
    Ap01AppVfsClientV2(const Ap01AppVfsClientV2 &)=delete;
    Ap01AppVfsClientV2 &operator=(const Ap01AppVfsClientV2 &)=delete;
    Ap01VfsOps ops(){return {this,prepare,open,close,read,write,seek,size,exists,mkdir,remove,rename,capacity};}
};
