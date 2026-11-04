#pragma once
#include <atomic>
#include <stdint.h>
enum class Ap01RebootStateV3:uint32_t {Idle,Pending,Invoked,Failed};
// One transaction worker requests/dispatches; independent readers observe timeout.
// Only request after durable SwitchPending or RollbackPending and write drain.
class Ap01AppRebootV3 {
    mutable std::atomic<uint32_t> phase{0};
    std::atomic<uint32_t> requestedAt{0};
    std::atomic<bool> dispatched{false};
public:
    void request(uint32_t now){
        if(phase.load(std::memory_order_acquire))return;
        requestedAt.store(now,std::memory_order_relaxed);
        phase.store(uint32_t(Ap01RebootStateV3::Pending),std::memory_order_release);
    }
    Ap01RebootStateV3 state(uint32_t now)const{
        auto value=Ap01RebootStateV3(phase.load(std::memory_order_acquire));
        uint32_t age=now-requestedAt.load(std::memory_order_relaxed);
        if(value!=Ap01RebootStateV3::Idle&&age>5000&&age<0x80000000u){
            uint32_t expected=uint32_t(value);
            if(phase.compare_exchange_strong(expected,uint32_t(Ap01RebootStateV3::Failed),std::memory_order_acq_rel))
                return Ap01RebootStateV3::Failed;
            return Ap01RebootStateV3(expected);
        }
        return value;
    }
    // Same worker as tick. Once invoked, never promise that a reset can be undone.
    bool cancel(){
        if(dispatched.load(std::memory_order_acquire))return false;
        phase.store(uint32_t(Ap01RebootStateV3::Idle),std::memory_order_release);return true;
    }
    void tick(uint32_t now,void *context,void (*reboot)(void *)){
        if(state(now)!=Ap01RebootStateV3::Pending)return;
        uint32_t age=now-requestedAt.load(std::memory_order_relaxed);
        if(age<250||age>=0x80000000u)return;
        uint32_t expected=uint32_t(Ap01RebootStateV3::Pending);
        if(!phase.compare_exchange_strong(expected,uint32_t(reboot?Ap01RebootStateV3::Invoked:Ap01RebootStateV3::Failed),std::memory_order_acq_rel))return;
        if(reboot){dispatched.store(true,std::memory_order_release);reboot(context);} // No retry even if the native function returns.
    }
};
