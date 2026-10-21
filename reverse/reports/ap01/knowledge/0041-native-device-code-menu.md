# 0041 原厂设置菜单：持久设备码候选

2026-10-21：按用户要求收尾提交。本次已实现、编译并生成候选；原生 QEMU 菜单运行验收及实机验收尚未完成，不能据此宣称菜单已在实机可用。未刷机，设备仍运行此前应用槽1版本，救援槽0未动。

## 行为与样式

- 在原厂0041设置列表的原“返回”之前增加“设备码”。子菜单为八位十进制数字、重新生成、返回主菜单。第三项返回父设置列表。
- 使用原厂列表容器、普通行和返回行，沿用背景、高亮、箭头、行距、滚动位置与旋钮事件。保留原字号和已有字形，仅给裁剪字库补齐缺失字形。
- 首次确认文件不存在时生成；进入、导航和重新启动不自动更换。只有明确点击“重新生成”才请求新值，拒绝与旧值相同的结果。
- 独立文件 `/data/ap01_ui.device_code`，16字节：`DVC1`、8个ASCII数字、前12字节的IEEE CRC32小端。临时文件写入同步、校验、重命名，再读回确认。损坏或读取错误不会自动重置，结果未知时只读确认。
- 未接入OTA/调试鉴权，未更改网络字段或配网列表。

## 实现与复现

实现位于 `tooling/firmware-modules/native_device_code_0041.*`、`native_device_code_menu_0041.*`、`native_device_code_font_0041.*`。宿主测试为 `test_native_device_code_0041.cpp`。

`tooling/scripts/enable-device-code-menu-0041.py --source-root <隔离的0041源码目录> --diff <差异文件>` 复制模块，加入审计源文件与链接保留项，并补齐镜像构建器。随后依次运行该源码目录的 `tools/check-ap01-native.py`、`tools/link-ap01-native.py`、`tools/build-ap01-rom.py --output <新候选路径>`。候选基于已部署f52b12源码快照，不混入尚未部署的screen-host重构。

固定原版0041 SHA256为 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。新增四个调用点文件偏移为 `0xb262c/8`、`0xb263a/8`、`0xb2648/8`、`0xb2754/10`；逐一校验原字节，veneer保留被覆盖指令。256字节模块头的192–251保存 `AP01MNU1` 钩子表，纳入头CRC；钩子目标必须在模块内部。原厂字节仅允许既有主UI入口、这四处调用与既有OTA签名分支变化。

## 已有验证

宿主ASan/UBSan测试通过：首次创建、重复读取零写入、重启保留、前导零、随机数拒绝采样、写入/读回/重命名失败、提交结果未知、损坏拒绝和中断后的临时记录恢复，共15类检查。RV32审计和链接通过，无可写静态段或未解析导入；字体生成可复现。完整镜像重建和原厂字节保护检查通过；五类非法钩子表被拒绝。

本地候选：`evidence/native-settings-menu-20261021/ap01-0041-device-code-menu-candidate01.bin`，7,018,104字节，build `c029d5107c7927b27fd1d979da203c70`，SHA256 `cc0e417b8e75c2f20461c26c0c6eccd227dedefbd3c0ceb2a873ea31d49dfe0b`。清单保持 `flashable=false`、`simulator_verified=false`、`hardware_verified=false`。

后续使用 `tooling/scripts/verify-native-device-code-menu-qemu.py`，通过原厂 `lv_group_send_data` 输入，在真实ROM中检查8行父菜单、3行子菜单、只读首行、点击更新、返回及重启持久化。脚本目前只做了语法与包装后语法检查，尚未执行该验收。原厂控件内部OOM会assert；显示布局、回调生命周期和真实熵源也仍需运行验证。
