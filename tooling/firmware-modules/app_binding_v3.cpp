#include "app_binding_v3.h"
int32_t Ap01AppBindingBridgeV3::bind(const Ap01AppBindingV3 &value){
    if(!value.context||!value.principal||!value.pairing||!value.online)return AP01_APP_V3_INVALID;
    if(lock.test_and_set(std::memory_order_acquire))return AP01_APP_V3_PENDING;
    int32_t result=AP01_APP_V3_INVALID;
    if(!ready.load(std::memory_order_acquire)){
        binding=value;ready.store(true,std::memory_order_release);result=AP01_APP_V3_OK;
    }
    lock.clear(std::memory_order_release);return result;
}
int Ap01AppBindingBridgeV3::principal(void *p,const char *token,char out[65]){
    auto &s=*(Ap01AppBindingBridgeV3 *)p;
    return s.ready.load(std::memory_order_acquire)?s.binding.principal(s.binding.context,token,out):0;
}
bool Ap01AppBindingBridgeV3::online(void *p){
    auto &s=*(Ap01AppBindingBridgeV3 *)p;
    return s.ready.load(std::memory_order_acquire)&&s.binding.online(s.binding.context)==1;
}
Ap01HttpReply Ap01AppBindingBridgeV3::pairing(void *p,const Ap01HttpRequest &q,uint64_t now){
    auto &s=*(Ap01AppBindingBridgeV3 *)p;Ap01HttpReply failure;failure.status=503;
    failure.bytes="{\"error\":\"app_unavailable\"}";
    if(!s.ready.load(std::memory_order_acquire)||q.length>UINT32_MAX)return failure;
    Ap01HttpRequestV3 request{q.method,q.path,q.token,q.deviceToken,q.contentType,q.requestId,q.offset,q.nonce,
                             q.body,uint32_t(q.length),q.chunkSha256,q.deviceMac};
    struct Reply {Ap01HttpReply value;unsigned calls=0;bool valid=false;} reply;
    auto emit=[](void *p,uint32_t status,const uint8_t *bytes,uint32_t count)->int32_t {
        auto &r=*(Reply *)p;
        if(++r.calls!=1||status<100||status>599||count>4096||(count&&!bytes))return -1;
        r.value.status=int(status);
        if(count&&!r.value.bytes.concat((const char *)bytes,count))return -1;
        r.valid=true;return 0;
    };
    if(s.binding.pairing(s.binding.context,&request,now,emit,&reply)||!reply.valid||reply.calls!=1)return failure;
    return reply.value;
}
