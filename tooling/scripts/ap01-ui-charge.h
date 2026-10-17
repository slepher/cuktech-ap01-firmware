/* SPDX-License-Identifier: Apache-2.0 */
/* AP01 0041 charging pages. See charge-0041-round4.json for native evidence.
 * Include after ap01_ui_label/now, before ap01-ui-pages.h.
 * Native coordinates/assets/fonts are retained where recovered. Telemetry and
 * commands use the shared, persistent local service model. */
#ifndef TOOLS_AP01_AP01_UI_CHARGE_H
#define TOOLS_AP01_AP01_UI_CHARGE_H

enum ap01_ui_charge_view_e
{
  AP01_CHARGE_LIST, AP01_CHARGE_MODES, AP01_CHARGE_PORT,
  AP01_CHARGE_SWITCH, AP01_CHARGE_SAFE, AP01_CHARGE_SAFE_INTRO,
  AP01_CHARGE_PROTOCOL
};

enum ap01_ui_charge_popup_e
{
  AP01_CHARGE_POPUP_NONE, AP01_CHARGE_POPUP_BANK,
  AP01_CHARGE_POPUP_DEVICE, AP01_CHARGE_POPUP_SAFE_DEVICE
};

static enum ap01_ui_charge_view_e g_ap01_ui_charge_view;
static unsigned int g_ap01_ui_charge_index;
static unsigned int g_ap01_ui_charge_port;
#define g_ap01_ui_charge_mode (g_ap01_sim.settings.output_mode)
static unsigned int g_ap01_ui_charge_scroll;
static lv_obj_t *g_ap01_ui_charge_clock;
static lv_obj_t *g_ap01_ui_charge_scan;
static unsigned int g_ap01_ui_charge_bank = AP01_SIM_LOCAL_BANK;
static unsigned int g_ap01_ui_charge_seen_revision;
static bool g_ap01_ui_charge_changed;
static bool g_ap01_ui_charge_seen;
static bool g_ap01_ui_charge_connected[AP01_SIM_BANKS];
static bool g_ap01_ui_charge_port_connected[AP01_SIM_BANKS + 1][AP01_SIM_PORTS];
static enum ap01_ui_charge_popup_e g_ap01_ui_charge_popup;
static unsigned int g_ap01_ui_charge_popup_bank;
static unsigned int g_ap01_ui_charge_popup_port;
static uint32_t g_ap01_ui_charge_popup_time;
static uint32_t g_ap01_ui_charge_intro_time;
static bool g_ap01_ui_charge_intro_caption;
static enum ap01_sim_status_e g_ap01_ui_charge_protocol_status;
static void ap01_ui_service_feedback(void);

static ap01_sim_port_t *ap01_ui_charge_current_port(void)
{
  return ap01_sim_get_port(g_ap01_ui_charge_bank, g_ap01_ui_charge_port);
}

static unsigned int ap01_ui_charge_milliwatts(const ap01_sim_port_t *port)
{
  return port->connected && port->enabled ?
         (unsigned int)((uint64_t)port->voltage_mv * port->current_ma / 1000) : 0;
}

static void ap01_ui_charge_popup_close(void)
{
  if (g_ap01_ui_charge_popup == AP01_CHARGE_POPUP_BANK)
    {
      g_ap01_ui_page = g_ap01_ui_charge_popup_bank == 0 ? AP01_UI_C1 : AP01_UI_C2;
      g_ap01_ui_mode = AP01_UI_MODE_OVERVIEW;
    }
  g_ap01_ui_charge_popup = AP01_CHARGE_POPUP_NONE;
  g_ap01_ui_charge_changed = true;
}

static bool ap01_ui_charge_popup_active(void)
{
  return g_ap01_ui_charge_popup != AP01_CHARGE_POPUP_NONE;
}

static bool ap01_ui_charge_needs_redraw(void)
{
  bool changed = g_ap01_ui_charge_changed;
  g_ap01_ui_charge_changed = false;
  return changed;
}

static const char *const g_ap01_ui_charge_ports[] = {"C1", "C2", "C3", "A"};
static const char *const g_ap01_ui_charge_modes[] =
  {"AI 智配", "极速单充", "均衡输出", "返回"};

static lv_obj_t *ap01_ui_charge_panel(lv_obj_t *parent, int x, int y,
                                     int w, int h, int radius, uint32_t color)
{
  lv_obj_t *obj = lv_obj_create(parent);
  lv_obj_set_pos(obj, x, y);
  lv_obj_set_size(obj, w, h);
  lv_obj_set_style_pad_all(obj, 0, LV_PART_MAIN);
  lv_obj_set_style_radius(obj, radius, LV_PART_MAIN);
  lv_obj_set_style_border_width(obj, 0, LV_PART_MAIN);
  lv_obj_set_style_bg_color(obj, lv_color_hex(color), LV_PART_MAIN);
  lv_obj_set_style_bg_opa(obj, LV_OPA_COVER, LV_PART_MAIN);
  lv_obj_remove_flag(obj, LV_OBJ_FLAG_SCROLLABLE);
  return obj;
}

static lv_obj_t *ap01_ui_charge_image(lv_obj_t *parent,
                                     const lv_image_dsc_t *src, int x, int y)
{
  lv_obj_t *obj = lv_image_create(parent);
  lv_image_set_src(obj, src);
  lv_obj_set_pos(obj, x, y);
  return obj;
}

static lv_obj_t *ap01_ui_charge_text(lv_obj_t *parent, const char *text,
                                    int x, int y, uint32_t color,
                                    const lv_font_t *font)
{
  return ap01_ui_label(parent, text, x, y, lv_color_hex(color), font);
}

static unsigned int g_ap01_ui_charge_summary_phase;

