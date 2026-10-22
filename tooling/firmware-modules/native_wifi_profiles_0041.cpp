#include "native_wifi_profiles_0041.h"
#include "native_json_0041.h"
#include <errno.h>
#include <memory>
#include <new>

namespace {
constexpr unsigned Header = 16, Record = 98, Capacity = Header + 8 * Record;
struct Workspace {
    Ap01WifiProfiles0041 old, next;
    uint8_t bytes[Capacity] = {}, check[Capacity];
};
uint32_t word(const uint8_t *p) {return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);}
void word(uint8_t *p,uint32_t n) {for(unsigned i=0;i<4;++i)p[i]=uint8_t(n>>(8*i));}
uint32_t crc(const uint8_t *p,unsigned n) {
    uint32_t c=~0u;
    for(unsigned j=0;j<n;++j){c^=j>=12&&j<16?0:p[j];for(unsigned i=0;i<8;++i)c=(c>>1)^(0xedb88320u&(0u-(c&1)));}
    return ~c;
}
bool ssidValid(const char *s,unsigned n) {
    if(!n||n>32)return false;
    for(unsigned i=0;i<n;) {
        unsigned a=(unsigned char)s[i++], more=0, value=0, minimum=0;
        if(a<0x20||a==0x7f)return false;
        if(a<0x80)continue;
        if(a>=0xc2&&a<=0xdf){more=1;value=a&31;minimum=0x80;}
        else if(a>=0xe0&&a<=0xef){more=2;value=a&15;minimum=0x800;}
        else if(a>=0xf0&&a<=0xf4){more=3;value=a&7;minimum=0x10000;}
        else return false;
        if(more>n-i)return false;
        while(more--){unsigned b=(unsigned char)s[i++];if((b&0xc0)!=0x80)return false;value=(value<<6)|(b&63);}
        if(value<minimum||value>0x10ffff||(value>=0xd800&&value<=0xdfff)||(value>=0x80&&value<=0x9f))return false;
    }
    return true;
}
int find(const Ap01WifiProfiles0041 &list,const char *ssid) {
    for(unsigned i=0;i<list.count;++i)if(!strcmp(list.profiles[i].ssid,ssid))return int(i);
    return -1;
}
int load(const Ap01WifiProfilesPort &port,Ap01WifiProfiles0041 &list) {
    if(!port.load||!port.current)return -ENOSYS;
    uint8_t bytes[Capacity];int n=port.load(port.context,bytes,sizeof(bytes));
    if(n==-ENOENT)return 0;
    if(n<0)return n;
    if(n<int(Header)||n>int(Capacity)||memcmp(bytes,"WPL1",4)||bytes[8]>8||bytes[9]||bytes[10]||bytes[11]||
       unsigned(n)!=Header+bytes[8]*Record||word(bytes+12)!=crc(bytes,n))return -EILSEQ;
    list.revision=word(bytes+4);list.count=bytes[8];
    if(!list.revision)return -EILSEQ;
    for(unsigned i=0;i<list.count;++i) {
        const uint8_t *r=bytes+Header+i*Record;auto &p=list.profiles[i];
        unsigned sn=r[0],pn=r[33];
        if(!ssidValid((const char *)r+1,sn)||pn>64||memchr(r+34,0,pn))return -EILSEQ;
        memcpy(p.ssid,r+1,sn);memcpy(p.password,r+34,pn);p.saved=true;
        for(unsigned j=0;j<i;++j)if(!strcmp(p.ssid,list.profiles[j].ssid))return -EILSEQ;
    }
    return 0;
}
Ap01HttpReply failure(int status,const char *error,bool unknown=false) {
    Ap01HttpReply r;r.status=status;r.bytes="{\"result\":\"";r.bytes+=unknown?"unknown":"rejected";
    r.bytes+="\",\"stage\":\"wifi_profiles\",\"action\":\"read_profiles_and_revision\",\"error\":\"";
    r.bytes+=error;r.bytes+="\"}";return r;
}
Ap01HttpReply reply(const Ap01WifiProfiles0041 &list,const char *mac) {
    NativeJsonAllocator0041 a;ArduinoJson::JsonDocument doc(&a);
    doc["result"]="ok";doc["device_mac"]=mac;doc["revision"]=list.revision;
    auto array=doc["profiles"].to<ArduinoJson::JsonArray>();
    for(unsigned i=0;i<list.count;++i){const auto &p=list.profiles[i];auto row=array.add<ArduinoJson::JsonObject>();
        row["ssid"]=p.ssid;row["has_password"]=p.password[0]!=0;row["current"]=p.current;row["source"]=p.saved?"saved":"current";}
    if(doc.overflowed())return failure(503,"oom");
    size_t size=ArduinoJson::measureJson(doc);std::unique_ptr<char[]> text(new(std::nothrow) char[size+1]);
    if(!text||ArduinoJson::serializeJson(doc,text.get(),size+1)!=size)return failure(503,"encode");
    Ap01HttpReply r;r.bytes=String(text.get(),size);r.status=r.bytes.length()==size?200:503;return r;
}
bool fields(ArduinoJson::JsonObjectConst obj,const char *a,const char *b,const char *c=nullptr) {
    for(auto pair:obj){const char *k=pair.key().c_str();if(strcmp(k,a)&&strcmp(k,b)&&(!c||strcmp(k,c)))return false;}
    return true;
}
}

