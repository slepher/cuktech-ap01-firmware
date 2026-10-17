/* SPDX-License-Identifier: Apache-2.0 */
/* AP01 application reconstruction on the upstream NuttX SIM board. */
#include <nuttx/config.h>
#include <errno.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/boardctl.h>
#include <nuttx/input/keyboard.h>
#include <lvgl/lvgl.h>

static int g_keyboard;
static bool g_running = true;
static bool g_pressed;
#include "ap01-ui.h"

static void read_encoder(lv_indev_t *indev, lv_indev_data_t *data)
{
  struct keyboard_event_s event;
  ssize_t n = read(g_keyboard, &event, sizeof(event));
  (void)indev;
  data->enc_diff = 0;
  data->key = LV_KEY_ENTER;
  if (n == sizeof(event))
    {
      data->continue_reading = true;
      if (event.code == XK_Return || event.code == XK_space)
        {
          g_pressed = event.type == KEYBOARD_PRESS;
          printf("INPUT button=%s\n", g_pressed ? "down" : "up");
        }
      else if (event.type == KEYBOARD_PRESS)
        {
          switch (event.code)
            {
              case XK_Left:
              case XK_Up:
                data->enc_diff = -1;
                break;
              case XK_Right:
              case XK_Down:
                data->enc_diff = 1;
                break;
              case XK_Escape:
                ap01_ui_back();
                break;
              case XK_f:
                ap01_ui_toggle_fixture();
                break;
              case XK_r:
                if (!ap01_ui_activity() && !ap01_ui_system_active() &&
                    !g_ap01_ui_guide_active && ap01_ui_weather_retry()) ap01_ui_redraw();
                break;
              case XK_q:
                g_running = false;
                break;
            }
          if (data->enc_diff != 0)
            {
              printf("INPUT rotate=%d\n", data->enc_diff);
            }
        }
    }
  else if (n != -1 || (errno != EAGAIN && errno != EINTR))
    {
      fprintf(stderr, "ERROR stage=keyboard-read errno=%d action=restart-sim\n",
              errno);
      g_running = false;
    }
  data->state = g_pressed ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}

int main(int argc, char *argv[])
{
  lv_nuttx_dsc_t info;
  lv_nuttx_result_t result;
  (void)argc;
  (void)argv;
  setvbuf(stdout, NULL, _IOLBF, 0);
  if (boardctl(BOARDIOC_INIT, 0) < 0)
    {
      fprintf(stderr, "ERROR stage=board-init errno=%d\n", errno);
      return 1;
    }
  lv_init();
  lv_nuttx_dsc_init(&info);
  lv_nuttx_init(&info, &result);
  if (result.disp == NULL)
    {
      fprintf(stderr, "ERROR stage=display-init action=check-DISPLAY\n");
      lv_deinit();
      return 1;
    }
  g_keyboard = open("/dev/kbd", O_RDONLY | O_NONBLOCK);
  if (g_keyboard < 0)
    {
      fprintf(stderr, "ERROR stage=keyboard-open errno=%d\n", errno);
      lv_nuttx_deinit(&result);
      lv_deinit();
      return 1;
    }
  lv_group_t *group = lv_group_create();
  lv_indev_t *encoder = lv_indev_create();
  lv_indev_set_type(encoder, LV_INDEV_TYPE_ENCODER);
  lv_indev_set_long_press_time(encoder, 3000);
  lv_indev_set_read_cb(encoder, read_encoder);
  lv_indev_set_group(encoder, group);
  ap01_ui_create(group);
  printf("READY NuttX SIM display=%ldx%ld input=/dev/kbd encoder\n",
         (long)lv_display_get_horizontal_resolution(result.disp),
         (long)lv_display_get_vertical_resolution(result.disp));
  while (g_running)
    {
      uint32_t delay = lv_timer_handler();
      usleep((delay > 10 ? 10 : (delay ? delay : 1)) * 1000);
    }
  close(g_keyboard);
  lv_indev_delete(encoder);
  lv_group_delete(group);
  lv_nuttx_deinit(&result);
  lv_deinit();
  printf("STOP keyboard-exit\n");
  boardctl(BOARDIOC_POWEROFF, 0);
  return 0;
}
