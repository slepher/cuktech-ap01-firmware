/* Linux host check at the real XIP address; run with UBSan, not ASan (whose
 * shadow gap includes this address). No device or input image is needed. */
#define _GNU_SOURCE
#include "module_manifest_0031.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static void word(unsigned char *p,uint32_t v)
{ for(unsigned i=0;i<4;i++)p[i]=(unsigned char)(v>>(8*i)); }
static void checksum(unsigned char *m)
{
    word(m+32,0);
    word(m+32,~ap01_module_crc(~0u,m,256));
}
int main(void)
{
    unsigned char *m=mmap((void *)(uintptr_t)0xa067d000,4096,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(m!=(void *)MAP_FAILED && (uintptr_t)m==0xa067d000);
    memcpy(m,"AP01HTTP",8);word(m+8,2);word(m+12,0x67e228);
    word(m+16,0x67e000);word(m+20,512);word(m+24,0xa067d100);
    word(m+28,~ap01_module_crc(~0u,m+256,256));
    word(m+52,8192);word(m+56,18080);word(m+60,2);
    checksum(m);
    assert(ap01_module_valid(m,"AP01HTTP",18080,2)); /* Keyless probe, no menu table. */
    word(m+8,1);memset(m+64,'a',64);checksum(m);
    assert(!ap01_module_valid(m,"AP01HTTP",18080,2)); /* No embedded-key fallback. */
    word(m+8,2);memset(m+64,0,64);checksum(m);
    memcpy(m+192,"AP31MNU1",8);word(m+200,2);
    word(m+204,0xbe8da);word(m+208,0xa067d110);word(m+212,8);
    word(m+216,0xbe9e6);word(m+220,0xa067d120);word(m+224,10);
    checksum(m);assert(ap01_module_valid(m,"AP01HTTP",18080,2));
    const unsigned fields[]={64,127,128,129,191,192,199,200,204,208,212,216,220,224,228,255};
    for(unsigned i=0;i<sizeof(fields)/sizeof(fields[0]);i++){
        unsigned at=fields[i];m[at]^=1;checksum(m);
        assert(!ap01_module_valid(m,"AP01HTTP",18080,2));
        m[at]^=1;checksum(m);
    }
    const uint32_t outside[]={0xa067d000,0xa067d0fe,0xa067d200,0xffffffff};
    for(unsigned i=0;i<sizeof(outside)/sizeof(outside[0]);i++){
        word(m+208,outside[i]);checksum(m);
        assert(!ap01_module_valid(m,"AP01HTTP",18080,2));
    }
    word(m+208,0xa067d110);checksum(m);
    m[300]^=1;assert(!ap01_module_valid(m,"AP01HTTP",18080,2));m[300]^=1;
    m[32]^=1;assert(!ap01_module_valid(m,"AP01HTTP",18080,2));m[32]^=1;
    assert(ap01_module_valid(m,"AP01HTTP",18080,2));
    assert(!munmap(m,4096));
    puts("0031 manifest: keyless v2, embedded key rejection, hooks and CRC checks passed");
    return 0;
}
