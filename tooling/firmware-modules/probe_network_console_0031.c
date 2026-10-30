/* Offline-only probe: real guest TCP loopback, native NSH and FD cloning.
 * Requires --native-loopback; never install this probe on a device. */
#include "diagnostic_console.h"
#include "device_code_0031.h"
#include <stdint.h>
#include <stddef.h>
#define F(a,t) ((t)(uintptr_t)(a))
extern const unsigned char ota_0031_manifest[256] __attribute__((visibility("hidden")));
int snprintf(char *,size_t,const char *,...);
void *memset(void *,int,size_t);
typedef struct {volatile int passed,stage,bytes;} result;
typedef struct {uint16_t family,port;uint32_t addr;unsigned char pad[8];} address;
static char **probe_environment(void)
{
    const unsigned char *self=*(const unsigned char *volatile *)(uintptr_t)0x62fc6bf8u;
    const unsigned char *group=*(const unsigned char*const*)(self+8);
    return group?*(char**const*)(group+80):NULL;
}
static unsigned value(const char *s){unsigned n=0;for(;*s;s++){if(*s<'0'||*s>'9')return 0;n=n*10+(unsigned)(*s-'0');}return n;}
static int same(const char *a,const char *b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static int contains(const char *s,const char *needle)
{for(;*s;s++){unsigned i=0;while(needle[i]&&s[i]==needle[i])i++;if(!needle[i])return 1;}return 0;}
static int write_all(int fd,const char *p,unsigned size)
{while(size){int n=F(0xa0027d94,int(*)(int,const void*,size_t))(fd,p,size);if(n<=0||(unsigned)n>size)return -1;p+=n;size-=(unsigned)n;}return 0;}
static int read_line(int fd,char *out,unsigned cap)
{
    unsigned used=0;
    while(used+1<cap){int n=F(0xa003f5f4,int(*)(int,void*,size_t))(fd,out+used,1);if(n!=1)return -1;
        if(out[used++]=='\n'){out[used]=0;return (int)used;}}
    return -1;
}
static int connect_plain(void)
{
    int fd=F(0xa00267c4,int(*)(int,int,int))(2,1,0);
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_SOCKET fd=%d\n",fd);if(fd<0)return -1;
    int32_t tv[2]={3,0};
    if(F(0xa010b966,int(*)(int,int,int,const void*,unsigned))(fd,1,10,tv,8))goto failed;
    address target={2,(uint16_t)((18080u>>8)|(18080u<<8)),0x0100007f,{0}};
    int connected=F(0xa003f3f0,int(*)(int,const void*,unsigned))(fd,&target,sizeof(target));
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_CONNECTED fd=%d rc=%d\n",fd,connected);
    if(connected)goto failed;
    return fd;
failed:F(0xa0026788,int(*)(int))(fd);return -1;
}
static int connect_authenticated(void)
{
    char code[9];ap01_code_io_0031 io=ap01_code_native_0031();
    if(ap01_code_load_0031(&io,code))return -1;
    int fd=connect_plain();if(fd<0)return -1;
    char line[256];
    int n=snprintf(line,sizeof(line),"GET /diagnostic HTTP/1.1\r\nAuthorization: Bearer %.8s\r\nConnection: Upgrade\r\nUpgrade: ap01-diag/1\r\n\r\n",code);
    if(n<=0||write_all(fd,line,(unsigned)n))goto failed;
    if(read_line(fd,line,sizeof(line))<0||!same(line,"HTTP/1.1 101 Switching Protocols\r\n"))goto failed;
    do{if(read_line(fd,line,sizeof(line))<0)goto failed;}while(!same(line,"\r\n"));
    return fd;
failed:F(0xa0026788,int(*)(int))(fd);return -1;
}
static int http_query(const char *method,const char *path,char *out,unsigned capacity)
{
    char code[9];ap01_code_io_0031 io=ap01_code_native_0031();
    if(ap01_code_load_0031(&io,code))return -1;
    int fd=connect_plain();if(fd<0)return -1;
    char request[256];int n=snprintf(request,sizeof(request),"%s %s HTTP/1.1\r\nAuthorization: Bearer %.8s\r\nContent-Length: 6804520\r\nX-ROM-CRC32: 00000000\r\n\r\n",method,path,code);
    /* GET must not claim an upload body. */
    if(same(method,"GET"))n=snprintf(request,sizeof(request),"GET %s HTTP/1.1\r\nAuthorization: Bearer %.8s\r\n\r\n",path,code);
    if(n<=0||write_all(fd,request,(unsigned)n))return -1;
    unsigned used=0;
    while(used+1<capacity){n=F(0xa003f5f4,int(*)(int,void*,size_t))(fd,out+used,capacity-used-1);if(n<0)return -1;if(!n)break;used+=(unsigned)n;}
    out[used]=0;F(0xa0026788,int(*)(int))(fd);return (int)used;
}
static int pending_upload(void)
{
    char code[9];ap01_code_io_0031 io=ap01_code_native_0031();
    if(ap01_code_load_0031(&io,code))return -1;
    int fd=connect_plain();if(fd<0)return -1;
    char request[256];int n=snprintf(request,sizeof(request),"POST /firmware HTTP/1.1\r\nAuthorization: Bearer %.8s\r\nContent-Length: 6804520\r\nX-ROM-CRC32: 00000000\r\n\r\nBFNP",code);
    if(n<=0||write_all(fd,request,(unsigned)n))return -1;
    return fd;
}
static int control_test(const char *operation,unsigned length,result *r)
{
    r->stage=110;int session=connect_authenticated();if(session<0)return -1;
    char line[128];
    r->stage=111;if(write_all(session,"SHELL\n",6)||read_line(session,line,sizeof(line))<0||!same(line,"OK SHELL\n"))return -1;
    r->stage=112;unsigned used=0;
    while(used<8){int n=F(0xa003f5f4,int(*)(int,void*,size_t))(session,line+used,8-used);if(n<=0)return -1;used+=(unsigned)n;}
    r->stage=113;if(write_all(session,"sleep 30\n",9))return -1;
    /* Control traffic must remain available while the shell is blocked. */
    r->stage=130;F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_CONTROL_CONNECT\n");int query=connect_authenticated();if(query<0)return -1;
    r->stage=131;F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_CONTROL_STATUS\n");char status[1536];
    if(write_all(query,"STATUS\n",7)||read_line(query,status,sizeof(status))<0||
       !contains(status,"\"protocol\":\"AP01-DIAG/1\"")||contains(status,"\"shell_pid\":-1"))return -1;
    F(0xa0026788,int(*)(int))(query);
    r->stage=132;F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_CONTROL_BUSY_CONNECT\n");query=connect_authenticated();if(query<0)return -1;
    r->stage=133;F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_CONTROL_BUSY_QUERY\n");if(write_all(query,"SHELL\n",6)||read_line(query,line,sizeof(line))<0||!same(line,"ERR busy\n"))return -1;
    F(0xa0026788,int(*)(int))(query);
    r->stage=114;int controller=connect_authenticated();if(controller<0)return -1;
    r->stage=115;if(write_all(controller,operation,length)||read_line(controller,line,sizeof(line))<0)return -1;
    if(!same(line,"OK SIGNAL\n")){F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_CONTROL answer=%s",line);return -1;}
    r->stage=116;F(0xa0026788,int(*)(int))(controller);
    while(F(0xa003f5f4,int(*)(int,void*,size_t))(session,line,sizeof(line))>0);
    F(0xa0026788,int(*)(int))(session);return 0;
}
#ifdef AP01_HTTP_UPLOAD_TARGET
extern const uint32_t ap01_probe_upload_length;
extern const unsigned char ap01_probe_upload_tail[];
#endif
#ifdef AP01_HTTP_FULL_UPLOAD
static int upload_read(uint32_t offset,unsigned char *data,unsigned count)
{
#ifdef AP01_HTTP_UPLOAD_TARGET
    if(offset<0x67e000u){
        unsigned prefix=0x67e000u-offset;if(prefix>count)prefix=count;
        if(F(0xa0057eaa,int(*)(uint32_t,void*,uint32_t))(0x10000u+offset,data,prefix))return -1;
        offset+=prefix;data+=prefix;count-=prefix;
    }
    for(unsigned i=0;i<count;i++)data[i]=ap01_probe_upload_tail[offset-0x67e000u+i]^85u;
    return 0;
#else
    return F(0xa0057eaa,int(*)(uint32_t,void*,uint32_t))(0x10000u+offset,data,count);
#endif
}
static int full_upload(void)
{
    char code[9];ap01_code_io_0031 io=ap01_code_native_0031();
    if(ap01_code_load_0031(&io,code))return -1;
    unsigned char image[8192];
    uint32_t length=(uint32_t)ota_0031_manifest[12]|(uint32_t)ota_0031_manifest[13]<<8|
        (uint32_t)ota_0031_manifest[14]<<16|(uint32_t)ota_0031_manifest[15]<<24;
#ifdef AP01_HTTP_UPLOAD_TARGET
    length=ap01_probe_upload_length;
#endif
    uint32_t crc=~0u;
    for(uint32_t offset=0;offset<length;){
        unsigned count=length-offset;if(count>256)count=256;
        if(upload_read(offset,image,count))return -1;
        for(unsigned i=0;i<count;i++){crc^=image[i];for(unsigned bit=0;bit<8;bit++)crc=(crc>>1)^(0xedb88320u&(0u-(crc&1)));}
        offset+=count;
    }
    int fd=connect_plain();if(fd<0)return -1;
    char request[256];int n=snprintf(request,sizeof(request),"POST /firmware HTTP/1.1\r\nAuthorization: Bearer %.8s\r\nContent-Length: %u\r\nX-ROM-CRC32: %08x\r\n\r\n",code,length,~crc);
    if(n<=0||write_all(fd,request,(unsigned)n))return -1;
    for(uint32_t offset=0;offset<length;){
        unsigned count=length-offset;if(count>8192)count=8192;
        for(unsigned read=0;read<count;){unsigned piece=count-read;if(piece>256)piece=256;
            if(upload_read(offset+read,image+read,piece))return -1;
            read+=piece;}
        if(write_all(fd,(const char*)image,count))return -1;
        offset+=count;
        if(!(offset%1048576u))F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_UPLOAD_SENT bytes=%u\n",offset);
    }
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_UPLOAD_SENT bytes=%u\n",length);
    char response[1024];unsigned used=0;
    while(used+1<sizeof(response)){n=F(0xa003f5f4,int(*)(int,void*,size_t))(fd,response+used,sizeof(response)-used-1);if(n<=0)break;used+=(unsigned)n;}
    response[used]=0;F(0xa0026788,int(*)(int))(fd);
    return contains(response,"200 OK")?0:-1;
}
#endif
static int client(int argc,char **argv)
{
    if(argc!=2)return -1;
    result *r=(result*)(uintptr_t)value(argv[1]);if(!r)return -1;
#ifdef AP01_HTTP_RECOVERY_PROBE
    /* Offline fixture calls the actual 0031 recovery helper, not an emulation
     * of its parser. Address independently recovered from pinned stock0031. */
    int recovery=F(0xa0063f00,int(*)(void*,unsigned))(NULL,1);
    r->stage=16;r->passed=recovery==0;
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_RECOVERY {\"result\":%d}\n",recovery);
    /* Stop the bounded fixture after observing success or explicit rejection. */
    F(0xa005576c,int(*)(uint32_t,void*))(0xff04,NULL);
    return recovery;
#endif
    r->stage=20;int upload=pending_upload();if(upload<0)return -1;
    char concurrent[9216];
    r->stage=21;if(http_query("GET","/logs",concurrent,sizeof(concurrent))<0||
        !contains(concurrent,"200 OK")||!contains(concurrent,"flash_open"))return -1;
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_HTTP_LOGS %s\n",concurrent);
    int trace=F(0xa003f448,int(*)(const char*,int,...))("/data/concurrent-http.out",38,0600);
    if(trace>=0){unsigned size=0;while(concurrent[size])size++;write_all(trace,concurrent,size);F(0xa0026788,int(*)(int))(trace);}
    r->stage=22;if(http_query("POST","/firmware",concurrent,sizeof(concurrent))<0||
        !contains(concurrent,"409 Error")){F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_HTTP_BUSY result=%.180s\n",concurrent);return -1;}
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_CONCURRENT_WRITE_BUSY_OK\n");
    r->stage=1;int fd=connect_authenticated();if(fd<0)return -1;
    char line[256];int n;
    if(write_all(fd,"SHELL\n",6))return -1;
    r->stage=5;
    if(read_line(fd,line,sizeof(line))<0||!same(line,"OK SHELL\n"))return -1;
    if(write_all(fd,"echo DIAG_NATIVE_OK\nexit\n",25))return -1;
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_SHELL_ADMITTED\n");
    r->stage=6;
    unsigned char *capture=F(0xa002fc1a,void*(*)(size_t))(8192);if(!capture)return -1;
    unsigned used=0;
    while(used<8192){n=F(0xa003f5f4,int(*)(int,void*,size_t))(fd,capture+used,8192-used);if(n<=0)break;used+=(unsigned)n;}
    F(0xa0026788,int(*)(int))(fd);
    static const char marker[]="DIAG_NATIVE_OK";unsigned found=0;
    for(unsigned i=0;i+sizeof(marker)-1<=used;i++){
        unsigned j=0;while(j<sizeof(marker)-1&&capture[i+j]==(unsigned char)marker[j])j++;
        unsigned prompt=i>=5&&capture[i-5]=='n'&&capture[i-4]=='s'&&capture[i-3]=='h'&&capture[i-2]=='>'&&capture[i-1]==' ';
        unsigned cleared=i>=3&&capture[i-3]==27&&capture[i-2]=='['&&capture[i-1]=='K';
        if(j==sizeof(marker)-1&&(!i||capture[i-1]=='\n'||prompt||cleared)&&
           i+j<used&&(capture[i+j]=='\n'||capture[i+j]=='\r'))found++;
    }
    int file=F(0xa003f448,int(*)(const char*,int,...))("/data/diag-native.out",38,0600);
    if(file>=0){write_all(file,(const char*)capture,used);F(0xa0026788,int(*)(int))(file);}
    r->bytes=(int)used;r->passed=found>=1;r->stage=7;
    F(0xa002e0a0,void(*)(void*))(capture);
    if(!r->passed)return -1;
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_SHELL_OUTPUT_OK\n");
    r->passed=0;r->stage=8;fd=connect_authenticated();if(fd<0)return -1;
    char status[1536];
    if(write_all(fd,"STATUS\n",7)||read_line(fd,status,sizeof(status))<0)return -1;
    F(0xa0026788,int(*)(int))(fd);
    if(!contains(status,"\"protocol\":\"AP01-DIAG/1\"")||!contains(status,"\"physical_reads\":\"busy\"")||!contains(status,"\"crc_ok\":1")||
       !contains(status,"\"source\":\"bootrom329\"")||!contains(status,"\"source\":\"0031.boot_snapshot\"")||!contains(status,"\"physical_tables\":"))return -1;
    for(unsigned i=0;i<12;i++){
        fd=connect_authenticated();if(fd<0)return -1;
        if(write_all(fd,"STATUS\n",7)||read_line(fd,status,sizeof(status))<0)return -1;
        F(0xa0026788,int(*)(int))(fd);
        if(!contains(status,"\"physical_reads\":\"busy\""))return -1;
    }
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_STATUS_BUSY_13_OK\n");
    r->stage=9;fd=connect_authenticated();if(fd<0)return -1;
    if(write_all(fd,"FLASH\n00010000 00000100\n",24)||read_line(fd,line,sizeof(line))<0)return -1;
    if(!same(line,"ERR busy\n"))return -1;
    F(0xa0026788,int(*)(int))(fd);
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_FLASH_BUSY_OK\n");
    /* Busy FLASH has no body; the subsequent LOGS must still be admitted. */
    r->stage=10;fd=connect_authenticated();if(fd<0)return -1;
    if(write_all(fd,"LOGS\n",5)||read_line(fd,line,sizeof(line))<0)return -1;
    if(!contains(line,"OK LOGS ")||read_line(fd,line,sizeof(line))<0||!contains(line,"diagnostic_probe"))return -1;
    F(0xa0026788,int(*)(int))(fd);
    F(0xa0026788,int(*)(int))(upload);upload=-1;
    r->stage=11;if(control_test("INTERRUPT\n",10,r))return -1;
    r->stage=12;if(control_test("CLOSE\n",6,r))return -1;
    if(upload>=0)F(0xa0026788,int(*)(int))(upload);
    r->stage=13;r->passed=1;
#ifdef AP01_HTTP_FULL_UPLOAD
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_NETWORK {\"passed\":1,\"stage\":13,\"bytes\":%d}\n",r->bytes);
    r->stage=14;r->passed=0;
    if(full_upload())return -1;
    r->stage=15;r->passed=1;
#endif
    return 0;
}
__attribute__((section(".text.entry"),used))
int ota_0031_main(int argc,char **argv)
{
    (void)argc;(void)argv;
    result *r=F(0xa002fc1a,void*(*)(size_t))(sizeof(*r));if(!r)return -1;
    r->passed=0;r->stage=0;r->bytes=0;
    int logfile=F(0xa003f448,int(*)(const char*,int,...))("/data/ap01-ota.jsonl",38,0600);
    if(logfile>=0){write_all(logfile,"{\"stage\":\"diagnostic_probe\"}\n",29);F(0xa0026788,int(*)(int))(logfile);}
    int listener=ota_0031_start();
    char pointer[16];snprintf(pointer,sizeof(pointer),"%u",(unsigned)(uintptr_t)r);char *args[]={pointer,NULL};
    int pid=F(0xa019d362,int(*)(const char*,unsigned,int,unsigned,int(*)(int,char**),char**,char**))
        ("diag-client",0,100,24576,client,args,probe_environment());
    if(pid<0)return -1;
    uint32_t start=F(0xa0059c62,uint32_t(*)(void))();int status=0;
    for(;;){
        const unsigned char *self=*(const unsigned char *volatile *)(uintptr_t)0x62fc6bf8u;
        int parent=*(const int*)(self+12);
        if(!diagnostic_console_0031_own_child(pid,parent))break;
        if(F(0xa0059c62,uint32_t(*)(void))()-start>300000)break;
        F(0xa003f498,int(*)(void*,unsigned,int))(NULL,0,10);
    }
    F(0xa002dd70,int(*)(int,const char*,...))(3,
        "DIAG_NETWORK {\"passed\":%d,\"stage\":%d,\"bytes\":%d,\"listener\":%d,\"child_status\":%d}\n",
        r->passed,r->stage,r->bytes,listener,status);
    return r->passed?0:-1;
}
