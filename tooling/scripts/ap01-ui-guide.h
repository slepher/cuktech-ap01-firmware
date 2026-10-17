/* SPDX-License-Identifier: Apache-2.0 */
/* Native 0041 onboarding, practice, boot and screensaver application family.
 * Include after charge/pages and before settings. Assets come from the ROM;
 * local services provide telemetry, settings and atomic persistence. */
#ifndef TOOLS_AP01_AP01_UI_GUIDE_H
#define TOOLS_AP01_AP01_UI_GUIDE_H

static unsigned int g_ap01_ui_guide_stage = 0x25;
static bool g_ap01_ui_guide_active;
static bool g_ap01_ui_guide_mijia;
static bool g_ap01_ui_guide_save_error;
static uint32_t g_ap01_ui_guide_transition;
static lv_obj_t *g_ap01_ui_guide_background;
static lv_obj_t *g_ap01_ui_guide_overlay;
static lv_obj_t *g_ap01_ui_guide_error;
static unsigned int g_ap01_ui_saver_kind;
static unsigned int g_ap01_ui_saver_variant;
static uint32_t g_ap01_ui_saver_last_input;
static bool g_ap01_ui_saver_initialized;
static unsigned int g_ap01_ui_saver_seen_revision;
static lv_obj_t *g_ap01_ui_saver_clock;
static lv_obj_t *g_ap01_ui_saver_period;
static lv_obj_t *g_ap01_ui_saver_date;
static lv_obj_t *g_ap01_ui_saver_day;
static lv_obj_t *g_ap01_ui_saver_weekday;
static lv_obj_t *g_ap01_ui_saver_temperature;
static lv_obj_t *g_ap01_ui_saver_digit[2][4];
static lv_obj_t *g_ap01_ui_saver_dot[2];
static lv_obj_t *g_ap01_ui_saver_watt[2];
static bool g_ap01_ui_saver_connected;
static bool g_ap01_ui_boot_running;
static uint32_t g_ap01_ui_boot_start;

static void ap01_ui_guide_reset(void)
{
  g_ap01_ui_guide_background = NULL;
  g_ap01_ui_guide_overlay = NULL;
  g_ap01_ui_guide_error = NULL;
  g_ap01_ui_saver_clock = NULL;
  g_ap01_ui_saver_period = NULL;
  g_ap01_ui_saver_date = NULL;
  g_ap01_ui_saver_day = NULL;
  g_ap01_ui_saver_weekday = NULL;
  g_ap01_ui_saver_temperature = NULL;
  for (unsigned int color = 0; color < 2; ++color)
    {
      g_ap01_ui_saver_dot[color] = NULL;
      g_ap01_ui_saver_watt[color] = NULL;
      for (unsigned int digit = 0; digit < 4; ++digit)
        g_ap01_ui_saver_digit[color][digit] = NULL;
    }
}

static void ap01_ui_guide_log(void)
{
  printf("GUIDE stage=0x%02x page=%u option=%u source=%s completed=%u\n",
    g_ap01_ui_guide_stage, g_ap01_ui_guide_page, g_ap01_ui_option,
    g_ap01_ui_guide_mijia ? "mijia" : "settings",
    g_ap01_sim.settings.guide_completed ? 1 : 0);
}

static void ap01_ui_guide_set_stage(unsigned int stage)
{
  g_ap01_ui_guide_stage = stage;
  g_ap01_ui_guide_page = stage - 0x25;
  g_ap01_ui_option = 1;
  g_ap01_ui_guide_transition = lv_tick_get();
  g_ap01_ui_guide_save_error = false;
  ap01_ui_guide_log();
}

static void ap01_ui_guide_open(bool source_is_mijia)
{
  g_ap01_ui_guide_active = true;
  g_ap01_ui_guide_mijia = source_is_mijia;
  ap01_ui_guide_set_stage(0x25);
}

