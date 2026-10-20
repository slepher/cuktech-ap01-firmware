# AP01 研究与离线构建工具

命令从本仓库根目录执行。源码位于 `tooling/firmware-modules/`，原厂 0041 输入为 `roms/0041/ap01-1.0.2_0041.bin`；私有输出默认在 `evidence/`，运行前按脚本要求准备目录和依赖。外部程序编译、链接和打包进 ROM 见[打包说明](../../reverse/reports/ap01/design.md)。

历史迁移与业务尺寸探针已移至[历史材料](../../reverse/migration/README.md)，不是现用工具。下列实验需要各自的交叉工具链、上游或 WSL 环境，Git 检出不包含全部私有输入。

## 0041 QEMU执行与Patch注入

`test-screen-window-0041.py --qemu <现有Linux AP01引擎> --image roms/0041/ap01-1.0.2_0041.bin --output <已有目录中的新JSON>` 有界执行原厂滑动、动画回调、窗口/页面标签查找和初始化尾部，检查9/10/17个孩子及24次双向转换。对象及LVGL叶函数为合成夹具，不执行真实分配/完整UI，也不访问设备。结果、REA静态证据与接口调整见[追加验证](../../reverse/reports/ap01/screen-host-append-validation-20261020.md)。引擎及WSL依赖须已有；报告拒绝覆盖。

当前目标与验收见[独立OTA闭环验收](../../reverse/reports/ap01/qemu-ota-final-20261017.md)，硬件细节见[模型证据](../../reverse/reports/ap01/qemu-rtc-display-20261017.md)。原件已进NuttX、MiIO及LVGL原生初始化/定时回调；`ui-empty-scan-continuous-125.json`在50秒宿主观察期推进到虚拟8628ms，无guest异常。LCD捕获仍是原厂开机Logo，不能称完整主界面显示已验。显式`--icount-shift 2 --icount-sleep on`是合成时间，不表示E907精确计时；`start-qemu-ap01.py`历史RTC实例不代表最新模型。

`run-qemu-mock.sh <新报告.json>`先编译当前模型，再有限时执行精确0041。必要功能显式启用：`--rom-shim <bin> --clic-mock --pec-uart-mock --flash-fixture <bin>`；CPU还须开启`x-ap01-clic=on,x-ap01-p=on`及原有T-Head扩展。`--breakpoint 0x62fc2500 --pass-interrupts 1000 --pass-ecalls 1000`允许原厂trap/handler/mret实际执行，其他异常仍停止。报告记录原件/引擎/shim/fixture哈希、UART、异常和QMP显示/Flash状态；截图与`pixel_writes`须结合执行入口判读，不将合成测试画面算作原厂UI。

连续观察可用`--observe-seconds 50 --timeout 60`并省略trap-handler breakpoint/pass参数。正常输入配置`--gpio3-input-high --gpio24-input-high`显式选择非工厂模式、松开旋钮按键；BLE/ADC采用真实不可用路径`--ble-unavailable --adc-unavailable`。扫描必须用`--scan-empty-mock`：20ms pending→done→空列表ENOENT；`--scan-unavailable`会使原件安排4秒延迟重启，保留它仅用于失败取证。无线连接没有被模拟。

`build-ota-channel-0041.sh <新名称>`构建RV32独立HTTP模块，`build-ota-channel-0041.py`重建固定unsigned候选上的限定Patch及清单；`run-qemu-ota-channel.py`用payload范围限定的loopback socket提供器执行实际HTTP模块。`verify-qemu-ota-boot.py`检查真实提交后的NOR表CRC/age/活动槽、候选逐字节匹配及旧槽保护，再供显式虚拟复启；它不是恢复出的Boot2。候选均为simulation-only，不能据此宣称031首次安装或实机恢复能力。

