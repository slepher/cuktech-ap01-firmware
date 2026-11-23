// Exercise the production slot scanner with physical Flash reads emulated.
#include <cassert>
#include <cstdio>
#include <fstream>
#include <iterator>
#include <vector>
#include <cstring>
#include "native_rom_addresses.h"
#include "native_integrity.h"
static std::vector<uint8_t> flash;
static bool readFails=false;
static int readFlash(uint32_t address,void *out,unsigned n) {
    uint32_t base=address>=0x7b0000?0x7b0000:0x10000;
    if(readFails||address<base||address-base+n>flash.size())return -1;
    memcpy(out,flash.data()+address-base,n);return 0;
}
static uintptr_t romAddress(uintptr_t address) {
    assert(address==0xa0058e12);return reinterpret_cast<uintptr_t>(&readFlash);
}
#undef AP01_ROM_ADDR
#define AP01_ROM_ADDR(address) romAddress(address)
#include "native_slot.cpp"
static void put32(size_t at,uint32_t value) {
    for(unsigned i=0;i<4;++i)flash[at+i]=uint8_t(value>>(8*i));
}
static void recoveryCrc(size_t n) {
    // Recovery CRC uses zero initial state and no final inversion.
    uint32_t crc=0;
    for(size_t i=0;i<n-4;++i){crc^=flash[i];for(unsigned b=0;b<8;++b)crc=(crc>>1)^(0xedb88320u&(0u-(crc&1)));}
    put32(n-4,crc);
}
int main(int argc,char **argv) {
    assert(argc==2);std::ifstream f(argv[1],std::ios::binary);
    std::vector<uint8_t> original((std::istreambuf_iterator<char>(f)),{});
    assert(original.size()>0x675034);flash=original;flash.resize(0x700000,0xff);
    Ap01SlotImage image;
    // No mapping at 0x9ffff000 exists in this host process.
    assert(ap01InspectSlot0041(0,image));assert(image.length==original.size());
    assert(ap01InspectSlot0041(1,image));
    flash[0x675000+36]^=1;recoveryCrc(original.size());
    assert(ap01InspectSlot0041(0,image)); // Integrity does not depend on a running-memory comparison.
    flash[0x675000]=0;recoveryCrc(original.size());
    assert(ap01InspectSlot0041(0,image)); // Optional metadata on rescue images.
    flash=original;flash.resize(0x700000,0xff);flash[0x613400]^=1;
    assert(ap01InspectSlot0041(0,image)); // Installed bytes are not rechecked against transport CRC.
    flash=original;flash.resize(0x700000,0xff);flash[0]^=1;recoveryCrc(original.size());
    assert(!ap01InspectSlot0041(0,image)&&!strcmp(image.error,"slot_header_crc"));
    readFails=true;assert(!ap01InspectSlot0041(0,image)&&!strcmp(image.error,"slot_read"));
    assert(!ap01InspectSlot0041(2,image)&&!strcmp(image.error,"slot_bounds"));
    puts("slot inspection: installed metadata, rescue, header, read and bounds checks passed");
}
