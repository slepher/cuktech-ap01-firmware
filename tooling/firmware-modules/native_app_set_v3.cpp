#include "native_app_set_v3.h"
#include <new>

Ap01NativeAppSetV3::Ap01NativeAppSetV3(uint64_t boot,const Ap01ManifestPackagesV3 &p,const Ap01BootPortV3 &b)
    :resident(boot,AP01_MANIFEST_APPS_V3),packages(p),backend(b),
     loader({{this,open,close},ready,prepare}){}
bool Ap01NativeAppSetV3::open(void *p,const Ap01ManifestEntryV3 &entry,Apx2Reader &reader,uint32_t &version){
    auto &s=*(Ap01NativeAppSetV3 *)p;
    return s.packages.open&&s.packages.close&&s.packages.open(s.packages.context,entry,reader,version);
}
void Ap01NativeAppSetV3::close(void *p,Apx2Reader &reader){
    auto &s=*(Ap01NativeAppSetV3 *)p;s.packages.close(s.packages.context,reader);
}
bool Ap01NativeAppSetV3::ready(void *p){return ((Ap01NativeAppSetV3 *)p)->resident.listening();}
bool Ap01NativeAppSetV3::prepare(void *p,const Ap01ManifestEntryV3 &entry,Ap01AppBootV3 *&loader,
                               const Ap01PlatformApiV3 *&api,void *&context){
    auto &s=*(Ap01NativeAppSetV3 *)p;
    if(s.count==AP01_MANIFEST_APPS_V3)return false;
    auto &app=s.contexts[s.count];
    app.reset(new(std::nothrow) Ap01NativeAppPlatformV3(s.resident,s.backend,entry));
    if(!app)return false;
    ++s.count;loader=&app->execution();api=&app->table();context=app.get();
    return api->abi_major==3;
}
