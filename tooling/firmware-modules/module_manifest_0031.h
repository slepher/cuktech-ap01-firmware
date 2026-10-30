#ifndef AP01_MODULE_MANIFEST_0031_H
#define AP01_MODULE_MANIFEST_0031_H
#include <stdint.h>
#include <stddef.h>
static uint32_t ap01_module_word(const unsigned char *p)
{return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static uint32_t ap01_module_crc(uint32_t crc,const unsigned char *p,size_t n)
{while(n--){crc^=*p++;for(unsigned i=0;i<8;i++)crc=(crc>>1)^(0xedb88320u&(0u-(crc&1)));}return crc;}
/* Shared self-check for linked modules, never an incoming-firmware policy. */
static int ap01_module_valid(const unsigned char *m,const char magic[8],unsigned port,unsigned flags)
{
    if(!m)return 0;
    for(unsigned i=0;i<8;i++)if(m[i]!=(unsigned char)magic[i])return 0;
    uint32_t length=ap01_module_word(m+12),offset=ap01_module_word(m+16);
    uint32_t size=ap01_module_word(m+20),entry=ap01_module_word(m+24);
    if(ap01_module_word(m+8)!=2||length>0x700000u||length<4136||offset<4096||
       offset>length-40||size<=256||size>length-40-offset||
       (flags!=3&&(uintptr_t)m!=0x9ffff000u+offset)||(entry&1)||
       (flags==3?(entry<256||entry>=size):
        (entry<0x9ffff000u+offset+256||entry>=0x9ffff000u+offset+size))||
       ap01_module_word(m+52)!=8192||ap01_module_word(m+56)!=port||
       ap01_module_word(m+60)!=flags||m[128])return 0;
    /* Version 2 contains no authentication material, including old keys. */
    for(unsigned i=64;i<192;i++)if(m[i])return 0;
    if(m[192]){
        const char *menu="AP31MNU1";
        for(unsigned i=0;i<8;i++)if(m[192+i]!=(unsigned char)menu[i])return 0;
        if((flags!=0&&flags!=2)||ap01_module_word(m+200)!=2)return 0;
        for(unsigned i=0;i<2;i++){
            const unsigned char *r=m+204+i*12;
            uint32_t target=ap01_module_word(r+4),base=0x9ffff000u+offset;
            if(ap01_module_word(r)!=(i?0xbe9e6u:0xbe8dau)||
               ap01_module_word(r+8)!=(i?10u:8u)||(target&1)||
               target<base+256||target>=base+size)return 0;
        }
    }else for(unsigned i=192;i<228;i++)if(m[i])return 0;
    for(unsigned i=228;i<256;i++)if(m[i])return 0;
    uint32_t crc=0xffffffffu;
    for(unsigned i=0;i<256;i++){
        unsigned char byte=i>=32&&i<36?0:m[i];crc=ap01_module_crc(crc,&byte,1);
    }
    return ~crc==ap01_module_word(m+32)&&
        ~ap01_module_crc(0xffffffffu,m+256,size-256)==ap01_module_word(m+28);
}
#endif
