/* Native 0031 NSH after authenticated HTTP Upgrade on shared port 18080.
 * Listener is a separate TASK created before the OTA listener/Flash opens.
 * Each shell is another TASK: stdin/stdout/stderr and exit stay in its group.
 * ABI evidence: reverse/reports/ap01/knowledge/0031-network-console.md.
 * Not deployable until native task/FD isolation and release gates pass. */
#include "diagnostic_console.h"
#include <stdint.h>
#include <stddef.h>
#include "diagnostic_platform_0031.h"
#ifndef DIAG_FN
#define DIAG_FN(address,type) ((type)(uintptr_t)(address))
#endif
extern const unsigned char ota_0031_manifest[256] __attribute__((visibility("hidden")));
int snprintf(char *,size_t,const char *,...);
typedef struct {uint16_t family,port;uint32_t addr;unsigned char pad[8];} console_address;
typedef struct {int fd;uint32_t last;uint64_t high;} console_connection;
typedef struct {int32_t fd;uint32_t events,revents;void *priv[3];} console_poll;
#ifndef DIAG_HOST_TEST
_Static_assert(sizeof(console_poll)==24,"0031 poll ABI");
#endif
static void close_socket(int fd){if(fd>=0)DIAG_FN(0xa0026788,int(*)(int))(fd);}
static int timeout(int fd,int option,int seconds)
{
    int32_t tv[2]={seconds,0};
    return DIAG_FN(0xa010b966,int(*)(int,int,int,const void*,unsigned))(fd,1,option,tv,8);
}
static uint64_t milliseconds(void *opaque)
{
    console_connection *c=opaque;uint32_t now=DIAG_FN(0xa0059c62,uint32_t(*)(void))();
    if(now<c->last)c->high+=(uint64_t)1<<32;
    c->last=now;return c->high+now;
}
static int transfer(console_connection *c,void *data,size_t n,uint32_t ms,int output)
{
    if(!ms)return -1;
    uint64_t end=milliseconds(c)+ms;
    for(;;){
        uint64_t now=milliseconds(c);if(now>=end)return -1;
        uint64_t remaining=end-now;
        console_poll p={c->fd,output?4u:1u,0,{NULL,NULL,NULL}};
        int r=DIAG_FN(0xa003f498,int(*)(console_poll*,unsigned,int))(&p,1,remaining>1000?1000:(int)remaining);
        if(p.revents&(8|32))return -1;
        if(r>0&&(p.revents&p.events)){
            r=output?DIAG_FN(0xa00393ee,int(*)(int,const void*,size_t,int,const void*,unsigned))
                        (c->fd,data,n,0x4040,NULL,0):
                     DIAG_FN(0xa010a4a4,int(*)(int,void*,size_t,int))(c->fd,data,n,0x40);
            if(r>=0)return r;
        }else if(p.revents&16)return -1;
        if(r<0){int e=*DIAG_FN(0xa00266c0,int*(*)(void))();if(e!=4&&e!=11)return -1;}
    }
}
static int receive(void *opaque,void *data,size_t n,uint32_t ms)
{return transfer(opaque,data,n,ms,0);}
static int transmit(void *opaque,const void *data,size_t n,uint32_t ms)
{return transfer(opaque,(void*)data,n,ms,1);}
static int respond(console_connection *c,const void *data,size_t size,uint32_t ms)
{
    const unsigned char *p=data;uint64_t end=milliseconds(c)+ms;
    while(size){
        uint64_t now=milliseconds(c);if(now>=end)return -1;
        int n=transmit(c,p,size,(uint32_t)(end-now));
        if(n<=0||(size_t)n>size)return -1;
        p+=n;size-=(size_t)n;
    }
    return 0;
}
static uint32_t word(const unsigned char *p)
{return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static uint32_t crc32(const unsigned char *p,unsigned n)
{
    uint32_t v=0xffffffffu;
    while(n--){v^=*p++;for(unsigned i=0;i<8;i++)v=(v>>1)^(0xedb88320u&(0u-(v&1)));}
    return ~v;
}
static unsigned slot_number(const char *name)
{
    const char *s=DIAG_FN(0xa0026d00,char*(*)(const char*))(name);
    static const char prefix[]="/dev/fw";
    if(!s)return 0;
    for(unsigned i=0;i<7;i++)if(s[i]!=prefix[i])return 0;
    return (s[7]=='1'||s[7]=='2')&&!s[8]?(unsigned)(s[7]-'0'):0;
}
typedef struct {int bytes,error;uint32_t span,entry;unsigned header_crc_ok;} header_info;
static header_info read_header(uint32_t address,unsigned valid)
{
    header_info info={0};unsigned char header[256];
    if(!valid||address>0x1000000u-sizeof(header)){info.error=22;return info;}
    int rc=DIAG_FN(0xa0057eaa,int(*)(uint32_t,void*,uint32_t))(address,header,sizeof(header));
    if(rc){info.error=rc<0?-rc:rc;return info;}
    info.bytes=256;info.span=word(header+0x84);info.entry=word(header+0xb0);
    info.header_crc_ok=crc32(header,252)==word(header+252);
    return info;
}
static void status_reply(console_connection *connection,int active,diagnostic_console_state *state)
{
    int physical_available=diagnostic_flash_acquire(state);
    uint32_t mapping=AP01_FLASH_OFFSET(),reset=AP01_RESET_REASON();
    unsigned char table[596];
#ifndef DIAG_TABLE_RAM
#define DIAG_TABLE_RAM ((const volatile unsigned char *)(uintptr_t)0x62fc8cd8u)
#endif
    const volatile unsigned char *ram=DIAG_TABLE_RAM;
    for(unsigned i=0;i<sizeof(table);i++)table[i]=ram[i];
    unsigned count=(unsigned)table[6]|(unsigned)table[7]<<8;
    unsigned valid=word(table)==0x54504642u&&count>0&&count<=16&&
        crc32(table,12)==word(table+12)&&crc32(table+16,count*36)==word(table+16+count*36);
    const unsigned char *fw=NULL;
    if(valid)for(unsigned i=0;i<count;i++){
        const unsigned char *entry=table+16+i*36;
        if(!entry[0]&&entry[3]=='F'&&entry[4]=='W'&&!entry[5]){fw=entry;break;}
    }
    /* VFS firmware nodes may serialize behind an active writer. Read the
     * headers through the original physical reader instead. */
    header_info first={0},second={0};
    if(physical_available){first=read_header(fw?word(fw+12):0,fw!=NULL);second=read_header(fw?word(fw+16):0,fw!=NULL);}
    else{first.error=16;second.error=16;}
    char build[33];static const char hex[]="0123456789abcdef";
    for(unsigned i=0;i<16;i++){unsigned v=ota_0031_manifest[36+i];build[2*i]=hex[v>>4];build[2*i+1]=hex[v&15];}build[32]=0;
    unsigned char physical[596];unsigned pt_valid[2]={0},pt_age[2]={0},pt_active[2]={0};int pt_rc[2];
    for(unsigned i=0;i<2;i++){
        pt_rc[i]=physical_available?DIAG_FN(0xa0057eaa,int(*)(uint32_t,void*,uint32_t))(0xe000u+i*0x1000u,physical,sizeof(physical)):-16;
        unsigned entries=pt_rc[i]?0:(unsigned)physical[6]|(unsigned)physical[7]<<8;
        if(!pt_rc[i]&&word(physical)==0x54504642u&&entries>0&&entries<=16&&
           crc32(physical,12)==word(physical+12)&&crc32(physical+16,entries*36)==word(physical+16+entries*36)){
            pt_valid[i]=1;pt_age[i]=word(physical+8);
            for(unsigned j=0;j<entries;j++){const unsigned char *e=physical+16+j*36;
                if(!e[0]&&e[3]=='F'&&e[4]=='W'&&!e[5]){pt_active[i]=(unsigned)e[2]+1;break;}}
        }
    }
    if(physical_available)diagnostic_flash_release(state);
    char body[2048];int n=snprintf(body,sizeof(body),
        "{\"protocol\":\"AP01-DIAG/1\",\"build\":\"%s\",\"ms\":%u,\"shell_pid\":%d,\"physical_reads\":\"%s\","
        "\"running\":{\"source\":\"bootrom329\",\"xip_offset\":%u,\"slot\":%u,\"address\":%u},"
        "\"reset\":{\"source\":\"0031.boot_snapshot\",\"native_code\":%u},"
        "\"physical_tables\":[{\"address\":57344,\"read_rc\":%d,\"crc_ok\":%u,\"age\":%u,\"active_slot\":%u},"
        "{\"address\":61440,\"read_rc\":%d,\"crc_ok\":%u,\"age\":%u,\"active_slot\":%u}],"
        "\"current_slot\":%u,\"update_slot\":%u,\"table\":{\"crc_ok\":%u,\"age\":%u,"
        "\"active\":%d,\"image_length\":%u,\"max_length\":[%u,%u],\"address\":[%u,%u]},"
        "\"fw1\":{\"bytes\":%d,\"errno\":%d,\"span\":%u,\"entry\":%u,\"header_crc_ok\":%u},"
        "\"fw2\":{\"bytes\":%d,\"errno\":%d,\"span\":%u,\"entry\":%u,\"header_crc_ok\":%u}}\n",
        build,DIAG_FN(0xa0059c62,uint32_t(*)(void))(),active,physical_available?"attempted":"busy",
        mapping,ap01_running_slot(mapping),ap01_slot_address(ap01_running_slot(mapping)),reset,
        pt_rc[0],pt_valid[0],pt_age[0],pt_active[0],pt_rc[1],pt_valid[1],pt_age[1],pt_active[1],
        slot_number("ro.boot.current_slot"),slot_number("ro.boot.update_slot"),valid,valid?word(table+8):0,
        fw?(int)fw[2]:-1,fw?word(fw+28):0,fw?word(fw+20):0,fw?word(fw+24):0,fw?word(fw+12):0,fw?word(fw+16):0,
        first.bytes,first.error,first.span,first.entry,first.header_crc_ok,
        second.bytes,second.error,second.span,second.entry,second.header_crc_ok);
    if(n>0&&(unsigned)n<sizeof(body))respond(connection,body,(unsigned)n,5000);
}
static void logs_reply(console_connection *connection,const char *data)
{
    if(!data){respond(connection,"ERR logs\n",9,1000);return;}
    unsigned size=0;while(size<8193&&data[size])size++;
    if(size>8192){respond(connection,"ERR logs\n",9,1000);return;}
    char header[32];int n=snprintf(header,sizeof(header),"OK LOGS %u\n",size);
    if(n>0&&(unsigned)n<sizeof(header)&&!respond(connection,header,(unsigned)n,1000))respond(connection,data,size,5000);
}
static void flash_reply(console_connection *connection,const diagnostic_console_io *io,diagnostic_console_state *state)
{
    uint32_t address=0,length=0;
    if(diagnostic_console_flash_range(io,milliseconds(connection)+10000,&address,&length)){
        respond(connection,"ERR range\n",10,1000);return;
    }
    if(!diagnostic_flash_acquire(state)){respond(connection,"ERR busy\n",9,1000);return;}
    unsigned char *data=DIAG_FN(0xa002fc1a,void*(*)(size_t))(length);
    if(!data){diagnostic_flash_release(state);respond(connection,"ERR memory\n",11,1000);return;}
    unsigned read=0;
    while(read<length){
        unsigned count=length-read;if(count>256)count=256;
        /* Original board physical reader, including Boot2 and both tables.
         * The wrapper bounds check is supplemented by the range parser's
         * checked arithmetic. No raw-program/erase imports exist here. */
        if(DIAG_FN(0xa0057eaa,int(*)(uint32_t,void*,uint32_t))(address+read,data+read,count))break;
        read+=count;
    }
    diagnostic_flash_release(state);
    if(read!=length)respond(connection,"ERR read\n",9,1000);
    else{
        char header[64];int n=snprintf(header,sizeof(header),"OK FLASH %u %08x\n",length,crc32(data,length));
        if(n>0&&(unsigned)n<sizeof(header)&&!respond(connection,header,(unsigned)n,1000))respond(connection,data,length,10000);
    }
    DIAG_FN(0xa002e0a0,void(*)(void*))(data);
}
int diagnostic_console_0031_own_child(int pid,int parent_pid)
{
    /* 0031 waitpid ignores options (including WNOHANG) and blocks on a
     * live child. Its no-retained-child-status build removes exited TCBs.
     * Lock scheduling while inspecting the same parent/group fields used
     * by native waitpid, and never signal a PID now owned by another task. */
    DIAG_FN(0xa01b19e4,void(*)(void))();
    const unsigned char *child=DIAG_FN(0xa002651e,void*(*)(int))(pid);
    const unsigned char *group=child?*(const unsigned char*const*)(child+8):NULL;
    int owned=group&&word(group+8)==(unsigned)parent_pid;
    DIAG_FN(0xa01b1948,void(*)(void))();
    return owned;
}
int diagnostic_console_0031_handle(int fd,diagnostic_console_state *state,const char *(*logs)(void *),void *opaque)
{
    console_connection connection={fd,0,0};
    diagnostic_console_io io={&connection,receive,transmit,milliseconds};
    enum diagnostic_operation operation=diagnostic_console_operation(&io,milliseconds(&connection)+10000);
    if(operation==DIAGNOSTIC_INVALID){respond(&connection,"ERR operation\n",14,1000);return -1;}
    DIAG_FN(0xa01b19e4,void(*)(void))();
    int active=state->shell_pid;
    if(active>0&&!diagnostic_console_0031_own_child(active,state->parent_pid))active=-1;
    int busy=active>0&&operation==DIAGNOSTIC_SHELL;
    if(operation==DIAGNOSTIC_SHELL&&!busy){
        const unsigned char *self=*(void *volatile *)(uintptr_t)0x62fc6bf8u;
        active=(int)word(self+12);
    }
    state->shell_pid=active;
    DIAG_FN(0xa01b1948,void(*)(void))();
    if(busy){respond(&connection,"ERR busy\n",9,1000);return -1;}
    if(operation==DIAGNOSTIC_STATUS){status_reply(&connection,active,state);return 0;}
    if(operation==DIAGNOSTIC_LOGS){logs_reply(&connection,logs?logs(opaque):NULL);return 0;}
    if(operation==DIAGNOSTIC_FLASH){flash_reply(&connection,&io,state);return 0;}
    if(operation==DIAGNOSTIC_INTERRUPT||operation==DIAGNOSTIC_CLOSE){
        int r=active>0?DIAG_FN(0xa00520be,int(*)(int,int))(active,operation==DIAGNOSTIC_CLOSE?9:2):-3;
        if(r){char error[48];int n=snprintf(error,sizeof(error),"ERR signal %d\n",r);
            if(n>0&&(unsigned)n<sizeof(error))respond(&connection,error,(unsigned)n,1000);}
        else respond(&connection,"OK SIGNAL\n",10,1000);
        return r;
    }
    if(respond(&connection,"OK SHELL\n",9,1000))return -1;
    void *tcb=*(void *volatile *)(uintptr_t)0x62fc6bf8u;
    for(int target=0;target<3;target++)
        if(DIAG_FN(0xa002828c,int(*)(void*,int,int))(tcb,fd,target)<0)return -1;
    if(fd>2)close_socket(fd);
    if(timeout(0,10,600)||timeout(1,14,5))return -1;
    char *args[]={"sh",NULL};
    return DIAG_FN(0xa0032348,int(*)(int,char**))(1,args);
}
