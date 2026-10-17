# AP01 0041 ROM逆向交接：从这里开始

更新：2026-10-17，Asia/Hong_Kong。本文是当前状态快照和接手入口，不是待办副本。平台待办仍归`docs/roadmap/backlog.md`的C9；现场设备/Bridge部署仍以根目录`PROGRESS.md`为准。

## 一分钟结论

1. 当前唯一逆向基线是 **AP01 1.0.2_0041**。0031材料可参考，地址与ABI必须重新核对，不能统一加偏移。
2. **原厂应用界面已在NuttX SIM中重建并验收**，包括原ROM字体/图片、页面、旋钮和模拟业务；它不是原厂整ROM执行，也没有真实米家/充电器/OTA服务接通。
3. **miio_client与mible_mesh_common_bt完整代码逆向正在推进，未完成。** MiIO全部162个已知根已完成局部实现审阅，90项描述符已关联实现合同；MiBLE补齐传输/计数器/认证等9份合同。当前同profile315函数，依赖闭包仍开放；见[上层续作与验收](upper-layer-0041-20261017.md)。
4. **已实际修复私有profile的no-return和已观察T-Head/历史P指令语义。** 蓝牙main恢复5696 B、公共初始化7982 B，第二版模型387项检查通过，HTTP/OTA八个函数的已知坏指令截断已消除。当前工作是回调、ABI、类型和直接/间接依赖闭包，不能再按旧generic profile的截断伪代码作结论。详细复现见[私有模型专项](private-profile-0041-20261017.md)。
5. **未刷AP01实机，未停止实机任务，未改Bridge。** 用户要求复杂工作使用 **GPT-6.1 Sol子代理，不用Luna**。仍保留“先不刷实机”的约束。

## 工作区、身份与文件

**Mock启动续作**：用户已授权必要外部Mock，55项回归通过；独立QEMU实例已启动并暂停于RTC配置缺口，NuttX/UI未运行。当前进程登记、模拟身份/时钟边界和下一步见[Mock运行记录](qemu-mock-runtime-20261017.md)，PID操作前重核。

**最新路线调整（2026-10-17）**：用户选择保留原厂后台、Patch注入独立App，并要求QEMU执行0041；没有可用救砖入口，继续不刷实机。已实现QEMU10.1.0最小machine和有限功能模型，18项回归通过；原件执行到RAM中的OTP读取触发，尚未启动NuttX/UI。QEMU专用入口注入/返回的非零寄存器对照通过，候选不可安装。优先续作[QEMU运行记录](qemu-0041-runtime-20261017.md)及[计划](qemu-0041-plan-20261017.md)；下文完整MiIO/MiBLE源码恢复账本保留，不再作为Patch接入的前置。0041实机/Bridge仍未改。

仓库：`D:\Documents\PlatformIO\Projects\codex_status`。PowerShell工具命令使用`login:false`并显式切换目录。旁仓库`D:\Documents\PlatformIO\Projects\cuktech-ap01-firmware-tools`只读。研究证据位于已存在的`artifacts/ap01-research/`；多数大文件被Git忽略，换机器/工作树前需另行保留，不要假定git clone会带回。

