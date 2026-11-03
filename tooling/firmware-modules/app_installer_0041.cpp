#include "app_installer_0041.h"
using P=Ap01AppUpdatePhase;using S=Ap01AppRunState;
Ap01AppInstaller0041::Ap01AppInstaller0041(LittleFSClass &fs,const uint8_t mac[6],const char *text,
        const Apx2Limits &limits,const Ap01AppImagePort0041 &port,const ap01_app_services_v2 &services,
        void *context,bool (*isBusy)(void *))
    :journal(fs,mac),download(fs,journal,limits),selection(fs,journal,limits),
     runner(fs,selection,limits,port,services),
     http(fs,journal,download,selection,{this,busy,stop,runtime},limits,text,limits.app_id?limits.app_id:""),
     busyContext(context),platformBusy(isBusy){}
bool Ap01AppInstaller0041::busy(void *p){
    auto &self=*(Ap01AppInstaller0041 *)p;
    return self.runner.status()==S::RebootRequired||(self.platformBusy&&self.platformBusy(self.busyContext));
}
bool Ap01AppInstaller0041::stop(void *p){
    auto &self=*(Ap01AppInstaller0041 *)p;
    self.bootPending=false;
    return self.runner.stop(self.requestNow)==S::Idle;
}
void Ap01AppInstaller0041::runtime(void *p,Ap01AppRuntimeStatus0041 &out){
    auto &self=*(Ap01AppInstaller0041 *)p;out={};
    switch(self.runner.status()){
    case S::Idle:out.state="idle";break;
    case S::Running:out.state="running";break;
    case S::Stopping:out.state="stopping";break;
    case S::Recovery:out.state="recovery";break;
    case S::Unknown:out.state="unknown";break;
    case S::RebootRequired:out.state="reboot_required";break;
    }
    if(const auto *running=self.runner.running()){
        const auto *view=self.runner.runningImage();
        out.generation=running->generation;memcpy(out.digest,running->digest,32);
        if(view)memcpy(out.version,view->version,sizeof(out.version));
        out.businessWrites=self.runner.businessWritesAllowed();
    }
}
Ap01HttpReply Ap01AppInstaller0041::handle(const Ap01HttpRequest &request,const char *principal,uint64_t now){
    requestNow=now;
    auto reply=http.handle(request,principal,now);
    runner.reconcile(now);
    // Only a durable decision schedules launch. A stop_pending response while
    // Ready must keep the old App stopped until the original commit is retried.
    const auto *r=journal.current();
    if(journal.resolved()&&r&&(r->phase==P::SwitchPending||r->phase==P::RollbackPending))launchPending=true;
    return reply;
}
S Ap01AppInstaller0041::tick(uint64_t now,uint32_t stock,uint32_t maintenance){
    if(busy(this))return runner.status();
    runner.tick(now,stock,maintenance); // Drain even when the journal becomes uncertain.
    if(!journal.resolved())return runner.status();
    if(bootPending){bootPending=false;launchPending=true;}
    if(launchPending&&(runner.status()==S::Idle||runner.status()==S::Recovery||runner.status()==S::Unknown)){
        launchPending=false;runner.launch(now);
    }
    const auto *r=journal.current();
    if(journal.resolved()&&r&&r->cleanupPending&&
       (r->phase==P::Succeeded||r->phase==P::FailedRolledBack||r->phase==P::Cancelled||
        (r->phase==P::RecoveryRequired&&runner.status()==S::Recovery)))selection.cleanup();
    return runner.status();
}
