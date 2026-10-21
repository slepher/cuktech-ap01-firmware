#include "native_maintenance_0041.h"
#include "native_json_0041.h"
#include <new>
#if defined(__riscv)
extern "C" const uint8_t ap01_native_manifest[256];
#endif
namespace {
void imageIdentity(JsonDocument &out) {
    out["fw"] = "1.0.2_0041";
#if defined(__riscv)
    char build[33]; const char *hex="0123456789abcdef";
    for (unsigned i=0;i<16;++i) {uint8_t v=ap01_native_manifest[36+i];build[2*i]=hex[v>>4];build[2*i+1]=hex[v&15];}
    build[32]=0;out["app_build"] = String(build);
    const uint8_t *p=ap01_native_manifest+12;
    out["rom_bytes"] = uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16|uint32_t(p[3])<<24;
#else
    out["app_build"] = "host-native-port";
#endif
}
void error(Ap01HttpReply &reply, int status, const char *code, const char *stage, bool unknown = false) {
    NativeJsonAllocator0041 allocator; JsonDocument out(&allocator);
    out["result"] = unknown ? "unknown" : "rejected";
    out["error"] = code; out["stage"] = stage;
    out["action"] = unknown ? "query_original_request" : "read_device_status";
    reply.status = status; reply.bytes = "";
    if (out.overflowed() || !serializeJson(out, reply.bytes))
        reply.bytes = "{\"result\":\"unknown\",\"error\":\"reply_oom\",\"stage\":\"response\"}";
}
bool encode(JsonDocument &doc, Ap01HttpReply &reply) {
    size_t expected = measureJson(doc); reply.bytes = "";
    if (doc.overflowed() || expected > 4048 || !reply.bytes.reserve(expected) ||
        serializeJson(doc, reply.bytes) != expected || reply.bytes.length() != expected) {
        error(reply, 503, "reply_limit", "response", true); return false;
    }
    return true;
}
}
Ap01Maintenance0041::Ap01Maintenance0041(LittleFSClass &storage,const Ap01MaintenancePort0041 &p,
    const Ap01MaintenanceBridge0041 &b,const char *identity,uint64_t bootId)
    :fs(storage),port(p),bridge(b),boot(bootId) {
    mac[0]=0;if(identity&&strlen(identity)==12)memcpy(mac,identity,13);
}
bool Ap01Maintenance0041::begin(uint64_t now) {
    if(!mac[0])return false;
    if(port.firmware.open) {
        firmware.reset(new(std::nothrow) Ap01Firmware(fs,port.firmware,mac));
        if(firmware)firmware->begin(now);
        gate.store(!firmware||firmware->blocksBusiness(),std::memory_order_release);
    }
    return true;
}
bool Ap01Maintenance0041::manualAuth(const Ap01HttpRequest &request, uint64_t now, Ap01HttpReply &reply) {
    // Maintenance has one executor. No code is cached across requests/rotation.
    if (now < manualRetryAt) {
        reply.status = 429;
        reply.bytes = "{\"result\":\"rejected\",\"error\":\"device_code_rate_limited\",\"stage\":\"manual_auth\",\"action\":\"wait_30_seconds\"}";
        return false;
    }
    char code[9] = {};
    if (!port.deviceCode || port.deviceCode(port.context, code)) {
        reply.status = 503;
        reply.bytes = "{\"result\":\"rejected\",\"error\":\"device_code_unavailable\",\"stage\":\"manual_auth\",\"action\":\"open_device_code_menu\"}";
        return false;
    }
    unsigned mismatch = 0;
    if (!request.token || strlen(request.token) != 8) mismatch = 1;
    else for (unsigned i = 0; i < 8; ++i) mismatch |= unsigned(uint8_t(code[i]) ^ uint8_t(request.token[i]));
    memset(code, 0, sizeof(code));
    if (mismatch) {
        if (++manualFailures >= 5) { manualFailures = 0; manualRetryAt = now + 30000; }
        reply.status = 401;
        reply.bytes = "{\"result\":\"rejected\",\"error\":\"device_code\",\"stage\":\"manual_auth\",\"action\":\"enter_current_menu_code\"}";
        return false;
    }
    manualFailures = 0; manualRetryAt = 0;
    return true;
}

Ap01HttpReply Ap01Maintenance0041::handle(const Ap01HttpRequest &request,uint64_t now) {
    Ap01HttpReply reply;tick(now);
    bool wifi=!strncmp(request.path,"/api/wifi/",10), diagnostic=!strncmp(request.path,"/api/diagnostic/",16);
    if(wifi||diagnostic) {
        if(!manualAuth(request,now,reply))return reply;
        return wifi?ap01WifiProfilesHttp0041(port.wifiProfiles,request,mac):
                    ap01DiagnosticHttp0041(port.diagnostic,request,mac,boot);
    }
    if(!strncmp(request.path,"/api/pairing",12)) {
        if(bridge.pairing)return bridge.pairing(bridge.context,request,now);
        error(reply,503,"application_unavailable","pairing");return reply;
    }
    bool local=(!strncmp(request.path,"/api/firmware/",14)||!strcmp(request.path,"/health")||
                !strcmp(request.path,"/api/maintenance/status"))&&(!request.token||strlen(request.token)!=32);
    char principal[65]="ap01-menu-maintenance";
    if(local) {if(!manualAuth(request,now,reply))return reply;}
    else {
        int status=bridge.principal?bridge.principal(bridge.context,request.token,principal):401;
        if(status!=200){error(reply,status,status==401?"unauthorized":"maintenance_busy",status==401?"maintenance_auth":"bindings");return reply;}
    }
    if(!strncmp(request.path,"/api/firmware/",14)) {
        if(!firmware){error(reply,port.firmware.open?503:501,"firmware_port_unavailable","maintenance_router");return reply;}
        bool start=(!strcmp(request.path,"/api/firmware/begin")||!strcmp(request.path,"/api/firmware/switch"))&&!strcmp(request.method,"POST");
        if(start)gate.store(true,std::memory_order_release);
        reply=firmware->handle(request,principal,now);
        gate.store(firmware->blocksBusiness(),std::memory_order_release);return reply;
    }
    if(!strcmp(request.method,"GET")&&(!strcmp(request.path,"/health")||!strcmp(request.path,"/api/maintenance/status"))) {
        NativeJsonAllocator0041 allocator;JsonDocument out(&allocator);
        out["device_mac"]=mac;out["fw_target"]="cuktech-ap01-0041";out["boot_id"]=boot;imageIdentity(out);
        out["service"]="ap01-maintenance";out["http_port"]=18080;
        out["business_online"]=bridge.online&&bridge.online(bridge.context)&&!active();
        out["firmware_ota"]=firmware&&firmware->available()?"chunked-v1":"unavailable";
        out["firmware_update_policy"]="sequential_with_traditional_ota";
        reply.status=200;encode(out,reply);return reply;
    }
    error(reply,404,"unsupported_endpoint","maintenance_router");return reply;
}
void Ap01Maintenance0041::tick(uint64_t now) {
    if(firmware){firmware->tick(now);gate.store(firmware->blocksBusiness(),std::memory_order_release);}
}
