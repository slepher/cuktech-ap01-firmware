#include "screen_host_0041.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct Fixture {unsigned active,idle,available,slides,entered,left,polled,escaped;int prepare;ap01_screen_host *host;} Fixture;
static unsigned active(void *p){return ((Fixture *)p)->active;}
static int idle(void *p){return ((Fixture *)p)->idle;}
static int available(void *p){return ((Fixture *)p)->available;}
static void slide(void *p,unsigned child,unsigned dir){Fixture *f=p;assert(dir==1||dir==2);f->active=child;f->idle=0;++f->slides;}
static int prepare(void *p,ap01_screen_slot *s,uint32_t token){(void)s;assert(token);return ((Fixture *)p)->prepare;}
static void entered(void *p,ap01_screen_slot *s){(void)s;++((Fixture *)p)->entered;}
static void left(void *p,ap01_screen_slot *s){(void)s;++((Fixture *)p)->left;}
static void poll(void *p,uint32_t now){(void)now;++((Fixture *)p)->polled;}
static int input(void *p,ap01_screen_slot *s,unsigned event){Fixture *f=p;(void)s;if(event==AP01_INPUT_ESCAPE){assert(!f->host->locked);++f->escaped;return AP01_FOCUS_KEEP;}return AP01_FOCUS_LOCK;}
static void settle(ap01_screen_host *h,Fixture *f,unsigned target){assert(f->active==target);f->idle=1;ap01_host_poll(h,100);assert(!h->phase);}
static ap01_screen_desc desc(const char *id,Fixture *f){ap01_screen_desc d={1,sizeof(d),id,f,prepare,entered,left,NULL,input,1};return d;}

