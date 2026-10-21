#include "native_device_code_0041.h"
#include "native_filesystem_0041.h"
#include <assert.h>
#include <map>
#include <string>
#include <vector>
#include <stdio.h>

namespace {
const char *Stored = "/data/ap01_ui.device_code";
const char *Temporary = "/data/ap01_ui.device_code.new";
struct Fake {
    std::map<std::string, std::vector<uint8_t>> files;
    std::string opened;
    unsigned position = 0, writes = 0, renames = 0, rngCalls = 0;
    bool writeFail = false, shortWrite = false, renameFail = false, renameCommittedError = false;
    bool finalReadFail = false, tempReadCorrupt = false, existsFail = false, rngFail = false;
    std::vector<uint32_t> random{0};
};
int exists(void *p, const char *path) {
    auto &f = *(Fake *)p; return f.existsFail ? -5 : f.files.count(path) ? 1 : 0;
}
int open(void *p, const char *path, unsigned mode) {
    auto &f = *(Fake *)p;
    if ((!mode && !f.files.count(path)) || (!mode && path == std::string(Stored) && f.finalReadFail)) return -5;
    f.opened = path; f.position = 0;
    if (mode) f.files[path].clear();
    return 7;
}
int close(void *, int fd) { assert(fd == 7); return 0; }
int size(void *p, int fd) { assert(fd == 7); auto &f = *(Fake *)p; return int(f.files[f.opened].size()); }
int read(void *p, int fd, void *out, size_t length) {
    assert(fd == 7); auto &f = *(Fake *)p; const auto &bytes = f.files[f.opened];
    unsigned n = unsigned(length);
    if (n > bytes.size() - f.position) n = unsigned(bytes.size()) - f.position;
    if (n > 3) n = 3; // Also exercise partial reads.
    memcpy(out, bytes.data() + f.position, n);
    if (n && f.tempReadCorrupt && f.opened == Temporary) ((uint8_t *)out)[0] ^= 1;
    f.position += n; return int(n);
}
int write(void *p, int fd, const void *in, size_t length) {
    assert(fd == 7); auto &f = *(Fake *)p; ++f.writes;
    if (f.writeFail) return -5;
    const auto *bytes = (const uint8_t *)in;
    if (f.shortWrite) --length;
    f.files[f.opened].assign(bytes, bytes + length); return int(length);
}
int fakeRename(void *p, const char *from, const char *to) {
    auto &f = *(Fake *)p; ++f.renames; assert(from == std::string(Temporary) && to == std::string(Stored));
    if (f.renameFail) return -5;
    f.files[to] = f.files[from]; f.files.erase(from);
    return f.renameCommittedError ? -5 : 0;
}
bool random(void *p, uint8_t *out, size_t length) {
    auto &f = *(Fake *)p; assert(length == 4); ++f.rngCalls;
    if (f.rngFail) return false;
    uint32_t value = f.random[(f.rngCalls - 1) % f.random.size()];
    for (unsigned i = 0; i < 4; ++i) out[i] = uint8_t(value >> (8 * i));
    return true;
}
Ap01VfsOps io(Fake &f) {
    return {&f, nullptr, open, close, read, write, nullptr, size, exists, nullptr, nullptr, fakeRename, nullptr};
}
int ensure(Fake &f, char out[9]) { return ap01DeviceCodeEnsure0041(io(f), random, &f, out); }
int regenerate(Fake &f, char out[9]) { return ap01DeviceCodeRegenerate0041(io(f), random, &f, out); }
int load(Fake &f, char out[9]) { return ap01DeviceCodeLoad0041(io(f), out); }
}

