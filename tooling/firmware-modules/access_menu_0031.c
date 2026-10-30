/* Exact original 0031 only. See access-menu-0031.md for address evidence.
 * All state belongs to the native Settings page; no App or writable globals. */
#include "device_code_0031.h"
#include <stdint.h>
#include <stddef.h>
#ifndef AP01_ACCESS_FN
#define AP01_ACCESS_FN(address, type) ((type)(uintptr_t)(address))
#endif
#ifndef AP01_ACCESS_ACTIVITY
#define AP01_ACCESS_ACTIVITY() (*(volatile unsigned char *)(uintptr_t)0x62fc4cde = 1)
#endif
typedef void *Object;
#ifndef AP01_ACCESS_USER
#define AP01_ACCESS_USER(o) ((void **)((unsigned char *)(o) + 0x10))
#endif
#ifndef AP01_ACCESS_PARENT
#define AP01_ACCESS_PARENT(o) (*(Object *)((unsigned char *)(o) + 4))
#endif
typedef struct {
    Object page, window, main;
    unsigned selected;
    int submenu,uncertain;
    char code[9];
} Context;
static void **user(Object o) { return AP01_ACCESS_USER(o); }
static Object child(Object o, int i)
{ return AP01_ACCESS_FN(0xa00c5d84, Object (*)(Object,int))(o,i); }
static unsigned children(Object o)
{ return AP01_ACCESS_FN(0xa00c5fe4, unsigned (*)(Object))(o); }
static void destroy(Object o)
{ if (o) AP01_ACCESS_FN(0xa00c7466, void (*)(Object))(o); }
static void font(Object o, const void *face)
{ AP01_ACCESS_FN(0xa01932a2, void (*)(Object,const void *))(o,face); }
static void text(Object o, const char *s)
{ AP01_ACCESS_FN(0xa0086bcc, void (*)(Object,const char *))(o,s); }
static void register_event(Object o, void (*fn)(void *), unsigned filter, void *data)
{ AP01_ACCESS_FN(0xa01aa0b6, void (*)(Object,void (*)(void *),unsigned,void *))(o,fn,filter,data); }
static void original(void *event)
{ AP01_ACCESS_FN(0xa00f8096, void (*)(void *))(event); }
static void background(Object row, unsigned value)
{
    AP01_ACCESS_FN(0xa0192f6a, void (*)(Object,unsigned))(row,255);
    AP01_ACCESS_FN(0xa0192f86, void (*)(Object,unsigned))(row,value);
}
static void hidden(Object o, int hide)
{
    if (hide) AP01_ACCESS_FN(0xa00c1400, void (*)(Object,unsigned))(o,1);
    else AP01_ACCESS_FN(0xa00c1680, void (*)(Object,unsigned))(o,1);
}
static Object ascii_row(Object list, const char *value)
{
    /* The stock Chinese subset must never see new ASCII before font setup. */
    Object row = AP01_ACCESS_FN(0xa0192fb4, Object (*)(Object,const char *,int,int))(list,"",0,0);
    if (!row) return NULL;
    font(child(row,0),(const void *)(uintptr_t)0xa01e1d7c);
    text(child(row,0),value);
    return row;
}
static void select_row(Context *c, Object list, unsigned previous, unsigned next)
{
    unsigned back = c->submenu ? 2 : 7;
    Object old = child(list,(int)previous), row = child(list,(int)next);
    background(old,0x262626); background(row,0x22363d);
    font(child(old,0),(const void *)(uintptr_t)(c->submenu || previous == 6 ? 0xa01e1d7c : 0xa028bce8));
    font(child(row,0),(const void *)(uintptr_t)(c->submenu || next == 6 ? 0xa01e1d7c : 0xa0481524));
    Object arrow = child(old,1);
    if (arrow) AP01_ACCESS_FN(0xa0192f3c, void (*)(Object,unsigned))(arrow,previous == back ? 0xffffff : 0x808080);
    arrow = child(row,1);
    if (arrow) AP01_ACCESS_FN(0xa0192f3c, void (*)(Object,unsigned))(arrow,next == back ? 0xffffff : 0x89d8f3);
    int y = next < 2 ? 0 : (int)(next/2)*146-5;
    unsigned first = c->submenu ? 1 : 0;
    unsigned animate = !((previous == first && next == back) || (previous == back && next == first));
    AP01_ACCESS_FN(0xa00c6dfe, void (*)(Object,int,unsigned))(list,y,animate);
    c->selected = next;
}
static void cleanup(void *event)
{
    uintptr_t *e = event;
    if ((e[2] & ~0x8000u) == 0x29) {
        Context *c=(Context *)e[3];
        if(c)memset(c,0,sizeof(*c));
        AP01_ACCESS_FN(0xa002e0a0, void (*)(void *))(c);
    }
}
static void code_text(Context *c,Object label,int rotate)
{
    ap01_code_io_0031 io=ap01_code_native_0031();
    int result=c->uncertain?ap01_code_load_0031(&io,c->code):
        rotate?ap01_code_regenerate_0031(&io,c->code):ap01_code_ensure_0031(&io,c->code);
    c->uncertain=result==-115||(c->uncertain&&result!=0);
    if(result)c->code[0]=0;
    text(label,!result?c->code:c->uncertain?"Check again":rotate?"Save failed":"Unavailable");
}
static void enter(Context *c, void **data)
{
    Object list = AP01_ACCESS_FN(0xa01988d4, Object (*)(Object))(c->page);
    if (!list) return;
    while (children(list)) destroy(child(list,-1));
    Object readout=ascii_row(list,"");
    if(!readout){destroy(list);return;}
    if(child(readout,1))hidden(child(readout,1),1);
    Object generate=ascii_row(list,"Generate again");
    if(!generate){destroy(list);return;}
    if(child(generate,1))hidden(child(generate,1),1);
    Object back = ascii_row(list,"Back");
    if (!back || children(list) != 3) { destroy(list); return; }
    code_text(c,child(readout,0),0);
    *user(child(list,0)) = c;
    hidden(c->main,1);
    data[2] = list; c->submenu = 1;
    select_row(c,list,0,1);
}
static void event(void *raw)
{
    uintptr_t *e = raw;
    Object page = NULL; void **data = NULL;
    int found = AP01_ACCESS_FN(0xa00b83d2, int (*)(Object,unsigned,Object *,void ***))
        ((Object)e[0],0x1a,&page,&data);
    Object list = found && data ? data[2] : NULL;
    Context *c = list && children(list) ? *user(child(list,0)) : NULL;
    if (!c || (e[2] & ~0x8000u) != 0x11) { original(raw); return; }
    unsigned char *state = *user(c->window);
    if (!state || state[2] != 0x1a) { original(raw); return; }
    int key = AP01_ACCESS_FN(0xa00bf7ea, int (*)(void *))(raw);
    if (key != 0x13 && key != 0x14 && key != 10) { original(raw); return; }
    /* Stock actions perform their own wake handling. */
    if (!c->submenu && key == 10 && state[1] < 0x36) { original(raw); return; }
    AP01_ACCESS_ACTIVITY();
    if (AP01_ACCESS_FN(0xa00b85e6, int (*)(void))()) return;
    if (!c->submenu) c->selected = state[1] >= 0x30 && state[1] <= 0x37 ? state[1]-0x30u : 0;
    if (key == 0x13 || key == 0x14) {
        unsigned first=c->submenu?1:0,count=c->submenu?2:8;
        unsigned next = first+(c->selected-first+(key==0x13?1:count-1))%count;
        select_row(c,list,c->selected,next);
        if (!c->submenu) state[1] = (unsigned char)(0x30+c->selected);
        return;
    }
    if (!c->submenu) {
        if (c->selected == 6) enter(c,data);
        else if (c->selected == 7) { state[1] = 0x36; original(raw); }
    } else if (c->selected == 2) {
        data[2] = c->main; c->submenu = 0;
        hidden(c->main,0); select_row(c,c->main,6,6);
        state[1] = 0x36; destroy(list);
    } else if(c->selected==1)code_text(c,child(child(list,0),0),1);
}
Object ap01_access_list_0031(Object parent)
{
    Object list = AP01_ACCESS_FN(0xa01988d4, Object (*)(Object))(parent);
    if (!list || children(list) != 7) return list;
    Context *c = AP01_ACCESS_FN(0xa002fc1a, void *(*)(size_t))(sizeof(*c));
    if (!c) return list;
    Object row = ascii_row(list,"Access / 18080");
    if (!row || children(list) != 8) {
        destroy(row); AP01_ACCESS_FN(0xa002e0a0, void (*)(void *))(c); return list;
    }
    AP01_ACCESS_FN(0xa00c6458, void (*)(Object,int))(row,6);
    c->page = parent; c->window = AP01_ACCESS_PARENT(parent);
    c->main = list; c->selected = 0; c->submenu = 0;c->uncertain=0;c->code[0]=0;
    *user(child(list,0)) = c;
    register_event(parent,cleanup,0x29,c);
    return list;
}
void ap01_access_register_0031(Object object, void (*callback)(void *), unsigned filter, void *data)
{
    register_event(object,(uintptr_t)callback == 0xa00f8096 ? event : callback,filter,data);
}
