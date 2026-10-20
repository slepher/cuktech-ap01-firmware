/* Exercise the actual port journal with a bounded fake native VFS. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
static unsigned char fake_table[596];
static uintptr_t import_function(uintptr_t);
#define OTA_PORT_HOST_TEST 1
#define OTA_TABLE_RAM fake_table
#define FN(addr,type) ((type)import_function(addr))
#include "ota_0031.c"
int diagnostic_console_0031_handle(int fd,diagnostic_console_state *s,const char *(*log)(void *),void *ctx){(void)fd;(void)s;(void)log;(void)ctx;assert(0);return -1;}
int diagnostic_console_0031_own_child(int pid,int parent){(void)pid;(void)parent;assert(0);return 0;}
const unsigned char ota_0031_manifest[256]={0};
const unsigned char ota_0031_reference_header[256]={0};
static char disk[LOG_LIMIT+1];
static unsigned disk_used,position,writes,syncs;
static int exists,err,open_failure,sync_failure,write_budget=-1;
static uint32_t fake_clock(void){return 1000;}
static int *fake_errno(void){return &err;}
static char *fake_getenv(const char *name){assert(!strcmp(name,"ro.boot.update_slot"));return "/dev/fw2";}
static int fake_open(const char *name,int flags,...)
{
    assert(!strcmp(name,LOG_PATH));
    if(open_failure){err=28;return -1;}
    if(!exists&&!(flags&4)){err=2;return -1;}
    exists=1;if(flags&32)disk_used=0;
    position=flags&16?disk_used:0;return 4;
}
static int fake_read(int fd,void *out,size_t n)
{
    assert(fd==4);if(n>disk_used-position)n=disk_used-position;
    memcpy(out,disk+position,n);position+=(unsigned)n;return (int)n;
}
static int fake_write(int fd,const void *data,size_t n)
{
    assert(fd==4);writes++;
    if(write_budget==0){err=5;return -1;}
    if(write_budget>0&&n>(unsigned)write_budget)n=(unsigned)write_budget;
    assert(position+n<=LOG_LIMIT);memcpy(disk+position,data,n);position+=(unsigned)n;
    if(position>disk_used)disk_used=position;
    disk[disk_used]=0;
    if(write_budget>0)write_budget-=(int)n;
    return (int)n;
}
static int fake_seek(int fd,int offset,int whence)
{assert(fd==4&&offset==0&&whence==2);position=disk_used;return (int)position;}
static int fake_sync(int fd){assert(fd==4);syncs++;if(sync_failure){err=5;return -1;}return 0;}
static int fake_close(int fd){assert(fd==4);return 0;}
static int fail_flash_open(flash_io *f,uint32_t n){(void)n;f->fd=-1;return -1;}
static void fake_lock(void){}
static uintptr_t import_function(uintptr_t address)
{
    switch(address){
    case 0xa009b656:return (uintptr_t)fail_flash_open;
    case 0xa01b19e4:case 0xa01b1948:return (uintptr_t)fake_lock;
    case 0xa002fc1a:return (uintptr_t)malloc;
    case 0xa0059c62:return (uintptr_t)fake_clock;
    case 0xa00266c0:return (uintptr_t)fake_errno;
    case 0xa0026d00:return (uintptr_t)fake_getenv;
    case 0xa003f448:return (uintptr_t)fake_open;
    case 0xa003f5f4:return (uintptr_t)fake_read;
    case 0xa0027d94:return (uintptr_t)fake_write;
    case 0xa00280d8:return (uintptr_t)fake_seek;
    case 0xa01b4a0e:return (uintptr_t)fake_sync;
    case 0xa0026788:return (uintptr_t)fake_close;
    default:assert(!"unexpected native import");return 0;
    }
}
static void valid_lines(const char *data,unsigned n)
{
    assert(!n||data[n-1]=='\n');
    unsigned start=0;
    for(unsigned i=0;i<n;i++)if(data[i]=='\n'){
        assert(data[start]=='{'&&i>start&&data[i-1]=='}');start=i+1;
    }
    assert(start==n);
}
int main(void)
{
    server s={0};connection c={0};c.owner=&s;
    memcpy(fake_table,"BFPT",4);fake_table[6]=2;fake_table[8]=7;
    fake_table[16]=16;memcpy(fake_table+19,"Boot2",6);
    fake_table[54]=1;memcpy(fake_table+55,"FW",3);
    load_log(&s);assert(!s.log_used);event(&c,"boot",0);
    assert(exists&&writes&&syncs&&!s.log_errno&&strstr(disk,"\"target_slot\":2"));
    assert(strstr(disk,"\"table_age\":7")&&strstr(disk,"\"table_active\":1"));valid_lines(disk,disk_used);
    fake_table[54]=0;event(&c,"slot_probe",0);assert(strstr(s.log,"\"table_active\":0"));
    fake_table[6]=17;event(&c,"invalid_table",0);assert(strstr(s.log,"\"table_active\":-1,\"table_age\":0"));
    fake_table[6]=2;fake_table[54]=1;
    server reboot={0};load_log(&reboot);assert(reboot.log_used==disk_used&&!strcmp(reboot.log,s.log));
    unsigned previous=disk_used;write_budget=17;event(&c,"readback",0);
    assert(s.log_errno==5&&disk_used==previous+17);
    server torn={0};load_log(&torn);assert(torn.log_used==previous&&torn.log_needs_reset);
    write_budget=-1;c.owner=&torn;event(&c,"boot",0);assert(!torn.log_errno&&!torn.log_needs_reset);
    valid_lines(disk,disk_used);assert(strstr(disk,"\"stage\":\"boot\""));
    for(unsigned i=0;i<120;i++){c.image.position=i*1024;event(&c,"progress",0);}
    assert(torn.log_used<=LOG_LIMIT&&disk_used<=LOG_LIMIT);valid_lines(disk,disk_used);
    valid_lines(torn.log,torn.log_used);assert(!strcmp(disk,torn.log));
    open_failure=1;event(&c,"slot_commit_start",0);assert(torn.log_errno==28);
    previous=writes;assert(strstr(logs(&c),"\"stage\":\"log_status\",\"errno\":28"));assert(writes==previous);
    open_failure=0;sync_failure=1;event(&c,"slot_commit_return",0);assert(torn.log_errno==5);
    sync_failure=0;event(&c,"response_committed",0);assert(!torn.log_errno);
    assert(strstr(logs(&c),"\"stage\":\"log_status\",\"errno\":0"));
    memcpy(disk,"broken\0data\n",12);disk_used=12;
    server corrupt={0};load_log(&corrupt);assert(!corrupt.log_used&&corrupt.log_needs_reset);
    /* A reader causes a bounded busy response before opening a writer.
     * A failed writer open releases both Flash ownership and retry fence. */
    server guarded={0};connection writer={0};writer.owner=&guarded;writer.flash.fd=-1;
    assert(diagnostic_flash_acquire(&guarded.diagnostic));
    assert(begin(&writer,296,1000)==OTA_STORE_BUSY&&!guarded.fenced&&!writer.flash_owned);
    diagnostic_flash_release(&guarded.diagnostic);
    assert(begin(&writer,296,1000)==OTA_STORE_ERROR&&guarded.fenced&&writer.flash_owned);
    abort_store(&writer);assert(!guarded.fenced&&!guarded.diagnostic.flash_busy&&!writer.flash_owned);
    assert(diagnostic_flash_acquire(&guarded.diagnostic));diagnostic_flash_release(&guarded.diagnostic);
    free(c.snapshot);
    puts("{\"passed\":true,\"checks\":9,\"scope\":\"actual port journal; fake native VFS, no physical flash\"}");
    return 0;
}
