#pragma once
#include <atomic>
#include <stdint.h>
// One collection gate. App callers take leases; the transaction owner can hold
// admission closed across background health approvals, Unknown and reboot wait.
class Ap01AppWriteGateV3 {
    std::atomic<uint32_t> state{0}; // 0 closed, 1 allowed, 2 transaction hold
    std::atomic<uint32_t> active{0};
public:
    bool enter(){
        if(state.load()!=1)return false;
        active.fetch_add(1);
        if(state.load()==1)return true;
        active.fetch_sub(1);return false;
    }
    void leave(){active.fetch_sub(1);}
    bool writes(bool allow){
        if(!allow){state.fetch_and(~1u);return active.load()==0;}
        if(active.load())return false;
        uint32_t expected=0;
        return state.compare_exchange_strong(expected,1)||expected==1;
    }
    // Only the single transaction owner may release the hold after it has
    // reconciled persistence/cleanup and returned control to health approval.
    // Releasing never opens admission by itself.
    bool hold(bool enabled){
        if(enabled)state.store(2);
        else {uint32_t expected=2;state.compare_exchange_strong(expected,0);}
        return active.load()==0;
    }
    bool held()const{return state.load()==2;}
    bool writable()const{return state.load()==1;}
    bool drained()const{return state.load()!=1&&active.load()==0;}
};
