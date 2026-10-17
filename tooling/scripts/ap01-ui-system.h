/* SPDX-License-Identifier: Apache-2.0 */
/* Native 0041 binding/version/OTA family with controlled local services.
 * Evidence: system-complete-0041.json. Include after ap01_ui_label/now and
 * service declarations. This module performs no device/network operation. */
#ifndef TOOLS_AP01_AP01_UI_SYSTEM_H
#define TOOLS_AP01_AP01_UI_SYSTEM_H

enum ap01_ui_system_view_e
{
  AP01_SYSTEM_NONE, AP01_SYSTEM_BINDING, AP01_SYSTEM_CHECK,
  AP01_SYSTEM_OFFER, AP01_SYSTEM_PROGRESS, AP01_SYSTEM_SUCCESS,
  AP01_SYSTEM_FAILURE, AP01_SYSTEM_ERROR, AP01_SYSTEM_RESET, AP01_SYSTEM_RECOVERY
};

static enum ap01_ui_system_view_e g_ap01_ui_system_view;
static enum ap01_ui_system_view_e g_ap01_ui_system_resume;
static unsigned int g_ap01_ui_system_choice = 1;
static unsigned int g_ap01_ui_system_version_choice;
static unsigned int g_ap01_ui_system_target;
static bool g_ap01_ui_system_from_settings;
static unsigned int g_ap01_ui_system_seen_revision;
static bool g_ap01_ui_system_changed;
static bool g_ap01_ui_system_seen;
static bool g_ap01_ui_system_recovery_seen;
static bool g_ap01_ui_system_recovery_connected;
static enum ap01_sim_status_e g_ap01_ui_system_binding;
static enum ap01_sim_status_e g_ap01_ui_system_ota;
static enum ap01_sim_status_e g_ap01_ui_system_check;
static ap01_sim_reply_t g_ap01_ui_system_reply;
static uint32_t g_ap01_ui_system_reset_start;
static lv_obj_t *g_ap01_ui_system_clock;
static lv_obj_t *g_ap01_ui_system_progress;
static lv_obj_t *g_ap01_ui_system_progress_text;
static void ap01_ui_simulated_restart(void);

static lv_obj_t *ap01_ui_system_panel(lv_obj_t *parent, int x, int y,
                                     int w, int h, int radius, uint32_t color)
{
  lv_obj_t *panel = lv_obj_create(parent);
  lv_obj_set_pos(panel, x, y);
  lv_obj_set_size(panel, w, h);
  lv_obj_set_style_pad_all(panel, 0, 0);
  lv_obj_set_style_border_width(panel, 0, 0);
  lv_obj_set_style_radius(panel, radius, 0);
  lv_obj_set_style_bg_color(panel, lv_color_hex(color), 0);
  lv_obj_set_style_bg_opa(panel, LV_OPA_COVER, 0);
  lv_obj_remove_flag(panel, LV_OBJ_FLAG_SCROLLABLE);
  return panel;
}

static lv_obj_t *ap01_ui_system_text(lv_obj_t *parent, const char *text,
                                    int x, int y, int width, uint32_t color,
                                    const lv_font_t *font, bool centered)
{
  lv_obj_t *label = ap01_ui_label(parent, text, x, y, lv_color_hex(color), font);
  if (width > 0) lv_obj_set_width(label, width);
  if (centered) lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, 0);
  return label;
}

static lv_obj_t *ap01_ui_system_image(lv_obj_t *parent,
                                     const lv_image_dsc_t *src, int x, int y)
{
  lv_obj_t *image = lv_image_create(parent);
  lv_image_set_src(image, src);
  lv_obj_set_pos(image, x, y);
  return image;
}

static void ap01_ui_system_badge(lv_obj_t *parent)
{
  (void)parent; /* Host window and logs identify the simulation. */
}

static void ap01_ui_system_reset(void)
{
  g_ap01_ui_system_clock = NULL;
  g_ap01_ui_system_progress = NULL;
  g_ap01_ui_system_progress_text = NULL;
}

