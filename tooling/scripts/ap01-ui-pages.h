/* SPDX-License-Identifier: Apache-2.0 */
/*
 * AP01 0041 page reconstruction.
 *
 * The panel, image, and footer coordinates marked "observed" come from the
 * bounded creator blocks in 0041-ghidra-pass3.txt. Circular gauge internals,
 * and graph grid are photo-guided reconstructions. The mini calendar uses
 * the ROM button-matrix map, native padding/gaps and its geometry engine.
 */

static lv_obj_t *g_ap01_ui_pages_weather_date;
static lv_obj_t *g_ap01_ui_pages_weather_weekday;
static lv_obj_t *g_ap01_ui_pages_weather_clock;
static lv_obj_t *g_ap01_ui_pages_date_month;
static lv_obj_t *g_ap01_ui_pages_date_year;
static lv_obj_t *g_ap01_ui_pages_date_clock;
static lv_obj_t *g_ap01_ui_pages_time_weekday;
static lv_obj_t *g_ap01_ui_pages_time_day;
static lv_obj_t *g_ap01_ui_pages_calendar_matrix;
static char g_ap01_ui_pages_calendar_days[35][4];
static const char *g_ap01_ui_pages_calendar_map[49];
static int g_ap01_ui_pages_calendar_year = -1;
static int g_ap01_ui_pages_calendar_month = -1;
static int g_ap01_ui_pages_calendar_day = -1;
static unsigned int g_ap01_ui_pages_seen_revision;
static bool g_ap01_ui_pages_changed;
static unsigned int ap01_ui_weather_night(void);
static int g_ap01_ui_pages_weather_day = -1;
static int g_ap01_ui_pages_weather_night = -1;
static void ap01_ui_calendar_log_date(int year, int month, int day,
                                       const char *view);

static bool ap01_ui_weather_has_data(void)
{
  return g_ap01_sim.weather.status == AP01_SIM_OK;
}

static unsigned int ap01_ui_weather_code(int legacy, unsigned int native_code)
{
  static const unsigned int codes[] = {100, 101, 300};
  return native_code != 0 ? native_code :
    legacy >= 0 && legacy < 3 ? codes[legacy] : 999;
}

static const char *ap01_ui_weather_condition_name(unsigned int code)
{
  /* Exact a00a6d34 switch; unsupported codes retain the native 未知. */
  switch (code)
    {
      case 100: case 150: return "晴";
      case 101: case 151: return "多云";
      case 102: case 152: return "少云";
      case 103: case 153: return "晴间多云";
      case 104: return "阴";
      case 300: case 350: return "阵雨";
      case 301: case 351: return "强阵雨";
      case 302: case 303: case 304: return "雷阵雨";
      case 305: return "小雨";
      case 306: return "中雨";
      case 307: return "大雨";
      case 308: return "极端降雨";
      case 309: return "细雨";
      case 310: case 317: return "暴雨";
      case 311: case 318: return "大暴雨";
      case 312: return "特大暴雨";
      case 313: return "冻雨";
      case 314: return "小到中雨";
      case 315: return "中到大雨";
      case 316: return "大到暴雨";
      case 399: return "雨";
      case 400: return "小雪";
      case 401: return "中雪";
      case 402: return "大雪";
      case 403: return "暴雪";
      case 404: return "雨夹雪";
      case 405: return "雨雪天气";
      case 406: case 456: return "阵雨夹雪";
      case 407: case 457: return "阵雪";
      case 408: return "小到中雪";
      case 409: return "中到大雪";
      case 410: return "大到暴雪";
      case 499: return "雪";
      case 500: return "薄雾";
      case 501: return "雾";
      case 502: return "霾";
      case 503: return "扬沙";
      case 504: return "浮尘";
      case 507: return "沙尘暴";
      case 508: return "强沙尘暴";
      case 509: return "浓雾";
      case 510: return "强浓雾";
      case 511: return "中度霾";
      case 512: return "重度霾";
      case 513: return "严重霾";
      case 514: return "大雾";
      case 515: return "特强浓雾";
      case 900: return "热";
      case 901: return "冷";
      default: return "未知";
    }
}

static unsigned int ap01_ui_weather_icon_index(unsigned int code,
                                               bool night, bool forecast)
{
  /* a00a6998 current conditions; a00a6afa future forecasts preserve the
   * explicit 150/350 night variants instead of using today's clock. */
  if (code == 104) return 6;
  if (code == 100 || code == 150)
    return 1 + (forecast ? code == 150 : night);
  if ((code >= 101 && code <= 103) || (code >= 151 && code <= 153))
    return 3 + (forecast ? code >= 151 : night);
  if (code >= 305 && code <= 318) return 7;
  if (code == 300 || code == 301 || code == 350 || code == 351)
    return 8 + (forecast ? code >= 350 : night);
  if (code >= 302 && code <= 304) return 11;
  if (code == 399) return 7;
  if (code == 404 || code == 406 || code == 456) return 13;
  if ((code >= 400 && code <= 410) || code == 457 || code == 499) return 12;
  if (code >= 500 && code <= 515) return 14;
  return 15;
}

