#include "screen_host_0041.h"
#include <string.h>

static int id_valid(const char *id) {
    unsigned n=0;
    if(!id||!*id)return 0;
    while(n<AP01_SCREEN_ID_BYTES&&id[n])++n;
    return n<AP01_SCREEN_ID_BYTES;
}
static int visible(const ap01_screen_slot *s) {return s->id[0]&&s->live&&s->desc.visible;}
static int available(ap01_screen_host *h){return !h->blocked&&h->port.available(h->port.context);}
static ap01_screen_slot *owned_child(ap01_screen_host *h,unsigned child) {
    unsigned a,i;
    for(a=0;a<h->app_count;++a)for(i=0;i<h->apps[a].capacity;++i)
        if(h->apps[a].slots[i].child==child)return &h->apps[a].slots[i];
    return NULL;
}
ap01_screen_slot *ap01_host_current(ap01_screen_host *h) {
    ap01_screen_slot *s=owned_child(h,h->port.active(h->port.context));return s&&s->id[0]?s:NULL;
}
ap01_screen_slot *ap01_host_find(ap01_screen_app *a,const char *id) {
    unsigned i;
    if(!a||!a->host||!id)return NULL;
    for(i=0;i<a->capacity;++i)if(a->slots[i].id[0]&&!strcmp(a->slots[i].id,id))return &a->slots[i];
    return NULL;
}
int ap01_host_init(ap01_screen_host *h,const ap01_screen_port *p,ap01_screen_app *apps,unsigned count) {
    unsigned a,i,b,j;
    if(!h||!p||!p->active||!p->idle||!p->available||!p->slide||(!apps&&count))return AP01_HOST_INVALID;
    for(a=0;a<count;++a) {
        if(!id_valid(apps[a].app_id))return AP01_HOST_INVALID;
        for(b=0;b<a;++b)if(!strcmp(apps[a].app_id,apps[b].app_id))return AP01_HOST_INVALID;
        if(!apps[a].slots||!apps[a].capacity||apps[a].capacity>AP01_SCREEN_SET_LIMIT)return AP01_HOST_CAPACITY;
        for(i=0;i<apps[a].capacity;++i) {
            ap01_screen_slot *s=&apps[a].slots[i];
            if(!s->root||s->child<9)return AP01_HOST_INVALID;
            for(b=0;b<=a;++b)for(j=0;j<(b==a?i:apps[b].capacity);++j)
                if(s->child==apps[b].slots[j].child||s->root==apps[b].slots[j].root)return AP01_HOST_INVALID;
        }
    }
    memset(h,0,sizeof(*h));h->port=*p;h->apps=apps;h->app_count=count;
    for(a=0;a<count;++a){apps[a].host=h;apps[a].count=0;apps[a].revision=0;}
    return AP01_HOST_OK;
}
void ap01_host_cancel(ap01_screen_host *h) {
    h->phase=0;h->source=h->target=NULL;h->locked=0;
    /* Invalidate delayed prepare completions, including after a new set. */
    ++h->transition;if(!h->transition)++h->transition;
}
void ap01_host_set_blocked(ap01_screen_host *h,int blocked) {
    if(blocked&&!h->blocked)ap01_host_cancel(h);
    h->blocked=!!blocked;
}
int ap01_host_is_visible(ap01_screen_app *a,const char *id) {
    if(!a||!a->host)return 0;
    ap01_screen_slot *s=ap01_host_find(a,id);
    return s&&visible(s)&&available(a->host)&&ap01_host_current(a->host)==s;
}
int ap01_host_replace(ap01_screen_app *a,uint32_t expected,const ap01_screen_desc *d,unsigned count) {
    unsigned i,j,map[AP01_SCREEN_SET_LIMIT],used[AP01_SCREEN_SET_LIMIT]={0};
    ap01_screen_host *h;
    if(!a||!(h=a->host)||(!d&&count))return AP01_HOST_INVALID;
    if(expected!=a->revision)return AP01_HOST_STALE;
    if(count>a->capacity)return AP01_HOST_CAPACITY;
    if(h->phase||!h->port.idle(h->port.context))return AP01_HOST_BUSY;
    /* Validate and plan before calling destructors or changing a live mapping. */
    for(i=0;i<count;++i) {
        if(d[i].abi_version!=AP01_SCREEN_ABI_0041||d[i].struct_bytes!=sizeof(*d)||
           !id_valid(d[i].screen_id)||!d[i].prepare||d[i].visible>1)return AP01_HOST_INVALID;
        for(j=0;j<i;++j)if(!strcmp(d[i].screen_id,d[j].screen_id))return AP01_HOST_INVALID;
        map[i]=a->capacity;
        for(j=0;j<a->capacity;++j)if(!strcmp(a->slots[j].id,d[i].screen_id)){map[i]=j;used[j]=1;break;}
    }
    for(i=0;i<count;++i)if(map[i]==a->capacity) {
        for(j=0;j<a->capacity&&used[j];++j){}
        if(j==a->capacity)return AP01_HOST_CAPACITY;
        map[i]=j;used[j]=1;
    }
    for(j=0;j<a->capacity;++j) {
        ap01_screen_slot *s=&a->slots[j];int retained=0;
        for(i=0;i<count;++i)if(map[i]==j&&!strcmp(s->id,d[i].screen_id)&&
            s->desc.context==d[i].context&&s->desc.prepare==d[i].prepare&&s->desc.unbind==d[i].unbind)retained=1;
        if(s->id[0]&&!retained){if(s->desc.unbind)s->desc.unbind(s->desc.context,s);s->id[0]=0;memset(&s->desc,0,sizeof(s->desc));}
    }
    for(i=0;i<count;++i){ap01_screen_slot *s=&a->slots[map[i]];strcpy(s->id,d[i].screen_id);s->desc=d[i];s->desc.screen_id=s->id;s->order=i;s->live=1;}
    a->count=count;++a->revision;if(!a->revision)++a->revision;
    for(j=0;j<a->capacity;++j)if(a->slots[j].child==h->port.active(h->port.context))h->locked=0;
    return AP01_HOST_OK;
}
static int begin(ap01_screen_host *h,ap01_screen_slot *target,unsigned child,unsigned dir,uint32_t now) {
    int result;
    if(h->phase||h->locked||!h->port.idle(h->port.context))return AP01_HOST_BUSY;
    if(!available(h))return AP01_HOST_BUSY;
    if(child==h->port.active(h->port.context))return AP01_HOST_OK;
    h->source=ap01_host_current(h);h->target=target;h->source_child=h->port.active(h->port.context);
    h->target_child=child;h->direction=dir;h->phase=1;h->deadline=now+AP01_SCREEN_PREPARE_TIMEOUT_MS;
    ++h->transition;if(!h->transition)++h->transition;
    result=target?target->desc.prepare(target->desc.context,target,h->transition):AP01_ENTER_READY;
    if(result==AP01_ENTER_FAILED){ap01_host_cancel(h);return AP01_HOST_FAILED;}
    if(result==AP01_ENTER_READY)return ap01_host_enter_ready(h,h->transition,1);
    return AP01_HOST_OK;
}
int ap01_host_enter_ready(ap01_screen_host *h,uint32_t token,int ready) {
    if(!h||h->phase!=1||h->transition!=token)return AP01_HOST_STALE;
    if(!ready||!available(h)||!h->port.idle(h->port.context)||
       h->port.active(h->port.context)!=h->source_child||(h->target&&!visible(h->target))){ap01_host_cancel(h);return AP01_HOST_FAILED;}
    if(h->port.native_edge)h->port.native_edge(h->port.context,h->source_child,h->target_child);
    h->phase=2;h->port.slide(h->port.context,h->target_child,h->direction);
    return AP01_HOST_OK;
}
int ap01_host_switch(ap01_screen_app *a,const char *id,unsigned direction,uint32_t now) {
    if(!a||!a->host)return AP01_HOST_INVALID;
    ap01_screen_slot *s=ap01_host_find(a,id);
    if(!s||!visible(s)||(direction!=1&&direction!=2))return AP01_HOST_INVALID;
    return begin(a->host,s,s->child,direction,now);
}
int ap01_host_rotate(ap01_screen_host *h,int direction,uint32_t now) {
    unsigned a,i,rank=0,current_rank=0,total=0,child=h->port.active(h->port.context);
    ap01_screen_slot *current=ap01_host_current(h),*next=NULL,*prev=NULL,*first=NULL,*last=NULL;
    if(direction!=1&&direction!=-1)return 0;
    ++h->input_revision;
    if(!available(h))return 0;
    if(h->phase||!h->port.idle(h->port.context))return 1;
    if(!current&&owned_child(h,child)) {
        (void)begin(h,NULL,direction>0?6:7,direction>0?2:1,now);return 1;
    }
    if(current&&h->locked){if(current->desc.input&&current->desc.input(current->desc.context,current,direction>0?AP01_INPUT_RIGHT:AP01_INPUT_LEFT)==AP01_FOCUS_UNLOCK)h->locked=0;return 1;}
    if(!current&&!((child==7&&direction>0)||(child==6&&direction<0)))return 0;
    /* Logical order is independent of the immutable physical root indices. */
    for(a=0;a<h->app_count;++a)for(i=0;i<h->apps[a].count;++i) {
        unsigned j;ap01_screen_slot *s=NULL;
        for(j=0;j<h->apps[a].capacity;++j)if(h->apps[a].slots[j].id[0]&&h->apps[a].slots[j].order==i){s=&h->apps[a].slots[j];break;}
        if(!s)continue;
        if(s==current)current_rank=rank;
        if(visible(s)){if(!first)first=s;last=s;++total;}
        ++rank;
    }
    if(!total&&!current)return 0;
    rank=0;
    for(a=0;a<h->app_count;++a)for(i=0;i<h->apps[a].count;++i){unsigned j;
        for(j=0;j<h->apps[a].capacity;++j){ap01_screen_slot *s=&h->apps[a].slots[j];
            if(!s->id[0]||s->order!=i)continue;
            if(visible(s)){if(rank<current_rank)prev=s;if(rank>current_rank&&!next)next=s;}++rank;break;}
    }
    {ap01_screen_slot *target=current?(direction>0?next:prev):(direction>0?first:last);
     (void)begin(h,target,target?target->child:(direction>0?6:7),direction>0?2:1,now);}
    return 1;
}
int ap01_host_short(ap01_screen_host *h) {
    ap01_screen_slot *s=ap01_host_current(h);int result;
    ++h->input_revision;
    if(h->escaped){h->escaped=0;return 1;}
    if(!available(h))return 0;
    if(!s)return owned_child(h,h->port.active(h->port.context))!=NULL;
    if(h->phase)return 1;
    result=s->desc.input?s->desc.input(s->desc.context,s,AP01_INPUT_SHORT):AP01_FOCUS_KEEP;
    if(result==AP01_FOCUS_LOCK)h->locked=1;else if(result==AP01_FOCUS_UNLOCK)h->locked=0;
    return 1;
}
void ap01_host_button(ap01_screen_host *h,int pressed,uint32_t now) {
    ++h->input_revision;
    if(pressed&&!h->pressed){h->pressed_at=now;h->escaped=0;}
    h->pressed=!!pressed;
}
void ap01_host_poll(ap01_screen_host *h,uint32_t now) {
    unsigned i;ap01_screen_slot *s;
    if(h->phase==1&&(int32_t)(now-h->deadline)>=0)ap01_host_cancel(h);
    for(i=0;i<h->app_count;++i)if(h->apps[i].poll)h->apps[i].poll(h->apps[i].context,now);
    if(h->phase&&(!available(h)||h->port.active(h->port.context)!=(h->phase==1?h->source_child:h->target_child))){ap01_host_cancel(h);return;}
    if(h->phase==1&&(int32_t)(now-h->deadline)>=0)ap01_host_cancel(h);
    if(h->phase==2&&h->port.idle(h->port.context)) {
        ap01_screen_slot *from=h->source,*to=h->target;h->phase=0;h->source=h->target=NULL;
        if(from&&from->desc.left)from->desc.left(from->desc.context,from);
        if(to&&to->desc.entered)to->desc.entered(to->desc.context,to);
    }
    s=ap01_host_current(h);
    if(!h->phase&&!s&&owned_child(h,h->port.active(h->port.context))&&available(h))
        (void)begin(h,NULL,6,2,now);
    if(h->locked&&h->pressed&&!h->escaped&&(uint32_t)(now-h->pressed_at)>=3000) {
        h->locked=0;h->escaped=1;
        if(s&&s->desc.input)(void)s->desc.input(s->desc.context,s,AP01_INPUT_ESCAPE);
    }
    if(!h->phase&&s&&s->live&&!visible(s)&&available(h))(void)ap01_host_rotate(h,1,now);
}
void ap01_host_retire(ap01_screen_app *a) {
    unsigned i;ap01_screen_host *h=a->host;
    ap01_screen_slot *current=ap01_host_current(h);
    for(i=0;i<a->capacity;++i)if(&a->slots[i]==current||&a->slots[i]==h->source||&a->slots[i]==h->target){ap01_host_cancel(h);break;}
    for(i=0;i<a->capacity;++i){ap01_screen_slot *s=&a->slots[i];s->live=0;if(s->id[0]&&s->desc.unbind)s->desc.unbind(s->desc.context,s);}
}
void ap01_host_destroy(ap01_screen_host *h) {
    unsigned a;ap01_host_cancel(h);
    for(a=0;a<h->app_count;++a){ap01_host_retire(&h->apps[a]);h->apps[a].host=NULL;h->apps[a].count=0;}
    h->app_count=0;
}
const ap01_host_api_0041 ap01_host_api={AP01_SCREEN_ABI_0041,sizeof(ap01_host_api_0041),
    ap01_host_replace,ap01_host_find,ap01_host_switch,ap01_host_enter_ready,ap01_host_is_visible};
