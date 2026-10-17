# AP01 0031 应用静态逆向（2026-10-16）

用户要求在SIM搭建同时启动subagent做应用逆向。由原生 `luna_runner` 子代理执行，父代理读取导出的编码器伪代码并核对5条记录。仅静态读取精确0031原件，未执行ROM、修改第三方源码或访问设备。

原件6804520 B，SHA256 `8a721fc8ef25458d415b2460e4a251e0503a82f7743fdff85b12612190e5c1cb`；REA6.5.0/Ghidra12.1.4，raw RV32 LE，base0x9ffff000、entry0xa0000000。完整Evidence包 [rea-ui-subagent-20261016.json](../../artifacts/ap01-research/rea-ui-subagent-20261016.json)，5042322 B、5条；导出核对完成后已关闭会话。

## 应用与输入路径

- `lvgl_ui_main`入口0xa0072bbe；REA当前识别60 B范围，分配0x270 B栈并给一次调用传入0x200 B缓冲。Ghidra在0xa0072bf6记录no-return并截断fallthrough，**不能据此断言整个main只有60 B或没有后续页面逻辑**。
- 编码器读取0xa00ccf7c：读8字节记录；观察到type=1分支中code0x69使enc_diff减1、0x6a加1，0x1c改变按钮状态；type=0分支也改变按钮状态。随后写LVGL输入状态并调用0xa00cce0e。字符串包含 `lv_nuttx_encoder.c`、`encoder_read_keyevent`、`encoder_read` 和GPIO encoder路径。此为原厂协议观察，不等于当前开源NuttX键盘协议。
- 0xa00bbfee伪代码呈现LVGL key/enter及right/left/enter页面分发线索，引用 `j_win_ui_theme_event_custom_handler`。Ghidra识别的是非连续5394 B地址集合、跨度6926 B；存在间接流及跨范围边界不确定，不把长伪代码当原始单一C函数。

## 编译进镜像的页面族

字符串及既有知识支持以下页面创建入口名称；字符串本身不保证在所有启动状态可达：

| 页面族 | 创建名称示例 |
| --- | --- |
| 启动与主页面 | boot_anim、time1、power1、weather1、date1、setting |
| 设置 | setting_dtl1/dtl2、scr_brt、ver_info、ota、SFR |
| 时间/天气详情 | time1_dtl1、date1_dtl1、wx1_dtl1 |
| 功率/充电 | power1_dtl1_list、mode_sel、prot_asst、anxin_chg、port_dtl |
| 配网/引导/设备 | mijia_dtl1、cuk_con_ins_dev、dev_ins_pop_up、opn_guid、get_start_guid |
| 弹窗/屏保 | app_ota_pop_up、scr_saver_pwr、scr_saver_tim2 |

部分完整符号为 `lv_page_ui_*_create` / `lv_win_ui_*_create`。具体名称和地址保存在Evidence中，未据名称合成真实API签名。虚拟形象等既有页面证据仍见原知识文档，本次定向查询不构成所有页面的穷尽清单。

## 对SIM的意义与边界

可用开源NuttX/LVGL重建“输入事件→编码器→焦点/按下→页面控制”这条应用链。原厂界面、米家任务和充电控制并未从现有材料获得完整可编译源码；本轮也未检索整个互联网证明其不存在。原厂图像、字体、资源和底座协议仍需分别核对，不能把字符串或反编译伪代码直接当源码。

当前SIM仅演示Clock/Power/Settings导航与确认；本次应用逆向提供后续重建依据，不表示已把原厂应用移植到SIM，不增加未授权的OTA/绑定/硬件实现范围。真实GPIO引脚、采样时序、驱动初始化和实机页面可达性未知。

## Evidence

- 入口：`ev_639ff2af33b31df8d3d67014fcd23dda536c5a937bd1ceced8b215c4311b45ae`。
- 编码器：`ev_2a1bebfaa15e26fc86739bceb4b348c11e5f6ec9caabc4f44525a2e8940a6a4e`。
- 分发器：`ev_519e863473e3ff3cb17fab9316d3a88ab359541a3fb9244ac9ca341251f5f629`。
- 输入路径字符串：`ev_8581cc5a6012ec209615163150cd1d950a22e1a8322653a05f4751438e60b6cb`。
- 页面创建字符串：`ev_621ff68e933b4f9b3c80206af7c364de25f6dd83e335a60eacb876685c6d7a90`。