`build-qemu-bootrom-shim.sh <新前缀>`编译只供模拟器的RV32 API绑定；`build-qemu-flash-fixture.py`构造16MiB合成NOR及SDK格式分区表。默认只有`/data [710000,720000)`和`/resource [EB0000,FF0000)`可修改进程内NOR；显式`ota-flash-mock=on`额外允许非活动FW槽及非活动分区表，活动槽/Boot2/保留区仍拒绝。`ota-fw1-active=on`仅供已核验提交后的FW1复启。磁盘输入fixture始终只读；不是实机备份或可安装Flash镜像。各`test-qemu-*.py`为独立合成用例，不代替整ROM验收。

入口：[显示续作交接](../../reverse/reports/ap01/qemu-display-handoff-20261017.md)。`build-qemu-ap01.sh`构建固定QEMU10.1.0及`qemu-ap01.c`；`run-qemu-ap01.py`执行精确0041，`test-qemu-ap01.py`检查模型，`probe-qemu-injection.py`保留早期注入对照。已进入原生任务并完成OTA模拟往返，实际LCD主界面仍未显示。须在WSL运行，构建前准备输出目录；不刷实机。

## 维护核心离线构建

`build_maintenance.py`只读核对现有0031-opt/opt-setting及清单，复用原校验器检查允许修改范围和尾部CRC，编译本仓库维护核心，执行宿主检查与同一套RV32模拟测试，输出栈/尺寸/源码与产物哈希。只生成静态库和核心ELF，**没有设备任务/HTTP/存储/安装/UI适配，不生成完整ROM**；不联网、不访问设备、不修改旁仓库、不创建目录。使用本机已有LLVM23和Rust所带链接器，以及既有Unicorn2.1.4；不用原Linux构建工具在macOS上冒充成功。

```sh
python3 -B tooling/scripts/build_maintenance.py --output <已提权预建的AP01产物目录> --require-rom
```

`--require-rom`在核心验证通过后仍返回2并记录`rom_ready=false`，表示设备接口缺失；去掉该参数仅检查核心构建。已有同名最终报告拒绝覆盖。现有固件没有完整原厂源码，本轮遵循“不额外逆向”，缺失接口见[实施记录](../../reverse/reports/ap01/maintenance-build-20261015.md)。

## 0031 原厂OTA与独立维护定位

`inspect_ota.py`复用0031精确校验/基本块分析，只读提取原厂OTA弹窗、点号定时回调、原生更新I/O等7个窗口及候选引用；不创建目录、不联网、不构建或刷机。输出含原字节与哈希，不定义可调用ABI或完整函数边界。

```sh
PYTHONPATH=evidence/private/ble0031-20261014/deps python3 -B tooling/scripts/inspect_ota.py \
  --image evidence/private/ble0031-20261014/ap01-1.0.2_0031.bin \
  --output <既有目录中的新报告.json> --self-test
```

输出已存在则拒绝，自检覆盖真实timer call目标、UI引用及变异/截断拒绝。[维护设计/证据边界](../../reverse/reports/ap01/independent-maintenance-20261015.md)不代表已实现常驻服务。

## 0031 最小XIP App候选

`build_app_rom.py`读取精确原厂0031和已验证的优化GIF，使用只读克隆中现有WSL RV32 GCC工具链编译本仓库`tooling/firmware-modules`，输出完整更新容器、App包、ELF/map/dis/su及源码/成品哈希清单。不联网、读凭据或访问设备，不创建目录，不覆盖既有产物；先准备输出目录。WSL 需使用可访问工具链及源码的环境。GIF逐帧无损验证用WSL现有Pillow。

```powershell
& 'C:\Python314\python.exe' -B tooling/scripts/build_app_rom.py --output <本仓库evidence/private中预建的新目录>
& 'C:\Users\cogic\.platformio\penv\Scripts\python.exe' -B tooling/scripts/test_app_rom.py --directory <该构建目录> --output <新的报告.json> --deps reverse/app-0031/deps
```

