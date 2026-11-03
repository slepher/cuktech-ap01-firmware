#pragma once
#include <stddef.h>
#include <stdint.h>
/* Standalone builds use native_sha256_0041.cpp. App builds may supply the same
   byte-oriented utility instead; link exactly one implementation. */
void syncSha256(const uint8_t *bytes,size_t length,uint8_t digest[32]);
// Bounded streaming state for package/file verification; no heap allocation.
class Ap01Sha256 {
    uint32_t h[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                     0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
    uint64_t length = 0;
    uint8_t pending[64] = {};
    unsigned used = 0;
    void block(const uint8_t *);
public:
    void update(const uint8_t *, size_t);
    void finish(uint8_t digest[32]); // Finalizes this state; do not update again.
};
/* IEEE CRC32 used by the existing APS1/AMT1 records and partition tables. */
static inline uint32_t ap01_native_crc32(const uint8_t *data,size_t n) {
    uint32_t crc=UINT32_MAX;
    while(n--){crc^=*data++;for(unsigned i=0;i<8;++i)crc=(crc>>1)^(0xedb88320u&(0u-(crc&1u)));}
    return ~crc;
}
