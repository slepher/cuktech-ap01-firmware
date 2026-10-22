#pragma once
#include <atomic>
#include <stdint.h>
// Last16 decisions survive stock ramlog spam. Numeric only; no credentials,
// SSIDs, durable writes or blocking producers.
struct Ap01WifiTraceEvent0041 {uint32_t sequence,ms;int32_t event,a,b,c,d;};
struct Ap01WifiTraceSnapshot0041 {
    Ap01WifiTraceEvent0041 events[16];unsigned count=0;uint32_t dropped=0;
};
class Ap01WifiTrace0041 {
    std::atomic_flag lock=ATOMIC_FLAG_INIT;
    std::atomic<uint32_t> dropped{0};
    uint32_t next=0;unsigned count=0;
    Ap01WifiTraceEvent0041 events[16]{};
public:
    enum Event {MenuKey=1,WakeConsumed,MenuReplace,WifiSelect,WifiStage,MenuForward};
    void add(uint32_t ms,int event,int a,int b,int c,int d) {
        if(lock.test_and_set(std::memory_order_acquire)){dropped.fetch_add(1,std::memory_order_relaxed);return;}
        events[next%16]={next+1,ms,event,a,b,c,d};++next;if(count<16)++count;
        lock.clear(std::memory_order_release);
    }
    bool read(Ap01WifiTraceSnapshot0041 &out) {
        if(lock.test_and_set(std::memory_order_acquire))return false;
        out.count=count;out.dropped=dropped.load(std::memory_order_relaxed);
        for(unsigned i=0;i<count;++i)out.events[i]=events[(next-count+i)%16];
        lock.clear(std::memory_order_release);return true;
    }
};
extern "C" void ap01WifiMenuTrace0041(int event,int a,int b,int c,int d);
