/* Execute the native adapter with its exact ROM-call boundary mocked. */
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static void *rom(uintptr_t address);
#define AP01_CODE_FN(address,type) ((type)rom(address))
#include "device_code_native_0031.c"

static struct {
    int fd,error,close_error,size,final_size,seek_error;
    int read_step,read_fault,write_step,write_fault,get_error,sync_error;
    unsigned reads,writes,closes,gets,syncs,puts,seeks,position;
    unsigned char input[16],output[16];
    char trace[80];unsigned trace_length;
    int lookup_result[2],null_node[2],null_relative[2],different_mount,rename_result;
    unsigned lookup_calls,rename_calls,node_releases,link_releases;
    unsigned char inode[2][32];
} f;
static void mark(char c)
{ assert(f.trace_length+1<sizeof(f.trace));f.trace[f.trace_length++]=c; }
static void reset(void)
{
    memset(&f,0,sizeof(f));f.fd=7;f.size=f.final_size=16;f.read_step=f.write_step=16;
    for(unsigned i=0;i<16;i++)f.input[i]=(unsigned char)(i+17);
    uint16_t flags=3;uint32_t operations=0xa01bb508;
    for(unsigned i=0;i<2;i++){
        memcpy(f.inode[i]+14,&flags,2);memcpy(f.inode[i]+16,&operations,4);
    }
}
static int open_mock(const char *path,int flags,...)
{
    assert(path && (flags==1 || flags==38));
    if(flags==38){va_list a;va_start(a,flags);assert(va_arg(a,int)==0600);va_end(a);}
    else assert(!strcmp(path,"record") || !strcmp(path,"/dev/urandom"));
    f.position=0;mark('O');return f.fd;
}
static int *errno_mock(void) { return &f.error; }
static int close_mock(int fd)
{ assert(fd==7);++f.closes;mark('C');return f.close_error; }
static int seek_mock(int fd,int offset,int origin)
{
    assert(fd==7 && !offset && (origin==0 || origin==2));++f.seeks;
    if(!origin){mark('Z');f.position=0;return f.seek_error;}
    mark('E');return f.seeks==1?f.size:f.final_size;
}
static int read_mock(int fd,void *out,size_t n)
{
    assert(fd==7 && n && n<=16);++f.reads;mark('R');
    if(f.read_fault){
        if(f.read_fault==1)return 0;
        if(f.read_fault==2)return -1;
        return (int)n+1;
    }
    unsigned count=(unsigned)f.read_step;if(count>n)count=(unsigned)n;
    assert(f.position+count<=sizeof(f.input));
    memcpy(out,f.input+f.position,count);f.position+=count;return (int)count;
}
static int write_mock(int fd,const void *in,size_t n)
{
    assert(fd==7 && n && n<=16);++f.writes;mark('W');
    if(f.write_fault){
        if(f.write_fault==1)return 0;
        if(f.write_fault==2)return -1;
        return (int)n+1;
    }
    unsigned count=(unsigned)f.write_step;if(count>n)count=(unsigned)n;
    assert(f.position+count<=sizeof(f.output));
    memcpy(f.output+f.position,in,count);f.position+=count;return (int)count;
}
static int get_file_mock(int fd,void **out)
{ assert(fd==7);++f.gets;mark('G');if(f.get_error)return f.get_error;*out=f.output;return 0; }
static int sync_mock(void *file)
{ assert(file==f.output);++f.syncs;mark('S');return f.sync_error; }
static void put_file_mock(void *file)
{ assert(file==f.output);++f.puts;mark('U'); }
static int lookup_mock(Lookup *lookup)
{
    unsigned i=f.lookup_calls++;assert(i<2 && lookup->nofollow==1);
    assert(!lookup->node && !lookup->peer && !lookup->parent && !lookup->relative && !lookup->link_buffer);
    for(unsigned j=0;j<3;j++)assert(!lookup->reserved[j]);
    assert(!strcmp(lookup->path,i?"to":"from"));
    lookup->node=f.null_node[i]?NULL:f.inode[i && f.different_mount];
    lookup->relative=f.null_relative[i]?NULL:i?"relative-to":"relative-from";
    lookup->link_buffer=malloc(1);assert(lookup->link_buffer);
    return f.lookup_result[i];
}
static int rename_mock(void *node,const char *from,const char *to)
{
    assert(node==f.inode[0]);assert(!strcmp(from,"relative-from") && !strcmp(to,"relative-to"));
    ++f.rename_calls;return f.rename_result;
}
static void node_release_mock(void *node)
{ assert(node==f.inode[0] || node==f.inode[1]);++f.node_releases; }
static void link_release_mock(void *link)
{ assert(link);++f.link_releases;free(link); }
static void *rom(uintptr_t address)
{
    switch(address){
    case 0xa003f448:return open_mock;
    case 0xa00266c0:return errno_mock;
    case 0xa0026788:return close_mock;
    case 0xa00280d8:return seek_mock;
    case 0xa003f5f4:return read_mock;
    case 0xa0027d94:return write_mock;
    case 0xa0025804:return get_file_mock;
    case 0xa0025888:return sync_mock;
    case 0xa0027d54:return put_file_mock;
    case 0xa019d862:return lookup_mock;
    case 0xa00487de:return rename_mock;
    case 0xa0027b44:return node_release_mock;
    case 0xa002e0a0:return link_release_mock;
    default:assert(!"unexpected ROM call");return NULL;
    }
}
int main(void)
{
    ap01_code_io_0031 ops=ap01_code_native_0031();unsigned char out[18];
    reset();memset(out,0xaa,sizeof(out));f.read_step=3;
    assert(!ops.read(NULL,"record",out+1) && f.reads==6 && f.closes==1);
    assert(!memcmp(out+1,f.input,16) && out[0]==0xaa && out[17]==0xaa);
    assert(f.seeks==3 && f.trace[f.trace_length-1]=='C');
    reset();f.fd=-1;f.error=2;assert(ops.read(NULL,"record",out)==-2 && !f.closes);
    reset();f.fd=-1;f.error=5;assert(ops.read(NULL,"record",out)==-5 && !f.closes);
    const int sizes[]={-1,0,15,17};
    for(unsigned i=0;i<sizeof(sizes)/sizeof(sizes[0]);i++){
        reset();f.size=sizes[i];assert(ops.read(NULL,"record",out)==(sizes[i]<0?-5:-22));
        assert(!f.reads && f.closes==1);
    }
    reset();f.seek_error=-1;assert(ops.read(NULL,"record",out)==-5 && !f.reads && f.closes==1);
    for(int fault=1;fault<=3;fault++){
        reset();f.read_fault=fault;assert(ops.read(NULL,"record",out)==-5 && f.closes==1);
    }
    reset();f.final_size=17;assert(ops.read(NULL,"record",out)==-5 && f.closes==1);
    reset();f.close_error=-1;assert(ops.read(NULL,"record",out)==-5 && f.closes==1);

    reset();f.write_step=3;assert(!ops.write(NULL,"temporary",f.input));
    assert(!memcmp(f.input,f.output,16) && f.writes==6 && f.gets==1 && f.syncs==1 && f.puts==1 && f.closes==1);
    assert(!strcmp(f.trace,"OWWWWWWGSUC"));
    reset();f.fd=-1;assert(ops.write(NULL,"temporary",f.input)==-5 && !f.writes && !f.closes);
    for(int fault=1;fault<=3;fault++){
        reset();f.write_fault=fault;assert(ops.write(NULL,"temporary",f.input)==-5);
        assert(!strcmp(f.trace,"OWGSUC"));
    }
    reset();f.get_error=-5;assert(ops.write(NULL,"temporary",f.input)==-5 && !f.syncs && !f.puts && f.closes==1);
    reset();f.sync_error=-5;assert(ops.write(NULL,"temporary",f.input)==-5 && f.puts==1 && f.closes==1);
    reset();f.close_error=-5;assert(ops.write(NULL,"temporary",f.input)==-5 && f.syncs==1 && f.puts==1);

    reset();f.read_step=1;memset(out,0xaa,sizeof(out));assert(ops.random(NULL,out+1));
    assert(f.reads==4 && f.closes==1 && !f.seeks && out[0]==0xaa && out[5]==0xaa);
    assert(!memcmp(out+1,f.input,4));
    reset();f.fd=-1;assert(!ops.random(NULL,out) && !f.closes);
    for(int fault=1;fault<=3;fault++){
        reset();f.read_fault=fault;assert(!ops.random(NULL,out) && f.closes==1);
    }
    reset();f.close_error=-5;assert(!ops.random(NULL,out) && f.closes==1);

    reset();assert(!ops.replace(NULL,"from","to"));
    assert(f.lookup_calls==2 && f.rename_calls==1 && f.node_releases==2 && f.link_releases==2);
    reset();f.rename_result=-17;assert(ops.replace(NULL,"from","to")==-17);
    assert(f.rename_calls==1 && f.node_releases==2 && f.link_releases==2);
    for(unsigned side=0;side<2;side++){
        reset();f.lookup_result[side]=-5;assert(ops.replace(NULL,"from","to")==-5);
        assert(!f.rename_calls && f.node_releases==1 && f.link_releases==2);
        reset();f.null_node[side]=1;assert(ops.replace(NULL,"from","to")==-5);
        assert(!f.rename_calls && f.node_releases==1 && f.link_releases==2);
        reset();f.null_relative[side]=1;assert(ops.replace(NULL,"from","to")==-5);
        assert(!f.rename_calls && f.node_releases==2 && f.link_releases==2);
    }
    reset();f.different_mount=1;assert(ops.replace(NULL,"from","to")==-5);
    assert(!f.rename_calls && f.node_releases==2 && f.link_releases==2);
    reset();f.inode[0][14]=2;assert(ops.replace(NULL,"from","to")==-5);
    assert(!f.rename_calls && f.node_releases==2 && f.link_releases==2);
    reset();f.inode[0][16]^=1;assert(ops.replace(NULL,"from","to")==-5);
    assert(!f.rename_calls && f.node_releases==2 && f.link_releases==2);
    reset();f.inode[0][14]=0x83;assert(!ops.replace(NULL,"from","to"));
    assert(f.rename_calls==1 && f.node_releases==2 && f.link_releases==2);
    puts("0031 native code adapter: exact/partial IO, sync/close, random and mounted rename cleanup passed");
    return 0;
}
