// Private file-App formatter for the audited App's integer/string formats.
// No heap, ROM address, locale, floating conversion, or mutable global state.
// Unsupported conversions fail explicitly instead of consuming guessed args.
#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>
#include <limits.h>
namespace {
struct Output {
    char *bytes;size_t capacity;uint32_t count=0;bool okay=true;
    void repeat(char c,uint32_t n){
        if(n>uint32_t(INT_MAX)-count){okay=false;return;}
        size_t room=capacity&&count<capacity-1?capacity-1-count:0;
        size_t copy=n<room?n:room;for(size_t i=0;i<copy;++i)bytes[count+i]=c;
        count+=n;
    }
    void text(const char *s,uint32_t n){
        if(n>uint32_t(INT_MAX)-count){okay=false;return;}
        size_t room=capacity&&count<capacity-1?capacity-1-count:0;
        size_t copy=n<room?n:room;for(size_t i=0;i<copy;++i)bytes[count+i]=s[i];
        count+=n;
    }
    int finish(){
        if(capacity)bytes[okay?(count<capacity?count:capacity-1):0]=0;
        return okay?int(count):-1;
    }
};
int format(char *buffer,size_t capacity,const char *f,va_list args){
    if((capacity&&!buffer)||!f)return -1;
    Output out{buffer,capacity};
    while(*f&&out.okay){
        if(*f!='%'){out.repeat(*f++,1);continue;}
        ++f;if(*f=='%'){out.repeat('%',1);++f;continue;}
        bool left=false,zero=false;
        while(*f=='-'||*f=='0'){if(*f=='-')left=true;else zero=true;++f;}
        uint32_t width=0;
        while(*f>='0'&&*f<='9'){
            unsigned digit=unsigned(*f++-'0');
            if(width>(uint32_t(INT_MAX)-digit)/10){out.okay=false;break;}
            width=width*10+digit;
        }
        if(!out.okay)break;
        unsigned length=0;if(*f=='l'){++length;++f;if(*f=='l'){++length;++f;}}
        char type=*f;if(!type){out.okay=false;break;}++f;
        if(type=='s'||type=='c'){
            if(length||zero){out.okay=false;break;}
            char c=0;const char *text=nullptr;uint32_t n=0;
            if(type=='c'){c=char(va_arg(args,int));text=&c;n=1;}
            else {text=va_arg(args,const char *);if(!text){out.okay=false;break;}
                while(text[n]){if(n==uint32_t(INT_MAX)){out.okay=false;break;}++n;}}
            if(!out.okay)break;
            uint32_t padding=width>n?width-n:0;
            if(!left)out.repeat(' ',padding);
            out.text(text,n);if(left)out.repeat(' ',padding);continue;
        }
        bool sign=type=='d'||type=='i';
        if(!sign&&type!='u'&&type!='x'&&type!='X'){out.okay=false;break;}
        uint64_t value=0;bool negative=false;
        if(sign){
            int64_t number=length==2?va_arg(args,long long):length==1?va_arg(args,long):va_arg(args,int);
            negative=number<0;value=negative?uint64_t(0)-uint64_t(number):uint64_t(number);
        }else value=length==2?va_arg(args,unsigned long long):length==1?va_arg(args,unsigned long):va_arg(args,unsigned);
        unsigned base=type=='x'||type=='X'?16:10;char digits[24];uint32_t n=0;
        do {unsigned digit=unsigned(value%base);value/=base;
            digits[n++]=char(digit<10?'0'+digit:(type=='X'?'A':'a')+digit-10);
        }while(value);
        uint32_t field=n+(negative?1:0),padding=width>field?width-field:0;
        if(!left&&!zero)out.repeat(' ',padding);
        if(negative)out.repeat('-',1);
        if(!left&&zero)out.repeat('0',padding);
        while(n)out.repeat(digits[--n],1);
        if(left)out.repeat(' ',padding);
    }
    return out.finish();
}
}
extern "C" int ap01_app_snprintf_v2(char *out,size_t size,const char *pattern,...) noexcept {
    va_list args;va_start(args,pattern);int n=format(out,size,pattern,args);va_end(args);return n;
}
#ifndef AP01_RUNTIME_FORMAT_HOST_TEST
extern "C" int snprintf(char *out,size_t size,const char *pattern,...) noexcept {
    va_list args;va_start(args,pattern);int n=format(out,size,pattern,args);va_end(args);return n;
}
#endif
