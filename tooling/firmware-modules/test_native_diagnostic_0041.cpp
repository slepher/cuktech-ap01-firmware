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