模拟器依赖隔离目录内Unicorn2.1.4，实际执行候选RV32指令；stub原厂对象创建/分配/释放/日志。`verify_gif.py`仅比对资源帧。候选不是完整Bridge或文件App OTA；[源码/ABI](../../tooling/firmware-modules/README.md)、[验收和限制](../../reverse/reports/ap01/app-implementation-20261013.md)。本轮不刷机。

本目录保存 AP01 分析脚本；结论与依赖见 [研究入口](../../reverse/reports/ap01/README.md)。第三方克隆保持只读，不需要在其中安装或放入本项目脚本。

## 下载 0041 原厂固件与复用登录

当前 Git 已收录原厂 0041，无需为离线构建重新登录。下载工具将新结果写入 `evidence/private/`；核验后按 [ROM 清单](../../roms/CATALOG.md)管理规范镜像。

`download_official.py` 复用只读克隆的扫码/云查询模块。扫码后立即把可复用凭据保存为本仓库 `evidence/private/xiaomi-account.dpapi` 并读回校验；采用Windows当前用户DPAPI，缓存不入库、不输出内容。后续默认读取缓存直接登录，`--login` 可强制重新扫码。既不读写 env，也不列举设备或调用控制接口。固定目标型号和 0041 版本；若最新接口返回其他版本，停止下载。分别限制登录与固件 HTTPS 目的地，下载会话不带账号 Cookie；错误原文隐藏，二维码退出时删除，缓存继续保留。审阅与状态见 [下载专项](../../reverse/reports/ap01/firmware-download-20261013.md)。

2026-10-13实际0041下载/保存后读回已通过，新进程复用登录查询成功；实际缓存受 `.gitignore` 的 `evidence/` 规则覆盖且未跟踪。已有同名BIN/记录时工具仍拒绝覆盖，不将登录复用等同于重复下载。

需要安装了 requests 和上游依赖的 Python 环境；以下为历史 Windows 环境示例。在 PowerShell 执行：

```powershell
& 'C:\Users\cogic\.platformio\penv\Scripts\python.exe' -B 'tooling\scripts\download_official.py' --self-test
& 'C:\Users\cogic\.platformio\penv\Scripts\python.exe' -B 'tooling\scripts\download_official.py'
```

首次用官方米家 App 扫描 `evidence/private/xiaomi-login-qr.png`。二维码有效期至多五分钟；凭据保存发生在查询/下载之前。控制台最终输出路径/长度/MD5/SHA256，BIN 与去除 URL/凭据的 JSON 保存到既有 `evidence/private/`。工具拒绝覆盖已有文件；下载失败五分钟内输入 `retry` 可重查/下载，最多三次尝试；取消/超时/进程退出后也可再次运行同一命令复用缓存。实际官方固件域名 `iot-ota-cdn.io.mi.com` 已按精确主机加入白名单。此工具不发送设备升级。

## 静态分析器

`__main__.py` 使用现有 Capstone 5.0.7 及同父目录 `cuktech-ap01-firmware-tools/core/firmware_image` 校验模块，读取该克隆的 `artifacts/firmware/original/ap01-1.0.2_0031.bin` 和原始载荷源码。输入镜像需匹配工具内固定的 SHA256、长度与校验；不会联网或访问设备。

从 cuktech-ap01-firmware 根目录执行：

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
python -B tooling/scripts/__main__.py --self-test
```

输出分析结果时加 `--output <本仓库中已存在的空目录>`。先准备目录；工具拒绝覆盖已有产物。目录应位于 `evidence/private/`，不要写回第三方克隆。禁用字节码缓存可避免导入校验模块时向上游写入缓存。

## 0041/0031版本对照与Ghidra

`compare_roms.py`固定0041/0031身份并验证头CRC与恢复记录；生成候选字符串/地址引用和窗口，不是完整CFG。处理GCC字符串后缀共享，未知解码项可能是数据。`--inventory-only`提取并校验两版启动ROMFS、rcS与8项内置应用表；`--self-test`核对两版及既有0031解析器。需要现有Capstone，不联网、不读取登录缓存、不产生ROM。

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python -B tooling/scripts/compare_roms.py --output <已经提权预建的本仓库证据目录> --self-test
python -B tooling/scripts/compare_roms.py --output <同一目录>
python -B tooling/scripts/compare_roms.py --output <同一目录> --inventory-only
```

