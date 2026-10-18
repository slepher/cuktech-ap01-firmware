#include "diagnostic_console.h"
static uint32_t left(const diagnostic_console_io *io,uint64_t end)
{
    uint64_t now=io->now_ms(io->ctx);
    return now>=end?0:end-now>UINT32_MAX?UINT32_MAX:(uint32_t)(end-now);
}
static int send_text(const diagnostic_console_io *io,const char *p,size_t size,uint64_t end)
{
    while(size){
        uint32_t timeout=left(io,end);if(!timeout)return -1;
        int n=io->write(io->ctx,p,size,timeout);
        if(!left(io,end)||n<=0||(size_t)n>size)return -1;
        p+=n;size-=(size_t)n;
    }
    return 0;
}
int diagnostic_console_authenticate(const diagnostic_console_io *io,const char *key,uint64_t end)
{
    if(!io||!io->read||!io->write||!io->now_ms||!key)return -1;
    for(unsigned i=0;i<64;i++){
        char c=key[i];
        if(!((c>='0'&&c<='9')||(c>='a'&&c<='f')||(c>='A'&&c<='F')))return -1;
    }
    if(key[64]||send_text(io,"AP01-DIAG/1\n",12,end))return -1;
    char line[71];unsigned used=0;
    while(used<sizeof(line)){
        uint32_t timeout=left(io,end);if(!timeout)return -1;
        char c;int n=io->read(io->ctx,&c,1,timeout);
        if(!left(io,end)||n!=1)return -1;
        if(c=='\n'){
            if(used&&line[used-1]=='\r')used--;
            unsigned difference=used^69u;
            static const char prefix[]="AUTH ";
            for(unsigned i=0;i<5;i++)difference|=i<used?(unsigned char)line[i]^(unsigned char)prefix[i]:1;
            for(unsigned i=0;i<64;i++)difference|=i+5<used?(unsigned char)line[i+5]^(unsigned char)key[i]:1;
            if(!difference)return 0;
            send_text(io,"ERR auth\n",9,end);return -1;
        }
        if((unsigned char)c<32&&c!='\r')return -1;
        if((unsigned char)c>126)return -1;
        line[used++]=c;
    }
    return -1;
}
enum diagnostic_operation diagnostic_console_operation(const diagnostic_console_io *io,uint64_t end)
{
    if(!io||!io->read||!io->now_ms)return DIAGNOSTIC_INVALID;
    static const char names[][10]={"","SHELL","STATUS","INTERRUPT","CLOSE","LOGS","FLASH"};
    char line[11];unsigned used=0;
    while(used<sizeof(line)){
        uint32_t timeout=left(io,end);if(!timeout)return DIAGNOSTIC_INVALID;
        char c;int n=io->read(io->ctx,&c,1,timeout);
        if(!left(io,end)||n!=1)return DIAGNOSTIC_INVALID;
        if(c=='\n'){
            if(used&&line[used-1]=='\r')used--;
            for(unsigned op=1;op<=6;op++){
                unsigned i=0;while(i<used&&names[op][i]&&names[op][i]==line[i])i++;
                if(i==used&&!names[op][i])return (enum diagnostic_operation)op;
            }
            return DIAGNOSTIC_INVALID;
        }
        if(c<'A'||c>'Z'){
            if(c!='\r')return DIAGNOSTIC_INVALID;
        }
        line[used++]=c;
    }
    return DIAGNOSTIC_INVALID;
}
int diagnostic_console_flash_range(const diagnostic_console_io *io,uint64_t end,uint32_t *address,uint32_t *length)
{
    if(!io||!io->read||!io->now_ms||!address||!length)return -1;
    uint32_t values[2]={0,0};
    for(unsigned i=0;i<18;i++){
        uint32_t timeout=left(io,end);if(!timeout)return -1;
        char c;int n=io->read(io->ctx,&c,1,timeout);
        if(!left(io,end)||n!=1)return -1;
        if(i==8){if(c!=' ')return -1;continue;}
        if(i==17){if(c!='\n')return -1;continue;}
        unsigned digit=c>='0'&&c<='9'?(unsigned)(c-'0'):c>='a'&&c<='f'?(unsigned)(c-'a'+10):
                       c>='A'&&c<='F'?(unsigned)(c-'A'+10):16;
        if(digit>15)return -1;
        unsigned field=i>8;values[field]=(values[field]<<4)|digit;
    }
    if(!values[1]||values[1]>65536||values[0]>0x1000000u-values[1])return -1;
    *address=values[0];*length=values[1];return 0;
}
