#pragma once
#include "app_set_journal_v3.h"
// Worker only. check validates/stages the entire immutable collection; it must
// never invoke App code. Returned selections authorize one boot only.
enum class Ap01SetBootModeV3 {Maintenance,Empty,Stable,Trial,Rollback};
enum class Ap01SetHealthDecisionV3 {Waiting,Approved,Reboot,Maintenance};
struct Ap01SetSelectionV3 {
    Ap01SetBootModeV3 mode=Ap01SetBootModeV3::Maintenance;
    uint8_t digest[32]{};uint64_t version=0;
};
class Ap01SetSelectorV3 {
    Ap01SetJournalV3 &journal;uint64_t boot;
    bool attempted=false,authorized=false;
    Ap01SetBootModeV3 mode=Ap01SetBootModeV3::Maintenance;
    bool observing=false,seenHealthy=false,continuous=false;
    uint32_t startedAt=0,healthyAt=0,lastObservation=0;
    Ap01SetHealthDecisionV3 decision=Ap01SetHealthDecisionV3::Waiting;
    bool persist(Ap01SetRecordV3 &,Ap01SetPhaseV3,uint32_t error=0);
public:
    using Check=bool (*)(void *,const uint8_t digest[32],uint64_t version);
    Ap01SetSelectorV3(Ap01SetJournalV3 &j,uint64_t bootId):journal(j),boot(bootId){}
    // Requires successful journal.load(). Empty journal is maintenance/bootstrap,
    // never implicit permission to run an arbitrary fixed-path candidate.
    Ap01SetSelectionV3 select(void *,Check);
    // Only after full-set health acceptance. No second reboot on success.
    bool accept();
    // After any App may have executed, never load another set in this boot.
    // true requests reboot for rollback; false means remain in maintenance.
    bool failed(uint32_t error);
    // Begin immediately before publishing to UI. Cannot reset the deadline.
    void beginObservation(uint32_t now);
    // Worker passes aggregate supervisor health (including maintenance/UI).
    // A gap over 1 s breaks continuity; no App calls are made here.
    Ap01SetHealthDecisionV3 observe(uint32_t now,bool healthy,bool fault);
};
