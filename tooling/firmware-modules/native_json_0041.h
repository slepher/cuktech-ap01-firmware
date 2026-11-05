#pragma once
#include "native_string_0041.h"
#include <ArduinoJson.h>
#include <stdlib.h>

// Request-local replacement for ArduinoJson's writable DefaultAllocator
// singleton. A document must be destroyed before this stack object.
class NativeJsonAllocator0041 : public ArduinoJson::Allocator {
public:
    void *allocate(size_t n) override { return malloc(n); }
    void deallocate(void *p) override { free(p); }
    void *reallocate(void *p, size_t n) override { return realloc(p, n); }
};

// ArduinoJson's String writer clears the destination (discarding reserve) and
// its byte count can omit a failed final flush. Keep our reserve and check both.
inline bool ap01EncodeJson0041(const ArduinoJson::JsonDocument &doc,String &out,size_t limit=SIZE_MAX){
    out=String();size_t expected=ArduinoJson::measureJson(doc);
    if(doc.overflowed()||expected>limit||!out.reserve(expected))return false;
    struct Sink {
        String &value;
        size_t write(uint8_t c){return value.concat(char(c))?1:0;}
        size_t write(const uint8_t *p,size_t n){return value.concat((const char *)p,n)?n:0;}
    } sink{out};
    if(ArduinoJson::serializeJson(doc,sink)==expected&&out.length()==expected)return true;
    out=String();return false;
}
