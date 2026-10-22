// Actual native adapter + core, with explicit ROM/PSM/VFS API boundary fixtures.
// No App, real RF, flash, device credentials, config_router or identity writes.
#include "native_wifi_switch_0041.h"
#include "native_wifi_profiles_port_0041.h"
#include "native_vfs_0041.h"
#include <cassert>
#include <cerrno>
#include <cstring>
#include <cstdio>
#include <map>
#include <string>
#include <vector>
struct PowerCut {};
struct Model {
    std::map<std::string,std::vector<uint8_t>> files;
    std::map<std::string,std::string> psm{{"password","old-secret"},{"ssid","Old"},{"did","preserved"},{"token","synthetic"},{"binding","preserved"}};
    std::string cached="Old",password="old-secret",actual="Old";
    uint32_t ip=0;bool associated=false,busy=false,failStart=false,failStop=false;
    bool failSsid=false,cutSsid=false,loseRename=false,failRename=false,failDelete=false,loseDelete=false,failEncrypt=false;
    unsigned starts=0,stops=0,sets=0,journalBytes=0;
} *model;
static int current(void *,char *s,unsigned,char *p,unsigned){strcpy(s,model->cached.c_str());strcpy(p,model->password.c_str());return 0;}
static bool blocked(void *){return model->busy;}
static std::string key(const char *space,const char *name){return std::string("/data/e#")+space+"."+name;}
static int present(void *,const char *p){return model->files.count(p)?1:0;}
static int erase(void *,const char *p){if(model->failDelete)return -EIO;model->files.erase(p);return model->loseDelete?-EIO:0;}
static int renameFile(void *,const char *a,const char *b){if(model->failRename)return -EIO;auto f=model->files.find(a);if(f==model->files.end())return -ENOENT;model->files[b]=f->second;model->files.erase(f);return model->loseRename?-EIO:0;}
Ap01VfsOps ap01RomVfs(){Ap01VfsOps p{};p.exists=present;p.remove=erase;p.rename=renameFile;return p;}
static int encryptedSet(const char *space,const char *name,const void *bytes,uint32_t n){
    assert(!strcmp(space,"ap01_wifi")&&!strcmp(name,"rollback.new"));
    if(model->failEncrypt)return -EIO;
    auto *b=(const uint8_t *)bytes;model->files[key(space,name)]={b,b+n};model->journalBytes=n;return (n/16+1)*16;
}
static int encryptedGet(const char *space,const char *name,void *out,uint32_t cap){
    auto f=model->files.find(key(space,name));if(f==model->files.end())return -ENOENT;
    if(f->second.size()>cap)return -E2BIG;memcpy(out,f->second.data(),f->second.size());return f->second.size();
}
static int set(const char *space,const char *name,const char *value){
    assert(!strcmp(space,"network")&&(!strcmp(name,"ssid")||!strcmp(name,"password")));
    ++model->sets;if(!strcmp(name,"ssid")){if(model->cutSsid)throw PowerCut{};if(model->failSsid){model->failSsid=false;return -EIO;}}
    model->psm[name]=value;return strlen(value);
}
static int get(const char *space,const char *name,char *out,int cap){assert(!strcmp(space,"network"));auto v=model->psm.at(name);assert(v.size()<unsigned(cap));strcpy(out,v.c_str());return v.size();}
static int stop(){++model->stops;return model->failStop?-EIO:0;}
static void cache(const char *s,const char *p,int enabled){assert(enabled==1);model->cached=s;model->password=p;}
static int start(){++model->starts;return model->failStart?-EIO:0;}
static int socketOpen(int family,int type,int proto){assert(family==2&&type==2&&proto==0);return 17;}
static int socketClose(int fd){assert(fd==17);return 0;}
static int essid(int fd,const char *iface,char *out,uint8_t *associated){assert(fd==17&&!strcmp(iface,"wlan0"));strcpy(out,model->actual.c_str());*associated=model->associated;return 0;}
static int ipv4(int fd,const char *iface,int cmd,uint32_t *out){assert(fd==17&&!strcmp(iface,"wlan0")&&cmd==0x701);*out=model->ip;return 0;}
static void *resolve(uintptr_t address){
    switch(address){
    case 0xa005f6d8:return (void *)encryptedGet;case 0xa005f8d8:return (void *)encryptedSet;
    case 0xa0061bc2:return (void *)set;case 0xa00616de:return (void *)get;
    case 0xa00699c4:return (void *)stop;case 0xa006bfdc:return (void *)cache;case 0xa0068a7a:return (void *)start;
    case 0xa00268c4:return (void *)socketOpen;case 0xa0026888:return (void *)socketClose;
    case 0xa00756c2:return (void *)essid;case 0xa00c6ba0:return (void *)ipv4;
    default:assert(false&&"unapproved original API");return nullptr;}
}
// Imported after boundary fixtures: this is the production adapter, not a copy.
#define AP01_WIFI_SWITCH_ROM_FN(a,t) ((t)resolve(a))
#include "native_wifi_switch_port_0041.cpp"
Ap01WifiProfilesPort ap01WifiProfilesNativePort0041(void *p,bool (*busy)(void *)) {return {p,current,nullptr,nullptr,busy};}
static Ap01WifiProfile0041 profile(const char *s="New",const char *p="new-secret"){Ap01WifiProfile0041 v;strcpy(v.ssid,s);strcpy(v.password,p);return v;}
static void protect(const Model &m){assert(m.psm.at("did")=="preserved"&&m.psm.at("token")=="synthetic"&&m.psm.at("binding")=="preserved");}
int main(){
    const char *saved="/data/e#ap01_wifi.rollback";
    {Model f;model=&f;auto p=ap01WifiSwitchNativePort0041(nullptr,blocked);
     Ap01WifiProfile0041 empty;assert(p.recover(nullptr,empty)==-ENOENT);
    }
    {Model f;model=&f;auto p=ap01WifiSwitchNativePort0041(nullptr,blocked);auto v=profile();
     assert(!p.apply(nullptr,v,false)&&f.sets==0&&f.starts==1&&f.cached=="New"&&f.psm["ssid"]=="Old");
     f.actual="Old";f.associated=true;f.ip=0x01020304;assert(!p.online(nullptr,"New"));
     f.actual="New";f.ip=0;assert(!p.online(nullptr,"New"));f.ip=UINT32_MAX;assert(!p.online(nullptr,"New"));
     f.ip=0x01020304;assert(p.online(nullptr,"New"));f.associated=false;assert(!p.online(nullptr,"New"));
     assert(!p.apply(nullptr,v,true)&&f.starts==1&&f.sets==2&&f.psm["ssid"]=="New");protect(f);}
    for(unsigned length:{1u,8u,32u}){Model f;model=&f;auto p=ap01WifiSwitchNativePort0041(nullptr,blocked);
     std::string s(length,'S'),pw(length==32?64:8,'P');auto old=profile(s.c_str(),pw.c_str());
     assert(!p.journal(nullptr,&old)&&f.journalBytes==10+s.size()+pw.size());Ap01WifiProfile0041 actual;
     assert(!p.recover(nullptr,actual)&&!strcmp(actual.ssid,old.ssid)&&!strcmp(actual.password,old.password));
     auto good=f.files.at(saved);for(unsigned n=0;n<good.size();++n){f.files[saved]={good.begin(),good.begin()+n};assert(p.recover(nullptr,actual)<0);}
     f.files[saved]=good;f.files[saved][7]^=1;assert(p.recover(nullptr,actual)==-EILSEQ);protect(f);}
    for(bool fail:{false,true}){Model f;model=&f;f.loseRename=!fail;f.failRename=fail;auto p=ap01WifiSwitchNativePort0041(nullptr,blocked);auto old=profile("Old","old-secret");assert((p.journal(nullptr,&old)==0)==!fail);protect(f);}
    {Model f;model=&f;auto p=ap01WifiSwitchNativePort0041(nullptr,blocked);auto old=profile("Old","old-secret");assert(!p.journal(nullptr,&old));
     f.failSsid=true;assert(p.apply(nullptr,profile(),true)==-EIO&&f.psm["password"]=="new-secret"&&f.psm["ssid"]=="Old");
     Ap01WifiSwitch0041 restart(p);restart.begin(10);assert(restart.state()==Ap01WifiSwitch0041::Restoring&&f.psm["password"]=="old-secret"&&f.psm["ssid"]=="Old"&&!f.files.count(saved));
     f.actual="Old";f.associated=true;f.ip=1;restart.tick(11);assert(restart.state()==Ap01WifiSwitch0041::Failed);protect(f);}
    {Model f;model=&f;auto p=ap01WifiSwitchNativePort0041(nullptr,blocked);auto old=profile("Old","old-secret");assert(!p.journal(nullptr,&old));
     f.cutSsid=true;try{p.apply(nullptr,profile(),true);assert(false);}catch(PowerCut &){}f.cutSsid=false;
     Ap01WifiSwitch0041 restart(p);restart.begin(20);assert(f.psm["password"]=="old-secret"&&f.psm["ssid"]=="Old");protect(f);}
    {Model f;model=&f;auto p=ap01WifiSwitchNativePort0041(nullptr,blocked);auto old=profile("Old","old-secret");assert(!p.journal(nullptr,&old));f.failDelete=true;
     Ap01WifiSwitch0041 restart(p);restart.begin(30);assert(restart.state()==Ap01WifiSwitch0041::RecoveryFailed&&f.files.count(saved));protect(f);}
    {Model f;model=&f;auto p=ap01WifiSwitchNativePort0041(nullptr,blocked);auto old=profile("Old","old-secret");f.failEncrypt=true;assert(p.journal(nullptr,&old)<0&&!f.files.count(saved));protect(f);}
    puts("native port: exact driver ABI, actual SSID+IP, volatile/persistent separation, 1/typical/max journal, every truncation/CRC, lost rename ACK, partial PSM/power-cut restart, cleanup/write failure and identity preservation passed");
}
