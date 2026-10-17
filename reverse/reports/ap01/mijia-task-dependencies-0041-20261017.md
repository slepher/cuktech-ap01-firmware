# AP01 0041 米家任务功能与脱离影响

2026-10-17。按用户要求，使用GPT-6.1 Sol子代理分别分析miio_client与mible_mesh_common_bt，父代理核对启动/UI/天气边界。仅离线原件分析，不连接设备、不终止任务、不刷机、不改Bridge。原件SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。

## 任务身份与判定边界

rcS分别后台启动两任务及lvgl_ui_main；两项内置入口各配置6144 B栈。此数字不含派生线程、堆、网络缓冲和系统对象。停止前台页面与停止后台任务不同；不启动父任务、运行中强制终止、删除整个SDK代码也不是同一操作。未证明NuttX各任务具备独立地址空间或安全强制卸载能力。

## miio_client

应用入口`0xa0067296`，网络/事件循环`0xa0066296`，公共组件初始化`0xa0064368`。

| 功能 | 0041静态证据 | 脱离影响 |
| --- | --- | --- |
| 米家消息及本地RPC | localhost TCP54322、poll/accept、method与local.分派；详见localhost专项 | 原厂本地协调入口与米家命令/状态链无法照常使用 |
| 原厂Wi-Fi连接管理 | `0xa006580c..5840`注册扫描/完成/连接/断开回调；`0xa00657a6..57c4`创建netMonitorTask，入口`0xa006d260` | 不启动会跳过这些初始化；不能保证原厂自动连接、DHCP和重连可用 |
| 网络地址获取与链路事件 | `0xa006d124..d258`有DHCP/IPv4路径；主事件循环处理wlan0 link-down并中断DHCP | 内核网卡驱动存在不等于原有网络管理仍正常 |
| HTTP及云通信工作任务 | 公共初始化创建httpc_task(`0xa0123dca`, 参数0x1400)、otu_task(`0xa011b158`,0x1000)、ots_task(`0xa011a020`,0x1400) | 从启动阶段禁用会跳过这些任务创建；原厂HTTP客户端基础也需另行接续 |
| 原厂OTA控制面 | miIO.ota表项`0xa066de24`→`0xa01158f6`；ota_app在`0xa0064654`附加 | 原厂米家OTA命令/协调失去正常入口；不等于Flash安装代码或Bootloader从ROM消失 |
| 时间同步线索 | `waiting for the miio ntp result`及otn_ntp相关实现 | 存在米家时间相关路径，但完整校时依赖尚未证明；独立方案必须验证或另接校时 |

`netMonitorTask`自身传入栈参数0x1000。以上栈参数未结合创建封装完整ABI及实机高水位作容量验收，不能相加后当作可回收RAM。强杀父任务是否保留或回收子任务/注册对象取决于任务组与实现，尚未验证。

上述DHCP路径位于注册的连接回调`0xa006cda4`内，而不是netMonitorTask函数体。`miIO.ota`处理器还在`0xa0115916..5956`拒绝local-origin上下文，不能把localhost RPC直接当作已可用的本地OTA入口。

## mible_mesh_common_bt

内置入口`0xa0062d28`。直接初始化蓝牙host（`0xa0063048`→`0xa00da95e`）、公共地址及扫描/连接回调，并注册`ble_config`、`ble_restore`、`ble_deinit`、`ble_event`、`ble_fastpair`、`ble_scan`等RPC（`0xa0063d72..3ed6`→`0xa0129608`），创建ble_gateway。

因此该任务不是仅由名字判断的可选Mesh转发进程；至少承担共享蓝牙栈初始化、米家蓝牙配网/快配及蓝牙网关接口。若从启动时删除，会失去这条初始化和注册链。已有Wi-Fi凭据不会仅因少启动一个任务就被主动擦除，但新配网、改网、恢复出厂后重新接入不能假定还有效。

进一步证据：`0xa00641fc`创建ble_gateway（入口`0xa0121320`），在`0xa0121402`调用`0xa012b0a2`；`0xa012b36a`设置FE95服务UUID，`0xa012b4d0`调用GATT注册`0xa00d1946`，`0xa012b7c4`引用`stdauth_wificfg_recp_opcode_process`。存在米家应用层认证、token/key及绑定处理，不能等同于已经具备标准SMP链路加密。另有rpc_consume子线程和共享回调；内部清理路径`0xa0063910..3a92`不证明外部强杀会执行它。

蓝牙鉴权、配网状态向OT传递和蓝牙相关米家操作的详细证据/边界保存在子代理报告；是否实际加入Mesh网络、是否必须承担特定充电硬件通信，不依据任务名作结论。

## 界面、天气与充电的边界

- 显示/旋钮主应用为lvgl_ui_main；切换独立App前台无须因此终止上述后台任务。但启动就绪、绑定/在线状态、网络服务仍需接续。
- 天气请求的字面URL明确为`https://iot.cuktech.net/api/weather2?`和`/api/weather?`，实际引用分别在`0xa00aad5e`、`0xa00aaf5e`。天气业务还有PogoPinMng/WeatherApi及线程池初始化。不能简单说“天气就是米家云转发”；独立保留天气仍需替代Wi-Fi、HTTP客户端及核清地点/身份/时间依赖。
- 原件存在PogoPinMng/UartComm、TA1208/TA1408及ADC/温度/端口循环等独立硬件管理线索。它们与米家蓝牙任务不同，不支持直接断言“禁用蓝牙就不能充电”，也不支持在未恢复完整初始化依赖前承诺显示、端口控制、统计均完全不受影响。
- 原厂米家绑定/远程功能/OTA与自建Bridge身份及HTTP服务不是同一权限体系；保留/替代时分别处理，不沿用原厂token冒充Bridge授权。

## 实施判断

当前独立App接入优先保留两项后台任务；不再需要米家时，可将其作为单独的底座解耦目标，先补独立Wi-Fi配网/凭据/连接重连、时间来源、HTTP客户端、天气输入和设备更新/恢复，再逐项关闭依赖。仅改rcS删除两行不能称为完成脱离。

本轮不执行停用实验。实际故障表现、启动是否等待、丢失网络时的超时路径、充电控制/保护及可回收RAM，均需在匹配ROM的运行环境验证；SIM的模拟服务不能替代这些实机结论。

证据：[miio子代理报告](../../artifacts/ap01-research/rehost-20261016/miio-dependency-0041.json)、[蓝牙子代理报告](../../artifacts/ap01-research/rehost-20261016/mible-dependency-0041.json)、[父级UI/天气指令窗口](../../artifacts/ap01-research/rehost-20261016/app-service-ui-dependency-windows.txt)、[原厂启动/入口表](knowledge/0041签名与Bridge接口分析.md:102)、[localhost核对](localhost-service-0041-20261017.md)。已留存Ghidra导出含custom0/unaff限制，本轮Capstone对未知厂商指令保留原始字节，不将字符串定位当作运行验证。
