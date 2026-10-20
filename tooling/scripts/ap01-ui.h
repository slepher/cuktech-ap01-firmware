/* SPDX-License-Identifier: Apache-2.0 */
/*
 * AP01 application rehost for the NuttX/LVGL SIM.
 *
 * This is deliberately a small, source-level reconstruction.  It keeps one
 * focused LVGL object alive and changes its contents as the reconstructed
 * page state changes. Native UI actions use the bounded local service model;
 * this SIM performs no physical device, network, or flash operation.
 */
#ifndef TOOLS_AP01_AP01_UI_H
#define TOOLS_AP01_AP01_UI_H

#include <lvgl/lvgl.h>
#include "ap01-assets.h"

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <string.h>
#include "ap01-sim-service.h"

enum ap01_ui_page_e
{
  AP01_UI_POWER = 0,
  AP01_UI_C1,
  AP01_UI_C2,
  AP01_UI_TIME,
  AP01_UI_DATE,
  AP01_UI_WEATHER,
  AP01_UI_SETTINGS,
  AP01_UI_PET,
  AP01_UI_MIJIA,
  AP01_UI_PAGE_COUNT
};

enum ap01_ui_mode_e
{
  AP01_UI_MODE_OVERVIEW = 0,
  AP01_UI_MODE_LIST,
  AP01_UI_MODE_DETAIL
};

#define AP01_UI_SETTINGS_COUNT 8
#define AP01_UI_PORT_COUNT 2

static lv_obj_t *g_ap01_ui_root;
static lv_obj_t *g_ap01_ui_brightness_shade;
static lv_obj_t *g_ap01_ui_date;
static lv_obj_t *g_ap01_ui_clock_image[5];
static enum ap01_ui_page_e g_ap01_ui_page = AP01_UI_POWER;
static enum ap01_ui_mode_e g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW;
static unsigned int g_ap01_ui_selection;
static unsigned int g_ap01_ui_brightness = 10;
static unsigned int g_ap01_ui_option;
#define g_ap01_ui_setting_enabled (g_ap01_sim.settings.enabled)
static bool g_ap01_ui_brightness_edit;
static unsigned int g_ap01_ui_guide_page;
#define g_ap01_ui_pet_index (g_ap01_sim.settings.pet)
#define g_ap01_ui_12_hour (g_ap01_sim.settings.hour12)
#define g_ap01_ui_offline (!g_ap01_sim.wifi_connected)
static bool g_ap01_ui_clock_mock;
static time_t g_ap01_ui_clock_epoch;
static bool g_ap01_ui_civil_mock;
static struct tm g_ap01_ui_civil_time;
static bool g_ap01_ui_photo_fixture;
static bool g_ap01_ui_redraw_pending;
static lv_obj_t *g_ap01_ui_settings_clock;
static void ap01_ui_pages_tick(void);
static void ap01_ui_pages_reset(void);
static void ap01_ui_charge_tick(void);
static void ap01_ui_details_tick(void);
static void ap01_ui_redraw(void);
static void ap01_ui_service_feedback(void);
static void ap01_ui_simulated_restart(void);

static const char *ap01_ui_page_name(enum ap01_ui_page_e page)
{
  static const char *const names[AP01_UI_PAGE_COUNT] =
    {
      "Power", "C1", "C2", "Time", "Date", "Weather", "Settings",
      "Pet", "Mijia"
    };
  return page < AP01_UI_PAGE_COUNT ? names[page] : "Unknown";
}

static const char *ap01_ui_mode_name(enum ap01_ui_mode_e mode)
{
  static const char *const names[] = {"overview", "list", "detail"};
  return mode <= AP01_UI_MODE_DETAIL ? names[mode] : "unknown";
}

static const char *ap01_ui_setting_name(unsigned int selection)
{
  /* Original 0041 order, with the SIM Wi-Fi row inserted after screensaver. */
  static const char *const names[AP01_UI_SETTINGS_COUNT] =
    {
      "屏幕常亮", "屏幕保护", "Wi-Fi", "屏幕亮度", "版本信息", "操作指南",
      "恢复出厂设置", "返回"
    };
  return selection < AP01_UI_SETTINGS_COUNT ? names[selection] : "未知设置";
}

static lv_opa_t ap01_ui_brightness_opa(void)
{
  /* Keep controls visible at native raw 0; this is only a SIM display effect. */
  unsigned int level = g_ap01_ui_brightness > 10 ? 10 : g_ap01_ui_brightness;
  return (lv_opa_t)(32U + level * 223U / 10U);
}

