#!/usr/bin/env python3
"""Build local LVGL descriptors from the verified AP01 0041 ROM.

Requires ImageMagick convert. Generated proprietary asset bytes stay in the
local build/evidence directory; this script contains offsets, not ROM data.
"""
import argparse
import io
from PIL import Image
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import zlib

SHA256 = "972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9"
DIGITS = [0x255b18, 0x377790, 0x377998, 0x377c9c, 0x378034,
          0x378250, 0x378554, 0x3788cc, 0x378ad0, 0x378e70]
BASE = 0x9ffff000


def native_font(rom, address, include_kerning=False):
    """Read the original little-endian LVGL packed glyph/cmap records."""
    def offset(pointer, size):
        value = pointer - BASE
        if not 0 <= value <= len(rom) - size:
            raise ValueError(f"Font pointer outside ROM: {pointer:#x}")
        return value

    wrapper = offset(address, 28)
    height, baseline, fmt = struct.unpack_from("<ii4xI", rom, wrapper + 12)
    bitmap, metrics, cmaps, kern, packed = struct.unpack_from("<5I", rom, offset(fmt, 24))
    count, bpp = (packed >> 16) & 0x1ff, (packed >> 25) & 15
    assert 0 < height <= 128 and 0 <= baseline < height
    assert 0 < count <= 4 and bpp == 4 and packed >> 30 == 0
    points = []
    for cmap_index in range(count):
        cmap = offset(cmaps + cmap_index * 20, 20)
        start, length, first, unicodes, indexes, items, kind = struct.unpack_from("<IHHIIHB", rom, cmap)
        if kind == 0:
            indexes = offset(indexes, length)
            points.extend((start + i, first + rom[indexes + i]) for i in range(length)
                          if i == 0 or rom[indexes + i] != 0)
        elif kind == 2:
            assert unicodes == 0 and indexes == 0
            points.extend((start + i, first + i) for i in range(length))
        elif kind == 3:
            unicodes = offset(unicodes, items * 2)
            points.extend((start + struct.unpack_from("<H", rom, unicodes + i * 2)[0], first + i)
                          for i in range(items))
        else:
            raise ValueError(f"Unsupported native cmap type {kind}")
    points.sort()
    assert len({code for code, gid in points}) == len(points)
    glyphs, pixels, advances = [], bytearray(), {}
    for code, gid in points:
        word, width, rows, x, y = struct.unpack_from("<IBBbb", rom, offset(metrics + gid * 8, 8))
        assert width <= 128 and rows <= 128
        data = offset(bitmap + (word & 0xfffff), (width * rows + 1) // 2)
        glyphs.append((code, len(pixels), ((word >> 20) + 8) >> 4, width, rows, x, y))
        advances[gid] = word >> 20
        for i in range(width * rows):
            value = rom[data + i // 2]
            pixels.append(((value >> 4) if i % 2 == 0 else (value & 15)) * 17)
    if not include_kerning:
        return height, baseline, glyphs, pixels
    pairs = []
    if kern:
        scale = packed & 0xffff
        gids = {gid: code for code, gid in points}
        if (packed >> 29) & 1:
            values, left, right, left_count, right_count = struct.unpack_from("<IIIBB", rom, offset(kern, 14))
            for left_gid, left_code in gids.items():
                left_class = rom[offset(left + left_gid, 1)]
                for right_gid, right_code in gids.items():
                    right_class = rom[offset(right + right_gid, 1)]
                    assert left_class <= left_count and right_class <= right_count
                    if left_class and right_class:
                        value = struct.unpack_from("<b", rom, offset(values + (left_class - 1) * right_count + right_class - 1, 1))[0]
                        adjustment = ((advances[left_gid] + ((value * scale) >> 4) + 8) >> 4) - ((advances[left_gid] + 8) >> 4)
                        if adjustment: pairs.append((left_code, right_code, adjustment))
        else:
            ids, values, pair_word = struct.unpack_from("<III", rom, offset(kern, 12))
            count, wide = pair_word & 0x3fffffff, pair_word >> 30
            assert count <= 100000 and wide <= 1
            size = 2 if wide else 1
            for index in range(count):
                left_gid, right_gid = struct.unpack_from("<HH" if wide else "<BB", rom, offset(ids + index * size * 2, size * 2))
                value = struct.unpack_from("<b", rom, offset(values + index, 1))[0]
                if left_gid in gids and right_gid in gids:
                    adjustment = ((advances[left_gid] + ((value * scale) >> 4) + 8) >> 4) - ((advances[left_gid] + 8) >> 4)
                    if adjustment: pairs.append((gids[left_gid], gids[right_gid], adjustment))
    return height, baseline, glyphs, pixels, pairs


def write_native_fonts(out, rom):
    out.write(r'''
typedef struct { uint32_t unicode, offset; uint16_t advance;
  uint8_t width, height; int8_t x, y; } ap01_rom_glyph_t;
typedef struct { uint32_t left, right; int16_t adjustment; } ap01_rom_kern_t;
typedef struct { unsigned count; const ap01_rom_glyph_t *glyphs;
  const uint8_t *pixels; unsigned kern_count; const ap01_rom_kern_t *kern; } ap01_rom_font_data_t;
static bool ap01_rom_font_descriptor(const lv_font_t *font,
  lv_font_glyph_dsc_t *d, uint32_t letter, uint32_t next)
{
  const ap01_rom_font_data_t *data = font->dsc;
  for (unsigned i = 0; i < data->count; ++i)
    if (data->glyphs[i].unicode == letter)
      {
        const ap01_rom_glyph_t *g = &data->glyphs[i];
        d->adv_w = g->advance; d->box_w = g->width; d->box_h = g->height;
        for (unsigned k = 0; next && k < data->kern_count; ++k)
          if (data->kern[k].left == letter && data->kern[k].right == next)
            { d->adv_w = g->advance + data->kern[k].adjustment; break; }
        d->ofs_x = g->x; d->ofs_y = g->y;
        d->format = LV_FONT_GLYPH_FORMAT_A8;
        d->is_placeholder = false; d->gid.index = i;
        return true;
      }
  return false;
}
static const void *ap01_rom_font_bitmap(lv_font_glyph_dsc_t *d, lv_draw_buf_t *buf)
{
  if (buf == NULL) return NULL;
  const ap01_rom_font_data_t *data = d->resolved_font->dsc;
  const ap01_rom_glyph_t *g = &data->glyphs[d->gid.index];
  for (unsigned y = 0; y < g->height; ++y)
    memcpy(buf->data + y * buf->header.stride,
           data->pixels + g->offset + y * g->width, g->width);
  return buf;
}
''')
    records = []
    for name, address, fallback in [
        ("ap01_rom_ascii17", 0xa02549ac, "ap01_font"),
        ("ap01_rom_body20", 0xa025488c, "ap01_rom_ascii17"),
        ("ap01_rom_title25", 0xa02548d4, "ap01_rom_body20"),
        ("ap01_rom_clock21", 0xa02549f4, "ap01_rom_ascii17"),
        ("ap01_rom_month", 0xa02547b4, "ap01_rom_body20"),
        ("ap01_rom_year", 0xa0254988, "ap01_rom_ascii17"),
        ("ap01_rom_calendar_week", 0xa037253c, "ap01_rom_body20"),
        ("ap01_rom_mini_date", 0xa0254a60, "ap01_rom_ascii17"),
        ("ap01_rom_weather_text", 0xa0254820, "ap01_rom_body20"),
        ("ap01_rom_mini_week", 0xa0254844, "ap01_rom_weather_text"),
        ("ap01_rom_temperature", 0xa0254a84, "ap01_rom_ascii17"),
        ("ap01_rom_guide_title", 0xa055fb7c, "ap01_rom_body20"),
        ("ap01_rom_guide_text", 0xa02547fc, "ap01_rom_body20"),
        ("ap01_rom_charge_gauge", 0xa0254700, "ap01_rom_body20"),
        ("ap01_rom_charge_port", 0xa0254724, "ap01_rom_body20"),
        ("ap01_rom_charge_watt", 0xa0254748, "ap01_rom_body20"),
        ("ap01_rom_charge_number", 0xa025476c, "ap01_rom_body20"),
        ("ap01_rom_charge_status", 0xa02547d8, "ap01_rom_body20"),
        ("ap01_rom_charge_excellent", 0xa0254aa8, "ap01_rom_body20"),
        ("ap01_rom_detail_metric", 0xa0254a18, "ap01_rom_body20"),
        ("ap01_rom_detail_caption", 0xa0254964, "ap01_rom_body20"),
        ("ap01_rom_humidity_digits", 0xa05647b4, "ap01_rom_body20"),
        ("ap01_rom_humidity_unit", 0xa0564790, "ap01_rom_body20"),
        ("ap01_rom_forecast", 0xa0372584, "ap01_rom_body20"),
        ("ap01_rom_weather_note", 0xa0564748, "ap01_rom_body20"),
        ("ap01_rom_weather_temp", 0xa05647d8, "ap01_rom_body20"),
        ("ap01_rom_date_heading", 0xa055fb58, "ap01_rom_body20"),
        ("ap01_rom_mijia_hint", 0xa0254868, "ap01_rom_body20"),
        ("ap01_rom_charge_title", 0xa0254790, "ap01_rom_body20"),
        ("ap01_rom_charge_percent", 0xa059bee4, "ap01_rom_body20"),
        ("ap01_rom_charge_percent_unit", 0xa059be9c, "ap01_rom_body20"),
        ("ap01_rom_charge_port_number", 0xa0630ad0, "ap01_rom_body20"),
        ("ap01_rom_charge_card_label", 0xa0630af4, "ap01_rom_body20"),
        ("ap01_rom_charge_card_unit", 0xa0630aac, "ap01_rom_body20"),
        ("ap01_rom_charge_card_value", 0xa0630a88, "ap01_rom_body20"),
        ("ap01_rom_charge_popup_port", 0xa066b5ec, "ap01_rom_body20"),
        ("ap01_rom_charge_popup_percent", 0xa066b610, "ap01_rom_body20"),
        ("ap01_rom_charge_popup_percent_unit", 0xa066b5c8, "ap01_rom_body20"),
        ("ap01_rom_charge_popup_power", 0xa066b634, "ap01_rom_body20"),
        ("ap01_rom_charge_popup_brand", 0xa066b658, "ap01_rom_body20"),
        ("ap01_rom_charge_protocol_port", 0xa06015e4, "ap01_rom_body20"),
        ("ap01_rom_charge_error", 0xa02548b0, "ap01_rom_body20"),
        ("ap01_rom_charge_device_name", 0xa066b67c, "ap01_rom_body20"),
        ("ap01_rom_guide_welcome", 0xa0606ac8, "ap01_rom_body20"),
        ("ap01_rom_guide_practice_body", 0xa0372560, "ap01_rom_body20"),
        ("ap01_rom_guide_prompt", 0xa066b5a4, "ap01_rom_body20"),
        ("ap01_rom_saver_time", 0xa03725a8, "ap01_rom_body20"),
        ("ap01_rom_saver_decimal", 0xa0372518, "ap01_rom_body20"),
        ("ap01_rom_saver_watt", 0xa03724f4, "ap01_rom_body20"),
        ("ap01_rom_saver_day", 0xa02549d0, "ap01_rom_body20"),
        ("ap01_rom_calendar_subtitle", 0xa060d91c, "ap01_rom_body20"),
        ("ap01_rom_calendar_day", 0xa060d940, "ap01_rom_ascii17"),
        ("ap01_rom_charge_live_power3", 0xa062c514, "ap01_rom_body20"),
        ("ap01_rom_power_battery", 0xa025491c, "ap01_rom_ascii17"),
        ("ap01_rom_power_battery_unit", 0xa02548f8, "ap01_rom_ascii17"),
    ]:
        height, baseline, glyphs, pixels, pairs = native_font(rom, address, True)
        out.write(f"static const ap01_rom_kern_t {name}_kern[] = {{\n")
        for pair in pairs or [(0, 0, 0)]:
            out.write("{" + ",".join(map(str, pair)) + "},\n")
        out.write("};\n")
        out.write(f"static const ap01_rom_glyph_t {name}_glyphs[] = {{\n")
        for row in glyphs:
            out.write("{" + ",".join(map(str, row)) + "},\n")
        out.write(f"}};\nstatic const uint8_t {name}_pixels[] = {{\n")
        for i in range(0, len(pixels), 64):
            out.write(",".join(map(str, pixels[i:i + 64])) + ",\n")
        out.write(f"}};\nstatic const ap01_rom_font_data_t {name}_data = "
                  f"{{{len(glyphs)}, {name}_glyphs, {name}_pixels, {len(pairs)}, {name}_kern}};\n"
                  f"static const lv_font_t {name} = {{"
                  ".get_glyph_dsc=ap01_rom_font_descriptor,"
                  ".get_glyph_bitmap=ap01_rom_font_bitmap,"
                  f".line_height={height},.base_line={baseline},"
                  f".dsc=&{name}_data,.fallback=&{fallback}}};\n")
        records.append({"name": name, "wrapper": hex(address), "height": height,
                        "baseline": baseline, "glyphs": len(glyphs), "kerning_restored": True, "kerning_pairs":len(pairs)})
    out.write("#define ap01_rom_charge_live_power ap01_rom_detail_metric\n"
              "#define ap01_rom_system_hint ap01_rom_mijia_hint\n"
              "#define ap01_rom_system_version ap01_rom_forecast\n"
              "#define ap01_rom_system_button ap01_rom_guide_welcome\n")
    return records


def png_at(rom, offset):
    assert rom[offset:offset + 8] == b"\x89PNG\r\n\x1a\n", hex(offset)
    end = offset + 8
    width = height = None
    while True:
        assert end + 12 <= len(rom), "Truncated PNG chunk"
        size = struct.unpack_from(">I", rom, end)[0]
        kind = rom[end + 4:end + 8]
        payload = rom[end + 8:end + 8 + size]
        assert end + 12 + size <= len(rom), "PNG outside ROM"
        crc = struct.unpack_from(">I", rom, end + 8 + size)[0]
        assert zlib.crc32(kind + payload) == crc, "PNG CRC mismatch"
        if kind == b"IHDR":
            width, height = struct.unpack_from(">II", payload)
            assert 0 < width <= 320 and 0 < height <= 240
        end += size + 12
        if kind == b"IEND":
            assert size == 0 and width is not None
            return rom[offset:end], width, height


def generate(rom_path, output):
    assert output.parent.is_dir(), "Output directory must be pre-created"
    rom = rom_path.read_bytes()
    if len(rom) != 6769704 or hashlib.sha256(rom).hexdigest() != SHA256:
        raise ValueError("Expected unmodified AP01 1.0.2_0041 ROM")
    records = []
    with output.open("w") as out:
        out.write("/* Generated locally from verified AP01 0041; do not commit. */\n"
                  "#include <lvgl/lvgl.h>\n#include <string.h>\n")

        def descriptor(name, data, width, height, color):
            out.write(f"static const uint8_t {name}_bytes[] = {{\n")
            for i in range(0, len(data), 32):
                out.write(",".join(f"0x{b:02x}" for b in data[i:i + 32]) + ",\n")
            out.write("};\n")
            value = ("{.header={.magic=LV_IMAGE_HEADER_MAGIC,"
                     f".cf=LV_COLOR_FORMAT_{color},.w={width},.h={height},"
                     f".stride={width * 4 if color == 'ARGB8888' else 0}}},"
                     f".data_size=sizeof({name}_bytes),.data={name}_bytes}}")
            return value

        image_sources = {}
        for name, offset in [("ap01_arc", 0x62f440), ("ap01_logo", 0x242680),
                             ("ap01_sun", 0x252ff0), ("ap01_colon", 0x25621c),
                             ("ap01_sunrise", 0x253810), ("ap01_sunset", 0x2539d8),
                             ("ap01_wifi", 0x252aa8), ("ap01_wifi_off", 0x37107c), ("ap01_setting_row", 0x55f694),
                             ("ap01_clock_status", 0x243824),
                             ("ap01_time_humidity_icon", 0x252c14),
                             ("ap01_power_card", 0x2528cc),
                             ("ap01_power_gradient", 0x251d80),
                             ("ap01_power_status", 0x243590),
                             ("ap01_power_battery", 0x243824),
                             ("ap01_guide_turn", 0x5894c4), ("ap01_guide_press", 0x593064),
                             ("ap01_guide_button", 0x66bd44),
                             ("ap01_brightness_row", 0x55f9ec),
                             ("ap01_brightness_icon", 0x607894),
                             ("ap01_charge_mode_card", 0x55fd60),
                             ("ap01_charge_port_card", 0x560488),
                             ("ap01_charge_mode_icon", 0x55f3f4),
                             ("ap01_mijia_qr", 0x243950),
                             ("ap01_charge_protocol_bg", 0x5ecc1c),
                             ("ap01_charge_protocol_title", 0x5ebffc),
                             ("ap01_charge_protocol_caption", 0x5fef60),
                             ("ap01_charge_protocol_scan", 0x5eb7e4),
                             ("ap01_charge_safe_title", 0x5e99cc),
                             ("ap01_charge_safe_caption", 0x5ea9e0),
                             ("ap01_charge_safe_hint", 0x5e9e18),
                             ("ap01_charge_port_icon", 0x62fd0c),
                             ("ap01_charge_cable_icon", 0x55f530),
                             ("ap01_guide_practice_intro", 0x575938),
                             ("ap01_guide_practice_turn_done", 0x57f8d8),
                             ("ap01_guide_practice_power", 0x56f790),
                             ("ap01_guide_practice_c1_done", 0x571eb8),
                             ("ap01_guide_bubble50", 0x36ff8c),
                             ("ap01_guide_bubble70", 0x370230),
                             ("ap01_guide_bubble90", 0x370510),
                             ("ap01_boot_logo", 0x242680),
                             ("ap01_saver_glow_top", 0x365dc0),
                             ("ap01_saver_glow_bottom", 0x36c978),
                             ("ap01_saver_curve", 0x365184),
                             ("ap01_saver_fast", 0x37082c),
                             ("ap01_saver_thermometer", 0x252dc4),
                             ("ap01_system_mijia_qr", 0x243950),
                             ("ap01_system_binding_timeout", 0x247f68),
                             ("ap01_system_ota_success", 0x605d24),
                             ("ap01_system_confirm_button", 0x60759c),
                             ("ap01_system_version_card", 0x5600e4),
                             ("ap01_weather_aqi_scale", 0x564644),
                             ("ap01_time_temperature_icon", 0x252dc4)]:
            png, w, h = png_at(rom, offset)
            if offset in image_sources:
                out.write(f"#define {name} {image_sources[offset]}\n")
                records.append({"name": name, "offset": hex(offset), "size": len(png),
                                "alias_of": image_sources[offset]})
                continue
            image_sources[offset] = name
            raw = Image.open(io.BytesIO(png)).convert("RGBA").tobytes("raw", "BGRA")
            assert len(raw) == w * h * 4
            value = descriptor(name, raw, w, h, "ARGB8888")
            out.write(f"static const lv_image_dsc_t {name} = {value};\n")
            records.append({"name": name, "offset": hex(offset), "size": len(png)})
        digits = []
        for i, offset in enumerate(DIGITS):
            png, w, h = png_at(rom, offset)
            assert (w, h) == (55, 50)
            raw = Image.open(io.BytesIO(png)).convert("RGBA").tobytes("raw", "BGRA")
            assert len(raw) == w * h * 4
            digits.append(descriptor(f"ap01_digit_{i}", raw, w, h, "ARGB8888"))
            records.append({"name": f"digit{i}", "offset": hex(offset), "size": len(png)})
        out.write("static const lv_image_dsc_t ap01_digits[10] = {\n" +
                  ",\n".join(digits) + "\n};\n")
        pets = []
        # Native five-item pet table at 0xa055fe44, traversed by key 10.
        for index in range(5):
            wrapper = struct.unpack_from("<I", rom, 0xa055fe44 - BASE + index * 4)[0]
            size, data = struct.unpack_from("<II", rom, wrapper - BASE + 12)
            offset = data - BASE
            assert 0 < size <= 1024 * 1024 and 0 <= offset <= len(rom) - size
            gif = rom[offset:offset + size]
            assert gif[:6] in (b"GIF87a", b"GIF89a") and gif[-1:] == b";"
            assert struct.unpack_from("<HH", gif, 6) == (320, 240)
            pets.append(descriptor(f"ap01_pet_{index}", gif, 320, 240, "RAW"))
            records.append({"name": f"ap01_pet_{index}", "offset": hex(offset),
                            "size": len(gif), "sha256": hashlib.sha256(gif).hexdigest()})
        out.write("static const lv_image_dsc_t ap01_pets[5] = {\n" +
                  ",\n".join(pets) + "\n};\n")
        extra_gifs = {}
        for name, offset, size in [
            ("ap01_charge_bank_insert", 0x643fc0, 130357),
            ("ap01_charge_safe_intro", 0x5b067c, 230831),
            ("ap01_saver_time_0", 0x28e838, 187664),
            ("ap01_saver_time_1", 0x2bc564, 157250),
            ("ap01_saver_power", 0x2e2bc4, 502081),
        ]:
            gif = rom[offset:offset + size]
            assert gif[:6] in (b"GIF87a", b"GIF89a") and gif[-1] == 0x3b
            width, height = struct.unpack_from("<HH", gif, 6)
            extra_gifs[name] = descriptor(name, gif, width, height, "RAW")
            if not name.startswith("ap01_saver_time_"):
                out.write(f"static const lv_image_dsc_t {name} = {extra_gifs[name]};\n")
            records.append({"name": name, "offset": hex(offset), "size": size,
                            "sha256": hashlib.sha256(gif).hexdigest()})
        out.write("static const lv_image_dsc_t ap01_saver_time[2] = {\n" +
                  ",\n".join(extra_gifs[f"ap01_saver_time_{i}"] for i in range(2)) + "\n};\n")
        saver_digits = []
        for color, table in enumerate((0xa03761b0, 0xa0376748)):
            row = []
            for digit in range(10):
                wrapper = struct.unpack_from("<I", rom, table - BASE + digit * 4)[0]
                _, data = struct.unpack_from("<II", rom, wrapper - BASE + 12)
                png, width, height = png_at(rom, data - BASE)
                raw = Image.open(io.BytesIO(png)).convert("RGBA").tobytes("raw", "BGRA")
                row.append(descriptor(f"ap01_saver_digit_{color}_{digit}", raw, width, height, "ARGB8888"))
            saver_digits.append("{\n" + ",\n".join(row) + "\n}")
        out.write("static const lv_image_dsc_t ap01_saver_digits[2][10] = {\n" + ",\n".join(saver_digits) + "\n};\n")
        for symbol, offsets in [("dot", (0x3771f8, 0x3772dc)), ("watt", (0x3773c4, 0x377550))]:
            values = []
            for color, offset in enumerate(offsets):
                png, width, height = png_at(rom, offset)
                raw = Image.open(io.BytesIO(png)).convert("RGBA").tobytes("raw", "BGRA")
                values.append(descriptor(f"ap01_saver_{symbol}_{color}", raw, width, height, "ARGB8888"))
            out.write(f"static const lv_image_dsc_t ap01_saver_{symbol}[2] = {{\n" + ",\n".join(values) + "\n};\n")
        for symbol, offsets in [
            ("condition", ((0x564df0, 0x62b0fc, 0x62a104), (0x62b9f8, 0x62b554, 0x62a5b0))),
            ("forecast", ((0x3724c0, 0x372038, 0x3717a0), (0x37278c, 0x372270, 0x371a14))),
        ]:
            rows = []
            for night, positions in enumerate(offsets):
                row = []
                for condition, offset in enumerate(positions):
                    png, width, height = png_at(rom, offset)
                    raw = Image.open(io.BytesIO(png)).convert("RGBA").tobytes("raw", "BGRA")
                    row.append(descriptor(f"ap01_weather_{symbol}_{night}_{condition}", raw, width, height, "ARGB8888"))
                rows.append("{" + ",".join(row) + "}")
            out.write(f"static const lv_image_dsc_t ap01_weather_{symbol}[2][3] = {{" + ",".join(rows) + "};\n")
        for symbol, wrappers in [
            ("large", {1:0xa0563dd4,2:0xa062a9dc,3:0xa062a0e0,4:0xa062a538,5:0xa0628940,6:0xa0628738,7:0xa0628e38,8:0xa06290e8,9:0xa0629594,10:0xa062c014,11:0xa062bc54,12:0xa0629da8,13:0xa0629aa0,14:0xa0628be8,17:0xa0628e38,22:0xa062b03c,23:0xa062b650}),
            ("small", {1:0xa03714a4,2:0xa0371770,3:0xa037101c,4:0xa0371254,5:0xa037031c,6:0xa03701d4,7:0xa03705fc,8:0xa0370784,9:0xa03709f8,10:0xa03720c8,11:0xa0371ea8,12:0xa0370e30,13:0xa0370c84,14:0xa0370494,17:0xa03705fc,22:0xa0371a48,23:0xa0371c70}),
            ("tiny", {1:0xa0251da8,2:0xa062ff20,3:0xa062fb30,4:0xa062fd24,5:0xa062f000,6:0xa062eee8,7:0xa062f2bc,8:0xa062f414,9:0xa062f618,10:0xa0630838,11:0xa0630658,12:0xa062f9a4,13:0xa062f834,14:0xa062f16c,17:0xa062f2bc,22:0xa0630190,23:0xa06303f0}),
        ]:
            sources, items = {}, ["NULL"] * 24
            for index, wrapper in wrappers.items():
                if wrapper not in sources:
                    pointer = struct.unpack_from("<I", rom, wrapper - BASE + 16)[0]
                    png, width, height = png_at(rom, pointer - BASE)
                    raw = Image.open(io.BytesIO(png)).convert("RGBA").tobytes("raw", "BGRA")
                    name = f"ap01_weather_{symbol}_native_{index}"
                    value = descriptor(name, raw, width, height, "ARGB8888")
                    out.write(f"static const lv_image_dsc_t {name} = {value};\n")
                    sources[wrapper] = "&" + name
                    records.append({"name":name,"wrapper":hex(wrapper),"offset":hex(pointer-BASE),"size":len(png)})
                items[index] = sources[wrapper]
            out.write(f"static const lv_image_dsc_t *const ap01_weather_{symbol}[24] = {{" + ",".join(items) + "};\n")
        # LVGL's bundled CJK subset misses several labels. This is an explicit
        # reconstruction font, not a recovered original AP01 font.
        font = Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
        ui_source = "".join(p.read_text() for p in Path(__file__).parent.glob("ap01-*.h"))
        characters = sorted({c for c in ui_source
                             if (0x3000 <= ord(c) <= 0x9fff or
                                 0xff00 <= ord(c) <= 0xffef or
                                 0x2000 <= ord(c) <= 0x22ff) and c.isprintable()})
        out.write("static const uint32_t ap01_font_unicode[] = {" +
                  ",".join(str(ord(c)) for c in characters) + "};\n")
        out.write("static const uint8_t ap01_font_pixels[][320] = {\n")
        for char in characters:
            pixels = subprocess.run(
                ["convert", "-size", "16x20", "xc:black", "-font", str(font),
                 "-pointsize", "16", "-fill", "white", "-gravity", "center",
                 "-annotate", "+0+0", char, "-depth", "8", "gray:-"],
                capture_output=True, check=True).stdout
            assert len(pixels) == 320
            out.write("{" + ",".join(str(b) for b in pixels) + "},\n")
        out.write("};\n" + r'''
static bool ap01_font_descriptor(const lv_font_t *font,
  lv_font_glyph_dsc_t *d, uint32_t letter, uint32_t next)
{
  (void)font; (void)next;
  for (unsigned i = 0; i < sizeof(ap01_font_unicode) / sizeof(uint32_t); ++i)
    if (ap01_font_unicode[i] == letter)
      {
        d->adv_w = 16; d->box_w = 16; d->box_h = 20;
        d->ofs_x = 0; d->ofs_y = -3;
        d->format = LV_FONT_GLYPH_FORMAT_A8;
        d->is_placeholder = false; d->gid.index = i;
        return true;
      }
  return false;
}
static const void *ap01_font_bitmap(lv_font_glyph_dsc_t *d, lv_draw_buf_t *buf)
{
  if (buf == NULL) return NULL;
  for (unsigned y = 0; y < 20; ++y)
    memcpy(buf->data + y * buf->header.stride,
           ap01_font_pixels[d->gid.index] + y * 16, 16);
  return buf;
}
static const lv_font_t ap01_font = {
  .get_glyph_dsc = ap01_font_descriptor, .get_glyph_bitmap = ap01_font_bitmap,
  .line_height = 20, .base_line = 3, .fallback = &lv_font_montserrat_14
};
''')
        def rom_string(pointer):
            start = pointer - BASE
            assert 0 <= start < len(rom)
            end = rom.index(0, start, start + 256)
            return json.dumps(rom[start:end].decode("utf-8"), ensure_ascii=False)
        for name, address in [("ap01_lunar_month_bits", 0xa059bac0), ("ap01_lunar_new_year", 0xa066b6a0)]:
            values = struct.unpack_from("<225I", rom, address - BASE)
            assert values[0] == 1887
            out.write(f"static const uint32_t {name}[225] = {{" + ",".join(map(str, values)) + "};\n")
        for name, address, count in [("ap01_lunar_day_names", 0xa055fabc, 30), ("ap01_lunar_month_names", 0xa059be44, 13), ("ap01_solar_term_names", 0xa0638df0, 24)]:
            pointers = struct.unpack_from(f"<{count}I", rom, address - BASE)
            out.write(f"static const char *const {name}[{count}] = {{" + ",".join(rom_string(p) for p in pointers) + "};\n")
        out.write("static const struct { unsigned char month, day, flags; const char *text; } ap01_calendar_festivals[26] = {\n")
        for index in range(26):
            month, day, flags, _, pointer = struct.unpack_from("<4BI", rom, 0xa056d9f8 - BASE + index * 8)
            out.write(f"{{{month},{day},{flags},{rom_string(pointer)}}},\n")
        out.write("};\nstatic const int64_t ap01_solar_term_millis[200][24] = {\n")
        for index in range(200):
            year, *terms = struct.unpack_from("<25q", rom, 0xa0638e50 - BASE + index * 200)
            assert year == 1900 + index
            out.write("{" + ",".join(f"INT64_C({v})" for v in terms) + "},\n")
        out.write("};\n")
        fonts = write_native_fonts(out, rom)
    report = {"source_sha256": SHA256, "assets": records,
              "reconstruction_font": str(font), "font_glyphs": len(characters),
              "font_sha256": hashlib.sha256(font.read_bytes()).hexdigest(),
              "native_fonts": fonts,
              "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
    output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"source_sha256": SHA256, "assets":len(records), "fonts":len(fonts), "output_sha256":report["output_sha256"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    generate(args.rom, args.output)