| 对象 | 仓库内路径/位置 | 身份与边界 |
| --- | --- | --- |
| 0041原件 | `artifacts/ap01-research/ap01-1.0.2_0041.bin` | 6,769,704 B；SHA256见下；只读 |
| 研究证据目录 | `artifacts/ap01-research/rehost-20261016/` | 名称仍为16日，包含17日最新结果；不要按目录日期误判旧版 |
| 原件旧Ghidra导出 | `artifacts/ap01-research/0041-20261013/0041-ghidra-pass1.txt`至`pass5.txt` | 大量已有伪代码/调用关系；保留custom0/unaff/函数边界限制 |
| REA旧协议证据 | `artifacts/ap01-research/rehost-20261016/miio-mible-rea-0041.evidence.json` | 冻结的30项函数记录，约11.4 MB |
| 指纹清单 | 同目录`miio-mible-rea-manifest-0041.json` | 绑定协议报告、原件、参考源码与Evidence，不是全代码完成证明 |
| 私有分析根 | `artifacts/ap01-research/private-0041-20261017/` | 独立Ghidra/REA副本、语言、profile、修复脚本与Evidence；共享工具不改 |
| 当前完整采集 | 私有根`evidence/upper-complete.evidence.json` | 315函数、179061078 B；内容SHA见`upper-manifest.json`；同一新profile |
| 当前覆盖与索引 | 私有根`evidence/upper-coverage.json`、`upper-command-catalog.json` | 2529条直接边、537个未采集直接callee、161处未定向调用；90项描述符合同索引 |
| 当前指纹清单 | 私有根`evidence/upper-manifest.json` | 190处Evidence引用、57模型输入校验；旧manifest绑定的18文件均不变 |
| 上层实现续作 | 私有根`evidence/upper-miio-a.md/.json`、`upper-miio-b.md/.json`、`upper-routing.md/.json`、`upper-mible.md/.json` | 新增130根逐函数合同、6份公共路由合同及9份BLE合同；保留各自实际profile |
| 上轮冻结采集 | 私有根`evidence/final-0041.evidence.json`、`manifest-final.json` | 276函数，168348248 B，SHA256 `80c93186458c90a7edd8a61beae8b1af4643ef6ce1ba695b87c9ea804bb1a6cc`；不可覆盖 |
| 实现级恢复 | 私有根`evidence/miio-recovered.md/.json`、`mible-recovered.md/.json` | 按模块给出字段、分支、错误与清理；引用各冻结profile，不混写为原源码 |

原件SHA256：

```text
972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9
```

机器码为32位小端RISC-V/RVC，包含T-Head扩展。文件偏移0映射 **`0x9ffff000`**，入口 **`0xa0000000`**，因此本映射内`file_offset = VA - 0x9ffff000`。不要把入口当作文件偏移0的装载基址。原件整体是系统与应用静态链接的固件，不是几个可直接拆出的独立ELF。

快速只读核验：

```powershell
Set-Location 'D:\Documents\PlatformIO\Projects\codex_status'
Get-FileHash artifacts/ap01-research/ap01-1.0.2_0041.bin -Algorithm SHA256
```

## 原厂启动与两个任务的位置

0041 ROMFS位于文件`0x1bee24`；rcS正文位于`0x1bef04`、97 B：

```sh
set +e
ifup wlan0
miio_client &
mible_mesh_common_bt &
lvgl_ui_main &
echo "NSH auto exit."
exit
```

内置应用表从文件`0x1be934`开始，每条16 B，共8项：

| 程序 | 0041入口VA | 配置栈 |
| --- | --- | ---: |
| lvgl_ui_main | 0xa005cc1e | 65536 B |
| mible_mesh_common_bt | 0xa0062d28 | 6144 B |
| miio_client | 0xa0067296 | 6144 B |
| nsh | 0xa0032230 | 4096 B |
| renew | 0xa005a62a | 4096 B |
| setlogmask | 0xa0058f5e | 4096 B |
| sh | 0xa00323f6 | 4096 B |
| wapi | 0xa0077024 | 4096 B |

表内存在不等于同时常驻；应用还会创建子线程。它们是NuttX任务/线程，未证明具备Linux式地址空间隔离。三项启动应用配置栈总和76 KiB不是系统总RAM占用。

0041自身机器码确认将`0xa8000000..0xa8400000`共4 MiB外部区域登记到通用堆，相关初始化在`0xa0029640..0xa0029688`。**这是登记容量，不是实测空闲容量。** 原厂启动代码、全部后台线程、最大连续块、栈高水位以及显示DMA约束尚未实机测量。

## miio_client：已经确定的实现范围

它既不是UI页面，也不只是云端转发器。入口`0xa0067296`进入事件循环`0xa0066296`，调用公共初始化`0xa0064368`，其中安装Wi-Fi扫描/连接/断开回调，创建网络监视、HTTP及云/OTA相关工作任务。