输出拒绝覆盖已有同名文件。0041/0031有效结果见`reverse/analysis/0041-20261013/refined/`。

`Ap01Export.java`给直接Ghidra headless使用：先以`BinaryLoader`、`RISCV:LE:32:default`、base `0x9ffff000`导入匹配SHA的原件；处理数据库时传`-noanalysis -scriptPath <tooling/scripts绝对路径> -postScript Ap01Export.java <新的输出文件> <明确入口地址> ...`。脚本给GP设置实际启动值，反汇编入口、分析变化，再导出真实函数调用/交叉引用/伪代码。数据库、编译产物及目录创建须按项目规则提权。Ghidra脚本失败有时仍给进程exit0，必须核对日志无SCRIPT ERROR、报告实际存在、语言/SHA正确及坏指令/custom0限制。

当前REA6.4.0 Ghidra provider不接纳裸RV32，本脚本输出不能标成REA Evidence。已安装Windows Ghidra12.1.4/JDK21.0.10运行通过；处理器扩展仍有未知语义，不能仅靠自动伪代码填写ABI。有效导出和独立GNU/OpenSSL核对见[0041报告](../../reverse/reports/ap01/knowledge/0041签名与Bridge接口分析.md)。

## 历史资源探针

`reverse/migration/scripts/resource_budget.py` 是停用的历史业务尺寸探针，保留原字节；外部源码及环境未随仓库收录，不作为现用工具。外部程序的资源预算须使用自身源码重新测量并记录源哈希。旧报告和对象在 `reverse/raw/bridge-budget-20261011/`。

## 0031 蓝牙绑定接口定位

`inspect_ble.py`复用本目录0031校验器/解码器，依赖固定上游只读克隆的`core/firmware_image`与Capstone 5.0.7。支持显式原件路径，不要求Windows产物已复制到Mac。只输出候选引用及指定窗口，不生成ROM、不连接/配对设备；先准备输出目录，输出文件必须不存在。

```sh
PYTHONPATH=evidence/private/ble0031-20261014/deps python3 -B tooling/scripts/inspect_ble.py \
  --image evidence/private/ble0031-20261014/ap01-1.0.2_0031.bin \
  --output <既有目录中的新报告.json> --self-test \
  --window 0xa0127bd0:0xa01282d0 --window 0xa0191a50:0xa0191ae6
```

未知指令和分支会清除基本块常量推导，避免跨调用臆测寄存器值；仍是有限线性扫描，不证明函数边界、ABI、SMP或密钥持久化。2026-10-14定位/LLVM交叉核对和实机边界见[绑定专项](../../reverse/reports/ap01/ble-binding-20261014.md)。

`test_ble_security.py`额外依赖隔离目录内Unicorn 2.1.4，执行精确0031原件中72字节的ATT权限检查函数，不生成替代实现。10个明确场景和6144个组合验证普通读写、缺回调、加密/认证拒绝及返回时的栈/属性约束；仅证明这个真实函数的行为，不替代无线实测或证明整个ROM没有SMP。

```sh
PYTHONPATH=evidence/private/ble0031-20261014/deps python3 -B tooling/scripts/test_ble_security.py \
  --image evidence/private/ble0031-20261014/ap01-1.0.2_0031.bin \
  --output <既有目录中的新报告.json>
```

## 0041 NuttX SIM应用重建

入口 `nuttx-sim.ps1 build|run|stop|status`，编译前 stop；WSL Ubuntu-24.04 隔离环境，320×240。左右键模拟旋钮，Enter/Space 确认，Esc 返回，F 切换照片时钟，R 重试天气，Q 退出。原件只读；构建及运行不访问实机，不执行物理 OTA。

