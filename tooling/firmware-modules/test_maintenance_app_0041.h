#pragma once
#include "application.h"
#include "native_maintenance_0041.h"
inline Ap01MaintenanceBridge0041 testMaintenanceBridge0041(Ap01Application &app) {
    return {&app,
        [](void *p,const char *token,char out[65]){return ((Ap01Application *)p)->bindingPrincipal(token,out);},
        [](void *p,const Ap01HttpRequest &r,uint64_t now){return ((Ap01Application *)p)->pairingHttp(r,now);},
        [](void *p){return ((Ap01Application *)p)->businessAvailable();}};
}
