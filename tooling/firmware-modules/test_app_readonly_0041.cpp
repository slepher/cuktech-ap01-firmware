// Real business/BundleStore/application code, mutation-counting host VFS.
#include "application.h"
#include "local_json_allocator.h"
#include "platform_target.h"
#include "test_app_file_store_0041.h"
#include "app_files_0041.h"
#include "app_vfs_client_v2.h"
#include "app_files_v3.h"
#include "app_services_0041.h"
#include "app_network_client_v2.h"
#include "app_network_client_v3.h"
#include "app_network_v3.h"
#include "http.h"
#include <fstream>
#include <iterator>
#include <string>
static Disk disk;static unsigned mutations=0,frames=0,failWriteAt=0;
static Ap01AppFilesV3 *directFiles=nullptr;
static size_t largestWrite=0;static bool failEveryWrite=false;
static int prepare(void *,const char *){++mutations;return 0;}
static int open(void *,const char *path,unsigned mode){if(mode)++mutations;return Disk::open(&disk,path,mode);}
static int write(void *,int fd,const void *p,size_t n){
    ++mutations;if(n>largestWrite)largestWrite=n;
    if(directFiles)assert(!directFiles->writes(false)); // Cannot freeze an in-flight write.
    if(failEveryWrite||mutations==failWriteAt)return -1;return Disk::write(&disk,fd,p,n);
}
static int remove(void *,const char *p){++mutations;return Disk::remove(&disk,p);}
static int rename(void *,const char *a,const char *b){++mutations;return Disk::rename(&disk,a,b);}
static int mkdir(void *,const char *p){++mutations;return ::mkdir(p,0700);}
static bool present(void *,uint8_t *bytes,uint32_t){if(bytes){++frames;delete[] bytes;}return true;}
static bool random(void *,uint8_t *bytes,size_t n){memset(bytes,7,n);return true;}
static bool lock(void *){return true;}
static void unlock(void *){}
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
