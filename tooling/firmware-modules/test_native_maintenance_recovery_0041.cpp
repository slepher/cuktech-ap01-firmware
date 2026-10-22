// Reuse the real filesystem/flash fixture, without linking any application.
#define AP01_MAINTENANCE_ONLY_TEST 1
#define main existing_maintenance_tests
#include "test_native_maintenance_0041.cpp"
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
    const std::string mark=R"({"device_mac":"AABBCCDDEEFF","request_id":"stable","slot":0,"expected_stable_revision":0,"confirm":true})";
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
        if(scenario==1)fw.tick(30001); // Failed application health must not bar repair.
        if(scenario==2){f.healthy=true;fw.tick(1);fw.tick(9001);}
        if(scenario==4)f.unknown=true;
        auto body=beginBody(std::string(296,'x'));
        auto begin=request("POST","/api/firmware/begin",body);
        auto reply=fw.handle(begin,"bridge-test",30002);
        if(scenario==4){assert(reply.status==503&&f.opens==0);unsigned n=f.selections;
            assert(fw.handle(begin,"bridge-test",30003).status==503&&f.selections==n);continue;}
        assert(reply.status==200&&f.opens==1&&f.selected==1);
        fw.tick(50000);assert(f.selected==1); // Old health timer cannot override manual maintenance.
        assert(fw.handle(request("DELETE","/api/firmware/fw-test",{}),"bridge-test",50001).status==200);
        f.valid=false;assert(fw.handle(request("POST","/api/firmware/switch",change),"bridge-test",50002).status==409);
        f.valid=true;assert(fw.handle(request("POST","/api/firmware/switch",change),"bridge-test",50003).status==200&&f.selected==0);
        unsigned n=f.selections;assert(fw.handle(request("POST","/api/firmware/switch",change),"bridge-test",50004).status==200&&f.selections==n);
    }
    puts("maintenance recovery: stale/armed/timed-out/healthy stable records, safe boot selection, invalid image and unknown selection replay passed");
}
