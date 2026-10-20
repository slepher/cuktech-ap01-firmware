# 0031 自定义 App：已有准备与继续入口

2026-10-13，依据用户纠正核查。**实际部署目标是支持自定义App的0031变体**：保留原厂系统/驱动/米家配网，新增稳定更新底座和Bridge应用。0041签名研究保存为版本对照，不构成升级或移植任务。尚无本项目可刷的AP01 Bridge ROM。

## 已有记录


| 准备 | 可继续使用的资料 | 完成范围与边界 |
| --- | --- | --- |
| 0031原件、分区和启动 | [0031分区与启动](knowledge/0031分区与启动入口复查.md)、[提取证据](../../raw/0031-deep-20261011/evidence.json) | 固定原件SHA/CRC；双固件槽、资源区、ROMFS/rcS、8项内置应用表已提取。布局是静态配置，不是同机Flash备份 |
| 分配器与4 MiB外部堆 | 上述知识第7节、[堆反汇编](../../raw/bridge-budget-20261011/selected-disassembly.txt) | 原厂malloc与外部区域登记属于同一堆的调用路径已核对；实际空闲、连续块及代码执行能力未测 |
| 完整Bridge架构 | [接入设计](design.md)第2/4/5节、[需求SPEC-RE-002/003](requirements.md) | Wi-Fi常驻、米家配网、BLE仅Bridge绑定、完整1–8模板、MAC/token/owner/事务及共用绘制的设计已有；设备适配未实现 |
| RV32尺寸试编译 | [resource-budget.json](../../raw/bridge-budget-20261011/resource-budget.json)、探针对象（材料未随仓库收录：`../../reverse/raw/bridge-budget-20261011/layout-probe.o`） | 有源哈希、工具命令、RV32布局与对象；CtTemplate 11,321 B，序列化缓存11,333 B。是数据尺寸探针，不是完整C++应用或ROM |
| HTTP/socket调查 | [0031网络复查](knowledge/0031网络监听与HTTP复查.md)、[GNU监听反汇编](../../raw/bridge-budget-20261011/http-listener-objdump.txt) | 原厂回环127.0.0.1:54322及客户端路径已定位；没有证明现成LAN HTTP路由可挂接 |
| 独立App与稳定更新服务 | [接入设计第6节](design.md)、[App调查产物](../../raw/bridge-budget-20261011/app-ota-assessment.json) | 版本化C接口、App描述、独立更新任务、下载后停止覆盖、启动健康确认/内置恢复均已设计；动态加载执行仍未验 |
| 首次安装及原厂恢复材料 | [阶段报告](report.md#首次刷入评定)、[下载记录](firmware-download-20261013.md)、[修正后的刷入方案](first-flash-plan-20261013.md) | 0031原厂MiIO未签名OTA有作者实践及本地分支证据；本机首次安装、修改版到原件回刷和独立救砖尚未验 |


## 上游现有载荷能提供什么

只读第三方克隆的`features/agents_dashboard_firmware/result_loader.c`已有原厂分配/释放、webclient、定时器、显示及交互包装；`result_loader.ld`把载荷链接到`0xA02465D0`、容量60,934 B。这些可用来缩短0031调用点调查，实际声明/参数仍逐项核对。

它校验并下载的是APAG v2页面/GIF数据；载荷代码本身通过build.py注入完整ROM。它没有证明“从文件下载新的可执行App并运行”。现有链接脚本主要收集text/rodata/assets，也不能代替完整C++程序的数据/BSS初始化和构造流程。不要把这个上游GIF载荷作为本项目已完成的App加载器。

## 接续工作


1. 按**0031**继续核实任务/网络/显示/存储ABI，验证受限App执行区域、缓存同步、重定位和数据初始化；核对C++工具链与运行时，先跑可返回的小模块及健康回执。
2. 在同一0031基线制作稳定底座＋最小App候选，完成首次安装、原厂共存、诊断和修复入口验证，再接完整Bridge应用。无需另起0041移植计划。
3. 应用与Bundle仍为单份，下载/预检后停止并覆盖；实测资源、当前格式预算和恢复条件通过后验App OTA。原生ROM双槽保留。

若独立App执行条件未成立，只能把编译进ROM的最小模块作为接口验证中间产物，不能把整镜像迭代或GIF刷新报告成已经实现独立App OTA。

## 本轮核查
