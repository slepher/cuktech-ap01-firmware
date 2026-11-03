#include "app_http_0041.h"
#include "native_json_0041.h"
#include "native_integrity_0041.h"
namespace {
using P=Ap01AppUpdatePhase;using D=Ap01AppDownloadResult;using S=Ap01AppSelectionResult;
bool hex(const char *s,uint8_t *out,unsigned n){
    if(!s||strlen(s)!=2*n)return false;
    for(unsigned i=0;i<2*n;++i){unsigned c=s[i];int d=c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:c>='A'&&c<='F'?c-'A'+10:-1;
        if(d<0)return false;
        if(!(i&1))out[i/2]=uint8_t(d<<4);else out[i/2]|=uint8_t(d);
    }return true;
}
void hexText(const uint8_t *in,unsigned n,char *out){const char *h="0123456789abcdef";for(unsigned i=0;i<n;++i){out[2*i]=h[in[i]>>4];out[2*i+1]=h[in[i]&15];}out[2*n]=0;}
const char *phase(P p){switch(p){
    case P::Receiving:return "receiving";case P::Ready:return "ready";case P::SwitchPending:return "switch_pending";
    case P::TrialStarted:return "trial_started";case P::RollbackPending:return "rollback_pending";case P::RollbackStarted:return "rollback_started";
    case P::Succeeded:return "succeeded";case P::FailedRolledBack:return "failed_rolled_back";case P::RecoveryRequired:return "recovery_required";case P::Cancelled:return "cancelled";
}return "invalid";}
const uint8_t *currentDigest(const Ap01AppUpdateRecord &r){return r.phase==P::Succeeded?r.newDigest:r.oldDigest;}
Ap01HttpReply response(int status,const char *error,const char *device,const Ap01AppUpdateRecord *r,const Apx2Limits &limits,bool runtimeReporting,const Ap01AppRuntimeStatus0041 *runtime){
    NativeJsonAllocator0041 allocator;JsonDocument doc(&allocator);
    doc["device_mac"]=device;doc["error_code"]=error;doc["retryable"]=status==503;
    doc["next_action"]=status==503?"query_original_operation":status>=400?"read_status":"query_result";
    doc["phase"]=r?phase(r->phase):"idle";doc["state"]=r?phase(r->phase):"idle";
    doc["sequence"]=r?r->sequence:0;doc["chunk_max"]=Ap01AppDownload0041::chunkMax;doc["package_max"]=limits.package_bytes;
    doc["runtime_reporting"]=runtimeReporting;
    if(runtime){
        auto value=doc["runtime"].to<JsonObject>();value["state"]=runtime->state;
        value["generation"]=runtime->generation;value["business_writes"]=runtime->businessWrites;
        if(runtime->generation){char digest[65];hexText(runtime->digest,32,digest);
            value["sha256"]=String(digest);value["version"]=String(runtime->version);}
    }
    if(r){
        char id[33],old[65],target[65];hexText(r->transaction,16,id);hexText(currentDigest(*r),32,old);hexText(r->newDigest,32,target);
        doc["operation_id"]=String(id);doc["current_sha256"]=String(old);doc["target_sha256"]=String(target);
        doc["received"]=r->received;doc["length"]=r->total;doc["cleanup_pending"]=bool(r->cleanupPending);
    }
    Ap01HttpReply reply;reply.status=status;
    if(doc.overflowed()||!serializeJson(doc,reply.bytes)){reply.status=503;reply.bytes="{\"error_code\":\"reply_oom\",\"next_action\":\"query_original_operation\"}";}
    return reply;
}
bool terminal(P p){return p==P::Succeeded||p==P::FailedRolledBack||p==P::Cancelled||p==P::RecoveryRequired;}
}
Ap01HttpReply Ap01AppHttp0041::handle(const Ap01HttpRequest &request,const char *principal,uint64_t now){
    (void)now;
    const auto *r=journal.current();
    auto reply=[&](int status,const char *error="",bool disclose=true){
        Ap01AppRuntimeStatus0041 runtime{};if(disclose&&port.runtime)port.runtime(port.context,runtime);
        return response(status,error,mac,disclose?r:nullptr,limits,port.runtime!=nullptr,
                        disclose&&port.runtime?&runtime:nullptr);
    };
    if(!principal||!principal[0]||strlen(principal)>64)return reply(401,"unauthorized",false);
    bool status=!strcmp(request.method,"GET")&&!strcmp(request.path,"/api/app/status");
    // Different authenticated principals may see capabilities, never another
    // principal's operation ID, offsets or receipt contents.
    if(r&&strcmp(r->principal,principal))return reply(status?200:404,status?"":"receipt_not_found",false);
    if(!journal.resolved())return reply(503,"journal_unresolved",false);
    if(status)return reply(200);
    if(!request.deviceMac||strcmp(request.deviceMac,mac))return reply(400,"device_mac",false);
    uint8_t id[16]={};
    bool begin=!strcmp(request.method,"POST")&&!strcmp(request.path,"/api/app/update/begin");
    bool chunk=!strcmp(request.method,"PUT")&&!strcmp(request.path,"/api/app/update/chunk");
    bool result=!strcmp(request.method,"GET")&&!strcmp(request.path,"/api/app/update/result");
    bool commit=!strcmp(request.method,"POST")&&!strcmp(request.path,"/api/app/update/commit");
    bool cancel=!strcmp(request.method,"POST")&&!strcmp(request.path,"/api/app/update/cancel");
    if(!begin&&!chunk&&!result&&!commit&&!cancel)return reply(404,"unsupported_endpoint");
    if(!hex(request.requestId,id,16))return reply(400,"operation_id");
    if(!begin&&(!r||memcmp(r->transaction,id,16)))return reply(404,"receipt_expired",false);
    if(result)return reply(terminal(r->phase)?200:202);
    if(port.busy&&port.busy(port.context))return reply(503,"platform_busy");
    if(begin){
        NativeJsonAllocator0041 allocator;JsonDocument input(&allocator);
        if(!request.body||!request.length||request.length>1024||!request.contentType||strcmp(request.contentType,"application/json")||
           memchr(request.body,0,request.length)||deserializeJson(input,request.body,request.length)||
           !input.is<JsonObject>()||input.size()!=6)return reply(400,"begin_json");
        if(strcmp(input["device_mac"]|"",mac)||strcmp(input["app_id"]|"",appId)||
           !input["length"].is<uint32_t>()||!input["expected_sequence"].is<uint64_t>())return reply(400,"begin_identity");
        Ap01AppUpdateRecord next;memcpy(next.transaction,id,16);strcpy(next.principal,principal);
        if(!hex(mac,next.mac,6)||!hex(input["sha256"]|"",next.newDigest,32)||
           !hex(input["expected_current"]|"",next.oldDigest,32))return reply(400,"begin_digest");
        next.total=input["length"].as<uint32_t>();
        bool replay=r&&!memcmp(r->transaction,id,16);
        if(!replay){
            if(input["expected_sequence"].as<uint64_t>()!=(r?r->sequence:0))return reply(409,"sequence_conflict");
            uint8_t zero[32]={};if(memcmp(next.oldDigest,r?currentDigest(*r):zero,32))return reply(409,"current_conflict");
            if(!r&&fs.inspect("/app-current.apx2")!=0)return reply(409,"untracked_current");
            size_t total=fs.totalBytes(),used=fs.usedBytes();
            if(used>total||uint64_t(next.total)+4096>total-used)return reply(507,"storage_budget");
        }
        D d=download.begin(next);r=journal.current();
        return reply(d==D::Ok?(terminal(r->phase)?200:202):d==D::Unknown||d==D::Storage?503:409,d==D::Ok?"":"begin_rejected");
    }
    if(chunk){
        if(!request.offset||!request.offset[0]||strlen(request.offset)>10)return reply(400,"offset");
        uint64_t offset=0;for(const char *p=request.offset;*p;++p){if(*p<'0'||*p>'9')return reply(400,"offset");offset=offset*10+*p-'0';}
        uint8_t expected[32],actual[32];
        if(offset>UINT32_MAX||!request.body||request.length>Ap01AppDownload0041::chunkMax||
           !hex(request.chunkSha256,expected,32)||!request.contentType||strcmp(request.contentType,"application/octet-stream"))return reply(400,"chunk_envelope");
        syncSha256(request.body,request.length,actual);if(memcmp(expected,actual,32))return reply(400,"chunk_digest");
        D d=download.chunk(id,uint32_t(offset),request.body,uint32_t(request.length));r=journal.current();
        return reply(d==D::Ok?202:d==D::Unknown||d==D::Storage?503:409,d==D::Ok?"":"chunk_rejected");
    }
    if(commit){
        if(r->phase==P::Receiving){Apx2Error detail;D d=download.ready(id,detail);r=journal.current();if(d!=D::Ok)return reply(d==D::Unknown||d==D::Storage?503:409,detail==Apx2Error::Ok?"not_ready":apx2ErrorName(detail));}
        if(r->phase==P::Ready&&(!port.stop||!port.stop(port.context)))return reply(503,"stop_pending");
        S s=selection.commit();r=journal.current();
        if(s!=S::Waiting)return reply(s==S::Unknown?503:409,s==S::Unknown?"journal_unknown":"commit_state");
        return reply(terminal(r->phase)?200:202);
    }
    if((r->phase==P::TrialStarted||r->phase==P::SwitchPending)&&(!port.stop||!port.stop(port.context)))return reply(503,"stop_pending");
    S s=selection.cancel();r=journal.current();
    return reply(s==S::Unknown?503:terminal(r->phase)?200:202,s==S::Unknown?"journal_unknown":"");
}
