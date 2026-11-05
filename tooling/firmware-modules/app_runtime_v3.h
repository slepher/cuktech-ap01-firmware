#pragma once
#include "app_platform_api_v3.h"
#include <stdio.h>
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
// Force-include for App translation units, after stdio declarations. Varargs
// pass directly to the platform implementation; no private printf engine.
#define snprintf(...) (ap01RuntimeApiV3()->format(__VA_ARGS__))
