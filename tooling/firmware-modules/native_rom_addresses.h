#pragma once
/* Keep the reviewed 0041 API names and layouts; select only ROM locations.
   Missing 0055 mappings are compile errors rather than implicit old addresses. */
#if defined(AP01_ROM_0055)
#include "native_rom_addresses_0055.h"
#define AP01_ROM_ADDR(address) AP01_ROM_0055_##address
#define AP01_STOCK_SCREEN_COUNT 11
#else
#define AP01_ROM_ADDR(address) address
#define AP01_STOCK_SCREEN_COUNT 9
#endif
#define AP01_ROM_STRING_IMPL(value) #value
#define AP01_ROM_STRING_EXPAND(value) AP01_ROM_STRING_IMPL(value)
#define AP01_ROM_STRING(address) AP01_ROM_STRING_EXPAND(AP01_ROM_ADDR(address))
