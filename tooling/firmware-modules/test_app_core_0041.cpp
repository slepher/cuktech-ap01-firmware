#include "app_core_0041.h"
#include <cassert>
#include <cstring>
#include <cstdio>
#include <initializer_list>
struct Port {
    Ap01AppGeneration0041 *gate;unsigned calls=0;bool fail=false,close=false;
    static bool clock(void *p,uint64_t *out){++((Port *)p)->calls;*out=123456789;return true;}
    static bool random(void *p,uint8_t *out,uint32_t n){auto &s=*(Port *)p;++s.calls;memset(out,0xa5,n);
        if(s.close){s.gate->close();assert(!s.gate->drained());}return !s.fail;}
    static bool mac(void *p,char out[13]){++((Port *)p)->calls;memcpy(out,"010203040506",13);return true;}
    static bool yield(void *p){auto &s=*(Port *)p;++s.calls;
        if(s.close){s.gate->close();assert(!s.gate->drained());}return !s.fail;}
};
int main(){
    Ap01AppGeneration0041 gate;Port port{&gate};Ap01AppCore0041 core(gate,{&port,Port::clock,Port::random,Port::mac,Port::yield});
    auto table=core.table(gate.begin());uint8_t out[257]={};uint64_t now=0;char mac[13];
    assert(ap01_app_core_call(&table,AP01_CORE_MONOTONIC_MS,&now,8)==0&&now==123456789);
    assert(ap01_app_core_call(&table,AP01_CORE_MAC,mac,13)==0&&!strcmp(mac,"010203040506"));
    assert(ap01_app_core_call(&table,AP01_CORE_RANDOM,out,256)==0&&out[255]==0xa5);
    unsigned calls=port.calls;
    for(auto op:{0u,99u})assert(ap01_app_core_call(&table,op,out,8)==AP01_SERVICE_INVALID);
    assert(ap01_app_core_call(&table,AP01_CORE_RANDOM,out,257)==AP01_SERVICE_INVALID);
    assert(ap01_app_core_call(&table,AP01_CORE_MONOTONIC_MS,out,7)==AP01_SERVICE_INVALID);
    assert(port.calls==calls);
    assert(ap01_app_core_call(&table,AP01_CORE_YIELD,out,1)==AP01_SERVICE_INVALID);
    assert(ap01_app_core_call(&table,AP01_CORE_YIELD,nullptr,0)==0&&port.calls==calls+1);
    port.fail=true;assert(ap01_app_core_call(&table,AP01_CORE_YIELD,nullptr,0)==AP01_SERVICE_IO);port.fail=false;
    uint32_t written=99;
    assert(table.invoke(table.context,table.generation,1,AP01_CORE_RANDOM,out,1,out,1,&written)==AP01_SERVICE_INVALID&&!written);
    auto bad=table;bad.available_services=0;assert(ap01_app_core_call(&bad,AP01_CORE_RANDOM,out,1)==AP01_SERVICE_UNAVAILABLE);
    port.fail=true;assert(ap01_app_core_call(&table,AP01_CORE_RANDOM,out,256)==AP01_SERVICE_IO);
    for(unsigned i=0;i<256;++i)assert(out[i]==0);
    port.fail=false;port.close=true;assert(ap01_app_core_call(&table,AP01_CORE_RANDOM,out,1)==0&&gate.drained());
    calls=port.calls;assert(ap01_app_core_call(&table,AP01_CORE_RANDOM,out,1)==AP01_SERVICE_UNAVAILABLE&&port.calls==calls);
    auto next=core.table(gate.begin());port.close=false;
    assert(ap01_app_core_call(&table,AP01_CORE_RANDOM,out,1)==AP01_SERVICE_UNAVAILABLE);
    assert(ap01_app_core_call(&next,AP01_CORE_RANDOM,out,1)==0);
    port.close=true;assert(ap01_app_core_call(&next,AP01_CORE_YIELD,nullptr,0)==0&&gate.drained());
    assert(ap01_app_core_call(&next,AP01_CORE_YIELD,nullptr,0)==AP01_SERVICE_UNAVAILABLE);
    puts("core C service: sizes/capabilities, clock/MAC/random, failure zeroing, in-flight close and stale generation rejection passed");
}
