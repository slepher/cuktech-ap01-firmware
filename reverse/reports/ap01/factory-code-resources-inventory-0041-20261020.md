# AP01 0041 原厂代码与资源盘点

ROM SHA256：`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。只读检查 ROM，未改固件。

## 口径

- C文件以ROM保留路径为下界，不等于源码全集。已识别的NuttX、LVGL等公共组件已排除；日历等定制模块来源待单独确认。
- PNG逐块验证CRC/IEND；GIF验证块边界/trailer，未解码像素/LZW。
- 入重建清单不等于原件所有分支已逆向；未入清单不等于从未分析。
- 不包含完整Flash的/resource、Boot2、无头或压缩资源；重建名称未必是原始文件名。

## C文件

### 底座与外设业务（10）

| 路径 | ROM文件偏移 | 纳入17项UI模块矩阵 |
| --- | --- | --- |
| `PogoPinMng/PogoPinMng.c` | `0x1c39b4` | 否；覆盖待按函数核账 |
| `PogoPinMng/UartComm.c` | `0x1c3a94` | 否；覆盖待按函数核账 |
| `PogoPinMng/WeatherApi.c` | `0x1c3b30` | 否；覆盖待按函数核账 |
| `PogoPinMng/FactoryTestMode.c` | `0x1c3bac` | 否；覆盖待按函数核账 |
| `PogoPinMng/MiIotMng.c` | `0x1c4014` | 否；覆盖待按函数核账 |
| `PogoPinMng/BuzzerMng.c` | `0x1c4604` | 否；覆盖待按函数核账 |
| `PogoPinMng/UiIFaceMng.c` | `0x2694f0` | 否；覆盖待按函数核账 |
| `PogoPinMng/UsbIfaceOta.c` | `0x2695fc` | 否；覆盖待按函数核账 |
| `PogoPinMng/UsbIfaceMng.c` | `0x269b24` | 否；覆盖待按函数核账 |
| `PogoPinMng/EsUnitProtocol.c` | `0x26a3f4` | 否；覆盖待按函数核账 |

### 其他应用或定制组件（来源待逐项确认）（5）

| 路径 | ROM文件偏移 | 纳入17项UI模块矩阵 |
| --- | --- | --- |
| `lvgl_ui_main.c` | `0x1c4b30` | 否；覆盖待按函数核账 |
| `SystemSettings/SystemSettings.c` | `0x26970c` | 否；覆盖待按函数核账 |
| `factory_ui/lv_window_slider.c` | `0x26972c` | 否；覆盖待按函数核账 |
| `lv_lunar_calendar/lv_calendar_ck.c` | `0x269d00` | 否；覆盖待按函数核账 |
| `lv_comp_calendar/lv_calendar_comp.c` | `0x608b1c` | 否；覆盖待按函数核账 |

### 原厂 UI（17）

| 路径 | ROM文件偏移 | 纳入17项UI模块矩阵 |
| --- | --- | --- |
| `lv_power_ui/lv_ap01_ui.c` | `0x1c4b60` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_theme.c` | `0x1c4b98` | 是；家族级SIM重建 |
| `lv_power_ui/lv_guidance.c` | `0x1c4d80` | 是；家族级SIM重建 |
| `lv_power_ui/lv_wx_data_trans.c` | `0x1c4e30` | 是；家族级SIM重建 |
| `lv_power_ui/lv_boot_anim.c` | `0x1c4e70` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_scr_saver.c` | `0x269a90` | 是；家族级SIM重建 |
| `lv_power_ui/lv_setting_data.c` | `0x269c54` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_base.c` | `0x269cdc` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_setting_dtl.c` | `0x37c1dc` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_power1_dtl.c` | `0x37c59c` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_time1_dtl.c` | `0x37c66c` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_date1_dtl.c` | `0x37c6d4` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_wx1_dtl.c` | `0x37c710` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_window.c` | `0x5612fc` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_cuk_con.c` | `0x56c04c` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_pop_up.c` | `0x59cf7c` | 是；家族级SIM重建 |
| `lv_power_ui/lv_ui_power2_dtl.c` | `0x59d568` | 是；家族级SIM重建 |

### 米家 SDK（来源与许可另核）（1）

