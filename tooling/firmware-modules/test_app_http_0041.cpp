#include "app_http_0041.h"
#include "app_installer_0041.h"
#include "app_services_0041.h"
#include "app_heap_client_v2.h"
#include "native_maintenance_0041.h"
#include "native_integrity_0041.h"
#include "test_app_file_store_0041.h"
#include <string>
#include <vector>
#include <fstream>
#include <iterator>
std::string hex(const uint8_t *bytes,unsigned n){std::string out;const char *h="0123456789abcdef";while(n--){out+=h[*bytes>>4];out+=h[*bytes++&15];}return out;}
struct Port {
    Ap01AppHttp0041 *api=nullptr;unsigned stops=0;bool stopped=false,busy=false;
    static bool stop(void *p){auto &s=*(Port *)p;++s.stops;return s.stopped;}
    static bool isBusy(void *p){return ((Port *)p)->busy;}
    static void runtime(void *,Ap01AppRuntimeStatus0041 &out){
        out.state="running";out.generation=7;memset(out.digest,0xab,32);
        strcpy(out.version,"fixture");out.businessWrites=true;
    }
};
struct Stream {
    std::string input,output;size_t at=0;
    static int read(void *p,uint8_t *out,size_t n,uint64_t){auto &s=*(Stream *)p;n=std::min(n,s.input.size()-s.at);memcpy(out,s.input.data()+s.at,n);s.at+=n;return n;}
    static int write(void *p,const uint8_t *in,size_t n,uint64_t){((Stream *)p)->output.append((const char *)in,n);return n;}
};
std::string wire(Ap01Maintenance0041 &m,const char *method,const std::string &path,const std::string &body,const char *type="application/json",const char *token="01234567"){
    std::string target=path;
    if(path.find("/api/app/update/")==0&&path.find("device_mac=")==std::string::npos)target+="&device_mac=010203040506";
    Stream s;s.input=std::string(method)+" "+target+" HTTP/1.1\r\nAuthorization: Bearer "+token+"\r\nContent-Type: "+type+"\r\nContent-Length: "+std::to_string(body.size())+"\r\n\r\n"+body;
    assert(ap01ServeMaintenanceHttp0041(m,{&s,Stream::read,Stream::write},0,15000));return s.output;
}
void status(const std::string &reply,int expected){assert(reply.find("HTTP/1.1 "+std::to_string(expected)+" ")==0);}
// Host entry backend exercises production loading/lifecycle, not RV32 instructions.
struct Execution {
    std::vector<uint8_t> memory;unsigned starts=0,events=0,healthCalls=0,stops=0;
    Ap01AppInstaller0041 *installer=nullptr;bool preparePending=false;
    Ap01AppServices0041 *services=nullptr;Ap01AppFiles0041 *files=nullptr;
    Ap01AppHeap0041 *heap=nullptr;alignas(16) uint8_t heapMemory[4096]{};
    uint8_t *heapAllocation=nullptr;bool heapBound=false;
    ap01_app_services_v2 captured{};uint64_t now=0;uint32_t held=0;unsigned drains=0;
    static bool clock(void *p,uint64_t *out){*out=((Execution *)p)->now;return true;}
    static bool random(void *,uint8_t *out,uint32_t n){memset(out,7,n);return true;}
    static bool mac(void *,char out[13]){memcpy(out,"010203040506",13);return true;}
    static bool permission(void *p,uint32_t generation,bool allow){return ((Execution *)p)->files->writes(generation,allow);}
    static bool drain(void *p){auto &x=*(Execution *)p;if(!x.files->drain())return false;
        if(!x.heap->drain())return false;x.heapBound=false;x.heapAllocation=nullptr;
        x.held=0;++x.drains;return true;}
    bool canWrite(){
        ap01_app_file_request_v2 request{};strcpy(request.path,"/probe");request.argument=1;
        uint32_t handle=0,written=0;
        int32_t result=captured.invoke(captured.context,captured.generation,2,AP01_FILE_OPEN,&request,sizeof(request),&handle,4,&written);
        if(result){assert(result==AP01_FILE_READ_ONLY||result==AP01_SERVICE_UNAVAILABLE);return false;}
        assert(written==4);
        if(!held){held=handle;return true;} // Leave one descriptor for resident drain.
        request={};request.handle=handle;
        assert(!captured.invoke(captured.context,captured.generation,2,AP01_FILE_CLOSE,&request,sizeof(request),nullptr,0,&written));return true;
    }
    static bool reserve(void *p,const Apx2View &v,Ap01AppMemory0041 &out){auto &x=*(Execution *)p;
        if(v.heap_bytes>sizeof(x.heapMemory)||!x.heap->bind(x.installer->callbacks().current()+1,x.heapMemory,v.heap_bytes))return false;
        x.heapBound=true;
        x.memory.resize(v.image_bytes+v.bss_bytes);out={x.memory.data(),uint32_t(x.memory.size()),0x10000,&x};return true;}
    static int32_t invoke(void *p,uint32_t generation,uint32_t service,uint32_t operation,const void *input,uint32_t length,void *output,uint32_t capacity,uint32_t *written){
        auto table=((Execution *)p)->services->table(generation);
        return table.invoke(table.context,generation,service,operation,input,length,output,capacity,written);
    }
    static int32_t start(const ap01_app_services_v2 *s,void **out){auto &x=*(Execution *)s->context;
        if(x.starts){uint64_t stale=0;assert(ap01_app_core_call(&x.captured,AP01_CORE_MONOTONIC_MS,&stale,8)==AP01_SERVICE_UNAVAILABLE);
            assert(!x.canWrite()&&x.drains==x.starts&&!x.held);}
        x.captured=*s;assert(!x.canWrite());
        Ap01AppHeapClientV2 allocator(*s);x.heapAllocation=(uint8_t *)allocator.zeroAllocate(1,32);assert(x.heapAllocation);
        for(unsigned i=0;i<32;++i)assert(!x.heapAllocation[i]);memset(x.heapAllocation,0x4b,32);
        assert(!allocator.allocate(sizeof(x.heapMemory))); // Cannot exceed declared heap_bytes.
        uint64_t now=0;char mac[13];uint8_t random=0;
        assert(!ap01_app_core_call(s,AP01_CORE_MONOTONIC_MS,&now,8)&&now==x.now);
        assert(!ap01_app_core_call(s,AP01_CORE_MAC,mac,13)&&!strcmp(mac,"010203040506"));
        assert(!ap01_app_core_call(s,AP01_CORE_RANDOM,&random,1)&&random==7);
        uint32_t written=99;assert(s->invoke(s->context,s->generation,99,0,nullptr,0,nullptr,0,&written)==AP01_SERVICE_UNAVAILABLE&&!written);
        ++x.starts;x.preparePending=true;*out=&x;return 0;}
    static int32_t event(void *p,const ap01_app_event_v2 *){auto &x=*(Execution *)p;++x.events;
        for(unsigned i=0;i<32;++i)assert(x.heapAllocation[i]==0x4b);return 0;}
    static int32_t prepare(void *p){auto &x=*(Execution *)p;if(x.preparePending){x.preparePending=false;return 1;}return 0;}
    static int32_t stop(void *p){auto &x=*(Execution *)p;++x.stops;
        for(unsigned i=0;i<32;++i)assert(x.heapAllocation[i]==0x4b);return 0;}
    static int32_t health(void *p,ap01_app_health_v2 *out){++((Execution *)p)->healthCalls;out->entry_ready=1;return 0;}
    static bool publish(void *,const Ap01AppMemory0041 &,const Apx2View &,ap01_app_entries_v2 &out){out={start,event,prepare,stop,health};return true;}
    static void release(void *p,const Ap01AppMemory0041 &){auto &x=*(Execution *)p;
        if(x.heapBound){assert(x.heap->drain());x.heapBound=false;}
        assert(x.installer->callbacks().drained()&&x.drains==x.stops&&!x.held&&!x.heapAllocation);x.memory.clear();}
};
int serveInstaller(LittleFSClass &fs,const uint8_t mac[6],const Ap01VfsOps &io,const char *root){
    Execution execution;Apx2Limits limits{4096,4096,1024,1024,2,UINT64_MAX,"golden.app"};
    ap01_app_services_v2 services{2,sizeof(services),0,0,AP01_APP_CORE_CAPABILITY|AP01_APP_FILE_CAPABILITY|AP01_APP_HEAP_CAPABILITY,&execution,Execution::invoke};
    Ap01AppInstaller0041 installer(fs,mac,"010203040506",limits,
        {&execution,Execution::reserve,Execution::publish,Execution::release,Execution::drain,Execution::permission},services);execution.installer=&installer;
    std::string businessRoot=std::string(root)+"/business";assert(!mkdir(businessRoot.c_str(),0700));
    Ap01AppFiles0041 files(installer.callbacks(),io,businessRoot.c_str());execution.files=&files;
    Ap01AppCore0041 core(installer.callbacks(),{&execution,Execution::clock,Execution::random,Execution::mac});
    Ap01AppHeap0041 heap(installer.callbacks());execution.heap=&heap;
    Ap01AppServices0041 bus(core,files,nullptr,&heap);execution.services=&bus;
    auto loaded=installer.begin();assert(loaded==Ap01AppJournalResult::Empty||loaded==Ap01AppJournalResult::Ok);
    Ap01MaintenancePort0041 port{};port.context=&installer;
    port.deviceCode=[](void *,char out[9]){memcpy(out,"01234567",9);return 0;};
    port.appUpdate=[](void *p,const Ap01HttpRequest &r,const char *principal,uint64_t now){return ((Ap01AppInstaller0041 *)p)->handle(r,principal,now);};
    Ap01Maintenance0041 maintenance(fs,port,{},"010203040506",1);assert(maintenance.begin());
    uint32_t ticks=0;
    for(;;){
        uint8_t size[4];size_t got=fread(size,1,4,stdin);if(!got)break;assert(got==4);
        uint32_t n=uint32_t(size[0])|uint32_t(size[1])<<8|uint32_t(size[2])<<16|uint32_t(size[3])<<24;
        if(!n)break;assert(n<=8192);
        Stream stream;stream.input.resize(n);assert(fread(&stream.input[0],1,n,stdin)==n);
        uint64_t now=uint64_t(ticks)*1000;
        execution.now=now;
        ap01_app_event_v2 event{sizeof(event),1,0,0,nullptr,0};
        if(installer.status()==Ap01AppRunState::Running)assert(installer.event(now,event)==Ap01AppLifeResult::Ok);
        installer.tick(now,ticks,ticks);++ticks;
        assert(ap01ServeMaintenanceHttp0041(maintenance,{&stream,Stream::read,Stream::write},now,now+15000));
        if(execution.starts)assert(execution.canWrite()==installer.businessWritesAllowed());
        n=stream.output.size();for(unsigned i=0;i<4;++i)size[i]=uint8_t(n>>(8*i));
        assert(fwrite(size,1,4,stdout)==4&&fwrite(stream.output.data(),1,n,stdout)==n);fflush(stdout);
    }
    if(installer.record()&&installer.record()->phase==Ap01AppUpdatePhase::Succeeded){
        assert(execution.starts>=1&&execution.events>=30*execution.starts&&execution.healthCalls>=30*execution.starts);
        assert(installer.businessWritesAllowed()&&!installer.record()->cleanupPending);
    }
    return 0;
}
int main(int argc,char **argv){
    assert(argc==3||argc==4);bool serving=argc==4&&!strcmp(argv[3],"--serve");
    std::ifstream in(argv[2],std::ios::binary);std::vector<uint8_t> package{std::istreambuf_iterator<char>(in),{}};assert(package.size()==320);
    Disk disk;auto io=disk.ops();LittleFSClass fs(io,argv[1]);uint8_t mac[6]={1,2,3,4,5,6};
    if(serving)return serveInstaller(fs,mac,io,argv[1]);
    Ap01AppUpdateJournal0041 journal(fs,mac);auto loaded=journal.load();
    assert(loaded==Ap01AppJournalResult::Empty||(serving&&loaded==Ap01AppJournalResult::Ok));
    Apx2Limits limits{4096,4096,1024,1024,2,UINT64_MAX,"golden.app"};
    Ap01AppDownload0041 download(fs,journal,limits);Ap01AppSelection0041 selection(fs,journal,limits);Port port;
    Ap01AppHttp0041 api(fs,journal,download,selection,{&port,Port::isBusy,Port::stop,Port::runtime},limits,"010203040506","golden.app");port.api=&api;
    Ap01MaintenancePort0041 maintenancePort{};maintenancePort.context=&port;
    maintenancePort.deviceCode=[](void *,char out[9]){memcpy(out,"01234567",9);return 0;};
    maintenancePort.appUpdate=[](void *p,const Ap01HttpRequest &r,const char *principal,uint64_t now){return ((Port *)p)->api->handle(r,principal,now);};
    Ap01Maintenance0041 m(fs,maintenancePort,{},"010203040506",1);assert(m.begin());
    std::string id(32,'1'),zero(64,'0');std::string begin="{\"device_mac\":\"010203040506\",\"app_id\":\"golden.app\",\"length\":320,\"expected_sequence\":0,\"sha256\":\""+hex(package.data()+192,32)+"\",\"expected_current\":\""+zero+"\"}";
    std::string base="/api/app/update/",query="?operation_id="+id;
    status(wire(m,"GET","/api/app/status","", "application/json","bad"),401);
    auto runtimeStatus=wire(m,"GET","/api/app/status","");status(runtimeStatus,200);
    assert(runtimeStatus.find("\"runtime_reporting\":true")!=std::string::npos&&runtimeStatus.find("\"generation\":7")!=std::string::npos);
    status(wire(m,"POST",base+"begin"+query+"&device_mac=999999999999",begin),400);
    status(wire(m,"POST",base+"begin"+query,begin),202);
    auto seq=journal.current()->sequence;
    status(wire(m,"POST",base+"begin"+query,begin),202);assert(journal.current()->sequence==seq);
    auto stale=wire(m,"POST",base+"begin?operation_id="+std::string(32,'2'),begin);status(stale,409);assert(stale.find("sequence_conflict")!=std::string::npos);
    auto conflicting=begin;conflicting.replace(conflicting.find(":320"),4,":321");status(wire(m,"POST",base+"begin"+query,conflicting),409);
    Ap01HttpRequest foreign{};foreign.method="GET";foreign.path="/api/app/update/result";foreign.requestId=id.c_str();
    auto hidden=api.handle(foreign,"different-principal",0);assert(hidden.status==404&&!strstr(hidden.bytes.c_str(),id.c_str())&&!strstr(hidden.bytes.c_str(),"\"runtime\"")&&!strstr(hidden.bytes.c_str(),"\"generation\""));
    std::string payload((const char *)package.data(),package.size());uint8_t digest[32];syncSha256(package.data(),package.size(),digest);
    std::string chunk=base+"chunk"+query+"&offset=0&sha256="+hex(digest,32);
    status(wire(m,"PUT",base+"chunk"+query+"&offset=0&sha256="+zero,payload,"application/octet-stream"),400);
    status(wire(m,"PUT",chunk,payload,"application/octet-stream"),202);
    seq=journal.current()->sequence;status(wire(m,"PUT",chunk,payload,"application/octet-stream"),202);assert(journal.current()->sequence==seq);
    status(wire(m,"POST",base+"commit"+query,""),503);assert(journal.current()->phase==Ap01AppUpdatePhase::Ready);
    port.stopped=true;status(wire(m,"POST",base+"commit"+query,""),202);unsigned stops=port.stops;
    status(wire(m,"POST",base+"commit"+query,""),202);assert(port.stops==stops);
    Ap01AppSelection launch;assert(selection.select(1,launch)==Ap01AppSelectionResult::Launch&&launch.trial);
    for(unsigned i=0;i<=30;++i)assert(selection.observe(1,launch.digest,i*1000,{true,true,i,i,i})==Ap01AppSelectionResult::Waiting);
    auto receipt=wire(m,"GET",base+"result"+query,"");status(receipt,200);assert(receipt.find("succeeded")!=std::string::npos);
    port.busy=true;status(wire(m,"GET",base+"result"+query,""),200);status(wire(m,"GET","/api/app/status",""),200);port.busy=false;
    status(wire(m,"POST",base+"begin"+query,begin),200);
    status(wire(m,"POST",base+"cancel"+query,""),200);assert(journal.current()->phase==Ap01AppUpdatePhase::Succeeded);
    status(wire(m,"GET",base+"result?operation_id="+std::string(32,'2'),""),404);
    status(wire(m,"PUT",chunk+"&operation_id="+id,payload,"application/octet-stream"),400);
    puts("app HTTP: manual auth, begin/replay/fence, private receipts, block SHA, stop pending, single commit, health success, cancel replay passed");
}