static void ap01_ui_charge_tick(void)
{
  struct tm now;
  char text[8];
  unsigned int b, p;
  uint32_t tick = lv_tick_get();
  if (g_ap01_ui_charge_summary_phase != tick / 3000)
    {
      g_ap01_ui_charge_summary_phase = tick / 3000;
      if (g_ap01_ui_page == AP01_UI_POWER && g_ap01_ui_mode == AP01_UI_MODE_OVERVIEW)
        g_ap01_ui_charge_changed = true;
    }
  if (g_ap01_ui_charge_scan != NULL)
    lv_image_set_rotation(g_ap01_ui_charge_scan, tick % 3600);
  if (g_ap01_ui_charge_clock != NULL && ap01_ui_now(&now))
    {
      strftime(text, sizeof(text), g_ap01_ui_12_hour ? "%I:%M" : "%H:%M", &now);
      lv_label_set_text(g_ap01_ui_charge_clock, text);
    }
  if (g_ap01_ui_charge_seen_revision != g_ap01_sim.revision)
    {
      g_ap01_ui_charge_seen_revision = g_ap01_sim.revision;
      if (g_ap01_ui_charge_popup != AP01_CHARGE_POPUP_BANK &&
          g_ap01_ui_charge_view != AP01_CHARGE_SAFE_INTRO)
        g_ap01_ui_charge_changed = true;
    }
  for (b = 0; b <= AP01_SIM_LOCAL_BANK; ++b)
    {
      if (b < AP01_SIM_BANKS && g_ap01_ui_charge_seen && g_ap01_sim.banks[b].connected &&
          !g_ap01_ui_charge_connected[b])
        {
          g_ap01_ui_charge_popup = AP01_CHARGE_POPUP_BANK;
          g_ap01_ui_charge_popup_bank = b;
          g_ap01_ui_charge_popup_time = tick;
          g_ap01_ui_charge_changed = true;
        }
      for (p = 0; p < AP01_SIM_PORTS; ++p)
        {
          ap01_sim_port_t *port = ap01_sim_get_port(b, p);
          if (g_ap01_ui_charge_seen && port->connected &&
              !g_ap01_ui_charge_port_connected[b][p] &&
              !ap01_ui_charge_popup_active())
            {
              g_ap01_ui_charge_popup = port->safe_enabled ?
                AP01_CHARGE_POPUP_SAFE_DEVICE : AP01_CHARGE_POPUP_DEVICE;
              g_ap01_ui_charge_popup_bank = b;
              g_ap01_ui_charge_popup_port = p;
              g_ap01_ui_charge_popup_time = tick;
              g_ap01_ui_charge_changed = true;
            }
          g_ap01_ui_charge_port_connected[b][p] = port->connected;
        }
      if (b < AP01_SIM_BANKS)
        g_ap01_ui_charge_connected[b] = g_ap01_sim.banks[b].connected;
    }
  g_ap01_ui_charge_seen = true;
  if (ap01_ui_charge_popup_active() &&
      (!(g_ap01_ui_charge_popup_bank == AP01_SIM_LOCAL_BANK ? g_ap01_sim.charger_connected :
         g_ap01_sim.banks[g_ap01_ui_charge_popup_bank].connected) ||
       (g_ap01_ui_charge_popup != AP01_CHARGE_POPUP_BANK &&
        !ap01_sim_get_port(g_ap01_ui_charge_popup_bank, g_ap01_ui_charge_popup_port)->connected)))
    {
      g_ap01_ui_charge_popup = AP01_CHARGE_POPUP_NONE;
      g_ap01_ui_charge_changed = true;
    }
  if (ap01_ui_charge_popup_active() && tick - g_ap01_ui_charge_popup_time >= 3000)
    ap01_ui_charge_popup_close();
  if (g_ap01_ui_charge_view == AP01_CHARGE_SAFE_INTRO)
    {
      if (tick - g_ap01_ui_charge_intro_time >= 6000)
        {
          g_ap01_ui_charge_view = AP01_CHARGE_SAFE;
          g_ap01_ui_charge_index = 0;
          g_ap01_ui_charge_changed = true;
        }
      else if (tick - g_ap01_ui_charge_intro_time >= 3000 &&
               !g_ap01_ui_charge_intro_caption)
        {
          g_ap01_ui_charge_intro_caption = true;
          g_ap01_ui_charge_changed = true;
        }
    }
  if (g_ap01_ui_charge_view == AP01_CHARGE_PROTOCOL &&
      g_ap01_ui_charge_protocol_status != ap01_ui_charge_current_port()->protocol_status)
    {
      g_ap01_ui_charge_protocol_status = ap01_ui_charge_current_port()->protocol_status;
      g_ap01_ui_charge_index = 1;
      g_ap01_ui_charge_changed = true;
      /* Native a00f3c22 owns the asynchronous failure/retry screen. Only
       * rejected input commands use the generic structured-error overlay. */
    }
}

static void ap01_ui_charge_reset(void)
{
  /* Redraw destroys widgets, but retains the current native navigation state. */
  g_ap01_ui_charge_clock = NULL;
  g_ap01_ui_charge_scan = NULL;
}

static void ap01_ui_charge_badge(void)
{
  /* Simulation identity is in the host window/log, outside the native canvas. */
}

static void ap01_ui_charge_arc(lv_obj_t *parent, int x, int y, int size,
                              int rotation, int sweep, int width,
                              uint32_t bg, uint32_t fg)
{
  lv_obj_t *arc = lv_arc_create(parent);
  lv_obj_set_pos(arc, x, y);
  lv_obj_set_size(arc, size, size);
  lv_arc_set_rotation(arc, rotation);
  lv_arc_set_bg_angles(arc, 0, sweep);
  lv_arc_set_range(arc, 0, 120);
  lv_arc_set_value(arc, 0);
  lv_obj_set_style_arc_color(arc, lv_color_hex(bg), LV_PART_MAIN);
  lv_obj_set_style_arc_color(arc, lv_color_hex(fg), LV_PART_INDICATOR);
  lv_obj_set_style_arc_width(arc, width, LV_PART_MAIN);
  lv_obj_set_style_arc_width(arc, width, LV_PART_INDICATOR);
  lv_obj_set_style_opa(arc, LV_OPA_TRANSP, LV_PART_KNOB);
  lv_obj_remove_flag(arc, LV_OBJ_FLAG_CLICKABLE);
}

