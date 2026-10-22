#include "native_wifi_switch_0041.h"
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <vector>
struct Fake {
    char current[33]="Old", password[65]="synthetic-old";
    bool ip=false,journalPresent=false,corrupt=false,blocked=false,failTrial=false,failPersist=false,failRestore=false,failClear=false;
    unsigned applies=0,persists=0,journals=0,clears=0;
    Ap01WifiProfile0041 old;
    std::vector<uint8_t> bytes=std::vector<uint8_t>(114);
    Fake(){
        memcpy(bytes.data(),"WPL1",4);bytes[4]=1;bytes[8]=1;bytes[16]=3;memcpy(bytes.data()+17,"New",3);
        bytes[49]=13;memcpy(bytes.data()+50,"synthetic-new",13);
        unsigned c=~0u;for(unsigned i=0;i<bytes.size();++i){c^=i>=12&&i<16?0:bytes[i];for(unsigned k=0;k<8;++k)c=(c>>1)^(0xedb88320u&(0u-(c&1)));}
        c=~c;for(unsigned k=0;k<4;++k)bytes[12+k]=c>>(8*k);
    }
    static int currentRead(void *p,char *s,unsigned,char *pw,unsigned){auto &f=*(Fake*)p;strcpy(s,f.current);strcpy(pw,f.password);return 0;}
    static int load(void *p,uint8_t *b,unsigned n){auto &f=*(Fake*)p;assert(n>=f.bytes.size());memcpy(b,f.bytes.data(),f.bytes.size());return f.bytes.size();}
    static bool busy(void *p){return ((Fake*)p)->blocked;}
    static int apply(void *p,const Ap01WifiProfile0041 &v,bool persistent){auto &f=*(Fake*)p;++f.applies;
        if(persistent){++f.persists;if(f.failPersist){f.failPersist=false;return -EIO;}}
        if(!strcmp(v.ssid,"New")&&f.failTrial)return -EIO;
        if(!strcmp(v.ssid,"Old")&&f.failRestore)return -EIO;
        strcpy(f.current,v.ssid);strcpy(f.password,v.password);return 0;}
    static bool online(void *p,const char *s){auto &f=*(Fake*)p;return f.ip&&!strcmp(f.current,s);}
    static int journal(void *p,const Ap01WifiProfile0041 *v){auto &f=*(Fake*)p;if(v){++f.journals;f.old=*v;f.journalPresent=true;}
        else{++f.clears;f.journalPresent=false;if(f.failClear)return -EIO;}return 0;}
    static int recover(void *p,Ap01WifiProfile0041 &v){auto &f=*(Fake*)p;if(f.corrupt)return -EILSEQ;if(!f.journalPresent)return -ENOENT;v=f.old;return 0;}
    Ap01WifiSwitchPort0041 port(){return {this,{this,currentRead,load,nullptr,busy},apply,online,journal,recover};}
};
int main(){
    using S=Ap01WifiSwitch0041;
    {Fake f;S s(f.port());s.begin(0);assert(s.state()==S::Idle&&!s.busy());
     assert(s.request("")==-EINVAL);assert(!s.request("New")&&s.busy());assert(s.request("New")==-EBUSY);
     assert(s.feedback(100001)==S::ResultUnknown&&s.busy()&&s.request("New")==-EBUSY);
     s.tick(1);assert(s.state()==S::Connecting&&f.applies==1&&!f.persists&&!f.journalPresent);
     s.tick(45000);assert(s.state()==S::Connecting);s.tick(45001);assert(s.state()==S::Restoring&&!strcmp(f.current,"Old"));
     f.ip=true;s.tick(45002);assert(s.state()==S::Failed&&!s.busy());
     assert(!s.request("Old"));s.tick(45003);assert(s.state()==S::Connected&&f.applies==2);}
    {Fake f;S s(f.port());s.begin(0);assert(!s.request("New"));s.tick(1);f.ip=true;s.tick(2);
     assert(s.state()==S::Connected&&!strcmp(f.current,"New")&&f.persists==1&&f.journals==1&&f.clears==1&&!f.journalPresent);}
    {Fake f;S s(f.port());s.begin(0);s.request("New");s.tick(1);f.ip=true;f.failPersist=true;s.tick(2);
     assert(s.state()==S::Restoring&&!strcmp(f.current,"Old")&&f.persists==2&&!f.journalPresent);s.tick(3);assert(s.state()==S::Failed);}
    {Fake f;strcpy(f.old.ssid,"Old");strcpy(f.old.password,"synthetic-old");f.journalPresent=true;strcpy(f.current,"New");
     S s(f.port());s.begin(0);assert(s.state()==S::Restoring&&f.persists==1&&!f.journalPresent&&!strcmp(f.current,"Old"));f.ip=true;s.tick(1);assert(s.state()==S::Failed);}
    {Fake f;f.corrupt=true;S s(f.port());s.begin(0);assert(s.state()==S::RecoveryFailed&&s.request("New")==-EIO&&!f.applies);}
    {Fake f;S s(f.port());s.begin(0);f.blocked=true;s.request("New");s.tick(1);assert(s.state()==S::Failed&&!f.applies);}
    {Fake f;S s(f.port());s.begin(0);f.failTrial=true;s.request("New");s.tick(1);assert(s.state()==S::Restoring&&!strcmp(f.current,"Old"));s.tick(45001);assert(s.state()==S::Failed);}
    {Fake f;S s(f.port());s.begin(0);f.failTrial=f.failRestore=true;s.request("New");s.tick(1);assert(s.state()==S::RecoveryFailed);}
    {Fake f;S s(f.port());s.begin(0);s.request("Gone");s.tick(1);assert(s.state()==S::Failed&&!f.applies);}
    {Fake f;S s(f.port());s.begin(0);s.request("New");s.tick(1);f.ip=true;f.failClear=true;s.tick(2);
     assert(s.state()==S::RecoveryFailed&&f.persists==1&&!strcmp(f.current,"New"));}
    {Fake f;
     // The saved credential for the running SSID may be edited without applying it.
     f.bytes.resize(212);f.bytes[8]=2;f.bytes[114]=3;
     memcpy(f.bytes.data()+115,"Old",3);f.bytes[147]=12;
     memcpy(f.bytes.data()+148,"saved-edited",12);
     unsigned crc=~0u;for(unsigned i=0;i<f.bytes.size();++i){crc^=i>=12&&i<16?0:f.bytes[i];for(unsigned k=0;k<8;++k)crc=(crc>>1)^(0xedb88320u&(0u-(crc&1)));}
     crc=~crc;for(unsigned k=0;k<4;++k)f.bytes[12+k]=crc>>(8*k);
     S s(f.port());s.begin(0);assert(!s.request("New"));s.tick(1);
     s.tick(45001);assert(s.state()==S::Restoring);
     assert(!strcmp(f.password,"synthetic-old"));}
    puts("Wi-Fi switch: trial/IP timeout/success, current no-op, busy, missing SSID, partial commit rollback, restart and corrupt recovery passed");
}
