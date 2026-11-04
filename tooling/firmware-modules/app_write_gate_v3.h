#pragma once
#include <atomic>
#include <stdint.h>
// One gate for all business file mutations in a running collection. A single
// platform transaction executor owns writes(); App callers only take leases.
class Ap01AppWriteGateV3 {
    std::atomic<bool> allowed{false};
    std::atomic<uint32_t> active{0};
public:
    bool enter(){
        if(!allowed.load())return false;
        active.fetch_add(1);
        if(allowed.load())return true;
        active.fetch_sub(1);return false;
    }
    void leave(){active.fetch_sub(1);}
    bool writes(bool allow){
        if(!allow){allowed.store(false);return active.load()==0;}
        if(active.load())return false;
        allowed.store(true);return true;
    }
    bool writable()const{return allowed.load();}
    bool drained()const{return !allowed.load()&&active.load()==0;}
};