static void ap01_ui_apply_brightness(void)
{
  if (g_ap01_ui_root != NULL)
    {
      /* Root opacity would also make its black clear transparent, leaving
       * prior-page pixels in partially refreshed framebuffer regions. */
      lv_obj_set_style_opa(g_ap01_ui_root, LV_OPA_COVER, LV_PART_MAIN);
      if (g_ap01_ui_brightness_shade != NULL)
        lv_obj_set_style_bg_opa(g_ap01_ui_brightness_shade,
          LV_OPA_COVER - ap01_ui_brightness_opa(), LV_PART_MAIN);
    }
}

static void ap01_ui_log_state(void)
{
  printf("STATE page=%s mode=%s selection=%u\n",
         ap01_ui_page_name(g_ap01_ui_page),
         ap01_ui_mode_name(g_ap01_ui_mode), g_ap01_ui_selection);
}

static lv_obj_t *ap01_ui_label(lv_obj_t *parent, const char *text, int32_t x,
                               int32_t y, lv_color_t color,
                               const lv_font_t *font)
{
  lv_obj_t *label = lv_label_create(parent);
  lv_label_set_text(label, text);
  lv_obj_set_pos(label, x, y);
  lv_obj_set_style_text_color(label, color, LV_PART_MAIN);
  lv_obj_set_style_text_font(label, font, LV_PART_MAIN);
  return label;
}

/* F toggles a deterministic offline scene for comparison with the supplied
 * hardware photos. Normal operation continues to use the host RTC. */
static bool ap01_ui_now(struct tm *local_time)
{
  if (g_ap01_ui_civil_mock) { *local_time = g_ap01_ui_civil_time; return true; }
  /* All calendar, lunar and weather day/night views share this local clock.
   * Host mode is explicitly UTC+8 (Hong Kong); mock epoch is an already
   * localized UTC-shaped fixture, avoiding a second timezone adjustment. */
  time_t now = g_ap01_ui_clock_mock ? g_ap01_ui_clock_epoch :
    g_ap01_ui_photo_fixture ? (time_t)(37 * 60) :
    time(NULL) + (time_t)(8 * 60 * 60);
  return gmtime_r(&now, local_time) != NULL;
}

static void ap01_ui_set_clock_text(void)
{
  struct tm local_time;
  char clock_text[24];
  char date_text[24];
  const bool show_date = g_ap01_ui_page == AP01_UI_DATE;
  bool have_time = true;

  if (!ap01_ui_now(&local_time))
    {
      have_time = false;
      snprintf(clock_text, sizeof(clock_text), "--:--:--");
      snprintf(date_text, sizeof(date_text), "----/--/--");
    }
  else
    {
      strftime(clock_text, sizeof(clock_text), g_ap01_ui_12_hour ? "%I:%M:%S" : "%H:%M:%S", &local_time);
      strftime(date_text, sizeof(date_text), "%Y/%m/%d", &local_time);
    }

  if (have_time && g_ap01_ui_clock_image[0] != NULL && !show_date)
    {
      unsigned int i;
      static const unsigned int positions[] = {0, 1, 3, 4};
      for (i = 0; i < 4; ++i)
        {
          unsigned int digit =
            (unsigned int)(clock_text[positions[i]] - '0');
          lv_image_set_src(g_ap01_ui_clock_image[i], &ap01_digits[digit]);
        }
    }
  if (g_ap01_ui_settings_clock != NULL)
    {
      clock_text[5] = '\0';
      lv_label_set_text(g_ap01_ui_settings_clock, clock_text);
    }
  if (g_ap01_ui_date != NULL)
    {
      lv_label_set_text(g_ap01_ui_date, date_text);
    }
}

#include "ap01-ui-charge.h"

#include "ap01-ui-pages.h"

#include "ap01-ui-details.h"

#include "ap01-ui-system.h"
#include "ap01-ui-guide.h"
#include "ap01-ui-settings.h"
#include "ap01-sim-control.h"

/* Native a00afc88 overview order differs from the enumeration: Pet precedes
 * Settings. a009d7b4 reads ck_config/wifi_configured (not live Wi-Fi). */
static bool ap01_ui_page_visible(enum ap01_ui_page_e page)
{
  if (page == AP01_UI_POWER) return g_ap01_sim.charger_connected;
  if (page == AP01_UI_C1 || page == AP01_UI_C2)
    return g_ap01_sim.banks[page - AP01_UI_C1].connected;
  if (page == AP01_UI_MIJIA) return !g_ap01_sim.wifi_configured;
  return true;
}

