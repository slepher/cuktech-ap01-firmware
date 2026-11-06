#pragma once
#include "app_platform_api_v3.h"
#ifdef __cplusplus
#include <cstdio>
#else
#include <stdio.h>
#endif
#ifdef __cplusplus
extern "C" {
#endif
int ap01BindRuntimeV3(const Ap01PlatformApiV3 *,void *);
const Ap01PlatformApiV3 *ap01RuntimeApiV3(void);
void *ap01RuntimeContextV3(void);
static inline int32_t ap01RuntimeWriteScopeV3(int32_t (*callback)(void *),void *argument,int32_t *result){
    return ap01WriteScopeV3(ap01RuntimeApiV3(),ap01RuntimeContextV3(),callback,argument,result);
}
#ifdef __cplusplus
}
#endif
// Include C++ stdio before installing the macro: <cstdio> otherwise undefines
// snprintf when another App header includes it later. Varargs
// pass directly to the platform implementation; no private printf engine.
#define snprintf(...) (ap01RuntimeApiV3()->format(__VA_ARGS__))
