#include "diagnostic_console.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static const char key[]="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
typedef struct {char input[160],output[160];size_t pos,size,used,cap;uint64_t now;unsigned tick,reads;int eof;} fixture;
static int read_byte(void *p,void *out,size_t n,uint32_t timeout)
{
    fixture *f=p;assert(n==1&&timeout);f->now+=f->tick;f->reads++;
    if(f->pos==f->size)return f->eof?-1:0;
    *(char*)out=f->input[f->pos++];return 1;
}
static int write_bytes(void *p,const void *bytes,size_t n,uint32_t timeout)
{
    fixture *f=p;assert(timeout);if(n>f->cap)n=f->cap;
    assert(f->used+n<sizeof(f->output));memcpy(f->output+f->used,bytes,n);f->used+=n;return (int)n;
}
static uint64_t now(void *p){return ((fixture*)p)->now;}
static void init(fixture *f,const char *ending)
{memset(f,0,sizeof(*f));f->cap=160;f->size=(size_t)snprintf(f->input,sizeof(f->input),"AUTH %s%s",key,ending);}
static int run(fixture *f)
{diagnostic_console_io io={f,read_byte,write_bytes,now};return diagnostic_console_authenticate(&io,key,1000);}
int main(void)
{
    fixture f;unsigned checks=0;
    init(&f,"\n");assert(!run(&f)&&f.pos==70&&!strstr(f.output,key));checks++;
    init(&f,"\r\n");f.cap=1;assert(!run(&f)&&f.pos==71&&!strcmp(f.output,"AP01-DIAG/1\n"));checks++;
    init(&f,"\necho untouched\n");assert(!run(&f)&&f.pos==70);checks++;
    init(&f,"\n");f.input[5]^=1;assert(run(&f)&&strstr(f.output,"ERR auth")&&!strstr(f.output,key));checks++;
    init(&f,"\n");f.input[0]='a';assert(run(&f));checks++;
    init(&f,"\n");f.size=7;assert(run(&f));checks++;
    init(&f,"\n");f.size=7;f.eof=1;assert(run(&f));checks++;
    init(&f,"\n");f.tick=16;assert(run(&f)&&f.now>=1000&&f.reads<70);checks++;
    init(&f,"\n");memset(f.input,'x',100);f.size=100;assert(run(&f)&&f.reads==71);checks++;
    init(&f,"\n");f.input[5]=0;assert(run(&f));checks++;
    init(&f,"\n");f.input[5]=(char)255;assert(run(&f));checks++;
    init(&f,"\n");f.cap=0;assert(run(&f)&&!f.reads);checks++;
    const char *operations[]={"SHELL\n","STATUS\r\n","INTERRUPT\n","CLOSE\n","LOGS\n","FLASH\n","UNKNOWN\n","SHELL x\n","INTERRUPTXXXX\n"};
    diagnostic_console_io io={&f,read_byte,write_bytes,now};
    for(unsigned i=0;i<9;i++){
        memset(&f,0,sizeof(f));strcpy(f.input,operations[i]);f.size=strlen(f.input);
        assert(diagnostic_console_operation(&io,1000)==(i<6?(enum diagnostic_operation)(i+1):DIAGNOSTIC_INVALID));checks++;
    }
    assert(diagnostic_console_operation(NULL,1000)==DIAGNOSTIC_INVALID);checks++;
    const char *ranges[]={"00000000 00010000\n","00ffffff 00000001\n","01000000 00000001\n", "ffffffff 00000001\n", "00000000 00000000\n", "00000000 00010001\n", "0000x000 00000001\n", "00000000 00000001"};
    for(unsigned i=0;i<8;i++){
        memset(&f,0,sizeof(f));strcpy(f.input,ranges[i]);f.size=strlen(f.input);
        uint32_t address=123,length=456;int r=diagnostic_console_flash_range(&io,1000,&address,&length);
        assert((r==0)==(i<2));if(i>=2)assert(address==123&&length==456);checks++;
    }
    printf("{\"passed\":true,\"checks\":%u,\"commands_executed\":0}\n",checks);return 0;
}
