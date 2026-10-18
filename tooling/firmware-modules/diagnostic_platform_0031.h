#ifndef AP01_DIAGNOSTIC_PLATFORM_0031_H
#define AP01_DIAGNOSTIC_PLATFORM_0031_H
#include <stdint.h>
/* BootROM table 0x90015800, entry 329: Get_Flash_Image_Offset(group,bank).
 * Report the raw controller value, independently of partition-table/env slots. */
#ifndef AP01_FLASH_OFFSET
#define AP01_FLASH_OFFSET() ((uint32_t(*)(unsigned,unsigned))(uintptr_t) \
    (*(const volatile uint32_t *)(uintptr_t)0x90015d24u))(0,0)
#endif
#ifndef AP01_RESET_REASON
#define AP01_RESET_REASON() (*(const volatile uint32_t *)(uintptr_t)0x62fc5c5cu)
#endif
static inline unsigned ap01_running_slot(uint32_t offset)
{
    if(offset==0x10000u||offset==0x11000u)return 1;
    if(offset==0x7b0000u||offset==0x7b1000u)return 2;
    return 0;
}
static inline uint32_t ap01_slot_address(unsigned slot)
{return slot==1?0x10000u:slot==2?0x7b0000u:0;}
#endif
