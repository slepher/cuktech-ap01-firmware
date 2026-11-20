#pragma once
// Reviewed current-ROM locations; missing mappings are compilation errors.
#include "native_rom_map.h"
#define AP01_ROM_ADDR(address) AP01_ROM_ADDRESS_##address
#define AP01_STOCK_SCREEN_COUNT 11
#define AP01_ROM_STRING_IMPL(value) #value
#define AP01_ROM_STRING_EXPAND(value) AP01_ROM_STRING_IMPL(value)
#define AP01_ROM_STRING(address) AP01_ROM_STRING_EXPAND(AP01_ROM_ADDR(address))
