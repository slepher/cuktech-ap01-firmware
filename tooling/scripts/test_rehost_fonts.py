"""Check original 0041 glyph decoding against retained independent evidence."""
import hashlib
import importlib.util
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("assets", Path(__file__).with_name("rehost-assets.py"))
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)
rom = (Path(__file__).resolve().parents[2] / "roms/0041/ap01-1.0.2_0041.bin").read_bytes()
assert hashlib.sha256(rom).hexdigest() == assets.SHA256

height, baseline, glyphs, pixels = assets.native_font(rom, 0xa02549ac)
one = next(g for g in glyphs if g[0] == ord("1"))
assert (height, baseline, one[2:]) == (17, 3, (6, 6, 11, 0, 0))
glyph = pixels[one[1]:one[1] + one[3] * one[4]]
assert hashlib.sha256(glyph).hexdigest() == "17b469afee39a852f543daabb01cb514ad67e7f9ce8ab5ab93b9e1d5dd7d9649"
# The evidence PNG extraction retained nibbles, while the SIM uses A8 alpha.
assert hashlib.sha256(bytes(v // 17 for v in glyph)).hexdigest() == \
    "ddfe044e461dee383c63703d5b2281a4af65fd00fca78cad18bfeda7fff66c72"

height, baseline, glyphs, _ = assets.native_font(rom, 0xa025488c)
assert (height, baseline) == (20, 2)
points = {g[0] for g in glyphs}
assert all(ord(c) in points for c in "设置屏幕常亮屏幕保护屏幕亮度版本信息操作指南恢复出厂设置返回")
# Guide font has two cmaps, including FORMAT0_TINY, unlike the settings font.
height, baseline, glyphs, _ = assets.native_font(rom, 0xa02547fc)
assert (height, baseline, len(glyphs)) == (14, 2, 42)

for pointer, expected_height, expected_baseline, letters in [
    (0xa037253c, 12, 2, "日一二三四五六"),
    (0xa0254844, 16, 2, "周日一二三四五六"),
    (0xa0254a60, 17, 0, "0123456789"),
    (0xa055fb58, 18, 2, "年日月今天"),
    (0xa05647d8, 28, 0, "0123456789C°"),
    (0xa0630ad0, 26, 0, "-0123456789"),
    (0xa0254a18, 24, 5, "0123456789%"),
]:
    height, baseline, glyphs, _ = assets.native_font(rom, pointer)
    assert (height, baseline) == (expected_height, expected_baseline)
    assert set(map(ord, letters)) <= {g[0] for g in glyphs}

damaged = bytearray(rom)
struct.pack_into("<I", damaged, 0xa025488c - assets.BASE + 24, 1)
try:
    assets.native_font(damaged, 0xa025488c)
except ValueError:
    pass
else:
    raise AssertionError("out-of-ROM font descriptor was accepted")
print("0041 fonts: packed metrics, independent glyph hash, native CJK, two cmaps, pointer bounds PASS")