static void ap01_ui_charge_draw_power(void)
{
  static const int x[] = {16, 87, 158, 229};
  static const uint32_t bg[] = {0x66541e, 0x66541e, 0x375661, 0x663100};
  static const uint32_t fg[] = {0xffd24b, 0xffd24b, 0x89d8f3, 0xff7a00};
  static const char *const names[] = {"A", "C3", "C2", "C1"};
  unsigned int i;
  unsigned int total = 0;
  unsigned int active = 4;
  char value[64];
  ap01_sim_port_t *ports = g_ap01_sim.ports;
  for (i = 0; i < 4; ++i)
    {
      if (!ports[i].input) total += ap01_ui_charge_milliwatts(&ports[i]);
      if (ports[i].connected && active == 4) active = i;
    }
  for (i = 0; i < 4; ++i)
    {
      /* a0198a9e: 58x58, (x,12), rotation148, sweep244, width6. */
      lv_obj_t *label;
      ap01_ui_charge_arc(g_ap01_ui_root, x[i], 12, 58, 148, 244, 6, bg[i], fg[i]);
      lv_obj_t *arc = lv_obj_get_child(g_ap01_ui_root, -1);
      unsigned int watts = ap01_ui_charge_milliwatts(&ports[3 - i]) / 1000;
      lv_arc_set_value(arc, watts > 120 ? 120 : watts);
      snprintf(value, sizeof(value), "%u", watts);
      label = ap01_ui_charge_text(g_ap01_ui_root, value, x[i], 31, 0xffffff,
                                  &ap01_rom_charge_gauge);
      lv_obj_set_width(label, 58);
      lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
      label = ap01_ui_charge_text(g_ap01_ui_root, names[i], x[i], 58, fg[i],
                                  &ap01_rom_charge_port);
      lv_obj_set_width(label, 58);
      lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
    }

  {
    unsigned int watts = total / 1000;
    if (watts > 999) watts = 999;
    for (i = 0; i < 3; ++i)
      {
        unsigned int divisor = i == 0 ? 100 : i == 1 ? 10 : 1;
        ap01_ui_charge_image(g_ap01_ui_root, &ap01_digits[watts / divisor % 10],
                               10 + 55 * i, 95);
      }
  }
  snprintf(value, sizeof(value), ".%u", total / 100 % 10);
  ap01_ui_charge_text(g_ap01_ui_root, value, 186, 95, 0xffffff,
                       &ap01_rom_charge_number);
  ap01_ui_charge_text(g_ap01_ui_root, "W", 185, 124, 0xffffff,
                       &ap01_rom_charge_watt);
  {
    lv_obj_t *status = ap01_ui_charge_panel(g_ap01_ui_root, 231, 92, 76, 54,
                                            8, 0xffffff);
    /* Native battery descriptor is a status image, not live SIM telemetry. */
    ap01_ui_charge_image(status, &ap01_power_battery, 2, 4);
    ap01_ui_charge_text(status, g_ap01_ui_charge_modes[g_ap01_ui_charge_mode % 3],
                         2, 31, 0, &ap01_rom_charge_status);
  }

  /* Native a00ad486 mutually hides the Excellent/gradient group and the
   * per-device groups; a00ad602 rotates connected candidates every3000ms. */
  unsigned int candidates[4], count = 0;
  for (i = 0; i < 4; ++i)
    if (ports[i].connected) candidates[count++] = i;
  if (count)
    {
      active = candidates[g_ap01_ui_charge_summary_phase % count];
      ap01_sim_port_t *port = &ports[active];
      ap01_ui_charge_text(g_ap01_ui_root, g_ap01_ui_charge_ports[active],
                           15, 172, 0xffffff, &ap01_rom_ascii17);
      if (port->bms_online)
        {
          snprintf(value, sizeof(value), "%u", port->battery);
          lv_obj_t *number = ap01_ui_charge_text(g_ap01_ui_root, value, 38, 165,
                            0xffffff, &ap01_rom_power_battery);
          lv_obj_t *unit = ap01_ui_charge_text(g_ap01_ui_root, "%", 0, 0,
                            0xffffff, &ap01_rom_power_battery_unit);
          lv_obj_align_to(unit, number, LV_ALIGN_OUT_RIGHT_BOTTOM, 2, 0);
          ap01_ui_charge_image(g_ap01_ui_root, &ap01_power_status, 92, 168);
          lv_obj_t *bar = lv_bar_create(g_ap01_ui_root);
          lv_obj_set_pos(bar, 15, 195);
          lv_obj_set_size(bar, 94, 7);
          lv_bar_set_range(bar, 0, 100);
          lv_bar_set_value(bar, port->battery, LV_ANIM_OFF);
          lv_obj_set_style_bg_color(bar, lv_color_hex(0x4d4d4d), LV_PART_MAIN);
          lv_obj_set_style_bg_color(bar, lv_color_hex(0x06ff8b), LV_PART_INDICATOR);
        }
      ap01_ui_charge_text(g_ap01_ui_root, port->device_name, 15, 212, 0xffffff,
                           &ap01_rom_detail_caption);
    }
  else
    {
      ap01_ui_charge_text(g_ap01_ui_root, "Excellent", 16, 160, 0xffffff,
                           &ap01_rom_charge_excellent);
      ap01_ui_charge_image(g_ap01_ui_root, &ap01_power_gradient, 16, 193);
    }
  ap01_ui_charge_image(g_ap01_ui_root,
                         g_ap01_sim.wifi_connected ? &ap01_wifi : &ap01_wifi_off,
                         292, 12);
  ap01_ui_charge_badge();
}

static void ap01_ui_charge_draw_bank(void)
{
  char title[40];
  unsigned int i;
  unsigned int bank_index = g_ap01_ui_page == AP01_UI_C1 ? 0 : 1;
  ap01_sim_bank_t *bank = &g_ap01_sim.banks[bank_index];
  snprintf(title, sizeof(title), "C%u 接入移动电源",
           g_ap01_ui_page == AP01_UI_C1 ? 1 : 2);
  ap01_ui_charge_text(g_ap01_ui_root, title, 15, 16, 0xffffff,
                       &ap01_rom_charge_title);
  ap01_ui_charge_arc(g_ap01_ui_root, 151, 13, 21, 270, 360, 4,
                      0x4d4d4d, bank->battery < 10 ? 0xff5e34 : 0x06ff8b);
  lv_arc_set_range(lv_obj_get_child(g_ap01_ui_root, -1), 0, 100);
  lv_arc_set_value(lv_obj_get_child(g_ap01_ui_root, -1), bank->battery);
  snprintf(title, sizeof(title), "%u", bank->battery);
  ap01_ui_charge_text(g_ap01_ui_root, title, 176, 14,
                       bank->battery < 10 ? 0xff5e34 : 0xffffff,
                       &ap01_rom_charge_percent);
  ap01_ui_charge_text(g_ap01_ui_root, "%", 176 + (bank->battery >= 100 ? 32 :
                       bank->battery >= 10 ? 22 : 12), 14,
                       bank->battery < 10 ? 0xff5e34 : 0xffffff,
                       &ap01_rom_charge_percent_unit);
  if (bank->remaining_minutes != 0)
    {
      snprintf(title, sizeof(title), "%02uH%02uM", bank->remaining_minutes / 60,
               bank->remaining_minutes % 60);
      ap01_ui_charge_text(g_ap01_ui_root, title, 236, 16, 0xffffff,
                           &ap01_rom_charge_percent_unit);
    }
  for (i = 0; i < 4; ++i)
    {
      /* a01986fa, then a00ef1d4's disconnected branch: only '--' survives. */
      lv_obj_t *panel = ap01_ui_charge_panel(g_ap01_ui_root,
                                             i % 2 ? 164 : 14,
                                             i < 2 ? 49 : 143,
                                             142, 85, 14, 0x262626);
      ap01_sim_port_t *port = &bank->ports[i];
      if (!port->connected)
        ap01_ui_charge_text(panel, "--", 16, 47, 0x666666,
                             &ap01_rom_charge_port_number);
      else
        {
          ap01_ui_charge_text(panel, g_ap01_ui_charge_ports[i], 16, 12,
                               0xffffff, &ap01_rom_charge_card_label);
          ap01_ui_charge_text(panel, port->input ? "IN" : "OUT", 96, 12,
                               port->input ? 0x89d8f3 : 0xffd24b,
                               &ap01_rom_charge_card_label);
          snprintf(title, sizeof(title), "%u", ap01_ui_charge_milliwatts(port) / 1000);
          ap01_ui_charge_text(panel, title, 16, 47, 0xffffff,
                               &ap01_rom_charge_port_number);
          ap01_ui_charge_text(panel, "W", 68, 59, 0xffffff,
                               &ap01_rom_charge_card_unit);
          snprintf(title, sizeof(title), "%u.%u V", port->voltage_mv / 1000,
                   port->voltage_mv / 100 % 10);
          ap01_ui_charge_text(panel, title, 86, 43, 0xffffff,
                               &ap01_rom_charge_card_value);
          snprintf(title, sizeof(title), "%u.%u A", port->current_ma / 1000,
                   port->current_ma / 100 % 10);
          ap01_ui_charge_text(panel, title, 86, 61, 0xffffff,
                               &ap01_rom_charge_card_value);
        }
    }
  ap01_ui_charge_badge();
}

