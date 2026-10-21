#include "native_device_code_0041.h"
#include "native_filesystem_0041.h"
#include <string.h>

namespace {
constexpr const char *Stored = "/data/ap01_ui.device_code";
constexpr const char *Temporary = "/data/ap01_ui.device_code.new";
constexpr unsigned Bytes = 16;
uint32_t crc(const uint8_t *bytes, unsigned length) {
    uint32_t value = ~0u;
    for (unsigned n = 0; n < length; ++n) {
        value ^= bytes[n];
        for (unsigned bit = 0; bit < 8; ++bit)
            value = (value >> 1) ^ (0xedb88320u & (0u - (value & 1)));
    }
    return ~value;
}
void encode(const char code[9], uint8_t (&bytes)[Bytes]) {
    memcpy(bytes, "DVC1", 4); memcpy(bytes + 4, code, 8);
    uint32_t check = crc(bytes, 12);
    for (unsigned i = 0; i < 4; ++i) bytes[12 + i] = uint8_t(check >> (8 * i));
}
int readCode(const Ap01VfsOps &io, const char *path, char code[9]) {
    int present = io.exists(io.context, path);
    if (present != 1) return present == 0 ? -2 : -5;
    int fd = io.open(io.context, path, 0);
    if (fd < 0) return -5;
    uint8_t bytes[Bytes];
    int size = io.size(io.context, fd), result = size < 0 ? -5 : size != Bytes ? -22 : 0;
    unsigned done = 0;
    while (!result && done < Bytes) {
        int n = io.read(io.context, fd, bytes + done, Bytes - done);
        if (n <= 0 || unsigned(n) > Bytes - done) result = -5;
        else done += unsigned(n);
    }
    if (!result && io.size(io.context, fd) != Bytes) result = -5;
    if (io.close(io.context, fd)) result = -5;
    if (result) return result;
    uint32_t check = 0;
    for (unsigned i = 0; i < 4; ++i) check |= uint32_t(bytes[12 + i]) << (8 * i);
    if (memcmp(bytes, "DVC1", 4) || check != crc(bytes, 12)) return -22;
    for (unsigned i = 4; i < 12; ++i) if (bytes[i] < '0' || bytes[i] > '9') return -22;
    memcpy(code, bytes + 4, 8); code[8] = 0;
    return 0;
}
int commit(const Ap01VfsOps &io, const char code[9], const char *previous, char out[9]) {
    // A failed rename can nevertheless commit. The final read decides success.
    io.rename(io.context, Temporary, Stored);
    char actual[9]; int result = readCode(io, Stored, actual);
    if (!result && !memcmp(actual, code, 9)) { memcpy(out, code, 9); return 0; }
    if (!result && previous && !memcmp(actual, previous, 9)) return -5;
    return -115;
}
int save(const Ap01VfsOps &io, const char code[9], const char *previous, char out[9]) {
    uint8_t bytes[Bytes]; encode(code, bytes);
    int fd = io.open(io.context, Temporary, 1);
    if (fd < 0) return -5;
    // Native VFS write reports success only after sync.
    int written = io.write(io.context, fd, bytes, Bytes);
    int closed = io.close(io.context, fd);
    if (written != Bytes || closed) return -5;
    char check[9]; int result = readCode(io, Temporary, check);
    if (result || memcmp(check, code, 9)) return -5;
    return commit(io, code, previous, out);
}
int generate(const Ap01VfsOps &io, bool (*random)(void *, uint8_t *, size_t),
             void *context, const char *previous, char out[9]) {
    if (!random) return -11;
    for (unsigned attempt = 0; attempt < 32; ++attempt) {
        uint8_t bytes[4];
        if (!random(context, bytes, sizeof(bytes))) return -11;
        uint32_t value = uint32_t(bytes[0]) | (uint32_t(bytes[1]) << 8) |
            (uint32_t(bytes[2]) << 16) | (uint32_t(bytes[3]) << 24);
        // Largest multiple of 100,000,000 below 2^32: unbiased modulo.
        if (value >= 4200000000u) continue;
        value %= 100000000u;
        char code[9]; code[8] = 0;
        for (unsigned i = 8; i; --i) { code[i - 1] = char('0' + value % 10); value /= 10; }
        if (previous && !memcmp(code, previous, 9)) continue;
        return save(io, code, previous, out);
    }
    return -11;
}
}

int ap01DeviceCodeLoad0041(const Ap01VfsOps &io, char out[9]) {
    char code[9]; int result = readCode(io, Stored, code);
    if (!result) memcpy(out, code, 9);
    return result;
}
int ap01DeviceCodeEnsure0041(const Ap01VfsOps &io, bool (*random)(void *, uint8_t *, size_t),
                             void *context, char out[9]) {
    int result = ap01DeviceCodeLoad0041(io, out);
    if (result != -2) return result;
    // Recover a fully written first-generation record without rotating it.
    char pending[9]; result = readCode(io, Temporary, pending);
    if (!result) return commit(io, pending, nullptr, out);
    if (result != -2) return result;
    return generate(io, random, context, nullptr, out);
}
int ap01DeviceCodeRegenerate0041(const Ap01VfsOps &io, bool (*random)(void *, uint8_t *, size_t),
                                 void *context, char out[9]) {
    char previous[9]; int result = ap01DeviceCodeLoad0041(io, previous);
    if (result && result != -2 && result != -22) return result;
    return generate(io, random, context, result ? nullptr : previous, out);
}