static bool ap01_ui_guide_finish(void)
{
  bool old = g_ap01_sim.settings.guide_completed;
  g_ap01_sim.settings.guide_completed = true;
  if (!ap01_sim_save())
    {
      g_ap01_sim.settings.guide_completed = old;
      g_ap01_ui_guide_save_error = true;
      if (g_ap01_ui_guide_error != NULL)
        lv_label_set_text(g_ap01_ui_guide_error, "保存失败，单击重试");
      printf("GUIDE result=error stage=persistence action=retry completed=%u\n",
              old ? 1 : 0);
      return false;
    }
  g_ap01_ui_guide_active = false;
  printf("GUIDE result=completed persisted=1 source=%s\n",
          g_ap01_ui_guide_mijia ? "mijia" : "settings");
  return true;
}

static void ap01_ui_guide_turn(int direction)
{
  if (direction == 0) return;
  if (g_ap01_ui_guide_stage <= 0x27)
    {
      if (direction > 0) g_ap01_ui_option = 1;
      else g_ap01_ui_option = 0;
    }
  else if (g_ap01_ui_guide_stage == 0x28)
    {
      /* Either native encoder key completes the first practice task. */
      ap01_ui_guide_set_stage(0x29);
      return;
    }
  ap01_ui_guide_log();
}

static bool ap01_ui_guide_press(void)
{
  switch (g_ap01_ui_guide_stage)
    {
      case 0x25:
        /* Native Skip skips the two explanatory panels, NOT practice. */
        ap01_ui_guide_set_stage(g_ap01_ui_option == 0 ? 0x27 : 0x26);
        break;
      case 0x26:
        ap01_ui_guide_set_stage(g_ap01_ui_option == 0 ? 0x25 : 0x27);
        break;
      case 0x27:
        if (g_ap01_ui_option == 0) return ap01_ui_guide_finish();
        ap01_ui_guide_set_stage(0x28);
        break;
      case 0x28:
        /* Native state 0x28 waits specifically for rotation. */
        ap01_ui_guide_log();
        break;
      case 0x29:
      case 0x2a:
      case 0x2b:
        ap01_ui_guide_set_stage(g_ap01_ui_guide_stage + 1);
        break;
      case 0x2c:
        return ap01_ui_guide_finish();
      default:
        break;
    }
  return false;
}

static bool ap01_ui_guide_back(void)
{
  /* Escape is the SIM's explicit cancel. Preserve completion on cancellation;
   * the native encoder has no separate Escape key. */
  g_ap01_ui_guide_active = false;
  printf("GUIDE result=cancelled completed=%u source=%s\n",
    g_ap01_sim.settings.guide_completed ? 1 : 0,
    g_ap01_ui_guide_mijia ? "mijia" : "settings");
  return true;
}

static void ap01_ui_guide_button(const char *text, int x, bool focused)
{
  lv_obj_t *button = ap01_ui_page_image(g_ap01_ui_root,
    &ap01_guide_button, x, 192);
  lv_obj_set_style_image_recolor(button,
    lv_color_hex(focused ? 0x22363d : 0x262626), LV_PART_MAIN);
  lv_obj_set_style_image_recolor_opa(button, LV_OPA_COVER, LV_PART_MAIN);
  lv_obj_t *label = ap01_ui_label(button, text, 0, 0,
    lv_color_hex(focused ? 0x89d8f3 : 0xffffff), &ap01_rom_body20);
  lv_obj_center(label);
}

static lv_obj_t *ap01_ui_guide_centered(lv_obj_t *parent, const char *text,
  int x, int y, int width, const lv_font_t *font)
{
  lv_obj_t *label = ap01_ui_label(parent, text, x, y,
    lv_color_hex(0xffffff), font);
  lv_obj_set_width(label, width);
  lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
  return label;
}

