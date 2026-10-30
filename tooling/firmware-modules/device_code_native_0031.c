/* Original 0031 NuttX/LittleFS only; address evidence in access-menu-0031.md. */
#include "device_code_0031.h"
#ifndef AP01_CODE_FN
#define AP01_CODE_FN(address,type) ((type)(uintptr_t)(address))
#endif
typedef struct {
    const char *path;
    void *node,*peer,*parent;
    const char *relative;
    void *link_buffer;
    unsigned char nofollow,reserved[3];
} Lookup;
#if defined(__riscv)
_Static_assert(sizeof(Lookup)==28,"0031 inode_search_s");
#endif
static int close_file(int fd)
{ return AP01_CODE_FN(0xa0026788,int (*)(int))(fd); }
static int sync_file(int fd)
{
    void *file=NULL;
    int r=AP01_CODE_FN(0xa0025804,int (*)(int,void **))(fd,&file);
    if(r<0)return r;
    r=AP01_CODE_FN(0xa0025888,int (*)(void *))(file);
    AP01_CODE_FN(0xa0027d54,void (*)(void *))(file);
    return r;
}
static int read_record(void *context,const char *path,unsigned char out[16])
{
    (void)context;
    int fd=AP01_CODE_FN(0xa003f448,int (*)(const char *,int,...))(path,1);
    if(fd<0)return *AP01_CODE_FN(0xa00266c0,int *(*)(void))()==2?-2:-5;
    int size=AP01_CODE_FN(0xa00280d8,int (*)(int,int,int))(fd,0,2);
    int result=size<0?-5:size!=16?-22:0;
    if(!result&&AP01_CODE_FN(0xa00280d8,int (*)(int,int,int))(fd,0,0)!=0)result=-5;
    unsigned done=0;
    while(!result&&done<16){
        int n=AP01_CODE_FN(0xa003f5f4,int (*)(int,void *,size_t))(fd,out+done,16-done);
        if(n<=0||(unsigned)n>16-done)result=-5;else done+=(unsigned)n;
    }
    if(!result&&AP01_CODE_FN(0xa00280d8,int (*)(int,int,int))(fd,0,2)!=16)result=-5;
    if(close_file(fd))result=-5;
    return result;
}
static int write_record(void *context,const char *path,const unsigned char bytes[16])
{
    (void)context;
    /* NuttX WRONLY|CREAT|TRUNC, only ever used for the temporary record. */
    int fd=AP01_CODE_FN(0xa003f448,int (*)(const char *,int,...))(path,38,0600);
    if(fd<0)return -5;
    unsigned done=0;int result=0;
    while(done<16){
        int n=AP01_CODE_FN(0xa0027d94,int (*)(int,const void *,size_t))(fd,bytes+done,16-done);
        if(n<=0||(unsigned)n>16-done){result=-5;break;}done+=(unsigned)n;
    }
    if(sync_file(fd))result=-5;
    if(close_file(fd))result=-5;
    return result;
}
static int mount_lookup(Lookup *lookup,const char *path)
{
    memset(lookup,0,sizeof(*lookup));lookup->path=path;lookup->nofollow=1;
    return AP01_CODE_FN(0xa019d862,int (*)(Lookup *))(lookup);
}
static int valid_mount(const Lookup *lookup,int result)
{
    if(result<0||!lookup->node||!lookup->relative)return 0;
    const unsigned char *node=lookup->node;
    uint16_t flags;uintptr_t operations=0;
    memcpy(&flags,node+14,2);memcpy(&operations,node+16,4);
    return (flags&15)==3&&operations==0xa01bb508u;
}
static void release_mount(Lookup *lookup,int result)
{
    if(result>=0&&lookup->node)AP01_CODE_FN(0xa0027b44,void (*)(void *))(lookup->node);
    if(lookup->link_buffer)AP01_CODE_FN(0xa002e0a0,void (*)(void *))(lookup->link_buffer);
}
static int replace_record(void *context,const char *from,const char *to)
{
    (void)context;
    Lookup a,b;int ar=mount_lookup(&a,from),br=mount_lookup(&b,to),result=-5;
    if(valid_mount(&a,ar)&&valid_mount(&b,br)&&a.node==b.node)
        result=AP01_CODE_FN(0xa00487de,int (*)(void *,const char *,const char *))(a.node,a.relative,b.relative);
    release_mount(&b,br);release_mount(&a,ar);return result;
}
static int random_bytes(void *context,unsigned char out[4])
{
    (void)context;
    int fd=AP01_CODE_FN(0xa003f448,int (*)(const char *,int,...))("/dev/urandom",1);
    if(fd<0)return 0;
    unsigned done=0;
    while(done<4){
        int n=AP01_CODE_FN(0xa003f5f4,int (*)(int,void *,size_t))(fd,out+done,4-done);
        if(n<=0||(unsigned)n>4-done)break;
        done+=(unsigned)n;
    }
    int closed=close_file(fd);return done==4&&!closed;
}
ap01_code_io_0031 ap01_code_native_0031(void)
{
    /* Caller-owned table also keeps the RAM experiment position-independent. */
    ap01_code_io_0031 io;
    io.context=NULL;io.read=read_record;io.write=write_record;
    io.replace=replace_record;io.random=random_bytes;
    return io;
}