static bool ap01_ui_system_active(void)
{
  return g_ap01_ui_system_view != AP01_SYSTEM_NONE;
}

static bool ap01_ui_system_needs_redraw(void)
{
  bool changed = g_ap01_ui_system_changed;
  g_ap01_ui_system_changed = false;
  return changed;
}

static void ap01_ui_system_close(void)
{
  g_ap01_ui_system_view = AP01_SYSTEM_NONE;
  g_ap01_ui_system_changed = true;
}

static void ap01_ui_system_show_error(void)
{
  if (g_ap01_ui_system_view != AP01_SYSTEM_ERROR)
    g_ap01_ui_system_resume = g_ap01_ui_system_view;
  g_ap01_ui_system_reply = g_ap01_sim.reply;
  g_ap01_ui_system_view = AP01_SYSTEM_ERROR;
  g_ap01_ui_system_choice = 0;
  g_ap01_ui_system_changed = true;
}

static bool ap01_ui_system_update_offer(unsigned int target)
{
  if (target > 1) return false;
  if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK)
    return ap01_sim_reply("update-offer", AP01_SIM_ERROR, "busy",
      g_ap01_sim.ota == AP01_SIM_PENDING ? "update-in-progress" : "restart-required");
  bool recovery = target == 1 && g_ap01_sim.device_recovery_required;
  if (!recovery && !(target ? g_ap01_sim.device_update_available :
                              g_ap01_sim.update_available)) return false;
  g_ap01_ui_system_target = target;
  g_ap01_ui_system_from_settings = false;
  g_ap01_sim.ota_target = target;
  g_ap01_ui_system_view = recovery ? AP01_SYSTEM_RECOVERY : AP01_SYSTEM_OFFER;
  g_ap01_ui_system_choice = 1;
  g_ap01_ui_system_changed = true;
  return true;
}

static bool ap01_ui_system_check_update(unsigned int target)
{
  if (!ap01_sim_update_check(target))
    {
      ap01_ui_system_show_error();
      return false;
    }
  g_ap01_ui_system_target = target;
  g_ap01_ui_system_check = g_ap01_sim.update_check;
  g_ap01_ui_system_view = AP01_SYSTEM_CHECK;
  g_ap01_ui_system_choice = 1;
  g_ap01_ui_system_changed = true;
  return true;
}

static bool ap01_ui_system_start_update(void)
{
  g_ap01_sim.ota_target = g_ap01_ui_system_target;
  if (!ap01_sim_ota_start(g_ap01_sim.ota_crc_valid, g_ap01_sim.ota_signed))
    {
      ap01_ui_system_show_error();
      return false;
    }
  g_ap01_ui_system_ota = g_ap01_sim.ota;
  g_ap01_ui_system_view = AP01_SYSTEM_PROGRESS;
  g_ap01_ui_system_changed = true;
  return true;
}

static void ap01_ui_system_reset_success(void)
{
  g_ap01_ui_system_view = AP01_SYSTEM_RESET;
  g_ap01_ui_system_reset_start = lv_tick_get();
  g_ap01_ui_system_changed = true;
}

