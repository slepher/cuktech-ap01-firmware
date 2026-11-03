#pragma once
#include "native_filesystem_0041.h"
#include <assert.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
struct Disk {
    int cut=-1;bool failJournal=false,loseJournalAck=false,failSync=false,loseRename=false,failRemove=false;
    bool package[1024]={};
    static int open(void *p,const char *name,unsigned mode){auto &d=*(Disk *)p;int fd=::open(name,mode?O_WRONLY|O_CREAT|(mode==1?O_TRUNC:O_APPEND):O_RDONLY,0600);if(fd>=0){assert(fd<1024);d.package[fd]=strstr(name,"app-incoming")!=nullptr;}return fd;}
    static int close(void *,int fd){return ::close(fd);}
    static int read(void *,int fd,void *out,size_t n){return ::read(fd,out,n);}
    static int write(void *p,int fd,const void *data,size_t n){auto &d=*(Disk *)p;
        if(!d.package[fd]&&d.failJournal)return -1;
        if(d.package[fd]&&d.cut>=0&&n>unsigned(d.cut))n=d.cut;
        int got=::write(fd,data,n);if(fsync(fd)||(d.failSync&&n))return -1;
        return !d.package[fd]&&d.loseJournalAck?-1:got;
    }
    static int32_t seek(void *,int fd,int32_t at,unsigned origin){return lseek(fd,at,origin);}
    static int32_t size(void *,int fd){struct stat s;return fstat(fd,&s)?-1:s.st_size;}
    static int exists(void *,const char *p){struct stat s;return stat(p,&s)?(errno==ENOENT?0:-1):1;}
    static int remove(void *p,const char *name){return ((Disk *)p)->failRemove?-1:unlink(name);}
    static int rename(void *p,const char *a,const char *b){int r=::rename(a,b);return ((Disk *)p)->loseRename?-1:r;}
    static int capacity(void *,const char *,uint64_t *total,uint64_t *used){*total=4*1024*1024;*used=0;return 0;}
    Ap01VfsOps ops(){Ap01VfsOps o{};o.context=this;o.open=open;o.close=close;o.read=read;o.write=write;o.seek=seek;o.size=size;o.exists=exists;o.remove=remove;o.rename=rename;o.statfs=capacity;return o;}
};
