#!/usr/bin/env python3
"""Exercise real X11 keyboard -> NuttX /dev/kbd -> LVGL encoder events."""
import hashlib
import json
import os
from pathlib import Path
import re
import select
import subprocess
import time

root = Path(os.environ.get("NUTTX_SIM_HOME", "/home/slepher/nuttx-ap01-sim"))
evidence = Path(__file__).resolve().parents[2] / "reverse/rehost"
assert evidence.is_dir(), "Pre-create the evidence directory with required permissions"
log_path = evidence / "round4-nuttx-sim-keyboard.log"
executable = root / "nuttx/nuttx"
verification_path = evidence / "round4-nuttx-sim-verification.json"
verification_path.write_text(json.dumps({"passed": False, "status": "running",
                                       "binary_sha256": hashlib.sha256(executable.read_bytes()).hexdigest()}) + "\n")
sim = None
xserver = subprocess.Popen(
    ["Xvfb", "-displayfd", "1", "-screen", "0", "640x480x24",
     "-nolisten", "unix", "-nolisten", "tcp"],
    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
)


def wait_for(check, description):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if check():
            return
        if sim is not None and sim.poll() is not None:
            raise AssertionError(f"SIM exited before {description}: {log_path.read_text()}")
        time.sleep(0.05)
    raise AssertionError(f"Timed out: {description}\n{log_path.read_text()}")


