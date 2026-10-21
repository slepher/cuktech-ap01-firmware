# 0041 原厂设置菜单：持久设备码候选

2026-10-22，06已单次上传至AP01应用槽1并认证运行build`5757fdd677800d1412d8795c1cb2dbe0`。菜单八位码/原Bridge密钥维护兼容，原Bridge业务正常；八位码实际切槽和重启至原0031救援0、独立入口回到06通过，无二次上传。设备码跨重启保持，Wi-Fi列表未变，用户确认界面正常。救援0未写，完整非活动6822344B（含PEC）SHA256`d843aae4e097c31ce06a315c62e1a66f4fb3bf9299db289b6f31562d0ef2231b`与原保留镜像一致。真实无绑定完整OTA仍属原生模拟证据，实机既有绑定保留；掉电/栈高水位未验。实机报告：`codex_status/artifacts/ap01-menu-ota06-rollout-20261022/physical-validation.json`。以下为候选/05历史记录；实现及验证脚本纳入本轮提交。


2026-10-22 最新源码/候选06（未部署）：应用维护`/api/firmware/*`及health支持菜单八位码或原Bridge绑定密钥。八位码使用独立本地维护principal，不要求绑定/owner，不创建绑定；每个chunk/重放重新校验当前码。码轮换后新码可继续/查询原事务，旧码拒绝；MAC/revision/长度/CRC/槽位/回执保护保留。救援0031不改，设备仍是05。

候选06：7019304B，build`5757fdd677800d1412d8795c1cb2dbe0`，SHA256`82d33c493f7625a2b22588210d6492897af93b4f7eba05d3559abd9f15197e18`，ELF`76cbab6897edb5652a72a6553d749f0be799d7c9aa698fad1e7678749003be86`。相比05增加ROM224B，RAM/持久格式不变，Application648B。精确/当前源码ASan/UBSan、零绑定完整原生OTA/切槽、原Bridge密钥OTA通过；零绑定维护使用已由原生菜单生成的持久DVC1记录及干净resource文件系统，绑定数前后均为0。空resource新菜单进入探针未通过，不冒称该GUI验收。细节/失败记录见codex_status/project-workflow/ap01-device-code-menu/status.md，离线汇总在artifacts/ap01-device-code-ota-20261021/offline-acceptance.json。

复现：在05隔离源码上执行`enable-menu-ota-0041.py --source-root <目录> --diff <文件>`后审计/链接/重建；`verify-menu-ota-qemu.py --menu-record-report <原生菜单报告>`验证维护，`--manual-switch-only`验证切槽。原菜单回归加`--device-code-auth --firmware-code`表示06策略，省略后者保留05策略。源码尚未提交，本轮未访问设备、未修改救援ROM。

2026-10-21 后续：菜单数字已统一为完整原厂20px字体，码/生成行隐藏箭头；父菜单双向循环，子菜单只在生成/返回间循环，数字栏不可选。候选05增加手动鉴权，已单次OTA至应用槽1并认证运行build `cf1789f6c5c02787b2c3e86c5765fc74`，救援0未写；用户确认菜单循环、数字不可选/字体一致及前两行无箭头，码轮换鉴权实机通过，非活动救援完整读回匹配保留镜像。下文02候选内容为历史实现/验证记录，当前现场以codex_status/PROGRESS.md为准。

手动维护端口18080的`/api/wifi/*`、`/api/diagnostic/*`使用`Authorization: Bearer <菜单八位码>`，不接受原Bridge密钥。日常业务、配对/claim/owner、固件OTA/切槽及独立救援继续使用原凭据；八位码不能替代固件凭据。每次只读当前提交码，五次失败暂停30秒，存储异常503，无HTTP初始化/轮换。入口脚本为`tooling/scripts/enable-device-code-auth-0041.py --source-root <已接入菜单的隔离源码> --diff <差异文件>`；原生验证可用`verify-native-device-code-menu-qemu.py --device-code-auth`及`verify-device-code-recovery-qemu.py`，后者分开验证普通OTA与`--manual-switch-only`。