static void ap01_ui_system_tick(void)
{
  if (g_ap01_ui_system_view == AP01_SYSTEM_RECOVERY && (!g_ap01_sim.charger_connected || !g_ap01_sim.device_recovery_required))
    ap01_ui_system_close();
  if (g_ap01_ui_system_view == AP01_SYSTEM_RESET &&
      lv_tick_elaps(g_ap01_ui_system_reset_start) >= 1000)
    {
      ap01_ui_system_close();
      ap01_ui_simulated_restart();
      return;
    }
  bool recovery_event = g_ap01_sim.device_recovery_required &&
    g_ap01_sim.charger_connected &&
    (!g_ap01_ui_system_recovery_seen || !g_ap01_ui_system_recovery_connected);
  if (recovery_event)
    {
      /* Deferral is observational: do not emit a busy error every100ms. */
      if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK)
        g_ap01_ui_system_recovery_seen = false;
      else g_ap01_ui_system_recovery_seen = ap01_ui_system_update_offer(1);
    }
  else if (!g_ap01_sim.device_recovery_required) g_ap01_ui_system_recovery_seen = false;
  if (g_ap01_ui_system_view == AP01_SYSTEM_RECOVERY && !g_ap01_sim.charger_connected)
    ap01_ui_system_close();
  g_ap01_ui_system_recovery_connected = g_ap01_sim.charger_connected;
  struct tm now;
  char text[24];
  if (g_ap01_ui_system_clock != NULL && ap01_ui_now(&now))
    {
      strftime(text, sizeof(text), g_ap01_sim.settings.hour12 ? "%I:%M" : "%H:%M", &now);
      lv_label_set_text(g_ap01_ui_system_clock, text);
    }
  if (g_ap01_ui_system_progress != NULL)
    lv_bar_set_value(g_ap01_ui_system_progress, g_ap01_sim.ota_progress, LV_ANIM_OFF);
  if (g_ap01_ui_system_progress_text != NULL)
    {
      snprintf(text, sizeof(text), "%u%%", g_ap01_sim.ota_progress);
      lv_label_set_text(g_ap01_ui_system_progress_text, text);
    }
  if (g_ap01_ui_system_seen_revision != g_ap01_sim.revision)
    {
      g_ap01_ui_system_seen_revision = g_ap01_sim.revision;
      if (!ap01_ui_system_active() &&
          (g_ap01_ui_page == AP01_UI_MIJIA ||
           (g_ap01_ui_page == AP01_UI_SETTINGS && g_ap01_ui_selection == 3)))
        g_ap01_ui_system_changed = true;
    }
  if ((!g_ap01_ui_system_seen && g_ap01_sim.binding == AP01_SIM_PENDING) ||
      (g_ap01_ui_system_seen && g_ap01_ui_system_binding != g_ap01_sim.binding))
    {
      g_ap01_ui_system_binding = g_ap01_sim.binding;
      if (g_ap01_sim.ota != AP01_SIM_PENDING && g_ap01_sim.ota != AP01_SIM_OK)
        {
          if (g_ap01_sim.binding == AP01_SIM_OK && g_ap01_sim.bound)
            {
              /* Native total-info callback retires Mijia after successful bind. */
              if (g_ap01_ui_system_view == AP01_SYSTEM_BINDING) ap01_ui_system_close();
              if (g_ap01_ui_page == AP01_UI_MIJIA)
                {
                  g_ap01_ui_page = AP01_UI_POWER;
                  g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW;
                }
            }
          else if (g_ap01_sim.binding != AP01_SIM_IDLE)
            {
              g_ap01_ui_system_view = AP01_SYSTEM_BINDING;
              g_ap01_ui_system_reply = g_ap01_sim.reply;
            }
          g_ap01_ui_system_changed = true;
        }
    }
  if ((!g_ap01_ui_system_seen && g_ap01_sim.update_check == AP01_SIM_PENDING) ||
      (g_ap01_ui_system_seen && g_ap01_ui_system_check != g_ap01_sim.update_check))
    {
      g_ap01_ui_system_check = g_ap01_sim.update_check;
      if (g_ap01_sim.ota != AP01_SIM_PENDING && g_ap01_sim.ota != AP01_SIM_OK)
        {
          g_ap01_ui_system_target = g_ap01_sim.update_target;
          if (g_ap01_sim.update_check == AP01_SIM_OK)
            {
              if (!ap01_ui_system_update_offer(g_ap01_sim.update_target))
                ap01_ui_system_close();
            }
          else if (g_ap01_sim.update_check != AP01_SIM_IDLE)
            {
              g_ap01_ui_system_view = AP01_SYSTEM_CHECK;
              g_ap01_ui_system_reply = g_ap01_sim.reply;
              g_ap01_ui_system_choice = 1;
            }
          g_ap01_ui_system_changed = true;
        }
    }
  if ((!g_ap01_ui_system_seen && g_ap01_sim.ota == AP01_SIM_PENDING) ||
      (g_ap01_ui_system_seen && g_ap01_ui_system_ota != g_ap01_sim.ota))
    {
      g_ap01_ui_system_ota = g_ap01_sim.ota;
      g_ap01_ui_system_target = g_ap01_sim.ota_target;
      if (g_ap01_sim.ota == AP01_SIM_PENDING)
        g_ap01_ui_system_view = AP01_SYSTEM_PROGRESS;
      else if (g_ap01_sim.ota == AP01_SIM_OK)
        g_ap01_ui_system_view = AP01_SYSTEM_SUCCESS;
      else if (g_ap01_sim.ota == AP01_SIM_ERROR || g_ap01_sim.ota == AP01_SIM_TIMEOUT)
        {
          g_ap01_ui_system_view = AP01_SYSTEM_FAILURE;
          g_ap01_ui_system_reply = g_ap01_sim.reply;
          g_ap01_ui_system_choice = 1;
        }
      g_ap01_ui_system_changed = true;
    }
  g_ap01_ui_system_seen = true;
}

