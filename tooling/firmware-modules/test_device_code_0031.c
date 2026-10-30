/* Actual persistent-code core; fault injection models the durable namespace,
 * including a rename whose caller sees an error after it already committed. */
#include "device_code_0031.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct { unsigned char bytes[16]; int length, error; } File;
typedef struct {
    File final, pending;
    uint32_t random_value;
    unsigned random_calls, writes, renames;
    int random_fail, write_fault, rename_fault, read_after_rename;
} Store;
static File *file(Store *s,const char *path)
{
    if(!strcmp(path,"/data/ap01_0031.device_code"))return &s->final;
    assert(!strcmp(path,"/data/ap01_0031.device_code.new"));return &s->pending;
}
static int read_record(void *p,const char *path,unsigned char out[16])
{
    Store *s=p;File *f=file(s,path);
    if(f==&s->final && s->renames && s->read_after_rename)return -5;
    if(f->error)return f->error;
    if(!f->length)return -2;
    if(f->length!=16)return -22;
    memcpy(out,f->bytes,16);return 0;
}
static int write_record(void *p,const char *path,const unsigned char in[16])
{
    Store *s=p;File *f=file(s,path);assert(f==&s->pending);++s->writes;
    f->error=0;f->length=s->write_fault==1?7:16;
    memcpy(f->bytes,in,(size_t)f->length);
    if(s->write_fault==3)f->bytes[5]^=1;
    return s->write_fault==1 || s->write_fault==2 ? -5 : 0;
}
static int replace_record(void *p,const char *from,const char *to)
{
    Store *s=p;assert(file(s,from)==&s->pending && file(s,to)==&s->final);
    ++s->renames;
    if(s->rename_fault==1)return -5;
    s->final=s->pending;memset(&s->pending,0,sizeof(s->pending));
    return s->rename_fault==2?-5:0;
}
static int random_word(void *p,unsigned char out[4])
{
    Store *s=p;++s->random_calls;if(s->random_fail)return 0;
    for(unsigned i=0;i<4;i++)out[i]=(unsigned char)(s->random_value>>(8*i));
    return 1;
}
static ap01_code_io_0031 io(Store *s)
{
    ap01_code_io_0031 result={s,read_record,write_record,replace_record,random_word};
    return result;
}
static int load(Store *s,char out[9])
{ ap01_code_io_0031 ops=io(s);return ap01_code_load_0031(&ops,out); }
static int ensure(Store *s,char out[9])
{ ap01_code_io_0031 ops=io(s);return ap01_code_ensure_0031(&ops,out); }
static int regenerate(Store *s,char out[9])
{ ap01_code_io_0031 ops=io(s);return ap01_code_regenerate_0031(&ops,out); }
static Store initialized(void)
{
    Store s={0};char code[9];s.random_value=12345678;
    assert(!ensure(&s,code) && !strcmp(code,"12345678"));return s;
}
static int authorize(Store *s,ap01_code_gate_0031 *gate,const char *token,uint64_t now)
{
    char current[9];int result=load(s,current);
    return ap01_code_auth_0031(gate,result?NULL:current,token,token?strlen(token):0,now);
}
int main(void)
{
    Store s={0};char code[9]="stale",old[9];
    assert(load(&s,code)==-2 && !code[0] && !s.random_calls);
    s.random_value=12345678;
    assert(!ensure(&s,code) && !strcmp(code,"12345678"));
    assert(s.random_calls==1 && s.writes==1 && s.renames==1 && !s.pending.length);
    /* Golden record CRC is independently calculated with zlib.crc32. */
    const unsigned char golden[16]={'D','V','C','1','1','2','3','4','5','6','7','8',
                                   0x73,0x30,0xbe,0x6b};
    assert(!memcmp(s.final.bytes,golden,16));
    unsigned calls=s.random_calls;s.random_fail=1;
    assert(!ensure(&s,code) && !strcmp(code,"12345678") && s.random_calls==calls);
    /* A new process has only these durable bytes, not any cached code. */
    Store reboot={0};reboot.final=s.final;reboot.random_fail=1;
    assert(!ensure(&reboot,code) && !strcmp(code,"12345678") && !reboot.random_calls);
    Store other={0};other.random_value=87654321;
    assert(!ensure(&other,code) && !strcmp(code,"87654321"));
    assert(memcmp(other.final.bytes,s.final.bytes,16));
    s.random_fail=0;s.random_value=42;memcpy(old,"12345678",9);
    assert(!regenerate(&s,code) && !strcmp(code,"00000042") && strcmp(code,old));
    assert(!load(&s,code) && !strcmp(code,"00000042"));

    /* Every record byte is integrity checked; never generate over corruption
     * implicitly. Explicit local regeneration is the repair operation. */
    Store good=initialized();
    for(unsigned i=0;i<16;i++){
        s=good;s.final.bytes[i]^=1;calls=s.random_calls;
        assert(ensure(&s,code)==-22 && !code[0] && s.random_calls==calls);
    }
    s=good;s.final.bytes[0]^=1;s.random_value=99;
    assert(!regenerate(&s,code) && !strcmp(code,"00000099"));
    s=good;s.final.error=-5;calls=s.random_calls;
    assert(ensure(&s,code)==-5 && !code[0]);
    assert(regenerate(&s,code)==-5 && !code[0] && s.random_calls==calls);
    s=(Store){0};s.pending.error=-5;
    assert(ensure(&s,code)==-5 && !s.random_calls && !code[0]);
    s=(Store){0};s.random_fail=1;
    assert(ensure(&s,code)==-11 && !s.writes && !s.renames && !code[0]);

    /* Rejection sampling is bounded and does not silently accept biased words
     * or reuse the old code. No partial credential is committed. */
    s=(Store){0};s.random_value=4200000000u;
    assert(ensure(&s,code)==-11 && s.random_calls==32 && !s.writes);
    s=(Store){0};s.random_value=4199999999u;
    assert(!ensure(&s,code) && !strcmp(code,"99999999"));
    s=good;calls=s.random_calls;
    assert(regenerate(&s,code)==-11 && s.random_calls==calls+32 && s.writes==good.writes);
    assert(!load(&s,code) && !strcmp(code,"12345678"));

    /* Complete first-generation temporary data is recovered, not replaced.
     * Torn temporary data needs an explicit local regeneration. */
    s=(Store){0};s.pending=good.final;s.random_fail=1;
    assert(!ensure(&s,code) && !strcmp(code,"12345678") && !s.random_calls);
    s=(Store){0};s.pending=good.final;s.pending.length=7;s.random_value=88;
    assert(ensure(&s,code)==-22 && !s.random_calls && !s.renames);
    assert(!regenerate(&s,code) && !strcmp(code,"00000088"));
    s=good;s.pending=other.final;s.random_fail=1;calls=s.renames;
    assert(!ensure(&s,code) && !strcmp(code,"12345678") && s.renames==calls);

    for(int fault=1;fault<=3;fault++){
        s=good;s.random_value=777;s.write_fault=fault;calls=s.renames;
        assert(regenerate(&s,code)==-5 && !code[0] && s.renames==calls);
        assert(!load(&s,code) && !strcmp(code,"12345678"));
    }
    /* A full write reported failed before rename can be recovered on first
     * generation. For rotation, the existing committed code always wins. */
    s=(Store){0};s.random_value=777;s.write_fault=2;
    assert(ensure(&s,code)==-5 && !s.final.length && s.pending.length==16);
    s.write_fault=0;s.random_fail=1;calls=s.random_calls;
    assert(!ensure(&s,code) && !strcmp(code,"00000777") && s.random_calls==calls);
    s=good;s.random_value=888;s.rename_fault=1;
    assert(regenerate(&s,code)==-5 && !code[0]);
    s.rename_fault=0;s.random_fail=1;calls=s.renames;
    assert(!ensure(&s,code) && !strcmp(code,"12345678") && s.renames==calls);
    s=(Store){0};s.random_value=888;s.rename_fault=1;
    assert(ensure(&s,code)==-115 && !code[0]);
    s.rename_fault=0;s.random_fail=1;
    assert(!ensure(&s,code) && !strcmp(code,"00000888"));
    s=good;s.random_value=999;s.rename_fault=2;
    assert(!regenerate(&s,code) && !strcmp(code,"00000999"));
    s=good;s.random_value=999;s.read_after_rename=1;
    /* Allow the pre-rotation load; fault only the post-rename readback. */
    s.renames=0;
    assert(regenerate(&s,code)==-115 && !code[0]);
    s.read_after_rename=0;
    assert(!load(&s,code) && !strcmp(code,"00000999"));

    ap01_code_gate_0031 gate={0};s=good;
    assert(authorize(&s,&gate,"12345678",100)==AP01_CODE_OK);
    assert(authorize(&s,&gate,NULL,100)==AP01_CODE_DENIED);
    assert(authorize(&s,&gate,"0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",100)==AP01_CODE_DENIED);
    assert(authorize(&s,&gate,"00000000",100)==AP01_CODE_DENIED);
    assert(authorize(&s,&gate,"12345678",100)==AP01_CODE_OK && !gate.failures);
    /* One gate models all four worker tasks: the fifth failure locks every
     * subsequent request, including one with the valid current credential. */
    for(unsigned worker=0;worker<5;worker++)
        assert(authorize(&s,&gate,"00000000",100)==AP01_CODE_DENIED);
    assert(gate.retry_at==30100);
    assert(authorize(&s,&gate,"12345678",30099)==AP01_CODE_LIMITED);
    assert(authorize(&s,&gate,"12345678",30100)==AP01_CODE_OK && !gate.failures && !gate.retry_at);
    s.random_value=42;assert(!regenerate(&s,code));
    assert(authorize(&s,&gate,"12345678",30100)==AP01_CODE_DENIED);
    assert(authorize(&s,&gate,"00000042",30100)==AP01_CODE_OK);
    reboot=(Store){0};reboot.final=s.final;gate=(ap01_code_gate_0031){0};
    assert(authorize(&reboot,&gate,"00000042",1)==AP01_CODE_OK);
    s=(Store){0};
    assert(authorize(&s,&gate,"00000042",1)==AP01_CODE_UNAVAILABLE && !s.random_calls);
    s.final=good.final;s.final.bytes[15]^=1;
    assert(authorize(&s,&gate,"12345678",1)==AP01_CODE_UNAVAILABLE);
    s.final=good.final;s.final.error=-5;
    assert(authorize(&s,&gate,"12345678",1)==AP01_CODE_UNAVAILABLE);
    puts("0031 device code: persistence, rotation, power-loss recovery, faults and shared rate gate passed");
    return 0;
}
