#include "native_device_code_font_0041.h"
#include <stddef.h>
#include <stdint.h>

namespace {
// 0041 ROM font wrappers at a025488c/a055fb7c, independently decoded by
// audit-ap01-rom-fonts.py. Original fmt_txt callbacks consume these tables;
// no replacement callback or inferred lv_font_glyph_dsc_t is needed.
struct Font {
    uintptr_t descriptorCallback, bitmapCallback, releaseCallback;
    int32_t lineHeight, baseline;
    uint32_t flags;
    const void *data;
    const Font *fallback;
    void *user;
};
struct Glyph { uint32_t bitmapAndAdvance; uint8_t width, height; int8_t x, y; };
struct Cmap {
    uint32_t first;
    uint16_t length, firstGlyph;
    const uint16_t *unicode;
    const void *offsets;
    uint16_t count;
    uint8_t kind, padding;
};
struct FontData {
    const uint8_t *bitmap;
    const Glyph *glyphs;
    const Cmap *cmaps;
    const void *kern;
    uint32_t packed;
    uint32_t stride;
};
static_assert(sizeof(void *) == 4 && sizeof(Font) == 36, "0041 RV32 font wrapper ABI");
static_assert(offsetof(Font, data) == 24 && offsetof(Font, fallback) == 28, "0041 font offsets");
static_assert(sizeof(Glyph) == 8 && sizeof(Cmap) == 20 && sizeof(FontData) == 24,
              "0041 compact fmt_txt font ABI");
#include "native_device_code_font_0041.inc"
// Stock selected face has all ten digits; the normal subset lacks 5/6/7/9.
// Keep an error-text fallback, but never mix individual digit faces.
static const Font NumberFont = {0xa00e4864,0xa00e45aa,0,20,2,0x0001fe00,
    (const void *)0xa037bfec,&NormalFont,nullptr};
// Exact complete original Montserrat14 descriptor: all printable ASCII,
// including Y and every digit. One face for the whole SSID in both states.
static const Font WifiFont = {0xa00e4864,0xa00e45aa,0,16,3,0x0001ff00,
    (const void *)0xa025fad8,&NormalFont,nullptr};
}

const void *ap01WifiSsidFont0041() {return &WifiFont;}

const void *ap01DeviceCodeFont0041(bool selected) {
    return selected ? &SelectedFont : &NormalFont;
}

const void *ap01DeviceCodeNumberFont0041() { return &NumberFont; }

const void *ap01DeviceCodeTitleFont0041() {
    return &TitleFont;
}
