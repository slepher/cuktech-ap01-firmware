/* Host regression of the actual 0031 menu with the ROM boundary mocked. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ota_channel.h"

typedef struct Node Node;
struct Node {
    unsigned char native[128];
    Node *parent, *items[16];
    unsigned count, hidden, color, opacity, animate;
    int scroll;
    void *user;
    const void *font;
    char text[40];
    void (*callback)(void *);
    unsigned filter;
    void *callback_data;
};
static void *rom(uintptr_t address);
static unsigned activity, nodes, contexts, forwarded, wake;
static int key, fail_context, fail_row, fail_list;
static Node *current_page;
static void *page_metadata[2], *page_values[4];
static unsigned char state[3];
static unsigned forwarded_state;
#define AP01_ACCESS_FN(address, type) ((type)rom(address))
#define AP01_ACCESS_ACTIVITY() (++activity)
#define AP01_ACCESS_USER(o) (&((Node *)(o))->user)
#define AP01_ACCESS_PARENT(o) (((Node *)(o))->parent)
#include "access_menu_0031.c"

/* Only the fake device filesystem persists across menu recreation/reboot.
 * No ROM manifest supplies any key to this test or the production menu. */
static struct {
    unsigned char stored[16],pending[16];
    int present,pending_present,read_error,uncertain_rename,random_fail;
    uint32_t random_value;
    unsigned random_calls,writes;
} disk;
static int code_read(void *p,const char *path,unsigned char out[16])
{
    (void)p;
    if(!strcmp(path,"/data/ap01_0031.device_code")) {
        if(disk.read_error)return -5;
        if(!disk.present)return -2;
        memcpy(out,disk.stored,16);return 0;
    }
    assert(!strcmp(path,"/data/ap01_0031.device_code.new"));
    if(!disk.pending_present)return -2;
    memcpy(out,disk.pending,16);return 0;
}
static int code_write(void *p,const char *path,const unsigned char in[16])
{
    (void)p;assert(!strcmp(path,"/data/ap01_0031.device_code.new"));
    memcpy(disk.pending,in,16);disk.pending_present=1;++disk.writes;return 0;
}
static int code_replace(void *p,const char *from,const char *to)
{
    (void)p;assert(!strcmp(from,"/data/ap01_0031.device_code.new"));
    assert(!strcmp(to,"/data/ap01_0031.device_code") && disk.pending_present);
    memcpy(disk.stored,disk.pending,16);disk.present=1;disk.pending_present=0;
    if(disk.uncertain_rename)disk.read_error=1;
    return disk.uncertain_rename?-5:0;
}
static int code_random(void *p,unsigned char out[4])
{
    (void)p;++disk.random_calls;if(disk.random_fail)return 0;
    for(unsigned i=0;i<4;i++)out[i]=(unsigned char)(disk.random_value>>(8*i));
    return 1;
}
ap01_code_io_0031 ap01_code_native_0031(void)
{
    ap01_code_io_0031 ops={NULL,code_read,code_write,code_replace,code_random};
    return ops;
}
static Node *node(Node *parent)
{
    Node *n = calloc(1,sizeof(*n)); assert(n); ++nodes;
    n->parent=parent;
    if(parent) { assert(parent->count<16); parent->items[parent->count++]=n; }
    return n;
}
static void remove_node(void *object)
{
    Node *n=object; assert(n);
    while(n->count) remove_node(n->items[n->count-1]);
    if(n->callback && n->filter==0x29) {
        uintptr_t e[4]={(uintptr_t)n,0,0x29,(uintptr_t)n->callback_data};
        n->callback(e);
    }
    if(n->parent) {
        Node *p=n->parent; unsigned i=0;
        while(i<p->count && p->items[i]!=n) ++i;
        assert(i<p->count);
        memmove(p->items+i,p->items+i+1,(p->count-i-1)*sizeof(Node *)); --p->count;
    }
    --nodes; free(n);
}
static void *get_child(void *object,int index)
{
    Node *n=object; assert(n);
    if(index<0) index+=(int)n->count;
    return index>=0 && (unsigned)index<n->count ? n->items[index] : NULL;
}
static unsigned get_count(void *object) { assert(object); return ((Node *)object)->count; }
static Node *make_row(Node *list,const char *value)
{
    Node *r=node(list); Node *label=node(r); node(r);
    snprintf(label->text,sizeof(label->text),"%s",value); return r;
}
static void *stock_list(void *parent)
{
    if(fail_list) { fail_list=0; return NULL; }
    Node *list=node(parent);
    for(unsigned i=0;i<7;++i) {
        char title[12]; snprintf(title,sizeof(title),"stock%u",i); make_row(list,title);
    }
    return list;
}
static void *add_row(void *list,const char *value,int a,int b)
{
    assert(!a && !b && !*value); /* New text must be set after ASCII font. */
    if(fail_row && !--fail_row) return NULL;
    return make_row(list,value);
}
static void set_font(void *object,const void *face) { assert(object); ((Node *)object)->font=face; }
static void set_text(void *object,const char *value)
{
    Node *n=object; assert(n && n->font==(void *)(uintptr_t)0xa01e1d7c);
    assert(strlen(value)<sizeof(n->text)); strcpy(n->text,value);
}
static void opacity(void *object,unsigned value) { assert(object); ((Node *)object)->opacity=value; }
static void color(void *object,unsigned value) { assert(object); ((Node *)object)->color=value; }
static void hide(void *object,unsigned flag) { assert(object && flag==1); ((Node *)object)->hidden=1; }
static void show(void *object,unsigned flag) { assert(object && flag==1); ((Node *)object)->hidden=0; }
static void scroll(void *object,int y,unsigned animate)
{ Node *n=object; assert(n); n->scroll=y; n->animate=animate; }
static void move(void *object,int index)
{
    Node *n=object,*p=n->parent; unsigned old=0;
    assert(index>=0 && (unsigned)index<p->count);
    while(p->items[old]!=n) ++old;
    assert(old>=(unsigned)index);
    memmove(p->items+index+1,p->items+index,(old-(unsigned)index)*sizeof(Node *));
    p->items[index]=n;
}
static void registration(void *object,void (*fn)(void *),unsigned filter,void *data)
{
    Node *n=object; assert(n); n->callback=fn; n->filter=filter; n->callback_data=data;
}
static void stock_event(void *raw) { assert(raw); ++forwarded; forwarded_state=state[1]; }
static int lookup(void *window,unsigned id,void **page,void ***data)
{
    assert(id==0x1a); (void)window;
    if(!current_page) return 0;
    *page=current_page; *data=page_values; return 1;
}
static int event_key(void *raw) { assert(raw); return key; }
static int wake_consumed(void) { return (int)wake; }
static void *allocate(size_t size)
{ if(fail_context) {fail_context=0;return NULL;} void *p=malloc(size); assert(p); ++contexts; return p; }
static int cleaning;
static void release(void *p)
{
    assert(p && contexts);
    if(cleaning)for(size_t i=0;i<sizeof(Context);i++)assert(!((unsigned char *)p)[i]);
    --contexts;free(p);
}
static void *rom(uintptr_t address)
{
    switch(address) {
    case 0xa00c5d84:return get_child;
    case 0xa00c5fe4:return get_count;
    case 0xa00c7466:return remove_node;
    case 0xa01932a2:return set_font;
    case 0xa0086bcc:return set_text;
    case 0xa01aa0b6:return registration;
    case 0xa00f8096:return stock_event;
    case 0xa0192f6a:return opacity;
    case 0xa0192f86:case 0xa0192f3c:return color;
    case 0xa00c1400:return hide;
    case 0xa00c1680:return show;
    case 0xa0192fb4:return add_row;
    case 0xa00c6dfe:return scroll;
    case 0xa002e0a0:return release;
    case 0xa01988d4:return stock_list;
    case 0xa00b83d2:return lookup;
    case 0xa00bf7ea:return event_key;
    case 0xa00b85e6:return wake_consumed;
    case 0xa002fc1a:return allocate;
    case 0xa00c6458:return move;
    default:assert(!"unknown ROM call"); return NULL;
    }
}
static Node *setup(void)
{
    Node *window=node(NULL); current_page=node(window);
    memset(state,0,sizeof(state)); state[1]=0x30; state[2]=0x1a; window->user=state;
    memset(page_values,0,sizeof(page_values)); page_metadata[1]=page_values;
    current_page->user=page_metadata;
    page_values[2]=ap01_access_list_0031(current_page);
    ap01_access_register_0031(window,(void (*)(void *))(uintptr_t)0xa00f8096,0x11,NULL);
    assert(window->callback==event);
    return window;
}
static void send(Node *window,int value,unsigned code)
{
    uintptr_t raw[4]={(uintptr_t)window,0,code,0}; key=value;
    window->callback(raw);
}
static void teardown(Node *window)
{ cleaning=1;remove_node(window);cleaning=0;current_page=NULL;assert(!nodes && !contexts); }
typedef struct { char request[256], response[512]; size_t read, written; } Http;
static int http_read(void *p,void *out,size_t n,uint32_t timeout)
{
    Http *h=p; assert(timeout); size_t remaining=strlen(h->request)-h->read;
    if(n>remaining)n=remaining;
    memcpy(out,h->request+h->read,n);h->read+=n;return (int)n;
}
static int http_write(void *p,const void *in,size_t n,uint32_t timeout)
{
    Http *h=p;assert(timeout && h->written+n<sizeof(h->response));
    memcpy(h->response+h->written,in,n);h->written+=n;h->response[h->written]=0;return (int)n;
}
static uint64_t clock_ms=1;
static ap01_code_gate_0031 gate;
static uint64_t http_now(void *p) { (void)p;return clock_ms; }
static int no_begin(void *p,uint32_t n,uint32_t t) { (void)p;(void)n;(void)t;assert(0);return 0; }
static int no_chunk(void *p,const void *b,size_t n,uint32_t t) { (void)p;(void)b;(void)n;(void)t;assert(0);return 0; }
static int no_commit(void *p,uint32_t t) { (void)p;(void)t;assert(0);return 0; }
static void no_abort(void *p) { (void)p;assert(0); }
static const char *http_logs(void *p) { (void)p;return "{\"test\":true}\n"; }
static enum ota_error authenticate(void *p,const char *token,size_t length)
{
    (void)p;char actual[9];ap01_code_io_0031 ops=ap01_code_native_0031();
    int r=ap01_code_load_0031(&ops,actual);
    int result=ap01_code_auth_0031(&gate,r?NULL:actual,token,length,clock_ms);
    static const enum ota_error errors[]={OTA_OK,OTA_UNAUTHORIZED,OTA_RATE_LIMITED,OTA_AUTH_UNAVAILABLE};
    assert(result>=0 && (unsigned)result<sizeof(errors)/sizeof(errors[0]));
    return errors[result];
}
static void check_auth(const char *token,int status,enum ota_error expected)
{
    Http h={0};char auth[100]={0};
    if(token)snprintf(auth,sizeof(auth),"Authorization: Bearer %s\r\n",token);
    snprintf(h.request,sizeof(h.request),"GET /logs HTTP/1.1\r\n%s\r\n",auth);
    ota_channel_io io={&h,http_read,http_write,http_now,no_begin,no_chunk,no_commit,no_abort,http_logs,NULL};
    ota_channel_result result=ota_channel_handle_authenticated(&io,authenticate,clock_ms+1000);
    assert(result.error==expected);
    char prefix[32];snprintf(prefix,sizeof(prefix),"HTTP/1.1 %d ",status);
    assert(strstr(h.response,prefix));
    if(token && *token)assert(!strstr(h.response,token));
    if(status!=200)assert(!strstr(h.response,"\"test\":true"));
}
int main(void)
{
    check_auth("12345678",503,OTA_AUTH_UNAVAILABLE);
    assert(!disk.random_calls && !disk.writes);
    disk.random_value=12345678;
    Node *w=setup(),*main=page_values[2]; assert(main->count==8 && contexts==1);
    for(unsigned i=0;i<6;++i) {char s[12];snprintf(s,sizeof(s),"stock%u",i);assert(!strcmp(main->items[i]->items[0]->text,s));}
    assert(!strcmp(main->items[6]->items[0]->text,"Access / 18080"));
    assert(!strcmp(main->items[7]->items[0]->text,"stock6"));
    send(w,0x14,0x11); assert(state[1]==0x37 && !main->animate);
    send(w,0x13,0x11); assert(state[1]==0x30 && !main->animate);
    for(unsigned i=0;i<6;++i) send(w,0x13,0x11);
    wake=1; send(w,10,0x11); assert(page_values[2]==main && !main->hidden); wake=0;
    send(w,10,0x11); Node *sub=page_values[2]; assert(sub!=main && main->hidden && sub->count==3);
    Node *readout=sub->items[0]->items[0];Context *context=sub->items[0]->user;
    assert(!strcmp(readout->text,"12345678") && disk.random_calls==1 && disk.writes==1);
    assert(context->selected==1 && sub->items[0]->items[1]->hidden && sub->items[1]->items[1]->hidden);
    assert(!strcmp(sub->items[1]->items[0]->text,"Generate again") && !strcmp(sub->items[2]->items[0]->text,"Back"));
    check_auth(readout->text,200,OTA_OK);
    check_auth("00000000",401,OTA_UNAUTHORIZED);check_auth(NULL,401,OTA_UNAUTHORIZED);
    check_auth("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",401,OTA_UNAUTHORIZED);
    check_auth(readout->text,200,OTA_OK);
    for(unsigned i=0;i<5;i++)check_auth("00000000",401,OTA_UNAUTHORIZED);
    check_auth(readout->text,429,OTA_RATE_LIMITED);clock_ms=30000;
    check_auth(readout->text,429,OTA_RATE_LIMITED);clock_ms=30001;
    check_auth(readout->text,200,OTA_OK);
    send(w,0x14,0x11); assert(context->selected==2 && !sub->animate);
    send(w,0x13,0x11); assert(context->selected==1 && !sub->animate);
    for(unsigned i=0;i<8;i++){send(w,i&1?0x13:0x14,0x11);assert(context->selected!=0);}
    disk.random_value=42;send(w,10,0x11);
    assert(!strcmp(readout->text,"00000042") && disk.random_calls==2);
    check_auth("12345678",401,OTA_UNAUTHORIZED);check_auth(readout->text,200,OTA_OK);
    /* Unknown durable outcome must turn subsequent button presses into loads,
     * even after returning to the main list and entering this page again. */
    disk.random_value=777;disk.uncertain_rename=1;send(w,10,0x11);
    assert(context->uncertain && !strcmp(readout->text,"Check again"));
    unsigned random_calls=disk.random_calls,writes=disk.writes;
    send(w,10,0x11);assert(disk.random_calls==random_calls && disk.writes==writes);
    check_auth("00000777",503,OTA_AUTH_UNAVAILABLE);
    send(w,0x13,0x11);send(w,10,0x11);assert(page_values[2]==main);
    send(w,10,0x11);sub=page_values[2];readout=sub->items[0]->items[0];context=sub->items[0]->user;
    assert(context->uncertain && !strcmp(readout->text,"Check again") && disk.random_calls==random_calls);
    disk.read_error=0;disk.uncertain_rename=0;send(w,10,0x11);
    assert(!context->uncertain && !strcmp(readout->text,"00000777") && disk.random_calls==random_calls);
    check_auth("00000042",401,OTA_UNAUTHORIZED);check_auth(readout->text,200,OTA_OK);
    disk.random_value=888;send(w,10,0x11);assert(!strcmp(readout->text,"00000888"));
    send(w,0x13,0x11);
    send(w,10,0x11); assert(page_values[2]==main && !main->hidden && state[1]==0x36);
    send(w,0x13,0x11); unsigned before=forwarded;
    send(w,10,0x11); assert(forwarded==before+1 && forwarded_state==0x36);
    state[1]=0x32; before=forwarded; send(w,10,0x11); assert(forwarded==before+1);
    state[2]=0x19; before=forwarded; send(w,0x13,0x11); assert(forwarded==before+1); state[2]=0x1a;
    before=forwarded; send(w,123,0x11); send(w,0,1); assert(forwarded==before+2);
    state[1]=0x36;
    random_calls=disk.random_calls;
    for(int i=1;i<=3;++i) { unsigned count=nodes;fail_row=i;send(w,10,0x11);assert(page_values[2]==main && !main->hidden && nodes==count && disk.random_calls==random_calls); }
    fail_list=1; send(w,10,0x11); assert(page_values[2]==main);
    /* Page deletion while the readout is open frees its single context. */
    send(w,10,0x11); assert(page_values[2]!=main); teardown(w);
    w=setup(); state[1]=0x36; send(w,10,0x11); sub=page_values[2];
    assert(!strcmp(sub->items[0]->items[0]->text,"00000888") && disk.random_calls==random_calls);
    gate=(ap01_code_gate_0031){0};clock_ms=1; /* Independent request state after reboot. */
    check_auth("00000888",200,OTA_OK);teardown(w);
    fail_context=1; w=setup(); assert(((Node *)page_values[2])->count==7 && !contexts);
    before=forwarded; send(w,10,0x11); assert(forwarded==before+1); teardown(w);
    fail_row=1; w=setup(); assert(((Node *)page_values[2])->count==7 && !contexts); teardown(w);
    fail_list=1; w=setup(); assert(!page_values[2] && !contexts); teardown(w);
    memset(&disk,0,sizeof(disk));disk.random_fail=1;gate=(ap01_code_gate_0031){0};
    w=setup();state[1]=0x36;send(w,10,0x11);sub=page_values[2];
    assert(!strcmp(sub->items[0]->items[0]->text,"Unavailable"));
    check_auth("12345678",503,OTA_AUTH_UNAVAILABLE);
    disk.random_fail=0;disk.random_value=12345678;send(w,10,0x11);
    assert(!strcmp(sub->items[0]->items[0]->text,"12345678"));
    check_auth("12345678",200,OTA_OK);teardown(w);
    puts("0031 access menu: persistent generation/rotation, auth/rate gate, lifecycle and allocation failures passed");
    return 0;
}