static enum ap01_ui_page_e ap01_ui_first_page(void)
{
  /* a00a7472 ->a00b2ea6 always selects Mijia8 before revealing an
   * unconfigured boot; configured boots keep the Power/Time initial choice. */
  if (!g_ap01_sim.wifi_configured) return AP01_UI_MIJIA;
  return g_ap01_sim.charger_connected ? AP01_UI_POWER : AP01_UI_TIME;
}

static void ap01_ui_service_feedback(void)
{
  /* Called only after a rejected local transaction. Drawing happens after the
   * input/service dispatch returns, so a service never deletes active widgets. */
  ap01_ui_system_show_error();
}

static bool ap01_ui_settings_commit(const ap01_sim_settings_t *candidate)
{
  if (ap01_sim_apply_settings(candidate)) return true;
  ap01_ui_service_feedback();
  return false;
}

static void ap01_ui_guide_return(void)
{
  if (g_ap01_ui_guide_mijia)
    {
      g_ap01_ui_page = ap01_ui_first_page();
      g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW;
      g_ap01_ui_selection = 0;
    }
  else
    {
      g_ap01_ui_page = AP01_UI_SETTINGS;
      g_ap01_ui_mode = AP01_UI_MODE_LIST;
      g_ap01_ui_selection = 5;
    }
}

