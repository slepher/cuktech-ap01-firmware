/* Offline-only native TASK / FD / NSH-exit isolation probe. Never deploy. */
#include <stdint.h>
#include <stddef.h>
#define F(a,t) ((t)(uintptr_t)(a))
int snprintf(char *,size_t,const char *,...);
void *memcpy(void *out,const void *in,size_t n)
{unsigned char *p=out;const unsigned char *q=in;while(n--)*p++=*q++;return out;}
void *memset(void *out,int value,size_t n)
{unsigned char *p=out;while(n--)*p++=(unsigned char)value;return out;}
typedef struct {volatile uintptr_t group;volatile int entered;} observation;
static int fail(const char *stage,int code)
{
    F(0xa002dd70,int(*)(int,const char*,...))(6,"DIAG_ISOLATION_FAIL stage=%s rc=%d errno=%d\n",stage,code,*F(0xa00266c0,int*(*)(void))());
    return -1;
}
static uintptr_t number(const char *text)
{uintptr_t n=0;for(;*text;text++){unsigned c=(unsigned char)*text;if(c<'0'||c>'9')return 0;n=n*10+c-'0';}return n;}
static void *current(void){return *(void *volatile *)(uintptr_t)0x62fc6bf8u;}
__attribute__((noinline))
void console_probe_report(unsigned passed,int bytes,unsigned different,unsigned matches)
{
    char report[192];int size=snprintf(report,sizeof(report),
        "DIAG_ISOLATION {\"passed\":%u,\"different_group\":%u,\"file_bytes\":%d,\"native_sh_output\":%u}\n",
        passed,different,bytes,matches);
    F(0xa0027d94,int(*)(int,const void*,size_t))(1,report,(unsigned)size);
    F(0xa002dd70,int(*)(int,const char*,...))(3,"%s",report);
}
static int child(int argc,char **argv)
{
    if(argc!=3)return -1;
    observation *o=(observation*)number(argv[1]);int fd=(int)number(argv[2]);
    if(!o||fd<3)return -1;
    o->group=*(uintptr_t*)((unsigned char*)current()+8);o->entered=1;
    if(F(0xa002828c,int(*)(void*,int,int))(current(),fd,1)!=1)return -1;
    if(F(0xa002828c,int(*)(void*,int,int))(current(),fd,2)!=2)return -1;
    F(0xa0026788,int(*)(int))(fd);
    /* Native nsh_parse tokenizes in place; -c must receive writable RAM. */
    char command[]="echo DIAG_CHILD_OK";
    char *args[]={"sh","-c",command,NULL};
    return F(0xa0032348,int(*)(int,char**))(3,args);
}
__attribute__((section(".text.entry"),used))
int ota_0031_main(int argc,char **argv)
{
    (void)argc;(void)argv;
    uint32_t table_magic=0,image_magic=0;
    int tr=F(0xa0057eaa,int(*)(uint32_t,void*,uint32_t))(0xe000,&table_magic,4);
    int ir=F(0xa0057eaa,int(*)(uint32_t,void*,uint32_t))(0x10000,&image_magic,4);
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_FLASH_READ passed=%u table_rc=%d image_rc=%d\n",!tr&&!ir&&table_magic==0x54504642u&&image_magic==0x504e4642u,tr,ir);
    if(tr||ir||table_magic!=0x54504642u||image_magic!=0x504e4642u)return fail("physical_flash_read",-1);
    observation *o=F(0xa002fc1a,void*(*)(size_t))(sizeof(*o));
    if(!o)return fail("malloc",-1);
    o->group=0;o->entered=0;
    uintptr_t parent=*(uintptr_t*)((unsigned char*)current()+8);
    int fd=F(0xa003f448,int(*)(const char*,int,...))("/data/diag-probe.out",39,0600);
    if(fd<3)return fail("open",fd);
    char pointer[16],descriptor[12];snprintf(pointer,sizeof(pointer),"%u",(unsigned)(uintptr_t)o);
    snprintf(descriptor,sizeof(descriptor),"%d",fd);char *args[]={pointer,descriptor,NULL};
    int pid=F(0xa019d362,int(*)(const char*,unsigned,int,unsigned,int(*)(int,char**),char**,char**))
        ("diag-probe",0,100,8192,child,args,NULL);
    F(0xa0026788,int(*)(int))(fd);
    if(pid<0)return fail("create",pid);
    uint32_t start=F(0xa0059c62,uint32_t(*)(void))();
    int status=0;
    for(;;){
        int waited=F(0xa0053940,int(*)(int,int*,int))(pid,&status,1);
        if(waited==pid)break;
        if(waited<0)return fail("waitpid",waited);
        if(F(0xa0059c62,uint32_t(*)(void))()-start>10000)return fail("child_timeout",pid);
        F(0xa003f498,int(*)(void*,unsigned,int))(NULL,0,10);
    }
    int readfd=F(0xa003f448,int(*)(const char*,int,...))("/data/diag-probe.out",1);
    char data[64]={0};int n=readfd<0?-1:F(0xa003f5f4,int(*)(int,void*,size_t))(readfd,data,sizeof(data)-1);
    if(readfd>=0)F(0xa0026788,int(*)(int))(readfd);
    F(0xa002dd70,int(*)(int,const char*,...))(3,"DIAG_CHILD_CAPTURE [%s]\n",data);
    unsigned matches=n>=13;
    static const char marker[]="DIAG_CHILD_OK";
    for(unsigned i=0;i<13&&matches;i++)if(data[i]!=marker[i])matches=0;
    int passed=o->entered&&o->group&&o->group!=parent&&matches;
    console_probe_report(passed,n,o->group!=parent,matches);
    F(0xa002e0a0,void(*)(void*))(o);
    return passed?0:-1;
}
