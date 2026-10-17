/* SPDX-License-Identifier: Apache-2.0 */
/* 0041 Date/Weather details. Include after ap01-ui-pages.h.
 * Native behavior/layout evidence: details-0041-round4.json. This is an
 * Calendar browsing never writes the host RTC. Weather uses the controlled
 * SIM service; IDLE preserves native disconnected values. */
#ifndef TOOLS_AP01_AP01_UI_DETAILS_H
#define TOOLS_AP01_AP01_UI_DETAILS_H

static lv_obj_t *g_ap01_ui_detail_clock;
static lv_obj_t *g_ap01_ui_detail_weather_date;
static lv_obj_t *g_ap01_ui_detail_weather_weekday;
static lv_obj_t *g_ap01_ui_detail_calendar;
static lv_obj_t *g_ap01_ui_detail_month;
static int g_ap01_ui_detail_year;
static int g_ap01_ui_detail_month_number;
/* -1 is the month heading row; 0..5 are Gregorian week rows. */
static int g_ap01_ui_detail_week;
static int g_ap01_ui_detail_today_year = -1;
static int g_ap01_ui_detail_today_month = -1;
static int g_ap01_ui_detail_today_day = -1;
static unsigned int g_ap01_ui_detail_weather_index;

static bool ap01_ui_details_needs_redraw(void)
{
  bool changed = g_ap01_ui_pages_changed;
  g_ap01_ui_pages_changed = false;
  return changed;
}

struct ap01_ui_lunar_s
{
  int year, month, day, slot, days;
  bool leap;
};

static int ap01_ui_calendar_day_number(int year, int month, int day)
{
  month = (month + 9) % 12;
  year -= month / 10;
  return 365 * year + year / 4 - year / 100 + year / 400 +
    (month * 306 + 5) / 10 + day - 1;
}

static bool ap01_ui_calendar_lunar(int year, int month, int day,
                                    struct ap01_ui_lunar_s *lunar)
{
  /* a01acf40 has no table guard. The SIM bounds the exact ROM tables,
   * rather than reproducing its out-of-bounds access. */
  if (year < 1888 || year > 2111) return false;
  unsigned int packed = ((unsigned int)year << 9) | (month << 5) | day;
  int index = year - 1887;
  if (packed < ap01_lunar_new_year[index]) --index;
  if (index < 1 || index >= 225) return false;
  unsigned int new_year = ap01_lunar_new_year[index];
  int offset = ap01_ui_calendar_day_number(year, month, day) -
    ap01_ui_calendar_day_number(new_year >> 9, (new_year >> 5) & 15,
                                new_year & 31) + 1;
  unsigned int bits = ap01_lunar_month_bits[index];
  int leap_month = (bits >> 13) & 15;
  int slot = 1, days = 0;
  for (; slot <= 13; ++slot)
    {
      days = bits & (0x2000u >> slot) ? 30 : 29;
      if (offset <= days) break;
      offset -= days;
    }
  if (slot > 13 || offset < 1) return false;
  lunar->year = index + 1887;
  lunar->month = slot - (leap_month != 0 && slot > leap_month);
  lunar->day = offset;
  lunar->slot = slot;
  lunar->days = days;
  lunar->leap = leap_month != 0 && slot == leap_month + 1;
  return lunar->month >= 1 && lunar->month <= 12;
}

