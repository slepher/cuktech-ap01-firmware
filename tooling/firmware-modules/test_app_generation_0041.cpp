#include "app_generation_0041.h"
#include <assert.h>
#include <thread>
#include <vector>
#include <stdio.h>

int main() {
    Ap01AppGeneration0041 gate;
    assert(gate.drained() && !gate.acquire(0));
    auto first = gate.begin();
    assert(first && !gate.begin() && !gate.drained());
    {
        Ap01AppLease0041 lease(gate, first);
        assert(lease);
        gate.close();
        assert(!gate.acquire(first) && !gate.drained() && !gate.begin());
        // Stop timeout must retain code while this lease remains alive.
        gate.close();
        assert(!gate.drained());
    }
    assert(gate.drained());
    auto second = gate.begin();
    assert(second == first + 1 && !gate.acquire(first));
    {
        Ap01AppLease0041 stale(gate, first), valid(gate, second);
        assert(!stale && valid);
    }
    gate.close();
    assert(gate.drained());

    // Race queued callbacks with close, drain, unload and next-generation start.
    // active models the only memory that can be accessed under an admitted lease.
    std::atomic<bool> done{false};
    std::atomic<uint32_t> published{0}, active{0};
    std::atomic<unsigned> entered{0};
    std::vector<std::thread> workers;
    for (unsigned i = 0; i < 4; ++i) workers.emplace_back([&] {
        while (!done.load()) {
            uint32_t queued = published.load();
            std::this_thread::yield();
            Ap01AppLease0041 lease(gate, queued);
            if (lease) {
                assert(active.load() == queued);
                ++entered;
                std::this_thread::yield();
                assert(active.load() == queued);
            }
        }
    });
    for (unsigned i = 0; i < 2000; ++i) {
        // Initialization precedes publication; begin does not expose the new
        // generation to callback producers until published is updated.
        active.store(gate.current() + 1);
        uint32_t id = gate.begin(); assert(id);
        published.store(id);
        unsigned before = entered.load();
        while (entered.load() == before) std::this_thread::yield();
        gate.close();
        while (!gate.drained()) std::this_thread::yield();
        active.store(0); // Code/state may now be freed.
        assert(!gate.acquire(id));
    }
    done.store(true);
    for (auto &worker : workers) worker.join();
    assert(gate.drained());
    printf("generation admission: stale callbacks, stop timeout, 2000 concurrent unload/reload cycles passed\n");
}