| 路径 | ROM文件偏移 | 纳入17项UI模块矩阵 |
| --- | --- | --- |
| `miio_sdk/miio_instance/client/miio_client.c` | `0x2590b8` | 否；覆盖待按函数核账 |

## 图像数量

| 类别 | ROM检出 | 已入重建清单的唯一偏移 | 尚未纳入 |
| --- | ---: | ---: | ---: |
| PNG | 199 | 106 | 93 |
| GIF | 11 | 10 | 1 |

重建资源清单121个名称，116个唯一偏移；字体wrapper 55项。

## 尚未纳入重建清单的图像

| 类型 | ROM偏移 | 字节数 | 尺寸 |
| --- | --- | ---: | --- |
| PNG | `0x2432bc` | 694 | 82×13 |
| PNG | `0x2481cc` | 2374 | 206×67 |
| PNG | `0x248b30` | 35726 | 250×115 |
| PNG | `0x2516dc` | 381 | 24×24 |
| PNG | `0x251878` | 434 | 24×24 |
| PNG | `0x251a48` | 394 | 24×24 |
| PNG | `0x251bf0` | 370 | 24×24 |
| PNG | `0x255ea0` | 861 | 60×57 |
| PNG | `0x370d34` | 397 | 20×20 |
| PNG | `0x370ee0` | 383 | 20×20 |
| PNG | `0x37360c` | 656 | 42×40 |
| PNG | `0x3738b8` | 923 | 42×40 |
| PNG | `0x373c70` | 348 | 34×40 |
| PNG | `0x373de8` | 530 | 34×40 |
| PNG | `0x374018` | 574 | 41×40 |
| PNG | `0x374274` | 788 | 41×40 |
| PNG | `0x3745a4` | 711 | 43×40 |
| PNG | `0x374888` | 959 | 43×40 |
| PNG | `0x374c64` | 482 | 45×40 |
| PNG | `0x374e64` | 909 | 45×40 |
| PNG | `0x375210` | 578 | 41×40 |
| PNG | `0x375470` | 859 | 41×40 |
| PNG | `0x3757e8` | 686 | 42×40 |
| PNG | `0x375ab4` | 995 | 42×40 |
| PNG | `0x375eb4` | 364 | 43×40 |
| PNG | `0x37603c` | 863 | 43×40 |
| PNG | `0x3763b8` | 742 | 42×40 |
| PNG | `0x3766bc` | 1047 | 42×40 |
| PNG | `0x376af0` | 702 | 42×40 |
| PNG | `0x376dcc` | 996 | 42×40 |
| PNG | `0x3771f8` | 199 | 9×40 |
| PNG | `0x3772dc` | 201 | 9×40 |
| PNG | `0x3773c4` | 368 | 28×14 |
| PNG | `0x377550` | 502 | 28×14 |
| PNG | `0x3798b0` | 385 | 44×57 |
| PNG | `0x379a50` | 754 | 60×57 |
| PNG | `0x379d60` | 928 | 60×57 |
| PNG | `0x37a11c` | 594 | 61×55 |
| PNG | `0x37a38c` | 714 | 58×56 |
| PNG | `0x37a674` | 935 | 60×57 |
| PNG | `0x37aa38` | 372 | 60×54 |
| PNG | `0x37abc8` | 988 | 60×57 |
| PNG | `0x37afc0` | 943 | 60×57 |
| PNG | `0x532ba8` | 2560 | 258×84 |
| PNG | `0x5335c4` | 3332 | 258×84 |
| PNG | `0x5342e4` | 3542 | 258×84 |
| PNG | `0x5350d8` | 3616 | 258×84 |
| PNG | `0x535f14` | 3946 | 258×84 |
| PNG | `0x536e9c` | 4092 | 258×84 |
| PNG | `0x537eb4` | 4218 | 258×84 |
| PNG | `0x538f4c` | 4312 | 258×84 |
| PNG | `0x53a040` | 4462 | 258×84 |
| PNG | `0x53b1cc` | 4605 | 258×84 |
| PNG | `0x53c3e8` | 4735 | 258×84 |
| PNG | `0x53d684` | 3995 | 206×67 |
| PNG | `0x53e63c` | 4054 | 206×67 |
| PNG | `0x53f630` | 4096 | 206×67 |
| PNG | `0x540668` | 4195 | 206×67 |
| PNG | `0x5416cc` | 2630 | 206×67 |
| PNG | `0x542130` | 2736 | 206×67 |
| PNG | `0x542bfc` | 2768 | 206×67 |
| PNG | `0x5436e8` | 2968 | 206×67 |
| PNG | `0x54429c` | 3034 | 206×67 |
| PNG | `0x544e94` | 3136 | 206×67 |
| PNG | `0x545af0` | 3229 | 206×67 |
| PNG | `0x5467ac` | 3320 | 206×67 |
| PNG | `0x5474c0` | 3431 | 206×67 |
| PNG | `0x548244` | 3502 | 206×67 |
| PNG | `0x549010` | 3567 | 206×67 |
| PNG | `0x549e1c` | 3616 | 206×67 |
| PNG | `0x54ac58` | 3676 | 206×67 |
| PNG | `0x54bad0` | 4032 | 206×67 |
| PNG | `0x54caac` | 3948 | 206×67 |
| PNG | `0x54da34` | 36105 | 250×115 |
| PNG | `0x55675c` | 35963 | 250×115 |
| PNG | `0x600670` | 3871 | 45×45 |
| PNG | `0x6015ac` | 3726 | 45×45 |
| PNG | `0x6294f8` | 574 | 144×64 |
| PNG | `0x6325d8` | 726 | 70×70 |
| PNG | `0x6328cc` | 922 | 71×70 |
| PNG | `0x632c84` | 756 | 70×70 |
| PNG | `0x632f94` | 882 | 70×70 |
| PNG | `0x633324` | 1601 | 70×70 |
| PNG | `0x633984` | 1841 | 70×70 |
| PNG | `0x6340d4` | 1045 | 70×70 |
| PNG | `0x634508` | 1112 | 70×70 |
| PNG | `0x63497c` | 1491 | 70×70 |
| PNG | `0x634f6c` | 1712 | 70×70 |
| PNG | `0x635638` | 2476 | 70×70 |
| PNG | `0x636000` | 2167 | 70×70 |
| PNG | `0x636894` | 2201 | 70×70 |
| PNG | `0x63714c` | 1270 | 70×70 |
| PNG | `0x637660` | 1537 | 70×70 |
| GIF | `0x59eb58` | 72453 | 170×170 |