| 入口/区域 | 用途与当前结论 |
| --- | --- |
| 0xa0066296 | socket/poll/accept主循环，监听设备自身127.0.0.1:54322 |
| 0xa0064368 | 公共组件、回调及工作线程初始化；多条间接依赖仍需展开 |
| 0xa006cda4 | Wi-Fi连接回调；`0xa006d124..d258`内有DHCP/IP设置，不能误归为netMonitor函数体 |
| 0xa006d260 | netMonitorTask入口 |
| 0xa0123dca | httpc_task入口，创建时传入0x1400栈参数 |
| 0xa011b158 / 0xa011a020 | otu_task / ots_task入口 |
| 0xa01b82e8 | 接收/拆分JSON对象，按method分派；有加密相关分支 |
| 0xa01b6a84 | local.消息分派；伪代码受错误no-return影响，不能只读其开头 |
| 0xa01b6146 | 上报RPC：状态检查、id提取、待回执记录及转发 |
| 0xa0197822 | 整数id提取辅助 |
| 0xa01977cc | 按id匹配、摘链、调用回调、释放待回执记录 |
| 0xa01202e4 / 0xa01ab298 | 带锁的命令组注册及包装 |
| 0xa01158f6 | miIO.ota命令入口；拒绝local-origin，另有参数/忙态检查 |

原件有90条连续20 B命令描述：`0xa066d808..0xa066df10`，49项`cmd.`、13项`cmdrpc.`、25项`miIO.`、1项`ota.`、2项`user.`。已逐条核对指针、名称和handler。**这是实现目录，不是90项已证明可从LAN调用的API。** 组类型低3位与每条记录尾部flags不同；不能猜flags就是权限。

已定位10项local分派（状态、时间、地区、DID、info、配网及相关确认/日志密钥请求等），另有local.info回包。连接状态有6值表示：device_init、wifi_ap_mode、sta_mode、cloud_trying、cloud_connected（最后两个数值4/5均映射该文本）。它与下文蓝牙11态不是同一枚举。

上报有可提取id时申请32 B待回执记录，保存id、时间helper值、原fd、回调及next。匹配回执会摘链并释放；无id另有路径。状态值>2可进入转发，包含cloud_trying，**不是已送达/执行成功证明**。过期策略和超时回调完整链仍未恢复。`0xa00626ea`是通用回执回调，不能叫“已确认的超时处理器”；`0xa0062882/0xa00629c6`是FD诊断打印，不是超时清理。

停用影响：从启动时禁用会跳过原厂联网与这些工作任务的初始化，不能保证原来的关联、DHCP、重连及OTA入口可用。启动后强杀父任务是否清理子任务和共享回调未知。只删除一条rcS命令并不能证明完成米家脱离。

## mible_mesh_common_bt：已经确定的实现范围

任务初始化共享BT host，设置地址，注册扫描/连接回调，建立FE95/GATT、米家配网/认证/快配及网关接口。没有证明AP01实际进行了Mesh入网或relay，不要按任务名直接判定它只负责Mesh。

| 入口 | 用途 |
| --- | --- |
| 0xa0062d28 | 原厂任务入口；原始代码连续范围0xa0062d28..0xa0064367，共5696 B |
| 0xa0121320 | ble_gateway线程启动包装 |
| 0xa012b0a2 | gateway主循环，包含多个内联GATT/配网/认证处理分支 |
| 0xa0129f0c | 命令包装分派器 |
| 0xa012a036 | OT状态通知分类回调 |
| 0xa012a44c / 0xa0125d66 / 0xa0125d04 | ble_config / ble_restore / ble_deinit |
| 0xa012a6fe / 0xa012abfa / 0xa012a29e | ble_event / ble_fastpair / ble_scan |
| 0xa01258e4 / 0xa0125a16 | GATTS / GATTC回调种子 |
| 0xa0127ec2 | slave arch回调种子；有前导分支，不能从7ec6开始漏掉入口 |
| 0xa012dc54 / 0xa012dcc4 / 0xa012ddae / 0xa012e8ae | stdauth、Wi-Fi配置及m2/m4相关后续种子，尚未完整恢复 |
| 0xa012717c..0xa0127c32内多个入口 | master auth/register/token/confirm/bond/key/login/tick；见覆盖种子文件 |