static void ap01_ui_system_mijia_draw(void)
{
  bool failed = g_ap01_sim.binding == AP01_SIM_ERROR ||
                g_ap01_sim.binding == AP01_SIM_TIMEOUT;
  if (!failed)
    {
      /* Native creator: centered148x152 white frame at y29; image at y38. */
      ap01_ui_system_panel(g_ap01_ui_root, 86, 29, 148, 152, 8, 0xffffff);
      ap01_ui_system_image(g_ap01_ui_root, &ap01_system_mijia_qr, 93, 38);
      ap01_ui_system_text(g_ap01_ui_root, g_ap01_sim.settings.guide_completed ?
                           "旋转旋钮切换界面" : "单击进入操作指引", 0, 192, 320,
                           0xb2b2b2, &ap01_rom_system_hint, true);
    }
  else
    {
      lv_obj_t *circle = ap01_ui_system_panel(g_ap01_ui_root, 127, 44, 66, 66,
                                              33, 0x404040);
      ap01_ui_system_image(circle, &ap01_system_binding_timeout, 15, 15);
      ap01_ui_system_text(g_ap01_ui_root, "绑定超时", 116, 140, 0, 0xffffff,
                           &ap01_rom_charge_error, false);
      ap01_ui_system_text(g_ap01_ui_root, "请单击重启后添加", 91, 178, 0,
                           0xb2b2b2, &ap01_rom_system_hint, false);
    }
  ap01_ui_system_badge(g_ap01_ui_root);
}

static bool ap01_ui_system_mijia_press(void)
{
  if (g_ap01_sim.binding == AP01_SIM_ERROR || g_ap01_sim.binding == AP01_SIM_TIMEOUT)
    {
      if (!ap01_sim_binding_cancel() || !ap01_sim_restart_complete()) ap01_ui_system_show_error();
      else
        {
          g_ap01_ui_system_binding = AP01_SIM_IDLE;
          ap01_ui_system_close();
          ap01_ui_simulated_restart();
        }
      return true;
    }
  /* False requests the parent's native initial-guide entry; binding itself
   * starts via the controlled app/service event, equivalent to scanning QR. */
  return g_ap01_sim.bound || g_ap01_sim.settings.guide_completed;
}

static void ap01_ui_system_version_open(void)
{
  g_ap01_ui_system_version_choice = 0;
}

static void ap01_ui_system_version_turn(int direction)
{
  if (!g_ap01_sim.charger_connected) g_ap01_ui_system_version_choice = 0;
  else if (direction > 0) g_ap01_ui_system_version_choice = 1;
  else if (direction < 0) g_ap01_ui_system_version_choice = 0;
}