static void ap01_ui_guide_tick(void)
{
  if (!g_ap01_ui_guide_active || g_ap01_ui_guide_stage < 0x28 ||
      g_ap01_ui_guide_background == NULL ||
      g_ap01_ui_guide_overlay == NULL) return;
  bool ready = lv_tick_elaps(g_ap01_ui_guide_transition) >= 500;
  /* a00ec490 after 500ms sets native image recolor opacity 0x59 and black
   * recolor; the task overlays then become visible. These PNGs are static,
   * not 89-frame animations. The saver GIFs below are actual ROM animations. */
  lv_obj_set_style_image_recolor(g_ap01_ui_guide_background,
                                 lv_color_hex(0x000000), LV_PART_MAIN);
  lv_obj_set_style_image_recolor_opa(g_ap01_ui_guide_background,
                                    ready ? 89 : 0, LV_PART_MAIN);
  if (ready) lv_obj_remove_flag(g_ap01_ui_guide_overlay, LV_OBJ_FLAG_HIDDEN);
  else lv_obj_add_flag(g_ap01_ui_guide_overlay, LV_OBJ_FLAG_HIDDEN);
}

static void ap01_ui_guide_draw(void)
{
  unsigned int stage = g_ap01_ui_guide_stage;
  if (stage <= 0x26)
    {
      ap01_ui_page_image(g_ap01_ui_root,
        stage == 0x25 ? &ap01_guide_turn : &ap01_guide_press, 0, 0);
      ap01_ui_label(g_ap01_ui_root,
        stage == 0x25 ? "旋转旋钮" : "单击旋钮", 27, 66,
        lv_color_hex(0xffffff), &ap01_rom_guide_title);
      ap01_ui_label(g_ap01_ui_root,
        stage == 0x25 ? "在各个画面或选项\n之间进行切换" :
                        "进入当前页面，\n或选定当前选项",
        27, 104, lv_color_hex(0xffffff), &ap01_rom_guide_text);
      ap01_ui_guide_button(stage == 0x25 ? "跳过" : "上一步", 14,
                            g_ap01_ui_option == 0);
      ap01_ui_guide_button("下一步", 224, g_ap01_ui_option == 1);
      for (unsigned int i = 0; i < 2; ++i)
        ap01_ui_page_panel(g_ap01_ui_root, 8, 8, LV_RADIUS_CIRCLE,
          i == stage - 0x25 ? 0x89d8f3 : 0x4d4d4d, 294, 14 + i * 13);
    }
  else if (stage == 0x27)
    {
      /* Complete creator continuation a01b165c..18ae recovered directly
       * with local GNU objdump after Ghidra's false memcpy noreturn. */
      ap01_ui_guide_centered(g_ap01_ui_root, "欢迎使用", 0, 30, 320,
        &ap01_rom_guide_welcome);
      ap01_ui_guide_centered(g_ap01_ui_root,
        "下面我们将通过3个简单的小任务\n帮助您快速掌握基本操作。",
        37, 74, 245, &ap01_rom_forecast);
      ap01_ui_guide_button("跳过", 14, g_ap01_ui_option == 0);
      ap01_ui_guide_button("开始", 224, g_ap01_ui_option == 1);
    }
  else
    {
      const lv_image_dsc_t *background = &ap01_guide_practice_intro;
      const lv_image_dsc_t *bubble = &ap01_guide_bubble70;
      if (stage == 0x29) background = &ap01_guide_practice_turn_done;
      if (stage == 0x2b) background = &ap01_guide_practice_power;
      if (stage == 0x2c) background = &ap01_guide_practice_c1_done;
      g_ap01_ui_guide_background = ap01_ui_page_image(g_ap01_ui_root,
        background, 0, 0);
      g_ap01_ui_guide_overlay = ap01_ui_page_panel(g_ap01_ui_root,
        320, 240, 0, 0, 0, 0);
      lv_obj_set_style_bg_opa(g_ap01_ui_guide_overlay, LV_OPA_TRANSP,
                              LV_PART_MAIN);
      if (stage == 0x28) bubble = &ap01_guide_bubble50;
      if (stage == 0x29 || stage == 0x2c) bubble = &ap01_guide_bubble90;
      ap01_ui_page_image(g_ap01_ui_guide_overlay, bubble, 36, 7);
      if (stage == 0x28)
        ap01_ui_guide_centered(g_ap01_ui_guide_overlay,
          "1/2 请尝试旋转旋钮", 36, 22, 248, &ap01_rom_charge_title);
      else if (stage == 0x2a || stage == 0x2b)
        ap01_ui_guide_centered(g_ap01_ui_guide_overlay,
          stage == 0x2a ? "2/2 请尝试单击旋钮进入\n功率展示界面" :
                          "2/2 请尝试单击旋钮进入\nC1接口",
          70, 23, 180, &ap01_rom_charge_title);
      else
        {
          ap01_ui_guide_centered(g_ap01_ui_guide_overlay,
            stage == 0x29 ? "完成！左右旋转旋钮可以切换\n功率、时间、日期、天气等界面" :
                            "很棒！单击旋钮可以进行确认\n和进入界面等操作",
            stage == 0x29 ? 54 : 65, 22,
            stage == 0x29 ? 212 : 190, &ap01_rom_guide_practice_body);
          ap01_ui_guide_centered(g_ap01_ui_guide_overlay,
            stage == 0x29 ? "单击进入下一步" : "单击完成观看", 36, 72,
            248, &ap01_rom_guide_prompt);
        }
      ap01_ui_guide_tick();
    }
  g_ap01_ui_guide_error = ap01_ui_guide_centered(g_ap01_ui_root,
    g_ap01_ui_guide_save_error ? "保存失败，单击重试" : "", 10, 166, 300,
    &ap01_rom_body20);
  lv_obj_set_style_text_color(g_ap01_ui_guide_error,
    lv_color_hex(0xff7a00), LV_PART_MAIN);
  ap01_ui_page_sim_badge();
}