static const lv_image_dsc_t *ap01_ui_weather_icon(unsigned int code,
                                                 bool small, bool forecast)
{
  unsigned int index = ap01_ui_weather_icon_index(code,
    ap01_ui_weather_night() != 0, forecast);
  return small ? ap01_weather_small[index] : ap01_weather_large[index];
}

static const char *ap01_ui_weather_status_text(void)
{
  switch (g_ap01_sim.weather.status)
    {
      case AP01_SIM_PENDING: return "正在获取天气...";
      case AP01_SIM_ERROR: return "获取失败，按R重试";
      case AP01_SIM_TIMEOUT: return "获取超时，按R重试";
      case AP01_SIM_OK: return "";
      default: return g_ap01_sim.wifi_connected ? "按R获取天气" : "未连接网络";
    }
}

static unsigned int ap01_ui_weather_night(void)
{
  struct tm now;
  if (!ap01_ui_now(&now)) return 0;
  unsigned int minute = now.tm_hour * 60 + now.tm_min;
  return minute < g_ap01_sim.weather.sunrise_minutes ||
         minute >= g_ap01_sim.weather.sunset_minutes;
}

static bool ap01_ui_weather_retry(void)
{
  if (g_ap01_ui_page != AP01_UI_WEATHER) return false;
  bool accepted = ap01_sim_weather_refresh();
  g_ap01_ui_pages_changed = true;
  printf("WEATHER refresh accepted=%u status=%u stage=%s action=%s\n",
    accepted ? 1 : 0, g_ap01_sim.weather.status,
    accepted ? "fetch" : g_ap01_sim.reply.stage,
    accepted ? "wait" : g_ap01_sim.reply.action_hint);
  return true;
}

static lv_obj_t *ap01_ui_page_panel(lv_obj_t *parent, int32_t width,
                                    int32_t height, int32_t radius,
                                    uint32_t color, int32_t x, int32_t y)
{
  /* Direct a00a6392 panel helper shape: parent,w,h,radius,bg,x,y. */
  lv_obj_t *panel = lv_obj_create(parent);
  lv_obj_set_size(panel, width, height);
  lv_obj_set_pos(panel, x, y);
  lv_obj_set_style_radius(panel, radius, LV_PART_MAIN);
  lv_obj_set_style_bg_color(panel, lv_color_hex(color), LV_PART_MAIN);
  lv_obj_set_style_bg_opa(panel, LV_OPA_COVER, LV_PART_MAIN);
  lv_obj_set_style_border_width(panel, 0, LV_PART_MAIN);
  lv_obj_set_style_pad_all(panel, 0, LV_PART_MAIN);
  lv_obj_remove_flag(panel, LV_OBJ_FLAG_SCROLLABLE);
  return panel;
}
static lv_obj_t *ap01_ui_page_image(lv_obj_t *parent,
                                    const lv_image_dsc_t *source,
                                    int32_t x, int32_t y)
{
  lv_obj_t *image = lv_image_create(parent);
  lv_image_set_src(image, source);
  lv_obj_set_pos(image, x, y);
  return image;
}

static void ap01_ui_page_sim_badge(void)
{
  /* SIM provenance belongs in the host window/log, outside native canvas. */
}

static bool ap01_ui_pages_now(struct tm *local_time)
{
  return ap01_ui_now(local_time);
}

static void ap01_ui_pages_reset(void)
{
  g_ap01_ui_pages_weather_date = NULL;
  g_ap01_ui_pages_weather_weekday = NULL;
  g_ap01_ui_pages_weather_clock = NULL;
  g_ap01_ui_pages_date_month = NULL;
  g_ap01_ui_pages_date_year = NULL;
  g_ap01_ui_pages_date_clock = NULL;
  g_ap01_ui_pages_time_weekday = NULL;
  g_ap01_ui_pages_time_day = NULL;
  g_ap01_ui_pages_calendar_matrix = NULL;
  g_ap01_ui_pages_calendar_year = -1;
  g_ap01_ui_pages_calendar_month = -1;
  g_ap01_ui_pages_calendar_day = -1;
  g_ap01_ui_pages_seen_revision = g_ap01_sim.revision;
  g_ap01_ui_pages_changed = false;
}

static int ap01_ui_pages_days_in_month(int year, int month)
{
  static const int days[] = {31, 28, 31, 30, 31, 30,
                             31, 31, 30, 31, 30, 31};
  if (month == 2 && (year % 4 == 0 &&
                     (year % 100 != 0 || year % 400 == 0)))
    {
      return 29;
    }
  return days[month - 1];
}

