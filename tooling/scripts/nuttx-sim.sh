#!/usr/bin/env bash
set -euo pipefail
root=${NUTTX_SIM_HOME:-/home/slepher/nuttx-ap01-sim}
source_dir=$(cd -- "$(dirname -- "$0")" && pwd)

is_running()
{
  [[ -f "$root/sim.pid" ]] || return 1
  local pid
  pid=$(cat "$root/sim.pid")
  [[ $pid =~ ^[1-9][0-9]*$ ]] || return 1
  [[ $(readlink -f "/proc/$pid/exe") == "$root/nuttx/nuttx" ]]
}

case ${1:-status} in
  build)
    if is_running; then
      echo 'ERROR stage=build action=stop-sim-before-building' >&2
      exit 1
    fi
    cd "$root/nuttx"
    test "$(git rev-parse HEAD)" = 6fc5b3e9dc51dcda46d99519f72b7f2ec6db2e64
    test "$(git -C ../apps rev-parse HEAD)" = 8ff533beb37eeef1f288c467acd7c50b542464eb
    python3 "$source_dir/rehost-assets.py" \
      "${AP01_ROM:-$source_dir/../../roms/0041/ap01-1.0.2_0041.bin}" \
      ../apps/examples/lvgldemo/ap01-assets.h
    cp "$source_dir/nuttx-sim.c" ../apps/examples/lvgldemo/lvgldemo.c
    cp "$source_dir/ap01-ui.h" ../apps/examples/lvgldemo/ap01-ui.h
    cp "$source_dir/ap01-ui-pages.h" ../apps/examples/lvgldemo/ap01-ui-pages.h
    cp "$source_dir/ap01-ui-settings.h" ../apps/examples/lvgldemo/ap01-ui-settings.h
    cp "$source_dir/ap01-ui-charge.h" ../apps/examples/lvgldemo/ap01-ui-charge.h
    cp "$source_dir/ap01-ui-details.h" ../apps/examples/lvgldemo/ap01-ui-details.h
    cp "$source_dir/ap01-ui-guide.h" "$source_dir/ap01-ui-system.h" "$source_dir/ap01-sim-wifi.h" "$source_dir/ap01-sim-service.h" "$source_dir/ap01-sim-service-impl.h" "$source_dir/ap01-sim-control.h" ../apps/examples/lvgldemo/
    python3 - <<'PY'
from pathlib import Path
p = Path('arch/sim/src/sim/posix/sim_x11eventloop.c')
text = p.read_text()
# X11 autorepeat emits synthetic release/press pairs. Keep the encoder
# button held across those pairs so LVGL can measure a physical long press.
old = ('          case KeyRelease:\n'
       '            sim_kbdevent(XLookupKeysym(&event.xkey, 0), false);')
new = ('          case KeyRelease:\n'
       '            if ((XLookupKeysym(&event.xkey, 0) == XK_Return ||\n'
       '                 XLookupKeysym(&event.xkey, 0) == XK_space) &&\n'
       '                XPending(g_display) > 0)\n'
       '              {\n'
       '                XEvent next;\n'
       '                XPeekEvent(g_display, &next);\n'
       '                if (next.type == KeyPress &&\n'
       '                    next.xkey.keycode == event.xkey.keycode &&\n'
       '                    next.xkey.time == event.xkey.time)\n'
       '                  {\n'
       '                    XNextEvent(g_display, &next);\n'
       '                    break;\n'
       '                  }\n'
       '              }\n'
       '            sim_kbdevent(XLookupKeysym(&event.xkey, 0), false);')
if old in text:
    assert text.count(old) == 1
    p.write_text(text.replace(old, new))
elif new not in text:
    raise ValueError('Unexpected NuttX X11 keyboard adapter; inspect before patching')
p = Path('../apps/graphics/lvgl/lvgl/src/libs/gif/gifdec.c')
text = p.read_text()
# A token that exactly fills the remaining pixels is valid. The upstream
# 9.2.1 guard rejects it and also leaks its table on the error path.
old = ('if(frm_off + str_len >= frm_size){\n'
       '\t\tLV_LOG_WARN("LZW table token overflows the frame buffer");\n'
       '\t\treturn -1;\n\t}')
new = ('if(frm_off + str_len > frm_size) {\n'
       '            LV_LOG_WARN("LZW table token overflows the frame buffer");\n'
       '            lv_free(table);\n            return -1;\n        }')