static void ap01_ui_charge_draw_overview(void)
{
  if (g_ap01_ui_page == AP01_UI_POWER) ap01_ui_charge_draw_power();
  else ap01_ui_charge_draw_bank();
}

static void ap01_ui_charge_open(void)
{
  g_ap01_ui_charge_view = AP01_CHARGE_LIST;
  g_ap01_ui_charge_index = 0;
  g_ap01_ui_charge_scroll = 0;
  g_ap01_ui_charge_bank = AP01_SIM_LOCAL_BANK;
}

static void ap01_ui_charge_focus(lv_obj_t *obj, bool focused)
{
  lv_obj_set_style_outline_width(obj, focused ? 2 : 0, LV_PART_MAIN);
  lv_obj_set_style_outline_color(obj, lv_color_hex(0x89d8f3), LV_PART_MAIN);
  lv_obj_set_style_outline_pad(obj, -2, LV_PART_MAIN);
}

static void ap01_ui_charge_card_color(lv_obj_t *obj, uint32_t color)
{
  /* a00a5da8 supplies a color for the native white alpha-mask PNG. Recolor
   * the image only; children retain their own text/icon colors. */
  lv_obj_set_style_image_recolor(obj, lv_color_hex(color), LV_PART_MAIN);
  lv_obj_set_style_image_recolor_opa(obj, LV_OPA_COVER, LV_PART_MAIN);
}

static void ap01_ui_charge_draw_list(void)
{
  lv_obj_t *list = ap01_ui_charge_panel(g_ap01_ui_root, 0, 0, 320, 240, 0, 0);
  unsigned int i;
  for (i = 0; i < 6; ++i)
    {
      int y = (i == 0 ? 8 : 98 + ((int)i - 1) * 104) -
              (int)g_ap01_ui_charge_scroll;
      lv_obj_t *row;
      if (i == 0)
        {
          row = ap01_ui_charge_image(list, &ap01_charge_mode_card, 10, y);
          /* Creator a00b0958..096a: selected mode card color 0x22363d.
           * The inactive mode fill follows the native neutral card color. */
          ap01_ui_charge_card_color(row, g_ap01_ui_charge_index == 0 ?
                                      0x22363d : 0x262626);
          ap01_ui_charge_image(row, &ap01_charge_mode_icon, 31, 30);
          ap01_ui_charge_text(row, "输出模式", 60, 17, 0xffffff,
                               &ap01_rom_weather_text);
          ap01_ui_charge_text(row, g_ap01_ui_charge_modes[g_ap01_ui_charge_mode],
                               60, 39, 0xffffff, &ap01_rom_month);
        }
      else if (i < 5)
        {
          ap01_sim_port_t *port = ap01_sim_get_port(g_ap01_ui_charge_bank, i - 1);
          char text[32];
          row = ap01_ui_charge_image(list, &ap01_charge_port_card, 10, y);
          /* Creator a00b0a04..0a16 passes 0x1f1f1f to a00a5da8. */
          ap01_ui_charge_card_color(row, 0x1f1f1f);
          ap01_ui_charge_text(row, g_ap01_ui_charge_ports[i - 1], 24, 35,
                               0x89d8f3, &ap01_rom_weather_text);
          snprintf(text, sizeof(text), "%uW MAX", port->max_watts);
          ap01_ui_charge_text(row, text, 60, port->connected ? 18 : 35, 0xffffff,
                               &ap01_rom_ascii17);
          if (!port->enabled)
            ap01_ui_charge_text(row, "接口关闭", 194, 35, 0x666666,
                                 &ap01_rom_mini_week);
          else if (port->connected)
            {
              unsigned int mw = ap01_ui_charge_milliwatts(port);
              snprintf(text, sizeof(text), "%u.%uW", mw / 1000, mw / 100 % 10);
              ap01_ui_charge_text(row, text, 60, 45, 0xffffff,
                                   &ap01_rom_ascii17);
              snprintf(text, sizeof(text), "%s %uW", port->protocol == 0 ? "PD" :
                       port->protocol == 1 ? "PPS" : "UFCS", port->max_watts);
              ap01_ui_charge_text(row, text, 161, 67, 0xffffff,
                                   &ap01_rom_ascii17);
            }
        }
      else
        {
          row = ap01_ui_charge_image(list, &ap01_setting_row, 10, y);
          /* Creator a00b0cee..0d00 passes 0x262626 for the return mask. */
          ap01_ui_charge_card_color(row, 0x262626);
          ap01_ui_charge_text(row, "返回", 44, 27, 0xffffff,
                               &ap01_rom_body20);
        }
      /* Native selected rows tint/recolor the card. An outline retains native
       * bitmap pixels; this selection treatment is explicitly reconstructed. */
      ap01_ui_charge_focus(row, g_ap01_ui_charge_index == i);
    }
  ap01_ui_charge_badge();
}

