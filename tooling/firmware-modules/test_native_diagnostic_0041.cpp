// Host sanitizer check of the bounded read-only wire contract; no ROM execution.
#include "native_diagnostic_0041.h"
#include "native_json_0041.h"
#include <assert.h>
#include <string>

struct State {bool busy=false;unsigned reads=0;int result=3;};
static int file(void *p,const char *path,uint32_t offset,uint8_t *out,unsigned n,uint32_t *total) {
    auto &s=*(State *)p;++s.reads;assert(!strcmp(path,"/data/wapi.conf"));
    *total=3;if(s.result<0)return s.result;if(offset>3)return -22;
    unsigned got=3-offset;if(got>n)got=n;const uint8_t input[]={0,0xff,0x41};
    memcpy(out,input+offset,got);return got;
}
static int flash(void *p,uint32_t offset,uint8_t *out,unsigned n) {
    ++((State *)p)->reads;assert(offset<0x1000000&&n<=0x1000000-offset);
    memset(out,0x42,n);return n;
}
static bool busy(void *p){return ((State *)p)->busy;}
static Ap01HttpReply call(const Ap01DiagnosticPort &port,const char *path,const char *method,const char *body) {
    Ap01HttpRequest r{};r.path=path;r.method=method;r.contentType="application/json";
    r.body=(const uint8_t *)body;r.length=strlen(body);
    return ap01DiagnosticHttp0041(port,r,"34F01557210B",123);
}
int main() {
    State s;Ap01DiagnosticPort port{&s,file,flash,busy};
    auto reply=call(port,"/api/diagnostic/status","GET","");
    assert(reply.status==200&&strstr(reply.bytes.c_str(),"34F01557210B")&&!s.reads);
    ArduinoJson::JsonDocument version;
    assert(!ArduinoJson::deserializeJson(version,reply.bytes.c_str()));
    assert(version["rom"]["base_version"]=="1.0.2_0041");
    assert(version["rom"]["modified_version"]=="0.1.2-cuktech");
    assert(version["rom"]["supports_app"]==false && version["apps"].is<ArduinoJson::JsonArray>());
    assert(version["apps"].size()==0 && version["apps_scope"]=="loaded_this_boot");
    Ap01ManifestV3 manifest;manifest.count=3;manifest.order[0]=1;manifest.order[1]=0;
    strcpy(manifest.entries[0].id,"peer");strcpy(manifest.entries[0].version,"0.2.0-peer");
    strcpy(manifest.entries[1].id,"codex_status");strcpy(manifest.entries[1].version,"0.18.108-ap01");
    Ap01RuntimeSnapshotV3 snapshot;snapshot.manifest=&manifest;snapshot.started=2;
    port.context=&snapshot;port.romBuild="0123456789abcdef0123456789abcdef";
    port.runtime=[](void *p){return *(Ap01RuntimeSnapshotV3 *)p;};
    reply=call(port,"/api/diagnostic/versions","GET","");
    assert(reply.status==200 && !ArduinoJson::deserializeJson(version,reply.bytes.c_str()));
    assert(version["rom"]["supports_app"]==true && version["rom"]["build_id"]==port.romBuild);
    assert(version["apps"].size()==2 && version["apps"][0]["app_id"]=="codex_status");
    assert(version["apps"][0]["version"]=="0.18.108-ap01" && version["apps"][1]["app_id"]=="peer");
    strcpy(manifest.entries[1].version,"d1.0");
    reply=call(port,"/api/diagnostic/versions","GET","");
    assert(!ArduinoJson::deserializeJson(version,reply.bytes.c_str()) && version["apps"][0]["version"]=="d1.0");
    snapshot.started=0;snapshot.manifest=nullptr;
    reply=call(port,"/api/diagnostic/versions","GET","");
    assert(!ArduinoJson::deserializeJson(version,reply.bytes.c_str()));
    assert(version["rom"]["supports_app"]==true && version["apps"].size()==0);
    snapshot.started=1;
    assert(call(port,"/api/diagnostic/versions","GET","").status==503);
    snapshot.manifest=&manifest;manifest.order[0]=3;
    assert(call(port,"/api/diagnostic/versions","GET","").status==503);
    assert(call(port,"/api/diagnostic/versions","POST","{}").status==405);
    port.runtime=nullptr;port.romBuild=nullptr;port.context=&s;
    Ap01WifiTrace0041 trace;
    port.trace=[](void *p,Ap01WifiTraceSnapshot0041 &out){return ((Ap01WifiTrace0041 *)p)->read(out);};
    port.context=&trace;
    for(int i=0;i<24;++i)trace.add(i,1,i,-1,2,3);
    reply=call(port,"/api/diagnostic/status","GET","");
    ArduinoJson::JsonDocument parsed;assert(!ArduinoJson::deserializeJson(parsed,reply.bytes.c_str()));
    auto events=parsed["wifi_trace"]["events"].as<ArduinoJson::JsonArray>();
    assert(reply.status==200&&events.size()==16&&events[0]["seq"]==9&&events[15]["seq"]==24);
    assert(parsed["wifi_trace"]["capacity"]==16&&parsed["wifi_trace"]["dropped"]==0);
    for(auto item:events)assert(item.as<ArduinoJson::JsonObject>().size()==7);
    port.trace=[](void *,Ap01WifiTraceSnapshot0041 &){return false;};
    assert(call(port,"/api/diagnostic/status","GET","").status==503);
    port.trace=nullptr;port.context=&s;
    const char *ok="{\"device_mac\":\"34F01557210B\",\"path\":\"/data/wapi.conf\",\"offset\":0,\"length\":1024}";
    reply=call(port,"/api/diagnostic/file","POST",ok);
    assert(reply.status==200&&strstr(reply.bytes.c_str(),"00ff41")&&strstr(reply.bytes.c_str(),"\"eof\":true"));
    for(const char *bad:{"/data/../secret","/resource/./x","/data//x","/dev/fw1","/data/","/data/x\\y"}) {
        std::string body="{\"device_mac\":\"34F01557210B\",\"path\":\"";
        body+=bad;body+="\",\"offset\":0,\"length\":1}";
        assert(call(port,"/api/diagnostic/file","POST",body.c_str()).status==400);
    }
    unsigned before=s.reads;s.busy=true;
    assert(call(port,"/api/diagnostic/file","POST",ok).status==503&&s.reads==before);
    assert(call(port,"/api/diagnostic/status","GET","").status==200);s.busy=false;
    s.result=-2;assert(call(port,"/api/diagnostic/file","POST",ok).status==404);
    s.result=-11;assert(call(port,"/api/diagnostic/file","POST",ok).status==409);s.result=3;
    const char *eof="{\"device_mac\":\"34F01557210B\",\"path\":\"/data/wapi.conf\",\"offset\":3,\"length\":1}";
    assert(call(port,"/api/diagnostic/file","POST",eof).status==200);
    assert(call(port,"/api/diagnostic/file","GET",ok).status==405);
    assert(call(port,"/api/diagnostic/file","POST","{}").status==409);
    for(const char *range:{"\"offset\":-1,\"length\":1","\"offset\":0,\"length\":0","\"offset\":0,\"length\":1025",
                           "\"offset\":16777216,\"length\":1","\"offset\":16777215,\"length\":2","\"offset\":4294967295,\"length\":1"}) {
        std::string body="{\"device_mac\":\"34F01557210B\",";body+=range;body+="}";
        assert(call(port,"/api/diagnostic/flash","POST",body.c_str()).status==400);
    }
    reply=call(port,"/api/diagnostic/flash","POST","{\"device_mac\":\"34F01557210B\",\"offset\":16777215,\"length\":1}");
    assert(reply.status==200&&strstr(reply.bytes.c_str(),"\"data_hex\":\"42\""));
    assert(call({},"/api/diagnostic/flash","POST","{\"device_mac\":\"34F01557210B\",\"offset\":0,\"length\":1}").status==501);
    puts("0041 diagnostic protocol: passed");
}
