// Fault-inject only the parser's nothrow array allocations; response/handler
// allocations are outside this reservation claim. No sockets or device access.
#include "native_http_transport_0041.h"
#include <assert.h>
#include <new>
#include <string>
#include <algorithm>
namespace {bool denyArrays;unsigned allocations;}
void *operator new[](size_t n,const std::nothrow_t &) noexcept {
    ++allocations;if(denyArrays)return nullptr;
    try{return ::operator new[](n);}catch(...){return nullptr;}
}
struct Stream {
    std::string input,output,body;size_t at=0;unsigned calls=0;
    Ap01HttpWorkspace0041 *workspace=nullptr;
    bool emptyReply=false;
    static int read(void *p,uint8_t *out,size_t n,uint64_t deadline){
        auto &s=*(Stream *)p;assert(deadline==5000);
        n=std::min(n,std::min<size_t>(113,s.input.size()-s.at));
        memcpy(out,s.input.data()+s.at,n);s.at+=n;return int(n);
    }
    static int write(void *p,const uint8_t *in,size_t n,uint64_t deadline){
        assert(deadline==5000);((Stream *)p)->output.append((const char *)in,n);return int(n);
    }
    static Ap01HttpReply handle(void *p,const Ap01HttpRequest &r,uint64_t now){
        auto &s=*(Stream *)p;++s.calls;assert(now==1);
        assert(r.length==s.body.size()&&!memcmp(r.body,s.body.data(),r.length));
        if(s.workspace){assert(r.body>=s.workspace->bytes&&r.body+r.length<=s.workspace->bytes+sizeof(s.workspace->bytes));}
        Ap01HttpReply reply;reply.status=200;if(!s.emptyReply)reply.bytes="{\"ok\":true}";return reply;
    }
    bool run(bool maintenance=true){
        return ap01ServeNativeHttp0041(this,handle,maintenance,{this,read,write},1,5000,workspace);
    }
};
static Stream request(const char *path,size_t n,Ap01HttpWorkspace0041 *workspace){
    Stream s;s.workspace=workspace;s.body.resize(n);
    for(size_t i=0;i<n;++i)s.body[i]=char(i%251);
    s.input=std::string("POST ")+path+" HTTP/1.1\r\nContent-Length: "+std::to_string(n)+"\r\n\r\n"+s.body;
    return s;
}
int main(){
    Ap01HttpWorkspace0041 workspace;memset(&workspace,0xa5,sizeof(workspace));
    denyArrays=true;allocations=0;
    for(size_t n:{size_t(0),size_t(1),size_t(4096),size_t(32768),size_t(1)}){
        auto s=request("/api/firmware/chunk",n,&workspace);
        assert(s.run()&&s.calls==1&&s.output.find("HTTP/1.1 200 ")==0&&allocations==0);
    }
    auto large=request("/api/firmware/chunk",32769,&workspace);
    assert(large.run()&&!large.calls&&large.output.find("HTTP/1.1 413 ")==0&&allocations==0);
    auto other=request("/health",4097,&workspace);
    assert(other.run()&&!other.calls&&other.output.find("HTTP/1.1 413 ")==0);
    auto app=request("/api/firmware/chunk",4097,&workspace);
    assert(app.run(false)&&!app.calls&&app.output.find("HTTP/1.1 413 ")==0);
    auto truncated=request("/api/firmware/chunk",32768,&workspace);truncated.input.pop_back();
    assert(!truncated.run()&&!truncated.calls&&allocations==0);
    auto exhausted=request("/health",0,nullptr);
    assert(exhausted.run()&&!exhausted.calls&&exhausted.output.find("HTTP/1.1 503 ")==0&&allocations==1);
    allocations=0;auto empty=request("/health",0,&workspace);empty.emptyReply=true;
    assert(empty.run()&&empty.calls==1&&allocations==0);
    assert(empty.output.find("HTTP/1.1 503 ")==0&&empty.output.find("\"result\":\"unknown\"")!=std::string::npos);
    assert(empty.output.find("query_original_operation")!=std::string::npos);
    denyArrays=false;allocations=0;
    auto fallback=request("/api/firmware/chunk",32768,nullptr);
    assert(fallback.run()&&fallback.calls==1&&allocations==2);
    puts("maintenance HTTP workspace: zero parser allocations under injected exhaustion; empty/small/max/reuse, limits, truncation and fallback passed");
}
