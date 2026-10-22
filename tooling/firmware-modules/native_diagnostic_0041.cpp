#include "native_diagnostic_0041.h"
#include "native_json_0041.h"
#include "native_integrity_0041.h"
#include <new>
#include <memory>

namespace {
Ap01HttpReply failure(int status, const char *error, int native = 0) {
    Ap01HttpReply reply; reply.status = status;
    char text[256];
    int n = snprintf(text, sizeof(text),
        "{\"result\":\"rejected\",\"error\":\"%s\",\"native_error\":%d,"
        "\"stage\":\"diagnostic\",\"action\":\"read_diagnostic_status\"}", error, native);
    if (n > 0 && size_t(n) < sizeof(text)) reply.bytes = text;
    return reply;
}
bool readablePath(const char *path) {
    if (!path || strlen(path) > 127 ||
        (strncmp(path, "/data/", 6) && strncmp(path, "/resource/", 10) && strcmp(path, "/dev/ramlog"))) return false;
    for (const char *p = path; *p; ++p) {
        if ((unsigned char)*p < 32 || *p == '\\') return false;
        if (*p == '/' && (p[1] == '/' || !p[1] ||
            (p[1] == '.' && (!p[2] || p[2] == '/' || (p[2] == '.' && (!p[3] || p[3] == '/')))))) return false;
    }
    return true;
}

}
Ap01HttpReply ap01DiagnosticHttp0041(const Ap01DiagnosticPort &port, const Ap01HttpRequest &request,
                                    const char *mac, uint64_t boot) {
    NativeJsonAllocator0041 allocator;
    ArduinoJson::JsonDocument input(&allocator), output(&allocator);
    bool status = !strcmp(request.path, "/api/diagnostic/status");
    bool file = !strcmp(request.path, "/api/diagnostic/file");
    bool flash = !strcmp(request.path, "/api/diagnostic/flash");
    if (!status && !file && !flash) return failure(404, "unsupported_endpoint");
    if (strcmp(request.method, status ? "GET" : "POST")) return failure(405, "method");
    if (!status) {
        if (strcmp(request.contentType, "application/json") || request.length > 1024 ||
            ArduinoJson::deserializeJson(input, request.body, request.length) || !input.is<ArduinoJson::JsonObject>())
            return failure(400, "json");
        if (!input["device_mac"].is<const char *>() || strcmp(input["device_mac"].as<const char *>(), mac))
            return failure(409, "device_identity");
    }
    if (output["result"].set("ok") && output["device_mac"].set(mac)) {
        output["protocol"] = "ap01-diagnostic-0041-v1";
        output["boot_id"] = boot;
        output["max_chunk_bytes"] = 1024;
        output["flash_bytes"] = 0x1000000u;
        output["file_reader"] = port.file != nullptr;
        output["flash_reader"] = port.flash != nullptr;
    }
    if (!status) {
        if (!input["offset"].is<uint32_t>() || !input["length"].is<unsigned>()) return failure(400, "range");
        uint32_t offset = input["offset"].as<uint32_t>();
        unsigned length = input["length"].as<unsigned>();
        if (!length || length > 1024 || (flash && (offset >= 0x1000000u || length > 0x1000000u-offset)))
            return failure(400, "range");
        const char *path = file && input["path"].is<const char *>() ? input["path"].as<const char *>() : nullptr;
        if (file && !readablePath(path)) return failure(400, "path");
        if ((file && !port.file) || (flash && !port.flash)) return failure(501, "reader_unavailable");
        if (port.busy && port.busy(port.context)) return failure(503, "flash_busy");
        std::unique_ptr<uint8_t[]> bytes(new(std::nothrow) uint8_t[length]);
        std::unique_ptr<char[]> hex(new(std::nothrow) char[2*length+1]);
        if (!bytes || !hex) return failure(503, "oom");
        uint32_t total = 0x1000000u;
        int got = file ? port.file(port.context,path,offset,bytes.get(),length,&total) :
                         port.flash(port.context,offset,bytes.get(),length);
        if (got < 0) return failure(got == -2 ? 404 : got == -11 ? 409 : 503, "read", got);
        if (unsigned(got) > length || (flash && unsigned(got) != length)) return failure(503,"short_read");
        const char *digits = "0123456789abcdef";
        for (int i=0;i<got;++i) {hex[2*i]=digits[bytes[i]>>4];hex[2*i+1]=digits[bytes[i]&15];}
        hex[2*got]=0;
        output["source"] = file ? path : "physical_flash";
        output["offset"] = offset; output["length"] = got;
        if (total != UINT32_MAX) {output["total_bytes"]=total;output["eof"]=offset<=total&&unsigned(got)==total-offset;}
        output["crc32"] = ap01_native_crc32(bytes.get(),got);
        output["data_hex"] = hex.get();
    }
    if (output.overflowed()) return failure(503,"oom");
    size_t size = ArduinoJson::measureJson(output);
    std::unique_ptr<char[]> text(new(std::nothrow) char[size+1]);
    if (!text || ArduinoJson::serializeJson(output,text.get(),size+1) != size) return failure(503,"encode");
    Ap01HttpReply reply; reply.bytes = String(text.get(),size);
    if (reply.bytes.length() != size) return failure(503,"oom");
    reply.status=200; return reply;
}