05完整包7019080B，SHA256 `ccfa3c7dee00f81b4c2a9b60add89944eef82857bddff710f73443d0f4a26e7d`；ELF `386adefc11615650eb16b4a35a93d060fbedfdfa24762099f537dfec0615e8fd`。精确源码宿主ASan/UBSan、原生auth01/02同Flash重启/码轮换、recovery06完整OTA/保护区域及switch01无稳定记录回切通过；原始证据在codex_status/artifacts/ap01-device-code-auth-20261021。活动0031救援的PEC物理区`[0x688800,0x68d400)`存在既有读保护，不把它的抑制读数冒称全包原始哈希；安装后非活动救援完整6822344B（含PEC）SHA256为`d843aae4e097c31ce06a315c62e1a66f4fb3bf9299db289b6f31562d0ef2231b`，与保留镜像一致。实机旧码401、新码可用，Bridge原凭据继续工作，Wi-Fi列表revision2未变；脱敏证据为codex_status/artifacts/ap01-device-code-auth-20261021/physical-validation.json。物理重启后新码、掉电/熵质量/栈峰值仍未验，同Flash重启为模拟证据。本次源码尚未提交。

2026-10-21：已实现并在执行真实0041 ROM的QEMU中验证菜单进入、点击更新、返回和重启持久化。实机尚未部署，不能据此宣称菜单已在实机可用；设备仍运行此前应用槽1版本，救援槽0未动。

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

当前本地候选：`evidence/native-settings-menu-20261021/ap01-0041-device-code-menu-candidate02.bin`，7,018,168字节，build `1faf1ef0e52e4dfdd671db968fbaff11`，SHA256 `286d3accf21eaeda1598c63ecf9e0d533ad77dfc711f56c3c1a2e292d7fb9a8a`。归档时的清单保持未验标记，之后的运行结果独立记录，不修改历史清单。候选01已被替代，不能部署。

## 真实ROM运行发现与修复

候选01在原厂新增行构造调用中不能返回。`native-menu05.json`断点证明到达新增行调用`0xa0686bfa`，但未到返回点`0xa0686bfc`。原厂裁剪字库不能先处理新增文案；现在先以空文本创建行、装好补字字体再设置文字，标题往返也按清空文本、换字体、设置标题处理。

同时修正补字FontData的ABI：真实结构为24字节，原字体回调`0xa00e48fa`读取描述符偏移20的stride字节，不能只定义前20字节。三个原字体对应字段均为零，新增描述符明确补零。证据为本地`font-stride-abi.json`；修复后重新生成字库并完整审计、链接和重建候选02。

`tooling/scripts/verify-native-device-code-menu-qemu.py`通过原厂`lv_group_send_data`及当前焦点对象的原厂事件分发输入，不直接调用新增菜单回调。`native-menu06.json`验证8行父菜单、3行子菜单、只读首行、显式生成、返回父菜单和返回主页；`native-menu07.json`使用同一份保存后的Flash重新启动，比对记录摘要完全一致。`native-menu08.json`进一步验证按下/KEY/释放完整点击、关闭原厂页面后重建并重入，全部通过。

截图来自原厂LVGL实际RGB565帧缓冲。QEMU的LCD画面可能停在开机logo，不能拿它代替原厂帧缓冲。虚拟fbdev的POLLOUT等待还会导致旧帧；截图前在UI线程调用原厂`lv_display_refr_timer(NULL)`（`0xa00e0ac8`，原就绪回调本身采用相同调用）刷新默认显示器。此为外设就绪模型，不由宿主绘制像素。

最终`native-menu09.json`通过完整点击、页面销毁重建、同一Flash重启摘要比对和原厂刷新后的画面验收。人工检查帧缓冲：`native-menu09.device-code-entry.fb1.png`显示原设置末尾的新增入口与原返回，`native-menu09.device-code-submenu.fb0.png`显示标题、八位数字及重新生成，`native-menu09.device-code-return.fb1.png`显示选中的“返回主菜单”。均沿用原厂圆角行、背景、青色高亮、箭头、字号和滚动视窗；图片中的数字仅为QEMU合成数据。最终检查范围为新增菜单，不代表完整业务应用或物理LCD验收。

重跑需传原生runner的完整参数，包括`--lvgl-input-model --safety-seconds <有界时长>`，使用合成绑定和MAC，禁止`--native-loopback`。`--device-code-restart`要求前次报告含设备码摘要，并使用前次保存的Flash；验证重启前后摘要及打开前后记录均不变。

持久文件16字节，提交时临时文件另16字节；模块不增加可写全局。原厂控件内部OOM仍会assert，原生完整调用链栈峰值、实机熵源、LCD/SPI及实体旋钮仍须实机验收。本次运行未改实机网络字段、配网列表或任何槽位。
