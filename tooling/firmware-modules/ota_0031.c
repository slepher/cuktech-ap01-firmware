/* AP01 0031-only independent OTA port. No radio or Boot2 equivalence claim.
 * Every ROM import below was located in the 0031 image itself (REA 6.5.0,
 * RISCV:LE:32:default, base 0x9ffff000): see
 * project-workflow/ap01/knowledge/0031-ota-symbols-20261017.md.
 * Image format: BFNP header CRC at 0xfc, 24-byte recovery tag + BE length +
 * LE CRC at the end. The builder must keep the cloud OTA dispatcher policy
 * explicit; this module never claims the original dispatcher was disabled.
 */
#include "ota_channel.h"
#include "ota_image.h"
#include "diagnostic_console.h"
#include "module_manifest_0031.h"
#include "device_code_0031.h"
#include <stdint.h>
#include <stddef.h>

#ifndef FN
#define FN(addr,type) ((type)(uintptr_t)(addr))
#endif
#ifndef OTA_TABLE_RAM
#define OTA_TABLE_RAM ((const unsigned char *)(uintptr_t)0x62fc8cd8u)
#endif
#define LIMIT_MS 300000u
#define LOG_LIMIT 8192u
#define LOG_PATH "/data/ap01-ota.jsonl"
#ifndef OTA_PORT_HOST_TEST
#include "diagnostic_platform_0031.h"
#endif

extern const unsigned char ota_0031_manifest[256] __attribute__((visibility("hidden")));
int snprintf(char *,size_t,const char *,...);

#ifndef OTA_PORT_HOST_TEST
void *memcpy(void *d,const void *s,size_t n) { unsigned char *p=d;const unsigned char *q=s;while(n--)*p++=*q++;return d; }
void *memset(void *d,int c,size_t n) { unsigned char *p=d;while(n--)*p++=(unsigned char)c;return d; }
int memcmp(const void *a,const void *b,size_t n) { const unsigned char *p=a,*q=b;while(n--){if(*p!=*q)return (int)*p-*q;p++;q++;}return 0; }
size_t strlen(const char *s) { const char *p=s;while(*p)p++;return (size_t)(p-s); }
int strcmp(const char *a,const char *b) { while(*a&&*a==*b){a++;b++;}return (unsigned char)*a-(unsigned char)*b; }
char *strchr(const char *s,int c) { do {if(*s==(char)c)return (char *)s;}while(*s++);return NULL; }
char *strstr(const char *s,const char *n) { if(!*n)return (char *)s;for(;*s;s++){size_t i=0;while(n[i]&&s[i]==n[i])i++;if(!n[i])return (char *)s;}return NULL; }
#endif

typedef struct { int32_t fd,flip; } flash_io;
typedef struct { int32_t fd;uint32_t events,revents;void *priv[3]; } poll_fd;
typedef struct { uint16_t family,port;uint32_t addr;unsigned char pad[8]; } ip_addr;
#ifndef OTA_PORT_HOST_TEST
_Static_assert(sizeof(poll_fd)==24,"0031 poll ABI");
#endif
_Static_assert(sizeof(ip_addr)==16,"0031 IPv4 ABI");
typedef struct {
    int listen_fd,fenced,reboot_returned;
    int workers[4];
    diagnostic_console_state diagnostic;
    uint32_t last_ms;
    uint64_t high_ms;
    ap01_code_gate_0031 auth_gate;
    unsigned log_used;
    int log_errno,log_needs_reset,log_reported_errno;
    char log[LOG_LIMIT+1];
} server;
typedef struct {
    server *owner;
    int fd,started,finished,flash_owned;
    uint32_t last_ms;uint64_t high_ms;
    char *snapshot;
    flash_io flash;
    ota_image image;
    uint32_t progress_mark;
    _Alignas(4) unsigned char scratch[1024];
} connection;
_Static_assert(offsetof(connection,scratch)%4==0,"native Flash buffer word alignment");