static void ap01_ui_system_version_draw(void)
{
  char text[64];
  unsigned int i;
  int scroll = g_ap01_sim.charger_connected && g_ap01_ui_system_version_choice ? 80 : 0;
  ap01_ui_system_text(g_ap01_ui_root, "版本信息", 18, 16, 0, 0xffffff,
                       &ap01_rom_body20, false);
  g_ap01_ui_system_clock = ap01_ui_system_text(g_ap01_ui_root, "00:00", 247,
                                               17, 55, 0xffffff,
                                               &ap01_rom_clock21, false);
  lv_obj_t *list = ap01_ui_system_panel(g_ap01_ui_root, 0, 50, 320, 190, 0, 0);
  for (i = 0; i < (g_ap01_sim.charger_connected ? 2U : 1U); ++i)
    {
      lv_obj_t *row = ap01_ui_system_image(list, &ap01_system_version_card,
                                           10, 10 + i * 95 - scroll);
      bool focused = i == 1 && g_ap01_ui_system_version_choice == 0;
      lv_obj_set_style_image_recolor(row, lv_color_hex(focused ? 0x22363d : 0x1f1f1f), 0);
      lv_obj_set_style_image_recolor_opa(row, LV_OPA_COVER, 0);
      ap01_ui_system_text(row, i == 0 ? "配件显示屏 AP01" : "TA1208", 20,
                           22, 0, 0xffffff, &ap01_rom_body20, false);
      if (i == 0) snprintf(text, sizeof(text), "当前版本 V%04u", g_ap01_sim.firmware_version);
      else snprintf(text, sizeof(text), "当前版本 V%u.%u",
                    g_ap01_sim.device_firmware_version / 10,
                    g_ap01_sim.device_firmware_version % 10);
      ap01_ui_system_text(row, text, 20, 53, 0, 0x969696,
                           &ap01_rom_system_version, false);
      if (i == 1 && g_ap01_sim.device_update_available)
        ap01_ui_system_text(row, "有新版本", 202, 53, 0, 0x89d8f3,
                             &ap01_rom_system_version, false);
    }
  int back_y = (g_ap01_sim.charger_connected ? 200 : 105) - scroll;
  lv_obj_t *back = ap01_ui_system_image(list, &ap01_setting_row, 10, back_y);
  bool focused = !g_ap01_sim.charger_connected || g_ap01_ui_system_version_choice == 1;
  lv_obj_set_style_image_recolor(back, lv_color_hex(focused ? 0x22363d : 0x1f1f1f), 0);
  lv_obj_set_style_image_recolor_opa(back, LV_OPA_COVER, 0);
  ap01_ui_system_text(back, "返回", 40, 24, 0, 0xffffff, &ap01_rom_body20, false);
  ap01_ui_system_badge(g_ap01_ui_root);
}

static bool ap01_ui_system_version_press(void)
{
  if (!g_ap01_sim.charger_connected || g_ap01_ui_system_version_choice == 1)
    return true; /* Native Back: parent returns to settings. */
  if (g_ap01_sim.device_update_available && ap01_ui_system_update_offer(1))
    {
      /* Native version action calls a00fcd54(window,0), bypassing the
       * external previous-failure creator branch (parameter1). */
      g_ap01_ui_system_from_settings = true;
      g_ap01_ui_system_view = AP01_SYSTEM_OFFER;
    }
  return false; /* Native TA1208 row has no action without an actual offer. */
}

static void ap01_ui_system_buttons(lv_obj_t *parent, const char *left,
                                   const char *right)
{
  const char *const labels[] = {left, right};
  unsigned int i;
  for (i = 0; i < 2; ++i)
    {
      lv_obj_t *button = ap01_ui_system_image(parent, &ap01_guide_button,
                                               i == 0 ? 14 : 224, 192);
      lv_obj_set_style_image_recolor(button, lv_color_hex(i == g_ap01_ui_system_choice ?
                                      0x22363d : 0x262626), 0);
      lv_obj_set_style_image_recolor_opa(button, LV_OPA_COVER, 0);
      lv_obj_t *label = ap01_ui_system_text(button, labels[i], 0, 0, 0,
                                            i == g_ap01_ui_system_choice ? 0x89d8f3 : 0xffffff,
                                            &ap01_rom_system_button, false);
      lv_obj_center(label);
    }
}

