#include "native_wifi_switch_0041.h"
#include "native_vfs_0041.h"
#include "native_wifi_profiles_port_0041.h"
#include <errno.h>
#include "native_integrity_0041.h"
#include <string.h>
#ifndef AP01_WIFI_SWITCH_ROM_FN
#define AP01_WIFI_SWITCH_ROM_FN(a,t) ((t)(uintptr_t)(a))
#endif
#define ROM AP01_WIFI_SWITCH_ROM_FN
namespace {
constexpr const char *Stored="/data/e#ap01_wifi.rollback";
constexpr const char *Temporary="/data/e#ap01_wifi.rollback.new";

int readJournal(void *,Ap01WifiProfile0041 &out){
    auto io=ap01RomVfs();int present=io.exists(io.context,Stored);
    if(!present)return -ENOENT;if(present!=1)return -EIO;
    uint8_t bytes[106]={}; // 10 + maximum SSID32/password64.
    int n=ROM(0xa005f6d8,int (*)(const char *,const char *,void *,uint32_t))("ap01_wifi","rollback",bytes,sizeof(bytes));
    if(n<10||n>106||memcmp(bytes,"WNR1",4)||!bytes[4]||bytes[4]>32||bytes[5]>64||n!=10+bytes[4]+bytes[5])return -EILSEQ;
    unsigned at=n-4;uint32_t check=0;for(unsigned i=0;i<4;++i)check|=uint32_t(bytes[at+i])<<(8*i);
    if(check!=ap01_native_crc32(bytes,at)||memchr(bytes+6,0,bytes[4]+bytes[5]))return -EILSEQ;
    out=Ap01WifiProfile0041{};memcpy(out.ssid,bytes+6,bytes[4]);memcpy(out.password,bytes+6+bytes[4],bytes[5]);return 0;
}
int journal(void *,const Ap01WifiProfile0041 *old){
    auto io=ap01RomVfs();
    if(!old){io.remove(io.context,Stored);return io.exists(io.context,Stored)==0?0:-EIO;}
    unsigned sn=strlen(old->ssid),pn=strlen(old->password);if(!sn||sn>32||pn>64)return -EINVAL;
    uint8_t bytes[106]={},check[106]={};unsigned n=10+sn+pn;
    memcpy(bytes,"WNR1",4);bytes[4]=sn;bytes[5]=pn;memcpy(bytes+6,old->ssid,sn);memcpy(bytes+6+sn,old->password,pn);
    uint32_t value=ap01_native_crc32(bytes,n-4);for(unsigned i=0;i<4;++i)bytes[n-4+i]=uint8_t(value>>(8*i));
    int result=ROM(0xa005f8d8,int (*)(const char *,const char *,const void *,uint32_t))("ap01_wifi","rollback.new",bytes,n);
    if(result!=int((n/16+1)*16)||ROM(0xa005f6d8,int (*)(const char *,const char *,void *,uint32_t))("ap01_wifi","rollback.new",check,sizeof(check))!=int(n)||memcmp(bytes,check,n))return -EIO;
    io.rename(io.context,Temporary,Stored);Ap01WifiProfile0041 actual;
    return !readJournal(nullptr,actual)&&!strcmp(actual.ssid,old->ssid)&&!strcmp(actual.password,old->password)?0:-EIO;
}
int persist(const Ap01WifiProfile0041 &p){
    auto set=ROM(0xa0061bc2,int (*)(const char *,const char *,const char *));
    auto get=ROM(0xa00616de,int (*)(const char *,const char *,char *,int));
    char ssid[33]={},password[65]={};
    // Do not call config_router/reset/restore: those paths can change identity.
    if(set("network","password",p.password)<0||set("network","ssid",p.ssid)<0||
       get("network","ssid",ssid,sizeof(ssid))<0||get("network","password",password,sizeof(password))<0||
       !memchr(ssid,0,sizeof(ssid))||!memchr(password,0,sizeof(password))||strcmp(ssid,p.ssid)||strcmp(password,p.password))return -EIO;
    memset(password,0,sizeof(password));return 0;
}
int apply(void *context,const Ap01WifiProfile0041 &p,bool persistent){
    if(persistent&&persist(p))return -EIO;
    auto current=ap01WifiProfilesNativePort0041(context,nullptr);
    char ssid[33]={},password[65]={};
    int got=current.current(context,ssid,sizeof(ssid),password,sizeof(password));
    bool same=!got&&!strcmp(ssid,p.ssid)&&!strcmp(password,p.password);memset(password,0,sizeof(password));
    // A confirmed trial already runs this network. Persist it without reconnecting.
    if(persistent&&same)return 0;
    if(ROM(0xa00699c4,int (*)())()<0)return -EIO;
    ROM(0xa006bfdc,void (*)(const char *,const char *,int))(p.ssid,p.password,1);
    return ROM(0xa0068a7a,int (*)())()<0?-EIO:0;
}
bool online(void *,const char *target){
    int fd=ROM(0xa00268c4,int (*)(int,int,int))(2,2,0);if(fd<0)return false;
    char ssid[33]={};uint8_t associated=0;uint32_t ip=0;
    bool good=ROM(0xa00756c2,int (*)(int,const char *,char *,uint8_t *))(fd,"wlan0",ssid,&associated)>=0&&associated&&
        memchr(ssid,0,sizeof(ssid))&&!strcmp(ssid,target)&&
        ROM(0xa00c6ba0,int (*)(int,const char *,int,uint32_t *))(fd,"wlan0",0x701,&ip)>=0&&ip&&ip!=UINT32_MAX;
    ROM(0xa0026888,int (*)(int))(fd);return good;
}
}
Ap01WifiSwitchPort0041 ap01WifiSwitchNativePort0041(void *context,bool (*busy)(void *)){
    return {context,ap01WifiProfilesNativePort0041(context,busy),apply,online,journal,readJournal};
}
