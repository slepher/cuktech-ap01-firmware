#pragma once
#include "app_image_0041.h"
#include "app_selection_0041.h"

enum class Ap01AppRunState {Idle,Running,Stopping,Recovery,Unknown,RebootRequired};
// Firmware's serialized App executor. HTTP commit/cancel and file mutations
// must share its exclusion; never call select as a status query. External stock
// and maintenance counters are sampled by the platform, not supplied by App.
class Ap01AppRunner0041 {
    LittleFSClass &fs;
    Ap01AppSelection0041 &selection;
    Apx2Limits limits;
    ap01_app_services_v2 services;
    Ap01AppImage0041 image;
    Ap01AppImagePort0041 resourcePort;
    Ap01AppSelection chosen{};
    Ap01AppRunState state=Ap01AppRunState::Idle;
    enum class AfterStop {Hold,Retry,Recovery,Unknown} after=AfterStop::Hold;
    bool dispatching=false,writesEnabled=false;
    bool syncWrites();
    Ap01AppRunState drain(uint64_t now);
    Ap01AppRunState fail(uint64_t now,AfterStop);
public:
    static constexpr uint64_t stopBudgetMs=5000;
    Ap01AppRunner0041(LittleFSClass &f,Ap01AppSelection0041 &s,const Apx2Limits &l,
                     const Ap01AppImagePort0041 &p,const ap01_app_services_v2 &table)
        :fs(f),selection(s),limits(l),services(table),image(p),resourcePort(p){}
    Ap01AppRunState launch(uint64_t now);
    // Hold stopped for HTTP commit/cancel. Caller then explicitly launches the
    // persisted choice. This operation never guesses a transaction outcome.
    Ap01AppRunState stop(uint64_t now);
    Ap01AppRunState tick(uint64_t now,uint32_t stockProgress,uint32_t maintenanceProgress);
    // Reconcile after journal mutations, before the executor accepts more work.
    Ap01AppRunState reconcile(uint64_t now);
    Ap01AppLifeResult event(uint64_t now,const ap01_app_event_v2 &);
    Ap01AppRunState status() const {return state;}
    bool businessWritesAllowed() const {return state==Ap01AppRunState::Running&&writesEnabled&&selection.businessWritesAllowed(chosen.generation);}
    Ap01AppGeneration0041 &callbacks(){return image.callbacks();}
    const Ap01AppSelection *running() const {return state==Ap01AppRunState::Running?&chosen:nullptr;}
    const Apx2View *runningImage() const {return running()?image.loaded():nullptr;}
};
