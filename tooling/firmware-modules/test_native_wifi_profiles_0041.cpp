// Host-only contract test. No device, network driver, or original PSM writes.
#include "native_wifi_profiles_0041.h"
#include <assert.h>
#include <errno.h>
#include <string>
#include <vector>

struct State {
    char ssid[33]="home", password[65]="original-private";
    const char identity[40]="UID/token/BLE binding fixture unchanged";
    std::vector<uint8_t> bytes;
    bool busy=false,failCurrent=false,failStore=false,badReadback=false,damageAfterStore=false;
    int failLoad=0;unsigned writes=0;
};
static int current(void *p,char *ssid,unsigned sn,char *pass,unsigned pn) {
    auto &s=*(State *)p;if(s.failCurrent)return -EIO;
    assert(sn>=sizeof(s.ssid)&&pn>=sizeof(s.password));memcpy(ssid,s.ssid,sizeof(s.ssid));memcpy(pass,s.password,sizeof(s.password));return 0;
}
static int load(void *p,uint8_t *out,unsigned cap) {
    auto &s=*(State *)p;if(s.failLoad)return s.failLoad;if(s.bytes.empty())return -ENOENT;
    if(s.bytes.size()>cap)return -EFBIG;
    memcpy(out,s.bytes.data(),s.bytes.size());if(s.badReadback)out[0]^=1;return int(s.bytes.size());
}
static int store(void *p,const uint8_t *in,unsigned n) {
    auto &s=*(State *)p;++s.writes;if(s.failStore)return -EIO;s.bytes.assign(in,in+n);s.badReadback=s.damageAfterStore;return 0;
}
static bool busy(void *p){return ((State *)p)->busy;}
static Ap01HttpReply call(State &s,const char *method,const std::string &body="",const char *path="/api/wifi/profiles") {
    Ap01HttpRequest r{};r.method=method;r.path=path;r.contentType="application/json";r.body=(const uint8_t *)body.data();r.length=body.size();
    return ap01WifiProfilesHttp0041({&s,current,load,store,busy},r,"34F01557210B");
}
static std::string put(unsigned revision,const std::string &rows) {
    return "{\"device_mac\":\"34F01557210B\",\"expected_revision\":"+std::to_string(revision)+",\"profiles\":"+rows+"}";
}
static void unchanged(const State &s) {
    assert(!strcmp(s.ssid,"home")&&!strcmp(s.password,"original-private"));
    assert(!strcmp(s.identity,"UID/token/BLE binding fixture unchanged"));
}
int main() {
    State s;
    auto response=call(s,"GET");assert(response.status==200&&strstr(response.bytes.c_str(),"\"source\":\"current\""));
    assert(!strstr(response.bytes.c_str(),"original-private")&&!s.writes);
    assert(call(s,"PUT",put(0,"[{\"ssid\":\"home\"},{\"ssid\":\"home\",\"password\":\"original-private\"}]")).status==200);
    Ap01WifiProfiles0041 list;assert(!ap01WifiProfilesRead0041({&s,current,load,store,busy},list));
    assert(list.count==1&&list.profiles[0].saved&&list.profiles[0].current&&list.revision==1);unchanged(s);
    assert(call(s,"PUT",put(1,"[{\"ssid\":\"home\",\"password\":\"edited-private\"},{\"ssid\":\"guest\",\"password\":\"\"}]")).status==200);
    assert(!ap01WifiProfilesRead0041({&s,current,load,store,busy},list));
    assert(list.count==2&&!strcmp(list.profiles[0].password,"edited-private")&&list.profiles[0].current);unchanged(s);
    response=call(s,"GET");assert(!strstr(response.bytes.c_str(),"edited-private"));
    assert(call(s,"PUT",put(2,"[]")).status==200);
    assert(!ap01WifiProfilesRead0041({&s,current,load,store,busy},list));
    assert(list.count==1&&!list.profiles[0].saved&&list.profiles[0].current);unchanged(s);
    unsigned writes=s.writes;
    for(const std::string &body:{put(2,"[]"),put(3,"[{\"ssid\":\"unknown\"}]"),
        put(3,"[{\"ssid\":\"x\",\"password\":\"a\"},{\"ssid\":\"x\",\"password\":\"b\"}]"),
        put(3,"[{\"ssid\":\"x\\u0000y\",\"password\":\"\"}]"),
        put(3,"[{\"ssid\":\"x\",\"password\":\"a\\u0000b\"}]"),
        put(3,"[{\"ssid\":\"x\\n\",\"password\":\"\"}]"),
        put(3,"[{\"ssid\":\"x\",\"password\":null}]"),
        put(3,"[{\"ssid\":\"x\",\"password\":\"\",\"activate\":true}]"),
        std::string("{\"device_mac\":\"wrong\",\"expected_revision\":3,\"profiles\":[]}"),
        std::string("{\"device_mac\":\"34F01557210B\",\"expected_revision\":3,\"profiles\":[],\"uid\":\"x\"}")}) {
        assert(call(s,"PUT",body).status>=400&&s.writes==writes);unchanged(s);
    }
    for(const std::string &name:{std::string(33,'x'),std::string("\xc0\xaf"),std::string("\xed\xa0\x80"),std::string("\xf4\x90\x80\x80")})
        assert(call(s,"PUT",put(3,"[{\"ssid\":\""+name+"\",\"password\":\"\"}]")).status==400&&s.writes==writes);
    assert(call(s,"PUT",put(3,"[{\"ssid\":\"x\",\"password\":\""+std::string(65,'p')+"\"}]")).status==400&&s.writes==writes);
    std::string rows="[";
    for(unsigned i=0;i<8;++i){if(i)rows+=",";rows+="{\"ssid\":\"n"+std::to_string(i)+"\",\"password\":\"p\"}";}rows+="]";
    assert(call(s,"PUT",put(3,rows)).status==200);
    assert(!ap01WifiProfilesRead0041({&s,current,load,store,busy},list));assert(list.count==9&&list.profiles[8].current);
    writes=s.writes;s.failCurrent=true;assert(call(s,"PUT",put(4,"[]")).status==503&&s.writes==writes);s.failCurrent=false;
    std::string nine=rows;nine.pop_back();nine+=",{\"ssid\":\"n8\",\"password\":\"p\"}]";
    assert(call(s,"PUT",put(4,nine)).status==400&&s.writes==writes);
    s.busy=true;assert(call(s,"GET").status==503&&s.writes==writes);s.busy=false;
    auto original=s.bytes;s.bytes[4]^=1;assert(call(s,"PUT",put(4,"[]")).status==409&&s.writes==writes);s.bytes=original;
    s.failLoad=-EFBIG;assert(call(s,"PUT",put(4,"[]")).status==503&&s.writes==writes);s.failLoad=0;
    s.failStore=true;assert(call(s,"PUT",put(4,"[]")).status==503&&s.bytes==original);s.failStore=false;
    assert(call(s,"POST").status==405&&call(s,"GET","","/api/wifi/activate").status==404);
    unchanged(s);
    State empty;empty.ssid[0]=0;assert(call(empty,"GET").status==200&&!empty.writes);
    State boundary;
    assert(call(boundary,"PUT",put(0,"[{\"ssid\":\""+std::string(32,'s')+"\",\"password\":\""+std::string(64,'p')+"\"}]")).status==200);
    assert(!ap01WifiProfilesRead0041({&boundary,current,load,store,busy},list)&&strlen(list.profiles[0].ssid)==32&&strlen(list.profiles[0].password)==64);
    State damaged;damaged.damageAfterStore=true;
    response=call(damaged,"PUT",put(0,"[]"));
    assert(response.status==503&&strstr(response.bytes.c_str(),"store_verification_failed")&&
        strstr(response.bytes.c_str(),"\"result\":\"unknown\"")&&strstr(response.bytes.c_str(),"read_profiles_and_revision")&&damaged.writes==1);unchanged(damaged);
    puts("0041 Wi-Fi saved profiles: passed");
}
