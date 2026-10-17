#include "recovery_policy.h"
#if __STDC_HOSTED__
#include <stdio.h>
static volatile uint32_t result[3];
#else
#define result ((volatile uint32_t *)0x20fd0000u)
#endif
static void check(uint32_t yes){result[0]++;if(!yes)result[1]++;}
int recovery_run_tests(void)
{
    recovery_policy s={0,0,0,0};result[0]=result[1]=result[2]=0;
    check(recovery_step(&s,1,1,1000,0,0,0)==RG_SELECT_BASE);
    check(s.phase==RG_NEW); /* no experiment may run until durable readback */
    check(recovery_step(&s,1,0,1001,0,0,0)==RG_RUN_TRIAL);
    check(s.armed_ms==1001);
    check(recovery_step(&s,1,0,2000,0,1,0)==RG_RUN_TRIAL);
    check(recovery_step(&s,1,0,11999,0,1,0)==RG_RUN_TRIAL);
    check(recovery_step(&s,1,0,12000,0,0,0)==RG_RUN_TRIAL);
    check(recovery_step(&s,1,0,12001,0,1,0)==RG_RUN_TRIAL);
    check(recovery_step(&s,1,0,22001,0,1,0)==RG_SELECT_TRIAL);
    check(recovery_step(&s,1,0,22002,0,1,0)==RG_WAIT);
    check(recovery_step(&s,1,1,22003,0,1,0)==RG_RUN_TRIAL);
    check(s.phase==RG_CONFIRMED);
    check(recovery_step(&s,1,1,22004,1,1,0)==RG_SELECT_BASE);
    check(recovery_step(&s,1,0,22005,0,1,0)==RG_REBOOT_BASE);
    check(recovery_step(&s,0,0,0,1,0,1)==RG_BASE);
    s=(recovery_policy){0,0,0,0};
    check(recovery_step(&s,1,1,1000,0,0,1)==RG_FAULT);
    check(recovery_step(&s,1,0,1001,0,0,0)==RG_FAULT);
    s=(recovery_policy){0,0,0,0};
    check(recovery_step(&s,1,0,0xfffffff0u,0,1,0)==RG_RUN_TRIAL);
    check(recovery_step(&s,1,0,0x26ffu,0,1,0)==RG_RUN_TRIAL);
    check(recovery_step(&s,1,0,0x2700u,0,1,0)==RG_SELECT_TRIAL);
    s=(recovery_policy){0,0,0,0};
    check(recovery_step(&s,1,0,0,0,0,0)==RG_RUN_TRIAL);
    check(recovery_step(&s,1,1,1,0,0,0)==RG_FAULT);
    check(recovery_step(0,1,0,0,0,0,0)==RG_FAULT);
    check(recovery_step(&s,2,0,0,0,0,0)==RG_FAULT);
    check(recovery_step(&s,1,2,0,0,0,0)==RG_FAULT);
    check(recovery_step(&s,1,0,0,2,0,0)==RG_FAULT);
    check(recovery_firmware_write_allowed(0,0x7b0000,0x700000));
    check(recovery_firmware_write_allowed(0,0xeaffff,1));
    check(!recovery_firmware_write_allowed(0,0x10000,4096));
    check(!recovery_firmware_write_allowed(1,0x10000,4096));
    check(!recovery_firmware_write_allowed(1,0x7b0000,4096));
    check(!recovery_firmware_write_allowed(0,0xeaffff,2));
    check(!recovery_firmware_write_allowed(0,0x7b0000,0));
    check(!recovery_firmware_write_allowed(0,0xffffffffu,4096));
    check(!recovery_firmware_write_allowed(0,0x7b0000,0xffffffffu));
    result[2]=0x52475031u;
    return (int)result[1];
}
#if __STDC_HOSTED__
int main(void){int r=recovery_run_tests();printf("{\"checks\":%u,\"failures\":%u}\n",result[0],result[1]);return r;}
#endif