static void ap01_ui_system_draw(void)
{
  if (!ap01_ui_system_active()) return;
  lv_obj_t *panel = ap01_ui_system_panel(g_ap01_ui_root, 0, 0, 320, 240, 0, 0);
  char text[160];
  const char *model = g_ap01_ui_system_target ? "TA1208" : "AP01";
  if (g_ap01_ui_system_view == AP01_SYSTEM_BINDING)
    {
      ap01_ui_system_mijia_draw();
    }
  else if (g_ap01_ui_system_view == AP01_SYSTEM_ERROR)
    {
      ap01_ui_system_text(panel, "操作失败", 18, 12, 284, 0xff7a00,
                           &ap01_rom_title25, false);
      ap01_ui_system_text(panel, g_ap01_ui_system_reply.error, 18, 77, 284,
                           0xffffff, &ap01_rom_ascii17, false);
      snprintf(text, sizeof(text), "%s / %s", g_ap01_ui_system_reply.operation,
               g_ap01_ui_system_reply.stage);
      ap01_ui_system_text(panel, text, 18, 47, 284, 0xb2b2b2,
                           &ap01_rom_ascii17, false);
      ap01_ui_system_text(panel, g_ap01_ui_system_reply.action_hint, 18, 116,
                           284, 0xb2b2b2, &ap01_rom_ascii17, false);
      lv_obj_t *button = ap01_ui_system_image(panel, &ap01_system_confirm_button, 20, 164);
      lv_obj_set_style_image_recolor(button, lv_color_hex(0x22363d), 0);
      lv_obj_set_style_image_recolor_opa(button, LV_OPA_COVER, 0);
      lv_obj_t *label = ap01_ui_system_text(button, "确认", 0, 0, 0, 0x89d8f3,
                                            &ap01_rom_system_button, false);
      lv_obj_center(label);
    }
  else if (g_ap01_ui_system_view == AP01_SYSTEM_RECOVERY)
    {
      ap01_ui_system_text(panel, "上次更新失败，需要\n重新更新固件", 55, 56, 210,
                           0xffffff, &ap01_rom_charge_error, true);
      lv_obj_t *button = ap01_ui_system_image(panel, &ap01_system_confirm_button, 20, 157);
      lv_obj_set_style_image_recolor(button, lv_color_hex(0x22363d), 0);
      lv_obj_set_style_image_recolor_opa(button, LV_OPA_COVER, 0);
      lv_obj_t *label = ap01_ui_system_text(button, "确认", 0, 0, 0, 0x89d8f3,
                                            &ap01_rom_system_button, false);
      lv_obj_center(label);
    }
  else if (g_ap01_ui_system_view == AP01_SYSTEM_OFFER)
    {
      if (g_ap01_ui_system_target)
        snprintf(text, sizeof(text), "当前版本 V%u.%u", g_ap01_sim.device_firmware_version / 10,
                 g_ap01_sim.device_firmware_version % 10);
      else snprintf(text, sizeof(text), "当前版本 V%04u", g_ap01_sim.firmware_version);
      ap01_ui_system_text(panel, text, 0, 19, 320, 0x808080,
                           &ap01_rom_system_version, true);
      snprintf(text, sizeof(text), "%s有更新固件\n是否立即升级？", model);
      ap01_ui_system_text(panel, text, 60, 61, 200, 0xffffff,
                           &ap01_rom_charge_error, true);
      ap01_ui_system_buttons(panel, "返回", "开始");
    }
  else if (g_ap01_ui_system_view == AP01_SYSTEM_PROGRESS)
    {
      ap01_ui_system_text(panel, g_ap01_ui_system_target ? "正在更新固件..." :
                           "正在升级，请稍后", 0, g_ap01_ui_system_target ? 91 : 63, 320, 0xffffff,
                           &ap01_rom_charge_error, true);
      g_ap01_ui_system_progress = lv_bar_create(panel);
      lv_obj_set_pos(g_ap01_ui_system_progress, 22, 143);
      lv_obj_set_size(g_ap01_ui_system_progress, 276, 9);
      lv_bar_set_range(g_ap01_ui_system_progress, 0, 100);
      lv_bar_set_value(g_ap01_ui_system_progress, g_ap01_sim.ota_progress, LV_ANIM_OFF);
      lv_obj_set_style_bg_color(g_ap01_ui_system_progress, lv_color_hex(0x999999), 0);
      lv_obj_set_style_bg_color(g_ap01_ui_system_progress, lv_color_hex(0x89d8f3), LV_PART_INDICATOR);
      g_ap01_ui_system_progress_text = ap01_ui_system_text(panel, "0%", 0, 159,
        320, 0xffffff, &ap01_rom_ascii17, true);
      if (g_ap01_ui_system_target)
        ap01_ui_system_text(panel, "请不要关闭电源或移动显示屏", 0, 202, 320,
                             0xb2b2b2, &ap01_rom_system_hint, true);
    }
  else if (g_ap01_ui_system_view == AP01_SYSTEM_RESET)
    {
      ap01_ui_system_image(panel, &ap01_system_ota_success, 127, 49);
      /* Native hidden creator taila00fe838/86a uses the same OTA success
       * icon, title fonta02548b0 y144 and hintfonta0254868 y202. */
      ap01_ui_system_text(panel, "恢复出厂设置成功", 0, 144, 320, 0xffffff,
                           &ap01_rom_charge_error, true);
      ap01_ui_system_text(panel, "重启中", 0, 202, 320, 0xb2b2b2,
                           &ap01_rom_system_hint, true);
    }
  else if (g_ap01_ui_system_view == AP01_SYSTEM_SUCCESS)
    {
      ap01_ui_system_image(panel, &ap01_system_ota_success, 127, 49);
      snprintf(text, sizeof(text), "%s固件更新成功", model);
      ap01_ui_system_text(panel, text, 0, 144, 320, 0xffffff,
                           &ap01_rom_charge_error, true);
      ap01_ui_system_text(panel, "短按旋钮返回主界面", 0, 202, 320, 0xb2b2b2,
                           &ap01_rom_system_hint, true);
    }
  else if (g_ap01_ui_system_view == AP01_SYSTEM_FAILURE)
    {
      snprintf(text, sizeof(text), "%s固件更新失败", model);
      ap01_ui_system_text(panel, text, 0, 72, 320, 0xffffff,
                           &ap01_rom_charge_error, true);
      ap01_ui_system_text(panel, g_ap01_ui_system_reply.error, 18, 120, 284,
                           0xff7a00, &ap01_rom_ascii17, false);
      ap01_ui_system_buttons(panel, "返回", "重试");
    }
  else
    {
      bool pending = g_ap01_sim.update_check == AP01_SIM_PENDING;
      ap01_ui_system_text(panel, pending ? "正在检查更新" : "检查更新失败", 0, 75,
                           320, 0xffffff, &ap01_rom_title25, true);
      if (!pending)
        ap01_ui_system_text(panel, g_ap01_ui_system_reply.error, 18, 122, 284,
                             0xff7a00, &ap01_rom_ascii17, false);
      ap01_ui_system_buttons(panel, "返回", pending ? "取消" : "重试");
    }
  ap01_ui_system_badge(g_ap01_ui_root);
}

