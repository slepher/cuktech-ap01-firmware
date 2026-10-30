/* Small original-XIP bootstrap. Appended bytes are read as physical Flash data,
 * never executed through a presumed extension of the Boot2 XIP mapping. */
#include <stdint.h>
#include <stddef.h>
#include "diagnostic_platform_0031.h"
#define F(a,t) ((t)(uintptr_t)(a))
static uint32_t crc(const unsigned char *p,unsigned n)
{
    uint32_t v=0xffffffffu;
    while(n--){v^=*p++;for(unsigned i=0;i<8;i++)v=(v>>1)^(0xedb88320u&(0u-(v&1)));}
    return ~v;
}
__attribute__((section(".text.entry"),used))
int diagnostic_loader_0031(int argc,char **argv)
{
    uint32_t slot=ap01_running_slot(AP01_FLASH_OFFSET());
    uint32_t address=ap01_slot_address(slot)+0x67e000u;
    uint32_t h[64];
    if(!slot||F(0xa0057eaa,int(*)(uint32_t,void*,uint32_t))(address,h,256))return -1;
    uint32_t size=h[5],entry=h[6],check=h[8];h[8]=0;
    if(h[0]!=0x31305041u||h[1]!=0x314d4152u||h[2]!=2||h[4]!=0x67e000u||
       size<=256||size>65536||entry<256||entry>=size||(entry&1)||crc((void*)h,256)!=check)return -2;
    unsigned char *memory=F(0xa002fc1a,void*(*)(size_t))(size);
    if(!memory)return -3;
    int rc=F(0xa0057eaa,int(*)(uint32_t,void*,uint32_t))(address,memory,size);
    if(!rc&&crc(memory+256,size-256)==h[7]){
        __asm__ volatile("fence.i" ::: "memory");
        F(0xa002dd70,int(*)(int,const char*,...))(3,"AP01_RAM_READY base=%08x bytes=%u entry=%u\n",(unsigned)(uintptr_t)memory,size,entry);
        rc=((int(*)(int,char**))(uintptr_t)(memory+entry))(argc,argv);
    }else rc=-4;
    F(0xa002e0a0,void(*)(void*))(memory);
    return rc;
}
