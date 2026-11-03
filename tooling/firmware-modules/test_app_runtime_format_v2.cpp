#include <cassert>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <climits>
#include <initializer_list>
extern "C" int ap01_app_snprintf_v2(char *,size_t,const char *,...) noexcept;
template<class... Args> void check(const char *format,Args... args){
    for(size_t size:{0u,1u,2u,8u,16u,32u,128u,256u}){
        char actual[258],expected[258];memset(actual,0x6a,sizeof(actual));memset(expected,0x6a,sizeof(expected));
        int a=ap01_app_snprintf_v2(size?actual+1:nullptr,size,format,args...);
        int b=snprintf(size?expected+1:nullptr,size,format,args...);
        assert(a==b&&!memcmp(actual,expected,sizeof(actual)));
    }
}
int main(){
    for(long long n:{LLONG_MIN,LLONG_MIN+1,-2147483648LL,-1LL,0LL,1LL,2147483647LL,LLONG_MAX}){
        check("%lld",n);check("%024lld",n);check("%-24lld",n);check("%24lld",n);
    }
    uint64_t value=0x123456789abcdef;
    for(unsigned i=0;i<5000;++i){value=value*6364136223846793005ULL+1;
        check("%llu",(unsigned long long)value);check("%08x",unsigned(value));check("%016llX",(unsigned long long)value);
        check("%d",int(value));check("%02u:%02u",unsigned(value%24),unsigned(value%60));
    }
    check("%ld/%lu",LONG_MIN,ULONG_MAX);check("%% %s %c %10s %-10s","body",'x',"left","right");
    check("HTTP/1.1 %d Response\r\nContent-Type: %s\r\nContent-Length: %u\r\nConnection: close\r\nCache-Control: no-store\r\n\r\n",503,"application/json",123u);
    check("{\"result\":\"rejected\",\"error\":\"%s\",\"stage\":\"http_parse\",\"action\":\"correct_request\"}","content_length");
    check("%02d:%02d",-1,59);check("%c",0);check("%-024lld",LLONG_MIN);
    char buffer[8];
    for(const char *bad:{"%m","%n","%f","%.2d","%*d","%ls","%0s","%","%2147483648d"}){
        memset(buffer,0x6a,sizeof(buffer));
        assert(ap01_app_snprintf_v2(buffer+1,6,bad)==-1);
        assert(buffer[0]==0x6a&&buffer[1]==0&&buffer[7]==0x6a);
    }
    assert(ap01_app_snprintf_v2(nullptr,1,"x")==-1);
    assert(ap01_app_snprintf_v2(buffer,sizeof(buffer),nullptr)==-1);
    assert(ap01_app_snprintf_v2(buffer,sizeof(buffer),"%s",static_cast<const char *>(nullptr))==-1);
    // Counting huge padding must be bounded by output capacity, not field width.
    assert(ap01_app_snprintf_v2(buffer,sizeof(buffer),"%2147483647d",1)==INT_MAX);
    assert(!strcmp(buffer,"       "));
    assert(ap01_app_snprintf_v2(nullptr,0,"%2147483647d",1)==INT_MAX);
    assert(ap01_app_snprintf_v2(buffer,sizeof(buffer),"%2147483647d!",1)==-1&&buffer[0]==0);
    puts("formatter: libc differential, truncation guards, integer limits and rejection checks passed");
    return 0;
}