static void ap01_ui_pages_calendar_draw(lv_event_t *event)
{
  lv_draw_task_t *task = lv_event_get_draw_task(event);
  lv_draw_dsc_base_t *base = (lv_draw_dsc_base_t *)lv_draw_task_get_draw_dsc(task);
  if (base == NULL || base->part != LV_PART_ITEMS) return;
  unsigned int index = base->id1;
  if (lv_draw_task_get_type(task) == LV_DRAW_TASK_TYPE_LABEL)
    {
      lv_draw_label_dsc_t *label = (lv_draw_label_dsc_t *)base;
      bool selected = lv_buttonmatrix_has_button_ctrl(g_ap01_ui_pages_calendar_matrix,
        index, LV_BUTTONMATRIX_CTRL_CHECKED);
      bool adjacent = lv_buttonmatrix_has_button_ctrl(g_ap01_ui_pages_calendar_matrix,
        index, LV_BUTTONMATRIX_CTRL_CUSTOM_1);
      if (index < 7)
        {
          int old_width = lv_text_get_width(label->text, (uint32_t)strlen(label->text),
            label->font, label->letter_space);
          int new_width = lv_text_get_width(label->text, (uint32_t)strlen(label->text),
            &ap01_rom_calendar_week, 2);
          label->ofs_x += (old_width - new_width) / 2;
          label->ofs_y += ((int)label->font->line_height -
            (int)ap01_rom_calendar_week.line_height) / 2;
        }
      label->font = index < 7 ? &ap01_rom_calendar_week : &ap01_rom_year;
      label->letter_space = 2;
      label->opa = adjacent ? LV_OPA_40 : LV_OPA_COVER;
      label->color = lv_color_hex(selected ? 0 : index % 7 == 0 ||
        index % 7 == 6 ? 0x8e8d93 : 0xffffff);
    }
}

static void ap01_ui_pages_refresh_calendar(const struct tm *local_time)
{
  /* A03724D0 / A00F0E52 has seven weekday buttons +35 date buttons;
   * the final newline leaves the seventh row empty. Late sixth-week dates
   * are absent from the native mini overview, available in full detail. */
  int first_weekday;
  int days;
  unsigned int i;

  if (local_time == NULL || g_ap01_ui_pages_date_month == NULL ||
      g_ap01_ui_pages_date_year == NULL)
    {
      return;
    }

  if (g_ap01_ui_pages_calendar_year != local_time->tm_year + 1900 ||
      g_ap01_ui_pages_calendar_month != local_time->tm_mon + 1)
    {
      char year[16];
      static const char *const months[] =
        {"一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月",
         "九月", "十月", "十一月", "十二月"};

      snprintf(year, sizeof(year), "%04d", local_time->tm_year + 1900);
      lv_label_set_text(g_ap01_ui_pages_date_month, months[local_time->tm_mon]);
      lv_label_set_text(g_ap01_ui_pages_date_year, year);
      g_ap01_ui_pages_calendar_year = local_time->tm_year + 1900;
      g_ap01_ui_pages_calendar_month = local_time->tm_mon + 1;
    }

  first_weekday = (local_time->tm_wday -
                   (local_time->tm_mday - 1) % 7 + 7) % 7;
  days = ap01_ui_pages_days_in_month(local_time->tm_year + 1900,
                                     local_time->tm_mon + 1);
  int previous_month = local_time->tm_mon == 0 ? 12 : local_time->tm_mon;
  int previous_year = local_time->tm_year + 1900 - (local_time->tm_mon == 0);
  int previous_days = ap01_ui_pages_days_in_month(previous_year, previous_month);
  lv_buttonmatrix_clear_button_ctrl_all(g_ap01_ui_pages_calendar_matrix,
    LV_BUTTONMATRIX_CTRL_CHECKED | LV_BUTTONMATRIX_CTRL_CUSTOM_1);
  for (i = 0; i < 35; ++i)
    {
      int day = (int)i - first_weekday + 1;
      bool adjacent = day < 1 || day > days;
      int displayed = day < 1 ? day + previous_days : day > days ? day - days : day;
      snprintf(g_ap01_ui_pages_calendar_days[i], 4, "%d", displayed);
      if (adjacent)
        lv_buttonmatrix_set_button_ctrl(g_ap01_ui_pages_calendar_matrix, i + 7,
          LV_BUTTONMATRIX_CTRL_CUSTOM_1);
      else if (day == local_time->tm_mday)
        lv_buttonmatrix_set_button_ctrl(g_ap01_ui_pages_calendar_matrix, i + 7,
          LV_BUTTONMATRIX_CTRL_CHECKED);
    }
  lv_obj_invalidate(g_ap01_ui_pages_calendar_matrix);
  g_ap01_ui_pages_calendar_day = local_time->tm_mday;
  ap01_ui_calendar_log_date(local_time->tm_year + 1900, local_time->tm_mon + 1,
    local_time->tm_mday, "overview");
}

