#pragma once
#include "app_download_0041.h"
#include "app_selection_0041.h"
#include "native_http_0041.h"
struct Ap01AppRuntimeStatus0041 {
    const char *state="unavailable";
    uint32_t generation=0;
    uint8_t digest[32]={};
    char version[32]={};
    bool businessWrites=false;
};
struct Ap01AppUpdatePort0041 {
    void *context=nullptr;
    bool (*busy)(void *)=nullptr;
    // Acquire shared update exclusion, freeze writes, stop/drain the current
    // App. True means no old code can execute. Never a raw forced free.
    bool (*stop)(void *)=nullptr;
    // Snapshot of the resident executor, never inferred from a journal receipt.
    void (*runtime)(void *,Ap01AppRuntimeStatus0041 &)=nullptr;
};
// Firmware-owned, one executor. Authentication precedes handle; principal is
// supplied by the firmware guard, never taken from request JSON.
class Ap01AppHttp0041 {
    LittleFSClass &fs;
    Ap01AppUpdateJournal0041 &journal;
    Ap01AppDownload0041 &download;
    Ap01AppSelection0041 &selection;
    Ap01AppUpdatePort0041 port;
    Apx2Limits limits;
    const char *mac,*appId;
public:
    Ap01AppHttp0041(LittleFSClass &f,Ap01AppUpdateJournal0041 &j,Ap01AppDownload0041 &d,
                   Ap01AppSelection0041 &s,const Ap01AppUpdatePort0041 &p,
                   const Apx2Limits &l,const char *deviceMac,const char *id)
        :fs(f),journal(j),download(d),selection(s),port(p),limits(l),mac(deviceMac),appId(id){}
    Ap01HttpReply handle(const Ap01HttpRequest &,const char *principal,uint64_t now);
};
