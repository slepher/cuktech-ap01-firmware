#include "native_device_code_menu_0041.h"
#include "native_device_code_0041.h"
#include "native_device_code_font_0041.h"
#include "native_vfs_0041.h"
#include <new>
#include <string.h>

#ifndef AP01_MENU_ROM_FN
#define AP01_MENU_ROM_FN(address, type) ((type)(uintptr_t)(address))
#endif

namespace {
using Object = void *;
struct Context {
    Object page = nullptr;
    Object window = nullptr;
    bool submenu = false;
    unsigned selected = 0;
    bool uncertain = false;
    char code[9] = {};
};
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
void font(Object label, bool selected) {
    AP01_MENU_ROM_FN(0xa019d0ae, void (*)(Object, const void *))
        (label, ap01DeviceCodeFont0041(selected));
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
    if (context) { memset(context->code, 0, sizeof(context->code)); delete context; }
}
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
        font(child(row, 0), false); text(child(row, 0), labels[index]);
    }
    return list;
}
void select(Context &context, Object list, unsigned previous, unsigned next) {
    Object oldRow = child(list, previous), newRow = child(list, next);
    background(oldRow, 0x262626); background(newRow, 0x22363d);
    Object oldLabel = child(oldRow, 0), newLabel = child(newRow, 0);
    if (context.submenu || previous == 6) font(oldLabel, false);
    else AP01_MENU_ROM_FN(0xa019d0ae, void (*)(Object, const void *))(oldLabel, (void *)0xa025488c);
    if (context.submenu || next == 6) font(newLabel, true);
    else AP01_MENU_ROM_FN(0xa019d0ae, void (*)(Object, const void *))(newLabel, (void *)0xa055fb7c);
    Object oldArrow = child(oldRow, 1), newArrow = child(newRow, 1);
    unsigned back = context.submenu ? 2 : 7;
    if (oldArrow) color(oldArrow, previous == back ? 0xffffff : 0x808080);
    if (newArrow) color(newArrow, next == back ? 0xffffff : 0x89d8f3);
    // Preserve the stock paired-row scroll positions (2:141, 4:287, 6:400).
    int y = next < 2 ? 0 : next < 4 ? 141 : next < 6 ? 287 : 400;
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
bool replaceList(Context &context, bool submenu) {
    auto data = pageData(context);
    if (!data) return false;
    Object next = submenu ? codeList(context.page, context) : mainList(context.page, &context);
    if (!next || children(next) != (submenu ? 3u : 8u)) { destroy(next); return false; }
    Object previous = data[2]; data[2] = next;
    context.submenu = submenu; context.selected = 0;
    text(data[0], "");
    if (submenu) AP01_MENU_ROM_FN(0xa019d0ae, void (*)(Object, const void *))
        (data[0], ap01DeviceCodeTitleFont0041());
    else AP01_MENU_ROM_FN(0xa019d0ae, void (*)(Object, const void *))(data[0], (void *)0xa02548d4);
    text(data[0], submenu ? "\u8bbe\u5907\u7801" : "\u8bbe\u7f6e");
    select(context, next, 0, submenu ? 0 : 6);
    destroy(previous); resetTimer(data); return true;
}
void event(void *raw) {
    auto words = (uintptr_t *)raw;
    Object page = nullptr; void **pageValues = nullptr;
    int found = AP01_MENU_ROM_FN(0xa00a72ae, int (*)(Object, unsigned, Object *, void ***))
        ((Object)words[0], 0x1a, &page, &pageValues);
    Object list = found && pageValues ? pageValues[2] : nullptr;
    unsigned rows = list ? children(list) : 0;
    Object owner = rows == 8 ? child(list, 6) : rows == 3 ? child(list, 0) : nullptr;
    auto context = owner ? (Context *)userData(owner) : nullptr;
    if (!context) { original(raw); return; }
    unsigned code = words[2] & ~0x8000u;
    if (code != 0x11) { original(raw); return; }
    auto state = (uint8_t *)userData(context->window);
    if (!state || state[2] != 0x1a) { original(raw); return; }
    auto data = pageData(*context);
    if (!data || !data[2]) return;
    *(volatile uint8_t *)(uintptr_t)0x62fc403a = 1;
    if (AP01_MENU_ROM_FN(0xa00a769a, int (*)())()) return;
    int key = AP01_MENU_ROM_FN(0xa00d8af6, int (*)(void *))(raw);
    if (!context->submenu) context->selected = state[1] >= 0x30 && state[1] <= 0x37 ? state[1] - 0x30 : 0;
    unsigned selected = context->selected, count = context->submenu ? 3 : 8;
    if (key == 0x13 || key == 0x14) {
        int next = int(selected) + (key == 0x13 ? 1 : -1);
        if (next >= 0 && unsigned(next) < count) select(*context, data[2], selected, unsigned(next));
        if (!context->submenu) state[1] = uint8_t(0x30 + context->selected);
        resetTimer(data); return;
    }
    if (key != 10) { original(raw); return; }
    // The stock long-press handler consumes the following Enter with this flag.
    if (*((uint8_t *)context->window + 100)) {
        *((uint8_t *)context->window + 100) = 0; resetTimer(data); return;
    }
    if (!context->submenu) {
        if (selected < 6) { original(raw); return; }
        if (selected == 7) { state[1] = 0x36; original(raw); return; }
        auto io = ap01RomVfs();
        int result = context->uncertain ? ap01DeviceCodeLoad0041(io, context->code) :
            ap01DeviceCodeEnsure0041(io, randomBytes, nullptr, context->code);
        context->uncertain = result == -115 || (context->uncertain && result != 0);
        if (result) memset(context->code, 0, sizeof(context->code));
        replaceList(*context, true); return;
    }
    if (selected == 2) {
        if (replaceList(*context, false)) state[1] = 0x36;
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
    if (!list || children(list) != 8) { delete context; return list; }
    context->page = parent; context->window = *(void **)((uint8_t *)parent + 4);
    registerEvent(parent, cleanup, 0x29, context);
    return list;
}

extern "C" void ap01SettingsRegister0041(void *object, void (*callback)(void *), unsigned filter, void *user) {
    if ((uintptr_t)callback != 0xa00fd1ac) { registerEvent(object, callback, filter, user); return; }
    // Registration can precede construction of the settings page. Resolve its
    // context through the live native page/list when each event is dispatched.
    registerEvent(object, event, filter, nullptr);
}
