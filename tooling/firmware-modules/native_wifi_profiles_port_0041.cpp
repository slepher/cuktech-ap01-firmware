#include "native_wifi_profiles_port_0041.h"
#include "native_vfs_0041.h"
#include <memory>
#include <new>

#ifndef AP01_WIFI_ROM_FN
#define AP01_WIFI_ROM_FN(address, type) ((type)(uintptr_t)(address))
#endif

namespace {
constexpr unsigned MaxBytes = 800;
constexpr const char *Namespace = "ap01_wifi";
constexpr const char *Stored = "/data/e#ap01_wifi.profiles";
constexpr const char *Temporary = "/data/e#ap01_wifi.profiles.new";

int current(void *, char *ssid, unsigned ssidBytes, char *password, unsigned passwordBytes) {
    if (ssidBytes < 33 || passwordBytes < 65) return -22;
    void *mutex = *(void *volatile *)(uintptr_t)0x62fca9d8;
    if (!mutex) return -11;
    // Original timedlock returns 0 on success, positive errno on failure.
    if (AP01_WIFI_ROM_FN(0xa005f3d8, int (*)(void *, uint32_t))(mutex,1000)) return -11;
    bool configured = *(volatile uint8_t *)(uintptr_t)0x62fca824 != 0;
    memcpy(ssid,(const void *)(uintptr_t)0x62fca831,33);
    memcpy(password,(const void *)(uintptr_t)0x62fca853,65);
    AP01_WIFI_ROM_FN(0xa01b3c8c, void (*)(void *))(mutex);
    if (!configured) {ssid[0]=password[0]=0;return 0;}
    return memchr(ssid,0,33)&&memchr(password,0,65) ? 0 : -22;
}

int readEncrypted(const char *key, uint8_t *out, unsigned capacity) {
    return AP01_WIFI_ROM_FN(0xa005f6d8, int (*)(const char *,const char *,void *,uint32_t))
        (Namespace,key,out,capacity);
}

int load(void *, uint8_t *out, unsigned capacity) {
    if (!capacity || capacity > MaxBytes) return -22;
    auto io=ap01RomVfs();int present=io.exists(io.context,Stored);
    if (present==0) return -2; // Do not rely on the original plaintext fallback.
    if (present!=1) return -5;
    int n=readEncrypted("profiles",out,capacity);
    return n>=0&&unsigned(n)<=capacity ? n : -5;
}

int store(void *, const uint8_t *bytes, unsigned length) {
    if (!bytes || !length || length>MaxBytes) return -22;
    auto check=std::unique_ptr<uint8_t[]>(new(std::nothrow) uint8_t[MaxBytes]);
    if (!check) return -12;
    auto io=ap01RomVfs();
    int n=AP01_WIFI_ROM_FN(0xa005f8d8, int (*)(const char *,const char *,const void *,uint32_t))
        (Namespace,"profiles.new",bytes,length);
    bool valid=n==int((length/16+1)*16) &&
        readEncrypted("profiles.new",check.get(),MaxBytes)==int(length) &&
        !memcmp(bytes,check.get(),length);
    // Only commit verified ciphertext by a same-LittleFS atomic rename.
    if (!valid || io.rename(io.context,Temporary,Stored)) {
        io.remove(io.context,Temporary);return -5;
    }
    return 0;
}
}

Ap01WifiProfilesPort ap01WifiProfilesNativePort0041(void *context, bool (*busy)(void *)) {
    return {context,current,load,store,busy};
}