static uint32_t le32(const unsigned char *p)
{ return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24; }
static inline int manifest_ok(const unsigned char *m)
#ifdef AP01_RAM_MODULE
{return ap01_module_valid(m,"AP01RAM1",18080,3);}
#else
{return ap01_module_valid(m,"AP01OTA1",18080,0)||ap01_module_valid(m,"AP01HTTP",18080,2);}
#endif
static uint64_t now(void *opaque)
{
    connection *c=opaque;
    uint32_t n=FN(0xa0059c62,uint32_t(*)(void))();
    if(n<c->last_ms)c->high_ms+=(uint64_t)1<<32;
    c->last_ms=n;return c->high_ms+n;
}
static int error_number(void)
{ return *FN(0xa00266c0,int *(*)(void))(); }
/* Native 0031 VFS imports: open/read/write/seek/fsync/close, checked against
 * the original Flash triad. NuttX flags: WRONLY=2, CREAT=4, APPEND=16,
 * TRUNC=32. File writes are best effort; failure remains visible in RAM. */
static void load_log(server *s)
{
    int fd=FN(0xa003f448,int(*)(const char*,int,...))(LOG_PATH,1);
    if(fd<0)return;
    while(s->log_used<LOG_LIMIT){
        int n=FN(0xa003f5f4,int(*)(int,void*,size_t))
            (fd,s->log+s->log_used,LOG_LIMIT-s->log_used);
        if(n<=0)break;
        s->log_used+=(unsigned)n;
    }
    FN(0xa0026788,int(*)(int))(fd);
    /* A torn last line is discarded, never presented as a complete event. */
    unsigned loaded=s->log_used;
    while(s->log_used&&s->log[s->log_used-1]!='\n')s->log_used--;
    s->log_needs_reset=loaded!=s->log_used;
    for(unsigned i=0;i<s->log_used;i++){
        unsigned char ch=(unsigned char)s->log[i];
        if((ch<32&&ch!='\n')||ch>126){s->log_used=0;s->log_needs_reset=1;break;}
    }
    s->log[s->log_used]=0;
}
static void append_log(server *s,const char *line,unsigned n)
{
    FN(0xa01b19e4,void(*)(void))();
    while(s->log_used+n>LOG_LIMIT){
        unsigned drop=0;while(drop<s->log_used&&s->log[drop++]!='\n');
        for(unsigned i=drop;i<s->log_used;i++)s->log[i-drop]=s->log[i];
        s->log_used-=drop;
    }
    memcpy(s->log+s->log_used,line,n);s->log_used+=n;s->log[s->log_used]=0;
    FN(0xa01b1948,void(*)(void))();
}
static void event(connection *c,const char *stage,int rc)
{
    int saved_errno=rc?error_number():0;
    server *s=c->owner;char line[512];
    const char *slot=FN(0xa0026d00,char*(*)(const char*))("ro.boot.update_slot");
    unsigned target=slot&&!strcmp(slot,"/dev/fw1")?1:slot&&!strcmp(slot,"/dev/fw2")?2:0;
    const unsigned char *table=OTA_TABLE_RAM;
    int active=-1;
    unsigned count=(unsigned)table[6]|(unsigned)table[7]<<8;
    if(le32(table)==0x54504642u&&count>0&&count<=16)
        for(unsigned i=0;i<count;i++){
            const unsigned char *entry=table+16+i*36;
            if(!entry[0]&&entry[3]=='F'&&entry[4]=='W'&&!entry[5]){
                if(entry[2]<2)active=entry[2];
                break;
            }
        }
    uint32_t age=active>=0?le32(table+8):0;
    int n=snprintf(line,sizeof(line),
        "{\"version\":\"%s\",\"build_crc\":%u,\"ms\":%u,\"stage\":\"%s\","
        "\"bytes\":%u,\"total\":%u,\"header_span\":%u,\"rc\":%d,\"errno\":%d,"
        "\"target_slot\":%u,\"table_active\":%d,\"table_age\":%u,\"fenced\":%d,\"log_errno\":%d"
#ifndef OTA_PORT_HOST_TEST
        ",\"xip_offset\":%u,\"reset_reason\":%u"
#endif
        "}\n",
        OTA_CHANNEL_VERSION,le32(ota_0031_manifest+28),
        FN(0xa0059c62,uint32_t(*)(void))(),stage,c->image.position,c->image.length,
        c->image.position>=256?le32(c->image.header+0x84):0,rc,saved_errno,
        target,active,age,s->fenced,s->log_errno
#ifndef OTA_PORT_HOST_TEST
        ,AP01_FLASH_OFFSET(),AP01_RESET_REASON()
#endif
        );
    if(n<=0||(unsigned)n>=sizeof(line))return;
    append_log(s,line,(unsigned)n);
    int fd=FN(0xa003f448,int(*)(const char*,int,...))(LOG_PATH,22,0600);
    if(fd<0){s->log_errno=error_number();return;}
    int end=FN(0xa00280d8,int(*)(int,int,int))(fd,0,2);
    const char *data=line;unsigned length=(unsigned)n;
    if(s->log_needs_reset||end<0||(unsigned)end+(unsigned)n>LOG_LIMIT){
        FN(0xa0026788,int(*)(int))(fd);
        fd=FN(0xa003f448,int(*)(const char*,int,...))(LOG_PATH,38,0600);
        if(fd<0){s->log_errno=error_number();return;}
        data=s->log;length=s->log_used;
    }
    unsigned written=0;
    int failure=0;
    while(written<length){
        int count=FN(0xa0027d94,int(*)(int,const void*,size_t))(fd,data+written,length-written);
        if(count<=0){failure=count<0?error_number():5;break;}
        written+=(unsigned)count;
    }
    if(FN(0xa01b4a0e,int(*)(int))(fd))failure=error_number();
    FN(0xa0026788,int(*)(int))(fd);
    s->log_errno=failure;s->log_needs_reset=failure!=0;
}
static const char *logs(void *opaque)
{
    connection *c=opaque;server *s=c->owner;
    if(s->log_errno!=s->log_reported_errno){
        char line[80];int n=snprintf(line,sizeof(line),"{\"stage\":\"log_status\",\"errno\":%d}\n",s->log_errno);
        if(n>0&&(unsigned)n<sizeof(line))append_log(s,line,(unsigned)n);
        s->log_reported_errno=s->log_errno;
    }
    if(!c->snapshot)c->snapshot=FN(0xa002fc1a,void*(*)(size_t))(LOG_LIMIT+1);
    if(!c->snapshot)return NULL;
    FN(0xa01b19e4,void(*)(void))();
    memcpy(c->snapshot,s->log,s->log_used+1);
    FN(0xa01b1948,void(*)(void))();
    return c->snapshot;
}
static int wait_fd(connection *c,unsigned events,uint64_t deadline)
{
    for(;;){
        uint64_t t=now(c);if(t>=deadline)return -1;
        uint64_t left=deadline-t;poll_fd p;memset(&p,0,sizeof(p));p.fd=c->fd;p.events=events;
        int r=FN(0xa003f498,int(*)(poll_fd *,unsigned,int))(&p,1,left>1000?1000:(int)left);
        if(r<0){if(error_number()==4)continue;return -1;}
        if(p.revents&(8|32))return -1;
        if(r>0&&(p.revents&events))return 0;
        if(p.revents&16)return -1;
    }
}
static int transfer(void *opaque,void *buffer,size_t length,uint32_t timeout,int output)
{
    connection *c=opaque;uint64_t deadline=now(c)+timeout;
    while(length){
        if(wait_fd(c,output?4:1,deadline))return -1;
        int n=output?FN(0xa00393ee,int(*)(int,const void*,size_t,int,const void*,unsigned))
                        (c->fd,buffer,length,0x4040,NULL,0):
                     FN(0xa010a4a4,int(*)(int,void*,size_t,int))(c->fd,buffer,length,0x40);
        if(n>=0)return n;
        int e=error_number();if(e!=4&&e!=11)return -1;
    }
    return 0;
}
static int receive(void *p,void *b,size_t n,uint32_t t) { return transfer(p,b,n,t,0); }
static int transmit(void *p,const void *b,size_t n,uint32_t t) { return transfer(p,(void *)b,n,t,1); }
static void close_fd(int fd) { if(fd>=0)FN(0xa0026788,int(*)(int))(fd); }
static int begin(void *opaque,uint32_t length,uint32_t timeout)
{
    connection *c=opaque;
    if(!timeout||c->started||ota_image_begin(&c->image,length))return OTA_STORE_ERROR;
    FN(0xa01b19e4,void(*)(void))();
    int busy=c->owner->fenced;
    if(!busy)busy=!diagnostic_flash_acquire(&c->owner->diagnostic);
    if(!busy){c->owner->fenced=1;c->flash_owned=1;}
    FN(0xa01b1948,void(*)(void))();
    if(busy)return OTA_STORE_BUSY;
    c->started=1;c->flash.fd=-1;c->flash.flip=0;
    event(c,"begin",0);
#ifndef OTA_PORT_HOST_TEST
    const char *target_name=FN(0xa0026d00,char*(*)(const char*))("ro.boot.update_slot");
    unsigned target=target_name&&!strcmp(target_name,"/dev/fw1")?1:target_name&&!strcmp(target_name,"/dev/fw2")?2:0;
    unsigned running=ap01_running_slot(AP01_FLASH_OFFSET());
    if(!running||!target||target==running){event(c,"target_mapping_mismatch",-1);return OTA_STORE_ERROR;}
#endif
    int rc=FN(0xa009b656,int(*)(flash_io*,uint32_t))(&c->flash,length);
    event(c,"flash_open",rc);
    if(rc!=0||c->flash.fd<=0){
        if(c->flash.fd==0){close_fd(0);c->flash.fd=-1;}
        return OTA_STORE_ERROR;
    }
    return OTA_STORE_OK;
}
static int chunk(void *opaque,const void *buffer,size_t bytes,uint32_t timeout)
{
    connection *c=opaque;uint32_t pos=c->image.position;
    if(!timeout||!c->started||c->finished||!bytes||bytes>sizeof(c->scratch)||
       ota_image_chunk(&c->image,buffer,bytes))return OTA_STORE_ERROR;
    /* The original writer mutates its first byte; validation uses input bytes. */
    memcpy(c->scratch,buffer,bytes);
    int rc=FN(0xa009b824,int(*)(flash_io*,uint32_t,void*,uint32_t))
       (&c->flash,pos,c->scratch,(uint32_t)bytes);
    if(rc){event(c,"flash_write",rc);return OTA_STORE_ERROR;}
    if(c->image.position/(1024u*1024u)>c->progress_mark){
        c->progress_mark=c->image.position/(1024u*1024u);event(c,"progress",0);
    }
    return OTA_STORE_OK;
}
static void close_store(connection *c)
{
    if(c->flash.fd>0){
        FN(0xa01ab044,void(*)(flash_io*))(&c->flash);
        c->flash.fd=-1;
    }
    if(c->flash_owned){diagnostic_flash_release(&c->owner->diagnostic);c->flash_owned=0;}
}
static int commit(void *opaque,uint32_t timeout)
{
    connection *c=opaque;uint64_t deadline=now(c)+timeout;
    if(!timeout||!c->started||c->finished)return OTA_STORE_ERROR;
    if(!ota_image_valid(&c->image)){
        event(c,"image_rejected",-1);return OTA_STORE_ERROR;
    }
    event(c,"image_valid",0);
    /* One-shot validation restores byte0 only on real CRC success. */
    c->finished=1;
    int r=FN(0xa009b8da,int(*)(flash_io*,uint32_t,uint32_t))(&c->flash,0,c->image.length);
    event(c,"readback",r);
    if(r)return OTA_STORE_ERROR;
    if(now(c)>=deadline)return OTA_STORE_ERROR;
    event(c,"slot_commit_start",0);
    r=FN(0xa005576c,int(*)(uint32_t,void*))(0xff13,NULL);
    event(c,"slot_commit_return",r);
    if(r!=0)return OTA_STORE_UNKNOWN;
    close_store(c);
    return OTA_STORE_OK;
}
static void abort_store(void *opaque)
{
    connection *c=opaque;
    close_store(c);
    if(c->started&&!c->finished)c->owner->fenced=0;
    /* Once first-byte restoration or commit began, retain the fence even on
     * timeout: a new request must not overwrite a possibly committed image. */
}
static char **environment(void)
{
    const unsigned char *self=*(const unsigned char *volatile *)(uintptr_t)0x62fc6bf8u;
    const unsigned char *group=*(const unsigned char*const*)(self+8);
    return group?*(char**const*)(group+80):NULL;
}
static unsigned pointer_value(const char *s)
{unsigned v=0;for(;*s;s++){if(*s<'0'||*s>'9')return 0;v=v*10+(unsigned)(*s-'0');}return v;}
static int diagnostic(void *opaque)
{connection *c=opaque;return diagnostic_console_0031_handle(c->fd,&c->owner->diagnostic,logs,c);}
/* All four workers share one rate gate; never hold the scheduler lock over
 * filesystem IO. Accepted requests finish with their original authorization;
 * rotation affects subsequent requests, not an already-open diagnostic shell. */
