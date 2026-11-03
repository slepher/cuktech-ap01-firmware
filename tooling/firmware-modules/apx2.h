#pragma once
#include <stdint.h>
#include "app_abi_v3.h"

// APX2 v2: explicit little-endian bytes, not a serialized native struct.
enum : uint32_t { APX2_HEADER = 256, APX2_ABI_MAJOR = 2, APX2_TARGET_0041 = 1,
                  APX2_ISA_RV32IMAFC_ILP32F = 1, APX2_ENTRY_COUNT = 5,
                  APX2_DIRECT_ABI_MAJOR = AP01_APP_ABI_MAJOR_V3,
                  APX2_DIRECT_ENTRY_COUNT = AP01_APP_V3_ENTRY_COUNT };
enum class Apx2Error : uint32_t {
    Ok, Read, Header, Bounds, Target, Abi, Services, Budget, Identity,
    DataVersion, Entry, Fixup, Integrity, Memory
};
struct Apx2Reader {
    void *context;
    uint32_t size;
    // Exact read or failure. Caller must keep the file immutable throughout validate/load.
    bool (*read)(void *, uint32_t offset, uint8_t *out, uint32_t length);
};
struct Apx2Limits {
    uint32_t package_bytes, memory_bytes, heap_bytes, stack_bytes;
    uint32_t data_version;
    uint64_t services;
    const char *app_id; // nullptr accepts any structurally valid App ID.
    // Each execution path explicitly selects one ABI; never auto-dispatch old entries.
    uint32_t abi_major = APX2_ABI_MAJOR;
};
struct Apx2View {
    uint32_t abi_major;
    uint32_t image_bytes, text_bytes, ro_offset, ro_bytes, data_offset, data_bytes, bss_bytes;
    uint32_t heap_bytes, stack_bytes, entries[APX2_ENTRY_COUNT], fixup_count;
    uint32_t data_read_min, data_read_max, data_write_version;
    uint64_t required_services;
    char app_id[32], version[32];
    uint8_t digest[32];
};
Apx2Error apx2Validate(const Apx2Reader &, const Apx2Limits &, Apx2View &);
// No allocation or execution. Validates before touching caller-owned memory.
// base is the actual RV32 load address; host tests may supply synthetic addresses.
// On I/O failure after copying begins the copied region is cleared; never invoke it.
// The execution backend must synchronize caches. ABI 3 images live until reboot.
Apx2Error apx2Load(const Apx2Reader &, const Apx2Limits &, uint8_t *memory,
                   uint32_t capacity, uint32_t base, Apx2View &);
const char *apx2ErrorName(Apx2Error);
