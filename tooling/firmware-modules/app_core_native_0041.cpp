#include "app_core_0041.h"
#include "native_io_0041.h"
#include <time.h>
namespace {
bool clock(void *,uint64_t *out){*out=ap01_native0041::nowMs();return true;}
bool random(void *,uint8_t *out,uint32_t n){return ap01_native0041::randomBytes(nullptr,out,n);}
bool mac(void *,char out[13]){char text[13];if(!ap01_native0041::wifiMac(text))return false;for(unsigned i=0;i<13;++i)out[i]=text[i];return true;}
bool yield(void *){ap01_native0041::pause(1);return true;}
bool utc(void *,uint64_t *out){time_t value=time(nullptr);if(value<0)return false;*out=uint64_t(value);return true;}
}
Ap01AppCorePort0041 ap01NativeAppCorePort0041(){return {nullptr,clock,random,mac,yield,utc};}
