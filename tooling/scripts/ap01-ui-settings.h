/* SPDX-License-Identifier: Apache-2.0 */
/* 0041 settings plus SIM Wi-Fi selection; original table 0xa01bb718. */
static void ap01_ui_settings_header(const char *title)
{
  ap01_ui_label(g_ap01_ui_root, title, 18,
                g_ap01_ui_mode == AP01_UI_MODE_DETAIL ? 16 : 20,
                lv_color_hex(0xffffff), g_ap01_ui_mode == AP01_UI_MODE_DETAIL ?
                &ap01_rom_body20 : &ap01_rom_title25);
  g_ap01_ui_settings_clock = ap01_ui_label(g_ap01_ui_root, "00:00", 238, 17,
                                           lv_color_hex(0xffffff), &ap01_rom_clock21);
  ap01_ui_set_clock_text();
}

static lv_obj_t *ap01_ui_settings_row(lv_obj_t *parent, const char *title,
                                      int y, bool focused, const char *value,
                                      bool back)
{
  lv_obj_t *row = lv_image_create(parent);
  lv_image_set_src(row, &ap01_setting_row);
  lv_obj_set_pos(row, 10, y);
  lv_obj_set_style_image_recolor(row, lv_color_hex(focused ? 0x22363d : 0x1f1f1f), 0);
  lv_obj_set_style_image_recolor_opa(row, LV_OPA_COVER, 0);
  if (focused)
    {
      lv_obj_set_style_outline_width(row, 0, 0);
      lv_obj_set_style_radius(row, 12, 0);
    }
  lv_obj_t *text = ap01_ui_label(row, title, back ? 44 : 20, 0,
                                 lv_color_hex(0xffffff), &ap01_rom_body20);
  lv_obj_align(text, LV_ALIGN_LEFT_MID, back ? 44 : 20, 0);
  text = ap01_ui_label(row, back ? "<" : (value ? value : ">"), 0, 0,
                       lv_color_hex(focused ? 0x89d8f3 : (back ? 0xffffff : 0x808080)), &ap01_rom_ascii17);
  lv_obj_align(text, back ? LV_ALIGN_LEFT_MID : LV_ALIGN_RIGHT_MID,
               back ? 20 : -20, 0);
  return row;
}