static void ap01_ui_charge_draw_choices(const char *title,
                                        const char *const *choices,
                                        unsigned int count)
{
  unsigned int first = g_ap01_ui_charge_index > 2 ? 1 : 0;
  unsigned int i;
  ap01_ui_charge_text(g_ap01_ui_root, title, 18, 16, 0xffffff,
                       &ap01_rom_body20);
  g_ap01_ui_charge_clock = ap01_ui_charge_text(g_ap01_ui_root, "00:00",
                                               247, 17, 0xffffff,
                                               &ap01_rom_clock21);
  for (i = first; i < count; ++i)
    {
      int y = 56 + ((int)i - (int)first) * 55;
      lv_obj_t *row = ap01_ui_charge_panel(g_ap01_ui_root, 10, y, 300, 50,
                                            10, g_ap01_ui_charge_index == i ?
                                            0x22363d : 0x262626);
      ap01_ui_charge_text(row, choices[i], 20, 14, 0xffffff,
                           &ap01_rom_body20);
      if ((g_ap01_ui_charge_view == AP01_CHARGE_MODES &&
           i == g_ap01_ui_charge_mode) ||
          (g_ap01_ui_charge_view == AP01_CHARGE_SWITCH && i < 2 &&
           (i == 0) == ap01_ui_charge_current_port()->enabled) ||
          (g_ap01_ui_charge_view == AP01_CHARGE_SAFE && i < 2 &&
           (i == 0) == ap01_ui_charge_current_port()->safe_enabled))
        ap01_ui_charge_text(row, LV_SYMBOL_OK, 267, 17, 0x89d8f3,
                             &lv_font_montserrat_14);
    }
  ap01_ui_charge_tick();
  ap01_ui_charge_badge();
}

static void ap01_ui_charge_history(lv_obj_t *parent, int x, int y, int w, int h)
{
  const ap01_sim_port_t *port = ap01_ui_charge_current_port();
  const unsigned int *history = port->history;
  unsigned int head = port->history_head;
  unsigned int available = port->history_count;
  lv_obj_t *chart = lv_chart_create(parent);
  lv_chart_series_t *series;
  unsigned int i;
  unsigned int count = available > AP01_SIM_HISTORY ? AP01_SIM_HISTORY : available;
  lv_obj_set_pos(chart, x, y);
  lv_obj_set_size(chart, w, h);
  lv_obj_set_style_pad_all(chart, 3, LV_PART_MAIN);
  lv_obj_set_style_bg_color(chart, lv_color_hex(0x141414), LV_PART_MAIN);
  lv_obj_set_style_border_width(chart, 0, LV_PART_MAIN);
  lv_obj_set_style_line_color(chart, lv_color_hex(0x414141), LV_PART_MAIN);
  lv_obj_set_style_size(chart, 0, 0, LV_PART_INDICATOR);
  lv_chart_set_type(chart, LV_CHART_TYPE_LINE);
  lv_chart_set_point_count(chart, AP01_SIM_HISTORY);
  lv_chart_set_range(chart, LV_CHART_AXIS_PRIMARY_Y, 0, 120000);
  lv_chart_set_div_line_count(chart, 4, 5);
  series = lv_chart_add_series(chart,
    lv_color_hex(ap01_ui_charge_current_port()->safe_enabled ? 0x06ff8b : 0x89d8f3),
    LV_CHART_AXIS_PRIMARY_Y);
  for (i = 0; i < AP01_SIM_HISTORY; ++i)
    lv_chart_set_next_value(chart, series, LV_CHART_POINT_NONE);
  for (i = 0; i < count; ++i)
    {
      unsigned int start = (head + AP01_SIM_HISTORY - count) % AP01_SIM_HISTORY;
      lv_chart_set_next_value(chart, series, history[(start + i) % AP01_SIM_HISTORY]);
    }
}

static void ap01_ui_charge_draw_port(void)
{
  static const char *const titles[] =
    {"", "接口开关", "放心充设置", "ADC 协议助手", "返回"};
  char text[40];
  unsigned int i;
  ap01_sim_port_t *port = ap01_ui_charge_current_port();
  int scroll = (int)g_ap01_ui_charge_index * 100;
  lv_obj_t *content = ap01_ui_charge_panel(g_ap01_ui_root, 0, -scroll, 320, 640, 0, 0);
  unsigned int mw = ap01_ui_charge_milliwatts(port);
  lv_obj_t *port_title = ap01_ui_charge_text(content,
    g_ap01_ui_charge_ports[g_ap01_ui_charge_port], 15, 28,
    port->safe_enabled ? 0x06ff8b : 0x89d8f3, &ap01_rom_detail_metric);
  snprintf(text, sizeof(text), "%uW MAX", port->max_watts);
  lv_obj_t *maximum = ap01_ui_charge_text(content, text, 44, 33, 0xffffff,
                                           &ap01_rom_ascii17);
  /* The chart begins at114. Keep the MAX label within its native left column
   * even when the local service provides a longer three-digit maximum. */
  lv_obj_set_style_text_letter_space(maximum, -1, 0);
  lv_obj_align_to(maximum, port_title, LV_ALIGN_OUT_RIGHT_BOTTOM, 5, -1);
  lv_obj_set_width(maximum, 112 - lv_obj_get_x(maximum));
  lv_label_set_long_mode(maximum, LV_LABEL_LONG_CLIP);
  snprintf(text, sizeof(text), mw < 100000 ? "%02u.%u" : "%03u.%u",
           mw / 1000, mw / 100 % 10);
  /* a018f288 uses these two exact number fonts; no separate W is created. */
  ap01_ui_charge_text(content, text, 16, 70, 0xffffff,
    mw < 100000 ? &ap01_rom_weather_temp : &ap01_rom_charge_live_power3);
  ap01_ui_charge_history(content, 114, 26, 194, 78);
  snprintf(text, sizeof(text), "%u.%uV | %u.%uA", port->voltage_mv / 1000,
           port->voltage_mv / 100 % 10, port->current_ma / 1000,
           port->current_ma / 100 % 10);
  ap01_ui_charge_text(content, text, 16, 124, 0xffffff, &ap01_rom_clock21);
  if (port->connected)
    {
      ap01_ui_charge_text(content, port->device_name, 16, 154, 0xffffff,
                           &ap01_rom_ascii17);
      if (port->bms_online)
        {
          snprintf(text, sizeof(text), "| %u%%", port->battery);
          ap01_ui_charge_text(content, text, 238, 154, 0xffffff,
                               &ap01_rom_ascii17);
        }
    }
  for (i = 1; i < 5; ++i)
    {
      int y = 190 + ((int)i - 1) * 100;
      lv_obj_t *row = ap01_ui_charge_panel(content, 10, y, 300, 94,
                                            12, g_ap01_ui_charge_index == i ?
                                            0x22363d : 0x262626);
      bool capable = i == 2 ? (port->capabilities & AP01_SIM_CAP_SAFE) != 0 :
                     i == 3 ? (port->capabilities & AP01_SIM_CAP_PROTOCOL) != 0 : true;
      ap01_ui_charge_text(row, titles[i], 20, 32, capable ? 0xffffff : 0x666666,
                           &ap01_rom_body20);
    }
  ap01_ui_charge_badge();
}

