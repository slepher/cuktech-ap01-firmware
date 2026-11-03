// S1 compiler/emulator fixture only. This is not the product App ABI.
#include <stdint.h>

struct ProbeServices {
    uint32_t version, size;
    uint32_t (*add_seven)(uint32_t);
};
static volatile uint32_t seed = 9;
static volatile uint32_t calls;
__attribute__((noinline)) static uint32_t plus_three(uint32_t x) { return x + 3; }
static uint32_t (*volatile transform)(uint32_t) = plus_three;

struct Operation { virtual uint32_t apply(uint32_t) const = 0; };
struct AddFive : Operation {
    uint32_t apply(uint32_t x) const override { return x + 5; }
};
__attribute__((noinline, noclone)) static uint32_t dispatch(const Operation &op, uint32_t x) {
    return op.apply(x);
}

extern "C" __attribute__((used, section(".text.probe_entry")))
uint32_t probe_entry(const ProbeServices *services, uint32_t value) {
    if (!services || services->version != 1 || services->size != sizeof(ProbeServices) ||
        !services->add_seven) return UINT32_MAX;
    AddFive op;
    uint32_t result = dispatch(op, transform(value));
    return services->add_seven(result) + seed + ++calls;
}
