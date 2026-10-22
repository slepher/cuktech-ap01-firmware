// Host contract test of the production menu adapter. ROM/LVGL calls are fakes;
// this is not a native layout, font or physical-display acceptance test.
#include <cassert>
#include <algorithm>
#include <vector>
#include <string>
#include <cstring>
#include "native_wifi_profiles_0041.h"
#include "native_device_code_0041.h"
#include "native_io_0041.h"
struct Node {alignas(void*) unsigned char raw[128]={};Node *parent=nullptr;std::vector<Node*> children;std::string text;};
static Node *page;static void **values;static unsigned char state[128]={};static int keyValue,stockSelection=-1;static unsigned selections=0;
static Node *create(Node *p){auto n=new Node;n->parent=p;if(p)p->children.push_back(n);return n;}
static void *row(void *p,const char *text,int,int){auto n=create((Node*)p);create(n)->text=text;create(n);return n;}
static void *back(void *p,int,int){return row(p,"Back",0,0);}
static void *list(void *p){auto n=create((Node*)p);for(int i=0;i<6;++i)row(n,std::to_string(i).c_str(),0,0);back(n,0,0);return n;}
static void *getChild(void *p,int i){auto &v=((Node*)p)->children;if(i<0)i+=v.size();return i>=0&&unsigned(i)<v.size()?v[i]:nullptr;}
static unsigned count(void *p){return ((Node*)p)->children.size();}
static void removeNode(void *p){auto n=(Node*)p;while(!n->children.empty())removeNode(n->children.back());if(n->parent){auto &v=n->parent->children;v.erase(std::find(v.begin(),v.end(),n));}delete n;}
static void move(void *p,int i){auto n=(Node*)p;auto &v=n->parent->children;v.erase(std::find(v.begin(),v.end(),n));v.insert(v.begin()+i,n);}
static void setText(void *p,const char *s){((Node*)p)->text=s;}
static void setFont(void *,const void*){}
static void property(void *,uint32_t){}
static void size(void *,int,int){}
static void scroll(void *,int,unsigned){}
static void timer(void*){}
static void reg(void *,void(*)(void*),unsigned,void*){}
static int lookup(void *,unsigned,void **p,void ***v){*p=page;*v=values;return 1;}
static void stock(void*){stockSelection=state[1];}
static int busy(){return 0;}
static int key(void*){return keyValue;}
static void *mark(void *p,void *,const void *,int,int,uint32_t,int,int,int){return create((Node*)p);}
template<class T>T rom(uintptr_t a){
#define F(address,fn) case address:return reinterpret_cast<T>(&fn)
 switch(a){F(0xa01a2c02,list);F(0xa019cdc0,row);F(0xa019ce64,back);F(0xa00dcee4,getChild);F(0xa00dd144,count);F(0xa00ded6c,removeNode);F(0xa00de128,move);F(0xa0091b3a,setText);F(0xa019d0ae,setFont);F(0xa019cd48,property);F(0xa019cd76,property);F(0xa019cd92,property);F(0xa00d8f7c,property);F(0xa00d9044,property);F(0xa00d8e96,size);F(0xa00de5dc,scroll);F(0xa008bd70,timer);F(0xa008c2d0,timer);F(0xa008ae58,timer);F(0xa01ad654,reg);F(0xa00a72ae,lookup);F(0xa00fd1ac,stock);F(0xa00a769a,busy);F(0xa00d8af6,key);F(0xa00a62ee,mark);default:assert(!"unexpected ROM call");return nullptr;}
#undef F
}
#define AP01_MENU_ROM_FN(a,t) rom<t>(a)
// Activity flag is the sole direct global ROM write; redirect it for host tests.
#define AP01_MENU_ACTIVITY() ((void)0)
#include "native_device_code_menu_0041.cpp"
const void *ap01DeviceCodeFont0041(bool){return nullptr;}
const void *ap01DeviceCodeNumberFont0041(){return nullptr;}
const void *ap01DeviceCodeTitleFont0041(){return nullptr;}
const void *ap01WifiSsidFont0041(){return nullptr;}
Ap01VfsOps ap01RomVfs(){return {};}
namespace ap01_native0041 {bool randomBytes(void *,uint8_t *,size_t){return true;}}
int ap01DeviceCodeLoad0041(const Ap01VfsOps &,char out[9]){strcpy(out,"01234567");return 0;}
int ap01DeviceCodeEnsure0041(const Ap01VfsOps &p,bool(*)(void*,uint8_t*,size_t),void*,char out[9]){return ap01DeviceCodeLoad0041(p,out);}
int ap01DeviceCodeRegenerate0041(const Ap01VfsOps &p,bool(*)(void*,uint8_t*,size_t),void*,char out[9]){return ap01DeviceCodeLoad0041(p,out);}
int ap01WifiProfilesRead0041(const Ap01WifiProfilesPort &,Ap01WifiProfiles0041 &out){out.count=2;strcpy(out.profiles[0].ssid,"One");strcpy(out.profiles[1].ssid,"Two");return 0;}
Ap01WifiProfilesPort ap01WifiProfilesNativePort0041(void *,bool(*)(void*)){return {};}
extern "C" int ap01WifiSelect0041(const char *){++selections;return 0;}
extern "C" int ap01WifiSelectionState0041(){return 0;}
int main(){
 page=create(nullptr);Node *window=create(nullptr);Context c;c.page=page;c.window=window;
 void *data[4]={create(page),nullptr,mainList(page,&c),nullptr};values=data;
 void *meta[2]={nullptr,data};userData(page)=meta;userData(window)=state;state[2]=0x1a;state[1]=0x30;
 auto send=[&](int k){keyValue=k;uintptr_t words[4]={(uintptr_t)page,0,0x11,0};event(words);};
 assert(count(data[2])==9);
 for(int i=0;i<6;++i)assert(((Node*)getChild(getChild(data[2],i),0))->text==std::to_string(i));
 assert(((Node*)getChild(getChild(data[2],7),0))->text=="Wi-Fi");
 for(int i=1;i<=9;++i){send(0x13);assert(state[1]==0x30+i%9);}send(0x14);assert(state[1]==0x38);
 send(10);assert(stockSelection==0x36); // Factory Back logical index.
 state[1]=0x33;send(10);assert(stockSelection==0x33); // Factory Version unchanged.
 state[1]=0x30;send(0x13);assert(state[1]==0x34); // Restores prior stock detail selection.
 state[1]=0x36;send(10);assert(c.submenu&&!c.wifi&&count(data[2])==3);
 send(0x13);send(10);assert(!c.submenu&&state[1]==0x36);
 send(0x13);send(10);assert(c.wifi&&count(data[2])==3);
 send(0x14);send(10);assert(!c.submenu&&state[1]==0x37&&count(data[2])==9);
 removeNode(page);removeNode(window);
 puts("menu adapter: stock indices/layout calls, nine-row wrap, stock callback routing, code/Wi-Fi enter and return passed");
}