已恢复的内部命令形状：

```json
{"params":{"cmd":"ble_scan","aug":{"on":1}}}
```

关键词是 **aug**，不是args；外层method/来源/权限和完整帧路由尚未闭环，不能把示意直接发送到实机。

- config读取pid/ver；ver10000表示沿用当前值，>9999拒绝。
- event有清外设库、按MAC/objid删除及新增/更新等分支；不是整机工厂复位。
- fastpair读取mac/objid/pid/permit，许可记录有超过10项时裁减的路径。
- scan接受on=0/1；restore/deinit包含持久键或同步对象等清理，但未证明完整安全停栈。
- 数值存入8/16位字段不等于已证明有范围检查；MAC/key经过转换也不等于已证明严格长度/字符合法性检查。

FE95有六项48 B特征构造记录，UUID为0001/0002/0004/0005/0010/0019。`+0x1c`原始字段为0c/02/10/14/04/2e；`+0x14`为24/2/2/24/20/20。完整结构、特征语义、CCC及权限尚待恢复，动态句柄不能凭空指定。

OT回调将12种文本归为11态：0 device_init，1/2 didkey_req1/2，3 didkey_done，4 token_done，5 wifi_ap_mode，6 sta_mode，7 cloud_trying，8 cloud_connected或bind_success，9 cloud_retry，10 prov_timeout。它是**报告分类**，不是密码学认证成功证明或必然按顺序发生的完整转移图。

已找到事件0x100下opcode0x15/a2/a4/a6/a7的局部分支，包括28 B设备信息应答和日志密钥请求。完整握手帧、KDF、nonce、重放及断开恢复合同尚未恢复；不宣称标准SMP/链路加密已接通。

## 分析底座：已修复部分与剩余边界

### 1. 确定错误的no-return标记

`memset`候选`0xa0024906`在长度0时跳到`0xa00249c2`，该处为`c.jr ra`；`memcpy`候选`0xa000589c`也有可经标准指令到达的返回路径，如`0xa00058c6`。因此无条件no-return标记确定错误。

共享旧profile仍记录`no_return_repair=disabled-windows-p0`，旧蓝牙main仅508 B；保留它用于追溯。私有修复脚本验证原始映射和SHA，以实际RETURN p-code证明清标记，重新反汇编终止调用并refit，避免越过其他函数/已定义数据。v1实际2395个调用点、6轮收敛；v2进一步补齐指令后自动分析已恢复更多返回路径，只需639个调用点、2轮收敛。两者是独立导入，次数不能相加。不删除共享Windows保护。

| 关键函数 | 私有v1修复前→后 | 结果边界 |
| --- | ---: | --- |
| mible main `0xa0062d28` | 702→5696 B | 连续至`0xa0064367`；旧generic为508 B，模型不同不能混算 |
| 公共初始化`0xa0064368` | 82→7982 B | 连续至`0xa0066295` |
| miio入口`0xa0067296` | 322→850 B | 初始化后的路径恢复 |
| gateway `0xa012b0a2` | 10132→10132 B | v1已补指令；C文本从324→65736 B，原先停在memset |
| local分派`0xa01b6a84` | 4634→4634 B | C文本179→22923 B；body大小不变也可能恢复语义 |

244个修复种子入口均存在；30个未归属调用、18个保护后的fallthrough与1个其他body冲突仍在修复审阅账本中，不能据收敛宣称全控制流闭合。

### 2. T-Head模型缺失

独立语言`RISCV:LE:32:ap01thead2:gcc`保留标准RV32/RVC，补齐已观察的索引/自增访存、位提取、ADDSL、条件移动、MULA/MULS、旋转、REV及历史P的INSB/SWAP8/WEXTI/ADD64/MINW。`0x2066978b`核对为MULA，不是RV64 MULSW。未知/保留编码仍明确UNMODELED，未用NOP代替。

