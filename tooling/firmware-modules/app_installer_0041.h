#pragma once
#include "app_http_0041.h"
#include "app_runner_0041.h"
// Resident composition for the maintenance executor. All methods, business
// events and OTA/Wi-Fi mutations must use the SAME platform serialization;
// this object does not create a second thread or an independent update lock.
class Ap01AppInstaller0041 {
    Ap01AppUpdateJournal0041 journal;
    Ap01AppDownload0041 download;
    Ap01AppSelection0041 selection;
    Ap01AppRunner0041 runner;
    Ap01AppHttp0041 http;
    void *busyContext;
    bool (*platformBusy)(void *);
    uint64_t requestNow=0;
    bool bootPending=true,launchPending=false;
    static bool busy(void *);
    static bool stop(void *);
    static void runtime(void *,Ap01AppRuntimeStatus0041 &);
public:
    Ap01AppInstaller0041(LittleFSClass &,const uint8_t mac[6],const char *macText,
                        const Apx2Limits &,const Ap01AppImagePort0041 &,
                        const ap01_app_services_v2 &,void *busyContext=nullptr,
                        bool (*platformBusy)(void *)=nullptr);
    Ap01AppJournalResult begin(){return journal.load();}
    Ap01HttpReply handle(const Ap01HttpRequest &,const char *principal,uint64_t now);
    Ap01AppRunState tick(uint64_t now,uint32_t stockProgress,uint32_t maintenanceProgress);
    Ap01AppLifeResult event(uint64_t now,const ap01_app_event_v2 &e){return runner.event(now,e);}
    bool businessWritesAllowed() const {return runner.businessWritesAllowed();}
    Ap01AppRunState status() const {return runner.status();}
    Ap01AppGeneration0041 &callbacks(){return runner.callbacks();}
    const Ap01AppUpdateRecord *record() const {return journal.current();}
};
