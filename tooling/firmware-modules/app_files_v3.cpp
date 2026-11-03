#include "app_files_v3.h"
#include <string.h>
#include <limits.h>
#if defined(__riscv)
static_assert(sizeof(Ap01VfsOps)==52&&offsetof(Ap01VfsOps,statfs)==48,"RV32 direct VFS layout");
#endif

bool Ap01AppFilesV3::path(const char *p) const {
    if(!p||!root||root[0]!='/')return false;
    size_t n=strlen(root);
    if(!n||root[n-1]=='/'||strncmp(p,root,n)||p[n]!='/'||!p[n+1])return false;
    // Match existing LittleFS path budget; validate again at the platform edge.
    if(strlen(p)>=128)return false;
    for(const char *c=p+n;*c;++c){
        if((unsigned char)*c<32||*c=='\\')return false;
        if(*c=='/'&&(!c[1]||c[1]=='/'||(c[1]=='.'&&(!c[2]||c[2]=='/'||
           (c[2]=='.'&&(!c[3]||c[3]=='/'))))))return false;
    }
    return true;
}
Ap01AppFilesV3::Slot *Ap01AppFilesV3::slot(int handle){
    for(auto &s:slots)if(s.fd>=0&&s.handle==handle)return &s;
    return nullptr;
}
bool Ap01AppFilesV3::writes(bool allow){Guard g(this);if(!g)return false;writable=allow;return true;}
int Ap01AppFilesV3::capacity(void *p,const char *root,uint64_t *total,uint64_t *used){
    Guard g(p);auto &s=g.self;
    if(!g||!root||!s.root||strcmp(root,s.root)||!total||!used||!s.io.statfs)return -1;
    uint64_t t=0,u=0;
    if(s.io.statfs(s.io.context,s.root,&t,&u)||u>t)return -1;
    *total=t;*used=u;return 0;
}
int Ap01AppFilesV3::prepare(void *p,const char *root){uint64_t t,u;return capacity(p,root,&t,&u);}
int Ap01AppFilesV3::open(void *p,const char *path,unsigned mode){
    Guard g(p);auto &s=g.self;
    if(!g||mode>2||(mode&&!s.writable)||!s.path(path)||!s.io.open||!s.io.close||s.nextHandle>INT32_MAX)return -1;
    for(auto &slot:s.slots)if(slot.fd<0){
        int fd=s.io.open(s.io.context,path,mode);if(fd<0)return -1;
        slot={int(s.nextHandle++),fd,mode!=0};return slot.handle;
    }
    return -1;
}
int Ap01AppFilesV3::close(void *p,int handle){
    Guard g(p);auto &s=g.self;if(!g)return -1;auto *slot=s.slot(handle);if(!slot)return -1;
    // Ambiguous close cannot be retried against a potentially recycled fd.
    if(s.io.close(s.io.context,slot->fd)){s.failed=true;return -1;}
    *slot={};return 0;
}
int Ap01AppFilesV3::read(void *p,int handle,void *out,size_t n){
    Guard g(p);auto &s=g.self;if(!g||(n&&!out)||n>INT32_MAX||!s.io.read)return -1;
    auto *slot=s.slot(handle);if(!slot)return -1;
    int got=s.io.read(s.io.context,slot->fd,out,n);return got<0||size_t(got)>n?-1:got;
}
int Ap01AppFilesV3::write(void *p,int handle,const void *in,size_t n){
    Guard g(p);auto &s=g.self;
    if(!g||!s.writable||(n&&!in)||n>INT32_MAX||!s.io.write)return -1;
    auto *slot=s.slot(handle);if(!slot||!slot->writable)return -1;
    int got=s.io.write(s.io.context,slot->fd,in,n);return got<0||size_t(got)!=n?-1:got;
}
int32_t Ap01AppFilesV3::seek(void *p,int handle,int32_t at,unsigned origin){
    Guard g(p);auto &s=g.self;if(!g||origin>2||!s.io.seek)return -1;
    auto *slot=s.slot(handle);return slot?s.io.seek(s.io.context,slot->fd,at,origin):-1;
}
int32_t Ap01AppFilesV3::size(void *p,int handle){
    Guard g(p);auto &s=g.self;if(!g||!s.io.size)return -1;
    auto *slot=s.slot(handle);return slot?s.io.size(s.io.context,slot->fd):-1;
}
int Ap01AppFilesV3::exists(void *p,const char *path){
    Guard g(p);auto &s=g.self;if(!g||!s.path(path)||!s.io.exists)return -1;
    int n=s.io.exists(s.io.context,path);return n==0||n==1?n:-1;
}
int Ap01AppFilesV3::mkdir(void *p,const char *path){
    Guard g(p);auto &s=g.self;
    return g&&s.writable&&s.path(path)&&s.io.mkdir?s.io.mkdir(s.io.context,path):-1;
}
int Ap01AppFilesV3::remove(void *p,const char *path){
    Guard g(p);auto &s=g.self;
    return g&&s.writable&&s.path(path)&&s.io.remove?s.io.remove(s.io.context,path):-1;
}
int Ap01AppFilesV3::rename(void *p,const char *from,const char *to){
    Guard g(p);auto &s=g.self;
    return g&&s.writable&&s.path(from)&&s.path(to)&&s.io.rename?s.io.rename(s.io.context,from,to):-1;
}