static void ap01_ui_charge_buttons(const char *left, const char *right)
{
  const char *labels[] = {left, right};
  unsigned int i;
  for (i = 0; i < 2; ++i)
    {
      lv_obj_t *button = ap01_ui_charge_panel(g_ap01_ui_root,
                                              i == 0 ? 35 : 170, 191,
                                              115, 37, 8,
                                              g_ap01_ui_charge_index == i ?
                                              0x22363d : 0x262626);
      lv_obj_t *label = ap01_ui_charge_text(button, labels[i], 0, 8,
                                            0xffffff, &ap01_rom_body20);
      lv_obj_set_width(label, 115);
      lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
      ap01_ui_charge_focus(button, g_ap01_ui_charge_index == i);
    }
}

static void ap01_ui_charge_draw_safe_intro(void)
{
  if (lv_tick_get() - g_ap01_ui_charge_intro_time < 3000)
    {
#if defined(LV_USE_GIF) && LV_USE_GIF
      lv_obj_t *gif = lv_gif_create(g_ap01_ui_root);
      lv_gif_set_src(gif, &ap01_charge_safe_intro);
      lv_obj_set_pos(gif, 75, 35);
#endif
    }
  else
    {
      /* a00f7ee0..7f5c creator, then a00f2bee GIF-ready transition. */
      ap01_ui_charge_image(g_ap01_ui_root, &ap01_charge_safe_title, 97, 63);
      ap01_ui_charge_image(g_ap01_ui_root, &ap01_charge_safe_caption, 94, 100);
      ap01_ui_charge_image(g_ap01_ui_root, &ap01_charge_safe_hint, 96, 149);
    }
  ap01_ui_charge_badge();
}

static void ap01_ui_charge_draw_protocol(void)
{
  ap01_sim_port_t *port = ap01_ui_charge_current_port();
  char text[64];
  unsigned int i;
  enum ap01_sim_status_e status = port->protocol_status;
  if (status == AP01_SIM_IDLE)
    {
      ap01_ui_charge_image(g_ap01_ui_root, &ap01_charge_protocol_bg, 0, 0);
      ap01_ui_charge_image(g_ap01_ui_root, &ap01_charge_protocol_title, 117, 84);
      ap01_ui_charge_image(g_ap01_ui_root, &ap01_charge_protocol_caption, 62, 114);
      ap01_ui_charge_buttons("返回", "开始");
    }
  else if (status == AP01_SIM_PENDING)
    {
      g_ap01_ui_charge_scan = ap01_ui_charge_image(g_ap01_ui_root,
        &ap01_charge_protocol_scan, 135, 23);
      snprintf(text, sizeof(text), "%s口设备识别中...",
               g_ap01_ui_charge_ports[g_ap01_ui_charge_port]);
      lv_obj_t *label = ap01_ui_charge_text(g_ap01_ui_root, text, 0, 99, 0xffffff,
                                            &ap01_rom_body20);
      lv_obj_set_width(label, 320);
      lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
      label = ap01_ui_charge_text(g_ap01_ui_root, "检测中会进行多次自动重连",
                                   0, 159, 0xffffff, &ap01_rom_mini_week);
      lv_obj_set_width(label, 320);
      lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
      label = ap01_ui_charge_text(g_ap01_ui_root, "请勿插拔设备", 0, 176, 0xffffff,
                                   &ap01_rom_mini_week);
      lv_obj_set_width(label, 320);
      lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
    }
  else if (status == AP01_SIM_OK)
    {
      lv_obj_t *badge = ap01_ui_charge_panel(g_ap01_ui_root, 16, 17, 40, 24,
                                              6, 0x89d8f3);
      ap01_ui_charge_text(badge, g_ap01_ui_charge_ports[g_ap01_ui_charge_port],
                           8, 4, 0, &ap01_rom_charge_protocol_port);
      ap01_ui_charge_text(g_ap01_ui_root, "协议检测", 70, 17, 0xffffff,
                           &ap01_rom_body20);
      for (i = 0; i < 3; ++i)
        {
          static const char *const names[] = {"PD", "PPS", "UFCS"};
          ap01_ui_charge_text(g_ap01_ui_root, names[i], 49, 65 + 36 * i,
                               0xffffff, &ap01_rom_ascii17);
          ap01_ui_charge_text(g_ap01_ui_root, port->protocol_mask & (1U << i) ?
                               "ON" : "OFF", 225, 65 + 36 * i,
                               port->protocol_mask & (1U << i) ? 0x06ff8b : 0x666666,
                               &ap01_rom_ascii17);
        }
      ap01_ui_charge_buttons("取消", "确认");
    }
  else
    {
      snprintf(text, sizeof(text), "%s口设备识别失败",
               g_ap01_ui_charge_ports[g_ap01_ui_charge_port]);
      lv_obj_t *label = ap01_ui_charge_text(g_ap01_ui_root, text, 0, 82, 0xffffff,
                                            &ap01_rom_charge_error);
      lv_obj_set_width(label, 320);
      lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
      if (g_ap01_sim.reply.error[0] != '\0')
        ap01_ui_charge_text(g_ap01_ui_root, g_ap01_sim.reply.error, 16, 129,
                             0xff7a00, &ap01_rom_ascii17);
      ap01_ui_charge_buttons("返回", "重试");
    }
  ap01_ui_charge_badge();
}

static void ap01_ui_charge_draw_detail(void)
{
  static const char *const switches[] = {"打开", "关闭", "返回"};
  if (g_ap01_ui_charge_view == AP01_CHARGE_LIST) ap01_ui_charge_draw_list();
  else if (g_ap01_ui_charge_view == AP01_CHARGE_MODES)
    ap01_ui_charge_draw_choices("输出模式", g_ap01_ui_charge_modes, 4);
  else if (g_ap01_ui_charge_view == AP01_CHARGE_PORT) ap01_ui_charge_draw_port();
  else if (g_ap01_ui_charge_view == AP01_CHARGE_SWITCH)
    ap01_ui_charge_draw_choices("接口开关", switches, 3);
  else if (g_ap01_ui_charge_view == AP01_CHARGE_SAFE)
    ap01_ui_charge_draw_choices("放心充设置", switches, 3);
  else if (g_ap01_ui_charge_view == AP01_CHARGE_SAFE_INTRO)
    ap01_ui_charge_draw_safe_intro();
  else ap01_ui_charge_draw_protocol();
}

