#pragma once
#include "native_http_0041.h"
#include <stdint.h>
enum class Ap01SetHttpActionV3 {Status,Result,Begin,Chunk,Ready,Commit,Cancel};
struct Ap01SetHttpCommandV3 {
    Ap01SetHttpActionV3 action=Ap01SetHttpActionV3::Status;
    uint8_t transaction[16]{},expected[32]{};
    uint64_t expectedVersion=0;
    uint32_t index=0,offset=0;
    const uint8_t *bytes=nullptr;uint32_t length=0;
};
// Called only after device-code authentication by the maintenance router.
// Borrowed body is valid only during handle. No mutation or allocation here.
// Returns HTTP status 200 on valid syntax, 400/404/405/413 otherwise.
int ap01ParseSetHttpV3(const Ap01HttpRequest &,const char *deviceMac,Ap01SetHttpCommandV3 &);