static bool ap01_ui_boot_active(void)
{
  return g_ap01_ui_boot_running;
}

static void ap01_ui_boot_open(void)
{
  g_ap01_ui_boot_running = true;
  g_ap01_ui_boot_start = lv_tick_get();
  printf("BOOT stage=logo native_page=0x24\n");
}

static void ap01_ui_boot_draw(void)
{
  /* Native boot creator a005edee..ee96: black 320x240, static 143x22 logo
   * at(88,109). The application polls readiness at1Hz; its no-device branch
   * uses two polls before revealing the initialized application. */
  ap01_ui_page_image(g_ap01_ui_root, &ap01_boot_logo, 88, 109);
  ap01_ui_page_sim_badge();
}

static bool ap01_ui_boot_tick(void)
{
  if (!g_ap01_ui_boot_running || lv_tick_elaps(g_ap01_ui_boot_start) < 2000)
    return false;
  g_ap01_ui_boot_running = false;
  g_ap01_ui_saver_last_input = lv_tick_get();
  g_ap01_ui_saver_initialized = true;
  printf("BOOT stage=ready elapsed_ms=%u guide_completed=%u\n",
    (unsigned int)lv_tick_elaps(g_ap01_ui_boot_start),
    g_ap01_sim.settings.guide_completed ? 1 : 0);
  return true;
}

static bool ap01_ui_boot_skip(void)
{
  /* Native boot has no key handler. Consume input until readiness rather
   * than applying a premature click to the application underneath it. */
  if (g_ap01_ui_boot_running)
    printf("BOOT input=consumed stage=initializing\n");
  return g_ap01_ui_boot_running;
}

static bool ap01_ui_saver_active(void)
{
  return g_ap01_ui_saver_kind != 0;
}

static bool ap01_ui_saver_activity(void)
{
  bool woke = ap01_ui_saver_active();
  g_ap01_ui_saver_last_input = lv_tick_get();
  g_ap01_ui_saver_initialized = true;
  if (woke)
    {
      printf("SAVER wake kind=%u input=consumed\n", g_ap01_ui_saver_kind);
      g_ap01_ui_saver_kind = 0;
      g_ap01_ui_saver_clock = NULL;
      g_ap01_ui_saver_period = NULL;
    }
  return woke;
}

