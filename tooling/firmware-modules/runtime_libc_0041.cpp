// Pure freestanding support shared by resident firmware and the file App.
// No ROM address, allocator state, constructor, or operating-system call.
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#ifdef AP01_RUNTIME_LIBC_HOST_TEST
#define memcpy ap01_test_memcpy
#define memmove ap01_test_memmove
#define memset ap01_test_memset
#define memcmp ap01_test_memcmp
#define memchr ap01_test_memchr
#define strlen ap01_test_strlen
#define strcmp ap01_test_strcmp
#define strncmp ap01_test_strncmp
#define strcpy ap01_test_strcpy
#define strchr ap01_test_strchr
#define strstr ap01_test_strstr
#define strtol ap01_test_strtol
#define strftime ap01_test_strftime
#endif
extern "C" {
void *memcpy(void *d,const void *s,size_t n) noexcept { auto *p=(uint8_t *)d;auto *q=(const uint8_t *)s;while(n--)*p++=*q++;return d; }
void *memmove(void *d,const void *s,size_t n) noexcept {
    auto *p=(uint8_t *)d;auto *q=(const uint8_t *)s;
    if ((uintptr_t)p <= (uintptr_t)q) return memcpy(d,s,n);
    p+=n;q+=n;while(n--)*--p=*--q;return d;
}
void *memset(void *d,int c,size_t n) noexcept { auto *p=(uint8_t *)d;while(n--)*p++=c;return d; }
int memcmp(const void *a,const void *b,size_t n) noexcept {auto *p=(const uint8_t *)a,*q=(const uint8_t *)b;while(n--){if(*p!=*q)return int(*p)-*q;++p;++q;}return 0;}
void *memchr(const void *s,int c,size_t n) noexcept {auto *p=(const uint8_t *)s;while(n--){if(*p==(uint8_t)c)return (void *)p;++p;}return nullptr;}
size_t strlen(const char *s) noexcept {const char *p=s;while(*p)++p;return p-s;}
int strcmp(const char *a,const char *b) noexcept {while(*a&&*a==*b){++a;++b;}return (unsigned char)*a-(unsigned char)*b;}
int strncmp(const char *a,const char *b,size_t n) noexcept {while(n--){if(*a!=*b||!*a)return (unsigned char)*a-(unsigned char)*b;++a;++b;}return 0;}
char *strcpy(char *a,const char *b) noexcept {char *p=a;while((*p++=*b++)){}return a;}
char *strchr(const char *s,int c) noexcept {do {if(*s==(char)c)return (char *)s;}while(*s++);return nullptr;}
char *strstr(const char *s,const char *needle) noexcept {if(!*needle)return (char *)s;for(;*s;++s){size_t i=0;while(needle[i]&&s[i]==needle[i])++i;if(!needle[i])return (char *)s;}return nullptr;}
long strtol(const char *s,char **end,int base) noexcept {
    const char *start=s;while(*s==' '||*s=='\t'||*s=='\n'||*s=='\r')++s;
    bool negative=*s=='-';if(*s=='+'||*s=='-')++s;
    if (!base) base=*s=='0'?8:10;
    if ((base==16||base==8) && s[0]=='0' && (s[1]=='x'||s[1]=='X')) {base=16;s+=2;}
    const char *digits=s;unsigned long value=0,limit=negative?0x80000000u:0x7fffffffu;bool overflow=false;
    while(*s){unsigned d=*s>='0'&&*s<='9'?*s-'0':*s>='a'&&*s<='z'?*s-'a'+10:*s>='A'&&*s<='Z'?*s-'A'+10:36;
        if(d>=(unsigned)base)break;if(value>(limit-d)/(unsigned)base)overflow=true;else if(!overflow)value=value*base+d;++s;}
    if(end)*end=(char *)(s==digits?start:s);if(overflow)value=limit;
    return negative?long(-int64_t(value)):long(value);
}
size_t strftime(char *out, size_t length, const char *format, const struct tm *value) noexcept {
    if (!length) return 0;
    int n = !strcmp(format,"%H:%M") ? snprintf(out,length,"%02d:%02d",value->tm_hour,value->tm_min) :
        !strcmp(format,"%m/%d") ? snprintf(out,length,"%02d/%02d",value->tm_mon+1,value->tm_mday) :
        !strcmp(format,"%m-%d %H:%M") ? snprintf(out,length,"%02d-%02d %02d:%02d",value->tm_mon+1,value->tm_mday,value->tm_hour,value->tm_min) : -1;
    if (n < 0 || size_t(n) >= length) {out[0]=0;return 0;}return n;
}
}
