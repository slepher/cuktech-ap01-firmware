# 0041 原厂 C 文件 → 函数 → 资源引用与逆向缺口

ROM SHA256：`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射基址 `0x9ffff000`。

本清单索引现有离线 REA/Ghidra 证据，不是新一轮全 ROM 反编译。当前 REA MCP 无活动目标，Windows 提供方声明的支持范围未包含 RV32，未重新打开原件。

## 状态口径

- **已完成的范围**：33 项构造器对应业务家族在既有 SIM 验收中通过；原件资源已提取/字体已恢复的范围另计。
- **部分完成**：已有原件函数分析、文件路径引用或资源引用；不等于整个函数、C 文件或原厂硬件行为已完成。
- **待补关联**：此次扫描的离线证据没有建立对应边，不能解释为从未分析、资源未使用或代码不存在。
- 单个函数引用多个 C 路径时保留全部关联，不按邻近地址或名称强行归属。函数名列是日志中的名称提及，不保证就是当前函数名。
- 资源边仅指直接数据地址/校验过的 LVGL 描述符/字体 wrapper；不把整个证据文件中共同出现的资源归给全部函数。

## 数量

- 文件路径 33 个；建立函数关联 14 个，待补关联 19 个。
- 收录函数/历史 seed 98 个；有文件路径关联 37 个，多文件关联 4 个。
- 图像及字体节点 265 个；有函数引用 90 个；函数—资源组合 125 对。
- 从原件校验得到图像描述符 210 个；完整 C 文件认证数为 0，不据此计算全 ROM 完成率。

## 文件覆盖总表

| 原厂/定制路径 | 函数关联数 | 已完成范围 | 仍缺 |
| --- | ---: | --- | --- |
| `PogoPinMng/PogoPinMng.c` | 0 | 已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证 | 先补路径→函数关联；并对照专项证据 |
| `PogoPinMng/UartComm.c` | 0 | 已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证 | 先补路径→函数关联；并对照专项证据 |
| `PogoPinMng/WeatherApi.c` | 0 | 已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证 | 先补路径→函数关联；并对照专项证据 |
| `PogoPinMng/FactoryTestMode.c` | 0 | 已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证 | 先补路径→函数关联；并对照专项证据 |
| `PogoPinMng/MiIotMng.c` | 0 | 已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证 | 先补路径→函数关联；并对照专项证据 |
| `PogoPinMng/BuzzerMng.c` | 0 | 已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证 | 先补路径→函数关联；并对照专项证据 |
| `PogoPinMng/UiIFaceMng.c` | 0 | 已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证 | 先补路径→函数关联；并对照专项证据 |
| `PogoPinMng/UsbIfaceOta.c` | 0 | 已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证 | 先补路径→函数关联；并对照专项证据 |
| `PogoPinMng/UsbIfaceMng.c` | 2 | 已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证 | 全函数与分支、间接引用、硬件/持久化 |
| `PogoPinMng/EsUnitProtocol.c` | 0 | 已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证 | 先补路径→函数关联；并对照专项证据 |
| `lvgl_ui_main.c` | 0 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 先补路径→函数关联；并对照专项证据 |
| `SystemSettings/SystemSettings.c` | 0 | 已有SIM保存服务；原厂持久化与Wi-Fi格式兼容性仍开放 | 先补路径→函数关联；并对照专项证据 |
| `factory_ui/lv_window_slider.c` | 0 | 工厂滑动器已有定位；未见完整工厂测试流程验收 | 先补路径→函数关联；并对照专项证据 |
| `lv_lunar_calendar/lv_calendar_ck.c` | 0 | 已有农历、日期表及日历行为恢复/测试；函数到C路径归属仍须核对 | 先补路径→函数关联；并对照专项证据 |
| `lv_comp_calendar/lv_calendar_comp.c` | 0 | 已有农历、日期表及日历行为恢复/测试；函数到C路径归属仍须核对 | 先补路径→函数关联；并对照专项证据 |
| `lv_power_ui/lv_ap01_ui.c` | 0 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 先补路径→函数关联；并对照专项证据 |
| `lv_power_ui/lv_ui_theme.c` | 3 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_guidance.c` | 4 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_wx_data_trans.c` | 0 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 先补路径→函数关联；并对照专项证据 |
| `lv_power_ui/lv_boot_anim.c` | 0 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 先补路径→函数关联；并对照专项证据 |
| `lv_power_ui/lv_ui_scr_saver.c` | 2 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_setting_data.c` | 0 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 先补路径→函数关联；并对照专项证据 |
| `lv_power_ui/lv_ui_base.c` | 4 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_ui_setting_dtl.c` | 4 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_ui_power1_dtl.c` | 5 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_ui_time1_dtl.c` | 2 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_ui_date1_dtl.c` | 1 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_ui_wx1_dtl.c` | 2 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_ui_window.c` | 3 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_ui_cuk_con.c` | 7 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_ui_pop_up.c` | 3 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `lv_power_ui/lv_ui_power2_dtl.c` | 4 | 已有UI家族重建/验收；不替代本文件全部函数归属与分支核账 | 全函数与分支、间接引用、硬件/持久化 |
| `miio_sdk/miio_instance/client/miio_client.c` | 0 | MiIO 162根及90命令关联已有后续局部实现审阅；不能由单一路径代表全进程 | 先补路径→函数关联；并对照专项证据 |