static void ap01_ui_system_turn(int direction)
{
  if (!ap01_ui_system_active() || g_ap01_ui_system_view == AP01_SYSTEM_ERROR ||
      g_ap01_ui_system_view == AP01_SYSTEM_BINDING ||
      g_ap01_ui_system_view == AP01_SYSTEM_PROGRESS ||
      g_ap01_ui_system_view == AP01_SYSTEM_SUCCESS ||
      g_ap01_ui_system_view == AP01_SYSTEM_RESET ||
      g_ap01_ui_system_view == AP01_SYSTEM_RECOVERY) return;
  /* a00afc88 root popup key19:D->E/H->J; a00fd1ac settings key19:
   * E->D/J->H. Preserve both native callback branches. */
  if (direction > 0) g_ap01_ui_system_choice = g_ap01_ui_system_from_settings ? 1 : 0;
  else if (direction < 0) g_ap01_ui_system_choice = g_ap01_ui_system_from_settings ? 0 : 1;
}

static bool ap01_ui_system_back(void)
{
  if (!ap01_ui_system_active()) return false;
  if (g_ap01_ui_system_view == AP01_SYSTEM_RESET ||
      g_ap01_ui_system_view == AP01_SYSTEM_SUCCESS ||
      g_ap01_ui_system_view == AP01_SYSTEM_RECOVERY) return true;
  if (g_ap01_ui_system_view == AP01_SYSTEM_ERROR)
    {
      g_ap01_ui_system_view = g_ap01_ui_system_resume;
      g_ap01_ui_system_changed = true;
      return true;
    }
  if (g_ap01_ui_system_view == AP01_SYSTEM_BINDING)
    {
      if (!ap01_sim_binding_cancel()) { ap01_ui_system_show_error(); return true; }
      g_ap01_ui_system_binding = g_ap01_sim.binding;
    }
  if (g_ap01_ui_system_view == AP01_SYSTEM_PROGRESS ||
      g_ap01_ui_system_view == AP01_SYSTEM_FAILURE)
    {
      if (!ap01_sim_ota_cancel()) { ap01_ui_system_show_error(); return true; }
      g_ap01_ui_system_ota = g_ap01_sim.ota;
    }
  if (g_ap01_ui_system_view == AP01_SYSTEM_CHECK)
    {
      if (!ap01_sim_update_cancel()) { ap01_ui_system_show_error(); return true; }
      g_ap01_ui_system_check = g_ap01_sim.update_check;
    }
  ap01_ui_system_close();
  return true;
}