static void ap01_ui_charge_turn(int direction)
{
  if (ap01_ui_charge_popup_active() ||
      g_ap01_ui_charge_view == AP01_CHARGE_SAFE_INTRO ||
      (g_ap01_ui_charge_view == AP01_CHARGE_PROTOCOL &&
       ap01_ui_charge_current_port()->protocol_status == AP01_SIM_PENDING))
    return;
  unsigned int max = g_ap01_ui_charge_view == AP01_CHARGE_LIST ? 5 :
                     g_ap01_ui_charge_view == AP01_CHARGE_MODES ? 3 :
                     g_ap01_ui_charge_view == AP01_CHARGE_PORT ? 4 :
                     g_ap01_ui_charge_view == AP01_CHARGE_PROTOCOL ? 1 : 2;
  unsigned int old = g_ap01_ui_charge_index;
  if (direction > 0 && old < max) ++g_ap01_ui_charge_index;
  if (direction < 0 && old > 0) --g_ap01_ui_charge_index;
  if (g_ap01_ui_charge_view == AP01_CHARGE_LIST && old != g_ap01_ui_charge_index)
    {
      /* Literal a00f61ae right/left scroll targets; deliberately asymmetric. */
      static const unsigned int right[] = {0, 0, 165, 165, 375, 480};
      static const unsigned int left[] = {0, 0, 165, 270, 270, 480};
      g_ap01_ui_charge_scroll = direction > 0 ?
        right[g_ap01_ui_charge_index] : left[g_ap01_ui_charge_index];
    }
  printf("CHARGE view=%u item=%u scroll=%u sim-local\n",
         g_ap01_ui_charge_view, g_ap01_ui_charge_index, g_ap01_ui_charge_scroll);
}

static bool ap01_ui_charge_press(void)
{
  ap01_sim_port_t *port = ap01_ui_charge_current_port();
  if (g_ap01_ui_charge_view == AP01_CHARGE_LIST)
    {
      if (g_ap01_ui_charge_index == 5) return true;
      g_ap01_ui_charge_view = g_ap01_ui_charge_index == 0 ?
                             AP01_CHARGE_MODES : AP01_CHARGE_PORT;
      if (g_ap01_ui_charge_index != 0)
        g_ap01_ui_charge_port = g_ap01_ui_charge_index - 1;
      g_ap01_ui_charge_index = 0;
    }
  else if (g_ap01_ui_charge_view == AP01_CHARGE_MODES)
    {
      if (g_ap01_ui_charge_index == 3) ap01_ui_charge_open();
      else
        {
          if (!ap01_sim_set_mode(g_ap01_ui_charge_index))
            ap01_ui_service_feedback();
        }
    }
  else if (g_ap01_ui_charge_view == AP01_CHARGE_PORT)
    {
      if (g_ap01_ui_charge_index == 4)
        {
          g_ap01_ui_charge_view = AP01_CHARGE_LIST;
          g_ap01_ui_charge_index = g_ap01_ui_charge_port + 1;
        }
      else if (g_ap01_ui_charge_index == 1)
        {
          g_ap01_ui_charge_view = AP01_CHARGE_SWITCH;
          g_ap01_ui_charge_index = 0;
        }
      else if (g_ap01_ui_charge_index == 2 &&
               (port->capabilities & AP01_SIM_CAP_SAFE) != 0)
        {
          g_ap01_ui_charge_view = AP01_CHARGE_SAFE;
          g_ap01_ui_charge_index = 0;
        }
      else if (g_ap01_ui_charge_index == 3 && port->connected &&
               (port->capabilities & AP01_SIM_CAP_PROTOCOL) != 0)
        {
          g_ap01_ui_charge_view = AP01_CHARGE_PROTOCOL;
          g_ap01_ui_charge_index = 1;
          if (!ap01_sim_protocol_cancel()) ap01_ui_service_feedback();
          g_ap01_ui_charge_protocol_status = port->protocol_status;
        }
    }
  else if (g_ap01_ui_charge_view == AP01_CHARGE_PROTOCOL)
    {
      if (port->protocol_status == AP01_SIM_PENDING) return false;
      if (port->protocol_status == AP01_SIM_IDLE)
        {
          if (g_ap01_ui_charge_index == 0)
            {
              g_ap01_ui_charge_view = AP01_CHARGE_PORT;
              g_ap01_ui_charge_index = 3;
            }
          else if (!ap01_sim_protocol_start(g_ap01_ui_charge_bank,
                                            g_ap01_ui_charge_port))
            ap01_ui_service_feedback();
        }
      else if (g_ap01_ui_charge_index == 0)
        {
          if (ap01_sim_protocol_cancel()) g_ap01_ui_charge_index = 1;
          else ap01_ui_service_feedback();
        }
      else if (port->protocol_status == AP01_SIM_OK)
        {
          if (ap01_sim_protocol_confirm(g_ap01_ui_charge_bank,
                                        g_ap01_ui_charge_port,
                                        (~port->protocol_mask) & 7U))
            {
              g_ap01_ui_charge_view = AP01_CHARGE_PORT;
              g_ap01_ui_charge_index = 3;
            }
          else ap01_ui_service_feedback();
        }
      else if (!ap01_sim_protocol_start(g_ap01_ui_charge_bank,
                                        g_ap01_ui_charge_port))
        ap01_ui_service_feedback();
      g_ap01_ui_charge_protocol_status = port->protocol_status;
    }
  else if (g_ap01_ui_charge_view == AP01_CHARGE_SAFE_INTRO)
    {
      /* Native GIF and its following caption timer consume short presses. */
      return false;
    }
  else if (g_ap01_ui_charge_index == 2)
    {
      unsigned int previous = g_ap01_ui_charge_view == AP01_CHARGE_SAFE ? 2 : 1;
      g_ap01_ui_charge_view = AP01_CHARGE_PORT;
      g_ap01_ui_charge_index = previous;
    }
  else if (g_ap01_ui_charge_view == AP01_CHARGE_SWITCH)
    {
      if (!ap01_sim_set_port(g_ap01_ui_charge_bank, g_ap01_ui_charge_port,
                             g_ap01_ui_charge_index == 0))
        ap01_ui_service_feedback();
    }
  else if (g_ap01_ui_charge_view == AP01_CHARGE_SAFE)
    {
      bool intro = g_ap01_ui_charge_index == 0 && !port->safe_enabled;
      if (ap01_sim_set_safe(g_ap01_ui_charge_bank, g_ap01_ui_charge_port,
                            g_ap01_ui_charge_index == 0,
                            port->safe_mode, port->safe_limit))
        {
          if (intro)
            {
              g_ap01_ui_charge_view = AP01_CHARGE_SAFE_INTRO;
              g_ap01_ui_charge_intro_time = lv_tick_get();
              g_ap01_ui_charge_intro_caption = false;
            }
        }
      else ap01_ui_service_feedback();
    }
  printf("CHARGE view=%u item=%u sim-local\n", g_ap01_ui_charge_view,
         g_ap01_ui_charge_index);
  return false;
}

