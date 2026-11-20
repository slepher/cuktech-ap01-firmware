#include <time.h>
#include <stdint.h>
#include <string.h>

#if defined(__riscv)
static_assert(sizeof(time_t) == 4 && sizeof(long) == 4,
              "0041 requires the 32-bit time ABI; compile with _USE_LONG_TIME_T");
#endif

bool ap01Calendar(time_t epoch, struct tm &result) {
    if (epoch < 0 || uint64_t(epoch) > UINT32_MAX) return false;
    // Match the AP01's local civil clock (Hong Kong, UTC+8). A background
    // task has no TZ environment; tzset/localtime there silently uses UTC.
    constexpr int localOffset = 8 * 60 * 60;
    // Bounded Gregorian conversion for the supported uint32 epoch range.
    // Keep this pure so a file App does not import the ROM's tm layout/helper.
    uint64_t seconds=uint64_t(epoch)+localOffset;
    uint32_t days=uint32_t(seconds/86400),remaining=days,year=1970;
    auto leap=[](uint32_t y){return y%4==0&&(y%100!=0||y%400==0);};
    while(remaining>=uint32_t(leap(year)?366:365)){remaining-=leap(year)?366:365;++year;}
    uint32_t dayOfYear=remaining,month=0;
    const uint8_t monthDays[]={31,28,31,30,31,30,31,31,30,31,30,31};
    for(;month<11;++month){uint32_t n=monthDays[month]+(month==1&&leap(year)?1:0);
        if(remaining<n)break;remaining-=n;}
    result = tm{};
    result.tm_sec=int(seconds%60);result.tm_min=int(seconds/60%60);result.tm_hour=int(seconds/3600%24);
    result.tm_mday=int(remaining+1);result.tm_mon=int(month);result.tm_year=int(year)-1900;
    result.tm_wday=int((days+4)%7);result.tm_yday=int(dayOfYear);result.tm_isdst=0;
    return true;
}