static const char *ap01_ui_calendar_subtitle(int year, int month, int day,
                                              bool *holiday)
{
  struct ap01_ui_lunar_s lunar;
  *holiday = false;
  if (!ap01_ui_calendar_lunar(year, month, day, &lunar)) return "";
  const char *text = lunar.day == 1 ? ap01_lunar_month_names[lunar.month] :
    ap01_lunar_day_names[lunar.day - 1];
  /* Native precedence: base lunar label < fixed solar festival < term <
   * lunar festival. Flags2 week-based festival records are not consulted. */
  for (unsigned int i = 0; i < 26; ++i)
    if ((ap01_calendar_festivals[i].flags & 3) == 0 &&
        ap01_calendar_festivals[i].month == month &&
        ap01_calendar_festivals[i].day == day)
      {
        text = ap01_calendar_festivals[i].text;
        *holiday = (ap01_calendar_festivals[i].flags & 4) != 0;
        break;
      }
  if (year >= 1900 && year <= 2099)
    {
      int epoch_day = ap01_ui_calendar_day_number(year, month, day) -
        ap01_ui_calendar_day_number(1970, 1, 1);
      for (unsigned int i = 0; i < 24; ++i)
        {
          /* Native truncates to 32-bit time_t. UTC0 is its ROM default;
           * there is no invented China-time correction to the table. */
          uint32_t seconds = (uint32_t)(ap01_solar_term_millis[year - 1900][i] / 1000);
          if (epoch_day >= 0 && seconds / 86400 == (uint32_t)epoch_day)
            { text = ap01_solar_term_names[i]; break; }
        }
    }
  for (unsigned int i = 0; i < 26; ++i)
    if ((ap01_calendar_festivals[i].flags & 3) == 1 &&
        ap01_calendar_festivals[i].month == lunar.month &&
        (ap01_calendar_festivals[i].day == lunar.day ||
         (ap01_calendar_festivals[i].day == 0 && lunar.day == lunar.days)))
      {
        text = ap01_calendar_festivals[i].text;
        *holiday = (ap01_calendar_festivals[i].flags & 4) != 0;
        break;
      }
  return text;
}

static void ap01_ui_calendar_log_date(int year, int month, int day,
                                       const char *view)
{
  struct ap01_ui_lunar_s lunar;
  bool holiday;
  const char *subtitle = ap01_ui_calendar_subtitle(year, month, day, &holiday);
  bool supported = ap01_ui_calendar_lunar(year, month, day, &lunar);
  /* One current-date record per redraw/day change; uses the same lookup
   * that supplies visible native detail subtitles, not a test-only path. */
  printf("DATE calendar view=%s year=%d month=%d day=%d subtitle=%s holiday=%u lunarSupported=%u\n",
    view, year, month, day, subtitle, holiday, supported);
}

static void ap01_ui_details_reset(void)
{
  g_ap01_ui_detail_clock = NULL;
  g_ap01_ui_detail_weather_date = NULL;
  g_ap01_ui_detail_weather_weekday = NULL;
  g_ap01_ui_detail_calendar = NULL;
  g_ap01_ui_detail_month = NULL;
}

static int ap01_ui_detail_first_weekday(int year, int month)
{
  /* Gregorian Sunday=0; independent of host timezone and time_t range. */
  static const int offsets[] = {0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4};
  if (month < 3) --year;
  return (year + year / 4 - year / 100 + year / 400 +
          offsets[month - 1] + 1) % 7;
}

static int ap01_ui_detail_week_count(int year, int month)
{
  return (ap01_ui_detail_first_weekday(year, month) +
          ap01_ui_pages_days_in_month(year, month) + 6) / 7;
}

static void ap01_ui_detail_shift_month(int *year, int *month, int direction)
{
  *month += direction;
  if (*month == 0) { *month = 12; --*year; }
  if (*month == 13) { *month = 1; ++*year; }
}

static void ap01_ui_detail_shift_row(int *year, int *month, int *week,
                                      int direction)
{
  if (direction > 0)
    {
      if (++*week == ap01_ui_detail_week_count(*year, *month))
        {
          ap01_ui_detail_shift_month(year, month, 1);
          *week = -1;
        }
    }
  else if (*week == -1)
    {
      ap01_ui_detail_shift_month(year, month, -1);
      *week = ap01_ui_detail_week_count(*year, *month) - 1;
    }
  else
    {
      --*week;
    }
}

static void ap01_ui_detail_log_date(void)
{
  int day = g_ap01_ui_detail_week < 0 ? 1 :
    g_ap01_ui_detail_week * 7 - ap01_ui_detail_first_weekday(
      g_ap01_ui_detail_year, g_ap01_ui_detail_month_number) + 1;
  if (day < 1) day = 1;
  printf("DATE detail year=%d month=%d day=%d focus=calendar week=%d rtc_write=0\n",
         g_ap01_ui_detail_year, g_ap01_ui_detail_month_number, day,
         g_ap01_ui_detail_week);
}