try:
    assert select.select([xserver.stdout], [], [], 10)[0], "Xvfb startup timed out"
    display = xserver.stdout.readline().decode().strip()
    assert display.isdecimal(), "Xvfb did not supply a display number"
    env = dict(os.environ, DISPLAY=f":{display}")
    with log_path.open("w") as log:
        sim = subprocess.Popen([str(executable)], cwd=executable.parent,
                               stdin=subprocess.DEVNULL, stdout=log,
                               stderr=subprocess.STDOUT, env=env)
        wait_for(lambda: "READY NuttX SIM display=320x240" in log_path.read_text(), "ready")
        window = subprocess.check_output(
            ["xdotool", "search", "--name", "^NuttX$"], env=env, text=True,
            timeout=5).strip().splitlines()
        assert len(window) == 1, window
        wid = window[0]
        geometry = subprocess.check_output(["xwininfo", "-id", wid], env=env,
                                           text=True, timeout=5)
        assert re.search(r"Width:\s+320\b", geometry), geometry
        assert re.search(r"Height:\s+240\b", geometry), geometry
        steps = []

        def key(key_name, expected):
            start = len(log_path.read_text())
            subprocess.run(["xdotool", "key", "--window", wid, key_name],
                           env=env, check=True, timeout=5, stderr=subprocess.PIPE)
            wait_for(lambda: expected in log_path.read_text()[start:], expected)
            time.sleep(0.03)
            assert log_path.read_text()[start:].count(expected) == 1, "Duplicate input action"
            steps.append({"key": key_name, "observed": expected})

        def state(page, mode="overview", selection=0):
            return f"STATE page={page} mode={mode} selection={selection}"

        def capture(name):
            time.sleep(0.35)
            path = evidence / f"round4-ui-{name}.png"
            result = subprocess.run(["import", "-window", wid, str(path)],
                                    env=env, timeout=5, capture_output=True)
            assert result.returncode == 0, (f"Screenshot {name} failed: "
                                            + result.stderr.decode(errors="replace"))
            return path

        key("f", "FIXTURE photo=1 local=1970-01-01T00:37:00")
        capture("power")
        for page in ("C1", "C2", "Time", "Date", "Weather", "Settings", "Pet", "Mijia", "Power"):
            key("Right", state(page))
        key("Left", state("Mijia"))
        capture("mijia")
        key("Return", "GUIDE page=0 option=1 source=mijia sim-only")
        key("Left", "GUIDE page=0 option=0")
        key("Return", state("Mijia"))
        key("Return", "GUIDE page=0 option=1 source=mijia sim-only")
        key("Return", "GUIDE page=1 option=1")
        key("Return", "GUIDE page=2 option=1")
        key("Return", state("Mijia"))
        key("Return", "GUIDE page=0 option=1 source=mijia sim-only")
        key("Escape", state("Mijia"))
        key("Left", state("Pet"))
        for page in ("Settings", "Weather", "Date", "Time", "C2", "C1", "Power"):
            key("Left", state(page))
        # Native Power list, mode choices, four port submenus, disconnected
        # capability gates and transport-unavailable outcomes.
        key("Return", state("Power", "detail"))
        key("Left", "CHARGE view=0 item=0 scroll=0")
        power_detail = capture("power-detail")
        mode_card_rgb = subprocess.check_output(
            ["convert", str(power_detail), "-crop", "280x60+20+18", "-depth", "8", "RGB:-"], timeout=5)
        mode_card_dark_pixels = sum(all(abs(mode_card_rgb[i+j] - target) <= 2
                                       for j, target in enumerate((0x22, 0x36, 0x3d)))
                                   for i in range(0, len(mode_card_rgb), 3))
        assert mode_card_dark_pixels > 5000, "Native mode mask was not recolored: white text would disappear"
        key("Return", "CHARGE view=1 item=0")
        key("Left", "CHARGE view=1 item=0")
        capture("power-modes")
        key("Right", "CHARGE view=1 item=1")
        key("Return", "CHARGE mode=1 sim-only; no device command")
        key("Right", "CHARGE view=1 item=2")
        key("Return", "CHARGE mode=2 sim-only; no device command")
        key("Right", "CHARGE view=1 item=3")
        key("Right", "CHARGE view=1 item=3")
        key("Return", "CHARGE view=0 item=0")
        for port, scroll in enumerate((0, 165, 165, 375), 1):
            key("Right", f"CHARGE view=0 item={port} scroll={scroll}")
            key("Return", "CHARGE view=2 item=0")
            capture(f"power-port-{port}")
            if port == 1:
                key("Right", "CHARGE view=2 item=1")
                key("Return", "CHARGE view=3 item=0")
                capture("port-switch")
                key("Return", "CHARGE action=port-switch result=unavailable stage=transport")
                key("Right", "CHARGE view=3 item=1")
                key("Return", "CHARGE action=port-switch result=unavailable stage=transport")
                key("Right", "CHARGE view=3 item=2")
                key("Return", "CHARGE view=2 item=1")
                key("Right", "CHARGE view=2 item=2")
                key("Return", "CHARGE view=2 item=2")  # capability not present
                key("Right", "CHARGE view=2 item=3")
                key("Return", "CHARGE view=2 item=3")  # capability not present
                key("Right", "CHARGE view=2 item=4")
            else:
                for index in range(1, 5):
                    key("Right", f"CHARGE view=2 item={index}")
            key("Return", f"CHARGE view=0 item={port}")
        key("Right", "CHARGE view=0 item=5 scroll=480")
        key("Right", "CHARGE view=0 item=5 scroll=480")
        capture("power-detail-back")
        for index, scroll in ((4, 270), (3, 270), (2, 165), (1, 0), (0, 0)):
            key("Left", f"CHARGE view=0 item={index} scroll={scroll}")
        for index, scroll in ((1, 0), (2, 165), (3, 165), (4, 375), (5, 480)):
            key("Right", f"CHARGE view=0 item={index} scroll={scroll}")
        key("Return", state("Power"))
        for page in ("C1", "C2"):
            key("Down", state(page))
            capture(page.lower())
            key("Return", f"INPUT port-press noop page={page}")
        key("Down", state("Time"))
        time_24 = capture("time")
        # Rendered native digits must reflect the frozen photo scene, rather
        # than merely logging a selected time format.
        def check_clock_pixels(path, digits):
            import importlib.util
            spec = importlib.util.spec_from_file_location("ap01_assets", Path(__file__).with_name("rehost-assets.py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            rom = (evidence.parent / "ap01-1.0.2_0041.bin").read_bytes()
            errors = []
            for x, digit in zip((20, 83, 181, 244), digits):
                png, width, height = module.png_at(rom, module.DIGITS[int(digit)])
                expected = subprocess.check_output(
                    ["convert", "png:-", "-background", "black", "-alpha", "remove", "-alpha", "off", "-depth", "8", "RGB:-"], input=png, timeout=5)
                actual = subprocess.check_output(
                    ["convert", str(path), "-crop", f"55x50+{x}+90", "-depth", "8", "RGB:-"], timeout=5)
                assert len(actual) == len(expected) == width * height * 3
                error = sum(abs(a-b) for a,b in zip(actual, expected)) / len(actual)
                assert error < 5, f"Clock digit {digit} pixels differ: {error}"
                errors.append(error)
            return errors
        clock_24_errors = check_clock_pixels(time_24, "0037")
        key("Return", state("Time", "detail"))
        capture("time-format-24h")
        key("Right", "TIME option=1")
        key("Return", "TIME format=12 sim-only")
        capture("time-format")
        key("Right", "TIME option=2")
        key("Return", state("Time"))
        time_12 = capture("time-12h")
        clock_12_errors = check_clock_pixels(time_12, "1237")
        key("Right", state("Date"))
        capture("date-12h")
        key("Return", state("Date", "detail"))
        capture("date-detail")
        key("Left", "DATE detail year=1970 month=1 day=1 focus=calendar week=-1")
        key("Left", "DATE detail year=1969 month=12 day=28 focus=calendar week=4")
        capture("date-detail-year-back")
        key("Right", "DATE detail year=1970 month=1 day=1 focus=calendar week=-1")
        key("Right", "DATE detail year=1970 month=1 day=1 focus=calendar week=0")
        for week, day in ((1, 4), (2, 11), (3, 18), (4, 25)):
            key("Right", f"DATE detail year=1970 month=1 day={day} focus=calendar week={week}")
        key("Right", "DATE detail year=1970 month=2 day=1 focus=calendar week=-1")
        key("Right", "DATE detail year=1970 month=2 day=1 focus=calendar week=0")
        capture("date-detail-month-forward")
        key("Return", state("Date"))
        key("Return", state("Date", "detail"))
        key("Escape", state("Date"))
        key("Right", state("Weather"))
        capture("weather-12h")
        key("Return", state("Weather", "detail"))
        capture("weather-detail-0")
        for index in (1, 2, 3, 4, 4):
            key("Right", f"WEATHER detail index={index} scroll_y={index*90}")
            capture(f"weather-detail-{index}")
        for index in (3, 2, 1, 0, 0):
            key("Left", f"WEATHER detail index={index} scroll_y={index*90}")
        key("Return", state("Weather"))
        key("Return", state("Weather", "detail"))
        key("Escape", state("Weather"))
        key("Right", state("Settings"))
        start = len(log_path.read_text())
        subprocess.run(["xdotool", "keydown", "--window", wid, "Return"],
                       env=env, check=True, timeout=5, stderr=subprocess.PIPE)
        time.sleep(0.8)
        subprocess.run(["xdotool", "keyup", "--window", wid, "Return"],
                       env=env, check=True, timeout=5, stderr=subprocess.PIPE)
        wait_for(lambda: "INPUT long-press unsupported" in log_path.read_text()[start:],
                 "long press")
        time.sleep(0.15)
        assert "mode=list" not in log_path.read_text()[start:], "Long release selected item"
        key("Return", state("Settings", "list"))
        key("Left", "INPUT settings-clamp direction=-1 selection=0")
        for i in range(1, 7):
            key("Right", state("Settings", "list", i))
        key("Right", "INPUT settings-clamp direction=1 selection=6")
        capture("settings-last")
        key("Return", state("Settings"))  # Actual seventh row is Back.
        key("Return", state("Settings", "list"))
        capture("settings-first")
        key("Return", state("Settings", "detail", 0))
        capture("always-on")
        key("Right", "DETAIL item=0 option=1 editing=0")
        key("Return", "SETTING sim item=0 enabled=0")
        key("Right", "DETAIL item=0 option=2 editing=0")
        key("Right", "DETAIL item=0 option=2 editing=0")
        key("Return", state("Settings", "list", 0))
        key("Right", state("Settings", "list", 1))
        key("Return", state("Settings", "detail", 1))
        key("Right", "DETAIL item=1 option=1 editing=0")
        key("Return", "SETTING sim item=1 enabled=0")
        key("Left", "DETAIL item=1 option=0 editing=0")
        key("Return", "SETTING sim item=1 enabled=1")
        capture("screen-saver")
        key("Right", "DETAIL item=1 option=1 editing=0")
        key("Right", "DETAIL item=1 option=2 editing=0")
        key("Return", state("Settings", "list", 1))
        key("Right", state("Settings", "list", 2))
        key("Return", state("Settings", "detail", 2))
        capture("brightness-idle")
        key("Return", "BRIGHTNESS editing=1 sim_raw=100")
        for value in range(90, -1, -10):
            key("Left", f"BRIGHTNESS sim_raw={value}")
        key("Left", "BRIGHTNESS sim_raw=0")
        capture("brightness-zero")
        key("Right", "BRIGHTNESS sim_raw=110")
        capture("brightness-110")
        key("Right", "BRIGHTNESS sim_raw=110")
        key("Left", "BRIGHTNESS sim_raw=100")
        capture("brightness-edit")
        key("Return", "BRIGHTNESS editing=0 sim_raw=100")
        key("Right", "DETAIL item=2 option=1 editing=0")
        key("Return", state("Settings", "list", 2))
        key("Right", state("Settings", "list", 3))
        key("Return", state("Settings", "detail", 3))
        capture("version")
        key("Return", state("Settings", "list", 3))
        key("Right", state("Settings", "list", 4))
        key("Return", "GUIDE page=0 option=1")
        capture("guide-turn")
        key("Return", "GUIDE page=1 option=1")
        guide_press = capture("guide-press")
        # A prior capture lost this button despite the logical state changing.
        # Check rendered pixels as well as the event log.
        button_mean = float(subprocess.check_output(
            ["convert", str(guide_press), "-crop", "82x36+224+192", "-format", "%[fx:mean]", "info:"],
            text=True, timeout=5))
        button_rgb = subprocess.check_output(
            ["convert", str(guide_press), "-crop", "82x36+224+192", "-depth", "8", "RGB:-"],
            timeout=5)
        focused_pixels = sum(all(abs(button_rgb[i+j] - target) <= 2
                                     for j, target in enumerate((0x22, 0x36, 0x3d)))
                             for i in range(0, len(button_rgb), 3))
        assert focused_pixels > 1000, "Guide page 2 focused Next button was not drawn"
        key("Return", "GUIDE page=2 option=1")
        capture("guide-practice-unavailable")
        key("Return", state("Settings", "list", 4))
        key("Return", "GUIDE page=0 option=1")
        key("Return", "GUIDE page=1 option=1")
        key("Left", "GUIDE page=1 option=0")
        key("Return", "GUIDE page=0 option=1")
        key("Left", "GUIDE page=0 option=0")
        key("Return", state("Settings", "list", 4))
        key("Right", state("Settings", "list", 5))
        key("Return", state("Settings", "detail", 5))
        capture("reset-cancel")
        key("Return", state("Settings", "list", 5))
        key("Return", state("Settings", "detail", 5))
        key("Right", "DETAIL item=5 option=1 editing=0")
        key("Return", "RESET sim-only defaults-restored")
        for i in range(4, -1, -1):
            key("Left", state("Settings", "list", i))
        key("Escape", state("Settings"))
        for page in ("Weather", "Date", "Time"):
            key("Left", state(page))
        reset_clock = capture("time-after-reset")
        check_clock_pixels(reset_clock, "0037")
        key("Return", state("Time", "detail"))
        capture("time-format-after-reset")
        key("Escape", state("Time"))
        key("Right", state("Date"))
        capture("date")
        key("Right", state("Weather"))
        capture("weather")
        key("Right", state("Settings"))
        key("Right", state("Pet"))
        pet_a = capture("pet-a")
        time.sleep(0.5)
        pet_b = capture("pet-b")
        assert pet_a.read_bytes() != pet_b.read_bytes(), "Original GIF did not animate"
        pet_images = [hashlib.sha256(pet_a.read_bytes()).hexdigest()]
        for index in range(1, 5):
            key("Return", f"PET index={index}")
            first = capture(f"pet-{index}")
            time.sleep(0.5)
            second = capture(f"pet-{index}-b")
            assert first.read_bytes() != second.read_bytes(), f"Pet {index} did not animate"
            pet_images.append(hashlib.sha256(first.read_bytes()).hexdigest())
        assert len(set(pet_images)) == 5, "Pet resources were duplicated"
        key("Return", "PET index=0")
        key("Left", state("Settings"))
        key("space", state("Settings", "list"))
        key("Escape", state("Settings"))
        key("f", "FIXTURE photo=0 local=host-RTC")
        subprocess.run(["xdotool", "key", "--window", wid, "q"],
                       env=env, check=True, timeout=5, stderr=subprocess.PIPE)
        assert sim.wait(timeout=5) == 0, "Keyboard exit failed"
        text = log_path.read_text()
        assert "CHARGE reset mode=0 sim-only" in text
        assert "TIME format=24 sim-only reset" in text
        assert "STOP keyboard-exit" in text
        assert "ERROR stage=" not in text and "Assertion failed" not in text
        assert "[Warn]" not in text, text
        report = {"passed": True, "display": [320, 240], "input": "real X11 events",
                  "steps": steps, "quit_exit": 0, "gif_animated": True, "source_baseline": "AP01 0041",
                  "photo_scene": "1970-01-01T00:37:00 offline",
                  "clock_24_digit_pixel_errors": clock_24_errors,
                  "clock_12_digit_pixel_errors": clock_12_errors,
                  "brightness_native_raw_range": [0, 110], "native_settings_rows": True,
                  "toggle_confirm_stays_in_detail": True, "guide_two_pages": True,
                  "guide_next_button_pixel_mean": button_mean,
                  "guide_focused_button_pixels": focused_pixels,
                  "reset_restores_24h": True, "reset_clock_pixels_verified": True,
                  "fixture_toggle_returns_to_host_RTC": True, "five_distinct_animated_pets": True,
                  "practice_stage_explicitly_unavailable": True,
                  "time_format_menu": True, "pet_five_cycle": True, "details_return": True, "power_six_rows_and_modes": True,
                  "mode_card_dark_pixels": mode_card_dark_pixels,
                  "four_power_port_submenus": True, "offline_port_switch_unavailable": True,
                  "c1_c2_native_noop_press": True, "date_week_month_year_browse": True,
                  "weather_five_scroll_positions": True, "mijia_static_qr_and_guidance": True,
                  "settings_clamp": [0, 6], "long_release_no_short_press": True,
                  "binary_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
                  "binary_bytes": executable.stat().st_size}
        verification_path.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({k: v for k, v in report.items() if k != "steps"}, indent=2))
        print(f"Keyboard steps passed: {len(steps)}")
finally:
    for process in (sim, xserver):
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