if old in text:
    assert text.count(old) == 1
    p.write_text(text.replace(old, new))
elif new not in text:
    raise ValueError('Unexpected LVGL GIF decoder version; inspect before patching')
PY
    if [[ ! -f .config ]]; then
      ./tools/configure.sh sim:lvgl_fb
    fi
    python3 - <<'PY'
import re
from pathlib import Path
p = Path('.config')
text = p.read_text()
settings = {
    'SIM_FBWIDTH': '320', 'SIM_FBHEIGHT': '240',
    # NuttX 12.10 gates X11 event polling on a mouse input driver.
    # Keep that driver enabled; the UI itself reads only /dev/kbd.
    'SIM_X11NOSHM': 'y', 'SIM_KEYBOARD': 'y', 'SIM_NOINPUT': 'n',
    'SIM_TOUCHSCREEN': 'y', 'LV_USE_NUTTX_TOUCHSCREEN': 'n',
    'LV_USE_DEMO_WIDGETS': 'n', 'INIT_ARGS': '""',
    'INIT_STACKSIZE': '65536', 'BOARDCTL_POWEROFF': 'y',
    'DISABLE_MOUNTPOINT': 'n', 'FS_HOSTFS': 'y', 'SIM_HOSTFS': 'y',
    'RTC': 'y', 'RTC_DRIVER': 'y', 'RTC_ARCH': 'y',
    'RTC_DATETIME': 'y', 'LV_FONT_SIMSUN_16_CJK': 'n',
    'LV_FONT_MONTSERRAT_48': 'y', 'LV_USE_GIF': 'y', 'LV_USE_ARC': 'y',
}
for key, value in settings.items():
    text = re.sub(rf'^(?:# )?CONFIG_{key}(?:=.*| is not set)\n', '', text, flags=re.M)
    text += f'CONFIG_{key}={value}\n'
p.write_text(text)
PY
    make olddefconfig
    # This apps release emits no LVGL header dependencies. Recompile the
    # library when its configuration changes, retaining all other caches.
    lvgl_config_hash=$(grep '^CONFIG_LV_' .config | sha256sum)
    if [[ ! -f "$root/lvgl-config.sha" ]] ||
       [[ $(cat "$root/lvgl-config.sha") != "$lvgl_config_hash" ]]; then
      find ../apps/graphics/lvgl/lvgl/src -name '*.c' -exec touch {} +
    fi
    make -j4 > "$root/build.log" 2>&1 || { tail -80 "$root/build.log"; exit 1; }
    echo "$lvgl_config_hash" > "$root/lvgl-config.sha"
    sha256sum nuttx
    stat -c 'SIM executable bytes=%s' nuttx
    ;;
  run)
    if is_running; then
      echo "SIM already running PID=$(cat "$root/sim.pid")"
      exit 0
    fi
    cd "$root/nuttx"
    test -x nuttx
    setsid ./nuttx </dev/null > "$root/run.log" 2>&1 &
    echo $! > "$root/sim.pid"
    for ((i=0; i<100; ++i)); do
      if grep -q '^READY ' "$root/run.log"; then
        echo "SIM running PID=$(cat "$root/sim.pid") DISPLAY=${DISPLAY:-unset}"
        exit 0
      fi
      if ! kill -0 "$(cat "$root/sim.pid")" 2>/dev/null; then
        cat "$root/run.log"
        exit 1
      fi
      sleep .1
    done
    cat "$root/run.log"
    echo 'ERROR stage=startup action=inspect-run.log' >&2
    exit 1
    ;;
  stop)
    if is_running; then
      kill "$(cat "$root/sim.pid")"
      for ((i=0; i<50; ++i)); do
        is_running || break
        sleep .1
      done
      if is_running; then
        echo 'ERROR stage=stop action=inspect-sim-process' >&2
        exit 1
      fi
    fi
    rm -f "$root/sim.pid"
    ;;
  status)
    if is_running; then
      echo "SIM PID=$(cat "$root/sim.pid") exe=$(readlink -f "/proc/$(cat "$root/sim.pid")/exe")"
    else
      echo 'SIM stopped'
    fi
    tail -15 "$root/run.log" 2>/dev/null || true
    ;;
  *) echo 'Usage: nuttx-sim.sh build|run|stop|status' >&2; exit 2 ;;
esac
