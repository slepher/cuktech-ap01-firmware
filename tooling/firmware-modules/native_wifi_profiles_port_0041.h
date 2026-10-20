#pragma once
#include "native_wifi_profiles_0041.h"

// List storage has its own encrypted PSM key. Current network is read-only.
Ap01WifiProfilesPort ap01WifiProfilesNativePort0041(void *, bool (*busy)(void *));