static void ap01_ui_redraw(void)
{
  if (g_ap01_ui_root == NULL) return;
  g_ap01_ui_redraw_pending = false;
  g_ap01_ui_settings_clock = NULL;
  g_ap01_ui_brightness_shade = NULL;
  g_ap01_ui_date = NULL;
  for (unsigned int i = 0; i < 5; ++i) g_ap01_ui_clock_image[i] = NULL;
  ap01_ui_pages_reset();
  ap01_ui_charge_reset();
  ap01_ui_details_reset();
  ap01_ui_guide_reset();
  ap01_ui_system_reset();
  lv_obj_clean(g_ap01_ui_root);
  ap01_ui_apply_brightness();
  if (ap01_ui_boot_active()) ap01_ui_boot_draw();
  else if (ap01_ui_saver_active()) ap01_ui_saver_draw();
  else if (g_ap01_ui_guide_active) ap01_ui_guide_draw();
  else if (g_ap01_ui_mode == AP01_UI_MODE_DETAIL && g_ap01_ui_page == AP01_UI_POWER)
    ap01_ui_charge_draw_detail();
  else if (g_ap01_ui_mode == AP01_UI_MODE_DETAIL &&
           (g_ap01_ui_page == AP01_UI_DATE || g_ap01_ui_page == AP01_UI_WEATHER))
    ap01_ui_details_draw();
  else if (g_ap01_ui_page == AP01_UI_TIME && g_ap01_ui_mode == AP01_UI_MODE_DETAIL)
    ap01_ui_draw_time_options();
  else if (g_ap01_ui_page == AP01_UI_MIJIA) ap01_ui_system_mijia_draw();
  else if (g_ap01_ui_page == AP01_UI_SETTINGS)
    {
      if (g_ap01_ui_mode == AP01_UI_MODE_DETAIL) ap01_ui_draw_settings_detail();
      else ap01_ui_draw_settings();
    }
  else ap01_ui_draw_overview();
  if (!ap01_ui_boot_active() && !ap01_ui_saver_active() && !g_ap01_ui_guide_active)
    ap01_ui_charge_draw_popup();
  if (!ap01_ui_boot_active()) ap01_ui_system_draw();
  /* Explicit SIM backlight presentation: shade fully rendered pixels rather
   * than making the native canvas and its erase pass translucent. */
  g_ap01_ui_brightness_shade = lv_obj_create(g_ap01_ui_root);
  lv_obj_set_pos(g_ap01_ui_brightness_shade, 0, 0);
  lv_obj_set_size(g_ap01_ui_brightness_shade, 320, 240);
  lv_obj_remove_flag(g_ap01_ui_brightness_shade, LV_OBJ_FLAG_CLICKABLE | LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_style_radius(g_ap01_ui_brightness_shade, 0, 0);
  lv_obj_set_style_border_width(g_ap01_ui_brightness_shade, 0, 0);
  lv_obj_set_style_bg_color(g_ap01_ui_brightness_shade, lv_color_hex(0x000000), 0);
  ap01_ui_apply_brightness();
  ap01_ui_set_clock_text();
  ap01_ui_log_state();
  lv_obj_invalidate(g_ap01_ui_root);
}

static void ap01_ui_simulated_restart(void)
{
  /* Pure UI restart. The initiating service owns committing firmware/reset. */
  g_ap01_ui_page = ap01_ui_first_page();
  g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW;
  g_ap01_ui_selection = g_ap01_ui_option = 0;
  g_ap01_ui_brightness = g_ap01_sim.settings.brightness;
  g_ap01_ui_brightness_edit = false;
  g_ap01_ui_guide_active = false;
  g_ap01_ui_saver_kind = 0;
  g_ap01_ui_system_view = AP01_SYSTEM_NONE;
  g_ap01_ui_system_seen = false;
  g_ap01_ui_system_recovery_seen = false;
  g_ap01_ui_charge_popup = AP01_CHARGE_POPUP_NONE;
  ap01_ui_saver_activity();
  ap01_ui_boot_open();
  ap01_ui_redraw();
}

static bool ap01_ui_mock_date(unsigned int value)
{
  unsigned int year = value / 10000, month = value / 100 % 100, day = value % 100;
  static const unsigned int days[] = {31,28,31,30,31,30,31,31,30,31,30,31};
  static const unsigned int offsets[] = {0,3,2,5,0,3,5,1,4,6,2,4};
  if (year < 1 || year > 9999 || month < 1 || month > 12) return false;
  bool leap = year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
  unsigned int maximum = days[month - 1] + (month == 2 && leap);
  if (day < 1 || day > maximum) return false;
  memset(&g_ap01_ui_civil_time, 0, sizeof(g_ap01_ui_civil_time));
  g_ap01_ui_civil_time.tm_year = (int)year - 1900;
  g_ap01_ui_civil_time.tm_mon = month - 1;
  g_ap01_ui_civil_time.tm_mday = day;
  g_ap01_ui_civil_time.tm_min = 37;
  unsigned int adjusted = year - (month < 3);
  g_ap01_ui_civil_time.tm_wday = (adjusted + adjusted / 4 - adjusted / 100 +
    adjusted / 400 + offsets[month - 1] + day) % 7;
  unsigned int yday = day - 1;
  for (unsigned int i = 1; i < month; ++i) yday += days[i - 1] + (i == 2 && leap);
  g_ap01_ui_civil_time.tm_yday = yday;
  g_ap01_ui_civil_mock = true;
  return true;
}

static bool ap01_ui_sim_control_ui(const char *operation, unsigned value)
{
  bool handled = false;
  if (!strcmp(operation, "saver")) handled = ap01_ui_saver_force(value);
  else if (!strcmp(operation, "offer")) handled = ap01_ui_system_update_offer(value);
  else if (!strcmp(operation, "restart"))
    { ap01_ui_simulated_restart(); handled = true; }
  else if (!strcmp(operation, "date")) handled = ap01_ui_mock_date(value);
  else if (!strcmp(operation, "clock"))
    { g_ap01_ui_civil_mock = false; g_ap01_ui_clock_mock = true;
      g_ap01_ui_clock_epoch = (time_t)value; handled = true; }
  else if (!strcmp(operation, "fixture"))
    { g_ap01_ui_photo_fixture = value != 0; handled = true; }
  if (handled) ap01_ui_redraw();
  return handled;
}

static void ap01_ui_tick(lv_timer_t *timer)
{
  (void)timer;
  ap01_sim_control_poll();
  ap01_sim_tick();
  if (!g_ap01_ui_brightness_edit && g_ap01_ui_brightness != g_ap01_sim.settings.brightness)
    {
      g_ap01_ui_brightness = g_ap01_sim.settings.brightness;
      ap01_ui_apply_brightness();
    }
  ap01_ui_set_clock_text();
  ap01_ui_pages_tick();
  ap01_ui_charge_tick();
  ap01_ui_details_tick();
  ap01_ui_system_tick();
  ap01_ui_guide_tick();
  bool redraw = ap01_ui_boot_tick();
  redraw |= ap01_ui_saver_tick();
  bool charge = ap01_ui_charge_needs_redraw();
  bool details = ap01_ui_details_needs_redraw();
  bool system = ap01_ui_system_needs_redraw();
  if (!ap01_ui_boot_active() && !ap01_ui_saver_active() && !g_ap01_ui_guide_active)
    {
      if (!ap01_ui_system_active() && !ap01_ui_page_visible(g_ap01_ui_page))
        {
          g_ap01_ui_page = ap01_ui_first_page();
          g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW;
          redraw = true;
        }
      redraw |= system || details || (charge &&
        (g_ap01_ui_page <= AP01_UI_C2 || ap01_ui_charge_popup_active()));
    }
  else if (ap01_ui_system_active()) redraw |= system;
  if (redraw) g_ap01_ui_redraw_pending = true;
  /* Keep the encoder's press/release transaction on its original objects.
   * Clock/progress updates above are safe; full replacement waits for release. */
  if (g_ap01_ui_redraw_pending &&
      !lv_obj_has_state(g_ap01_ui_root, LV_STATE_PRESSED)) ap01_ui_redraw();
  /* Also publish navigation and direct-object progress, even when revision
   * does not change. This is bounded HOSTFS output, never a network service. */
  ap01_sim_status_publish();
}

static bool ap01_ui_activity(void)
{
  if (ap01_ui_boot_skip()) return true;
  if (ap01_ui_saver_activity()) { ap01_ui_redraw(); return true; }
  return false;
}

static void ap01_ui_turn(int direction)
{
  if (ap01_ui_activity() || direction == 0) return;
  if (ap01_ui_system_active()) ap01_ui_system_turn(direction);
  else if (ap01_ui_charge_popup_active()) return;
  else if (g_ap01_ui_guide_active) ap01_ui_guide_turn(direction);
  else if (g_ap01_ui_mode == AP01_UI_MODE_DETAIL && g_ap01_ui_page == AP01_UI_POWER)
    ap01_ui_charge_turn(direction);
  else if (g_ap01_ui_mode == AP01_UI_MODE_DETAIL &&
           (g_ap01_ui_page == AP01_UI_DATE || g_ap01_ui_page == AP01_UI_WEATHER))
    ap01_ui_details_turn(direction);
  else if (g_ap01_ui_mode == AP01_UI_MODE_DETAIL && g_ap01_ui_page == AP01_UI_TIME)
    {
      if (direction > 0 && g_ap01_ui_option < 2) ++g_ap01_ui_option;
      if (direction < 0 && g_ap01_ui_option > 0) --g_ap01_ui_option;
    }
  else if (g_ap01_ui_page == AP01_UI_SETTINGS && g_ap01_ui_mode == AP01_UI_MODE_DETAIL)
    {
      if (g_ap01_ui_selection == 2)
        {
          unsigned limit = ap01_ui_wifi_count();
          if (g_ap01_ui_option > limit) g_ap01_ui_option = limit;
          if (direction > 0 && g_ap01_ui_option < limit) ++g_ap01_ui_option;
          if (direction < 0 && g_ap01_ui_option > 0) --g_ap01_ui_option;
        }
      else if (g_ap01_ui_selection == 4) ap01_ui_system_version_turn(direction);
      else if (g_ap01_ui_selection == 3 && g_ap01_ui_brightness_edit)
        {
          /* Native callback a00fd1ac: raw0..110 in steps10; right0->110. */
          if (direction > 0) g_ap01_ui_brightness = g_ap01_ui_brightness >= 1 &&
            g_ap01_ui_brightness <= 9 ? g_ap01_ui_brightness + 1 : 11;
          else g_ap01_ui_brightness = g_ap01_ui_brightness < 2 ? 0 : g_ap01_ui_brightness - 1;
        }
      else
        {
          unsigned limit = g_ap01_ui_selection < 2 ? 2 : 1;
          if (direction > 0 && g_ap01_ui_option < limit) ++g_ap01_ui_option;
          if (direction < 0 && g_ap01_ui_option > 0) --g_ap01_ui_option;
        }
    }
  else if (g_ap01_ui_page == AP01_UI_SETTINGS && g_ap01_ui_mode == AP01_UI_MODE_LIST)
    {
      if (direction < 0 && g_ap01_ui_selection > 0) --g_ap01_ui_selection;
      if (direction > 0 && g_ap01_ui_selection + 1 < AP01_UI_SETTINGS_COUNT) ++g_ap01_ui_selection;
    }
  else if (g_ap01_ui_mode == AP01_UI_MODE_OVERVIEW)
    {
      /* a00afc88 blocks both encoder directions on Mijia while the native
       * initial-setup flag62fc909d is set; shortpress enters onboarding. */
      if (g_ap01_ui_page == AP01_UI_MIJIA && !g_ap01_sim.settings.guide_completed)
        return;
      bool c1 = g_ap01_sim.banks[0].connected;
      bool c2 = g_ap01_sim.banks[1].connected;
      bool wifi = g_ap01_sim.wifi_configured;
      bool charger = g_ap01_sim.charger_connected;
      /* These are directed native edges, not a globally filtered ring.
       * Time->Date->Weather remains reachable without configured Wi-Fi. */
      if (direction > 0)
        {
          switch (g_ap01_ui_page)
            {
              case AP01_UI_POWER: g_ap01_ui_page = c1 ? AP01_UI_C1 : c2 ? AP01_UI_C2 : wifi ? AP01_UI_TIME : AP01_UI_PET; break;
              case AP01_UI_C1: g_ap01_ui_page = c2 ? AP01_UI_C2 : wifi ? AP01_UI_TIME : AP01_UI_PET; break;
              case AP01_UI_C2: g_ap01_ui_page = wifi ? AP01_UI_TIME : AP01_UI_PET; break;
              case AP01_UI_TIME: g_ap01_ui_page = AP01_UI_DATE; break;
              case AP01_UI_DATE: g_ap01_ui_page = AP01_UI_WEATHER; break;
              case AP01_UI_WEATHER: g_ap01_ui_page = AP01_UI_PET; break;
              case AP01_UI_PET: g_ap01_ui_page = AP01_UI_SETTINGS; break;
              case AP01_UI_SETTINGS: g_ap01_ui_page = !wifi ? AP01_UI_MIJIA : charger ? AP01_UI_POWER : AP01_UI_TIME; break;
              case AP01_UI_MIJIA: g_ap01_ui_page = charger ? AP01_UI_POWER : wifi ? AP01_UI_TIME : AP01_UI_PET; break;
              default: break;
            }
        }
      else
        {
          switch (g_ap01_ui_page)
            {
              case AP01_UI_POWER: g_ap01_ui_page = wifi ? AP01_UI_SETTINGS : AP01_UI_MIJIA; break;
              case AP01_UI_C1: g_ap01_ui_page = charger ? AP01_UI_POWER : AP01_UI_SETTINGS; break;
              case AP01_UI_C2: g_ap01_ui_page = c1 ? AP01_UI_C1 : charger ? AP01_UI_POWER : AP01_UI_SETTINGS; break;
              case AP01_UI_TIME: g_ap01_ui_page = c2 ? AP01_UI_C2 : c1 ? AP01_UI_C1 : charger ? AP01_UI_POWER : AP01_UI_SETTINGS; break;
              case AP01_UI_DATE: g_ap01_ui_page = AP01_UI_TIME; break;
              case AP01_UI_WEATHER: g_ap01_ui_page = AP01_UI_DATE; break;
              case AP01_UI_PET: g_ap01_ui_page = wifi ? AP01_UI_WEATHER : charger ? AP01_UI_POWER : AP01_UI_MIJIA; break;
              case AP01_UI_SETTINGS: g_ap01_ui_page = AP01_UI_PET; break;
              case AP01_UI_MIJIA: g_ap01_ui_page = AP01_UI_SETTINGS; break;
              default: break;
            }
        }
      g_ap01_ui_selection = 0;
    }
  ap01_ui_redraw();
}

static void ap01_ui_press(void)
{
  if (ap01_ui_activity()) return;
  if (ap01_ui_system_active())
    {
      if (!ap01_ui_system_press()) ap01_ui_guide_open(true);
    }
  else if (ap01_ui_charge_popup_active()) ap01_ui_charge_popup_press();
  else if (g_ap01_ui_guide_active)
    { if (ap01_ui_guide_press()) ap01_ui_guide_return(); }
  else if (g_ap01_ui_page == AP01_UI_POWER || g_ap01_ui_page == AP01_UI_DATE ||
           g_ap01_ui_page == AP01_UI_WEATHER)
    {
      bool power = g_ap01_ui_page == AP01_UI_POWER;
      if (g_ap01_ui_mode == AP01_UI_MODE_OVERVIEW)
        {
          if (power) ap01_ui_charge_open(); else ap01_ui_details_open(g_ap01_ui_page);
          g_ap01_ui_mode = AP01_UI_MODE_DETAIL;
        }
      else if (power ? ap01_ui_charge_press() : ap01_ui_details_press())
        g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW;
    }
  else if (g_ap01_ui_page == AP01_UI_C1 || g_ap01_ui_page == AP01_UI_C2)
    { printf("INPUT port-press native-noop page=%s\n", ap01_ui_page_name(g_ap01_ui_page)); return; }
  else if (g_ap01_ui_page == AP01_UI_MIJIA)
    { if (!ap01_ui_system_mijia_press()) ap01_ui_guide_open(true); }
  else if (g_ap01_ui_page == AP01_UI_PET)
    {
      ap01_sim_settings_t candidate = g_ap01_sim.settings;
      candidate.pet = (candidate.pet + 1) % 5;
      ap01_ui_settings_commit(&candidate);
    }
  else if (g_ap01_ui_page == AP01_UI_TIME)
    {
      if (g_ap01_ui_mode == AP01_UI_MODE_OVERVIEW)
        { g_ap01_ui_mode = AP01_UI_MODE_DETAIL; g_ap01_ui_option = 0; }
      else if (g_ap01_ui_option == 2) g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW;
      else
        {
          ap01_sim_settings_t candidate = g_ap01_sim.settings;
          candidate.hour12 = g_ap01_ui_option == 1;
          ap01_ui_settings_commit(&candidate);
        }
    }
  else if (g_ap01_ui_page == AP01_UI_SETTINGS)
    {
      if (g_ap01_ui_mode == AP01_UI_MODE_OVERVIEW)
        { g_ap01_ui_mode = AP01_UI_MODE_LIST; g_ap01_ui_selection = 0; }
      else if (g_ap01_ui_mode == AP01_UI_MODE_LIST)
        {
          if (g_ap01_ui_selection == 7)
            { g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW; g_ap01_ui_selection = 0; }
          else
            {
              g_ap01_ui_mode = AP01_UI_MODE_DETAIL;
              g_ap01_ui_option = g_ap01_ui_selection == 6 ? 1 : 0;
              g_ap01_ui_brightness_edit = false;
              g_ap01_ui_brightness = g_ap01_sim.settings.brightness;
              if (g_ap01_ui_selection == 4) ap01_ui_system_version_open();
              if (g_ap01_ui_selection == 5) ap01_ui_guide_open(false);
            }
        }
      else
        {
          bool back = false;
          if (g_ap01_ui_selection < 2)
            {
              back = g_ap01_ui_option == 2;
              if (!back)
                {
                  ap01_sim_settings_t candidate = g_ap01_sim.settings;
                  candidate.enabled[g_ap01_ui_selection] = g_ap01_ui_option == 0;
                  ap01_ui_settings_commit(&candidate);
                }
            }
          else if (g_ap01_ui_selection == 2)
            {
              unsigned slot = ap01_ui_wifi_slot(g_ap01_ui_option);
              back = slot == AP01_WIFI_SLOTS;
              if (!back && !ap01_wifi_select(slot)) ap01_ui_service_feedback();
            }
          else if (g_ap01_ui_selection == 3)
            {
              back = !g_ap01_ui_brightness_edit && g_ap01_ui_option == 1;
              if (!back && !g_ap01_ui_brightness_edit) g_ap01_ui_brightness_edit = true;
              else if (!back)
                {
                  ap01_sim_settings_t candidate = g_ap01_sim.settings;
                  candidate.brightness = g_ap01_ui_brightness;
                  if (ap01_ui_settings_commit(&candidate)) g_ap01_ui_brightness_edit = false;
                }
            }
          else if (g_ap01_ui_selection == 4) back = ap01_ui_system_version_press();
          else if (g_ap01_ui_selection == 6)
            {
              if (g_ap01_ui_option == 0) back = true;
              else if (!ap01_sim_factory_reset()) ap01_ui_service_feedback();
              else
                {
                  g_ap01_ui_brightness = g_ap01_sim.settings.brightness;
                  ap01_ui_system_reset_success();
                }
            }
          if (back) { g_ap01_ui_mode = AP01_UI_MODE_LIST; g_ap01_ui_brightness_edit = false; }
        }
    }
  ap01_ui_redraw();
}

static void ap01_ui_toggle_fixture(void)
{
  g_ap01_ui_photo_fixture = !g_ap01_ui_photo_fixture;
  ap01_ui_redraw();
}

static void ap01_ui_back(void)
{
  if (ap01_ui_activity()) return;
  if (ap01_ui_system_active()) ap01_ui_system_back();
  else if (ap01_ui_charge_popup_active()) ap01_ui_charge_popup_back();
  else if (g_ap01_ui_guide_active)
    { if (ap01_ui_guide_back()) ap01_ui_guide_return(); }
  else if (g_ap01_ui_mode == AP01_UI_MODE_DETAIL && g_ap01_ui_page == AP01_UI_POWER &&
           ap01_ui_charge_back()) { /* nested charge page popped */ }
  else if (g_ap01_ui_mode == AP01_UI_MODE_DETAIL)
    {
      g_ap01_ui_mode = g_ap01_ui_page == AP01_UI_SETTINGS ? AP01_UI_MODE_LIST : AP01_UI_MODE_OVERVIEW;
      g_ap01_ui_brightness_edit = false;
      g_ap01_ui_brightness = g_ap01_sim.settings.brightness;
    }
  else if (g_ap01_ui_mode == AP01_UI_MODE_LIST)
    { g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW; g_ap01_ui_selection = 0; }
  ap01_ui_redraw();
}

static void ap01_ui_long_press(void)
{
  if (ap01_ui_activity() || g_ap01_ui_guide_active) return;
  /* Native a00f1de4/a00b2dde checks62fc403b: OTA transfer/success blocks
   * the three-second home action until normal shortpress completes it. */
  if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK ||
      g_ap01_ui_system_view == AP01_SYSTEM_RESET) return;
  if (ap01_ui_system_active())
    {
      ap01_ui_system_back();
      if (ap01_ui_system_active()) { ap01_ui_redraw(); return; }
    }
  if (g_ap01_ui_charge_view == AP01_CHARGE_PROTOCOL &&
      ap01_ui_charge_current_port()->protocol_status == AP01_SIM_PENDING &&
      !ap01_sim_protocol_cancel()) { ap01_ui_service_feedback(); ap01_ui_redraw(); return; }
  if (ap01_ui_charge_popup_active()) ap01_ui_charge_popup_back();
  /* a00b2d6a selects Power0, else Time3 if configured, else Settings6;
   * a00a7728 removes temporary windows, a00a8004 restores main focus. */
  g_ap01_ui_page = g_ap01_sim.charger_connected ? AP01_UI_POWER :
    g_ap01_sim.wifi_configured ? AP01_UI_TIME : AP01_UI_SETTINGS;
  g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW;
  g_ap01_ui_selection = 0;
  g_ap01_ui_brightness_edit = false;
  g_ap01_ui_brightness = g_ap01_sim.settings.brightness;
  printf("INPUT long-press native-home page=%s threshold_ms=3000\n",
         ap01_ui_page_name(g_ap01_ui_page));
  ap01_ui_redraw();
}