## 已纳入资源名称

| 名称 | ROM偏移 | 字节数 |
| --- | --- | ---: |
| `ap01_arc` | `0x62f440` | 2224 |
| `ap01_logo` | `0x242680` | 3102 |
| `ap01_sun` | `0x252ff0` | 2051 |
| `ap01_colon` | `0x25621c` | 145 |
| `ap01_sunrise` | `0x253810` | 427 |
| `ap01_sunset` | `0x2539d8` | 439 |
| `ap01_wifi` | `0x252aa8` | 335 |
| `ap01_wifi_off` | `0x37107c` | 343 |
| `ap01_setting_row` | `0x55f694` | 827 |
| `ap01_clock_status` | `0x243824` | 270 |
| `ap01_time_humidity_icon` | `0x252c14` | 402 |
| `ap01_power_card` | `0x2528cc` | 446 |
| `ap01_power_gradient` | `0x251d80` | 2864 |
| `ap01_power_status` | `0x243590` | 631 |
| `ap01_power_battery` | `0x243824` | 270 |
| `ap01_guide_turn` | `0x5894c4` | 39812 |
| `ap01_guide_press` | `0x593064` | 39515 |
| `ap01_guide_button` | `0x66bd44` | 455 |
| `ap01_brightness_row` | `0x55f9ec` | 855 |
| `ap01_brightness_icon` | `0x607894` | 338 |
| `ap01_charge_mode_card` | `0x55fd60` | 869 |
| `ap01_charge_port_card` | `0x560488` | 918 |
| `ap01_charge_mode_icon` | `0x55f3f4` | 285 |
| `ap01_mijia_qr` | `0x243950` | 17913 |
| `ap01_charge_protocol_bg` | `0x5ecc1c` | 74533 |
| `ap01_charge_protocol_title` | `0x5ebffc` | 3073 |
| `ap01_charge_protocol_caption` | `0x5fef60` | 5873 |
| `ap01_charge_protocol_scan` | `0x5eb7e4` | 2042 |
| `ap01_charge_safe_title` | `0x5e99cc` | 1042 |
| `ap01_charge_safe_caption` | `0x5ea9e0` | 3557 |
| `ap01_charge_safe_hint` | `0x5e9e18` | 3015 |
| `ap01_charge_port_icon` | `0x62fd0c` | 473 |
| `ap01_charge_cable_icon` | `0x55f530` | 328 |
| `ap01_guide_practice_intro` | `0x575938` | 40836 |
| `ap01_guide_practice_turn_done` | `0x57f8d8` | 39885 |
| `ap01_guide_practice_power` | `0x56f790` | 9996 |
| `ap01_guide_practice_c1_done` | `0x571eb8` | 14973 |
| `ap01_guide_bubble50` | `0x36ff8c` | 645 |
| `ap01_guide_bubble70` | `0x370230` | 708 |
| `ap01_guide_bubble90` | `0x370510` | 768 |
| `ap01_boot_logo` | `0x242680` | 3102 |
| `ap01_saver_glow_top` | `0x365dc0` | 27545 |
| `ap01_saver_glow_bottom` | `0x36c978` | 13815 |
| `ap01_saver_curve` | `0x365184` | 3101 |
| `ap01_saver_fast` | `0x37082c` | 1259 |
| `ap01_saver_thermometer` | `0x252dc4` | 527 |
| `ap01_system_mijia_qr` | `0x243950` | 17913 |
| `ap01_system_binding_timeout` | `0x247f68` | 583 |
| `ap01_system_ota_success` | `0x605d24` | 6233 |
| `ap01_system_confirm_button` | `0x60759c` | 732 |
| `ap01_system_version_card` | `0x5600e4` | 904 |
| `ap01_weather_aqi_scale` | `0x564644` | 1933 |
| `ap01_time_temperature_icon` | `0x252dc4` | 527 |
| `digit0` | `0x255b18` | 857 |
| `digit1` | `0x377790` | 492 |
| `digit2` | `0x377998` | 741 |
| `digit3` | `0x377c9c` | 890 |
| `digit4` | `0x378034` | 510 |
| `digit5` | `0x378250` | 742 |
| `digit6` | `0x378554` | 860 |
| `digit7` | `0x3788cc` | 485 |
| `digit8` | `0x378ad0` | 898 |
| `digit9` | `0x378e70` | 898 |
| `ap01_pet_0` | `0x1c5a6c` | 385834 |
| `ap01_pet_1` | `0x3f4b24` | 486765 |
| `ap01_pet_2` | `0x46b8b0` | 221445 |
| `ap01_pet_3` | `0x4a19d4` | 569645 |
| `ap01_pet_4` | `0x37d080` | 490119 |
| `ap01_charge_bank_insert` | `0x643fc0` | 130357 |
| `ap01_charge_safe_intro` | `0x5b067c` | 230831 |
| `ap01_saver_time_0` | `0x28e838` | 187664 |
| `ap01_saver_time_1` | `0x2bc564` | 157250 |
| `ap01_saver_power` | `0x2e2bc4` | 502081 |
| `ap01_weather_large_native_1` | `0x564df0` | 2084 |
| `ap01_weather_large_native_2` | `0x62b9f8` | 1603 |
| `ap01_weather_large_native_3` | `0x62b0fc` | 1081 |
| `ap01_weather_large_native_4` | `0x62b554` | 1157 |
| `ap01_weather_large_native_5` | `0x62995c` | 650 |
| `ap01_weather_large_native_6` | `0x629754` | 489 |
| `ap01_weather_large_native_7` | `0x629e54` | 657 |
| `ap01_weather_large_native_8` | `0x62a104` | 1166 |
| `ap01_weather_large_native_9` | `0x62a5b0` | 1264 |
| `ap01_weather_large_native_10` | `0x62d030` | 1158 |
| `ap01_weather_large_native_11` | `0x62cc70` | 929 |
| `ap01_weather_large_native_12` | `0x62adc4` | 794 |
| `ap01_weather_large_native_13` | `0x62aabc` | 746 |
| `ap01_weather_large_native_14` | `0x629c04` | 561 |
| `ap01_weather_large_native_22` | `0x62c058` | 1528 |
| `ap01_weather_large_native_23` | `0x62c66c` | 1510 |
| `ap01_weather_small_native_1` | `0x3724c0` | 687 |
| `ap01_weather_small_native_2` | `0x37278c` | 698 |
| `ap01_weather_small_native_3` | `0x372038` | 539 |
| `ap01_weather_small_native_4` | `0x372270` | 564 |
| `ap01_weather_small_native_5` | `0x371338` | 345 |
| `ap01_weather_small_native_6` | `0x3711f0` | 300 |
| `ap01_weather_small_native_7` | `0x371618` | 363 |
| `ap01_weather_small_native_8` | `0x3717a0` | 599 |
| `ap01_weather_small_native_9` | `0x371a14` | 623 |
| `ap01_weather_small_native_10` | `0x3730e4` | 604 |
| `ap01_weather_small_native_11` | `0x372ec4` | 516 |
| `ap01_weather_small_native_12` | `0x371e4c` | 462 |
| `ap01_weather_small_native_13` | `0x371ca0` | 398 |
| `ap01_weather_small_native_14` | `0x3714b0` | 330 |
| `ap01_weather_small_native_22` | `0x372a64` | 524 |
| `ap01_weather_small_native_23` | `0x372c8c` | 539 |
| `ap01_weather_tiny_native_1` | `0x252dc4` | 527 |
| `ap01_weather_tiny_native_2` | `0x630f3c` | 593 |
| `ap01_weather_tiny_native_3` | `0x630b4c` | 469 |
| `ap01_weather_tiny_native_4` | `0x630d40` | 478 |
| `ap01_weather_tiny_native_5` | `0x63001c` | 336 |
| `ap01_weather_tiny_native_6` | `0x62ff04` | 250 |
| `ap01_weather_tiny_native_7` | `0x6302d8` | 315 |
| `ap01_weather_tiny_native_8` | `0x630430` | 486 |
| `ap01_weather_tiny_native_9` | `0x630634` | 512 |
| `ap01_weather_tiny_native_10` | `0x631854` | 491 |
| `ap01_weather_tiny_native_11` | `0x631674` | 451 |
| `ap01_weather_tiny_native_12` | `0x6309c0` | 367 |
| `ap01_weather_tiny_native_13` | `0x630850` | 339 |
| `ap01_weather_tiny_native_14` | `0x630188` | 305 |
| `ap01_weather_tiny_native_22` | `0x6311ac` | 579 |
| `ap01_weather_tiny_native_23` | `0x63140c` | 585 |