static void ap01_ui_saver_clock_update(void)
{
  struct tm now;
  char value[16];
  if (g_ap01_ui_saver_clock == NULL || !ap01_ui_now(&now)) return;
  strftime(value, sizeof(value), g_ap01_ui_12_hour ? "%I:%M" : "%H:%M", &now);
  lv_label_set_text(g_ap01_ui_saver_clock, value);
  if (g_ap01_ui_saver_period != NULL)
    lv_label_set_text(g_ap01_ui_saver_period,
      g_ap01_ui_12_hour ? (now.tm_hour < 12 ? "上午" : "下午") : "");
  if (g_ap01_ui_saver_date != NULL)
    {
      snprintf(value, sizeof(value), "%02d/%02d", now.tm_mon + 1, now.tm_mday);
      lv_label_set_text(g_ap01_ui_saver_date, value);
    }
  if (g_ap01_ui_saver_day != NULL)
    {
      static const char *const weekdays[] =
        {"周日", "周一", "周二", "周三", "周四", "周五", "周六"};
      snprintf(value, sizeof(value), "%02d", now.tm_mday);
      lv_label_set_text(g_ap01_ui_saver_day, value);
      lv_label_set_text(g_ap01_ui_saver_weekday, weekdays[now.tm_wday]);
    }
  if (g_ap01_ui_saver_temperature != NULL)
    {
      snprintf(value, sizeof(value), "%d", g_ap01_sim.charger_temperature);
      lv_label_set_text(g_ap01_ui_saver_temperature, value);
    }
}

static void ap01_ui_saver_gif(const lv_image_dsc_t *source)
{
#if defined(LV_USE_GIF) && LV_USE_GIF
  lv_obj_t *gif = lv_gif_create(g_ap01_ui_root);
  lv_gif_set_src(gif, source);
  lv_obj_set_pos(gif, 0, 0);
#else
  /* Build configuration is required to enable the native GIF decoder. */
  (void)source;
#endif
}

static void ap01_ui_saver_power_row(unsigned int milliwatts,
                                    unsigned int color, int y)
{
  unsigned int value = milliwatts / 100;
  unsigned int digits[] = {value / 1000 % 10, value / 100 % 10,
                           value / 10 % 10, value % 10};
  /* The native four-slot row handles XX.X; keep the recovered sprites and
   * add a hundreds digit when the controlled charger exceeds99.9W. Root
   * ports are bounded to4x120W, so this covers the complete service range. */
  unsigned int first = value >= 1000 ? 0 : 1;
  int width = ap01_saver_dot[color].header.w + 28;
  for (unsigned int i = first; i < 4; ++i)
    width += ap01_saver_digits[color][digits[i]].header.w + 4;
  int x = (320 - width) / 2;
  for (unsigned int i = 0; i < 4; ++i)
    {
      lv_obj_t **digit = &g_ap01_ui_saver_digit[color][i];
      if (*digit == NULL) *digit = lv_image_create(g_ap01_ui_root);
      if (i < first)
        {
          lv_obj_add_flag(*digit, LV_OBJ_FLAG_HIDDEN);
          continue;
        }
      lv_obj_remove_flag(*digit, LV_OBJ_FLAG_HIDDEN);
      if (i == 3)
        {
          if (g_ap01_ui_saver_dot[color] == NULL)
            g_ap01_ui_saver_dot[color] = ap01_ui_page_image(g_ap01_ui_root,
              &ap01_saver_dot[color], x, y);
          lv_obj_set_pos(g_ap01_ui_saver_dot[color], x, y);
          x += ap01_saver_dot[color].header.w + 4;
        }
      lv_image_set_src(*digit, &ap01_saver_digits[color][digits[i]]);
      lv_obj_set_pos(*digit, x, y);
      x += ap01_saver_digits[color][digits[i]].header.w + 4;
    }
  if (g_ap01_ui_saver_watt[color] == NULL)
    g_ap01_ui_saver_watt[color] = ap01_ui_page_image(g_ap01_ui_root,
      &ap01_saver_watt[color], x + 6, y + 13);
  lv_obj_set_pos(g_ap01_ui_saver_watt[color], x + 6, y + 13);
}

