#include "app_files_0041.h"
#include <string.h>
static_assert(sizeof(ap01_app_file_request_v2)==208,"file C ABI");
namespace {
struct Unlock {std::atomic_flag &flag;~Unlock(){flag.clear(std::memory_order_release);}};
bool empty(const char *p,unsigned n){for(unsigned i=0;i<n;++i)if(p[i])return false;return true;}
}
bool Ap01AppFiles0041::path(const char input[96],char out[224]) const {
    auto *end=(const char *)memchr(input,0,96);
    if(!root||root[0]!='/'||!end||input[0]!='/'||!input[1]||!empty(end,96-unsigned(end-input)))return false;
    for(const char *p=input;*p;++p){
        if((unsigned char)*p<32||*p=='\\')return false;
        if(*p=='/'&&(!p[1]||p[1]=='/'||(p[1]=='.'&&(!p[2]||p[2]=='/'||(p[2]=='.'&&(!p[3]||p[3]=='/'))))))return false;
    }
    size_t a=strlen(root),b=size_t(end-input);if(a+b>=224)return false;
    memcpy(out,root,a);memcpy(out+a,input,b+1);return true;
}
bool Ap01AppFiles0041::writes(uint32_t generation,bool allow){
    if(lock.test_and_set(std::memory_order_acquire))return false;
    Unlock unlock{lock};if(failed||!generation||generation!=gate.current())return false;
    if(allow){Ap01AppLease0041 lease(gate,generation);if(!lease)return false;}
    writableGeneration=allow?generation:0;return true;
}
bool Ap01AppFiles0041::drain(){
    if(lock.test_and_set(std::memory_order_acquire))return false;
    Unlock unlock{lock};if(failed||!gate.drained())return false;
    writableGeneration=0;
    for(auto &slot:slots)if(slot.fd>=0){
        if(!io.close||io.close(io.context,slot.fd)){failed=true;return false;}
        slot={};
    }
    return true;
}
int32_t Ap01AppFiles0041::invoke(void *p,uint32_t generation,uint32_t service,uint32_t operation,
        const void *input,uint32_t length,void *output,uint32_t capacity,uint32_t *written){
    if(!written)return AP01_SERVICE_INVALID;
    *written=0;
    if(!p||service!=AP01_APP_SERVICE_FILE||!input||length<sizeof(ap01_app_file_request_v2)||
       (capacity&&!output))return AP01_SERVICE_INVALID;
    auto &self=*(Ap01AppFiles0041 *)p;
    Ap01AppLease0041 lease(self.gate,generation);if(!lease)return AP01_SERVICE_UNAVAILABLE;
    if(self.lock.test_and_set(std::memory_order_acquire))return AP01_FILE_BUSY;
    Unlock unlock{self.lock};if(self.failed)return AP01_SERVICE_UNAVAILABLE;
    for(const auto &slot:self.slots)if(slot.fd>=0&&slot.generation!=generation)return AP01_SERVICE_UNAVAILABLE;
    ap01_app_file_request_v2 r;memcpy(&r,input,sizeof(r));
    if(uint64_t(length)!=sizeof(r)+uint64_t(operation==AP01_FILE_WRITE?r.argument:0)||
       (operation==AP01_FILE_WRITE&&r.argument>AP01_APP_FILE_CHUNK))return AP01_SERVICE_INVALID;
    bool pathOperation=operation==AP01_FILE_OPEN||(operation>=AP01_FILE_EXISTS&&operation<=AP01_FILE_RENAME);
    char path[224],destination[224];
    if(pathOperation){if(r.handle||!self.path(r.path,path))return AP01_SERVICE_INVALID;}
    else if(!empty(r.path,sizeof(r.path)))return AP01_SERVICE_INVALID;
    if(operation==AP01_FILE_RENAME){if(!self.path(r.destination,destination))return AP01_SERVICE_INVALID;}
    else if(!empty(r.destination,sizeof(r.destination)))return AP01_SERVICE_INVALID;
    if(operation!=AP01_FILE_SEEK&&(r.offset||r.origin))return AP01_SERVICE_INVALID;
    if(operation!=AP01_FILE_WRITE&&operation!=AP01_FILE_OPEN&&r.argument)return AP01_SERVICE_INVALID;
    if(operation==AP01_FILE_OPEN&&r.argument>2)return AP01_SERVICE_INVALID;
    bool mutating=(operation==AP01_FILE_OPEN&&r.argument)||operation==AP01_FILE_WRITE||operation==AP01_FILE_MKDIR||operation==AP01_FILE_REMOVE||operation==AP01_FILE_RENAME;
    if(mutating&&self.writableGeneration!=generation)return AP01_FILE_READ_ONLY;
    auto &io=self.io;
    bool word=operation==AP01_FILE_OPEN||operation==AP01_FILE_WRITE||operation==AP01_FILE_SEEK||operation==AP01_FILE_SIZE||operation==AP01_FILE_EXISTS;
    unsigned expected=word?4:operation==AP01_FILE_CAPACITY?16:0;
    if(operation==AP01_FILE_READ){if(!capacity||capacity>AP01_APP_FILE_CHUNK)return AP01_SERVICE_INVALID;}
    else if(capacity!=expected)return AP01_SERVICE_INVALID;
    Slot *slot=nullptr;
    if(operation>=AP01_FILE_CLOSE&&operation<=AP01_FILE_SIZE){
        for(auto &candidate:self.slots)if(candidate.handle==r.handle&&candidate.fd>=0&&candidate.generation==generation)slot=&candidate;
        if(!slot)return AP01_SERVICE_INVALID;
    }else if(!pathOperation&&r.handle)return AP01_SERVICE_INVALID;
    int32_t result=-1;
    switch(operation){
    case AP01_FILE_OPEN:{
        if(!io.open||!io.close||self.nextHandle>INT32_MAX)return AP01_FILE_LIMIT;
        for(auto &candidate:self.slots)if(candidate.fd<0){slot=&candidate;break;}
        if(!slot)return AP01_FILE_LIMIT;
        int fd=io.open(io.context,path,r.argument);if(fd<0)return AP01_SERVICE_IO;
        *slot={self.nextHandle++,generation,fd,r.argument!=0};result=slot->handle;break;}
    case AP01_FILE_CLOSE:
        if(!io.close||io.close(io.context,slot->fd)){self.failed=true;return AP01_SERVICE_IO;}
        *slot={};return AP01_SERVICE_OK;
    case AP01_FILE_READ:
        result=io.read?io.read(io.context,slot->fd,output,capacity):-1;
        if(result<0||uint32_t(result)>capacity)return AP01_SERVICE_IO;
        *written=uint32_t(result);return AP01_SERVICE_OK;
    case AP01_FILE_WRITE:
        if(!slot->writable)return AP01_FILE_READ_ONLY;
        result=io.write?io.write(io.context,slot->fd,(const uint8_t *)input+sizeof(r),r.argument):-1;
        if(result<0||uint32_t(result)!=r.argument)return AP01_SERVICE_IO;
        break;
    case AP01_FILE_SEEK:
        if(r.origin>2)return AP01_SERVICE_INVALID;
        result=io.seek?io.seek(io.context,slot->fd,r.offset,r.origin):-1;break;
    case AP01_FILE_SIZE:result=io.size?io.size(io.context,slot->fd):-1;break;
    case AP01_FILE_EXISTS:result=io.exists?io.exists(io.context,path):-1;break;
    case AP01_FILE_MKDIR:result=io.mkdir?io.mkdir(io.context,path):-1;break;
    case AP01_FILE_REMOVE:result=io.remove?io.remove(io.context,path):-1;break;
    case AP01_FILE_RENAME:result=io.rename?io.rename(io.context,path,destination):-1;break;
    case AP01_FILE_CAPACITY:{
        uint64_t sizes[2]={};if(!io.statfs||io.statfs(io.context,self.root,&sizes[0],&sizes[1])||sizes[1]>sizes[0])return AP01_SERVICE_IO;
        memcpy(output,sizes,16);*written=16;return AP01_SERVICE_OK;}
    default:return AP01_SERVICE_INVALID;
    }
    if(result<0)return AP01_SERVICE_IO;
    if(word){uint32_t value=uint32_t(result);memcpy(output,&value,4);*written=4;}
    return AP01_SERVICE_OK;
}