int main() {
    char out[9] = "sentinel";
    Fake f; assert(load(f, out) == -2 && !strcmp(out, "sentinel"));
    assert(ensure(f, out) == 0 && !strcmp(out, "00000000"));
    assert(f.writes == 1 && f.renames == 1 && f.rngCalls == 1 && f.files[Stored].size() == 16);
    auto original = f.files[Stored];
    for (unsigned i = 0; i < 4; ++i) assert(ensure(f, out) == 0 && load(f, out) == 0);
    assert(f.writes == 1 && f.rngCalls == 1 && f.files[Stored] == original);
    // A new module instance after restart reads the exact same bytes.
    Fake restarted; restarted.files = f.files;
    assert(ensure(restarted, out) == 0 && !strcmp(out, "00000000") && !restarted.rngCalls && !restarted.writes);
    f.random = {0, 4200000000u, 4294967295u, 99999999u}; f.rngCalls = 0;
    assert(regenerate(f, out) == 0 && !strcmp(out, "99999999") && f.rngCalls == 4);
    auto saved = f.files[Stored];
    f.random = {99999999u}; f.rngCalls = 0;
    assert(regenerate(f, out) == -11 && f.rngCalls == 32 && f.files[Stored] == saved);
    f.random = {4200000000u}; f.rngCalls = 0;
    assert(regenerate(f, out) == -11 && f.rngCalls == 32 && f.files[Stored] == saved);
    f.rngFail = true; assert(regenerate(f, out) == -11 && f.files[Stored] == saved); f.rngFail = false;
    f.random = {12345678};
    f.writeFail = true; assert(regenerate(f, out) == -5 && f.files[Stored] == saved); f.writeFail = false;
    f.shortWrite = true; assert(regenerate(f, out) == -5 && f.files[Stored] == saved); f.shortWrite = false;
    f.tempReadCorrupt = true; assert(regenerate(f, out) == -5 && f.files[Stored] == saved); f.tempReadCorrupt = false;
    f.renameFail = true; assert(regenerate(f, out) == -5 && f.files[Stored] == saved); f.renameFail = false;
    assert(ensure(f, out) == 0 && !strcmp(out, "99999999"));
    f.renameCommittedError = true;
    assert(regenerate(f, out) == 0 && !strcmp(out, "12345678")); f.renameCommittedError = false;
    // A committed record whose final read fails is unknown; no unconfirmed display.
    f.random = {87654321};
    // The read failure must occur after the pre-generation load, so inject on rename.
    struct Unknown { static int rename(void *p, const char *from, const char *to) {
        int result = fakeRename(p, from, to); ((Fake *)p)->finalReadFail = true; return result;
    }};
    auto unknownIo = io(f); unknownIo.rename = Unknown::rename;
    assert(ap01DeviceCodeRegenerate0041(unknownIo, random, &f, out) == -115 && !strcmp(out, "12345678"));
    f.finalReadFail = false;
    assert(load(f, out) == 0 && !strcmp(out, "87654321"));
    // Corruption and an I/O error never cause an automatic random replacement.
    f.files[Stored][5] ^= 1; unsigned calls = f.rngCalls, writes = f.writes;
    assert(ensure(f, out) == -22 && f.rngCalls == calls && f.writes == writes);
    f.random = {31415926}; assert(regenerate(f, out) == 0 && !strcmp(out, "31415926"));
    f.existsFail = true; calls = f.rngCalls;
    assert(ensure(f, out) == -5 && regenerate(f, out) == -5 && f.rngCalls == calls); f.existsFail = false;
    // Interrupted first creation recovers the valid pending value without new RNG.
    Fake pending; pending.files[Temporary] = f.files[Stored];
    assert(ensure(pending, out) == 0 && !strcmp(out, "31415926") && !pending.rngCalls && !pending.writes);
    Fake damaged; damaged.files[Temporary] = {0};
    assert(ensure(damaged, out) == -22 && !damaged.rngCalls && !damaged.writes);
    Fake failed; failed.rngFail = true;
    assert(ensure(failed, out) == -11 && !failed.writes && !failed.files.count(Stored));
    puts("device-code tests passed (no code values logged)");
}