static void ap01_ui_saver_power_update(void)
{
  unsigned int power[2] = {0, 0};
  for (unsigned int port = 0; port < AP01_SIM_PORTS; ++port)
    {
      const ap01_sim_port_t *item = &g_ap01_sim.ports[port];
      power[item->input ? 0 : 1] += ap01_ui_charge_milliwatts(item);
    }
  ap01_ui_saver_power_row(power[0], 0, 115);
  ap01_ui_saver_power_row(power[1], 1, 167);
}

static bool ap01_ui_saver_force(unsigned int mode)
{
  if (mode < 1 || mode > 3)
    {
      printf("SAVER result=error stage=validation action=select-mode-1-to-3\n");
      return false;
    }
  g_ap01_ui_saver_kind = mode;
  g_ap01_ui_saver_variant ^= 1;
  g_ap01_ui_saver_last_input = lv_tick_get();
  g_ap01_ui_saver_initialized = true;
  printf("SAVER active kind=%u native_page=0x%02x variant=%u\n",
    mode, mode == 1 ? 0x2d : (mode == 2 ? 0x2f : 0),
    g_ap01_ui_saver_variant);
  return true;
}

static void ap01_ui_saver_draw(void)
{
  if (g_ap01_ui_saver_kind == 3) return; /* Native screen-off mode. */
  if (g_ap01_ui_saver_kind == 1)
    {
      bool connected = g_ap01_sim.charger_connected;
      ap01_ui_page_image(g_ap01_ui_root, &ap01_saver_glow_top, 0, 2);
      ap01_ui_page_image(g_ap01_ui_root, &ap01_saver_glow_bottom, 0, 61);
      ap01_ui_page_image(g_ap01_ui_root, &ap01_saver_curve, 25, 38);
      if (connected)
        {
          ap01_ui_saver_power_update();
          ap01_ui_page_image(g_ap01_ui_root, &ap01_saver_fast, 130, 25);
        }
      else
        {
          ap01_ui_saver_gif(&ap01_saver_power);
          ap01_ui_guide_centered(g_ap01_ui_root, "0.0", 96, 103, 100,
            &ap01_rom_saver_decimal);
          ap01_ui_label(g_ap01_ui_root, "W", 201, 109,
            lv_color_hex(0xffffff), &ap01_rom_saver_watt);
        }
      g_ap01_ui_saver_clock = ap01_ui_label(g_ap01_ui_root, "", 22, 215,
        lv_color_hex(0xffffff), &ap01_rom_clock21);
      g_ap01_ui_saver_date = ap01_ui_label(g_ap01_ui_root, "", 218, 216,
        lv_color_hex(0xffffff), &ap01_rom_charge_title);
      lv_obj_set_width(g_ap01_ui_saver_date, 80);
      lv_obj_set_style_text_align(g_ap01_ui_saver_date, LV_TEXT_ALIGN_RIGHT,
                                  LV_PART_MAIN);
    }
  else
    {
      bool connected = g_ap01_sim.charger_connected;
      ap01_ui_saver_gif(&ap01_saver_time[g_ap01_ui_saver_variant]);
      g_ap01_ui_saver_clock = ap01_ui_guide_centered(g_ap01_ui_root, "",
        connected ? 204 : 110, 25, 100, &ap01_rom_saver_time);
      g_ap01_ui_saver_period = ap01_ui_label(g_ap01_ui_root, "",
        connected ? 170 : 79, 31,
        lv_color_hex(0xffffff), &ap01_rom_forecast);
      if (connected)
        {
          char value[16];
          lv_obj_t *date = ap01_ui_page_panel(g_ap01_ui_root,
            58, 58, LV_RADIUS_CIRCLE, 0x262626, 18, 12);
          g_ap01_ui_saver_weekday = ap01_ui_guide_centered(date, "", 0, 12,
            58, &ap01_rom_mini_date);
          g_ap01_ui_saver_day = ap01_ui_guide_centered(date, "", 0, 34, 58,
            &ap01_rom_saver_day);
          ap01_ui_page_image(g_ap01_ui_root, &ap01_arc, 86, 12);
          snprintf(value, sizeof(value), "%d", g_ap01_sim.charger_temperature);
          g_ap01_ui_saver_temperature = ap01_ui_guide_centered(
            g_ap01_ui_root, value, 86, 29, 58, &ap01_rom_mini_date);
          ap01_ui_page_image(g_ap01_ui_root, &ap01_saver_thermometer, 106, 52);
        }
    }
  g_ap01_ui_saver_seen_revision = g_ap01_sim.revision;
  g_ap01_ui_saver_connected = g_ap01_sim.charger_connected;
  ap01_ui_saver_clock_update();
  ap01_ui_page_sim_badge();
}

