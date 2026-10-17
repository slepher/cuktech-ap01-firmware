#include "recovery_policy.h"

uint32_t recovery_step(recovery_policy *s,uint32_t running,uint32_t selected,
                       uint32_t now,uint32_t button,uint32_t healthy,uint32_t failed)
{
    if(!s||running>1||selected>1||button>1||healthy>1||failed>1)return RG_FAULT;
    if(running==0)return RG_BASE;
    if(failed||s->phase==RG_FAILED){s->phase=RG_FAILED;return RG_FAULT;}
    if(button)s->phase=RG_ESCAPING;
    if(s->phase==RG_ESCAPING)return selected==0?RG_REBOOT_BASE:RG_SELECT_BASE;
    if(s->phase==RG_NEW){
        if(selected!=0)return RG_SELECT_BASE;
        s->armed_ms=now;s->phase=RG_GRACE;
    }
    if(s->phase==RG_GRACE){
        if(selected!=0){s->phase=RG_FAILED;return RG_FAULT;}
        if(!healthy)s->tracking_health=0;
        else if(!s->tracking_health){s->tracking_health=1;s->healthy_since=now;}
        if(healthy&&(uint32_t)(now-s->healthy_since)>=10000u){
            s->phase=RG_CONFIRMING;return RG_SELECT_TRIAL;
        }
        return RG_RUN_TRIAL;
    }
    if(s->phase==RG_CONFIRMING){
        if(selected==1){s->phase=RG_CONFIRMED;return RG_RUN_TRIAL;}
        return RG_WAIT; /* one outstanding commit; never resubmit blindly */
    }
    if(s->phase==RG_CONFIRMED)return selected==1?RG_RUN_TRIAL:RG_FAULT;
    return RG_FAULT;
}

uint32_t recovery_firmware_write_allowed(uint32_t running,uint32_t address,uint32_t length)
{
    return running==0&&length&&address>=0x7b0000u&&
        address<0xeb0000u&&length<=0xeb0000u-address;
}
