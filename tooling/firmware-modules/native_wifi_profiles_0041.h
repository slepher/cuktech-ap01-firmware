#pragma once
#include "native_http_0041.h"

struct Ap01WifiProfile0041 {
    char ssid[33] = {}, password[65] = {};
    bool current = false, saved = false;
};
struct Ap01WifiProfiles0041 {
    uint32_t revision = 0;
    unsigned count = 0;
    Ap01WifiProfile0041 profiles[9];
};
// Serialized by the maintenance owner. current is strictly read-only and returns
// 0 on success. load returns bytes or negative errno (-2 means absent). store
// returns 0 only after durable atomic replacement: failure preserves old bytes.
// Storage MUST use its own encrypted namespace, never original network keys.
struct Ap01WifiProfilesPort {
    void *context = nullptr;
    int (*current)(void *, char *, unsigned, char *, unsigned) = nullptr;
    int (*load)(void *, uint8_t *, unsigned) = nullptr;
    int (*store)(void *, const uint8_t *, unsigned) = nullptr;
    bool (*busy)(void *) = nullptr;
};
// Private credentials for local menu use only. Never serialize this structure.
int ap01WifiProfilesRead0041(const Ap01WifiProfilesPort &, Ap01WifiProfiles0041 &);
// Caller authenticates before dispatch; this handler never changes networking.
Ap01HttpReply ap01WifiProfilesHttp0041(const Ap01WifiProfilesPort &,
                                      const Ap01HttpRequest &, const char *mac);
