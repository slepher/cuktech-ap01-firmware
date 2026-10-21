#pragma once
#include <stddef.h>
#include <stdint.h>

struct Ap01VfsOps;
// Callers serialize access (the native menu uses only its UI thread).
// Success=0; absent=-2; I/O=-5; RNG unavailable=-11; corrupt=-22;
// commit outcome unknown=-115. Output is unchanged on every failure.
// Unknown commits must be resolved with Load, never blind regeneration.
int ap01DeviceCodeLoad0041(const Ap01VfsOps &, char out[9]);
int ap01DeviceCodeEnsure0041(const Ap01VfsOps &, bool (*random)(void *, uint8_t *, size_t),
                             void *context, char out[9]);
// Only an explicit menu action may call Regenerate. It can replace corrupt data.
int ap01DeviceCodeRegenerate0041(const Ap01VfsOps &, bool (*random)(void *, uint8_t *, size_t),
                                 void *context, char out[9]);