static void ap01_ui_pages_update_clock(void)
{
  struct tm local_time;
  char clock_text[8];
  char date_text[64];
  static const char *const weekdays[] =
    {"星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"};

  if (!ap01_ui_pages_now(&local_time))
    {
      snprintf(clock_text, sizeof(clock_text), "--:--");
      snprintf(date_text, sizeof(date_text), "----年--月--日");
      if (g_ap01_ui_pages_weather_weekday != NULL)
        lv_label_set_text(g_ap01_ui_pages_weather_weekday, "星期-");
    }
  else
    {
      strftime(clock_text, sizeof(clock_text), g_ap01_ui_12_hour ? "%I:%M" : "%H:%M", &local_time);
      snprintf(date_text, sizeof(date_text), "%04d年%d月%d日",
               local_time.tm_year + 1900, local_time.tm_mon + 1,
               local_time.tm_mday);
      if (g_ap01_ui_pages_weather_weekday != NULL)
        lv_label_set_text(g_ap01_ui_pages_weather_weekday,
                          weekdays[local_time.tm_wday]);
      if (g_ap01_ui_pages_time_weekday != NULL)
        {
          static const char *const short_weekdays[] =
            {"周日", "周一", "周二", "周三", "周四", "周五", "周六"};
          char day[4];
          snprintf(day, sizeof(day), "%02d", local_time.tm_mday);
          lv_label_set_text(g_ap01_ui_pages_time_weekday,
                            short_weekdays[local_time.tm_wday]);
          lv_label_set_text(g_ap01_ui_pages_time_day, day);
        }
    }
  if (g_ap01_ui_pages_weather_date != NULL)
    lv_label_set_text(g_ap01_ui_pages_weather_date, date_text);
  if (g_ap01_ui_pages_weather_clock != NULL)
    lv_label_set_text(g_ap01_ui_pages_weather_clock, clock_text);
  if (g_ap01_ui_pages_date_clock != NULL)
    lv_label_set_text(g_ap01_ui_pages_date_clock, clock_text);
  if (g_ap01_ui_pages_date_month != NULL &&
      ap01_ui_pages_now(&local_time))
    {
      if (g_ap01_ui_pages_calendar_year != local_time.tm_year + 1900 ||
          g_ap01_ui_pages_calendar_month != local_time.tm_mon + 1 ||
          g_ap01_ui_pages_calendar_day != local_time.tm_mday)
        {
          ap01_ui_pages_refresh_calendar(&local_time);
        }
    }
}

static void ap01_ui_pages_tick(void)
{
  struct tm now;
  if (g_ap01_ui_page == AP01_UI_WEATHER && ap01_ui_now(&now))
    {
      int day = now.tm_year * 366 + now.tm_yday;
      int night = (int)ap01_ui_weather_night();
      if (day != g_ap01_ui_pages_weather_day || night != g_ap01_ui_pages_weather_night)
        {
          g_ap01_ui_pages_changed = true;
          g_ap01_ui_pages_weather_day = day;
          g_ap01_ui_pages_weather_night = night;
        }
    }
  if ((g_ap01_ui_page == AP01_UI_TIME || g_ap01_ui_page == AP01_UI_WEATHER) &&
      g_ap01_ui_pages_seen_revision != g_ap01_sim.revision)
    {
      g_ap01_ui_pages_seen_revision = g_ap01_sim.revision;
      g_ap01_ui_pages_changed = true;
    }
  if (g_ap01_ui_pages_weather_date != NULL ||
      g_ap01_ui_pages_weather_clock != NULL ||
      g_ap01_ui_pages_date_month != NULL ||
      g_ap01_ui_pages_date_clock != NULL ||
      g_ap01_ui_pages_time_day != NULL)
    {
      ap01_ui_pages_update_clock();
    }
}

static void ap01_ui_page_footer(lv_obj_t **clock_label, int32_t clock_x)
{
  lv_obj_t *wifi;

  *clock_label = ap01_ui_label(g_ap01_ui_root, "--:--", clock_x, 213,
                               lv_color_hex(0xffffff), &ap01_rom_clock21);
  wifi = ap01_ui_page_image(g_ap01_ui_root,
                            g_ap01_sim.wifi_connected ? &ap01_wifi : &ap01_wifi_off,
                            278, 214);
  (void)wifi;
}

static lv_obj_t *ap01_ui_time_centered_label(lv_obj_t *parent,
                                             const char *text, int32_t y,
                                             uint32_t color,
                                             const lv_font_t *font)
{
  lv_obj_t *label = ap01_ui_label(parent, text, 0, y, lv_color_hex(color), font);
  lv_obj_set_width(label, 58);
  lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
  return label;
}

