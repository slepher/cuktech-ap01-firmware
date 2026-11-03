#pragma once
#include "native_string_0041.h"
struct Ap01HttpRequest {
    const char *method, *path, *token, *deviceToken, *contentType;
    const char *requestId = "", *offset = "", *nonce = "";
    const uint8_t *body;
    size_t length;
    const char *chunkSha256 = "";
    const char *deviceMac = "";
};
struct Ap01HttpReply {
    int status = 500;
    bool frame = false;
    String bytes;
};