static void ap01_ui_details_open(enum ap01_ui_page_e page)
{
  struct tm now;
  if (page == AP01_UI_WEATHER)
    {
      g_ap01_ui_detail_weather_index = 0;
      printf("WEATHER detail index=0 scroll_y=0 data=%s status=%u\n",
        ap01_ui_weather_has_data() ? "ready" : "unavailable", g_ap01_sim.weather.status);
    }
  else if (page == AP01_UI_DATE && ap01_ui_now(&now))
    {
      int current_cell;
      g_ap01_ui_detail_year = now.tm_year + 1900;
      g_ap01_ui_detail_month_number = now.tm_mon + 1;
      g_ap01_ui_detail_week = 0;
      current_cell = ap01_ui_detail_first_weekday(
        g_ap01_ui_detail_year, g_ap01_ui_detail_month_number) + now.tm_mday - 1;
      if (current_cell >= 28) current_cell = 0;
      /* a010bd80 fills 28 cells. a00f4bf8 advances when the native current
       * cell is in 21..27, twice for cell 0. No editable date is selected. */
      if (current_cell == 0 || (current_cell >= 21 && current_cell <= 27))
        {
          ap01_ui_detail_shift_row(&g_ap01_ui_detail_year,
            &g_ap01_ui_detail_month_number, &g_ap01_ui_detail_week, 1);
          if (current_cell == 0)
            ap01_ui_detail_shift_row(&g_ap01_ui_detail_year,
              &g_ap01_ui_detail_month_number, &g_ap01_ui_detail_week, 1);
        }
      ap01_ui_detail_log_date();
    }
}