## PogoPinMng/PogoPinMng.c

已有进展：已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证。[专项依据](../../../reverse/reports/ap01/mijia-task-dependencies-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## PogoPinMng/UartComm.c

已有进展：已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证。[专项依据](../../../reverse/reports/ap01/mijia-task-dependencies-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## PogoPinMng/WeatherApi.c

已有进展：已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证。[专项依据](../../../reverse/reports/ap01/mijia-task-dependencies-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## PogoPinMng/FactoryTestMode.c

已有进展：已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证。[专项依据](../../../reverse/reports/ap01/mijia-task-dependencies-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## PogoPinMng/MiIotMng.c

已有进展：已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证。[专项依据](../../../reverse/reports/ap01/mijia-task-dependencies-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## PogoPinMng/BuzzerMng.c

已有进展：已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证。[专项依据](../../../reverse/reports/ap01/mijia-task-dependencies-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## PogoPinMng/UiIFaceMng.c

已有进展：已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证。[专项依据](../../../reverse/reports/ap01/mijia-task-dependencies-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## PogoPinMng/UsbIfaceOta.c

已有进展：已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证。[专项依据](../../../reverse/reports/ap01/mijia-task-dependencies-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## PogoPinMng/UsbIfaceMng.c

已有进展：已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证。[专项依据](../../../reverse/reports/ap01/mijia-task-dependencies-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa01b2634` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa01b272c` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |

## PogoPinMng/EsUnitProtocol.c

已有进展：已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证。[专项依据](../../../reverse/reports/ap01/mijia-task-dependencies-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## lvgl_ui_main.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## SystemSettings/SystemSettings.c

已有进展：已有SIM保存服务；原厂持久化与Wi-Fi格式兼容性仍开放。[专项依据](../../../reverse/reports/ap01/knowledge/0041-sim-wifi-selection-gaps.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## factory_ui/lv_window_slider.c

已有进展：工厂滑动器已有定位；未见完整工厂测试流程验收。[专项依据](../../../reverse/reports/ap01/multi-screen-app-host-0041.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## lv_lunar_calendar/lv_calendar_ck.c

已有进展：已有农历、日期表及日历行为恢复/测试；函数到C路径归属仍须核对。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## lv_comp_calendar/lv_calendar_comp.c

已有进展：已有农历、日期表及日历行为恢复/测试；函数到C路径归属仍须核对。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## lv_power_ui/lv_ap01_ui.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## lv_power_ui/lv_ui_theme.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00ab628` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；已完成原件滑动有界执行（合成对象，无完整UI/实机）；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |
| `0xa00af262` | `lv_page_ui_app_ota_pop_up_create` | `FONT@0xa02548b0` (ap01_rom_charge_error) | 部分；多文件/内联归属待核；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |
| `0xa00afc88` | `lv_page_ui_time1_dtl1_create`, `lv_page_ui_date1_dtl1_create`, `lv_win_ui_setting_dtl_create`, `lv_page_ui_setting_dtl1_create`, `lv_win_ui_time1_dtl_create`, `lv_win_ui_date1_dtl_create`, `lv_win_ui_power1_dtl_create`, `lv_win_ui_wx1_dtl_create`；另 1 项见 JSON | `FONT@0xa0254790` (ap01_rom_charge_title)<br>`FONT@0xa025488c` (ap01_rom_body20)<br>`FONT@0xa02548d4` (ap01_rom_title25)<br>`FONT@0xa02549f4` (ap01_rom_clock21)<br>`FONT@0xa055fb58` (ap01_rom_date_heading) | 部分；多文件/内联归属待核；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json), [main-knob-0041-round2.json](../../../reverse/rehost/main-knob-0041-round2.json) |

## lv_power_ui/lv_guidance.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00ec490` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[miio-mible-rea-0041.evidence.json](../../../reverse/rehost/miio-mible-rea-0041.evidence.json) |
| `0xa00ed93c` | `j_win_ui_guid_dtl_event_custom_handler` | `PNG@0x56f790` (ap01_guide_practice_power)<br>`PNG@0x571eb8` (ap01_guide_practice_c1_done)<br>`PNG@0x57f8d8` (ap01_guide_practice_turn_done)<br>`PNG@0x5894c4` (ap01_guide_turn)<br>`PNG@0x593064` (ap01_guide_press) | 部分；日志路径关联；[guide-0041-round2.json](../../../reverse/rehost/guide-0041-round2.json) |
| `0xa01b10f0` | `lv_page_ui_opn_guid_dtl2_create`, `lv_win_ui_guidance_dtl_create` | `FONT@0xa02547fc` (ap01_rom_guide_text)<br>`FONT@0xa0372584` (ap01_rom_forecast)<br>`FONT@0xa055fb7c` (ap01_rom_guide_title)<br>`PNG@0x5894c4` (ap01_guide_turn)<br>`PNG@0x66bd44` (ap01_guide_button) | 部分；日志路径关联；[settings-0041-round2e.json](../../../reverse/rehost/settings-0041-round2e.json) |
| `0xa01b14be` | `lv_page_ui_get_start_guid_dtl3_create` | `FONT@0xa0254790` (ap01_rom_charge_title)<br>`PNG@0x36ff8c` (ap01_guide_bubble50)<br>`PNG@0x370230` (ap01_guide_bubble70)<br>`PNG@0x370510` (ap01_guide_bubble90)<br>`FONT@0xa0372560` (ap01_rom_guide_practice_body)<br>`FONT@0xa0372584` (ap01_rom_forecast)<br>`PNG@0x575938` (ap01_guide_practice_intro)<br>`FONT@0xa0606ac8` (ap01_rom_guide_welcome)<br>`FONT@0xa066b5a4` (ap01_rom_guide_prompt) | 部分；日志路径关联；[guide-practice-0041-round2.json](../../../reverse/rehost/guide-practice-0041-round2.json) |

## lv_power_ui/lv_wx_data_trans.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## lv_power_ui/lv_boot_anim.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## lv_power_ui/lv_ui_scr_saver.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00a7766` | `lv_page_ui_scr_saver_tim2_create`, `lv_page_ui_scr_saver_pwr_create`, `lv_win_ui_scr_saver_dtl_create` | `PNG@0x252dc4` (ap01_saver_thermometer/ap01_time_temperature_icon/ap01_weather_tiny_native_1)<br>`FONT@0xa0254790` (ap01_rom_charge_title)<br>`FONT@0xa02549d0` (ap01_rom_saver_day)<br>`FONT@0xa02549f4` (ap01_rom_clock21)<br>`FONT@0xa0254a60` (ap01_rom_mini_date)<br>`GIF@0x28e838` (ap01_saver_time_0)<br>`GIF@0x2e2bc4` (ap01_saver_power)<br>`PNG@0x365184` (ap01_saver_curve)<br>`PNG@0x365dc0` (ap01_saver_glow_top)<br>`PNG@0x36c978` (ap01_saver_glow_bottom)<br>`PNG@0x37082c` (ap01_saver_fast)<br>`FONT@0xa03724f4` (ap01_rom_saver_watt)<br>`FONT@0xa0372518` (ap01_rom_saver_decimal)<br>`FONT@0xa0372584` (ap01_rom_forecast)<br>`FONT@0xa03725a8` (ap01_rom_saver_time)<br>`PNG@0x3773c4` (未命名)<br>`PNG@0x377550` (未命名) | 部分；多文件/内联归属待核；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |
| `0xa00ab834` | `j_win_ui_scr_saver_dtl_event_custom_handler` | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |

## lv_power_ui/lv_setting_data.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## lv_power_ui/lv_ui_base.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00a72ae` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |
| `0xa00a7334` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |
| `0xa00a7766` | `lv_page_ui_scr_saver_tim2_create`, `lv_page_ui_scr_saver_pwr_create`, `lv_win_ui_scr_saver_dtl_create` | `PNG@0x252dc4` (ap01_saver_thermometer/ap01_time_temperature_icon/ap01_weather_tiny_native_1)<br>`FONT@0xa0254790` (ap01_rom_charge_title)<br>`FONT@0xa02549d0` (ap01_rom_saver_day)<br>`FONT@0xa02549f4` (ap01_rom_clock21)<br>`FONT@0xa0254a60` (ap01_rom_mini_date)<br>`GIF@0x28e838` (ap01_saver_time_0)<br>`GIF@0x2e2bc4` (ap01_saver_power)<br>`PNG@0x365184` (ap01_saver_curve)<br>`PNG@0x365dc0` (ap01_saver_glow_top)<br>`PNG@0x36c978` (ap01_saver_glow_bottom)<br>`PNG@0x37082c` (ap01_saver_fast)<br>`FONT@0xa03724f4` (ap01_rom_saver_watt)<br>`FONT@0xa0372518` (ap01_rom_saver_decimal)<br>`FONT@0xa0372584` (ap01_rom_forecast)<br>`FONT@0xa03725a8` (ap01_rom_saver_time)<br>`PNG@0x3773c4` (未命名)<br>`PNG@0x377550` (未命名) | 部分；多文件/内联归属待核；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |
| `0xa00af262` | `lv_page_ui_app_ota_pop_up_create` | `FONT@0xa02548b0` (ap01_rom_charge_error) | 部分；多文件/内联归属待核；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |

## lv_power_ui/lv_ui_setting_dtl.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00af262` | `lv_page_ui_app_ota_pop_up_create` | `FONT@0xa02548b0` (ap01_rom_charge_error) | 部分；多文件/内联归属待核；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |
| `0xa00afc88` | `lv_page_ui_time1_dtl1_create`, `lv_page_ui_date1_dtl1_create`, `lv_win_ui_setting_dtl_create`, `lv_page_ui_setting_dtl1_create`, `lv_win_ui_time1_dtl_create`, `lv_win_ui_date1_dtl_create`, `lv_win_ui_power1_dtl_create`, `lv_win_ui_wx1_dtl_create`；另 1 项见 JSON | `FONT@0xa0254790` (ap01_rom_charge_title)<br>`FONT@0xa025488c` (ap01_rom_body20)<br>`FONT@0xa02548d4` (ap01_rom_title25)<br>`FONT@0xa02549f4` (ap01_rom_clock21)<br>`FONT@0xa055fb58` (ap01_rom_date_heading) | 部分；多文件/内联归属待核；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json), [main-knob-0041-round2.json](../../../reverse/rehost/main-knob-0041-round2.json) |
| `0xa00fd1ac` | `j_win_ui_setting_dtl_event_custom_handler`, `lv_page_ui_setting_dtl8_SFR_create`, `lv_page_ui_setting_dtl5_ver_info_create`, `lv_page_ui_setting_dtl4_scr_brt_create` | `FONT@0xa025488c` (ap01_rom_body20)<br>`FONT@0xa02548d4` (ap01_rom_title25)<br>`FONT@0xa02549f4` (ap01_rom_clock21)<br>`FONT@0xa0254a18` (ap01_rom_detail_metric)<br>`FONT@0xa0372584` (ap01_rom_forecast)<br>`PNG@0x55f9ec` (ap01_brightness_row)<br>`FONT@0xa055fb7c` (ap01_rom_guide_title)<br>`PNG@0x600670` (未命名)<br>`PNG@0x607894` (ap01_brightness_icon) | 部分；日志路径关联；[settings-0041-round2b.json](../../../reverse/rehost/settings-0041-round2b.json), [settings-0041-round2c.json](../../../reverse/rehost/settings-0041-round2c.json) |
| `0xa01afb66` | `lv_page_ui_setting_dtl2_create` | `FONT@0xa025488c` (ap01_rom_body20)<br>`FONT@0xa02549f4` (ap01_rom_clock21) | 部分；日志路径关联；[settings-0041-round2d.json](../../../reverse/rehost/settings-0041-round2d.json) |

## lv_power_ui/lv_ui_power1_dtl.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00afc88` | `lv_page_ui_time1_dtl1_create`, `lv_page_ui_date1_dtl1_create`, `lv_win_ui_setting_dtl_create`, `lv_page_ui_setting_dtl1_create`, `lv_win_ui_time1_dtl_create`, `lv_win_ui_date1_dtl_create`, `lv_win_ui_power1_dtl_create`, `lv_win_ui_wx1_dtl_create`；另 1 项见 JSON | `FONT@0xa0254790` (ap01_rom_charge_title)<br>`FONT@0xa025488c` (ap01_rom_body20)<br>`FONT@0xa02548d4` (ap01_rom_title25)<br>`FONT@0xa02549f4` (ap01_rom_clock21)<br>`FONT@0xa055fb58` (ap01_rom_date_heading) | 部分；多文件/内联归属待核；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json), [main-knob-0041-round2.json](../../../reverse/rehost/main-knob-0041-round2.json) |
| `0xa00f1d0e` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa00f1f70` | `j_page_ui_pwr1_dtl7_popup_timer_xcb` | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa00f2bee` | `j_page_ui_pwr1_dtl7_gif_ready_event_cb` | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa00f5288` | `j_win_ui_power1_dtl_item_info_change_cb` | `FONT@0xa0254844` (ap01_rom_mini_week)<br>`FONT@0xa02549ac` (ap01_rom_ascii17)<br>`PNG@0x55f9ec` (ap01_brightness_row)<br>`PNG@0x560488` (ap01_charge_port_card) | 部分；多文件/内联归属待核；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |

## lv_power_ui/lv_ui_time1_dtl.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00afc88` | `lv_page_ui_time1_dtl1_create`, `lv_page_ui_date1_dtl1_create`, `lv_win_ui_setting_dtl_create`, `lv_page_ui_setting_dtl1_create`, `lv_win_ui_time1_dtl_create`, `lv_win_ui_date1_dtl_create`, `lv_win_ui_power1_dtl_create`, `lv_win_ui_wx1_dtl_create`；另 1 项见 JSON | `FONT@0xa0254790` (ap01_rom_charge_title)<br>`FONT@0xa025488c` (ap01_rom_body20)<br>`FONT@0xa02548d4` (ap01_rom_title25)<br>`FONT@0xa02549f4` (ap01_rom_clock21)<br>`FONT@0xa055fb58` (ap01_rom_date_heading) | 部分；多文件/内联归属待核；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json), [main-knob-0041-round2.json](../../../reverse/rehost/main-knob-0041-round2.json) |
| `0xa00b3252` | `j_win_ui_time1_dtl_event_custom_handler` | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |

## lv_power_ui/lv_ui_date1_dtl.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00afc88` | `lv_page_ui_time1_dtl1_create`, `lv_page_ui_date1_dtl1_create`, `lv_win_ui_setting_dtl_create`, `lv_page_ui_setting_dtl1_create`, `lv_win_ui_time1_dtl_create`, `lv_win_ui_date1_dtl_create`, `lv_win_ui_power1_dtl_create`, `lv_win_ui_wx1_dtl_create`；另 1 项见 JSON | `FONT@0xa0254790` (ap01_rom_charge_title)<br>`FONT@0xa025488c` (ap01_rom_body20)<br>`FONT@0xa02548d4` (ap01_rom_title25)<br>`FONT@0xa02549f4` (ap01_rom_clock21)<br>`FONT@0xa055fb58` (ap01_rom_date_heading) | 部分；多文件/内联归属待核；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json), [main-knob-0041-round2.json](../../../reverse/rehost/main-knob-0041-round2.json) |

## lv_power_ui/lv_ui_wx1_dtl.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00afc88` | `lv_page_ui_time1_dtl1_create`, `lv_page_ui_date1_dtl1_create`, `lv_win_ui_setting_dtl_create`, `lv_page_ui_setting_dtl1_create`, `lv_win_ui_time1_dtl_create`, `lv_win_ui_date1_dtl_create`, `lv_win_ui_power1_dtl_create`, `lv_win_ui_wx1_dtl_create`；另 1 项见 JSON | `FONT@0xa0254790` (ap01_rom_charge_title)<br>`FONT@0xa025488c` (ap01_rom_body20)<br>`FONT@0xa02548d4` (ap01_rom_title25)<br>`FONT@0xa02549f4` (ap01_rom_clock21)<br>`FONT@0xa055fb58` (ap01_rom_date_heading) | 部分；多文件/内联归属待核；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json), [main-knob-0041-round2.json](../../../reverse/rehost/main-knob-0041-round2.json) |
| `0xa00b35ee` | `j_win_ui_wx1_dtl_event_custom_handler` | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |

## lv_power_ui/lv_ui_window.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00b2ff4` | `lv_window_get_active_win_idx` | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |
| `0xa00b3036` | `lv_window_get_win_obj_by_idx` | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |
| `0xa00b3106` | `lv_window_set_active_by_idx` | 待补：此证据未建立直接资源边 | 部分；日志路径关联；已完成原件滑动有界执行（合成对象，无完整UI/实机）；[screen-host-append-20261020.json](../../../reverse/analysis/screen-host-append-20261020.json) |

## lv_power_ui/lv_ui_cuk_con.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00ec6f2` | `j_page_ui_cc_puw_gif_finish_event_cb` | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa00ef1d4` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-0041-round4.json](../../../reverse/rehost/charge-0041-round4.json) |
| `0xa00ef2da` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-0041-round4.json](../../../reverse/rehost/charge-0041-round4.json) |
| `0xa00f1102` | `lv_page_ui_cuk_con_ins_dev_create` | `FONT@0xa0254790` (ap01_rom_charge_title)<br>`FONT@0xa059be9c` (ap01_rom_charge_percent_unit)<br>`FONT@0xa059bee4` (ap01_rom_charge_percent) | 部分；日志路径关联；[charge-0041-round4.json](../../../reverse/rehost/charge-0041-round4.json) |
| `0xa00f44e8` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa00f4610` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa01b0f02` | `lv_page_ui_cuk_con_pop_up_create` | `GIF@0x643fc0` (ap01_charge_bank_insert) | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |

## lv_power_ui/lv_ui_pop_up.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00f1e48` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa01b0644` | `lv_page_ui_anxin_dev_ins_pop_up_create` | `FONT@0xa0254844` (ap01_rom_mini_week)<br>`FONT@0xa02549f4` (ap01_rom_clock21)<br>`FONT@0xa066b5c8` (ap01_rom_charge_popup_percent_unit)<br>`FONT@0xa066b5ec` (ap01_rom_charge_popup_port)<br>`FONT@0xa066b610` (ap01_rom_charge_popup_percent)<br>`FONT@0xa066b634` (ap01_rom_charge_popup_power)<br>`FONT@0xa066b658` (ap01_rom_charge_popup_brand) | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa01b0b2c` | `lv_page_ui_dev_ins_pop_up_create` | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |

## lv_power_ui/lv_ui_power2_dtl.c

已有进展：已有UI家族重建/验收；不替代本文件全部函数归属与分支核账。[专项依据](../../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| `0xa00f3b36` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa00f40ee` | 匿名/未保留名称 | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa00f5288` | `j_win_ui_power1_dtl_item_info_change_cb` | `FONT@0xa0254844` (ap01_rom_mini_week)<br>`FONT@0xa02549ac` (ap01_rom_ascii17)<br>`PNG@0x55f9ec` (ap01_brightness_row)<br>`PNG@0x560488` (ap01_charge_port_card) | 部分；多文件/内联归属待核；[charge-complete-0041.json](../../../reverse/rehost/charge-complete-0041.json) |
| `0xa01afd56` | `lv_page_ui_power2_dtl2_port_dtl_create` | 待补：此证据未建立直接资源边 | 部分；日志路径关联；[charge-0041-round4.json](../../../reverse/rehost/charge-0041-round4.json) |

## miio_sdk/miio_instance/client/miio_client.c

已有进展：MiIO 162根及90命令关联已有后续局部实现审阅；不能由单一路径代表全进程。[专项依据](../../../reverse/reports/ap01/upper-layer-0041-20261017.md)。

| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |
| --- | --- | --- | --- |
| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |

## 33 项既有 SIM 验收对照

以下保留既有通过结论；命中地址仅是构造器名字符串的引用，不直接当作构造器入口。

| 构造器名称 | 家族 | 已完成范围 | 名称提及所在函数/seed |
| --- | --- | --- | --- |
| `lv_page_ui_anxin_dev_ins_pop_up_create` | charge | passed-in-sim（SIM 家族场景） | `0xa01b0644` |
| `lv_page_ui_app_ota_pop_up_create` | system | passed-in-sim（SIM 家族场景） | `0xa00af262` |
| `lv_page_ui_boot_anim_create` | guide | passed-in-sim（SIM 家族场景） | `0xa005cc1e` |
| `lv_page_ui_cuk_con_ins_dev_create` | charge | passed-in-sim（SIM 家族场景） | `0xa00f1102` |
| `lv_page_ui_cuk_con_pop_up_create` | charge | passed-in-sim（SIM 家族场景） | `0xa01b0f02` |
| `lv_page_ui_date1_create` | weather-calendar | passed-in-sim（SIM 家族场景） | `0xa005cc1e` |
| `lv_page_ui_date1_dtl1_create` | weather-calendar | passed-in-sim（SIM 家族场景） | `0xa00afc88` |
| `lv_page_ui_dev_ins_pop_up_create` | charge | passed-in-sim（SIM 家族场景） | `0xa01b0b2c` |
| `lv_page_ui_get_start_guid_dtl3_create` | guide | passed-in-sim（SIM 家族场景） | `0xa01b14be` |
| `lv_page_ui_mijia_dtl1_create` | system | passed-in-sim（SIM 家族场景） | `0xa005cc1e` |
| `lv_page_ui_opn_guid_dtl2_create` | guide | passed-in-sim（SIM 家族场景） | `0xa01b10f0` |
| `lv_page_ui_power1_create` | charge | passed-in-sim（SIM 家族场景） | `0xa005cc1e` |
| `lv_page_ui_power1_dtl1_list_create` | charge | passed-in-sim（SIM 家族场景） | 待补名称→入口对应 |
| `lv_page_ui_power1_dtl3_mode_sel_create` | charge | passed-in-sim（SIM 家族场景） | 待补名称→入口对应 |
| `lv_page_ui_power1_dtl6_prot_asst_create` | charge | passed-in-sim（SIM 家族场景） | 待补名称→入口对应 |
| `lv_page_ui_power1_dtl7_anxin_chg_create` | charge | passed-in-sim（SIM 家族场景） | 待补名称→入口对应 |
| `lv_page_ui_power2_dtl2_port_dtl_create` | charge | passed-in-sim（SIM 家族场景） | `0xa01afd56` |
| `lv_page_ui_power2_dtl4_port_switch` | charge | passed-in-sim（SIM 家族场景） | 待补名称→入口对应 |
| `lv_page_ui_power2_dtl5_safechg_setting` | charge | passed-in-sim（SIM 家族场景） | 待补名称→入口对应 |
| `lv_page_ui_scr_saver_pwr_create` | guide | passed-in-sim（SIM 家族场景） | `0xa00a7766` |
| `lv_page_ui_scr_saver_tim2_create` | guide | passed-in-sim（SIM 家族场景） | `0xa00a7766` |
| `lv_page_ui_setting_create` | system | passed-in-sim（SIM 家族场景） | `0xa005cc1e` |
| `lv_page_ui_setting_dtl1_create` | system | passed-in-sim（SIM 家族场景） | `0xa00afc88` |
| `lv_page_ui_setting_dtl2_create` | system | passed-in-sim（SIM 家族场景） | `0xa01afb66` |
| `lv_page_ui_setting_dtl4_scr_brt_create` | system | passed-in-sim（SIM 家族场景） | `0xa00fd1ac` |
| `lv_page_ui_setting_dtl5_ver_info_create` | system | passed-in-sim（SIM 家族场景） | `0xa00fd1ac` |
| `lv_page_ui_setting_dtl6_ota_create` | system | passed-in-sim（SIM 家族场景） | 待补名称→入口对应 |
| `lv_page_ui_setting_dtl8_SFR_create` | system | passed-in-sim（SIM 家族场景） | `0xa00fd1ac` |
| `lv_page_ui_time1_create` | weather-calendar | passed-in-sim（SIM 家族场景） | `0xa005cc1e` |
| `lv_page_ui_time1_dtl1_create` | weather-calendar | passed-in-sim（SIM 家族场景） | `0xa00afc88` |
| `lv_page_ui_virchar_create` | system | passed-in-sim（SIM 家族场景） | `0xa005cc1e` |
| `lv_page_ui_weather1_create` | weather-calendar | passed-in-sim（SIM 家族场景） | `0xa005cc1e` |
| `lv_page_ui_wx1_dtl1_create` | weather-calendar | passed-in-sim（SIM 家族场景） | 待补名称→入口对应 |

## 已有函数证据、但 C 文件归属待补

| 函数/seed | 资源引用 | 证据文件 |
| --- | --- | --- |
| `0xa0000000` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass1.txt |
| `0xa0024906` | 待补 | reverse/rehost/page-logic-0041.json |
| `0xa0029640` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass2.txt |
| `0xa0029b1e` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass1.txt |
| `0xa0055a14` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass3.txt |
| `0xa005974a` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass2.txt |
| `0xa0059762` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass3.txt |
| `0xa005cc1e` | GIF@0x1c5a6c, PNG@0x242680, PNG@0x2432bc, PNG@0x243590, PNG@0x243824, PNG@0x243950, PNG@0x247f68, PNG@0x2481cc, PNG@0x248b30, PNG@0x251d80, PNG@0x2528cc, PNG@0x252aa8, PNG@0x252c14, PNG@0x252dc4, PNG@0x252ff0, PNG@0x253810, PNG@0x2539d8, FONT@0xa0254700, FONT@0xa0254724, FONT@0xa0254748, FONT@0xa025476c, FONT@0xa0254790, FONT@0xa02547b4, FONT@0xa02547d8, FONT@0xa02547fc, FONT@0xa0254820, FONT@0xa0254844, FONT@0xa0254868, FONT@0xa025488c, FONT@0xa02548b0, FONT@0xa02548d4, FONT@0xa02548f8, FONT@0xa025491c, FONT@0xa0254964, FONT@0xa0254988, FONT@0xa02549ac, FONT@0xa02549d0, FONT@0xa02549f4, FONT@0xa0254a18, FONT@0xa0254a60, FONT@0xa0254a84, FONT@0xa0254aa8, PNG@0x255b18, PNG@0x255ea0, PNG@0x25621c | reverse/analysis/0041-20261013/0041-ghidra-pass3.txt, reverse/rehost/page-logic-0041.json |
| `0xa005f222` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa0061d20` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa00626ea` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa0062882` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa00629c6` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa0062d28` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa0066296` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass5.txt |
| `0xa0067296` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass4.txt |
| `0xa0069dd4` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa006f5ce` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass1.txt |
| `0xa00703ce` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass3.txt |
| `0xa0074b94` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass2.txt |
| `0xa0074d30` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass2.txt |
| `0xa0074ea2` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass2.txt |
| `0xa00786a0` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass4.txt |
| `0xa00b2f6c` | 待补 | reverse/analysis/screen-host-append-20261020.json |
| `0xa00b3080` | 待补 | reverse/analysis/screen-host-append-20261020.json |
| `0xa00b30c0` | 待补 | reverse/analysis/screen-host-append-20261020.json |
| `0xa00b51d8` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass3.txt |
| `0xa00bb880` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa00d91c6` | 待补 | reverse/analysis/screen-host-append-20261020.json |
| `0xa00ed8e2` | PNG@0x575938 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa00f388c` | 待补 | reverse/rehost/charge-complete-0041.json |
| `0xa00f3c22` | 待补 | reverse/rehost/charge-complete-0041.json |
| `0xa00f50c2` | 待补 | reverse/rehost/charge-complete-0041.json |
| `0xa011085c` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass2.txt |
| `0xa01158f6` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa01202e4` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa0125d04` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa0125d66` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa0129f0c` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa012a036` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa012a29e` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa012a44c` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa012a6fe` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa012abfa` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa012b0a2` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa01311fe` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa01972fa` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass5.txt |
| `0xa01977cc` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa0197822` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa01986fa` | PNG@0x62fd0c, FONT@0xa0630a88, FONT@0xa0630aac, FONT@0xa0630ad0, FONT@0xa0630af4 | reverse/rehost/charge-0041-round4.json |
| `0xa0198a9e` | 待补 | reverse/rehost/charge-0041-round4.json |
| `0xa0199e66` | 待补 | reverse/analysis/0041-20261013/0041-ghidra-pass3.txt |
| `0xa019cdc0` | FONT@0xa025488c, PNG@0x55f694 | reverse/rehost/settings-0041-round2.json |
| `0xa019ce64` | FONT@0xa025488c, PNG@0x55f694 | reverse/rehost/settings-0041-round2b.json |
| `0xa01a2c02` | FONT@0xa025488c, PNG@0x55f694 | reverse/rehost/settings-0041-round2.json |
| `0xa01a96aa` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa01ab298` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa01b60bc` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa01b6146` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa01b6a84` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |
| `0xa01b82e8` | 待补 | reverse/rehost/miio-mible-rea-0041.evidence.json |

## 资源归属缺口

下列项有已验证图像边界或既有字体清单，但本次证据未建立函数引用。已用于 SIM 也仍可能缺少原件归属边。

| 资源 | 重建名称 | 提取/重建状态 | 下一步 |
| --- | --- | --- | --- |
| `PNG@0x2516dc` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x251878` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x251a48` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x251bf0` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x370d34` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x370ee0` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x37107c` | ap01_wifi_off | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3711f0` | ap01_weather_small_native_6 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x371338` | ap01_weather_small_native_5 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3714b0` | ap01_weather_small_native_14 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x371618` | ap01_weather_small_native_7 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3717a0` | ap01_weather_small_native_8 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x371a14` | ap01_weather_small_native_9 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x371ca0` | ap01_weather_small_native_13 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x371e4c` | ap01_weather_small_native_12 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x372038` | ap01_weather_small_native_3 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x372270` | ap01_weather_small_native_4 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3724c0` | ap01_weather_small_native_1 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x37278c` | ap01_weather_small_native_2 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x372a64` | ap01_weather_small_native_22 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x372c8c` | ap01_weather_small_native_23 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x372ec4` | ap01_weather_small_native_11 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3730e4` | ap01_weather_small_native_10 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x37360c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3738b8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x373c70` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x373de8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x374018` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x374274` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3745a4` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x374888` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x374c64` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x374e64` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x375210` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x375470` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3757e8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x375ab4` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x375eb4` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x37603c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3763b8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3766bc` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x376af0` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x376dcc` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3771f8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3772dc` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x377790` | digit1 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x377998` | digit2 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x377c9c` | digit3 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x378034` | digit4 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x378250` | digit5 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x378554` | digit6 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3788cc` | digit7 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x378ad0` | digit8 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x378e70` | digit9 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x3798b0` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x379a50` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x379d60` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x37a11c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x37a38c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x37a674` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x37aa38` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x37abc8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x37afc0` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x532ba8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5335c4` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5342e4` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5350d8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x535f14` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x536e9c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x537eb4` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x538f4c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x53a040` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x53b1cc` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x53c3e8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x53d684` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x53e63c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x53f630` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x540668` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5416cc` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x542130` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x542bfc` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5436e8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x54429c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x544e94` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x545af0` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5467ac` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5474c0` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x548244` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x549010` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x549e1c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x54ac58` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x54bad0` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x54caac` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x54da34` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x55675c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x55f3f4` | ap01_charge_mode_icon | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x55f530` | ap01_charge_cable_icon | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x55fd60` | ap01_charge_mode_card | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5600e4` | ap01_system_version_card | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x564644` | ap01_weather_aqi_scale | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x564df0` | ap01_weather_large_native_1 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5e99cc` | ap01_charge_safe_title | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5e9e18` | ap01_charge_safe_hint | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5ea9e0` | ap01_charge_safe_caption | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5eb7e4` | ap01_charge_protocol_scan | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5ebffc` | ap01_charge_protocol_title | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5ecc1c` | ap01_charge_protocol_bg | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x5fef60` | ap01_charge_protocol_caption | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x6015ac` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x605d24` | ap01_system_ota_success | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x60759c` | ap01_system_confirm_button | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x6294f8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x629754` | ap01_weather_large_native_6 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62995c` | ap01_weather_large_native_5 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x629c04` | ap01_weather_large_native_14 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x629e54` | ap01_weather_large_native_7 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62a104` | ap01_weather_large_native_8 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62a5b0` | ap01_weather_large_native_9 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62aabc` | ap01_weather_large_native_13 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62adc4` | ap01_weather_large_native_12 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62b0fc` | ap01_weather_large_native_3 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62b554` | ap01_weather_large_native_4 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62b9f8` | ap01_weather_large_native_2 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62c058` | ap01_weather_large_native_22 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62c66c` | ap01_weather_large_native_23 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62cc70` | ap01_weather_large_native_11 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62d030` | ap01_weather_large_native_10 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62f440` | ap01_arc | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x62ff04` | ap01_weather_tiny_native_6 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x63001c` | ap01_weather_tiny_native_5 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x630188` | ap01_weather_tiny_native_14 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x6302d8` | ap01_weather_tiny_native_7 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x630430` | ap01_weather_tiny_native_8 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x630634` | ap01_weather_tiny_native_9 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x630850` | ap01_weather_tiny_native_13 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x6309c0` | ap01_weather_tiny_native_12 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x630b4c` | ap01_weather_tiny_native_3 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x630d40` | ap01_weather_tiny_native_4 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x630f3c` | ap01_weather_tiny_native_2 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x6311ac` | ap01_weather_tiny_native_22 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x63140c` | ap01_weather_tiny_native_23 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x631674` | ap01_weather_tiny_native_11 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x631854` | ap01_weather_tiny_native_10 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x6325d8` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x6328cc` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x632c84` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x632f94` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x633324` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x633984` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x6340d4` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x634508` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x63497c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x634f6c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x635638` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x636000` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x636894` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x63714c` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `PNG@0x637660` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `GIF@0x2bc564` | ap01_saver_time_1 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `GIF@0x37d080` | ap01_pet_4 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `GIF@0x3f4b24` | ap01_pet_1 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `GIF@0x46b8b0` | ap01_pet_2 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `GIF@0x4a19d4` | ap01_pet_3 | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `GIF@0x59eb58` | 未命名 | 已识别边界，未入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `GIF@0x5b067c` | ap01_charge_safe_intro | 已入 SIM 清单 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `FONT@0xa037253c` | ap01_rom_calendar_week | 原字体已恢复 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `FONT@0xa05647b4` | ap01_rom_humidity_digits | 原字体已恢复 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `FONT@0xa0564790` | ap01_rom_humidity_unit | 原字体已恢复 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `FONT@0xa0564748` | ap01_rom_weather_note | 原字体已恢复 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `FONT@0xa05647d8` | ap01_rom_weather_temp | 原字体已恢复 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `FONT@0xa06015e4` | ap01_rom_charge_protocol_port | 原字体已恢复 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `FONT@0xa066b67c` | ap01_rom_charge_device_name | 原字体已恢复 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `FONT@0xa060d91c` | ap01_rom_calendar_subtitle | 原字体已恢复 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `FONT@0xa060d940` | ap01_rom_calendar_day | 原字体已恢复 | 描述符/表/RAM 初始化/动态选择引用追踪 |
| `FONT@0xa062c514` | ap01_rom_charge_live_power3 | 原字体已恢复 | 描述符/表/RAM 初始化/动态选择引用追踪 |

## 优先补齐顺序

1. 补齐无函数关联的应用文件，优先工厂测试、底座通信、USB 更新、设置持久化；先复核现有专项报告再做新采集。
2. 拆解多文件/多页面 seed，核对真实函数边界和日志调用点，不沿用错误 no-return 截断。
3. 补资源表、RAM 初始化和动态选择边；优先未纳入重建清单的 93 PNG 与 1 GIF。
4. 逐项核对错误、取消、超时、释放、重入、掉电恢复及真实硬件，建立函数级验收。
5. MiIO/MiBLE 采用 upper-layer 后续报告的 315 函数/537 未采集直接 callee/161 未定向调用历史快照，不能将旧 seed 数当作当前完成率。

完整边、每条 Evidence ID、profile、JSON 指针/文本行号、限制、输入哈希及排除的其他版本记录均见 [机器清单](../../analysis/factory-reference-map-0041.json)。