static void ap01_ui_time_arc(int32_t x, uint32_t color,
                              int32_t start, int32_t end)
{
  /* The ROM creator exposes slots/colors, not the gauge's internal drawing.
   * LVGL arcs reproduce the open-bottom rings. */
  lv_obj_t *arc = lv_arc_create(g_ap01_ui_root);
  lv_obj_set_size(arc, 58, 58);
  lv_obj_set_pos(arc, x, 12);
  lv_arc_set_rotation(arc, 135);
  lv_arc_set_bg_angles(arc, start, end);
  lv_obj_set_style_arc_color(arc, lv_color_hex(color), LV_PART_MAIN);
  lv_obj_set_style_arc_width(arc, 5, LV_PART_MAIN);
  lv_obj_set_style_arc_rounded(arc, true, LV_PART_MAIN);
  lv_obj_set_style_arc_color(arc, lv_color_hex(0x7ac5f4), LV_PART_INDICATOR);
  lv_obj_set_style_arc_width(arc, 5, LV_PART_INDICATOR);
  lv_arc_set_range(arc, 0, 100);
  unsigned int humidity = ap01_ui_weather_has_data() ? g_ap01_sim.weather.humidity : 0;
  lv_arc_set_value(arc, humidity > 100 ? 100 : (int)humidity);
  lv_obj_remove_style(arc, NULL, LV_PART_KNOB);
  lv_obj_remove_flag(arc, LV_OBJ_FLAG_CLICKABLE);
}

static void ap01_ui_draw_time_meters(void)
{
  char value_text[24];
  unsigned int milliwatts = 0;
  for (unsigned int port = 0; port < AP01_SIM_PORTS; ++port)
    if (!g_ap01_sim.ports[port].input)
      milliwatts += ap01_ui_charge_milliwatts(&g_ap01_sim.ports[port]);
  lv_obj_t *date = ap01_ui_page_panel(g_ap01_ui_root, 58, 58,
                                      LV_RADIUS_CIRCLE, 0x262626, 16, 12);
  lv_obj_t *power = ap01_ui_page_panel(g_ap01_ui_root, 58, 58,
                                       LV_RADIUS_CIRCLE, 0x262626, 87, 12);
  lv_obj_t *temperature;
  lv_obj_t *humidity;

  g_ap01_ui_pages_time_weekday = ap01_ui_time_centered_label(
    date, "周-", 8, 0x89d8f3, &ap01_rom_mini_week);
  g_ap01_ui_pages_time_day = ap01_ui_time_centered_label(
    date, "--", 27, 0xffffff, &ap01_rom_mini_date);
  if (g_ap01_sim.charger_connected)
    snprintf(value_text, sizeof(value_text), "%u", milliwatts / 1000);
  else snprintf(value_text, sizeof(value_text), "--");
  ap01_ui_time_centered_label(power, value_text, 10, 0xffffff,
                               &ap01_rom_mini_date);
  ap01_ui_time_centered_label(power, "W", 32, 0xffffff,
                               &ap01_rom_weather_text);

  /* Native 58x46 rainbow ring, file offset 0x62f440. */
  ap01_ui_page_image(g_ap01_ui_root, &ap01_arc, 158, 12);
  ap01_ui_time_arc(229, 0x253b49, 0, 270);
  temperature = ap01_ui_page_panel(g_ap01_ui_root, 48, 48,
                                    LV_RADIUS_CIRCLE, 0x000000, 163, 17);
  humidity = ap01_ui_page_panel(g_ap01_ui_root, 48, 48,
                                 LV_RADIUS_CIRCLE, 0x000000, 234, 17);
  /* Labels stay 58 wide to share the circle's center; their local x is -5. */
  snprintf(value_text, sizeof(value_text), "%d",
    ap01_ui_weather_has_data() ? g_ap01_sim.weather.temperature : 0);
  lv_obj_t *value = ap01_ui_time_centered_label(temperature, value_text, 10,
                                                0xffffff, &ap01_rom_clock21);
  lv_obj_set_x(value, -5);
  snprintf(value_text, sizeof(value_text), "%u%%",
    ap01_ui_weather_has_data() ? g_ap01_sim.weather.humidity : 0);
  value = ap01_ui_time_centered_label(humidity, value_text, 10,
                                      0xffffff, &ap01_rom_clock21);
  lv_obj_set_x(value, -5);
  /* a0198946: weather condition glyph, not a thermometer. Native15 hides it. */
  unsigned int index = ap01_ui_weather_icon_index(ap01_ui_weather_code(
    g_ap01_sim.weather.condition, g_ap01_sim.weather.native_code),
    ap01_ui_weather_night(), false);
  if (ap01_ui_weather_has_data() && ap01_weather_tiny[index] != NULL)
    ap01_ui_page_image(g_ap01_ui_root, ap01_weather_tiny[index], 177, 52);
  /* Native double-drop resource at file offset 0x252c14. */
  ap01_ui_page_image(g_ap01_ui_root, &ap01_time_humidity_icon, 248, 51);
  ap01_ui_page_image(g_ap01_ui_root,
                      g_ap01_sim.wifi_connected ? &ap01_wifi : &ap01_wifi_off,
                      292, 12);
}

