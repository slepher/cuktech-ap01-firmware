/* AP01 0031 safety-return prototype for the ota_1 development slot.
 * Role: no HTTP server.
 * Step 1 (boot, inside rcS): call boardctl 0xff13 once. That rewrites the
 *   inactive E000 partition table to active=0 and advances its age, so a power
 *   cycle within the escape window boots the ota_0 fallback.
 * Step 2 (after 9 s, healthy): write the SAME E000 table back with active=1 and
 *   age+1, using the native RAM table writer/CRC leaves that boardctl 0xff13
 *   itself uses (0x62fc168e CRC, 0x62fc1c5e/0x62fc159e table store). active=1
 *   in the FW entry selects address1 (0x7b0000), i.e. ota_1, so the next boot
 *   returns to the development slot.
 * Verification limits: explicit QEMU policy experiment. The RAM leaf layout and
 * behavior were derived by disassembling 0031 boardctl 0xff13; it does not prove
 * physical Boot2, knob-forced boot, or hardware read-only slots.
 */
#include <stdint.h>
#include <stddef.h>

#define FN(addr,type) ((type)(uintptr_t)(addr))
#define TABLE_RAM 0x62fc8cd8u
#define TABLE_TARGET 0xe000u
#define TABLE_BYTES 596u

static void sleep_ms(uint32_t ms)
{
    FN(0xa003f498,int(*)(void*,unsigned,int))(NULL,0,(int)ms);
}

/* Native boardctl 0xff13: pre-arm the inactive E000 table to ota_0. */
static int switch_boot(void)
{
    return FN(0xa005576c,int(*)(uint32_t,void*))(0xff13,NULL);
}

static uint32_t table_crc(const void *buffer, uint32_t length)
{
    return FN(0x62fc168e,uint32_t(*)(const void*,uint32_t))(buffer,length);
}

static int table_store(uint32_t target, const void *buffer, uint32_t length)
{
    return FN(0x62fc159e,int(*)(uint32_t,const void*,uint32_t))(target,buffer,length);
}

/* Write the current 596-byte table back with active=1 and age+1. */
static int lock_back(void)
{
    volatile unsigned char *b = (volatile unsigned char *)TABLE_RAM;
    if (*(volatile uint32_t *)b != 0x54504642u) return -2;
    uint32_t count = *(volatile uint16_t *)(b + 6);
    if (count < 1 || count > 16) return -3;
    uint32_t used = count * 36u + 20u;
    if (used + 16u > TABLE_BYTES) return -4;
    uint32_t age = *(volatile uint32_t *)(b + 8);
    if (age == 0xffffffffu) return -5;
    /* FW entry (first entry) active index: 1 selects Addr1 = 0x7b0000. */
    b[16 + 2] = 1;
    *(volatile uint32_t *)(b + 8) = age + 1u;
    *(volatile uint32_t *)(b + 12) = table_crc((const void *)b, 12u);
    uint32_t entries_crc = table_crc((const void *)(b + 16), count * 36u);
    *(volatile uint32_t *)(b + 16 + count * 36u) = entries_crc;
    /* Same order as boardctl 0xff13: length hint/erase leaf, then 596-byte store. */
    if (FN(0x62fc1c5e,int(*)(uint32_t,uint32_t))(TABLE_TARGET, used) != 0) return -6;
    return table_store(TABLE_TARGET, (const void *)b, TABLE_BYTES);
}

__attribute__((section(".text.entry"),used))
int ota_0031_main(int argc, char **argv)
{
    (void)argc; (void)argv;
    if (switch_boot() != 0) return -1;   /* pre-arm fallback slot */
    sleep_ms(9000);                      /* 1-10 s escape window */
    if (lock_back() != 0) return -1;     /* lock back to the running slot */
    return 0;
}
