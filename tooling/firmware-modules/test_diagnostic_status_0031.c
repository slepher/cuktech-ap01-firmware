/* The actual STATUS formatter, with native reads replaced by frozen inputs. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static unsigned char tables[2][596],ram_table[596];
static uint32_t fake_mapping=0x7b1000,reset_reason=4;
static int read_failure,corrupt_table;
static char output[4096];static unsigned used;
static uintptr_t import_function(uintptr_t);
#define DIAG_FN(a,t) ((t)import_function(a))
#define DIAG_HOST_TEST 1
#define DIAG_TABLE_RAM ram_table
#define AP01_FLASH_OFFSET() fake_mapping
#define AP01_RESET_REASON() reset_reason
#include "diagnostic_console_0031.c"
const unsigned char ota_0031_manifest[256]={0};
static uint32_t clock_ms(void){return 1000;}
static char *environment(const char *name)
{return !strcmp(name,"ro.boot.current_slot")?"/dev/fw1":"/dev/fw2";}
static int physical_read(uint32_t address,void *data,uint32_t size)
{
    if(address==0xe000||address==0xf000){
        if(read_failure)return -5;
        assert(size==596);memcpy(data,tables[address==0xf000],size);
        if(corrupt_table)((unsigned char*)data)[12]^=1;
        return 0;
    }
    assert((address==0x10000||address==0x7b0000)&&size==256);
    unsigned char *p=data;memset(p,0,256);memcpy(p,"BFNP",4);
    uint32_t span=0x6764f0;memcpy(p+0x84,&span,4);uint32_t check=crc32(p,252);memcpy(p+252,&check,4);return 0;
}
static int ready(console_poll *p,unsigned n,int timeout)
{assert(n==1&&timeout>0);p->revents=p->events;return 1;}
static int send_bytes(int fd,const void *data,size_t n,int flags,const void *to,unsigned length)
{(void)flags;(void)to;(void)length;assert(fd==5&&used+n<sizeof(output));memcpy(output+used,data,n);used+=(unsigned)n;output[used]=0;return (int)n;}
static uintptr_t import_function(uintptr_t address)
{
    switch(address){
    case 0xa0057eaa:return (uintptr_t)physical_read;
    case 0xa0059c62:return (uintptr_t)clock_ms;
    case 0xa0026d00:return (uintptr_t)environment;
    case 0xa003f498:return (uintptr_t)ready;
    case 0xa00393ee:return (uintptr_t)send_bytes;
    default:assert(!"unexpected import");return 0;
    }
}
static void store(unsigned char *p,uint32_t v){memcpy(p,&v,4);}
static void init_table(unsigned char *p,uint32_t age,unsigned active)
{
    memset(p,0,596);store(p,0x54504642);p[4]=2;p[6]=1;store(p+8,age);store(p+12,crc32(p,12));
    p[18]=(unsigned char)active;memcpy(p+19,"FW",3);
    store(p+28,0x10000);store(p+32,0x7b0000);store(p+36,0x700000);store(p+40,0x700000);store(p+52,crc32(p+16,36));
}
int main(void)
{
    init_table(tables[0],8,0);init_table(tables[1],9,1);memcpy(ram_table,tables[0],596);
    console_connection c={5,0,0};status_reply(&c,-1);
    assert(strstr(output,"\"current_slot\":1")&&strstr(output,"\"running\":{\"source\":\"bootrom329\",\"xip_offset\":8065024,\"slot\":2"));
    assert(strstr(output,"\"native_code\":4")&&strstr(output,"\"age\":9,\"active_slot\":2"));
    assert(strstr(output,"\"header_crc_ok\":1"));puts(output);
    used=0;corrupt_table=1;status_reply(&c,-1);assert(strstr(output,"\"crc_ok\":0,\"age\":0,\"active_slot\":0"));
    used=0;read_failure=1;status_reply(&c,-1);assert(strstr(output,"\"read_rc\":-5,\"crc_ok\":0"));
    for(unsigned i=0;i<5;i++){uint32_t offsets[]={0x10000,0x11000,0x7b0000,0x7b1000,0x99999};
        fake_mapping=offsets[i];assert(ap01_running_slot(fake_mapping)==(i<2?1:i<4?2:0));}
    puts("{\"passed\":true,\"physical_table_failures\":2,\"mapping_cases\":5,\"env_mismatch_tested\":true}");
    return 0;
}