static uint64_t auth_time(server *s)
{
    uint32_t n=FN(0xa0059c62,uint32_t (*)(void))();
    if(n<s->last_ms)s->high_ms+=(uint64_t)1<<32;
    s->last_ms=n;return s->high_ms+n;
}
static enum ota_error authenticate(void *opaque,const char *token,size_t length)
{
    connection *c=opaque;server *s=c->owner;
    FN(0xa01b19e4,void (*)(void))();
    int limited=auth_time(s)<s->auth_gate.retry_at;
    FN(0xa01b1948,void (*)(void))();
    if(limited)return OTA_RATE_LIMITED;
    ap01_code_io_0031 code_io=ap01_code_native_0031();
    char code[9]={0};int loaded=ap01_code_load_0031(&code_io,code);
    FN(0xa01b19e4,void (*)(void))();
    int result=ap01_code_auth_0031(&s->auth_gate,loaded?NULL:code,token,length,auth_time(s));
    FN(0xa01b1948,void (*)(void))();
    memset(code,0,sizeof(code));
    return result==AP01_CODE_OK?OTA_OK:result==AP01_CODE_LIMITED?OTA_RATE_LIMITED:
        result==AP01_CODE_UNAVAILABLE?OTA_AUTH_UNAVAILABLE:OTA_UNAUTHORIZED;
}
static int request_task(int argc,char **argv)
{
    if(argc!=2)return -1;
    connection *input=(connection*)(uintptr_t)pointer_value(argv[1]);if(!input)return -1;
    connection local=*input;FN(0xa002e0a0,void(*)(void*))(input);
    connection *c=&local;server *s=c->owner;
    /* A native TASK clones only the acceptor's descriptors: no sibling OTA
     * Flash handle can leak into a shell or another request. */
    close_fd(s->listen_fd);
    int32_t tv[2]={1,0};
    if(!FN(0xa010b966,int(*)(int,int,int,const void*,unsigned))(c->fd,1,10,tv,8)&&
       !FN(0xa010b966,int(*)(int,int,int,const void*,unsigned))(c->fd,1,14,tv,8)){
        ota_channel_io io={c,receive,transmit,now,begin,chunk,commit,abort_store,logs,diagnostic};
        ota_channel_result result=ota_channel_handle_authenticated(&io,authenticate,now(c)+LIMIT_MS);
        if(result.authenticated_update)event(c,result.committed?"response_committed":"response_rejected",result.error);
        if(c->flash.fd>0)abort_store(c);
        /* Finish the response connection before requesting reset, as in the
         * original receiver. A successful commit still resets if reply fails. */
        close_fd(c->fd);c->fd=-1;
        if(result.committed){
            event(c,"reboot_request",0);
            FN(0xa005576c,int(*)(uint32_t,void*))(0xff04,NULL);
            s->reboot_returned=1;event(c,"reboot_returned",-1);
        }
    }
    close_fd(c->fd);
    if(c->snapshot)FN(0xa002e0a0,void(*)(void*))(c->snapshot);
    return 0;
}
static int serve(int argc,char **argv)
{
    if(argc!=2)return -1;
    server *s=(server*)(uintptr_t)pointer_value(argv[1]);if(!s)return -1;
    s->diagnostic.parent_pid=(int)le32(*(const unsigned char *volatile *)(uintptr_t)0x62fc6bf8u+12);
    for(;;){
        int fd=FN(0xa019f446,int(*)(int,void*,void*))(s->listen_fd,NULL,NULL);
        if(fd<0)continue;
        unsigned slot=4;
        for(unsigned i=0;i<4;i++)if(s->workers[i]<=0||
            !diagnostic_console_0031_own_child(s->workers[i],s->diagnostic.parent_pid)){slot=i;break;}
        if(slot==4){close_fd(fd);continue;}
#ifdef AP01_HTTP_PROBE
        FN(0xa002dd70,int(*)(int,const char*,...))(3,"HTTP_ACCEPT fd=%d slot=%u\n",fd,slot);
#endif
        connection *c=FN(0xa002fc1a,void*(*)(size_t))(sizeof(*c));
        if(!c){close_fd(fd);continue;}
        memset(c,0,sizeof(*c));c->owner=s;c->fd=fd;c->flash.fd=-1;
        char pointer[16];snprintf(pointer,sizeof(pointer),"%u",(unsigned)(uintptr_t)c);char *args[]={pointer,NULL};
        s->workers[slot]=FN(0xa019d362,int(*)(const char*,unsigned,int,unsigned,int(*)(int,char**),char**,char**))
            ("ap01-http-request",0,100,16384,request_task,args,environment());
#ifdef AP01_HTTP_PROBE
        FN(0xa002dd70,int(*)(int,const char*,...))(3,"HTTP_TASK pid=%d\n",s->workers[slot]);
#endif
        if(s->workers[slot]<0)FN(0xa002e0a0,void(*)(void*))(c);
        close_fd(fd);
#ifdef AP01_HTTP_PROBE
        FN(0xa002dd70,int(*)(int,const char*,...))(3,"HTTP_PARENT_CLOSED\n");
#endif
    }
}
int ota_0031_start(void)
{
    server *s=FN(0xa002fc1a,void*(*)(size_t))(sizeof(*s));if(!s)return -1;
    memset(s,0,sizeof(*s));load_log(s);
    /* The original builtin task has a 4 KiB stack. Keep the connection's
     * upload scratch/header off that stack during startup logging. */
    connection *boot=FN(0xa002fc1a,void*(*)(size_t))(sizeof(*boot));
    if(!boot){FN(0xa002e0a0,void(*)(void*))(s);return -1;}
    memset(boot,0,sizeof(*boot));boot->owner=s;event(boot,"boot",0);
    FN(0xa002e0a0,void(*)(void*))(boot);
    s->listen_fd=FN(0xa00267c4,int(*)(int,int,int))(2,1,0);
    if(s->listen_fd<0)goto failed;
    ip_addr address;memset(&address,0,sizeof(address));address.family=2;
    address.port=(uint16_t)((18080u>>8)|(18080u<<8));
    if(FN(0xa003f398,int(*)(int,const void*,unsigned))(s->listen_fd,&address,sizeof(address))||
       FN(0xa019f3ea,int(*)(int))(s->listen_fd))goto failed;
    char pointer[16];snprintf(pointer,sizeof(pointer),"%u",(unsigned)(uintptr_t)s);char *args[]={pointer,NULL};
    int pid=FN(0xa019d362,int(*)(const char*,unsigned,int,unsigned,int(*)(int,char**),char**,char**))
        ("ap01-http",0,100,8192,serve,args,environment());
    if(pid<0)goto failed;
    /* Parent retains its descriptor; request tasks only clone the listener's
     * clean group. The boot caller remains alive until reset. */
    return pid;
failed:
    close_fd(s->listen_fd);FN(0xa002e0a0,void(*)(void*))(s);return -1;
}
#ifndef OTA_PORT_NO_ENTRY
__attribute__((section(".text.entry"),used))
int ota_0031_main(int argc,char **argv)
{
    (void)argc;(void)argv;
    if(!manifest_ok(ota_0031_manifest))return -1;
    int pid=ota_0031_start();if(pid<0)return -1;
    FN(0xa002dd70,int(*)(int,const char*,...))(5,"AP01_HTTP_BOOT listener_pid=%d port=18080\n",pid);
    for(;;)FN(0xa003f498,int(*)(poll_fd*,unsigned,int))(NULL,0,1000);
}
#endif