完整目录与逐项验收状态见 [功能矩阵](../../reverse/reports/ap01/application-function-matrix-0041.json)，计划与验收门槛见 [全功能重建](../../reverse/reports/ap01/application-completion-plan-20261016.md)。历史 `test-nuttx-sim.py` 仅用于 round4 旧二进制，含已淘汰的不可用断言；当前业务验收使用 `test-complete-sim.py`。

原厂 PNG/GIF、字体、字距配对、农历/节日/节气表由 `rehost-assets.py` 从固定 SHA256 的 0041 本地生成。`test_rehost_fonts.py` 验证字形，`check-calendar-0041.py` 验证完整有界日期表，`test_sim_services.c` 通过 ASan/UBSan 验证服务与持久化，`test-complete-sim.py` 使用真实 X11 按键、截图、独立原图数字像素与跨进程重启验证界面。

`sim-control.ps1` 向本机 HOSTFS 发送有编号、有界等待的服务事件并返回结构化 JSON；没有网络监听，也不会发送 ROM。命令超时表示结果未知，应读取 `status`/`sim-response.json`，不能盲目重发。首次启动无 Wi-Fi 配置时为原厂米家/指南路径；接入模拟数据示例：

```powershell
pwsh -File tooling/scripts/nuttx-sim.ps1 run
pwsh -File tooling/scripts/sim-control.ps1 wifi 1
pwsh -File tooling/scripts/sim-control.ps1 weather
pwsh -File tooling/scripts/sim-control.ps1 charger 1
pwsh -File tooling/scripts/sim-control.ps1 bank 0 1
pwsh -File tooling/scripts/sim-control.ps1 bank 1 1
```

控制回执中的 `request_ok` 是本次请求结果，`reply` 保留最近业务服务回执；成功读取 status 不会把业务失败改写为成功。请求绑定当前 session、递增 id 和原始内容；旧会话、已使用编号及同编号不同内容均不能重放操作，新进程允许重新开始编号。

服务命令的数字命名空间：bank0=C1移动电源，bank1=C2移动电源，bank2=本机充电器；port0..3=C1/C2/C3/A。`bank` 创建移动电源连接态，`device` 创建普通 USB 设备连接态，两者不同。

| 命令 | 参数及作用 |
| --- | --- |
| status | 读取状态、服务回执、UI状态、12个独立端口配置 |
| wifi / charger | 0断开、1接入；Wi-Fi配置标记与实时连接分别保存 |
| bank | bank, connected；原厂移动电源弹窗及导航门控 |
| device | bank, port, connected；普通/放心充设备插拔 |
| telemetry | bank, port, mV(0..28000), mA(0..5000) |
| port-state | bank, port, flags(input=1/BMS=2/connected=4), battery(0..100) |
| capabilities | bank, port, mask(safe=1/protocol=2), cableAmps(0..5) |
| mode / port / safe | 输出模式；bank/port/enable；bank/port/enable/limit |
| protocol-mask | bank/port/支持位掩码(PD=1/PPS=2/UFCS=4)，供下次识别 |
| protocol / protocol-cancel / protocol-confirm | bank/port检测；取消；bank/port/disabledMask |
| weather / weather-data | 异步刷新；原厂天气code/湿度/AQI/UVI（未知code隐藏图标） |
| climate / sun | 温度/最高/最低/体感均为真实值+100；日出/日落分钟 |
| bind / bind-cancel | 异步绑定与取消，绑定成功持久化 |
| check / check-cancel | target0=AP01、1=TA1208；异步检查或取消 |
| package | target/version/CRC异或值/signed；只校验本地模拟包，保留型号/版本/CRC要求 |
| offer / ota / ota-cancel | target原厂提示；CRC有效开始(签名元数据取已验证包)；取消 |
| recovery | 0/1：TA1208远端bootloader/恢复上报；同版本修复仍须target1有效包 |
| fault | 0正常、1下个请求失败、2下个请求超时 |
| fixture / clock / date | 照片00:37开关；冻结epoch；YYYYMMDD民用日期，均不改宿主RTC |
| saver / timers | mode1功率、2时间、3黑屏；idleSeconds/blankSeconds/mode |
| restart / reset | UI模拟重启；显式工厂复位，均不写实机 |

