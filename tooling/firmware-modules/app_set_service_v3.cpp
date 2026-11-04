#include "app_set_service_v3.h"
#include "native_json_0041.h"
#include <string.h>
#include <new>
namespace {
using P=Ap01SetPhaseV3;
void hex(const uint8_t *bytes,unsigned n,char *out){const char *digits="0123456789abcdef";
    for(unsigned i=0;i<n;++i){out[2*i]=digits[bytes[i]>>4];out[2*i+1]=digits[bytes[i]&15];}out[2*n]=0;}
void manifestPath(const uint8_t *digest,char *out){strcpy(out,"/resource/app-store/manifests/");unsigned n=strlen(out);hex(digest,32,out+n);strcat(out,".amf3");}
bool terminal(P p){return p==P::Succeeded||p==P::FailedRolledBack||p==P::Cancelled||p==P::RecoveryRequired;}
}
Apx2Reader Ap01SetServiceV3::ManifestFile::reader(){return {this,size,[](void *p,uint32_t at,uint8_t *out,uint32_t n){auto &s=*(ManifestFile*)p;
    if(at>s.size||n>s.size-at)return false;memcpy(out,s.bytes+at,n);return true;}};}
Ap01SetServiceV3::Ap01SetServiceV3(const Ap01VfsOps &v,Ap01SetJournalV3 &j,Ap01AppWriteGateV3 &g,Ap01AppRebootV3 &r,
    const Ap01ManifestLimitsV3 &l,const uint8_t address[6],uint64_t bootId,uint64_t maintenanceReserve)
    :io(v),journal(j),gate(g),reboot(r),limits(l),boot(bootId),reserve(maintenanceReserve){
    memcpy(mac,address,6);hex(mac,6,device);for(auto &c:device)if(c>='a'&&c<='f')c=char(c-'a'+'A');
}
bool Ap01SetServiceV3::readManifest(std::unique_ptr<ManifestFile> &out,const uint8_t *digest,uint64_t version){
    if(!version){out.reset();return true;}
    if(out&&out->parsed.sequence==version&&!memcmp(out->parsed.digest,digest,32))return true;
    out.reset(new(std::nothrow) ManifestFile);if(!out)return false;
    char path[112];manifestPath(digest,path);int fd=io.open(io.context,path,0);if(fd<0){out.reset();return false;}
    int32_t size=io.size(io.context,fd);bool okay=size>=64&&size<=3584;
    uint32_t at=0;
    while(okay&&at<uint32_t(size)){uint32_t n=uint32_t(size)-at;if(n>1024)n=1024;
        int got=io.read(io.context,fd,out->bytes+at,n);if(got<=0||uint32_t(got)>n)okay=false;else at+=uint32_t(got);}
    if(io.close(io.context,fd))okay=false;
    out->size=at;
    okay=okay&&ap01ReadManifestV3(out->reader(),limits,out->parsed)==Ap01ManifestErrorV3::Ok&&
        out->parsed.sequence==version&&!memcmp(out->parsed.digest,digest,32);
    if(!okay)out.reset();return okay;
}
bool Ap01SetServiceV3::hydrate(){
    const auto *r=journal.current();if(!r)return false;
    if(!readManifest(previous,r->oldDigest,r->oldVersion)||!readManifest(candidate,r->newDigest,r->newVersion))return false;
    if(!download)download.reset(new(std::nothrow) Ap01SetDownloadV3(io,journal,candidate->parsed));
    if(!commit)commit.reset(new(std::nothrow) Ap01SetCommitV3(journal,gate,reboot));
    return bool(download)&&bool(commit);
}
Ap01HttpReply Ap01SetServiceV3::reply(int status,const char *error,bool disclose){
    NativeJsonAllocator0041 allocator;JsonDocument doc(&allocator);
    doc["protocol"]=3;doc["device_mac"]=device;doc["boot_id"]=boot;doc["error_code"]=error;
    doc["next_action"]=frozen||!journal.writable()?"query_original_operation":status>=400?"read_status":"query_result";
    doc["chunk_max"]=1024;doc["manifest_max"]=3584;doc["app_max"]=limits.apps;
    doc["runtime_reporting"]=false; // Attached by the platform integration, never inferred from a receipt.
    const auto *r=disclose?journal.current():nullptr;
    const char *phases[]={"idle","receiving","ready","switch_pending","trial_started","rollback_pending","rollback_started","succeeded","failed_rolled_back","recovery_required","cancelled"};
    doc["phase"]=frozen||!journal.writable()?"unknown":r&&unsigned(r->phase)<11?phases[unsigned(r->phase)]:"idle";
    if(r){char text[65];hex(r->transaction,16,text);doc["operation_id"]=String(text);
        hex(r->oldDigest,32,text);doc["old_manifest"]=String(text);hex(r->newDigest,32,text);doc["candidate_manifest"]=String(text);
        doc["old_version"]=r->oldVersion;doc["candidate_version"]=r->newVersion;doc["sequence"]=r->sequence;
        doc["changed_mask"]=r->changedMask;doc["ready_mask"]=r->readyMask;doc["cleanup_pending"]=bool(r->cleanupPending);
        doc["trial_boot_id"]=r->trialBoot;doc["rollback_boot_id"]=r->rollbackBoot;
        auto received=doc["received"].to<JsonArray>();for(auto n:r->received)received.add(n);
    }
    const char *reboots[]={"idle","pending","invoked","failed"};
    // Reboot state requires a fresh clock; handler adds no fabricated completion.
    (void)reboots;
    Ap01HttpReply out;out.status=status;
    if(doc.overflowed()||!serializeJson(doc,out.bytes)){out.status=503;out.bytes="{\"error_code\":\"reply_oom\",\"next_action\":\"query_original_operation\"}";}
    return out;
}
Ap01HttpReply Ap01SetServiceV3::handle(const Ap01HttpRequest &request,const char *principal,uint32_t now){
    if(!principal||!*principal||strlen(principal)>64)return reply(401,"unauthorized",false);
    Ap01SetHttpCommandV3 command;int parsed=ap01ParseSetHttpV3(request,device,command);
    if(parsed!=200)return reply(parsed,"request_syntax",false);
    using A=Ap01SetHttpActionV3;
    const auto *r=journal.current();
    if(r&&strcmp(r->principal,principal))return reply(command.action==A::Status?200:404,"receipt_not_found",false);
    bool observe=command.action==A::Status||command.action==A::Result;
    if(observe&&(frozen||!journal.writable())){
        auto loaded=journal.load();if(loaded!=Ap01SetJournalResultV3::Ok&&loaded!=Ap01SetJournalResultV3::Empty)return reply(503,"journal_unresolved",false);
        download.reset();commit.reset();previous.reset();candidate.reset();frozen=false;r=journal.current();
        if(r&&strcmp(r->principal,principal))return reply(404,"receipt_not_found",false);
    }
    if(frozen||!journal.writable())return reply(503,"operation_unknown");
    if(command.action==A::Status)return reply(200,"");
    if(command.action!=A::Begin&&(!r||memcmp(command.transaction,r->transaction,16)))return reply(404,"receipt_expired",false);
    if(command.action==A::Result)return reply(terminal(r->phase)?200:202,"");
    if(command.action==A::Begin){
        uint8_t active[32]{};uint64_t version=0;bool replay=r&&!memcmp(r->transaction,command.transaction,16);
        if(r){bool selectedNew=!replay&&r->phase==P::Succeeded;memcpy(active,selectedNew?r->newDigest:r->oldDigest,32);version=selectedNew?r->newVersion:r->oldVersion;}
        if(memcmp(command.expected,active,32)||command.expectedVersion!=version)return reply(409,"current_conflict");
        download.reset();commit.reset();candidate.reset();previous.reset();
        if(!readManifest(previous,active,version))return reply(503,"manifest_read");
        candidate.reset(new(std::nothrow) ManifestFile);if(!candidate)return reply(503,"memory");
        candidate->size=command.length;memcpy(candidate->bytes,command.bytes,command.length);
        Apx2Reader old{};if(previous)old=previous->reader();Ap01SetRecordV3 plan;
        auto result=ap01BeginSetV3(journal,io,previous?&old:nullptr,candidate->reader(),limits,command.transaction,mac,principal,reserve,candidate->parsed,plan);
        using B=Ap01SetBeginResultV3;
        if(result==B::Unknown)frozen=true;
        return reply(result==B::New||result==B::Replay?200:result==B::Unknown||result==B::Storage?503:result==B::Space?507:409,
            result==B::New||result==B::Replay?"":result==B::Space?"storage_space":result==B::Unknown?"operation_unknown":"begin_rejected");
    }
    if(!hydrate())return reply(503,"manifest_read");
    if(command.action==A::Chunk||command.action==A::Ready){
        auto result=command.action==A::Chunk?download->chunk(command.transaction,command.index,command.offset,command.bytes,command.length):download->ready(command.transaction,command.index,1);
        using D=Ap01SetDownloadResultV3;if(result==D::Unknown)frozen=true;
        return reply(result==D::Ok?200:result==D::Unknown||result==D::Storage?503:409,result==D::Ok?"":result==D::Unknown?"operation_unknown":"package_rejected");
    }
    Ap01SetCommitResultV3 result;
    if(command.action==A::Cancel)result=commit->cancel(command.transaction,now);
    else {
        auto files=std::unique_ptr<Ap01AppSetFilesV3>(new(std::nothrow) Ap01AppSetFilesV3(io));if(!files)return reply(503,"memory");
        char path[112];manifestPath(r->newDigest,path);
        if(files->stage(path,r->newDigest,limits,1u<<22)!=Ap01SetFilesResultV3::Ready)return reply(409,"collection_preflight");
        result=commit->commit(command.transaction,r->oldDigest,r->oldVersion,candidate->parsed,files->packages(),now);
    }
    using C=Ap01SetCommitResultV3;if(result==C::Unknown)frozen=true;
    return reply(result==C::Pending?202:result==C::Cancelled?200:result==C::Unknown?503:409,
        result==C::Pending||result==C::Cancelled?"":result==C::Unknown?"operation_unknown":result==C::Busy?"write_drain_pending":result==C::DrainTimeout?"write_drain_timeout":result==C::RebootFailed?"reboot_failed":"transaction_rejected");
}