static lv_obj_t *ap01_ui_settings_viewport(void)
{
  /* a01a2c02: 320x180 viewport y60, pad-top5, row-gap5, x padding10. */
  lv_obj_t *list = lv_obj_create(g_ap01_ui_root);
  lv_obj_set_pos(list, 0, 60);
  lv_obj_set_size(list, 320, 180);
  lv_obj_remove_flag(list, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_style_pad_all(list, 0, 0);
  lv_obj_set_style_border_width(list, 0, 0);
  lv_obj_set_style_bg_opa(list, LV_OPA_TRANSP, 0);
  lv_obj_set_style_radius(list, 0, 0);
  return list;
}

static void ap01_ui_draw_settings(void)
{
  ap01_ui_settings_header("设置");
  lv_obj_t *list = ap01_ui_settings_viewport();
  /* a00fd1ac preserves pairs and scrolls only at native boundary states. */
  static const int positions[] = {0, 0, 141, 141, 287, 287, 433, 473};
  int scroll = positions[g_ap01_ui_selection];
  for (unsigned i = 0; i < AP01_UI_SETTINGS_COUNT; ++i)
    {
      const char *value = i < 2 ? (g_ap01_ui_setting_enabled[i] ? "打开" : "关闭") : NULL;
      if (i == 4) value = NULL;
      ap01_ui_settings_row(list, ap01_ui_setting_name(i), 5 + (int)i * 73 - scroll,
                            g_ap01_ui_mode == AP01_UI_MODE_LIST && i == g_ap01_ui_selection,
                            value, i == 7);
    }
}

static void ap01_ui_draw_time_options(void)
{
  /* Main key-10 creator: 0xa00b0dd6; three strings at 0xa037b6bc/c8/664. */
  ap01_ui_settings_header("时间设定");
  /* Native creator 0xa019471a: 320x190 list y50, 300x68 image rows,
   * pad-top10 and gap5. Native checkmark is also a three-point LVGL line;
   * the ROM stores its points in RAM, so these coordinates follow the photo. */
  static const char *const choices[] = {"24小时制", "12小时制", "返回"};
  static const lv_point_precise_t check[] = {{0, 6}, {6, 12}, {22, 0}};
  static const lv_point_precise_t chevron[] = {{7, 0}, {0, 7}, {7, 14}};
  lv_obj_t *list = ap01_ui_settings_viewport();
  lv_obj_set_pos(list, 0, 50);
  lv_obj_set_size(list, 320, 190);
  int scroll = g_ap01_ui_option == 2 ? 34 : 0;
  for (unsigned i = 0; i < 3; ++i)
    {
      bool focused = i == g_ap01_ui_option;
      lv_obj_t *row = lv_image_create(list);
      lv_image_set_src(row, &ap01_setting_row);
      lv_obj_set_pos(row, 10, 10 + (int)i * 73 - scroll);
      lv_obj_set_style_image_recolor(row, lv_color_hex(focused ? 0x22363d : 0x1f1f1f), 0);
      lv_obj_set_style_image_recolor_opa(row, LV_OPA_COVER, 0);
      lv_obj_t *label = ap01_ui_label(row, choices[i], i == 2 ? 44 : 20, 0,
                                      lv_color_hex(0xffffff), &ap01_rom_body20);
      lv_obj_align(label, LV_ALIGN_LEFT_MID, i == 2 ? 44 : 20, 0);
      if (i == 2 || (g_ap01_ui_12_hour == (i == 1)))
        {
          lv_obj_t *mark = lv_line_create(row);
          lv_line_set_points(mark, i == 2 ? chevron : check, 3);
          lv_obj_set_pos(mark, i == 2 ? 20 : 257, 27);
          lv_obj_set_style_line_width(mark, 2, 0);
          lv_obj_set_style_line_rounded(mark, true, 0);
          lv_obj_set_style_line_color(mark, lv_color_hex(i == 2 ? 0xffffff : 0x89d8f3), 0);
        }
    }
}

static unsigned ap01_ui_wifi_count(void)
{
  unsigned count = ap01_wifi_current_virtual() ? 1 : 0;
  for (unsigned i = 0; i < AP01_WIFI_SLOTS; ++i) count += g_ap01_wifi[i].length != 0;
  return count;
}

static unsigned ap01_ui_wifi_slot(unsigned choice)
{
  for (unsigned i = 0; i < AP01_WIFI_SLOTS; ++i)
    if (g_ap01_wifi[i].length && choice-- == 0) return i;
  if (ap01_wifi_current_virtual() && choice == 0) return AP01_WIFI_SLOTS;
  return AP01_WIFI_MENU_END;
}

static void ap01_ui_wifi_draw(void)
{
  unsigned count = ap01_ui_wifi_count();
  if (g_ap01_ui_option > count) g_ap01_ui_option = count;
  lv_obj_t *list = ap01_ui_settings_viewport();
  int scroll = g_ap01_ui_option > 1 ? (int)(g_ap01_ui_option - 1) * 73 : 0;
  for (unsigned i = 0; i <= count; ++i)
    {
      unsigned slot = ap01_ui_wifi_slot(i);
      bool back = slot == AP01_WIFI_MENU_END;
      lv_obj_t *row = ap01_ui_settings_row(list, back ? "返回" : ap01_wifi_menu_profile(slot)->ssid,
        5 + (int)i * 73 - scroll, i == g_ap01_ui_option,
        !back && (int)slot == g_ap01_wifi_target && ap01_wifi_has_attempt() ? "..." :
        !back && (int)slot == g_ap01_wifi_active ? (g_ap01_sim.wifi_connected ? "*" : "!") : NULL, back);
      /* SSIDs may occupy all 32 bytes: leave space for the active marker. */
      lv_obj_t *label = lv_obj_get_child(row, 0);
      lv_obj_set_width(label, 238);
      lv_label_set_long_mode(label, LV_LABEL_LONG_DOT);
    }
  if (!count)
    ap01_ui_label(g_ap01_ui_root, "Wi-Fi: 0", 18, 45,
                  lv_color_hex(0x808080), &ap01_rom_ascii17);
}

static void ap01_ui_draw_settings_detail(void)
{
  const unsigned selection = g_ap01_ui_selection;
  if (selection == 5)
    {
      ap01_ui_guide_draw();
      return;
    }
  if (selection != 4) ap01_ui_settings_header(ap01_ui_setting_name(selection));
  if (selection < 2)
    {
      /* Native options: 0xa059d33c/344 and fixed back text 0xa037b664.
       * Selection remains in the detail after a choice, matching key 10. */
      static const char *const choices[] = {"打开", "关闭", "返回"};
      lv_obj_t *list = ap01_ui_settings_viewport();
      int scroll = g_ap01_ui_option == 2 ? 55 : 0;
      for (unsigned i = 0; i < 3; ++i)
        ap01_ui_settings_row(list, choices[i], 5 + (int)i * 73 - scroll,
                              i == g_ap01_ui_option,
                              i < 2 && (g_ap01_ui_setting_enabled[selection] == (i == 0))
                                ? "*" : NULL, i == 2);
    }
  else if (selection == 2) ap01_ui_wifi_draw();
  else if (selection == 3)
    {
      ap01_ui_label(g_ap01_ui_root,
                     g_ap01_ui_brightness_edit ? "左右滑动调节，单击确认" : "单击进入亮度调节",
                     18, 56, lv_color_hex(g_ap01_ui_brightness_edit ? 0xffd24b : 0xffffff),
                     &ap01_rom_body20);
      lv_obj_t *row = ap01_ui_settings_row(g_ap01_ui_root, "", 80,
                                           g_ap01_ui_option == 0, "", false);
      lv_image_set_src(row, &ap01_brightness_row);
      lv_obj_set_size(row, 300, 76);
      char value[24];
      snprintf(value, sizeof(value), "%u%%", g_ap01_ui_brightness * 10);
      lv_obj_t *label = ap01_ui_label(row, value, 208, 22,
                                      lv_color_hex(0xffffff), &ap01_rom_detail_metric);
      lv_obj_align(label, LV_ALIGN_LEFT_MID, 208, -2);
      lv_obj_t *icon = lv_image_create(row);
      lv_image_set_src(icon, &ap01_brightness_icon);
      lv_obj_align(icon, LV_ALIGN_LEFT_MID, 266, 0);
      lv_obj_t *bar = lv_bar_create(row);
      lv_obj_set_size(bar, 180, 14);
      lv_obj_align(bar, LV_ALIGN_LEFT_MID, 20, 0);
      lv_bar_set_range(bar, 0, 100);
      lv_bar_set_value(bar, g_ap01_ui_brightness * 10, LV_ANIM_OFF);
      lv_obj_set_style_bg_color(bar, lv_color_hex(0xbfbfbf), LV_PART_MAIN);
      lv_obj_set_style_bg_color(bar, lv_color_hex(0xffa500), LV_PART_INDICATOR);
      ap01_ui_settings_row(g_ap01_ui_root, "返回", 160, g_ap01_ui_option == 1, NULL, true);
    }
  else if (selection == 4)
    {
      ap01_ui_system_version_draw();
    }
  else if (selection == 6)
    {
      lv_obj_t *prompt = ap01_ui_label(g_ap01_ui_root, "确认恢复出厂设置？", 0, 70,
                                       lv_color_hex(0xffffff), &ap01_rom_title25);
      lv_obj_set_width(prompt, 320);
      lv_obj_set_style_text_align(prompt, LV_TEXT_ALIGN_CENTER, 0);
      /* Native a0190efc buttons, same small PNG used by OTA. L76 is the
       * right Confirm default; M77 is Cancel. */
      const char *choices[] = {"取消", "确认"};
      for (unsigned i = 0; i < 2; ++i)
        {
          lv_obj_t *button = lv_image_create(g_ap01_ui_root);
          lv_image_set_src(button, &ap01_guide_button);
          lv_obj_set_pos(button, i == 0 ? 14 : 224, 192);
          lv_obj_set_style_image_recolor(button,
            lv_color_hex(i == g_ap01_ui_option ? 0x22363d : 0x262626), 0);
          lv_obj_set_style_image_recolor_opa(button, LV_OPA_COVER, 0);
          lv_obj_t *text = ap01_ui_label(button, choices[i], 0, 0,
            lv_color_hex(i == g_ap01_ui_option ? 0x89d8f3 : 0xffffff), &ap01_rom_system_button);
          lv_obj_center(text);
        }
    }
  else
    {
      ap01_ui_label(g_ap01_ui_root, "操作指南", 24, 72,
                     lv_color_hex(0xffffff), &ap01_rom_title25);
      ap01_ui_label(g_ap01_ui_root, "旋转切换页面，单击进入设置", 24, 112,
                     lv_color_hex(0xbfbfbf), &ap01_rom_body20);
      ap01_ui_settings_row(g_ap01_ui_root, "返回", 160, true, NULL, true);
    }
}