static bool ap01_ui_saver_tick(void)
{
  if (!g_ap01_ui_saver_initialized) ap01_ui_saver_activity();
  if (ap01_ui_saver_active())
    {
      if (!g_ap01_sim.settings.enabled[0] &&
          g_ap01_sim.settings.blank_seconds != 0 &&
          g_ap01_ui_saver_kind != 3 &&
          lv_tick_elaps(g_ap01_ui_saver_last_input) / 1000 >=
            g_ap01_sim.settings.blank_seconds)
        {
          g_ap01_ui_saver_kind = 3;
          printf("SAVER active kind=3 native_page=0x00 source=screen-off\n");
          return true;
        }
      if (g_ap01_ui_saver_kind != 3 && !g_ap01_sim.settings.enabled[1])
        {
          ap01_ui_saver_activity();
          return true;
        }
      ap01_ui_saver_clock_update();
      if (g_ap01_ui_saver_kind != 3 &&
          g_ap01_ui_saver_connected != g_ap01_sim.charger_connected)
        return true;
      if (g_ap01_ui_saver_kind == 1 && g_ap01_ui_saver_connected &&
          g_ap01_ui_saver_seen_revision != g_ap01_sim.revision)
        ap01_ui_saver_power_update();
      g_ap01_ui_saver_seen_revision = g_ap01_sim.revision;
      return false;
    }
  if (g_ap01_ui_boot_running || g_ap01_ui_guide_active ||
      g_ap01_sim.ota == AP01_SIM_PENDING ||
      g_ap01_sim.binding == AP01_SIM_PENDING ||
      (!g_ap01_sim.settings.enabled[1] && g_ap01_sim.settings.enabled[0]))
    return false;
  unsigned int elapsed = lv_tick_elaps(g_ap01_ui_saver_last_input) / 1000;
  unsigned int seconds = g_ap01_sim.settings.saver_seconds;
  if (!g_ap01_sim.settings.enabled[0] &&
      g_ap01_sim.settings.blank_seconds != 0 &&
      elapsed >= g_ap01_sim.settings.blank_seconds)
    {
      printf("SAVER idle_seconds=%u source=screen-off\n", elapsed);
      return ap01_ui_saver_force(3);
    }
  if (!g_ap01_sim.settings.enabled[1]) return false;
  if (seconds == 0 || lv_tick_elaps(g_ap01_ui_saver_last_input) / 1000 < seconds)
    return false;
  printf("SAVER idle_seconds=%u source=screen-save\n", elapsed);
  uint32_t last_input = g_ap01_ui_saver_last_input;
  bool activated = ap01_ui_saver_force(g_ap01_sim.settings.saver_mode);
  /* Activation is not user activity: retain the original idle epoch so a
   * later screen-off deadline still expires from the last physical input. */
  g_ap01_ui_saver_last_input = last_input;
  return activated;
}

#endif
