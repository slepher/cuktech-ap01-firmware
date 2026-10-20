#pragma once
#include "native_http_0041.h"

// Owned by the resident maintenance service, independent of business/UI state.
// Readers return a byte count or negative errno; they never open for writing.
struct Ap01DiagnosticPort {
    void *context = nullptr;
    int (*file)(void *, const char *, uint32_t, uint8_t *, unsigned, uint32_t *) = nullptr;
    int (*flash)(void *, uint32_t, uint8_t *, unsigned) = nullptr;
    bool (*busy)(void *) = nullptr;
};
Ap01HttpReply ap01DiagnosticHttp0041(const Ap01DiagnosticPort &, const Ap01HttpRequest &,
                                    const char *mac, uint64_t boot);
int ap01DiagnosticFile0041(void *, const char *, uint32_t, uint8_t *, unsigned, uint32_t *);
int ap01DiagnosticFlash0041(void *, uint32_t, uint8_t *, unsigned);