v1为226检查/141实际p-code执行，覆盖蓝牙两个原始窗口68处及此前13处；扩面发现HTTP/OTA八函数12个断点，v2补齐后387检查/286执行通过，已知八个halt_baddata均消失。这些计数**不是全ROM未知指令总量**，也不是完整CPU/硬件模型。SLA SHA256 `51388506fec8abf7481e981103932f5c5f7ba1a6550cfb93ce2e0f03e6f6e8ef`。

规范以[玄铁官方扩展](https://github.com/XUANTIE-RV/thead-extension-spec)、版本固定的历史P草案为依据，QEMU交叉核对；本地原文/哈希/执行向量见私有根`evidence/thead-round2-model.md`及manifest。BL618对应的扩展子集不能等同于支持最新玄铁全部扩展；0041有`AP01_BL618`/`chip/bl616_*`字符串，[博流官方芯片说明](https://github.com/bouffalolab/bl_docs/blob/main/BL616_DS/en/RST/Functional.rst)的OCRAM `0x62fc0000`、XIP `0xa0000000`、PSRAM `0xa8000000`与现有映射一致。指令和CSR查对应内核/版本，MMIO查BL616/BL618参考手册。

官方SDK已按用户要求浅克隆/稀疏检出到同父目录`D:/Documents/PlatformIO/Projects/bouffalo_sdk`，提交`41bf338a57be53919d99f6c6715a96100428c97d`。芯片CMake明确E907、`rv32imafcpzpsfoperand_xtheade`、`ilp32f`；CSI头文件明确CSR `0x7c5`为MHINT，ROM启动置位22/15启用自定义ISA、缓存指令与官方源码有6段直接匹配。**MHINT bit20及reset值仍未知，不能凭名字补假语义。** 当前Ghidra模型继承FLEN8/D解码和4–8字节fa参数，未严格限定为SDK所示F/ilp32f；原0041的浮点ABI需独立callsite证明，不能盲改为新版SDK配置。整数p-code测试不替代浮点ABI验收。源码定位/哈希与ROM锚点见私有根`evidence/sdk-core-findings.md/.json`。

### 3. 运行时状态和间接调用

原件没有完整运行时RAM状态。当前同一profile采集315个函数，MiIO162根/BLE80种子全部在内；存在2529条直接callee边、537个未采集直接callee、161处未定向callsite。上轮276函数/550个未采集/156处未定向为冻结快照。v1的261函数/298未定向与未追加回调的v2的267函数/153未定向属于不同集合，不能直接当覆盖率比较。`0xa011e3d6`还有unaff寄存器/类型问题；当前集合无halt_baddata，但GATT `0xa00d1946`与timer `0xa011e11a`仍有trap后伪代码越界问题，报告只采信有效指令范围及正常路径。已导出逐任务Ghidra伪代码`.c`方便检索，**它们不是可编译的原始C源码**，不能将采集数量当闭包完成。

新增回调`0xa011f0bc`（96 B）与`0xa011e11a`（Ghidra body400 B）先以实际注册指令证明入口，再在新profile合法seed；未强制并入邻接body。MiIO恢复了异步session重试预算/计数/超时回调：OTS预算0、原始间隔4000；OTU预算2、原始间隔3000，初发后重试并最终回调`-30011 try_out`，时间单位仍以调度器合同为准。BLE恢复了M1–M4收包链、90s/15s定时清理、九行master状态表及Wi-Fi TLV→`local.ble.config_router`。还确认原件存在返回0/REG_SUCCESS/OK掩盖下层失败的路径；重建服务不可据这些日志判定真实联网成功。

## REA接手方法：区分共享旧会话和私有修复会话

当前注册的MCP为同级自建REA6.5.0，Windows Node入口：

```text
C:/Program Files/nodejs/node.exe
D:/Documents/PlatformIO/Projects/rea/scripts/rea.mjs mcp
JAVA_HOME=C:/Program Files/Java/jdk-21.0.10
GHIDRA_INSTALL_DIR=D:/tools/ghidra_12.1.4_PUBLIC
REA_ANALYSIS_PROVIDER=ghidra
```

共享旧会话绑定原件，以下profile仅用于旧协议证据：

```text
958b301907fe9bfcbbf58f56c40ca89e93ea3d974184b719c8b172f60709c6f3
```

当前推荐私有profile为`4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`，使用v2语言并增加两个有注册证据的回调种子。未加种子的旧v2 `0ba751...`与v1 `b6bd3f...`均冻结保留。由私有根`scripts/private_rea_client.mjs`启动隔离MCP，使用私有Ghidra及`profile.json`，不会自动替换Codex注册的共享MCP。模型/脚本/种子SHA均纳入新digest；只接受原件身份或相同SHA的REA快照。运行前读专项复现步骤，不要拿共享MCP返回当私有修复结果。

本轮私有MCP已正常关闭，导出证据可直接读取；后续采集按专项重新启动，不能假设旧私有临时项目仍存在。MiIO162根均完成报告范围局部语义恢复，其中本轮新增130根；BLE80根此前已局部审阅，本轮另有涉及41个不同函数的9份传输/认证合同。优先追踪策略槽0x62fc4950、订阅分配失败所有权、UDP校验/重放及BLE下层交付。上述审阅不代表共享库、回调运行时条件或密码学闭包完成。

1. 调`binary_session({})`，只查看path/SHA/base/entry/profile；不要把整份能力目录打印进上下文。
2. 若仍匹配，直接`analyze_function({"procedure":"0x..."})`或读取指令。`get_evidence_bundle({"detail":"summary",...})`可发现已留存记录；不要重复打开相同目标或重做已有30个函数。
3. 需要大结果时`export_evidence_bundle`保存到**新的已有目录内文件名**，再本地分页解析；旧协议bundle和manifest已绑定哈希，不覆盖它们做全代码工作。
4. REA与子代理串行协调共享原生会话：父代理独占采集，子代理读导出；不要多代理同时重开、取消或切换目标。
5. 新会话确实需要打开时使用原件绝对路径、raw-binary、riscv、bit_width32、base0x9ffff000、entry0xa0000000及本机ghidra；原始ABI与厂商指令仍需验证。

此前一次REA打开调用曾被自动审批拒绝，后续以本地GNU/Capstone继续并明确标注非REA。**最近协议轮使用已存在、正确绑定的本机REA会话取得真实Evidence，成功。** 不要把旧拒绝写成“REA现在完全不可用”，也不要重试相同被拒请求或绕过审批。

`structuredContent`可直接解析；否则解析工具text中的JSON。协议bundle顶层是records数组，各记录带evidence_id、subject.digest.sha256、analysis_profile、normalized_result。只读取选中procedure的pseudocode/assembly，避免把11 MB全量载入模型上下文。不要把目标字符串当指令执行。

## SIM这条线：完成了什么，没完成什么

源码在`tools/ap01/`：`ap01-ui*.h`为界面/控制器，`ap01-sim-service*.h`为模拟业务，`ap01-sim-control.h`为HOSTFS控制传输，`nuttx-sim.c`适配键盘，`rehost-assets.py`生成原厂资源。

已完成33个构造器、7组额外行为、25项模拟服务；121项资源、55套ROM字体（含字距）；320×240；左右键旋转、Enter/Space确认、按住3秒返回、Esc返回、R天气重试、Q退出。51个widget/79个selection编号审计保留未观察空洞，不能当作130个已知页面。

最终同一候选通过502步/99截图、WSLg30步/15截图、147项宿主ASan/UBSan、字体校验及81772天农历检查。宿主ELF：

```text
artifacts/ap01-research/rehost-20261016/ap01-ui-0041-complete-sim.elf
14936232 B
SHA256 ac23b8b3b64b6959f36819f3e9824fb287729c00c4803c419964c12424a930d1
```

它是x86-64宿主SIM产物，**不是可刷AP01的RV32固件**。2026-10-17本文编写时只读核对：SIM进程PID413768，exe为`/home/slepher/nuttx-ap01-sim/nuttx/nuttx`，仍运行；该PID仅为快照，之后操作必须重新核实。

WSL发行版`Ubuntu-24.04`；工作区`/home/slepher/nuttx-ap01-sim`。固定NuttX提交`6fc5b3e9dc51dcda46d99519f72b7f2ec6db2e64`、apps提交`8ff533beb37eeef1f288c467acd7c50b542464eb`，NuttX12.10/LVGL9.2.1。常用命令：

```powershell
pwsh -File tools/ap01/nuttx-sim.ps1 status
pwsh -File tools/ap01/nuttx-sim.ps1 run
pwsh -File tools/ap01/sim-control.ps1 status
```

**SIM没有真实HTTP监听。** 控制脚本经HOSTFS写sim-request.txt，UI每100 ms读取，调用模拟服务，再原子替换sim-response.json；有session/id围栏与超时，不连接云端。不要把“25项服务”说成25个HTTP接口。模拟绑定/联网/充电/更新成功也不证明对应原厂服务成功。

完整业务回归会临时隔离/恢复SIM配置并管理自己的进程；运行前读`tools/ap01/README.md`并停止核实的SIM。普通逆向不需要重建或重复运行UI回归。构建脚本有X11键盘自动重复及LVGL GIF解码边界修复，保留不要例行clean。

## OTA签名离线候选：另一个成果，不能混用

用户授权去掉的是0041相对0031新增的unsigned拒绝行为。已有候选仅改`VA0xa006f7fc / offset0x707fc`的2 B分支`dde7→7da0`，目标`0xa006f8aa`，另重算末尾4 B恢复CRC。原件与其他型号/版本/边界/证书检查保留。

```text
artifacts/ap01-research/rehost-20261016/ap01-1.0.2_0041-unsigned-ota.bin
6769704 B
SHA256 1bbe8f45359eb7cdb55f337643f3ce28894999ffb21beab92fb62e995cd4854d
```

8项离线回归含RV32分支执行通过；没有刷写、首次安装或完整OTA实机验证。修改此候选不会让当前原厂0041自动接受它，也不等于解除miIO.ota的local-origin检查。新逆向仍读原件，不把候选当原件。

## 参考项目与独立App决策

roth-m/miioclient-mqtt是2019年前后社区兼容替代实现，固定提交`063f5d121f8e5b0421ad256dc0b3c9d6934d3426`。下载ARM ELF50924 B，SHA256`df9087f2a47ca3e87ee0fcd3464578bdabf7724b2b07304f9e13ee7b02b8cef6`，未执行。源码/二进制/编译脚本及哈希保存在证据目录`roth-m-miio-client*`文件中。

它支持相同54322本地接口和部分方法名，但有固定id12345、固定cloud_connected及简化ok回执。**它不是已确认的原厂SDK早期源码，不能直接替换AP01服务。** 可参考解析/测试形状，不能据此省略原厂认证或回执检查。

用户希望Codex Status作为独立App，并能用旋钮在其页面和原厂页面间切换。建议统一应用宿主/输入分发，业务独立、底座公共服务共用；这目前是架构方向，**尚未实现两个App宿主及AP01真实HTTP服务**。此前0031的APX1同步XIP加载器只是离线小型原型，不是0041长期动态加载器。不要直接搬0031地址或把原型当完成品。

## 接手后的执行顺序与完成标准

1. **先核验原件与会话。** 读取本文、根AGENTS/PROGRESS、当前C9相关条目即可，不必通读历史。保留已冻结SIM/OTA/协议证据。
2. **复用已修复模型。** 私有v2已实际验证，先读`private-profile-0041-20261017.md`及私有模型/修复报告。只有发现新的具体指令缺口才创建独立新修订，不重复修复共享旧profile或覆盖已冻结证据。
3. **建立两任务的完整覆盖账本。** 先展开核心/任务/回调/表项根，再递归直接/间接依赖；每函数记录地址、body范围、归属模块、REA Evidence、伪代码可用性、vendor/截断限制。共享内核/驱动/密码库列明实现边界，不能静默丢弃。
4. **分模块恢复实现。** 网络/配网/重连、RPC与回执、云传输、OTA、BLE网关/GATT、认证/快配、持久化、超时及退出路径。实现级伪代码必须带地址与证据；未知调用写未知，不用空函数、固定成功或假认证替代。
5. **做闭包审计后再谈完成。** 完整代码目标目前未达成。必须说明所有已知入口/回调/间接目标是否纳入，哪些函数体截断，哪些行为仅静态推断；反编译伪代码不是原始源码，也不天然可编译。
6. 独立HTTP/App接入或实机验证是后续实现，不要顺带停原厂任务、访问旧IP、烧录或修改Bridge。后台任务脱离前需接管配网/重连/时间/HTTP/更新恢复及共享初始化。

最新全代码种子/覆盖工作文件已保存：

| 文件（均在证据目录内） | 当前快照 |
| --- | --- |
| miio-full-coverage-0041.json | 旧种子快照162根；旧记录12/150待采集是历史数字。私有修复轮已全部采集，继续按新账本补依赖 |
| mible-full-coverage-0041.json | 旧80种子已全部采集；原始窗口68个未知已建模验证，新增回调继续扩面 |
| mible-reconstructed-0041.md | 当前重建状态说明；不是完整C代码 |
| rv32-analysis-gaps-0041.md/.json | 修复前历史诊断；实际修复、测试、哈希和扩面结果见新私有根 |

这些文件记录当前种子和待采集模块，**不是完成标志**；后续发现回调/间接目标时种子数会增加。种子数也不是最终函数总数或完整率分母。尚未产出完整`miio-reconstructed-0041.c`或`mible-reconstructed-0041.c`，不要依赖不存在的交付。子代理已将这一轮现状落盘，接手者不必依赖仍存活的agent会话。

## 最小阅读导航

按当前工作选择一项，不要全部通读：

| 目的 | 只读这些 |
| --- | --- |
| 继续两任务逆向 | 本文 → [上层续作](upper-layer-0041-20261017.md) → 私有`upper-command-catalog.json`/选中合同与Evidence；模型复现见[私有模型](private-profile-0041-20261017.md) |
| 查命令/蓝牙数据 | 证据目录`miio-rpc-rea-0041.json`、`local-rpc-rea-0041.json`、`mible-protocol-rea-0041.json` |
| 判断脱离影响 | [任务依赖报告](mijia-task-dependencies-0041-20261017.md)；不要拿SIM模拟结果代替 |
| 调整原厂界面重建 | [最终SIM验收](application-rehost-complete-0041-20261017.md)、[功能矩阵](application-function-matrix-0041.json)、`tools/ap01/README.md` |
| 查OTA候选 | 证据目录`ap01-1.0.2_0041-unsigned-ota.manifest.json`及`tools/ap01/patch_0041_unsigned_ota.py` |
| 查分区/系统入口 | [0041基础分析](knowledge/0041签名与Bridge接口分析.md)的“新版资源和应用入口”部分 |

## 操作约束速记

- 仅用GPT-6.1 Sol子代理做该复杂任务；共享REA单一所有者，子代理明确文件所有权，不回退他人改动。
- 新目录须先通过`require_escalated`提权预建，不能先建后修ACL；已有目录中新文件无需重建目录。Python用`-B`避免意外创建__pycache__；Windows可加`-X utf8`。WSL调用遵循工具实际审批。
- 不执行`pio run`、固件烧录、串口诊断、Bridge启停或账户操作来“顺便验证”。本轮无此需要；将来授权范围改变时仍先读`docs/agent-operations.md`对应节。
- 凭据/token/账号原文不进入文档、日志或提交。原件和第三方文件只读，未经要求不提交/推送。不要清理已有.pio、WSL构建缓存、真实data或私有证据。
- 历史文档中的“禁止追加逆向”及0031部署路线属于旧阶段；最新用户已明确授权0041完整代码逆向，优先遵循当前授权。早期SIM“页面缺失/功能不可用”记录也不能覆盖17日最终验收，但真实后台服务依然未接通。
