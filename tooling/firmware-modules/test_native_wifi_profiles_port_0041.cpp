// Linux host adapter test with synthetic encrypted-reader/writer and VFS ports.
// No firmware execution, actual encryption, network driver, or real credentials.
#include "native_vfs_0041.h"
#include <assert.h>
#include <errno.h>
#include <sys/mman.h>
#include <vector>
#include <string>

struct FakeStorage {
    std::vector<uint8_t> finalBytes{1,2,3}, temporaryBytes;
    bool finalPresent=true, temporaryPresent=false;
    bool writerFail=false, readbackFail=false, renameFail=false, busy=false;
    int existsResult=1, getterResult=0, lockResult=0;
    unsigned getters=0,writers=0,renames=0,removes=0,locks=0,unlocks=0;
    std::string events;
    const char identity[40]="UID/token/BLE binding fixture unchanged";
};
static FakeStorage state;
static const char *const FinalPath="/data/e#ap01_wifi.profiles";
static const char *const TempPath="/data/e#ap01_wifi.profiles.new";

static int fakeGetter(const char *space,const char *key,void *out,uint32_t capacity) {
    assert(!strcmp(space,"ap01_wifi"));
    assert(!strcmp(key,"profiles")||!strcmp(key,"profiles.new"));
    ++state.getters;state.events+='r';
    if(state.getterResult)return state.getterResult;
    bool temp=!strcmp(key,"profiles.new");
    assert(temp?state.temporaryPresent:state.finalPresent);
    const auto &bytes=temp?state.temporaryBytes:state.finalBytes;
    if(bytes.size()>capacity)return -EFBIG;
    memcpy(out,bytes.data(),bytes.size());
    if(temp&&state.readbackFail&&bytes.size())((uint8_t *)out)[0]^=1;
    return int(bytes.size());
}
static int fakeWriter(const char *space,const char *key,const void *input,uint32_t length) {
    assert(!strcmp(space,"ap01_wifi")&&!strcmp(key,"profiles.new"));
    ++state.writers;state.events+='w';
    if(state.writerFail)return -EIO;
    const auto *bytes=(const uint8_t *)input;
    state.temporaryBytes.assign(bytes,bytes+length);state.temporaryPresent=true;
    // Original encrypted writer returns padded ciphertext length, not plaintext.
    return int((length/16+1)*16);
}
static int fakeLock(void *handle,uint32_t timeout) {
    assert(handle==(void *)(uintptr_t)0x1234&&timeout==1000);++state.locks;return state.lockResult;
}
static void fakeUnlock(void *handle) {
    assert(handle==(void *)(uintptr_t)0x1234);++state.unlocks;
}
static uintptr_t romFunction(uintptr_t address) {
    switch(address) {
        case 0xa005f6d8:return (uintptr_t)&fakeGetter;
        case 0xa005f8d8:return (uintptr_t)&fakeWriter;
        case 0xa005f3d8:return (uintptr_t)&fakeLock;
        case 0xa01b3c8c:return (uintptr_t)&fakeUnlock;
        default:assert(false);return 0;
    }
}
#define AP01_WIFI_ROM_FN(address,type) reinterpret_cast<type>(romFunction(address))
#include "native_wifi_profiles_port_0041.cpp"
#undef AP01_WIFI_ROM_FN

static int fakeExists(void *,const char *path) {
    assert(!strcmp(path,FinalPath));
    if(state.existsResult!=1)return state.existsResult;
    return state.finalPresent?1:0;
}
static int fakeRemove(void *,const char *path) {
    assert(!strcmp(path,TempPath));++state.removes;state.events+='d';
    state.temporaryPresent=false;state.temporaryBytes.clear();return 0;
}
static int fakeRename(void *,const char *from,const char *to) {
    assert(!strcmp(from,TempPath)&&!strcmp(to,FinalPath));
    ++state.renames;state.events+='c';assert(state.temporaryPresent);
    if(state.renameFail)return -EIO;
    state.finalBytes=state.temporaryBytes;state.finalPresent=true;
    state.temporaryBytes.clear();state.temporaryPresent=false;return 0;
}
Ap01VfsOps ap01RomVfs() {
    Ap01VfsOps io{};io.exists=fakeExists;io.remove=fakeRemove;io.rename=fakeRename;return io;
}
static bool fakeBusy(void *context){assert(context==&state);return state.busy;}
static void identityUnchanged() {assert(!strcmp(state.identity,"UID/token/BLE binding fixture unchanged"));}