int main(void) {
    Fixture f={7,1,1,0,0,0,0,0,AP01_ENTER_READY,NULL};
    ap01_screen_slot slots[9]={{0}};
    ap01_screen_app apps[2]={{0}};ap01_screen_host h;
    ap01_screen_port p={&f,active,idle,available,slide,NULL};unsigned i;
    for(i=0;i<9;++i){slots[i].root=&slots[i];slots[i].child=9+i;}
    apps[0].app_id="templates";apps[0].slots=slots;apps[0].capacity=8;apps[0].poll=poll;apps[0].context=&f;
    apps[1].app_id="other";apps[1].slots=slots+8;apps[1].capacity=1;apps[1].poll=poll;apps[1].context=&f;
    assert(ap01_host_init(&h,&p,apps,2)==0);
    f.host=&h;
    assert(!ap01_host_rotate(&h,1,0)); /* Empty host preserves stock navigation. */
    ap01_screen_desc a[8],b=desc("other",&f);
    for(i=0;i<8;++i){static const char *ids[]={"a","b","c","d","e","f","g","h"};a[i]=desc(ids[i],&f);}
    assert(ap01_host_replace(apps,0,a,8)==0);
    assert(ap01_host_replace(apps+1,0,&b,1)==0);
    for(i=0;i<9;++i){assert(ap01_host_rotate(&h,1,0));settle(&h,&f,9+i);}
    assert(ap01_host_rotate(&h,1,0));settle(&h,&f,6);
    for(i=9;i;--i){assert(ap01_host_rotate(&h,-1,0));settle(&h,&f,8+i);}
    assert(ap01_host_rotate(&h,-1,0));settle(&h,&f,7);
    /* Swap logical order while retaining both physical roots. */
    ap01_screen_desc swap[2]={a[1],a[0]};
    assert(ap01_host_replace(apps,1,swap,2)==0);
    assert(ap01_host_find(apps,"a")->child==9&&ap01_host_find(apps,"b")->child==10);
    assert(ap01_host_rotate(&h,1,0));settle(&h,&f,10);
    assert(ap01_host_rotate(&h,1,0));settle(&h,&f,9);
    ap01_screen_desc bad[2]={a[0],a[0]};
    assert(ap01_host_replace(apps,2,bad,2)==AP01_HOST_INVALID);
    assert(apps[0].revision==2&&apps[0].count==2);
    assert(ap01_host_replace(apps,1,a,1)==AP01_HOST_STALE);
    assert(ap01_host_replace(apps+1,1,a,2)==AP01_HOST_CAPACITY);
    /* Hidden screens are skipped; hidden applications still receive polls. */
    ap01_host_find(apps,"b")->desc.visible=0;
    ap01_host_poll(&h,1);assert(f.polled>0);
    assert(ap01_host_rotate(&h,-1,0));settle(&h,&f,7);
    /* Deferred preparation, no slide before matching completion. */
    f.prepare=AP01_ENTER_PENDING;unsigned before=f.slides;
    assert(ap01_host_rotate(&h,1,100));assert(h.phase==1&&f.slides==before);
    uint32_t token=h.transition;
    assert(ap01_host_rotate(&h,1,101));assert(h.transition==token);
    assert(ap01_host_replace(apps,2,a,1)==AP01_HOST_BUSY);
    assert(ap01_host_enter_ready(&h,token+1,1)==AP01_HOST_STALE);
    assert(ap01_host_enter_ready(&h,token,1)==0);settle(&h,&f,9);
    assert(ap01_host_short(&h));assert(h.locked);
    assert(ap01_host_replace(apps+1,apps[1].revision,&b,1)==0&&h.locked);
    ap01_host_retire(apps+1);assert(h.locked);
    assert(ap01_host_replace(apps+1,apps[1].revision,&b,1)==0&&h.locked);
    ap01_host_button(&h,1,100);
    ap01_host_poll(&h,3099);assert(h.locked);
    /* Observe that escape clears the host lock before the callback. */
    ap01_host_poll(&h,3100);assert(!h.locked&&f.escaped==1);
    ap01_host_poll(&h,3200);assert(f.escaped==1);
    ap01_host_button(&h,0,3201);assert(ap01_host_short(&h)&&!h.locked);
    /* Failed and timed-out prepares preserve the source and invalidate tokens. */
    f.prepare=AP01_ENTER_FAILED;before=f.slides;
    assert(ap01_host_rotate(&h,1,4000));assert(!h.phase&&f.slides==before&&f.active==9);
    f.prepare=AP01_ENTER_PENDING;
    assert(ap01_host_rotate(&h,1,4000));token=h.transition;
    ap01_host_poll(&h,4000+AP01_SCREEN_PREPARE_TIMEOUT_MS);assert(!h.phase&&f.active==9);
    assert(ap01_host_enter_ready(&h,token,1)==AP01_HOST_STALE);
    f.available=0;assert(!ap01_host_rotate(&h,1,6000));f.available=1;
    /* Retiring a Bundle keeps identity but prevents routes into released data. */
    ap01_host_retire(apps);assert(!ap01_host_find(apps,"a")->live);
    assert(ap01_host_rotate(&h,1,6001));
    f.prepare=AP01_ENTER_READY;ap01_host_enter_ready(&h,h.transition,1);settle(&h,&f,17);
    assert(ap01_host_replace(apps,apps[0].revision,a,8)==0);
    assert(ap01_host_find(apps,"a")->live);
    assert(ap01_host_replace(apps+1,apps[1].revision,NULL,0)==0);
    ap01_host_poll(&h,6100);settle(&h,&f,6); /* Removing an active set cannot trap input. */
    f.prepare=AP01_ENTER_READY;
    assert(ap01_host_rotate(&h,-1,6200));settle(&h,&f,16);
    assert(ap01_host_api.is_visible(apps,"h"));
    ap01_host_set_blocked(&h,1);assert(!ap01_host_api.is_visible(apps,"h"));
    assert(ap01_host_switch(apps,"a",1,6300)==AP01_HOST_BUSY);
    before=f.polled;ap01_host_poll(&h,6400);assert(f.polled>before);
    ap01_host_set_blocked(&h,0);
    /* Stable ID retains its root, but replacing its context releases old resources. */
    a[0].unbind=left;
    assert(ap01_host_replace(apps,apps[0].revision,a,8)==0);
    Fixture alternate=f;unsigned released=f.left;a[0].context=&alternate;
    assert(ap01_host_replace(apps,apps[0].revision,a,8)==0&&f.left==released+1);
    assert(ap01_host_find(apps,"a")->child==9);
    ap01_host_destroy(&h);assert(!h.app_count&&!apps[0].host);
    assert(!ap01_host_api.is_visible(apps,"h"));
    puts("PASS: two applications, nine roots, stable IDs, atomic set validation, navigation, prepare, focus/escape, hidden polling");
    return 0;
}
