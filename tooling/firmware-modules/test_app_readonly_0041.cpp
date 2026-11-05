// Real business/BundleStore/application code, mutation-counting host VFS.
#include "application.h"
#include "v2_command_envelope.h"
#include "local_json_allocator.h"
#include "platform_target.h"
#include "test_app_file_store_0041.h"
#include "app_files_0041.h"
#include "app_vfs_client_v2.h"
#include "app_files_v3.h"
#include "app_platform_api_v3.h"
#include "app_services_0041.h"
#include "app_network_client_v2.h"
#include "app_network_client_v3.h"
#include "app_network_v3.h"
#include "http.h"
#include <fstream>
#include <iterator>
#include <string>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
static std::atomic_flag bindingLock=ATOMIC_FLAG_INIT;
static std::mutex writeMutex;static std::condition_variable writeCv;
static bool pauseWrite=false,writeEntered=false,releaseWrite=false;
static Disk disk;static unsigned mutations=0,frames=0,failWriteAt=0;
static Ap01AppFilesV3 *directFiles=nullptr;
static size_t largestWrite=0;static bool failEveryWrite=false;
static int prepare(void *,const char *){++mutations;return 0;}
static int open(void *,const char *path,unsigned mode){if(mode)++mutations;return Disk::open(&disk,path,mode);}
static int write(void *,int fd,const void *p,size_t n){
    ++mutations;if(n>largestWrite)largestWrite=n;
    if(directFiles)assert(!directFiles->writes(false)); // Cannot freeze an in-flight write.
    {
        std::unique_lock<std::mutex> guard(writeMutex);
        if(pauseWrite){writeEntered=true;writeCv.notify_all();
            assert(writeCv.wait_for(guard,std::chrono::seconds(5),[]{return releaseWrite;}));}
    }
    if(failEveryWrite||mutations==failWriteAt)return -1;return Disk::write(&disk,fd,p,n);
}
static int remove(void *,const char *p){++mutations;return Disk::remove(&disk,p);}
static int rename(void *,const char *a,const char *b){++mutations;return Disk::rename(&disk,a,b);}
static int mkdir(void *,const char *p){++mutations;return ::mkdir(p,0700);}
static bool present(void *,uint8_t *bytes,uint32_t){if(bytes){++frames;delete[] bytes;}return true;}
static bool random(void *,uint8_t *bytes,size_t n){memset(bytes,7,n);return true;}
static bool lock(void *){return !bindingLock.test_and_set(std::memory_order_acquire);}
static void unlock(void *){bindingLock.clear(std::memory_order_release);}
static std::string bytes(const std::string &path){std::ifstream file(path,std::ios::binary);return {std::istreambuf_iterator<char>(file),{}};}
// Deterministic transport faults under the real network service/client/parser.
// No sockets or device access; only the lowest transport functions are fakes.
struct NetworkWire {
    std::string input,output;size_t at=0;uint64_t now=100;
    unsigned reads=0,writes=0,closed=0,scenario=0;
    Ap01AppGeneration0041 *gate=nullptr;
    static bool clock(void *p,uint64_t *out){*out=((NetworkWire *)p)->now;return true;}
    static bool yield(void *p){++((NetworkWire *)p)->now;return true;}
    static int listen(void *,uint16_t,bool){return 10;}
    static int accept(void *,int){return 11;}
    static int close(void *p,int){++((NetworkWire *)p)->closed;return 0;}
    static int poll(void *,int,unsigned events){return int(events);}
    static int receive(void *p,int,uint8_t *out,uint32_t n,ap01_app_peer_v2 *peer){
        auto &w=*(NetworkWire *)p;++w.reads;
        if(!directFiles)assert(n<=1024);
        if(w.scenario==6){if(directFiles)return AP01_SERVICE_IO;w.gate->close();return AP01_NET_AGAIN;}
        if(w.scenario==3||(w.scenario==1&&w.reads%3==1))return AP01_NET_AGAIN;
        if(peer){memset(peer,0,sizeof(*peer));peer->ip[0]=127;peer->ip[3]=1;peer->port=1234;}
        size_t take=std::min(size_t(n),std::min(w.scenario==7?size_t(4096):size_t(7),w.input.size()-w.at));
        memcpy(out,w.input.data()+w.at,take);w.at+=take;return int(take);
    }
    static int send(void *p,int,const uint8_t *in,uint32_t n,const ap01_app_peer_v2 *){
        auto &w=*(NetworkWire *)p;++w.writes;if(!directFiles)assert(n<=1024);
        if(w.scenario==4||(w.scenario==1&&w.writes%3==1))return AP01_NET_AGAIN;
        if(w.scenario==5&&w.output.size()>=10)return AP01_SERVICE_IO;
        unsigned take=w.scenario==8?n:std::min(n,5u);w.output.append((const char *)in,take);return int(take);
    }
};
static void networkHttp(Ap01Application &app){
    for(unsigned scenario=0;scenario<8;++scenario){
        NetworkWire wire;wire.scenario=scenario;Ap01AppGeneration0041 gate;wire.gate=&gate;
#ifdef AP01_TEST_DIRECT_FILES
        Ap01AppNetworkV3 network({&wire,NetworkWire::listen,NetworkWire::accept,NetworkWire::close,NetworkWire::poll,NetworkWire::receive,NetworkWire::send},
                                &wire,NetworkWire::clock,NetworkWire::yield,18081,8767);
        using Client=Ap01AppNetworkClientV3;
        Client client(network.table());
        assert(client.listen(18080)<0); // Maintenance port is never granted to App.
#else
        Ap01AppCore0041 core(gate,{&wire,NetworkWire::clock,nullptr,nullptr,NetworkWire::yield});
        Ap01AppFiles0041 files(gate,{},"/unused");
        Ap01AppNetwork0041 network(gate,{&wire,NetworkWire::listen,NetworkWire::accept,NetworkWire::close,NetworkWire::poll,NetworkWire::receive,NetworkWire::send});
        Ap01AppServices0041 services(core,files,&network);
        using Client=Ap01AppNetworkClientV2;
        Client client(services.table(gate.begin()));
#endif
        int listener=client.listen(18081),connection=client.accept(listener);assert(listener>0&&connection>0);
        wire.input="POST /api/bundle/begin HTTP/1.1\r\nContent-Length: 3000\r\nContent-Type: application/json\r\n\r\n"+std::string(scenario==2?3:3000,'x');
        struct Stream {Client *client;int handle;} stream{&client,connection};
        Ap01Stream io{&stream,
            [](void *p,uint8_t *out,size_t n,uint64_t deadline){auto &s=*(Stream *)p;return s.client->receive(s.handle,out,n,deadline);},
            [](void *p,const uint8_t *in,size_t n,uint64_t deadline){auto &s=*(Stream *)p;return s.client->send(s.handle,in,n,deadline);}};
        uint64_t deadline=scenario==3||scenario==4?105:5100;
        bool okay=ap01ServeHttp(app,io,100,deadline);
        if(scenario==0||scenario==1||scenario==7){
            assert(okay&&wire.at==wire.input.size()&&wire.output.find("HTTP/1.1 503 ")==0);
            assert(wire.output.find("app_trial_readonly")!=std::string::npos);
            auto headerEnd=wire.output.find("\r\n\r\n"),lengthAt=wire.output.find("Content-Length: ");assert(headerEnd!=std::string::npos&&lengthAt!=std::string::npos);
            assert(std::stoul(wire.output.substr(lengthAt+16))==wire.output.size()-headerEnd-4);
        }else{
            assert(!okay);
            if(scenario==3||scenario==4)assert(wire.now==deadline);
            if(scenario==5)assert(wire.output.size()==10);else assert(wire.output.empty());
        }
#ifdef AP01_TEST_DIRECT_FILES
        assert(client.close(connection)&&client.close(listener)&&wire.closed==2);
        uint8_t out=0;assert(client.receive(connection,&out,1,wire.now+10)<0);
        if(scenario==0){
            int udp=client.listen(8767,true);assert(udp>0&&client.accept(udp)<0);
            uint8_t data[1300];Ap01PeerV3 peer{};
            wire.scenario=7;wire.input=std::string(sizeof(data),'u');wire.at=0;
            assert(client.receiveFrom(udp,data,sizeof(data),peer)==sizeof(data));
            assert(peer.ip[0]==127&&peer.ip[3]==1&&peer.port==1234&&!peer.reserved);
            assert(client.sendTo(udp,data,sizeof(data),peer)<0); // Partial UDP is an error.
            wire.scenario=8;assert(client.sendTo(udp,data,sizeof(data),peer)==sizeof(data));
            peer.reserved=1;assert(client.sendTo(udp,data,sizeof(data),peer)<0);
            assert(client.receive(udp,data,1,wire.now+10)<0&&client.close(udp));
        }
#else
        gate.close();assert(network.drain()&&wire.closed==2);
#endif
    }
}
// Authenticated C2 requests through the real application and coordinated VFS.
static void scopedHttp(Ap01Application &app,Ap01Business &business,bool &occupied,const std::string &bundle){
    const char *token="0123456789abcdef0123456789abcdef";
    std::string pair=R"({"device_mac":"AABBCCDDEEFF","bridge_id":"bridge-test","name":"scope-test","display_code":"1234","binding_token":"0123456789abcdef0123456789abcdef","request_id":"pair-scope","boot_id":7,"pairing_revision":0})";
    Ap01HttpRequest pairing{};pairing.method="POST";pairing.path="/api/pairing";pairing.token="";
    pairing.body=(const uint8_t *)pair.data();pairing.length=pair.size();
    auto paired=app.pairingHttp(pairing,300);if(paired.status!=202)fprintf(stderr,"pair: %s\n",paired.bytes.c_str());assert(paired.status==202);
    assert(app.pairingDisplayed("pair-scope",0,1));
    unsigned beforePair=mutations;
    assert(app.button(true,2,301)&&app.button(false,3,302));
    assert(mutations==beforePair); // UI cannot commit bindings.
    char principal[65];assert(app.bindingPrincipal(token,principal)==401);
    occupied=true;app.processConfirmation(303);
    assert(mutations==beforePair&&app.bindingPrincipal(token,principal)==401);
    // Cancel the queued approval, then replace it before the worker runs.
    Ap01HttpRequest cancel{};cancel.method="DELETE";cancel.path="/api/pairing/pair-scope";
    cancel.token=token;cancel.body=(const uint8_t *)"";
    assert(app.pairingHttp(cancel,304).status==200);
    pair.replace(pair.find("pair-scope"),10,"pair-new");
    pair.replace(pair.find("\"pairing_revision\":0"),20,"\"pairing_revision\":1");
    pairing.body=(const uint8_t *)pair.data();pairing.length=pair.size();occupied=false;
    assert(app.pairingHttp(pairing,305).status==202);
    assert(app.pairingDisplayed("pair-new",1,4));
    app.processConfirmation(306);
    assert(mutations==beforePair&&app.bindingPrincipal(token,principal)==401);
    assert(app.button(true,5,307)&&app.button(false,6,308));
    // A valid release cannot approve after the original request deadline.
    app.processConfirmation(120305);
    assert(mutations==beforePair&&app.bindingPrincipal(token,principal)==401);
    pair.replace(pair.find("pair-new"),8,"pair-final");
    pair.replace(pair.find("\"pairing_revision\":1"),20,"\"pairing_revision\":2");
    pairing.body=(const uint8_t *)pair.data();pairing.length=pair.size();
    assert(app.pairingHttp(pairing,120306).status==202);
    assert(app.pairingDisplayed("pair-final",2,7));
    assert(app.button(true,8,120307)&&app.button(false,9,120308));
    occupied=true;app.processConfirmation(120309);assert(mutations==beforePair);
    occupied=false;
    {std::lock_guard<std::mutex> guard(writeMutex);pauseWrite=true;writeEntered=false;releaseWrite=false;}
    std::thread worker([&]{app.processConfirmation(120310);});
    {std::unique_lock<std::mutex> guard(writeMutex);
        assert(writeCv.wait_for(guard,std::chrono::seconds(5),[]{return writeEntered;}));}
    // The production binding lock spans the admitted save/readback/rename.
    // UI, another worker turn and cancellation cannot interleave with it.
    unsigned atWrite=mutations;String state;
    assert(!app.button(true,10,120310)&&!app.button(false,11,120310));
    assert(!app.pairingDisplayed("pair-final",2,12)&&!app.pairingUi(120310,state));
    assert(app.bindingPrincipal(token,principal)==503);
    cancel.path="/api/pairing/pair-final";
    auto busyCancel=app.pairingHttp(cancel,120310);
    assert(busyCancel.status==503&&strstr(busyCancel.bytes.c_str(),"maintenance_busy"));
    app.processConfirmation(120310);assert(mutations==atWrite);
    {std::lock_guard<std::mutex> guard(writeMutex);pauseWrite=false;releaseWrite=true;writeCv.notify_all();}
    worker.join();
    assert(mutations>beforePair&&app.bindingPrincipal(token,principal)==200);
    unsigned pairedWrites=mutations;app.processConfirmation(120311);assert(mutations==pairedWrites);
    puts("concurrent pairing: blocked worker save excludes UI, duplicate worker, principal and cancellation; completes once after release");
    puts("pair confirmation: UI never writes; stale/cancelled/expired approvals rejected; worker Busy retries commit once");
    uint8_t session[16]={1};uint64_t number=0;std::string nonce;
    auto send=[&](unsigned op,const char *path,const std::string &payload,const char *id="",const char *offset=""){
        CompactFrameHeader h;h.op=op;h.requestNo=++number;h.payloadLen=payload.size();memcpy(h.session,session,16);
        uint8_t header[48];assert(compactFrameEncode(h,header));
        std::string wire((const char *)header,48);wire+=payload;
        Ap01HttpRequest request{};request.method="POST";request.path=path;request.token=token;request.deviceToken=token;
        request.contentType="application/vnd.codex-status.frame";request.body=(const uint8_t *)wire.data();request.length=wire.size();
        request.nonce=nonce.c_str();request.requestId=id;request.offset=offset;
        unsigned before=mutations;occupied=true;
        auto reply=app.businessHttp(request,130400+number);
        if(op!=1){
            assert(reply.status==503&&!reply.frame&&strstr(reply.bytes.c_str(),"maintenance_busy"));
            assert(mutations==before);
            occupied=false;reply=app.businessHttp(request,130400+number);
        }else assert(mutations==before); // Status remains available during contention.
        occupied=false;
        if(reply.status!=200)fprintf(stderr,"scoped op %u: %.*s\n",op,int(reply.bytes.length()-48),reply.bytes.c_str()+48);
        assert(reply.status==200&&reply.frame);
        CompactFrameHeader response;assert(compactFrameDecode((const uint8_t *)reply.bytes.c_str(),reply.bytes.length(),response,4096));
        memcpy(session,response.session,16);
        if(op!=1){
            unsigned after=mutations;auto context=std::string(business.context());
            auto replay=app.businessHttp(request,130500+number);
            assert(replay.status==reply.status&&replay.bytes.length()==reply.bytes.length());
            assert(!memcmp(replay.bytes.c_str(),reply.bytes.c_str(),reply.bytes.length()));
            assert(mutations==after&&context==business.context());
        }
        return std::string(reply.bytes.c_str()+48,reply.bytes.length()-48);
    };
    auto status=send(1,"/api/status","{}");
    LocalJsonAllocator allocator;JsonDocument doc(&allocator);assert(!deserializeJson(doc,status.c_str()));
    nonce=doc["session_nonce"].as<const char *>();
    send(4,"/claim",R"({"device_mac":"AABBCCDDEEFF","bridge_id":"bridge-test"})");
    char crc[9];snprintf(crc,sizeof(crc),"%08x",v2Crc32((const uint8_t *)bundle.data(),bundle.size()));
    std::string envelope=std::string(R"({"bridge_id":"bridge-test","device_mac":"AABBCCDDEEFF","request_id":"scope-bundle","length":)")+std::to_string(bundle.size())+",\"content_crc\":\""+crc+"\"}";
    send(10,"/api/bundle/begin",envelope);
    for(size_t at=0;at<bundle.size();at+=3072){auto offset=std::to_string(at);
        send(11,"/api/bundle/chunk",bundle.substr(at,3072),"scope-bundle",offset.c_str());}
    send(12,"/api/bundle/commit",envelope);
    std::string activate=std::string(R"({"bridge_id":"bridge-test","device_mac":"AABBCCDDEEFF","request_id":"scope-activate","template_id":")")+business.screenId(1)+"\",\"expected_active_context_id\":\""+business.context()+"\"}";
    send(13,"/api/activate",activate);
    assert(business.count()==2&&business.active()==1);
    unsigned before=mutations;std::string context=business.context();bool retry=false;
    occupied=true;assert(!business.localActivate(0,600,&retry)&&retry);
    assert(mutations==before&&context==business.context());
    occupied=false;assert(business.localActivate(0,601,&retry)&&!retry);
    assert(mutations>before&&context!=business.context()&&business.active()==0);
    failEveryWrite=true;assert(!business.localActivate(0,602,&retry)&&!retry);failEveryWrite=false;
    assert(business.writesAllowed());
    puts("local activation: Busy preserves context without writes; retry succeeds; storage failure is not retryable");
    puts("scoped C2 HTTP: status during Busy, authenticated claim/Bundle begin/chunk/commit/activate identical-request retries and mutation-free cached replays passed");
}
int main(int argc,char **argv){
    assert(argc==3);auto ops=disk.ops();ops.prepare=prepare;ops.open=open;ops.write=write;ops.remove=remove;ops.rename=rename;ops.mkdir=mkdir;
    Ap01AppGeneration0041 gate;uint32_t generation=gate.begin();
#ifdef AP01_TEST_DIRECT_FILES
    Ap01AppFilesV3 files(ops,argv[1]);directFiles=&files;
    auto direct=files.table();LittleFSClass fs(direct,argv[1]);
    auto writes=[&](bool allow){return files.writes(allow);};
    assert(fs.begin(false,"/resource",10,"resource")&&!mutations);
    for(const char *suffix:{"/../outside","//outside","/./outside","/x/","/x\\y"}) {
        std::string path=std::string(argv[1])+suffix;
        assert(direct.open(direct.context,path.c_str(),0)<0);
    }
    assert(direct.open(direct.context,"/other-app/file",0)<0);
#else
    Ap01AppFiles0041 files(gate,ops,argv[1]);
    Ap01AppVfsClientV2 client(files.table(generation),argv[1]);
    LittleFSClass fs(client.ops(),argv[1]);
    auto writes=[&](bool allow){return files.writes(generation,allow);};
#endif
    {Ap01Business empty(fs,{nullptr,present},1);assert(empty.begin(0,true));assert(!empty.writesAllowed()&&!mutations);assert(!fs.exists("/bundle"));}
    assert(writes(true));
    {
        Ap01Business seed(fs,{nullptr,present},1);assert(seed.begin(0));String error;std::string bundle=bytes(argv[2]);
        if(!seed.store.bsInstall(String(bundle.c_str()),FW_TARGET_ID,RENDER_TARGET_ID,"before-trial",error)){fprintf(stderr,"install: %s\n",error.c_str());return 1;}
    }
    auto meta=bytes(std::string(argv[1])+"/bundle/state.bin"),content=bytes(std::string(argv[1])+"/bundle/content.bin");assert(!meta.empty()&&!content.empty());
    File held=fs.open("/held.bin","w");assert(held);
    uint8_t large[3073];for(unsigned i=0;i<sizeof(large);++i)large[i]=uint8_t(i);
    assert(held.write(large,sizeof(large))==sizeof(large)&&held.sync());
    File interrupted=fs.open("/interrupted.bin","w");assert(interrupted);
    failWriteAt=mutations+(directFiles?1:2);assert(interrupted.write(large,sizeof(large))==0);
    failWriteAt=0;interrupted.close();
    File partial=fs.open("/interrupted.bin","r");assert(partial.size()==(directFiles?0:1024));partial.close();
    assert(writes(false));unsigned before=mutations;
    assert(held.write(large,1)==0&&!held.sync()&&mutations==before);held.close();
    File readback=fs.open("/held.bin","r");uint8_t actual[sizeof(large)];
    assert(readback.read(actual,sizeof(actual))==sizeof(actual)&&!memcmp(actual,large,sizeof(actual)));
    assert(readback.read()==-1&&readback.seek(1024)&&readback.read()==large[1024]);readback.close();
    assert(!fs.open("/blocked.bin","w")&&!fs.remove("/held.bin")&&!fs.rename("/held.bin","/other.bin"));
    assert(mutations==before);
    mutations=0;frames=0;
    Ap01Business business(fs,{nullptr,present},2);assert(business.begin(100,true));assert(frames==1&&!mutations);
    assert(!strcmp(business.context(),"before-trial")&&!business.writesAllowed());
    assert(!business.localActivate(0,101)&&!mutations);
    LocalJsonAllocator allocator;JsonDocument request(&allocator);String reply;
    for(unsigned op:{2u,10u,11u,12u,13u})assert(business.command(op,request,"nonce",102,nullptr,0,"id","0",reply)==503);
    Ap01Application app(fs,business,{nullptr,random,lock,unlock},"AABBCCDDEEFF",2);
    assert(app.begin());app.businessOnline(true);
    Ap01HttpRequest post{};post.method="POST";post.path="/api/bundle/begin";
    assert(app.businessHttp(post,103).status==503);
    const char body[]=R"({"device_mac":"AABBCCDDEEFF","bridge_id":"bridge-test","name":"trial-test","display_code":"1234","binding_token":"0123456789abcdef0123456789abcdef","request_id":"pair-test","boot_id":2,"pairing_revision":0})";
    post.path="/api/pairing";post.body=(const uint8_t *)body;post.length=strlen(body);post.token="";
    auto pairing=app.pairingHttp(post,104);assert(pairing.status>=400&&strstr(pairing.bytes.c_str(),"maintenance_busy"));
    networkHttp(app);
    assert(!mutations&&meta==bytes(std::string(argv[1])+"/bundle/state.bin")&&content==bytes(std::string(argv[1])+"/bundle/content.bin"));
    // Durable success is the caller's prerequisite for this explicit transition.
    assert(writes(true));
    assert(business.syncWritePermission(200,true)&&business.writesAllowed());assert(mutations>0);
    unsigned approved=mutations;std::string context=business.context();
    assert(business.syncWritePermission(201,true)&&mutations==approved&&context==business.context());
    assert(writes(false)&&business.syncWritePermission(202,false)&&!business.writesAllowed());
    assert(!business.localActivate(0,203)&&mutations==approved);
    assert(writes(true)&&business.syncWritePermission(204,true)&&business.writesAllowed());
    {Ap01Business failing(fs,{nullptr,present},3);assert(failing.begin(205,true));
     failEveryWrite=true;assert(!failing.syncWritePermission(206,true)&&!failing.writesAllowed());
     unsigned failedAt=mutations;failEveryWrite=false;
     assert(!failing.syncWritePermission(207,true)&&mutations==failedAt&&!failing.writesAllowed());}
    assert(strcmp(business.context(),"before-trial")&&meta!=bytes(std::string(argv[1])+"/bundle/state.bin"));
#ifdef AP01_TEST_DIRECT_FILES
    // Known coordination gap: transient platform contention is indistinguishable
    // from storage failure during writable restoration. Preserve this evidence
    // until an operation-level admission contract replaces per-call retries.
    {
        bool occupied=true;
        Ap01AppWriteGateV3 coordinated(&occupied,[](void *p){return !*(bool *)p;},[](void *){});
        assert(coordinated.writes(true));
        Ap01AppFilesV3 scoped(ops,argv[1]);scoped.bindGate(coordinated);
        auto table=scoped.table();LittleFSClass coordinatedFs(table,argv[1]);
        Ap01Business restoring(coordinatedFs,{nullptr,present},4);
        assert(restoring.begin(208,true));
        unsigned beforeContention=mutations;
        auto beforeMeta=bytes(std::string(argv[1])+"/bundle/state.bin");
        assert(!restoring.syncWritePermission(209,true)&&!restoring.writesAllowed());
        assert(mutations==beforeContention&&beforeMeta==bytes(std::string(argv[1])+"/bundle/state.bin"));
        occupied=false;
        assert(!restoring.syncWritePermission(210,true)&&!restoring.writesAllowed());
        assert(mutations==beforeContention);
        puts("negative control: uncoordinated legacy restore latches contention without any backend mutation");
        // The scoped candidate admits before calling any business code. Busy
        // never invokes begin(), so it cannot latch writeResumeFailed.
        scoped.threadIdentity(nullptr,[](void *)->uintptr_t{static thread_local int id;return (uintptr_t)&id;});
        Ap01Business admitted(coordinatedFs,{nullptr,present},5);assert(admitted.begin(211,true));
        struct Resume {Ap01Business *business;unsigned calls=0;} resume{&admitted};
        auto restore=[](void *p)->int32_t{auto &r=*(Resume *)p;++r.calls;
            return r.business->syncWritePermission(212,true)?0:-1;};
        occupied=true;int32_t outcome=99;
        assert(!scoped.writeScope(restore,&resume,outcome)&&!resume.calls&&outcome==99);
        assert(!admitted.writesAllowed()&&mutations==beforeContention);
        occupied=false;directFiles=&scoped;
        assert(scoped.writeScope(restore,&resume,outcome)&&resume.calls==1&&outcome==0);
        assert(admitted.writesAllowed()&&mutations>beforeContention);
        Ap01Business ioFailure(coordinatedFs,{nullptr,present},6);assert(ioFailure.begin(213,true));
        Resume failedResume{&ioFailure};failEveryWrite=true;
        assert(scoped.writeScope(restore,&failedResume,outcome)&&outcome==-1&&!ioFailure.writesAllowed());
        unsigned afterFailure=mutations;failEveryWrite=false;
        assert(scoped.writeScope(restore,&failedResume,outcome)&&outcome==-1&&mutations==afterFailure);
        directFiles=&files;
        puts("scoped admission: busy leaves real business untouched; retry restores Bundle and write permission (host thread identity)");
        struct Admission {Ap01PlatformApiV3 api{};Ap01AppFilesV3 *files;unsigned calls=0;} admission{{},&scoped};
        admission.api.abi_major=3;admission.api.abi_minor=1;admission.api.struct_bytes=sizeof(admission.api);
        admission.api.write_scope=[](void *p,int32_t (*callback)(void *),void *argument,int32_t *result)->int32_t{
            auto &a=*(Admission *)p;++a.calls;
            return a.files->writeScope(callback,argument,*result)?AP01_APP_V3_OK:AP01_APP_V3_PENDING;
        };
        Ap01BusinessPort resumePort{&admission,present,nullptr,nullptr,
            [](void *p,int32_t (*callback)(void *),void *argument,int32_t *result)->int32_t{
                auto &a=*(Admission *)p;return ap01WriteScopeV3(&a.api,p,callback,argument,result);
            }};
        Ap01Business integrated(coordinatedFs,resumePort,7);assert(integrated.begin(214,true));
        unsigned unchanged=mutations;occupied=true;
        for(unsigned i=0;i<5;++i)assert(integrated.syncWritePermission(215+i,true)&&!integrated.writesAllowed());
        assert(mutations==unchanged&&admission.calls==5);
        occupied=false;directFiles=&scoped;
        assert(integrated.syncWritePermission(220,true)&&integrated.writesAllowed());
        unsigned restored=mutations;assert(restored>unchanged&&admission.calls==6);
        assert(integrated.syncWritePermission(221,true)&&mutations==restored&&admission.calls==6);
        Ap01Business integratedFailure(coordinatedFs,resumePort,8);assert(integratedFailure.begin(222,true));
        failEveryWrite=true;assert(!integratedFailure.syncWritePermission(223,true));failEveryWrite=false;
        unsigned failedCalls=admission.calls,failedMutations=mutations;
        assert(!integratedFailure.syncWritePermission(224,true)&&admission.calls==failedCalls&&mutations==failedMutations);
        Ap01ApplicationPort httpPort{&admission,random,lock,unlock};httpPort.writeScope=resumePort.writeScope;
        Ap01Application httpApp(coordinatedFs,integrated,httpPort,"AABBCCDDEEFF",7);
        assert(httpApp.begin());httpApp.businessOnline(true);
        scopedHttp(httpApp,integrated,occupied,bytes(argv[2]));
        directFiles=&files;
        puts("production business write admission: five Busy polls preserve readonly health, later C API admission restores once; real storage failure remains latched");
    }
    assert(largestWrite>=3073); // One direct call, not the old 1KB transport.
    int handles[16];std::string path=std::string(argv[1])+"/held.bin";
    for(auto &h:handles){h=direct.open(direct.context,path.c_str(),0);assert(h>0);}
    assert(direct.open(direct.context,path.c_str(),0)<0);
    for(int h:handles)assert(!direct.close(direct.context,h));
    int fresh=direct.open(direct.context,path.c_str(),0);assert(fresh>handles[15]);
    assert(direct.read(direct.context,handles[0],actual,1)<0);
    assert(direct.write(direct.context,fresh,large,1)<0); // Read descriptor cannot mutate.
    assert(!direct.close(direct.context,fresh));
    directFiles=nullptr;
    puts("direct VFS: real Bundle/App restore and render, path/handle/quota/write-gate checks, no invoke or file chunking passed");
#else
    gate.close();assert(files.drain());
#endif
#ifdef AP01_TEST_DIRECT_FILES
    puts("real App direct file/network tables: 8 HTTP fault scenarios, 1300-byte UDP, maintenance port denial, stale/type-invalid handles, read-only Bundle/render/pairing and writable restart passed");
#else
    puts("real App over file C service; 8 HTTP parser/network client scenarios: fragmented read/write, AGAIN, 3000-byte body, EOF, read/write deadline, partial reply failure, closed generation; read-only Bundle/render/pairing and writable restart passed");
#endif
}