int main() {
    auto port=ap01WifiProfilesNativePort0041(&state,fakeBusy);
    assert(port.context==&state&&!port.busy(port.context));state.busy=true;assert(port.busy(port.context));state.busy=false;
    const uint8_t input[]={9,0,8,7,6};uint8_t out[800]={};
    assert(port.load(port.context,out,sizeof(out))==3&&out[0]==1);
    state.events.clear();
    assert(!port.store(port.context,input,sizeof(input))&&state.events=="wrc");
    assert(state.finalBytes==std::vector<uint8_t>(input,input+sizeof(input))&&!state.temporaryPresent);
    assert(port.load(port.context,out,sizeof(out))==int(sizeof(input))&&!memcmp(out,input,sizeof(input)));
    auto old=state.finalBytes;
    for(unsigned failure=0;failure<3;++failure) {
        state.writerFail=failure==0;state.readbackFail=failure==1;state.renameFail=failure==2;
        state.events.clear();unsigned commits=state.renames;
        const uint8_t changed[]={4,5,6,0,1,2};
        assert(port.store(port.context,changed,sizeof(changed))<0);
        assert(state.finalBytes==old&&!state.temporaryPresent&&state.events.back()=='d');
        assert(state.renames==commits+(failure==2?1:0));identityUnchanged();
    }
    state.writerFail=state.readbackFail=state.renameFail=false;
    state.finalPresent=false;unsigned reads=state.getters;
    assert(port.load(port.context,out,sizeof(out))==-2&&state.getters==reads);
    state.finalPresent=true;state.existsResult=-EIO;
    assert(port.load(port.context,out,sizeof(out))==-5&&state.getters==reads);state.existsResult=1;
    state.getterResult=801;assert(port.load(port.context,out,sizeof(out))==-5);state.getterResult=0;
    unsigned writes=state.writers;reads=state.getters;
    assert(port.store(port.context,input,0)==-22&&port.store(port.context,input,801)==-22&&
        port.store(port.context,nullptr,1)==-22&&state.writers==writes);
    assert(port.load(port.context,out,0)==-22&&port.load(port.context,out,801)==-22&&state.getters==reads);

    void *page=mmap((void *)(uintptr_t)0x62fca000,4096,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(page==(void *)(uintptr_t)0x62fca000);
    auto *mutex=(void **)(uintptr_t)0x62fca9d8;*mutex=(void *)(uintptr_t)0x1234;
    *(uint8_t *)(uintptr_t)0x62fca824=1;
    char expectedSsid[33]="synthetic-fixture",expectedPassword[65]="synthetic-private";
    memcpy((void *)(uintptr_t)0x62fca831,expectedSsid,sizeof(expectedSsid));
    memcpy((void *)(uintptr_t)0x62fca853,expectedPassword,sizeof(expectedPassword));
    char ssid[33],password[65];memset(ssid,0x5a,sizeof(ssid));memset(password,0x5a,sizeof(password));
    state.lockResult=ETIMEDOUT;
    assert(port.current(port.context,ssid,sizeof(ssid),password,sizeof(password))==-11);
    for(char c:ssid)assert(c==0x5a);
    for(char c:password)assert(c==0x5a);
    assert(state.locks==1&&state.unlocks==0);
    state.lockResult=0;
    assert(!port.current(port.context,ssid,sizeof(ssid),password,sizeof(password))&&
        !memcmp(ssid,expectedSsid,sizeof(ssid))&&!memcmp(password,expectedPassword,sizeof(password)));
    assert(state.locks==2&&state.unlocks==1);
    *(uint8_t *)(uintptr_t)0x62fca824=0;
    assert(!port.current(port.context,ssid,sizeof(ssid),password,sizeof(password))&&!ssid[0]&&!password[0]);
    assert(state.unlocks==2);
    *mutex=nullptr;unsigned locks=state.locks;
    assert(port.current(port.context,ssid,sizeof(ssid),password,sizeof(password))==-11&&state.locks==locks&&state.unlocks==2);
    assert(!munmap(page,4096));identityUnchanged();
    puts("0041 Wi-Fi native storage adapter: passed (synthetic host only)");
}
