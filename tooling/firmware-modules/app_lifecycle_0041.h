#pragma once
#include "app_abi_v2.h"
#include "app_generation_0041.h"

enum class Ap01AppLifeResult {Ok,Pending,Invalid,Fault,RebootRequired};
// Firmware-owned and retained across App instances. All lifecycle/event calls
// are serialized by one executor; independent native callbacks hold gate leases.
// Cancelling resources and removing UI callbacks is prepare_stop's contract.
// This class never frees code, stacks or platform handles by itself.
class Ap01AppLifecycle0041 {
    enum class Phase {Empty,Running,Stopping,Retained};
    Phase phase=Phase::Empty;
    Ap01AppGeneration0041 &gate;
    ap01_app_entries_v2 entries{};
    ap01_app_services_v2 services{};
    void *state=nullptr;
    uint32_t generation=0,eventProgress=0;
    uint64_t stopDeadline=0;
    bool entered=false,prepared=false,dispatching=false;
public:
    explicit Ap01AppLifecycle0041(Ap01AppGeneration0041 &g):gate(g){}
    // Entries resolved by a verified loader/backend, never supplied by HTTP.
    Ap01AppLifeResult start(const ap01_app_entries_v2 &,const ap01_app_services_v2 &);
    Ap01AppLifeResult event(uint32_t generation,const ap01_app_event_v2 &);
    Ap01AppLifeResult health(uint32_t generation,ap01_app_health_v2 &);
    Ap01AppLifeResult stop(uint64_t now,uint64_t budgetMs);
    Ap01AppLifeResult pollStop(uint64_t now);
    bool releasable() const {return phase==Phase::Empty&&gate.drained();}
    uint32_t progress() const {return eventProgress;}
};