更新须先注入对应目标的有效模拟包，例如 `sim-control.ps1 package 0 42 0 0` 后 `offer 0`；AP01与TA1208验证结果分别保存，不能跨目标复用。断网/断开充电器会锁存当前事务失败，重连不会把旧事务冒充成功。

配置存储为 WSL 既有工作区的 `ap01-sim-state.bin`，采用显式版本/计数/长度/CRC、临时写入读回及原子替换，损坏时拒绝保存并要求显式工厂复位。验收脚本临时隔离并恢复用户配置。所有“连接/绑定/更新成功”只指本机模拟服务结果。

最终0041全功能SIM验收及产物见[验收报告](../../reverse/reports/ap01/application-rehost-complete-0041-20261017.md)。构建脚本固定上游提交，并修复X11 Return/Space自动重复事件对对3秒长按的干扰；无需修改宿主键盘设置。完整验收入口为`test-complete-sim.py`；历史分批测试仅对应其当时版本。

当前RF续作：`--rf-calibration-mock` 显式启用合成LOFCAL/ACAL/TX PM反馈；`MIX020=0`选择fixture不执行ROSCAL/RCCAL，非硅片复位声明。`rf-fullcal-61.json`已运行原厂LOFCAL/ACAL/TX/BZTX/RX搜索及结果写回，停后续MIX708，主UI仍未到；MAXW已补齐，P77项和PM14组`tests-rf-pm-selector-60.json`通过。完整边界见`reverse/reports/ap01/qemu-rtc-display-20261017.md`。


## 0041 模拟界面的 Wi-Fi 选择

设置顺序为：屏幕常亮 → 屏幕保护 → **Wi-Fi** → 屏幕亮度 → 版本信息 → 操作指南 → 恢复出厂设置 → 返回。进入 Wi-Fi 后直接显示保存的网络名称，旋钮选择、单击切换；`*` 标记当前选择，末尾为返回。空列表仅提供返回。最多保存 8 个网络。

Wi-Fi列表独立保存在HOSTFS的 `ap01-sim-state.bin.wifi-list`，原有 `AP01SCF1` 结构不变。每条记录保存展示SSID和最多1024字节的不透明SIM配置。试联将字节写入 `.wapi.conf`，先用独立 `.wifi-pending` 日志记录旧槽/候选槽；关联后等待IP事件，才确认活动槽和联网。失败/超时恢复旧字节并独立重连旧网；进程在试联中重启也恢复旧配置。两网都失败时保存列表仍可用，能从本地菜单手选旧网，不需要管理会话。SSID最多32个UTF-8字节，回包不含配置内容。

这是SIM交互与恢复模型，**不是实机PSM存储兼容实现**。已实读确认当前设备使用 `/data/network.ssid`、`/data/e#network.password` 等多份键值文件，并无 `wapi.conf`；密码还使用设备相关加密。SIM不解析或生成该合同，不连接真实无线网络、不写真实设备，不能把模型联网或字节保留测试当成米家兼容验收。

通过现有本地管理接口导入、切换、删除（路径按实际 HOSTFS 修改）：

```sh
python3 tooling/scripts/sim-control.py wifi-put 0 --ssid Home --native-config /private/path/home-wapi.conf --root /home/slepher/nuttx-ap01-sim
python3 tooling/scripts/sim-control.py wifi-put 3 --ssid Office --native-config /private/path/office-wapi.conf --root /home/slepher/nuttx-ap01-sim
python3 tooling/scripts/sim-control.py wifi-select 0 --root /home/slepher/nuttx-ap01-sim
python3 tooling/scripts/sim-control.py wifi-delete 3 --root /home/slepher/nuttx-ap01-sim
```

