# 0041 应用重建与未签名 OTA 离线候选

> 后续更正：首批设置顺序/OTA菜单映射已被0041原表证据取代，当前字体、设置、交互和产物见[第二批验收](application-rehost-0041-round2-20261016.md)。本文件保留首批历史。

2026-10-16。用户将基线切到0041，并明确去除的是0041相对0031新增的未签名OTA拒绝行为。原件与第三方克隆只读，未访问设备、账号或Bridge，未刷机、提交或发布。

## 当前可运行结果

WSL Ubuntu-24.04 的 `/home/slepher/nuttx-ap01-sim` 已编译并通过82步真实X11键盘测试，WSLg窗口已启动。NuttX12.10.0、apps同版本、LVGL9.2.1，提交与环境入口沿用[搭建记录](nuttx-sim-20261016.md)。产物是x86-64应用重建环境，原厂RV32机器码没有在其中执行。

| 页面/操作 | 本轮状态 |
|---|---|
| 功率、C1、C2 | 按原厂创建顺序接入；固定两个模拟端口与示例数值，未接硬件 |
| 时间、日期 | NuttX SIM RTC取宿主时间，UTC+8；时间用原厂数字PNG，每秒更新 |
| 天气 | 原厂太阳图标与明确SIM示例值，未联网 |
| 设置 | 七项中文列表、两端停止、确认进详情、短按/Esc返回 |
| 屏幕亮度详情 | SIM透明度1–10，两端停止，无持久化/实机亮度控制 |
| 版本详情 | 明示0041来源及NuttX/LVGL宿主版本 |
| 其余设置详情 | 明示未移植/未执行；不执行OTA、复位或账号操作 |
| 萌宠 | 原厂GIF字节直接导入并播放，已验证相隔0.5秒画面变化 |

左右/上下键模拟旋钮；Enter/Space短按确认。长按与短按已分离，未恢复的长按业务仅记unsupported。Esc为SIM辅助返回、Q退出；两者不是原厂物理键。默认八个可切换页面首尾循环是重建策略；端口动态上下线、原厂导航跳过规则、米家内部详情、全部控件坐标/动效、真实设置存储与服务尚未还原，不能宣称完整原厂界面或像素一致。

设置项为屏幕常亮、屏幕保护、操作指南、屏幕亮度、版本信息、OTA更新、恢复出厂设置。六个中文资源在0041原件中确认；第六项精确原厂文案未找到，当前带`*`。七项顺序/端点规则结合0031事件状态与0041详情资源交叉映射，0041完整设置回调仍未恢复，属于明确的跨版本推断。

## 逆向与资源来源

0041原件 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。REA原始RV32LE映射base `0x9ffff000`、entry `0xa0000000`；UI入口`0xa005cc1e`，直接证据`ev_29c3e3a3ec43f12e0a1d9c5db26f6b39875288fb82b8c2126a9974ddfe734175`。设置注册回调候选`0xa00ab588`尚不能当完整函数/可调用ABI。

已有Ghidra导出 `0041-20261013/0041-ghidra-pass3.txt:2260` 的两次`FUN_ram_a00f1102`分别传端口1/2，说明功率与时间之间仍有C1/C2条件页。子代理最初漏列，已由父代理核对原文并纠正。字符串存在不等同于函数入口或事件顺序。

证据目录统一为 `reverse/rehost/`：

- `page-logic-0041.json`：24条REA记录，完整导出后已关闭会话；记录unknown计数不是完整行为恢复证明。
- `asset-index-0041.json`：199/199 PNG均经CRC/IEND扫描且与0031精确匹配；旧10个GIF中9个精确匹配，额外签名候选未当作完整GIF。
- `ap01-assets-0041.json`：本轮实际导入15项资产的0041偏移。数字0..9、冒号、logo、功率弧、太阳和萌宠均从0041原件生成。
- 中文用本机文泉驿正黑73字子集，属于重建字体；内置SimSun子集缺字，不能称为原厂字体。生成字节与ROM资源均仅留本地忽略区。

LVGL9.2.1的GIF解码器把`frm_off + str_len == frm_size`误报越界；构建脚本以固定旧文本核对后将`>=`修为`>`，并在真正越界错误路径释放LZW表。保留边界检查，原厂GIF无需转码。最终82步日志无LVGL警告；此前失败日志不作为最终验收。

## OTA新增门槛的离线修改

依据[0041签名调用链](knowledge/0041签名与Bridge接口分析.md)，只改文件`0x707fc`（VA`0xa006f7fc`）：`dde7`，即检查signed_file标志的压缩条件分支，改为`7da0`，压缩无条件跳转到原来的继续位置`0xa006f8aa`。不改标志本身，因此false不会被伪装成已签名；true仍保留后续原有验签条件与代码。版本/model、包格式、头CRC及其他检查代码不变。

恢复尾记录CRC从`0x47fb9315`更新为`0xf961cc33`，头CRC不变。全镜像精确比较只变6字节：2字节分支和尾4字节CRC。工具绑定原件SHA/长度/旧字节，拒绝损坏输入、已有输出或已有manifest，写出后已独立读回比对。

- 离线候选：`ap01-1.0.2_0041-unsigned-ota.bin`，6,769,704 B，SHA256 `1bbe8f45359eb7cdb55f337643f3ce28894999ffb21beab92fb62e995cd4854d`。
- 同名`.manifest.json`记录修改范围、前后校验值、候选指纹及未刷机状态。
- `python -B tooling/scripts/test_0041_unsigned_ota.py`：8项通过，无跳过。独立Unicorn RV32实际执行原件/候选的load、lui和branch三条指令，标志0/1四组PC与内存标志核对一致；其他测试核验CRC、变异拒绝及禁止覆盖。

这证明局部分支已按预期修改，不是完整OTA下载/安装或硬件启动验收。补丁只影响候选自身运行后的后续OTA；不能使当前运行的原厂0041自动接受这个未签名候选。Boot2/eFuse/首次安装及掉电恢复仍未验证。此次没有刷写，也没有修改签名私钥、TLS验证或Bridge认证。

## 构建与复现

```powershell
pwsh -File tooling/scripts/nuttx-sim.ps1 stop
pwsh -File tooling/scripts/nuttx-sim.ps1 build
pwsh -File tooling/scripts/nuttx-sim.ps1 run
pwsh -File tooling/scripts/nuttx-sim.ps1 status
```

这些WSL构建/运行仍按项目规则提权；新目录需预先提权创建。构建器默认读取本仓库0041原件，也可用`AP01_ROM`显式指定相同指纹文件。LVGL配置变化时只让其源码重编，保留其他缓存。键盘回归从WSL执行：

```sh
python3 ./tooling/scripts/test-nuttx-sim.py
```

最终 `ap01-ui-0041-sim.elf` 6,327,928 B，SHA256 `b5a9419cd5305a7ab04616aa0e4f4b580e463438d0f7af40f5ade0e345d02462`；匹配`.config`、源码/生成资源/修复后解码器压缩归档`ap01-ui-0041-sim.tgz` 3,388,725 B，SHA256 `2ace891b7a169b152b5ff1f8af50cfb71b84a20ca984157cb715079b0b99c7ff`。它们均位于上述证据目录，与AP01离线候选BIN是两种独立产物。验收JSON `nuttx-sim-verification.json`绑定同一ELF哈希；截图`ui-time.png`、`ui-settings-first.png`、`ui-brightness.png`、`ui-pet-a.png`等已审阅。

## 后续验收缺口
