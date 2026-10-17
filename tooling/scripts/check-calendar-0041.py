#!/usr/bin/env python3
"""Validate the bounded 0041 ROM lunar/solar-term reconstruction offline.

Run from any directory; no dependencies, generated directories, or network.
This checks ROM data and the recovered algorithm, not LVGL rendering.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[2]
ROM = ROOT / "artifacts/ap01-research/ap01-1.0.2_0041.bin"
EXPECTED = "972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9"
BASE = 0x9FFFF000


def validate():
    rom = ROM.read_bytes()
    source_hash = hashlib.sha256(rom).hexdigest()
    assert source_hash == EXPECTED, "This validator requires the matching 0041 ROM"
    bits = struct.unpack_from("<225I", rom, 0xA059BAC0 - BASE)
    starts = struct.unpack_from("<225I", rom, 0xA066B6A0 - BASE)

    def day_number(year, month, day):
        month = (month + 9) % 12
        year -= month // 10
        return (365 * year + year // 4 - year // 100 + year // 400
                + (month * 306 + 5) // 10 + day - 1)

    def lunar(date):
        if not 1888 <= date.year <= 2111:
            return None
        index = date.year - 1887
        packed = date.year << 9 | date.month << 5 | date.day
        if packed < starts[index]:
            index -= 1
        if index < 1:
            return None
        start = starts[index]
        offset = (day_number(date.year, date.month, date.day)
                  - day_number(start >> 9, start >> 5 & 15, start & 31) + 1)
        leap_month = bits[index] >> 13 & 15
        for slot in range(1, 14):
            length = 30 if bits[index] & (0x2000 >> slot) else 29
            if offset <= length:
                return dict(year=index + 1887,
                            month=slot - int(bool(leap_month and slot > leap_month)),
                            day=offset, leap=bool(leap_month and slot == leap_month + 1),
                            days=length)
            offset -= length
        raise AssertionError(f"Unconsumed lunar offset for {date}")

    anchors = {
        "1888-02-11": None,
        "1888-02-12": (1888, 1, 1, False),
        "1970-01-01": (1969, 11, 24, False),
        "2023-03-22": (2023, 2, 1, True),
        "2024-02-09": (2023, 12, 30, False),
        "2024-02-10": (2024, 1, 1, False),
        "2024-09-17": (2024, 8, 15, False),
        "2025-01-29": (2025, 1, 1, False),
        "2026-10-16": (2026, 9, 7, False),
        "2111-12-31": (2111, 12, 1, False),
        "2112-01-01": None,
    }
    results = {}
    for text, expected in anchors.items():
        value = lunar(dt.date.fromisoformat(text))
        actual = tuple(value[k] for k in ("year", "month", "day", "leap")) if value else None
        assert actual == expected, (text, actual, expected)
        results[text] = value

    date, end, count = dt.date(1888, 2, 12), dt.date(2112, 1, 1), 0
    while date < end:
        value = lunar(date)
        assert value and 1 <= value["month"] <= 12 and 1 <= value["day"] <= value["days"], date
        assert day_number(date.year, date.month, date.day) - day_number(1970, 1, 1) == (date - dt.date(1970, 1, 1)).days
        count += 1
        date += dt.timedelta(days=1)
    assert count == 81772

    def rom_text(pointer):
        start = pointer - BASE
        return rom[start:rom.index(b"\0", start)].decode("utf-8")

    days = [rom_text(p) for p in struct.unpack_from("<30I", rom, 0xA055FABC - BASE)]
    months = [rom_text(p) for p in struct.unpack_from("<13I", rom, 0xA059BE44 - BASE)]
    terms = [rom_text(p) for p in struct.unpack_from("<24I", rom, 0xA0638DF0 - BASE)]
    festivals = [struct.unpack_from("<BBBxI", rom, 0xA056D9F8 - BASE + i * 8) for i in range(26)]

    def subtitle(date):
        value = lunar(date)
        if value is None:
            return ""
        text = months[value["month"]] if value["day"] == 1 else days[value["day"] - 1]
        for month, day, flags, pointer in festivals:
            if flags & 3 == 0 and (month, day) == (date.month, date.day):
                text = rom_text(pointer)
                break
        if 1900 <= date.year <= 2099:
            values = struct.unpack_from("<25q", rom, 0xA0638E50 - BASE + (date.year - 1900) * 200)
            for index, millis in enumerate(values[1:]):
                seconds = abs(millis) // 1000 * (-1 if millis < 0 else 1)
                term_date = (dt.datetime(1970, 1, 1) + dt.timedelta(seconds=seconds & 0xFFFFFFFF)).date()
                if term_date == date:
                    text = terms[index]
                    break
        for month, day, flags, pointer in festivals:
            if flags & 3 == 1 and month == value["month"] and (day == value["day"] or day == 0 and value["day"] == value["days"]):
                text = rom_text(pointer)
                break
        return text

    label_anchors = {"1970-01-01": "元旦", "2024-02-09": "除夕",
                     "2024-02-10": "春节", "2024-09-17": "中秋节",
                     "2025-01-29": "春节", "2026-04-04": "清明"}
    for text, expected in label_anchors.items():
        assert subtitle(dt.date.fromisoformat(text)) == expected, text
    assert subtitle(dt.date(2024, 5, 12)) != "母亲节", "Native flags2 records are unused"

    # Native a01aceb6 divides signed epoch milliseconds, then passes only
    # the low32 seconds to its unsigned time_t localtime path (default UTC0).
    # Verify the wrap is observable rather than silently using host64 time_t.
    term_cases = []
    for year in (1900, 1969, 1970, 2026, 2099):
        values = struct.unpack_from("<25q", rom, 0xA0638E50 - BASE + (year - 1900) * 200)
        assert values[0] == year
        for index in (0, 6, 23):
            millis = values[index + 1]
            seconds = abs(millis) // 1000 * (-1 if millis < 0 else 1)
            original = dt.datetime(1970, 1, 1) + dt.timedelta(seconds=seconds)
            wrapped = dt.datetime(1970, 1, 1) + dt.timedelta(seconds=seconds & 0xFFFFFFFF)
            assert (wrapped == original) == (0 <= seconds <= 0xFFFFFFFF)
            term_cases.append(dict(year=year, index=index, millis=millis,
                                   utc=original.isoformat(), native_utc=wrapped.isoformat(),
                                   same_year=wrapped.year == year))
    assert all(not x["same_year"] for x in term_cases if x["year"] < 1970)
    assert all(x["same_year"] for x in term_cases if x["year"] in (1970, 2026, 2099))
    return dict(status="passed", rom_sha256=source_hash,
                source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (Path(__file__), ROOT / "tools/ap01/ap01-ui-details.h",
                                         ROOT / "tools/ap01/ap01-ui-pages.h")},
                supported_days=count, anchors=results, subtitle_anchors=label_anchors,
                unused_week_festivals_verified=True, solar_term_checks=term_cases,
                scope="Recovered algorithm/ROM tables only; rendering and interaction require parent SIM tests")


if __name__ == "__main__":
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
