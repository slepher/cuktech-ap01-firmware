// Reuse the real filesystem/flash fixture, without linking any application.
#define AP01_MAINTENANCE_ONLY_TEST 1
#define main existing_maintenance_tests
#include "test_native_maintenance.cpp"
#undef main

struct RecoverySlots:Flash {
    int running=0,selected=0; bool healthy=false,valid=true;
    unsigned selections=0;
    Ap01SlotImage image;
    static int current(void *p){return ((RecoverySlots*)p)->running;}
    static bool health(void *p){return ((RecoverySlots*)p)->healthy;}
    static bool inspect(void *p,unsigned,Ap01SlotImage &out){auto &f=*(RecoverySlots*)p;out=f.image;return f.valid;}
    static int select(void *p,unsigned slot){auto &f=*(RecoverySlots*)p;++f.selections;if(f.unknown)return -1;f.selected=slot;return 1;}
    static bool openChecked(void *p,uint32_t n){auto &f=*(RecoverySlots*)p;assert(f.selected==f.running);return Flash::begin(p,n);}
    Ap01FirmwarePort callbacks(){auto p=port();p.open=openChecked;p.runningSlot=current;p.inspectSlot=inspect;p.selectSlot=select;p.bootHealthy=health;return p;}
};
int main(int argc,char **argv){
    assert(argc==2);Disk disk;
    Ap01VfsOps io{&disk,prepare,openFile,closeFile,readFile,writeFile,seekFile,sizeFile,exists,mkdirFile,removeFile,renameFile,capacity};
    const std::string mark=R"({"device_mac":"AABBCCDDEEFF","request_id":"stable","slot":0,"confirm":true})";
    const std::string change=R"({"device_mac":"AABBCCDDEEFF","request_id":"manual","target_slot":0,"expected_revision":1})";
    for(unsigned scenario=0;scenario<6;++scenario){
        std::string folder=std::string(argv[1])+"/maintenance-"+std::to_string(scenario);
        LittleFSClass fs(io,folder.c_str());RecoverySlots f;f.image.length=296;f.image.crc=1234;
        memcpy(f.image.build,f.build,33);
        {Ap01Firmware fw(fs,f.callbacks(),"AABBCCDDEEFF");assert(fw.begin());assert(fw.handle(request("POST","/api/firmware/stable",mark),"bridge-test",1).status==200);}
        f.running=f.selected=1;
        if(scenario==0||scenario==4||scenario==5)++f.image.crc; // Stale optional metadata, valid image.
        Ap01Firmware fw(fs,f.callbacks(),"AABBCCDDEEFF");assert(fw.begin(0));
        if(scenario==5){
            const std::string manual=R"({"device_mac":"AABBCCDDEEFF","request_id":"manual","target_slot":0,"expected_revision":0})";
            assert(fw.handle(request("POST","/api/firmware/switch",manual),"bridge-test",1).status==200&&f.selected==0&&!f.opens);
            continue;
        }
        if(scenario==1)fw.tick(60001); // Failed application health must not bar repair.
        if(scenario==2){f.healthy=true;fw.tick(1);fw.tick(30001);}
        if(scenario==4)f.unknown=true;
        auto body=beginBody(std::string(296,'x'));
        auto begin=request("POST","/api/firmware/begin",body);
        auto reply=fw.handle(begin,"bridge-test",60002);
        if(scenario==4){assert(reply.status==503&&f.opens==0);unsigned n=f.selections;
            assert(fw.handle(begin,"bridge-test",60003).status==503&&f.selections==n);continue;}
        assert(reply.status==200&&f.opens==1&&f.selected==1);
        fw.tick(80000);assert(f.selected==1); // Old health timer cannot override manual maintenance.
        assert(fw.handle(request("DELETE","/api/firmware/fw-test",{}),"bridge-test",80001).status==200);
        f.valid=false;assert(fw.handle(request("POST","/api/firmware/switch",change),"bridge-test",80002).status==409);
        f.valid=true;assert(fw.handle(request("POST","/api/firmware/switch",change),"bridge-test",80003).status==200&&f.selected==0);
        unsigned n=f.selections;assert(fw.handle(request("POST","/api/firmware/switch",change),"bridge-test",80004).status==200&&f.selections==n);
    }
    const char *kinds[]={"base","official_0031","official_0041","official_0055","third_party","app_platform","app_platform"};
    for(unsigned i=0;i<7;++i) {
        std::string folder=std::string(argv[1])+"/policy-"+std::to_string(i);assert(!mkdir(folder.c_str(),0700));
        LittleFSClass fs(io,folder.c_str());RecoverySlots f;f.running=f.selected=1;f.valid=false;
        Ap01Firmware fw(fs,f.callbacks(),"AABBCCDDEEFF");assert(fw.begin());
        auto marked=fw.handle(request("POST","/api/firmware/stable",mark),"bridge-test",1);
        assert(marked.status==200&&strstr(marked.bytes.c_str(),"\"stable_slot\":0"));
        auto body=beginBody(std::string(296,'x'));auto pos=body.find("third_party");body.replace(pos,11,kinds[i]);
        if(i==6)body.insert(body.size()-1,",\"force\":true");
        auto reply=fw.handle(request("POST","/api/firmware/begin",body),"bridge-test",2);
        if(i==5) {
            assert(reply.status==409&&!f.opens&&strstr(reply.bytes.c_str(),"stable_slot_app_platform_requires_force"));
            continue;
        }
        assert(reply.status==200&&f.opens==1);
        if(i<2)assert(!strstr(reply.bytes.c_str(),"warning"));
        else assert(strstr(reply.bytes.c_str(),"warning"));
        auto slots=fw.handle(request("GET","/api/firmware/slots",{}),"bridge-test",3);
        assert(strstr(slots.bytes.c_str(),"\"stable_slot\":0")&&!strstr(slots.bytes.c_str(),"stable_revision"));
    }
    { // Changing/replacing the stable ROM does not revoke the slot assignment.
        std::string folder=std::string(argv[1])+"/fixed";assert(!mkdir(folder.c_str(),0700));
        LittleFSClass fs(io,folder.c_str());RecoverySlots f;
        {Ap01Firmware fw(fs,f.callbacks(),"AABBCCDDEEFF");assert(fw.begin());assert(fw.handle(request("POST","/api/firmware/stable",mark),"bridge-test",1).status==200);}
        f.running=f.selected=1;f.valid=false;f.image.length=777;f.image.crc=999;
        Ap01Firmware fw(fs,f.callbacks(),"AABBCCDDEEFF");assert(fw.begin());
        auto slots=fw.handle(request("GET","/api/firmware/slots",{}),"bridge-test",1);
        assert(f.selected==0&&strstr(slots.bytes.c_str(),"\"stable_slot\":0")&&strstr(slots.bytes.c_str(),"armed"));
    }
    for(unsigned scenario=0;scenario<3;++scenario) {
        std::string folder=std::string(argv[1])+"/window-"+std::to_string(scenario);assert(!mkdir(folder.c_str(),0700));
        LittleFSClass fs(io,folder.c_str());RecoverySlots f;
        {Ap01Firmware fw(fs,f.callbacks(),"AABBCCDDEEFF");assert(fw.begin());assert(fw.handle(request("POST","/api/firmware/stable",mark),"bridge-test",1).status==200);}
        f.running=f.selected=1;f.healthy=scenario!=2;
        Ap01Firmware fw(fs,f.callbacks(),"AABBCCDDEEFF");assert(fw.begin(0)&&f.selected==0);
        auto status=[&](uint64_t now){return text(fw.handle(request("GET","/api/firmware/slots",{}),"bridge-test",now).bytes);};
        auto initial=status(0);assert(initial.find("\"health_window_ms\":30000")!=std::string::npos&&initial.find("\"trial_timeout_ms\":60000")!=std::string::npos);
        if(scenario==0){assert(status(29999).find("armed")!=std::string::npos&&f.selected==0);assert(status(30000).find("healthy_locked")!=std::string::npos&&f.selected==1);}
        if(scenario==1){f.healthy=false;fw.tick(15000);f.healthy=true;fw.tick(16000);assert(status(45999).find("armed")!=std::string::npos&&f.selected==0);assert(status(46000).find("healthy_locked")!=std::string::npos&&f.selected==1);}
        if(scenario==2){assert(status(59999).find("armed")!=std::string::npos);assert(status(60000).find("retained_stable")!=std::string::npos&&f.selected==0);f.healthy=true;fw.tick(100000);assert(f.selected==0);}
    }
    puts("maintenance recovery: stale/armed/timed-out/healthy stable records, safe boot selection, invalid image and unknown selection replay passed");
}
