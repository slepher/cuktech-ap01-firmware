#include <cassert>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <ctime>
#include <initializer_list>
extern "C" {
void *ap01_test_memcpy(void *,const void *,size_t) noexcept;
void *ap01_test_memmove(void *,const void *,size_t) noexcept;
void *ap01_test_memset(void *,int,size_t) noexcept;
int ap01_test_memcmp(const void *,const void *,size_t) noexcept;
void *ap01_test_memchr(const void *,int,size_t) noexcept;
size_t ap01_test_strlen(const char *) noexcept;
int ap01_test_strcmp(const char *,const char *) noexcept;
int ap01_test_strncmp(const char *,const char *,size_t) noexcept;
char *ap01_test_strcpy(char *,const char *) noexcept;
char *ap01_test_strchr(const char *,int) noexcept;
char *ap01_test_strstr(const char *,const char *) noexcept;
long ap01_test_strtol(const char *,char **,int) noexcept;
size_t ap01_test_strftime(char *,size_t,const char *,const tm *) noexcept;
}
bool ap01Calendar(time_t,tm &);
int main(){
    char a[32]={},b[32]={};assert(ap01_test_memset(a,0x71,8)==a);memset(b,0x71,8);
    assert(ap01_test_memcpy(a+8,"abcdef",7)==a+8);memcpy(b+8,"abcdef",7);
    for(unsigned from=0;from<12;++from)for(unsigned to=0;to<12;++to){
        char x[32],y[32];memcpy(x,a,32);memcpy(y,b,32);
        ap01_test_memmove(x+to,x+from,12);memmove(y+to,y+from,12);assert(!memcmp(x,y,32));
    }
    assert(!ap01_test_memcmp(a,b,32)&&ap01_test_memcmp("a","b",1)<0);
    assert(ap01_test_memchr(a,'c',32)==a+10&&!ap01_test_memchr(a,'z',32));
    assert(ap01_test_strcpy(a,"hello")==a&&ap01_test_strlen(a)==5);
    assert(!ap01_test_strcmp(a,"hello")&&ap01_test_strcmp(a,"help")<0&&!ap01_test_strncmp(a,"help",3));
    assert(ap01_test_strchr(a,'l')==a+2&&ap01_test_strchr(a,0)==a+5);
    assert(ap01_test_strstr(a,"ell")==a+1&&ap01_test_strstr(a,"")==a&&!ap01_test_strstr(a,"no"));
    char *end=nullptr;assert(ap01_test_strtol(" -2147483648tail",&end,10)==INT32_MIN&&!strcmp(end,"tail"));
    assert(ap01_test_strtol("99999999999999999999",nullptr,10)==INT32_MAX);
    assert(ap01_test_strtol("-99999999999999999999",nullptr,10)==INT32_MIN);
    assert(ap01_test_strtol("0xff!",&end,0)==255&&*end=='!');
    assert(ap01_test_strtol("0755",nullptr,0)==493);
    // Independent libc reference for every supported epoch day at both ends.
    unsigned checked=0;
    for(uint64_t day=0;day<=UINT32_MAX/86400;++day)for(unsigned edge:{0u,86399u}){
        uint64_t epoch=day*86400+edge;if(epoch>UINT32_MAX)epoch=UINT32_MAX;
        time_t local=time_t(epoch)+8*60*60;tm expected{},actual{};
        assert(gmtime_r(&local,&expected)&&ap01Calendar(time_t(epoch),actual));
        assert(actual.tm_sec==expected.tm_sec&&actual.tm_min==expected.tm_min&&actual.tm_hour==expected.tm_hour);
        assert(actual.tm_mday==expected.tm_mday&&actual.tm_mon==expected.tm_mon&&actual.tm_year==expected.tm_year);
        assert(actual.tm_wday==expected.tm_wday&&actual.tm_yday==expected.tm_yday&&actual.tm_isdst==0);++checked;
        for(const char *format:{"%H:%M","%m/%d","%m-%d %H:%M"}){
            char x[32],y[32];auto n=ap01_test_strftime(x,sizeof(x),format,&actual);
            assert(n==strftime(y,sizeof(y),format,&expected)&&!strcmp(x,y));
        }
    }
    tm t{};assert(!ap01Calendar(-1,t)&&!ap01Calendar(time_t(UINT32_MAX)+1,t));
    a[0]='x';assert(!ap01_test_strftime(a,0,"%H:%M",&t)&&a[0]=='x');
    assert(!ap01_test_strftime(a,2,"%H:%M",&t)&&!a[0]);assert(!ap01_test_strftime(a,32,"%Y",&t)&&!a[0]);
    printf("pure runtime: memory/string/32-bit conversion and %u independent calendar cases (UTC+8, all epoch days, leap centuries) passed\n",checked);
}
