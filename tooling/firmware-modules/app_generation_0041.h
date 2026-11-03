#pragma once
#include <atomic>
#include <stdint.h>

// Firmware-owned admission gate. begin/close are serialized by the lifecycle
// executor; callbacks on other tasks only use acquire/release. Keep this object
// alive independently of App code and queued callbacks, including after unload.
class Ap01AppGeneration0041 {
    static constexpr uint32_t closed = uint32_t(1) << 31;
    std::atomic<uint32_t> generation{0};
    std::atomic<uint32_t> gate{closed};
public:
    // Zero means refused: prior App still open/in flight, or generation exhausted.
    // Never wraps; a controlled restart is required after UINT32_MAX generations.
    uint32_t begin() {
        if (gate.load(std::memory_order_acquire) != closed) return 0;
        uint32_t next = generation.load(std::memory_order_relaxed);
        if (next == UINT32_MAX) return 0;
        generation.store(++next, std::memory_order_release);
        gate.store(0, std::memory_order_release);
        return next;
    }
    bool acquire(uint32_t expected) {
        if (!expected || generation.load(std::memory_order_acquire) != expected) return false;
        uint32_t value = gate.load(std::memory_order_acquire);
        for (;;) {
            if ((value & closed) || value == closed - 1) return false;
            if (gate.compare_exchange_weak(value, value + 1, std::memory_order_acq_rel)) break;
        }
        // A stale waiter can race close/drain/begin before its CAS. It must not
        // touch App state or function pointers until this second check succeeds.
        if (generation.load(std::memory_order_acquire) == expected) return true;
        release();
        return false;
    }
    // Exactly once per successful acquire, after the last access to App memory.
    void release() { gate.fetch_sub(1, std::memory_order_release); }
    void close() { gate.fetch_or(closed, std::memory_order_acq_rel); }
    bool drained() const { return gate.load(std::memory_order_acquire) == closed; }
    uint32_t current() const { return generation.load(std::memory_order_acquire); }
};
static_assert(std::atomic<uint32_t>::is_always_lock_free, "App gate requires native RV32 atomics");

// Hold the lease across a callback's return, including destruction of any
// objects whose vtables/destructors belong to the App. Not copyable or movable.
class Ap01AppLease0041 {
    Ap01AppGeneration0041 *owner;
public:
    Ap01AppLease0041(Ap01AppGeneration0041 &gate, uint32_t generation)
        : owner(gate.acquire(generation) ? &gate : nullptr) {}
    ~Ap01AppLease0041() { if (owner) owner->release(); }
    explicit operator bool() const { return owner != nullptr; }
    Ap01AppLease0041(const Ap01AppLease0041 &) = delete;
    Ap01AppLease0041 &operator=(const Ap01AppLease0041 &) = delete;
};