`wifi-put` 也用于修改同一槽，保存列表不会自动激活；允许编辑/删除当前SSID的候选记录，当前独立快照及连接保持不变。缺失当前SSID时菜单追加只读恢复项，按SSID去重；真正切换需要从菜单明确选择。`wifi-release` 取消激活并保留列表，`wifi 0` 仅模拟断网。OTA和绑定进行期间拒绝切换/取消激活，试联期间拒绝编辑列表。

菜单中的 `...` 表示正在尝试，`*` 表示已收到IP确认，`!` 表示保存的活动配置当前离线。状态回包另有 `wifi_phase/wifi_target/wifi_previous`。SIM驱动默认分两次事件模拟关联和IP；测试可在选择前执行 `wifi-plan primary rollback delay_ms`，其中两个结果分别为0成功、1失败、2静默超时，延迟10–3000ms；`wifi-result 0/1/2` 可显式注入关联/IP/失败。未关联时IP事件被拒绝。模拟事件只用于测试，不是发往实机的配网命令。

**不依赖联网的另一入口**：模拟器停止时使用 `--offline`，无需管理会话或网络；下次启动导入列表，不会自动激活：

```sh
python3 tooling/scripts/sim-control.py wifi-put 2 --ssid Travel --native-config /private/path/travel-wapi.conf --offline --root /home/slepher/nuttx-ap01-sim
```

离线输入为独立的 `.wifi-offline-2` 文件，导入成功后删除，失败则保留供检查。配置及临时文件按 `0600` 写入，包含凭据，请留在本机。列表损坏不会被静默覆盖；恢复出厂设置可重建空列表。文件提交使用同步后原子重命名；不承诺多个文件之间的掉电事务。

宿主验证：

```sh
cc -std=c11 -D_POSIX_C_SOURCE=200809L -D_DARWIN_C_SOURCE -Wall -Wextra -Werror -Wno-unused-function -fsanitize=address,undefined tooling/scripts/test_sim_wifi.c -o /tmp/ap01-wifi-check
/tmp/ap01-wifi-check
```

`test_sim_wifi.c` 覆盖独立存储、原始字节保留、旧格式不变、重启恢复、离线导入、故障保持旧激活配置、损坏拒绝及重置。`test-complete-sim.py` 已增加名称列表、菜单位置、点击切换和错误返回的真实 X11 验收步骤；它需要另外配置的 NuttX/LVGL SIM 环境。

完整GUI验收使用 `test-complete-sim.py`，可用 `AP01_SIM_EVIDENCE` 指向预建的新证据目录，避免覆盖历史截图。原厂格式与实机切网/绑定保留仍按未闭环缺口跟踪，详见 [0041 Wi-Fi 选择缺口记录](../../reverse/reports/ap01/knowledge/0041-sim-wifi-selection-gaps.md)。

## 0041 实机独立诊断

`diagnostic-client-0041.py` 使用已登记设备的 token JSON，通过18080常驻维护服务读取状态、原厂文件、ramlog及物理Flash；无需业务owner或C2会话。接口及部署证据见[专项](../../reverse/reports/ap01/independent-diagnostic-0041-20261021.md)。

```sh
python tooling/scripts/diagnostic-client-0041.py --host DEVICE_IP:18080 --token-file /private/device-token.json --mac DEVICE_MAC --operation status
python tooling/scripts/diagnostic-client-0041.py --host DEVICE_IP:18080 --token-file /private/device-token.json --mac DEVICE_MAC --operation file --path /data/wapi.conf --output /private/wapi.conf
python tooling/scripts/diagnostic-client-0041.py --host DEVICE_IP:18080 --token-file /private/device-token.json --mac DEVICE_MAC --operation flash --offset 0x710000 --length 0x10000 --output /private/data-partition.bin
```

原始字节只写文件，不输出配置内容；已有文件拒绝覆盖，失败前缀保留为`.partial`。每块核对MAC、boot ID、偏移、长度和CRC32，导出后再次核对boot ID。分块读取不承诺全局原子快照；普通文件的总长变化会终止读取，ramlog按一次非阻塞有界采样保存。