static bool ap01_ui_charge_back(void)
{
  if (g_ap01_ui_charge_view == AP01_CHARGE_LIST) return false;
  if (g_ap01_ui_charge_view == AP01_CHARGE_MODES)
    ap01_ui_charge_open();
  else if (g_ap01_ui_charge_view == AP01_CHARGE_PORT)
    {
      g_ap01_ui_charge_view = AP01_CHARGE_LIST;
      g_ap01_ui_charge_index = g_ap01_ui_charge_port + 1;
    }
  else
    {
      unsigned int index = g_ap01_ui_charge_view == AP01_CHARGE_PROTOCOL ? 3 :
                           g_ap01_ui_charge_view == AP01_CHARGE_SWITCH ? 1 : 2;
      if (g_ap01_ui_charge_view == AP01_CHARGE_PROTOCOL &&
          !ap01_sim_protocol_cancel())
        {
          ap01_ui_service_feedback();
          return true;
        }
      g_ap01_ui_charge_view = AP01_CHARGE_PORT;
      g_ap01_ui_charge_index = index;
    }
  return true;
}

static bool ap01_ui_charge_popup_press(void)
{
  /* Native insert notifications finish on the GIF-ready/3s timer event. */
  return ap01_ui_charge_popup_active();
}

static bool ap01_ui_charge_popup_back(void)
{
  if (!ap01_ui_charge_popup_active()) return false;
  ap01_ui_charge_popup_close();
  return true;
}

static void ap01_ui_charge_draw_popup(void)
{
  if (!ap01_ui_charge_popup_active()) return;
  lv_obj_t *panel = ap01_ui_charge_panel(g_ap01_ui_root, 0, 0, 320, 240, 0, 0);
  if (g_ap01_ui_charge_popup == AP01_CHARGE_POPUP_BANK)
    {
#if defined(LV_USE_GIF) && LV_USE_GIF
      lv_obj_t *gif = lv_gif_create(panel);
      lv_gif_set_src(gif, &ap01_charge_bank_insert);
      lv_obj_set_pos(gif, 0, 0);
#endif
    }
  else
    {
      ap01_sim_port_t *port = ap01_sim_get_port(g_ap01_ui_charge_popup_bank,
                                                g_ap01_ui_charge_popup_port);
      char text[64];
      lv_obj_t *label;
      if (g_ap01_ui_charge_popup == AP01_CHARGE_POPUP_DEVICE)
        {
          lv_obj_t *badge = ap01_ui_charge_panel(panel, 81, 47, 46, 26, 6, 0x89d8f3);
          ap01_ui_charge_text(badge, g_ap01_ui_charge_ports[g_ap01_ui_charge_popup_port],
                               12, 5, 0, &ap01_rom_charge_protocol_port);
          ap01_ui_charge_image(panel, &ap01_charge_cable_icon, 137, 50);
          ap01_ui_charge_text(panel, "Charging", 155, 47, 0x89d8f3,
                               &ap01_rom_detail_metric);
          label = ap01_ui_charge_text(panel, port->device_name, 10, 99, 0xffffff,
                                       &ap01_rom_charge_device_name);
          lv_obj_set_width(label, 300);
          lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
          snprintf(text, sizeof(text), "%uA Cable", port->cable_amps);
          label = ap01_ui_charge_text(panel, text, 10, 162, 0xffffff,
                                       &ap01_rom_mini_date);
          lv_obj_set_width(label, 300);
          lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
        }
      else
        {
          lv_obj_t *badge = ap01_ui_charge_panel(panel, 125, 19, 108, 33, 10, 0x01331c);
          ap01_ui_charge_text(badge, "放心充已开启", 8, 10, 0x06ff8b,
                               &ap01_rom_mini_week);
          ap01_ui_charge_text(panel, g_ap01_ui_charge_ports[g_ap01_ui_charge_popup_port],
                               87, 26, 0x06ff8b, &ap01_rom_charge_popup_port);
          ap01_ui_charge_arc(panel, 73, 78, 60, 270, 360, 10, 0x333333, 0x06ff8b);
          lv_obj_t *arc = lv_obj_get_child(panel, -1);
          lv_arc_set_range(arc, 0, 100);
          lv_arc_set_value(arc, port->battery);
          snprintf(text, sizeof(text), "%u", port->battery);
          ap01_ui_charge_text(panel, text, 147, 80, 0xffffff,
                               &ap01_rom_charge_popup_percent);
          ap01_ui_charge_text(panel, "%", 191, 90, 0xffffff,
                               &ap01_rom_charge_popup_percent_unit);
          ap01_ui_charge_text(panel, port->device_name, 147, 123, 0xffffff,
                               &ap01_rom_clock21);
          lv_obj_t *info = ap01_ui_charge_panel(panel, 45, 157, 230, 70, 9, 0x262626);
          unsigned int mw = ap01_ui_charge_milliwatts(port);
          snprintf(text, sizeof(text), "%u.%u", mw / 1000, mw / 100 % 10);
          ap01_ui_charge_text(info, text, 10, 23, 0xffffff, &ap01_rom_charge_popup_power);
          ap01_ui_charge_text(info, "W", 92, 31, 0xffffff, &ap01_rom_charge_watt);
          snprintf(text, sizeof(text), "%u.%u V", port->voltage_mv / 1000,
                   port->voltage_mv / 100 % 10);
          ap01_ui_charge_text(info, text, 146, 13, 0xffffff, &ap01_rom_clock21);
          snprintf(text, sizeof(text), "%u.%u A", port->current_ma / 1000,
                   port->current_ma / 100 % 10);
          ap01_ui_charge_text(info, text, 146, 37, 0xffffff, &ap01_rom_clock21);
        }
    }
  ap01_ui_charge_badge();
}

#endif