static void ap01_ui_detail_calendar_update(const struct tm *today)
{
  int year = g_ap01_ui_detail_year;
  int month = g_ap01_ui_detail_month_number;
  int week = g_ap01_ui_detail_week;
  char value[32];
  if (g_ap01_ui_detail_calendar == NULL) return;
  lv_obj_clean(g_ap01_ui_detail_calendar);
  snprintf(value, sizeof(value), "%d年 %d月", year, month);
  lv_label_set_text(g_ap01_ui_detail_month, value);
  struct ap01_ui_lunar_s first_lunar;
  if (!ap01_ui_calendar_lunar(year, month, 1, &first_lunar))
    {
      lv_obj_t *range = ap01_ui_label(g_ap01_ui_detail_calendar,
        "农历范围1888–2111", 70, 163, lv_color_hex(0x8e8d93), &ap01_rom_guide_text);
      lv_obj_set_width(range, 200);
      lv_obj_set_style_text_align(range, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
    }
  for (int row = 0; row < 4; ++row)
    {
      /* A010A302: five map rows include the final empty row. With
       * height180,padTop8,padBottom0,rowGap8, each cell is28px and
       * successive visible rows start36px apart. Width308/7=44px. */
      int row_y = 8 + row * 36;
      if (week == -1)
        {
          /* The native state machine inserts a whole month-title row
           * between the last week and next month's first week. */
          snprintf(value, sizeof(value), "%d月", month);
          lv_obj_t *heading = ap01_ui_label(g_ap01_ui_detail_calendar,
            value, 6, row_y + 14, lv_color_hex(0x89d8f3),
            &ap01_rom_calendar_day);
          lv_obj_set_width(heading, 308);
          lv_obj_set_style_text_align(heading, LV_TEXT_ALIGN_CENTER,
                                      LV_PART_MAIN);
        }
      else
        {
          int first = ap01_ui_detail_first_weekday(year, month);
          int days = ap01_ui_pages_days_in_month(year, month);
          for (int column = 0; column < 7; ++column)
            {
              int day = week * 7 + column - first + 1;
              if (day < 1 || day > days) continue;
              snprintf(value, sizeof(value), "%d", day);
              bool is_today = today != NULL && year == today->tm_year + 1900 &&
                month == today->tm_mon + 1 && day == today->tm_mday;
              bool holiday;
              const char *subtitle = ap01_ui_calendar_subtitle(year, month, day,
                                                               &holiday);
              uint32_t text_color = is_today ? 0x000000 :
                column == 0 || column == 6 ? 0x8e8d93 : 0xffffff;
              if (is_today)
                {
                  /* a010decc measures the subtitle's UTF8 bytes: two CJK
                   * characters =>30px, three =>38px. */
                  int highlight = strlen(subtitle) == 9 ? 38 : 30;
                  ap01_ui_page_panel(g_ap01_ui_detail_calendar, highlight, 36, 4,
                    0x89d8f3, 6 + column * 44 + (44 - highlight) / 2, row_y);
                }
              lv_obj_t *cell = ap01_ui_label(g_ap01_ui_detail_calendar,
                value, 6 + column * 44, row_y + 1,
                lv_color_hex(text_color), &ap01_rom_mijia_hint);
              lv_obj_set_size(cell, 44, 18);
              lv_obj_set_style_text_align(cell, LV_TEXT_ALIGN_CENTER,
                                          LV_PART_MAIN);
              lv_obj_t *sub = ap01_ui_label(g_ap01_ui_detail_calendar,
                subtitle, 6 + column * 44, row_y + 21,
                lv_color_hex(text_color),
                &ap01_rom_calendar_subtitle);
              lv_obj_set_size(sub, 44, 13);
              lv_obj_set_style_text_align(sub, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
            }
        }
      ap01_ui_detail_shift_row(&year, &month, &week, 1);
    }
}

static void ap01_ui_details_tick(void)
{
  struct tm now;
  char value[40];
  static const char *const weekdays[] =
    {"星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"};
  if (!ap01_ui_now(&now)) return;
  if (g_ap01_ui_detail_clock != NULL)
    {
      strftime(value, sizeof(value), g_ap01_ui_12_hour ? "%I:%M" : "%H:%M", &now);
      lv_label_set_text(g_ap01_ui_detail_clock, value);
    }
  if (g_ap01_ui_detail_weather_date != NULL)
    {
      snprintf(value, sizeof(value), "%04d年%d月%d日", now.tm_year + 1900,
                now.tm_mon + 1, now.tm_mday);
      lv_label_set_text(g_ap01_ui_detail_weather_date, value);
      lv_label_set_text(g_ap01_ui_detail_weather_weekday, weekdays[now.tm_wday]);
    }
  if (g_ap01_ui_detail_calendar != NULL &&
      (g_ap01_ui_detail_today_year != now.tm_year ||
       g_ap01_ui_detail_today_month != now.tm_mon ||
       g_ap01_ui_detail_today_day != now.tm_mday))
    {
      /* The original timer updates today's highlight independently of
       * the browsed month; midnight does not snap the viewport home. */
      ap01_ui_detail_calendar_update(&now);
      g_ap01_ui_detail_today_year = now.tm_year;
      g_ap01_ui_detail_today_month = now.tm_mon;
      g_ap01_ui_detail_today_day = now.tm_mday;
      ap01_ui_calendar_log_date(now.tm_year + 1900, now.tm_mon + 1,
        now.tm_mday, "detail");
      struct ap01_ui_lunar_s lunar;
      bool holiday;
      const char *subtitle = ap01_ui_calendar_subtitle(now.tm_year + 1900,
        now.tm_mon + 1, now.tm_mday, &holiday);
      if (ap01_ui_calendar_lunar(now.tm_year + 1900, now.tm_mon + 1,
                                 now.tm_mday, &lunar))
        printf("DATE lunar solar=%04d-%02d-%02d year=%d month=%d day=%d leap=%u label=%s holiday=%u\n",
          now.tm_year + 1900, now.tm_mon + 1, now.tm_mday, lunar.year,
          lunar.month, lunar.day, lunar.leap, subtitle, holiday);
      else
        printf("DATE lunar solar=%04d-%02d-%02d supported=0 range=1888-02-12..2111-12-31\n",
          now.tm_year + 1900, now.tm_mon + 1, now.tm_mday);
    }
}

static void ap01_ui_detail_draw_date(void)
{
  static const char *const weekdays[] = {"日", "一", "二", "三", "四", "五", "六"};
  /* Main creator a00afc88: title(20,13), clock top-right(-20,12),
   * 320x18 weekday strip y46, 320x180 calendar y72. */
  g_ap01_ui_detail_month = ap01_ui_label(g_ap01_ui_root, "", 20, 13,
    lv_color_hex(0x89d8f3), &ap01_rom_date_heading);
  g_ap01_ui_detail_clock = ap01_ui_label(g_ap01_ui_root, "", 245, 12,
    lv_color_hex(0xffffff), &ap01_rom_clock21);
  for (int i = 0; i < 7; ++i)
    {
      lv_obj_t *day = ap01_ui_label(g_ap01_ui_root, weekdays[i],
        8 + i * 44, 46, lv_color_hex(i == 0 || i == 6 ? 0x8e8d93 : 0xffffff),
        &ap01_rom_calendar_week);
      lv_obj_set_width(day, 40);
      lv_obj_set_style_text_align(day, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
    }
  g_ap01_ui_detail_calendar = ap01_ui_page_panel(g_ap01_ui_root,
    320, 180, 0, 0x000000, 0, 72);
  g_ap01_ui_detail_today_year = -1;
  ap01_ui_details_tick();
  ap01_ui_page_sim_badge();
}

static void ap01_ui_detail_weather_metric(lv_obj_t *parent, int x,
                                           const char *caption,
                                           uint32_t background, uint32_t color,
                                           unsigned int reading, unsigned int maximum)
{
  /* Native fixed-color arcs clamp geometry to AQI500/UVI5. Labels keep
   * the reading; there are no native textual quality-grade categories. */
  lv_obj_t *meter = lv_arc_create(parent);
  lv_obj_set_pos(meter, x, 170);
  lv_obj_set_size(meter, 50, 50);
  lv_arc_set_bg_angles(meter, 148, 244);
  lv_arc_set_range(meter, 0, (int)maximum);
  lv_arc_set_value(meter, reading > maximum ? (int)maximum : (int)reading);
  lv_obj_set_style_arc_width(meter, 6, LV_PART_MAIN);
  lv_obj_set_style_arc_width(meter, 6, LV_PART_INDICATOR);
  lv_obj_set_style_arc_color(meter, lv_color_hex(background), LV_PART_MAIN);
  lv_obj_set_style_arc_color(meter, lv_color_hex(color), LV_PART_INDICATOR);
  lv_obj_set_style_bg_opa(meter, LV_OPA_TRANSP, LV_PART_KNOB);
  lv_obj_remove_flag(meter, LV_OBJ_FLAG_CLICKABLE);
  if (caption[0] == '\0') return;
  char text[16];
  snprintf(text, sizeof(text), "%u", reading);
  lv_obj_t *value = ap01_ui_label(parent, text, x, 183,
    lv_color_hex(0xffffff), reading >= 100 ? &ap01_rom_humidity_digits :
                                           &ap01_rom_detail_metric);
  lv_obj_set_width(value, 50);
  lv_obj_set_style_text_align(value, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
  lv_obj_t *name = ap01_ui_label(parent, caption, x, 222,
    lv_color_hex(0xffffff), &ap01_rom_detail_caption);
  lv_obj_set_width(name, 50);
  lv_obj_set_style_text_align(name, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
}

static void ap01_ui_detail_draw_weather(void)
{
  /* a00b821e builds one tall document, a00b35ee scrolls by index*90.
   * Five positions therefore expose overlapping content, not five tabs. */
  int scroll = (int)g_ap01_ui_detail_weather_index * 90;
  const ap01_sim_weather_t *weather = &g_ap01_sim.weather;
  bool valid = ap01_ui_weather_has_data();
  unsigned int code = ap01_ui_weather_code(weather->condition, weather->native_code);
  char value[80];
  lv_obj_t *content = ap01_ui_page_panel(g_ap01_ui_root, 320, 584,
    0, 0x000000, 0, -scroll);
  g_ap01_ui_detail_weather_date = ap01_ui_label(content, "", 29, 20,
    lv_color_hex(0xffffff), &ap01_rom_guide_text);
  g_ap01_ui_detail_weather_weekday = ap01_ui_label(content, "", 28, 38,
    lv_color_hex(0xffffff), &ap01_rom_guide_text);
  snprintf(value, sizeof(value), "%d°C", valid ? weather->temperature : 0);
  ap01_ui_label(content, value, 28, 66, lv_color_hex(0xffffff),
    &ap01_rom_weather_temp);
  snprintf(value, sizeof(value), "最高: %d 最低: %d", valid ? weather->high : 0,
    valid ? weather->low : 0);
  ap01_ui_label(content, value, 28, 115,
    lv_color_hex(0xffffff), &ap01_rom_weather_text);
  snprintf(value, sizeof(value), "体感温度: %d", valid ? weather->feels_like : 0);
  ap01_ui_label(content, value, 28, 136,
    lv_color_hex(0xffffff), &ap01_rom_weather_text);
  ap01_ui_page_image(content, &ap01_sunrise, 28, 173);
  ap01_ui_page_image(content, &ap01_sunset, 28, 196);
  unsigned int minutes = valid ? weather->sunrise_minutes % 1440 : 0;
  snprintf(value, sizeof(value), "%02u:%02u", minutes / 60, minutes % 60);
  ap01_ui_label(content, value, 51, 175, lv_color_hex(0xffffff),
    &ap01_rom_guide_text);
  minutes = valid ? weather->sunset_minutes % 1440 : 0;
  snprintf(value, sizeof(value), "%02u:%02u", minutes / 60, minutes % 60);
  ap01_ui_label(content, value, 51, 199, lv_color_hex(0xffffff),
    &ap01_rom_guide_text);
  g_ap01_ui_detail_clock = ap01_ui_label(content, "", 252, 20,
    lv_color_hex(0xffffff), &ap01_rom_guide_text);
  lv_obj_t *condition = ap01_ui_label(content,
    valid ? ap01_ui_weather_condition_name(code) : "未知", 224, 115,
    lv_color_hex(0xffffff), &ap01_rom_body20);
  lv_obj_set_width(condition, 88);
  lv_obj_set_style_text_align(condition, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
  const lv_image_dsc_t *icon = valid ? ap01_ui_weather_icon(code, false, false) : NULL;
  if (icon != NULL) ap01_ui_page_image(content, icon, 242, 63);
  if (!valid)
    {
      lv_obj_t *notice = ap01_ui_label(content, ap01_ui_weather_status_text(),
        215, 66, lv_color_hex(0x89d8f3), &ap01_rom_guide_text);
      lv_obj_set_width(notice, 95);
      lv_obj_set_style_text_align(notice, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
    }
  ap01_ui_page_image(content, &ap01_weather_aqi_scale, 112, 170);
  ap01_ui_detail_weather_metric(content, 112, "AQI", 0xffffff, 0xffffff,
    valid ? weather->aqi : 0, 500);
  ap01_ui_detail_weather_metric(content, 177, "UVI", 0x493112, 0xf2a33c,
    valid ? weather->uvi : 0, 5);
  ap01_ui_detail_weather_metric(content, 242, "", 0x294149, 0x89d8f3,
    valid ? weather->humidity : 0, 100);
  /* Humidity's native centered digits/unit use the smaller fixed fonts. */
  lv_obj_t *humidity = ap01_ui_page_panel(content, 34, 20, 0, 0x000000, 250, 183);
  snprintf(value, sizeof(value), "%u", valid ? weather->humidity : 0);
  ap01_ui_label(humidity, value, 1, 4, lv_color_hex(0xffffff),
    &ap01_rom_humidity_digits);
  ap01_ui_label(humidity, "%", 24, 7, lv_color_hex(0xffffff),
    &ap01_rom_humidity_unit);
  ap01_ui_page_image(content, &ap01_time_humidity_icon, 257, 222);
  for (int i = 0; i < 7; ++i)
    {
      int y = 240 + i * 43;
      ap01_ui_page_panel(content, 300, 1, 0, 0x333333, 10, y + 42);
      struct tm now;
      bool have_time = ap01_ui_now(&now);
      static const char *const weekdays[] = {"日", "一", "二", "三", "四", "五", "六"};
      if (i == 0)
        ap01_ui_label(content, "今天", 25, y + 11,
          lv_color_hex(0xffffff), &ap01_rom_mini_week);
      else if (have_time)
        {
          int year = now.tm_year + 1900, month = now.tm_mon + 1, day = now.tm_mday + i;
          int days = ap01_ui_pages_days_in_month(year, month);
          if (day > days) { day -= days; ap01_ui_detail_shift_month(&year, &month, 1); }
          snprintf(value, sizeof(value), "%d", day);
          ap01_ui_label(content, value, 15, y + 13, lv_color_hex(0xffffff), &ap01_rom_mini_week);
          ap01_ui_label(content, weekdays[(now.tm_wday + i) % 7], 35, y + 13,
            lv_color_hex(0xffffff), &ap01_rom_mini_week);
        }
      unsigned int forecast_code = ap01_ui_weather_code(weather->forecast[i].condition,
        weather->forecast[i].native_code);
      icon = valid ? ap01_ui_weather_icon(forecast_code, true, i != 0) : NULL;
      if (icon != NULL) ap01_ui_page_image(content, icon, 135, y + 6);
      if (valid) snprintf(value, sizeof(value), "%d°", weather->forecast[i].low);
      else snprintf(value, sizeof(value), "--°");
      ap01_ui_label(content, value, 191, y + 11,
        lv_color_hex(0x999999), &ap01_rom_forecast);
      if (valid) snprintf(value, sizeof(value), "%d°", weather->forecast[i].high);
      else snprintf(value, sizeof(value), "--°");
      ap01_ui_label(content, value, 243, y + 11,
        lv_color_hex(0xffffff), &ap01_rom_forecast);
    }
  lv_obj_t *note = ap01_ui_label(content, "天气服务由和风天气驱动", 0, 557,
    lv_color_hex(0x999999), &ap01_rom_weather_note);
  lv_obj_set_width(note, 300);
  lv_obj_set_style_text_align(note, LV_TEXT_ALIGN_CENTER, LV_PART_MAIN);
  for (unsigned int i = 0; i < 5; ++i)
    ap01_ui_page_panel(g_ap01_ui_root, 6, 6, 3,
      i == g_ap01_ui_detail_weather_index ? 0xffffff : 0x333333,
      307, 11 + (int)i * 11);
  ap01_ui_details_tick();
  printf("WEATHER data status=%u native=%u icon=%u temperature=%d humidity=%u aqi=%u uvi=%u\n",
    weather->status, code, ap01_ui_weather_icon_index(code, ap01_ui_weather_night(), false),
    weather->temperature, weather->humidity, weather->aqi, weather->uvi);
  ap01_ui_page_sim_badge();
}

static void ap01_ui_details_draw(void)
{
  if (g_ap01_ui_page == AP01_UI_DATE) ap01_ui_detail_draw_date();
  else if (g_ap01_ui_page == AP01_UI_WEATHER) ap01_ui_detail_draw_weather();
}

static void ap01_ui_details_turn(int direction)
{
  if (direction == 0) return;
  if (g_ap01_ui_page == AP01_UI_DATE)
    {
      /* Keep Gregorian arithmetic defined at the lower representable year. */
      if (direction > 0 && g_ap01_ui_detail_year >= 9999 &&
          g_ap01_ui_detail_month_number == 12 &&
          g_ap01_ui_detail_week == ap01_ui_detail_week_count(9999, 12) - 1)
        return;
      if (direction < 0 && g_ap01_ui_detail_year == 1 &&
          g_ap01_ui_detail_month_number == 1 && g_ap01_ui_detail_week == -1)
        return;
      ap01_ui_detail_shift_row(&g_ap01_ui_detail_year,
        &g_ap01_ui_detail_month_number, &g_ap01_ui_detail_week, direction);
      ap01_ui_detail_log_date();
    }
  else if (g_ap01_ui_page == AP01_UI_WEATHER)
    {
      unsigned int previous = g_ap01_ui_detail_weather_index;
      if (direction > 0 && previous < 4) ++g_ap01_ui_detail_weather_index;
      if (direction < 0 && previous > 0) --g_ap01_ui_detail_weather_index;
      printf("WEATHER detail index=%u scroll_y=%u boundary=%u\n",
        g_ap01_ui_detail_weather_index, g_ap01_ui_detail_weather_index * 90,
        previous == g_ap01_ui_detail_weather_index);
    }
}

static bool ap01_ui_details_press(void)
{
  if (g_ap01_ui_page != AP01_UI_DATE && g_ap01_ui_page != AP01_UI_WEATHER)
    return false;
  /* Native enter refreshes the matching overview and deletes the detail
   * window. Controller owns mode/parent restoration. */
  printf("%s detail press=back\n",
    g_ap01_ui_page == AP01_UI_DATE ? "DATE" : "WEATHER");
  return true;
}

#endif
