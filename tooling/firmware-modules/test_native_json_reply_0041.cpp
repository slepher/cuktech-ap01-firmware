#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <utility>
#include <assert.h>
namespace {bool denyRealloc;unsigned reallocations;}
static void *injectedRealloc(void *p,size_t n){
    ++reallocations;return denyRealloc?nullptr:realloc(p,n);
}
#define realloc injectedRealloc
#include "native_json_0041.h"
#undef realloc

int main(){
    NativeJsonAllocator0041 allocator;ArduinoJson::JsonDocument doc(&allocator);
    doc["phase"]="succeeded";size_t expected=ArduinoJson::measureJson(doc);
    String out;
    denyRealloc=true;
    // The previous check accepted a nonzero count despite a failed final flush.
    assert(ArduinoJson::serializeJson(doc,out)>0&&out.length()==0);
    assert(!ap01EncodeJson0041(doc,out)&&out.length()==0);
    denyRealloc=false;reallocations=0;
    assert(ap01EncodeJson0041(doc,out)&&out.length()==expected&&reallocations==1);
    assert(!strcmp(out.c_str(),"{\"phase\":\"succeeded\"}"));
    reallocations=0;
    assert(!ap01EncodeJson0041(doc,out,expected-1)&&out.length()==0&&reallocations==0);
    assert(ap01EncodeJson0041(doc,out,expected));
    doc["payload"]="a string long enough to cross multiple ArduinoJson output buffers without reallocating";
    reallocations=0;
    assert(ap01EncodeJson0041(doc,out)&&out.length()==ArduinoJson::measureJson(doc)&&reallocations==1);
    struct Deny:ArduinoJson::Allocator {
        void *allocate(size_t) override{return nullptr;}
        void deallocate(void *) override{}
        void *reallocate(void *,size_t) override{return nullptr;}
    } denied;
    ArduinoJson::JsonDocument broken(&denied);broken["phase"]="succeeded";
    assert(broken.overflowed());
    assert(!ap01EncodeJson0041(broken,out)&&out.length()==0);
    puts("JSON reply: failed final flush reproduced; one reserved allocation, complete length, output bound and document OOM checks passed");
}
