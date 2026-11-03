#include "app_core_0041.h"
#include <string.h>
int32_t Ap01AppCore0041::invoke(void *p,uint32_t generation,uint32_t service,uint32_t operation,
        const void *input,uint32_t length,void *output,uint32_t capacity,uint32_t *written){
    if(!written)return AP01_SERVICE_INVALID;
    *written=0;
    if(!p||service!=AP01_APP_SERVICE_CORE||input||length||(!output&&operation!=AP01_CORE_YIELD))return AP01_SERVICE_INVALID;
    auto &self=*(Ap01AppCore0041 *)p;
    Ap01AppLease0041 lease(self.gate,generation);if(!lease)return AP01_SERVICE_UNAVAILABLE;
    if(operation==AP01_CORE_YIELD){
        if(output||capacity)return AP01_SERVICE_INVALID;
        return self.port.yield&&self.port.yield(self.port.context)?AP01_SERVICE_OK:AP01_SERVICE_IO;
    }
    bool okay=false;
    if(operation==AP01_CORE_MONOTONIC_MS||operation==AP01_CORE_UTC_SECONDS){
        if(capacity!=8)return AP01_SERVICE_INVALID;
        auto clock=operation==AP01_CORE_MONOTONIC_MS?self.port.clock:self.port.utc;
        uint64_t now=0;okay=clock&&clock(self.port.context,&now);
        if(okay)memcpy(output,&now,8);
    }else if(operation==AP01_CORE_RANDOM){
        if(!capacity||capacity>256)return AP01_SERVICE_INVALID;
        okay=self.port.random&&self.port.random(self.port.context,(uint8_t *)output,capacity);
    }else if(operation==AP01_CORE_MAC){
        if(capacity!=13)return AP01_SERVICE_INVALID;
        char mac[13]={};okay=self.port.mac&&self.port.mac(self.port.context,mac)&&mac[12]==0;
        for(unsigned i=0;okay&&i<12;++i)okay=(mac[i]>='0'&&mac[i]<='9')||(mac[i]>='A'&&mac[i]<='F')||(mac[i]>='a'&&mac[i]<='f');
        if(okay)memcpy(output,mac,13);
    }else return AP01_SERVICE_INVALID;
    if(!okay){memset(output,0,capacity);return AP01_SERVICE_IO;}
    *written=capacity;return AP01_SERVICE_OK;
}