static void ap01_ui_event(lv_event_t *event)
{
  lv_event_code_t code = lv_event_get_code(event);
  if (code == LV_EVENT_KEY)
    {
      uint32_t key = lv_event_get_key(event);
      if (key == LV_KEY_LEFT) ap01_ui_turn(-1);
      else if (key == LV_KEY_RIGHT) ap01_ui_turn(1);
      else if (key == 'r' || key == 'R')
        {
          if (!ap01_ui_activity() && !ap01_ui_system_active() &&
              !g_ap01_ui_guide_active && ap01_ui_weather_retry()) ap01_ui_redraw();
        }
    }
  else if (code == LV_EVENT_SHORT_CLICKED) ap01_ui_press();
  else if (code == LV_EVENT_LONG_PRESSED) ap01_ui_long_press();
}

static void ap01_ui_create(lv_group_t *group)
{
  lv_obj_t *screen = lv_screen_active();
  lv_obj_set_style_bg_color(screen, lv_color_hex(0x000000), 0);
  lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);

  g_ap01_ui_root = lv_obj_create(screen);
  lv_obj_set_size(g_ap01_ui_root, lv_obj_get_width(screen),
                  lv_obj_get_height(screen));
  lv_obj_set_pos(g_ap01_ui_root, 0, 0);
  lv_obj_remove_flag(g_ap01_ui_root, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_add_flag(g_ap01_ui_root, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_set_style_radius(g_ap01_ui_root, 0, LV_PART_MAIN);
  lv_obj_set_style_border_width(g_ap01_ui_root, 0, LV_PART_MAIN);
  lv_obj_set_style_outline_width(g_ap01_ui_root, 0, LV_STATE_FOCUSED);
  lv_obj_set_style_pad_all(g_ap01_ui_root, 0, LV_PART_MAIN);
  lv_obj_set_style_bg_color(g_ap01_ui_root, lv_color_hex(0x000000), LV_PART_MAIN);
  lv_obj_set_style_bg_opa(g_ap01_ui_root, LV_OPA_COVER, LV_PART_MAIN);
  ap01_ui_apply_brightness();
  lv_obj_add_event_cb(g_ap01_ui_root, ap01_ui_event, LV_EVENT_ALL, NULL);

  lv_group_add_obj(group, g_ap01_ui_root);
  lv_group_focus_obj(g_ap01_ui_root);
  lv_group_set_editing(group, true);
  ap01_sim_init();
  ap01_sim_control_init();
  g_ap01_ui_brightness = g_ap01_sim.settings.brightness;
  g_ap01_ui_page = ap01_ui_first_page();
  g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW;
  g_ap01_ui_selection = 0;
  ap01_ui_saver_activity();
  ap01_ui_boot_open();
  ap01_ui_redraw();
  lv_timer_create(ap01_ui_tick, 100, NULL);
  ap01_sim_status_publish();
}

#endif /* TOOLS_AP01_AP01_UI_H */
