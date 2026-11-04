#include "native_app_file_boot_v3.h"
#include "native_io_0041.h"
#include <string.h>
Ap01NativeAppFileBootV3::Ap01NativeAppFileBootV3(uint64_t boot,const Ap01VfsOps &io,const Ap01BootPortV3 &backend,
    const Ap01ManifestLimitsV3 &budget,uint32_t staging):files(io),apps(boot,files.packages(),backend),limits(budget),stagingBytes(staging){
    // Explicitly charge the maximum staging allocation against the same RAM cap.
    if(UINT64_MAX-limits.resident_bytes<stagingBytes)limits.resident_bytes=UINT64_MAX;
    else limits.resident_bytes+=stagingBytes;
    apps.shared().onPoll(this,poll);
    apps.shared().appStatus(this,[](void *p,Ap01SupervisorSnapshotV3 &out){out=((Ap01NativeAppFileBootV3 *)p)->status();});
}
bool Ap01NativeAppFileBootV3::stage(const char *path,const uint8_t *expected){
    if(!apps.shared().listening())return false;
    uint32_t empty=0;if(!phase.compare_exchange_strong(empty,1,std::memory_order_acq_rel))return false;
    auto result=files.stage(path,expected,limits,stagingBytes);ioResult.store(result,std::memory_order_release);
    if(result!=Ap01SetFilesResultV3::Ready){files.discard();phase.store(4,std::memory_order_release);return false;}
    phase.store(2,std::memory_order_release);return true;
}
Ap01SetSelectionV3 Ap01NativeAppFileBootV3::stageSelected(Ap01SetSelectorV3 &selector){
    if(!apps.shared().listening())return {};
    uint32_t empty=0;if(!phase.compare_exchange_strong(empty,1,std::memory_order_acq_rel))return {};
    auto selected=selector.select(this,[](void *p,const uint8_t *digest,uint64_t version){
        auto &s=*(Ap01NativeAppFileBootV3 *)p;
        char path[112]="/resource/app-store/manifests/";
        constexpr unsigned prefix=sizeof("/resource/app-store/manifests/")-1;
        const char *hex="0123456789abcdef";
        for(unsigned i=0;i<32;++i){path[prefix+2*i]=hex[digest[i]>>4];path[prefix+2*i+1]=hex[digest[i]&15];}
        memcpy(path+prefix+64,".amf3",6);
        auto result=s.files.stage(path,digest,s.limits,s.stagingBytes);
        if(result==Ap01SetFilesResultV3::Ready&&s.files.version()!=version)result=Ap01SetFilesResultV3::Identity;
        s.ioResult.store(result,std::memory_order_release);
        return result==Ap01SetFilesResultV3::Ready;
    });
    if(selected.mode==Ap01SetBootModeV3::Maintenance){
        files.discard();phase.store(4,std::memory_order_release);
    }else if(!selected.version){
        selector.beginObservation(uint32_t(ap01_native0041::nowMs()));
        files.discard();bootResult.store(Ap01AppSetResultV3::Started,std::memory_order_release);
        phase.store(3,std::memory_order_release);
    }else{
        selector.beginObservation(uint32_t(ap01_native0041::nowMs()));
        phase.store(2,std::memory_order_release);
    }
    return selected;
}
Ap01SetHealthDecisionV3 Ap01NativeAppFileBootV3::healthSelected(Ap01SetSelectorV3 &selector,uint32_t now){
    auto snapshot=supervisor.snapshot();
    bool healthy=snapshot.state==Ap01SupervisorStateV3::Healthy;
    auto decision=selector.observe(now,healthy,snapshot.state==Ap01SupervisorStateV3::Fault);
    if(decision==Ap01SetHealthDecisionV3::Approved&&healthy){
        auto &gate=apps.shared().transactionGate();
        if(snapshot.count&&!gate.held()&&!gate.writable()&&!apps.writes(true))return Ap01SetHealthDecisionV3::Maintenance;
    }else{
        apps.writes(false);
        if(decision==Ap01SetHealthDecisionV3::Approved)return Ap01SetHealthDecisionV3::Maintenance;
    }
    if(decision==Ap01SetHealthDecisionV3::Reboot&&apps.writesDrained())reboot.request(now);
    return decision;
}
Ap01SupervisorSnapshotV3 Ap01NativeAppFileBootV3::status()const{
    auto out=supervisor.snapshot();out.reboot=reboot.state(uint32_t(ap01_native0041::nowMs()));
    uint32_t journal=journalSnapshot.load(std::memory_order_acquire);
    out.journal_result=journal&255;out.journal_phase=journal>>8;return out;
}
void Ap01NativeAppFileBootV3::poll(void *p,bool afterApps){
    auto &s=*(Ap01NativeAppFileBootV3 *)p;
    if(!afterApps&&s.phase.load(std::memory_order_acquire)==2){
        auto result=s.apps.boot(s.files.reader(),s.files.digest(),s.limits);
        s.bootResult.store(result,std::memory_order_release);
        if(result!=Ap01AppSetResultV3::Waiting){s.files.discard();s.phase.store(3,std::memory_order_release);}
    }
    if(afterApps&&s.bootResult.load(std::memory_order_acquire)==Ap01AppSetResultV3::Started){
        int32_t values[AP01_MANIFEST_APPS_V3]{};s.apps.execution().health(values);
        s.supervisor.publish(uint32_t(ap01_native0041::nowMs()),values,s.apps.execution().selection().count);
    }
}
void Ap01NativeAppFileBootV3::monitor(uint32_t now){
    auto result=bootResult.load(std::memory_order_acquire);
    int boot=phase.load(std::memory_order_acquire)==4?-1:result==Ap01AppSetResultV3::Waiting?0:
             result==Ap01AppSetResultV3::Started?1:-1;
    supervisor.tick(now,boot,apps.shared().listening(),apps.shared().maintenanceBeat(),apps.shared().attachedWindow());
}
