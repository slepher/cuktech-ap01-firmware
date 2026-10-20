#pragma once
#include <stddef.h>
#include <stdint.h>
/* Supplied by the application's shared SHA256 utility at final link time.
   This byte-oriented dependency does not import any business wire protocol. */
void syncSha256(const uint8_t *bytes,size_t length,uint8_t digest[32]);
/* IEEE CRC32 used by the existing APS1/AMT1 records and partition tables. */
static inline uint32_t ap01_native_crc32(const uint8_t *data,size_t n) {
    uint32_t crc=UINT32_MAX;
    while(n--){crc^=*data++;for(unsigned i=0;i<8;++i)crc=(crc>>1)^(0xedb88320u&(0u-(crc&1u)));}
    return ~crc;
}