static void ap01_ui_draw_time_power_graph(void)
{
  unsigned int i;
  /* Recovered native graph area; data is the shared local charger ring,
   * independent of the two external power-bank pages. */
  for (i = 0; i <= 8; ++i)
    ap01_ui_page_panel(g_ap01_ui_root, 1, 57, 0, 0x30343c,
                        116 + (int32_t)(i * 188 / 8), 168);
  for (i = 0; i < 38; ++i)
    ap01_ui_page_panel(g_ap01_ui_root, 3, 1, 0, 0x6d7785,
                        116 + (int32_t)i * 5, 225);
  if (g_ap01_sim.history_count == 0)
    {
      lv_obj_t *message = ap01_ui_label(g_ap01_ui_root, "Power  No Data",
                                     116, 185, lv_color_hex(0xffffff),
                                     &ap01_rom_ascii17);
      lv_obj_set_width(message, 188);
      lv_obj_set_style_text_align(message, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
      return;
    }
  static lv_point_precise_t points[AP01_SIM_HISTORY];
  unsigned int count = g_ap01_sim.history_count;
  if (count > AP01_SIM_HISTORY) count = AP01_SIM_HISTORY;
  unsigned int first = (g_ap01_sim.history_head + AP01_SIM_HISTORY - count) %
                         AP01_SIM_HISTORY;
  unsigned int maximum = 1000;
  for (i = 0; i < count; ++i)
    if (g_ap01_sim.history[(first + i) % AP01_SIM_HISTORY] > maximum)
      maximum = g_ap01_sim.history[(first + i) % AP01_SIM_HISTORY];
  for (i = 0; i < count; ++i)
    {
      unsigned int sample = g_ap01_sim.history[(first + i) % AP01_SIM_HISTORY];
      points[i].x = count == 1 ? 0 : i * 188 / (count - 1);
      points[i].y = 55 - (uint64_t)sample * 52 / maximum;
    }
  if (count == 1)
    {
      ap01_ui_page_panel(g_ap01_ui_root, 4, 4, LV_RADIUS_CIRCLE, 0xff7a00,
        114, 166 + (int)points[0].y);
      return;
    }
  lv_obj_t *line = lv_line_create(g_ap01_ui_root);
  lv_line_set_points(line, points, count);
  lv_obj_set_pos(line, 116, 168);
  lv_obj_set_style_line_color(line, lv_color_hex(0xff7a00), LV_PART_MAIN);
  lv_obj_set_style_line_width(line, 2, LV_PART_MAIN);
}

static void ap01_ui_draw_time_or_date(void)
{
  if (g_ap01_ui_page == AP01_UI_TIME)
    {
      unsigned int i;
      lv_obj_t *panel;

      /* time1 observes the 58px top circles, y90 digit container, and
       * 80x58 status card. Four 55x50 digits use the original ROM bitmaps. */
      ap01_ui_draw_time_meters();
      ap01_ui_page_sim_badge();
      panel = ap01_ui_page_panel(g_ap01_ui_root, 80, 58, 8, 0x262626, 20,
                                 169);
      const char *mode_text = g_ap01_sim.charger_connected ?
        (g_ap01_sim.settings.output_mode == 0 ? "AI\n智配" :
          g_ap01_ui_charge_modes[g_ap01_sim.settings.output_mode < 4 ?
            g_ap01_sim.settings.output_mode : 0]) :
        "未接入\n充电器";
      lv_obj_t *status = ap01_ui_label(panel, mode_text, 0, 12,
                                        lv_color_hex(0xffffff),
                                        &ap01_rom_weather_text);
      lv_obj_set_width(status, 80);
      lv_obj_set_style_text_align(status, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
      lv_obj_set_style_text_line_space(status, 1, LV_PART_MAIN);
      ap01_ui_draw_time_power_graph();
      for (i = 0; i < 4; ++i)
        {
          g_ap01_ui_clock_image[i] = lv_image_create(g_ap01_ui_root);
          lv_image_set_src(g_ap01_ui_clock_image[i], &ap01_digits[0]);
          lv_obj_set_pos(g_ap01_ui_clock_image[i],
                         i < 2 ? 20 + (int32_t)i * 63
                               : 181 + (int32_t)(i - 2) * 63,
                         90);
        }
      g_ap01_ui_clock_image[4] = lv_image_create(g_ap01_ui_root);
      lv_image_set_src(g_ap01_ui_clock_image[4], &ap01_colon);
      lv_obj_set_pos(g_ap01_ui_clock_image[4], 156, 101);
      ap01_ui_set_clock_text();
      ap01_ui_pages_update_clock();
      return;
    }

  {
    lv_obj_t *panel = ap01_ui_page_panel(g_ap01_ui_root, 276, 189, 16,
                                         0x1a1a1a, 22, 18);
    char year[16];
    struct tm local_time;
    bool have_time;
    static const char *const weekday_names[] =
      {"日", "一", "二", "三", "四", "五", "六"};

    ap01_ui_page_sim_badge();
    have_time = ap01_ui_pages_now(&local_time);
    if (have_time)
      {
        snprintf(year, sizeof(year), "%04d", local_time.tm_year + 1900);
      }
    else
      {
        snprintf(year, sizeof(year), "----");
      }
    g_ap01_ui_pages_date_month = ap01_ui_label(panel, "--月", 23, 10,
                                                lv_color_hex(0x89d8f3),
                                                &ap01_rom_month);
    g_ap01_ui_pages_date_year = ap01_ui_label(panel, year, 219, 19,
                                               lv_color_hex(0xffffff),
                                               &ap01_rom_year);

    unsigned int position = 0;
    for (unsigned int column = 0; column < 7; ++column)
      g_ap01_ui_pages_calendar_map[position++] = weekday_names[column];
    g_ap01_ui_pages_calendar_map[position++] = "\n";
    for (unsigned int i = 0; i < 35; ++i)
      {
        snprintf(g_ap01_ui_pages_calendar_days[i], 4, " ");
        g_ap01_ui_pages_calendar_map[position++] = g_ap01_ui_pages_calendar_days[i];
        if (i % 7 == 6) g_ap01_ui_pages_calendar_map[position++] = "\n";
      }
    g_ap01_ui_pages_calendar_map[position] = "";
    lv_obj_t *matrix = lv_buttonmatrix_create(panel);
    g_ap01_ui_pages_calendar_matrix = matrix;
    lv_obj_remove_style_all(matrix);
    lv_obj_set_size(matrix, 270, 150);
    lv_obj_set_pos(matrix, 3, 37);
    lv_obj_set_style_pad_left(matrix, 18, LV_PART_MAIN);
    lv_obj_set_style_pad_right(matrix, 18, LV_PART_MAIN);
    lv_obj_set_style_pad_top(matrix, 2, LV_PART_MAIN);
    lv_obj_set_style_pad_bottom(matrix, 6, LV_PART_MAIN);
    lv_obj_set_style_pad_column(matrix, 17, LV_PART_MAIN);
    lv_obj_set_style_pad_row(matrix, 8, LV_PART_MAIN);
    lv_obj_set_style_text_font(matrix, &ap01_rom_year, LV_PART_ITEMS);
    lv_obj_set_style_text_letter_space(matrix, 2, LV_PART_ITEMS);
    lv_obj_set_style_text_align(matrix, LV_TEXT_ALIGN_CENTER, LV_PART_ITEMS);
    lv_obj_set_style_bg_opa(matrix, LV_OPA_TRANSP, LV_PART_ITEMS);
    lv_obj_set_style_bg_opa(matrix, LV_OPA_COVER, LV_PART_ITEMS | LV_STATE_CHECKED);
    lv_obj_set_style_bg_color(matrix, lv_color_hex(0x89d8f3), LV_PART_ITEMS | LV_STATE_CHECKED);
    lv_obj_set_style_radius(matrix, 4, LV_PART_ITEMS);
    lv_obj_add_flag(matrix, LV_OBJ_FLAG_SEND_DRAW_TASK_EVENTS);
    lv_obj_remove_flag(matrix, LV_OBJ_FLAG_CLICKABLE | LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_add_event_cb(matrix, ap01_ui_pages_calendar_draw, LV_EVENT_DRAW_TASK_ADDED, NULL);
    lv_buttonmatrix_set_map(matrix, g_ap01_ui_pages_calendar_map);
    g_ap01_ui_pages_calendar_year = -1;
    g_ap01_ui_pages_calendar_month = -1;
    g_ap01_ui_pages_calendar_day = -1;
    if (have_time)
      {
        ap01_ui_pages_refresh_calendar(&local_time);
      }
    ap01_ui_page_footer(&g_ap01_ui_pages_date_clock, 20);
    ap01_ui_pages_update_clock();
  }
}

static void ap01_ui_draw_weather(void)
{
  lv_obj_t *panel;
  const ap01_sim_weather_t *weather = &g_ap01_sim.weather;
  bool valid = ap01_ui_weather_has_data();
  char value[80];

  /* Panel/text origins observed in weather1. Service IDLE retains the native
   * disconnected zeros; confirmed provider data drives all visible values. */
  panel = ap01_ui_page_panel(g_ap01_ui_root, 288, 184, 16, 0x1a1a1a, 16, 18);
  ap01_ui_page_sim_badge();
  g_ap01_ui_pages_weather_date = ap01_ui_label(panel, "", 20, 16,
                                                lv_color_hex(0xffffff),
                                                &ap01_rom_weather_text);
  g_ap01_ui_pages_weather_weekday = ap01_ui_label(panel, "", 20, 34,
                                                   lv_color_hex(0xffffff),
                                                   &ap01_rom_weather_text);
  lv_obj_set_style_text_align(g_ap01_ui_pages_weather_weekday,
                              LV_TEXT_ALIGN_LEFT, LV_PART_MAIN);
  snprintf(value, sizeof(value), "%d", valid ? weather->temperature : 0);
  lv_obj_t *temperature = ap01_ui_label(panel, value, 20, 70, lv_color_hex(0xffffff),
                &ap01_rom_temperature);
  /* Native temperature font supplies 0/C but no degree glyph. Its degree
   * helper is reconstructed as an outlined circle at the photo's baseline. */
  int temperature_width = lv_text_get_width(value, (uint32_t)strlen(value),
    &ap01_rom_temperature, 0);
  lv_obj_t *degree = ap01_ui_page_panel(panel, 10, 10, LV_RADIUS_CIRCLE,
                                         0x1a1a1a, 24 + temperature_width, 70);
  lv_obj_set_style_border_width(degree, 2, LV_PART_MAIN);
  lv_obj_set_style_border_color(degree, lv_color_hex(0xffffff), LV_PART_MAIN);
  ap01_ui_label(panel, "C", 36 + temperature_width, 70, lv_color_hex(0xffffff),
                &ap01_rom_temperature);
  (void)temperature;
  snprintf(value, sizeof(value), "最高: %d 最低: %d",
    valid ? weather->high : 0, valid ? weather->low : 0);
  ap01_ui_label(panel, value, 20, 124,
                lv_color_hex(0xffffff), &ap01_rom_weather_text);
  snprintf(value, sizeof(value), "体感温度: %d", valid ? weather->feels_like : 0);
  ap01_ui_label(panel, value, 20, 147, lv_color_hex(0xffffff),
                &ap01_rom_weather_text);
  lv_obj_t *condition = ap01_ui_label(panel,
    valid ? ap01_ui_weather_condition_name(ap01_ui_weather_code(
      weather->condition, weather->native_code)) : "未知", 193, 94,
                                       lv_color_hex(0xffffff),
                                       &ap01_rom_body20);
  lv_obj_set_width(condition, 78);
  lv_obj_set_style_text_align(condition, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
  const lv_image_dsc_t *icon = valid ? ap01_ui_weather_icon(
    ap01_ui_weather_code(weather->condition, weather->native_code), false, false) : NULL;
  if (icon != NULL) ap01_ui_page_image(panel, icon, 207, 39);
  ap01_ui_page_image(panel, &ap01_sunrise, 193, 125);
  ap01_ui_page_image(panel, &ap01_sunset, 193, 148);
  unsigned int minutes = valid ? weather->sunrise_minutes % 1440 : 0;
  snprintf(value, sizeof(value), "%02u:%02u", minutes / 60, minutes % 60);
  ap01_ui_label(panel, value, 217, 128, lv_color_hex(0xffffff),
                &ap01_rom_ascii17);
  minutes = valid ? weather->sunset_minutes % 1440 : 0;
  snprintf(value, sizeof(value), "%02u:%02u", minutes / 60, minutes % 60);
  ap01_ui_label(panel, value, 217, 152, lv_color_hex(0xffffff),
                &ap01_rom_ascii17);
  if (*ap01_ui_weather_status_text() != '\0')
    {
      lv_obj_t *notice = ap01_ui_label(panel, ap01_ui_weather_status_text(),
        193, 52, lv_color_hex(0x89d8f3), &ap01_rom_guide_text);
      lv_obj_set_width(notice, 78);
      lv_obj_set_style_text_align(notice, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
    }
  ap01_ui_page_footer(&g_ap01_ui_pages_weather_clock, 22);
  ap01_ui_pages_update_clock();
}

static void ap01_ui_draw_mijia(void)
{
  /* 0041 creator's static setup QR and hint, not a generated device binding
   * code. Pairing services and timeout/restart behavior are not simulated. */
  ap01_ui_page_panel(g_ap01_ui_root, 148, 152, 8, 0xffffff, 86, 29);
  ap01_ui_page_image(g_ap01_ui_root, &ap01_mijia_qr, 93, 38);
  lv_obj_t *hint = ap01_ui_label(g_ap01_ui_root, "单击进入操作指引", 10, 192,
                                 lv_color_hex(0xb2b2b2), &ap01_rom_mijia_hint);
  lv_obj_set_width(hint, 300);
  lv_obj_set_style_text_align(hint, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
  ap01_ui_page_sim_badge();
}

static void ap01_ui_draw_overview(void)
{
  if (g_ap01_ui_page <= AP01_UI_C2)
    {
      ap01_ui_charge_draw_overview();
      return;
    }

  if (g_ap01_ui_page == AP01_UI_MIJIA)
    {
      ap01_ui_draw_mijia();
      return;
    }
  if (g_ap01_ui_page == AP01_UI_TIME || g_ap01_ui_page == AP01_UI_DATE)
    {
      ap01_ui_draw_time_or_date();
      return;
    }
  if (g_ap01_ui_page == AP01_UI_WEATHER)
    {
      ap01_ui_draw_weather();
      return;
    }
  if (g_ap01_ui_page == AP01_UI_PET)
    {
      /* The extracted pet page is a full-screen GIF
       * added by this rehost; it has no generic help footer. */
#if defined(LV_USE_GIF) && LV_USE_GIF
      lv_obj_t *pet = lv_gif_create(g_ap01_ui_root);
      lv_gif_set_src(pet, &ap01_pets[g_ap01_ui_pet_index]);
      lv_obj_set_pos(pet, 0, 0);
#else
      ap01_ui_label(g_ap01_ui_root, "GIF disabled", 24, 110, lv_color_hex(0xffffff),
                    &ap01_rom_body20);
#endif
      ap01_ui_page_sim_badge();
      return;
    }

}