int ap01WifiProfilesRead0041(const Ap01WifiProfilesPort &port,Ap01WifiProfiles0041 &out) {
    out=Ap01WifiProfiles0041{};
    if(port.busy&&port.busy(port.context))return -EBUSY;
    int result=load(port,out);if(result)return result;
    Ap01WifiProfile0041 current;
    result=port.current(port.context,current.ssid,sizeof(current.ssid),current.password,sizeof(current.password));
    if(result)return result;
    if(!memchr(current.ssid,0,sizeof(current.ssid))||!memchr(current.password,0,sizeof(current.password)))return -EILSEQ;
    unsigned sn=strlen(current.ssid),pn=strlen(current.password);
    // Empty SSID means unconfigured. An offline device retains its saved SSID.
    if(!sn)return 0;
    if(!ssidValid(current.ssid,sn)||pn>64)return -EILSEQ;
    int i=find(out,current.ssid);
    if(i>=0)out.profiles[i].current=true;
    else {current.current=true;out.profiles[out.count++]=current;}
    return 0;
}

Ap01HttpReply ap01WifiProfilesHttp0041(const Ap01WifiProfilesPort &port,const Ap01HttpRequest &request,const char *mac) {
    if(strcmp(request.path,"/api/wifi/profiles"))return failure(404,"endpoint");
    bool put=!strcmp(request.method,"PUT");
    if(!put&&strcmp(request.method,"GET"))return failure(405,"method");
    NativeJsonAllocator0041 allocator;ArduinoJson::JsonDocument doc(&allocator);
    if(put) {
        if(strcmp(request.contentType,"application/json")||request.length>4096||
           ArduinoJson::deserializeJson(doc,request.body,request.length)||!doc.is<ArduinoJson::JsonObject>())return failure(400,"json");
        auto obj=doc.as<ArduinoJson::JsonObjectConst>();
        if(!fields(obj,"device_mac","expected_revision","profiles"))return failure(400,"fields");
        if(!obj["device_mac"].is<const char *>()||obj["device_mac"].as<ArduinoJson::JsonString>().size()!=strlen(mac)||
           strcmp(obj["device_mac"].as<const char *>(),mac))return failure(409,"device_identity");
        if(!obj["expected_revision"].is<uint32_t>()||!obj["profiles"].is<ArduinoJson::JsonArrayConst>())return failure(400,"shape");
    }
    if(!put) {
        std::unique_ptr<Ap01WifiProfiles0041> list(new(std::nothrow) Ap01WifiProfiles0041);
        if(!list)return failure(503,"oom");
        int result=ap01WifiProfilesRead0041(port,*list);
        if(result)return failure(result==-EILSEQ?409:503,result==-EILSEQ?"storage_corrupt":"read_unavailable");
        return reply(*list,mac);
    }
    std::unique_ptr<Workspace> work(new(std::nothrow) Workspace);
    if(!work)return failure(503,"oom");
    auto &old=work->old;
    int result=ap01WifiProfilesRead0041(port,old);
    if(result)return failure(result==-EILSEQ?409:503,result==-EILSEQ?"storage_corrupt":"read_unavailable");
    if(doc["expected_revision"].as<uint32_t>()!=old.revision)return failure(409,"revision");
    if(old.revision==UINT32_MAX)return failure(409,"revision_exhausted");
    auto rows=doc["profiles"].as<ArduinoJson::JsonArrayConst>();
    if(rows.size()>8)return failure(400,"profile_limit");
    auto &next=work->next;next.revision=old.revision+1;
    for(auto row:rows) {
        if(!row.is<ArduinoJson::JsonObjectConst>()||!fields(row.as<ArduinoJson::JsonObjectConst>(),"ssid","password")||
           !row["ssid"].is<const char *>())return failure(400,"profile_shape");
        auto ssid=row["ssid"].as<ArduinoJson::JsonString>();
        if(!ssidValid(ssid.c_str(),ssid.size()))return failure(400,"ssid");
        Ap01WifiProfile0041 p;memcpy(p.ssid,ssid.c_str(),ssid.size());p.saved=true;
        if(row["password"].isUnbound()) {
            int i=find(old,p.ssid);if(i<0)return failure(400,"password_required");
            strcpy(p.password,old.profiles[i].password);
        } else {
            if(!row["password"].is<const char *>())return failure(400,"password");
            auto pass=row["password"].as<ArduinoJson::JsonString>();
            if(pass.size()>64||memchr(pass.c_str(),0,pass.size()))return failure(400,"password");
            memcpy(p.password,pass.c_str(),pass.size());
        }
        int duplicate=find(next,p.ssid);
        if(duplicate>=0){if(strcmp(next.profiles[duplicate].password,p.password))return failure(400,"duplicate_conflict");continue;}
        next.profiles[next.count++]=p;
    }
    if(!port.store)return failure(503,"store_unavailable");
    auto &bytes=work->bytes;memcpy(bytes,"WPL1",4);word(bytes+4,next.revision);bytes[8]=uint8_t(next.count);
    for(unsigned i=0;i<next.count;++i){uint8_t *r=bytes+Header+i*Record;const auto &p=next.profiles[i];
        r[0]=uint8_t(strlen(p.ssid));memcpy(r+1,p.ssid,r[0]);r[33]=uint8_t(strlen(p.password));memcpy(r+34,p.password,r[33]);}
    unsigned length=Header+next.count*Record;word(bytes+12,crc(bytes,length));
    if(port.busy&&port.busy(port.context))return failure(503,"busy");
    if(port.store(port.context,bytes,length))return failure(503,"store_failed");
    auto &check=work->check;int got=port.load(port.context,check,sizeof(check));
    if(got!=int(length)||memcmp(bytes,check,length))return failure(503,"store_verification_failed",true);
    // Re-read current rather than inferring an activation from the saved list.
    if(ap01WifiProfilesRead0041(port,old))return failure(503,"readback_unavailable",true);
    auto response=reply(old,mac);
    if(response.status!=200)return failure(503,"response_unavailable",true);
    return response;
}