static bool ap01_ui_system_press(void)
{
  if (!ap01_ui_system_active()) return false;
  if (g_ap01_ui_system_view == AP01_SYSTEM_RESET) return true;
  if (g_ap01_ui_system_view == AP01_SYSTEM_ERROR) return ap01_ui_system_back();
  if (g_ap01_ui_system_view == AP01_SYSTEM_BINDING)
    {
      if (ap01_ui_system_mijia_press()) return true;
      ap01_ui_system_close(); /* Keep the service binding transaction running. */
      return false; /* Parent opens the initial guide, as native key10 does. */
    }
  if (g_ap01_ui_system_view == AP01_SYSTEM_PROGRESS) return true;
  if (g_ap01_ui_system_view == AP01_SYSTEM_RECOVERY)
    { ap01_ui_system_start_update(); return true; }
  if (g_ap01_ui_system_view == AP01_SYSTEM_SUCCESS)
    {
      if (!ap01_sim_restart_complete()) ap01_ui_system_show_error();
      else
        {
          g_ap01_ui_system_ota = g_ap01_sim.ota;
          ap01_ui_system_close();
          ap01_ui_simulated_restart();
        }
      return true;
    }
  if (g_ap01_ui_system_choice == 0) return ap01_ui_system_back();
  if (g_ap01_ui_system_view == AP01_SYSTEM_CHECK)
    {
      if (g_ap01_sim.update_check == AP01_SIM_PENDING) return ap01_ui_system_back();
      else ap01_ui_system_check_update(g_ap01_ui_system_target);
    }
  else ap01_ui_system_start_update();
  return true;
}

#endif
