#include "native_device_code_menu_0041.h"
#include "native_device_code_0041.h"
#include "native_device_code_font_0041.h"
#include "native_vfs_0041.h"
#include "native_wifi_profiles_port_0041.h"
#include "native_wifi_switch_0041.h"
#include <memory>
#include <new>
#include <stddef.h>
#include <string.h>

#ifndef AP01_MENU_ROM_FN
#define AP01_MENU_ROM_FN(address, type) ((type)(uintptr_t)(address))
#endif

namespace {
using Object = void *;
struct WifiRow {char ssid[33]={};bool current=false;};
struct Context {
    Object page = nullptr;
    Object window = nullptr;
    bool submenu = false;
    unsigned selected = 0;
    bool uncertain = false;
    char code[9] = {};
    bool wifi=false,stockDetail=false,wifiReadError=false,mainUnordered=false;
    unsigned returnIndex=0,wifiCount=0;
    int wifiPhase=-1;
    Object wifiTimer=nullptr;
    std::unique_ptr<WifiRow[]> networks;
};
static_assert(offsetof(Context,code)==17&&offsetof(Context,wifiPhase)==40,"0041 menu probe ABI");
__attribute__((section(".ap01_menu_budget"),used))
static const uint32_t menuBudget[]={sizeof(Context),sizeof(WifiRow),sizeof(Ap01WifiProfiles0041),9};
void *&userData(Object object) { return *(void **)((uint8_t *)object + 0x10); }
Object child(Object object, int index) {
    return AP01_MENU_ROM_FN(0xa00dcee4, Object (*)(Object, int))(object, index);
}
unsigned children(Object object) {
    return AP01_MENU_ROM_FN(0xa00dd144, unsigned (*)(Object))(object);
}
void destroy(Object object) {
    if (object) AP01_MENU_ROM_FN(0xa00ded6c, void (*)(Object))(object);
}
void text(Object label, const char *value) {
    AP01_MENU_ROM_FN(0xa0091b3a, void (*)(Object, const char *))(label, value);
}
void font(Object label, bool selected, bool number = false) {
    AP01_MENU_ROM_FN(0xa019d0ae, void (*)(Object, const void *))
        (label, number ? ap01DeviceCodeNumberFont0041() : ap01DeviceCodeFont0041(selected));
}
void color(Object object, uint32_t value) {
    AP01_MENU_ROM_FN(0xa019cd48, void (*)(Object, uint32_t))(object, value);
}
void background(Object object, uint32_t value) {
    AP01_MENU_ROM_FN(0xa019cd76, void (*)(Object, unsigned))(object, 255);
    AP01_MENU_ROM_FN(0xa019cd92, void (*)(Object, uint32_t))(object, value);
}
void registerEvent(Object object, void (*callback)(void *), unsigned filter, void *user) {
    AP01_MENU_ROM_FN(0xa01ad654, void (*)(Object, void (*)(void *), unsigned, void *))
        (object, callback, filter, user);
}
void original(void *event) {
    AP01_MENU_ROM_FN(0xa00fd1ac, void (*)(void *))(event);
}
void **pageData(Context &context) {
    auto metadata = (void **)userData(context.page);
    return metadata ? (void **)metadata[1] : nullptr;
}
void cleanup(void *event) {
    auto words = (uintptr_t *)event;
    if ((words[2] & ~0x8000u) != 0x29) return;
    auto context = (Context *)words[3];
    if (context) {
        if(context->wifiTimer) AP01_MENU_ROM_FN(0xa008ae58,void (*)(void *))(context->wifiTimer);
        memset(context->code,0,sizeof(context->code));delete context;
    }
}
void orderMain(Context &,Object);
unsigned mainChild(unsigned);
Object mainList(Object parent, Context *context) {
    Object list = AP01_MENU_ROM_FN(0xa01a2c02, Object (*)(Object))(parent);
    if (!list || !context) return list;
    Object row = AP01_MENU_ROM_FN(0xa019cdc0, Object (*)(Object, const char *, int, int))
        (list, "", 0, 0);
    if (!row) return list;
    userData(row) = context;
    font(child(row, 0), false);
    text(child(row, 0), "\u8bbe\u5907\u7801");
    AP01_MENU_ROM_FN(0xa00de128, void (*)(Object, int))(row, 6);
    userData(child(list,0))=context;
    Object wifi=AP01_MENU_ROM_FN(0xa019cdc0,Object (*)(Object,const char *,int,int))(list,"",0,0);
    if(!wifi){destroy(list);return nullptr;}
    font(child(wifi,0),false,true);text(child(wifi,0),"Wi-Fi");
    // Preserve the stock logical row order for Version badge callbacks.
    context->mainUnordered=true;orderMain(*context,list);
    return list;
}
Object codeList(Object parent, Context &context) {
    // Reuse the exact original settings container, including flex, padding,
    // scroll direction and position. Only its rows are replaced.
    Object list = AP01_MENU_ROM_FN(0xa01a2c02, Object (*)(Object))(parent);
    if (!list) return nullptr;
    while (children(list)) destroy(child(list, -1));
    const char *labels[] = {context.code[0] ? context.code :
                           context.uncertain ? "\u7ed3\u679c\u5f85\u786e\u8ba4" : "\u8bfb\u53d6\u5931\u8d25",
                           "\u91cd\u65b0\u751f\u6210", "\u8fd4\u56de\u4e3b\u83dc\u5355"};
    for (unsigned index = 0; index < 3; ++index) {
        Object row = index == 2 ?
            AP01_MENU_ROM_FN(0xa019ce64, Object (*)(Object, int, int))(list, 0, 0) :
            AP01_MENU_ROM_FN(0xa019cdc0, Object (*)(Object, const char *, int, int))
                (list, "", 0, 0);
        if (!row) { destroy(list); return nullptr; }
        if (index == 0) userData(row) = &context;
        font(child(row, 0), false, index == 0); text(child(row, 0), labels[index]);
        // These are a readout and an action, not navigation into another page.
        if (index < 2) {
            Object arrow = child(row, 1);
            if (arrow) AP01_MENU_ROM_FN(0xa00d8f7c, void (*)(Object, uint32_t))(arrow, 1);
        }
    }
    return list;
}
Object wifiList(Object parent,Context &context) {
    auto snapshot=std::unique_ptr<Ap01WifiProfiles0041>(new(std::nothrow) Ap01WifiProfiles0041);
    bool loaded=snapshot&&!ap01WifiProfilesRead0041(ap01WifiProfilesNativePort0041(nullptr,nullptr),*snapshot);
    context.wifiReadError=!loaded;
    unsigned count=loaded?snapshot->count:0;
    int phase=ap01WifiSelectionState0041();
    if(loaded&&((phase>=Ap01WifiSwitch0041::Queued&&phase<=Ap01WifiSwitch0041::Restoring)||phase==Ap01WifiSwitch0041::ResultUnknown))
        for(unsigned i=0;i<count;++i)snapshot->profiles[i].current=false;
    std::unique_ptr<WifiRow[]> names(count?new(std::nothrow) WifiRow[count]:nullptr);
    if(count&&!names)return nullptr;
    for(unsigned i=0;i<count;++i){strcpy(names[i].ssid,snapshot->profiles[i].ssid);names[i].current=snapshot->profiles[i].current;}
    Object list=AP01_MENU_ROM_FN(0xa01a2c02,Object (*)(Object))(parent);
    if(!list)return nullptr;
    while(children(list))destroy(child(list,-1));
    for(unsigned i=0;i<=count;++i){
        Object row=i==count?AP01_MENU_ROM_FN(0xa019ce64,Object (*)(Object,int,int))(list,0,0):
            AP01_MENU_ROM_FN(0xa019cdc0,Object (*)(Object,const char *,int,int))(list,"",0,0);
        if(!row){destroy(list);return nullptr;}
        userData(row)=&context;
        font(child(row,0),false,i<count);
        if(i<count){
            Object label=child(row,0);
            AP01_MENU_ROM_FN(0xa019d0ae,void (*)(Object,const void *))(label,ap01WifiSsidFont0041());
            // 0041 lv_label_t recovered at a0092022/a0091f8a: mode is
            // low4 bits at5c, static-text bit4. New labels have no animation
            // or DOT allocation; CLIP4 gives a bounded single line.
            auto &mode=*((uint8_t *)label+0x5c);mode=(mode&0xf0)|4;
            AP01_MENU_ROM_FN(0xa00d8e96,void (*)(Object,int,int))(label,225,26);
            text(label,names[i].ssid);
            destroy(child(row,1));
            Object mark=AP01_MENU_ROM_FN(0xa00a62ee,Object (*)(Object,Object,const void *,int,int,uint32_t,int,int,int))
                (row,row,(void *)0x62fc54d0,3,2,0x89d8f3,7,0x101,0);
            if(!mark){destroy(list);return nullptr;}
            if(!names[i].current)AP01_MENU_ROM_FN(0xa00d8f7c,void (*)(Object,uint32_t))(mark,1);
        }
    }
    context.networks=std::move(names);context.wifiCount=count;context.wifiPhase=-1;
    return list;
}
unsigned mainChild(unsigned visual){return visual<2?visual:visual==2?8:visual-1;}
void orderMain(Context &context,Object list) {
    if(!context.mainUnordered||!list||children(list)!=9)return;
    // Recovered 0041 layout API: a00e6996 writes LAYOUT property22.
    // Use native absolute row positions while retaining Version's logical3
    // for its stock badge updater; no inferred translate-style enum.
    AP01_MENU_ROM_FN(0xa00df94c,void (*)(Object,unsigned,int,unsigned))(list,22,0,0);
    for(unsigned visual=0;visual<9;++visual)
        AP01_MENU_ROM_FN(0xa00d92ec,void (*)(Object,unsigned,int,int))
            (child(list,mainChild(visual)),1,0,int(visual)*73);
    context.mainUnordered=false;
}
void wifiPoll(void *timer) {
    if(!timer)return;
    auto context=*(Context **)((uint8_t *)timer+12);
    if(!context)return;
    if(!context->submenu)return;
    if(!context->wifi)return;
    int phase=ap01WifiSelectionState0041();if(phase==context->wifiPhase)return;
    context->wifiPhase=phase;auto data=pageData(*context);if(!data)return;
    const char *title=phase==Ap01WifiSwitch0041::Queued||phase==Ap01WifiSwitch0041::Connecting||phase==Ap01WifiSwitch0041::Saving?"\u8fde\u63a5\u4e2d":
        phase==Ap01WifiSwitch0041::Restoring?"\u6b63\u5728\u6062\u590d":
        phase==Ap01WifiSwitch0041::Failed?"\u5207\u6362\u5931\u8d25":
        phase==Ap01WifiSwitch0041::RecoveryFailed?"\u6062\u590d\u5931\u8d25":
        phase==Ap01WifiSwitch0041::ResultUnknown?"\u7ed3\u679c\u5f85\u786e\u8ba4":"Wi-Fi";
    text(data[0],context->wifiReadError?"\u8bfb\u53d6\u5931\u8d25":title);
    if(phase==Ap01WifiSwitch0041::Connected||phase==Ap01WifiSwitch0041::Failed){
        auto port=ap01WifiProfilesNativePort0041(nullptr,nullptr);char ssid[33]={},password[65]={};
        if(port.current(nullptr,ssid,sizeof(ssid),password,sizeof(password)))return;
        memset(password,0,sizeof(password));
        for(unsigned i=0;i<context->wifiCount;++i){
            auto &row=context->networks[i];row.current=!strcmp(row.ssid,ssid);
            AP01_MENU_ROM_FN(row.current?0xa00d9044:0xa00d8f7c,void (*)(Object,uint32_t))(child(child(data[2],i),1),1);
        }
    }
}
void select(Context &context, Object list, unsigned previous, unsigned next) {
    Object oldRow=child(list,context.submenu?previous:mainChild(previous)), newRow=child(list,context.submenu?next:mainChild(next));
    background(oldRow, 0x262626); background(newRow, 0x22363d);
    Object oldLabel = child(oldRow, 0), newLabel = child(newRow, 0);
    if (context.submenu || previous == 2 || previous == 7) font(oldLabel, false, context.wifi ? previous<context.wifiCount : context.submenu ? previous==0 : previous==2);
    else AP01_MENU_ROM_FN(0xa019d0ae, void (*)(Object, const void *))(oldLabel, (void *)0xa025488c);
    if (context.submenu || next == 2 || next == 7) font(newLabel, true, context.wifi ? next<context.wifiCount : context.submenu ? next==0 : next==2);
    else AP01_MENU_ROM_FN(0xa019d0ae, void (*)(Object, const void *))(newLabel, (void *)0xa055fb7c);
    if(context.wifi) {
        if(previous<context.wifiCount)AP01_MENU_ROM_FN(0xa019d0ae,void (*)(Object,const void *))(oldLabel,ap01WifiSsidFont0041());
        if(next<context.wifiCount)AP01_MENU_ROM_FN(0xa019d0ae,void (*)(Object,const void *))(newLabel,ap01WifiSsidFont0041());
    }
    Object oldArrow = child(oldRow, 1), newArrow = child(newRow, 1);
    unsigned back = context.wifi ? context.wifiCount : context.submenu ? 2 : 8;
    if (oldArrow) color(oldArrow, previous == back ? 0xffffff : context.wifi ? 0x89d8f3 : 0x808080);
    if (newArrow) color(newArrow, next == back ? 0xffffff : 0x89d8f3);
    // Preserve the stock paired-row scroll positions (2:141, 4:287, 6:400).
    int y = next < 2 ? 0 : int(next/2)*146-5;
    AP01_MENU_ROM_FN(0xa00de5dc, void (*)(Object, int, unsigned))(list, y, 1);
    context.selected = next;
}
bool randomBytes(void *, uint8_t *out, size_t length) {
    int fd = AP01_MENU_ROM_FN(0xa003f4f6, int (*)(const char *, int, ...))("/dev/urandom", 1);
    if (fd < 0) return false;
    size_t done = 0;
    while (done < length) {
        int n = AP01_MENU_ROM_FN(0xa003f6a2, int (*)(int, void *, size_t))(fd, out + done, length - done);
        if (n <= 0 || size_t(n) > length - done) break;
        done += n;
    }
    AP01_MENU_ROM_FN(0xa0026888, int (*)(int))(fd);
    return done == length;
}
void resetTimer(void **data) {
    if (data[3]) {
        AP01_MENU_ROM_FN(0xa008bd70, void (*)(Object))(data[3]);
        AP01_MENU_ROM_FN(0xa008c2d0, void (*)(Object))(data[3]);
    }
}
bool replaceList(Context &context, bool submenu, bool wifi=false) {
    auto data = pageData(context);
    if (!data) return false;
    Object next = wifi ? wifiList(context.page,context) : submenu ? codeList(context.page, context) : mainList(context.page, &context);
    if (!next || children(next) != (wifi ? context.wifiCount+1 : submenu ? 3u : 9u)) { destroy(next); return false; }
    Object previous = data[2]; data[2] = next;
    unsigned returnIndex=context.wifi?2:7;
    context.submenu=submenu;context.wifi=wifi;context.selected=0;
    text(data[0], "");
    if (submenu) AP01_MENU_ROM_FN(0xa019d0ae, void (*)(Object, const void *))
        (data[0], ap01DeviceCodeTitleFont0041());
    else AP01_MENU_ROM_FN(0xa019d0ae, void (*)(Object, const void *))(data[0], (void *)0xa02548d4);
    if(!submenu)orderMain(context,next);
    text(data[0],wifi?"Wi-Fi":submenu?"\u8bbe\u5907\u7801":"\u8bbe\u7f6e");
    select(context,next,0,wifi?0:submenu?1:returnIndex);
    if(!submenu)context.networks.reset();
    destroy(previous); resetTimer(data); return true;
}
void event(void *raw) {
    auto words = (uintptr_t *)raw;
    Object page = nullptr; void **pageValues = nullptr;
    int found = AP01_MENU_ROM_FN(0xa00a72ae, int (*)(Object, unsigned, Object *, void ***))
        ((Object)words[0], 0x1a, &page, &pageValues);
    Object list = found && pageValues ? pageValues[2] : nullptr;
    unsigned rows = list ? children(list) : 0;
    Object owner = rows ? child(list,0) : nullptr;
    auto context = owner ? (Context *)userData(owner) : nullptr;
    if (!context) { original(raw); return; }
    unsigned code = words[2] & ~0x8000u;
    if (code != 0x11) { original(raw); return; }
    orderMain(*context,list);
    auto state = (uint8_t *)userData(context->window);
    if (!state) {original(raw);return;}
    if(state[2]!=0x1a){
        original(raw);return;
    }
    if(context->stockDetail){state[1]=uint8_t(0x30+context->returnIndex);context->stockDetail=false;}
    auto data = pageData(*context);
    if (!data || !data[2]) return;
    *(volatile uint8_t *)(uintptr_t)0x62fc403a = 1;
    if (AP01_MENU_ROM_FN(0xa00a769a, int (*)())()) return;
    int key = AP01_MENU_ROM_FN(0xa00d8af6, int (*)(void *))(raw);
    if (!context->submenu) context->selected = state[1] >= 0x30 && state[1] <= 0x38 ? state[1] - 0x30 : 0;
    unsigned selected=context->selected,count=context->wifi?context->wifiCount+1:context->submenu?3:9;
    if (key == 0x13 || key == 0x14) {
        unsigned first = context->submenu&&!context->wifi ? 1 : 0; // Numeric readout is never selectable.
        int next = int(selected) + (key == 0x13 ? 1 : -1);
        if (next < int(first)) next = count - 1;
        else if (unsigned(next) >= count) next = first;
        select(*context, data[2], selected, unsigned(next));
        if (!context->submenu) state[1] = uint8_t(0x30 + context->selected);
        resetTimer(data); return;
    }
    if (key != 10) { original(raw); return; }
    // The stock long-press handler consumes the following Enter with this flag.
    if (*((uint8_t *)context->window + 100)) {
        *((uint8_t *)context->window + 100) = 0; resetTimer(data); return;
    }
    if (!context->submenu) {
        if(selected==2){replaceList(*context,true,true);resetTimer(data);return;}
        if(selected<7){
            context->stockDetail=true;context->returnIndex=selected;
            state[1]=uint8_t(0x30+(selected>2?selected-1:selected));original(raw);return;
        }
        if(selected==8){state[1]=0x36;original(raw);return;}
        auto io = ap01RomVfs();
        int result = context->uncertain ? ap01DeviceCodeLoad0041(io, context->code) :
            ap01DeviceCodeEnsure0041(io, randomBytes, nullptr, context->code);
        context->uncertain = result == -115 || (context->uncertain && result != 0);
        if (result) memset(context->code, 0, sizeof(context->code));
        replaceList(*context, true); return;
    }
    if(context->wifi){
        if(selected==context->wifiCount){
            if(replaceList(*context,false))state[1]=0x32;
        }else{
            int result=context->wifiTimer?ap01WifiSelect0041(context->networks[selected].ssid):-12;
            int phase=ap01WifiSelectionState0041();
            bool inFlight=(phase>=Ap01WifiSwitch0041::Queued&&phase<=Ap01WifiSwitch0041::Restoring)||phase==Ap01WifiSwitch0041::ResultUnknown;
            if(result&&!(result==-16&&inFlight))text(data[0],"\u5207\u6362\u5931\u8d25");
            else{context->wifiPhase=-1;wifiPoll(context->wifiTimer);}
        }
        resetTimer(data);return;
    }
    if (selected == 2) {
        if (replaceList(*context, false)) state[1] = 0x37;
        return;
    }
    if (selected == 1) {
        auto io = ap01RomVfs();
        int result = context->uncertain ? ap01DeviceCodeLoad0041(io, context->code) :
            ap01DeviceCodeRegenerate0041(io, randomBytes, nullptr, context->code);
        context->uncertain = result == -115 || (context->uncertain && result != 0);
        if (!result) text(child(child(data[2], 0), 0), context->code);
        else {
            if (context->uncertain) memset(context->code, 0, sizeof(context->code));
            text(child(child(data[2], 0), 0), context->uncertain ?
                "\u7ed3\u679c\u5f85\u786e\u8ba4" : "\u4fdd\u5b58\u5931\u8d25");
        }
    }
    resetTimer(data);
}
}

extern "C" void *ap01SettingsList0041(void *parent) {
    auto context = new(std::nothrow) Context;
    Object list = mainList(parent, context);
    if (!context) return list;
    if (!list || children(list) != 9) { delete context; return list; }
    context->page = parent; context->window = *(void **)((uint8_t *)parent + 4);
    registerEvent(parent, cleanup, 0x29, context);
    context->wifiTimer=AP01_MENU_ROM_FN(0xa008bc64,Object (*)(void (*)(void *),unsigned,void *))(wifiPoll,200,context);
    return list;
}

extern "C" void ap01SettingsRegister0041(void *object, void (*callback)(void *), unsigned filter, void *user) {
    if ((uintptr_t)callback != 0xa00fd1ac) { registerEvent(object, callback, filter, user); return; }
    // Registration can precede construction of the settings page. Resolve its
    // context through the live native page/list when each event is dispatched.
    registerEvent(object, event, filter, nullptr);
}