## 字体

| 重建名称 | 原厂wrapper地址 | 高度 | 已恢复字形数 |
| --- | --- | ---: | ---: |
| `ap01_rom_ascii17` | `0xa02549ac` | 17 | 50 |
| `ap01_rom_body20` | `0xa025488c` | 20 | 117 |
| `ap01_rom_title25` | `0xa02548d4` | 25 | 87 |
| `ap01_rom_clock21` | `0xa02549f4` | 21 | 55 |
| `ap01_rom_month` | `0xa02547b4` | 22 | 60 |
| `ap01_rom_year` | `0xa0254988` | 14 | 31 |
| `ap01_rom_calendar_week` | `0xa037253c` | 12 | 7 |
| `ap01_rom_mini_date` | `0xa0254a60` | 17 | 25 |
| `ap01_rom_weather_text` | `0xa0254820` | 15 | 45 |
| `ap01_rom_mini_week` | `0xa0254844` | 16 | 65 |
| `ap01_rom_temperature` | `0xa0254a84` | 38 | 12 |
| `ap01_rom_guide_title` | `0xa055fb7c` | 20 | 109 |
| `ap01_rom_guide_text` | `0xa02547fc` | 14 | 42 |
| `ap01_rom_charge_gauge` | `0xa0254700` | 15 | 10 |
| `ap01_rom_charge_port` | `0xa0254724` | 9 | 5 |
| `ap01_rom_charge_watt` | `0xa0254748` | 17 | 1 |
| `ap01_rom_charge_number` | `0xa025476c` | 19 | 11 |
| `ap01_rom_charge_status` | `0xa02547d8` | 15 | 18 |
| `ap01_rom_charge_excellent` | `0xa0254aa8` | 18 | 7 |
| `ap01_rom_detail_metric` | `0xa0254a18` | 24 | 28 |
| `ap01_rom_detail_caption` | `0xa0254964` | 15 | 50 |
| `ap01_rom_humidity_digits` | `0xa05647b4` | 12 | 18 |
| `ap01_rom_humidity_unit` | `0xa0564790` | 8 | 1 |
| `ap01_rom_forecast` | `0xa0372584` | 17 | 96 |
| `ap01_rom_weather_note` | `0xa0564748` | 13 | 9 |
| `ap01_rom_weather_temp` | `0xa05647d8` | 28 | 14 |
| `ap01_rom_date_heading` | `0xa055fb58` | 18 | 22 |
| `ap01_rom_mijia_hint` | `0xa0254868` | 17 | 49 |
| `ap01_rom_charge_title` | `0xa0254790` | 17 | 82 |
| `ap01_rom_charge_percent` | `0xa059bee4` | 19 | 11 |
| `ap01_rom_charge_percent_unit` | `0xa059be9c` | 10 | 1 |
| `ap01_rom_charge_port_number` | `0xa0630ad0` | 26 | 11 |
| `ap01_rom_charge_card_label` | `0xa0630af4` | 16 | 20 |
| `ap01_rom_charge_card_unit` | `0xa0630aac` | 13 | 9 |
| `ap01_rom_charge_card_value` | `0xa0630a88` | 12 | 14 |
| `ap01_rom_charge_popup_port` | `0xa066b5ec` | 17 | 7 |
| `ap01_rom_charge_popup_percent` | `0xa066b610` | 30 | 10 |
| `ap01_rom_charge_popup_percent_unit` | `0xa066b5c8` | 15 | 1 |
| `ap01_rom_charge_popup_power` | `0xa066b634` | 28 | 28 |
| `ap01_rom_charge_popup_brand` | `0xa066b658` | 30 | 41 |
| `ap01_rom_charge_protocol_port` | `0xa06015e4` | 15 | 6 |
| `ap01_rom_charge_error` | `0xa02548b0` | 24 | 95 |
| `ap01_rom_charge_device_name` | `0xa066b67c` | 42 | 38 |
| `ap01_rom_guide_welcome` | `0xa0606ac8` | 22 | 31 |
| `ap01_rom_guide_practice_body` | `0xa0372560` | 15 | 77 |
| `ap01_rom_guide_prompt` | `0xa066b5a4` | 14 | 26 |
| `ap01_rom_saver_time` | `0xa03725a8` | 25 | 11 |
| `ap01_rom_saver_decimal` | `0xa0372518` | 48 | 11 |
| `ap01_rom_saver_watt` | `0xa03724f4` | 16 | 1 |
| `ap01_rom_saver_day` | `0xa02549d0` | 16 | 33 |
| `ap01_rom_calendar_subtitle` | `0xa060d91c` | 12 | 92 |
| `ap01_rom_calendar_day` | `0xa060d940` | 18 | 69 |
| `ap01_rom_charge_live_power3` | `0xa062c514` | 25 | 11 |
| `ap01_rom_power_battery` | `0xa025491c` | 21 | 10 |
| `ap01_rom_power_battery_unit` | `0xa02548f8` | 11 | 11 |

## 逆向缺口

- UI：17模块、33构造器已有业务家族级SIM验收；没有逐文件/逐函数/逐分支总账，不能算原厂应用完整逆向。
- 工厂测试：已定位独立滑动器；未见完整工厂业务验收。
- 底座、USB、设置：已有协议/初始化/升级/SIM合同证据，仍需对原件函数、并发、硬件和持久化逐项核账。
- MiIO/MiBLE：采用后续 upper-layer-0041-20261017.md 状态；315函数、537未采集直接callee、161未定向调用，仅为该profile当时的依赖缺口，不是全ROM剩余量。旧seed handoff数字已不能代表后续进展。
- Wi-Fi：knowledge/0041-sim-wifi-selection-gaps.md 保留原厂持久化格式、切网顺序、绑定保留缺口。
- 资源：未纳入项需缩略图与原件引用映射，区分工厂、备用、重复或实际页面用途；55套已恢复字体不代表全ROM字体数量。

依据：application-function-matrix-0041.json、application-rehost-complete-0041-20261017.md、upper-layer-0041-20261017.md、screen-host-append-validation-20261020.md；reverse/rehost/complete-assets.json、asset-index-0041.json。
