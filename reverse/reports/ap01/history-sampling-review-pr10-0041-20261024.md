# P-R10：P-10 轮询到功率历史采样事件合同非作者复核

**可独立使用阶段已闭合但接口未闭；限定接受 P-10，行为纠正0。** 普通匹配 cmd50 到各实际遍历 item、随后 total 历史写入的事件轴可用于接入。固定采样率、180槽对应物理时长、MCU测量时刻及最终投递活性没有闭合；不以本批验收代表完整遥测或 ROM 恢复。新增业务算法恢复0。

认领 P-10 的非作者复核 P-R10；复核者未参与作者工作。基线 `5bbc331`，独占 `.worktrees/batch-20261024-p/pr10`，只写本报告与同名 analysis。主树只读；父窗确认作者已停止、5项产物逐字节保存。已读主树 reverse-design、管理顶部P及P-10当前行，不通读滚动历史。采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 留存优先流程，不开/切共享REA及模型、不创建代理、不执行目标/设备/网络/SIM/QEMU/回放/构建/指令或输入模型，不修改ROM、生产、配置、分析器或作者产物，不提交推送。

开始 `2026-10-24 14:34:30 UTC`，原估约30分钟；按证据收敛提前交付，结束及墙钟见末节。Token由父窗统计，本席无实测用量接口，不估造有效工时。

## 继承结论

主复核对象为 [P-10作者报告](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/history-sampling-p10-0041-20261024.md)及其 `interface.json/static-evidence.json`；没有运行或导入作者验证器。必要前提：dock/B01默认表与selector、B03 helper后cmd58 phase写入、B05初始化局部、B19正常parser、B21描述符/固定槽/两次handler、P-02/P-R02普通数值到历史通知、window-history 364B/180槽合同。不重做历史算法、队列/driver、工厂分支、绘图reader及公共库内部。

原件沿 [CATALOG](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/CATALOG.md) 的0041：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。RV32 little-endian，`file_offset=VA-0x9ffff000`。只读取所需原件窗口，不另造整件哈希清单。

| 来源 | 独立核对与边界 |
| --- | --- |
| timer `0xa00a805a`完整留存 | dock `retained-functions.json#/functions[1]`，Evidence `ev_5fd69f489ac24670f4c858f79225e681a50079c28b088bb18e6f7b999de4fa59`，原 `whole-rom-private-20261023-066.json`，Ghidra12.1.4，thead2，digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3` |
| helper `0xa0191652` | `uart-response-0041-20261023.json#/functions[1]`及其原 `whole-rom-uart-retry-20261023-001.json`，Evidence `ev_3a861f94ddb2b4481b6d96b4f46d593f35e2729ecb9022aa64949e92b607615c`；直接核原记录Ghidra12.1.4/thead2/上述b636 digest |
| timer/helper/selector旧指令 | dock `instruction-windows.json` 的静态decoder engine `[5,0,1280]`，unknown厂商word保持unknown文本，语义承继B01。不能贴上Ghidra profile或新Evidence身份 |
| cmd50/cmd58 dispatcher | `buzzer-backlight-0041-20261023.json#/functions[address=0xa00a8582]`，Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`，原round3 initial bundle，Ghidra12.1.4/thead3，digest `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279` |
| timer注册与默认表 | 注册按 `timer-registration-source.json` 的thead3来源，不混同timer callback的thead2；32B默认表从ROM `0xa0004634`直接读取并与旧initializer核对 |

原provider的坏指令/函数控制流局限继续存在。本复核核局部正常窗口和既有独立验收的接缝，不将234行当完整dispatcher/全部writer覆盖，也不把本次核对时戳替换原Evidence采集身份。

## 本轮复核或纠正

以下为静态字节观察及条件控制流推断；结构名为分析命名。

| 验收项 | 决定 | 依据及不能外推的内容 |
| --- | --- | --- |
| 默认58优先、慢组门 | 接受 | 原32B表：groups `0x62fc4b20`，controller `0x62fc4b30`，58组limit1/period1；50/51/57/59组limit4/period10。selector按组顺序、phase余数和sent选择；50须首组已耗尽且慢组sent0。off-phase到 `0xa0191766` 写sent=limit，已耗尽经 `179c→176a` 不写sent |
| sent与交付 | 接受 | `17b6→0xa01951e2`返回后 `17ba`重读sent，`17c2` byte写递增；没有业务成功回执门。依B21可去重或满槽返回，因此sent不等于实际发送/响应/样本数 |
| timer消费done | 接受 | `82be`重试推进先返回，再读done；非零时清done、byte phase自增、清各sent、selector。普通presence/USB stage门和五相USB机会继续有效。注册20的ms识别继承旧LV接口，本轮未认证库时钟或实测实时边界 |
| helper与58次序 | 接受 | helper `1668`清transport state，`168e`可置done1后才比较/复制/派生通知；有eligible项跳 `1692`，不主动清旧done。58在 `8780`helper返回后重读cache，非零 `878e`清phase byte，再去selector；本局部不重新判done或清sent。间接handler副作用不能排除 |
| phase全部循环 | 接受 | byte写入不是mod10；即使只许自增，250→0为6次advance，普通整十间隔才10。B05已验55路径phase1→done0→sent0→selector，前奏须返回。不能从period10推出固定十次timer、1秒/点或180秒窗 |
| 正常接收/handler门 | 接受 | 按B19/B21只承接原CRC及state2/cmd匹配门后、当前handler确为普通dispatcher的路径；先响应副本/state3再首次handler。返回后槽重读发0x24，目标可变；普通0x24还受OTA/state门。不能把任意收到帧或任意0x24当样本 |
| cmd50长度与raw不变 | 接受 | `8b76/8b82/8b88`得到 `(u8[count]<<3)&0xf8`，是原截断公式，不追加count合法范围或响应len等于n的保证。helper返回后直接进入工厂/普通门，不按a0/raw变化跳过业务。旧helper比较相等只跳copy/派生cmd70，普通历史仍可发生。未进行外层长度审计 |
| 对象门/实际遍历 | 接受 | 必须到 `8bac`普通阶段且T非空；`8bb4→8aae`无本题历史。每次边界重读T/count；caller缓存I、普通数值helper重取对象与notifier重取对象的相等有条件。工厂路线、回调替换/销毁及重入不因本批而获得保证 |
| item和total样本 | 接受 | `9298/929c/92a0`传LHU(I+8)、I+0x3c，位4不门控该call；随后才可能同步item通知。loop退出 `8bd8`可直接到 `8c10`，重新取T、LHU(T+4)、T+0xe后call历史；count0亦可到此，未重算时写旧总值。稳定对象且原callee正常返回才有逐遍历item一次与total tail一次 |
| 样本、0x400与通知 | 接受 | 写历史后才OR0x400；历史返回0仍可能因其他mask通知，且可完全静默。承继180槽helper每call写入/推进，重复值或0不是跳样门。故样本数、历史事件数、所有通知数分离，通知时间戳漏静默写入 |
| 时间轴与新策略 | 接受 | 364B历史视图无时间戳，容量180不代表180次有效测量或180秒。对象写入序号能表达局部先后；cursor差有模180混叠。新接收/入口单调时钟、响应号、对象代际及不规则绘图是重建设计选择，不能反写为ROM字段/测量时间 |

无需作者修正。上述长度说明是对原公式的边界澄清，未判定作者错误或展开异常输入。接入应在同步边界复制所需标量/视图到自有存储；不跨回调持有借用T/I/view，不额外假设原程序原子性、所有权或活性。

## 真正新增

业务恢复0。新写 [独立stdlib核验源码](../../analysis/history-sampling-review-pr10-0041-20261024/independent_review.py)，实际运行产生 [独立检查记录](../../analysis/history-sampling-review-pr10-0041-20261024/independent-checks.json)：315项PASS，11窗766B/234行，另32B默认表。作者JSON仅用作待核位置索引，逐行另取旧decoder/dispatcher assembly及旧raw_ranges核对；直接从ROM独立解析2/4B长度、指定JAL/branch目标、LBU/LHU与byte store字段、count截断及历史call参数位置。没有运行、导入或复制作者验证器，没有使用Capstone或执行指令模型。

人工静态复核沿selector off-phase/耗尽分叉、helper完成先判、58后读cache、普通item/total尾与静默通知关系完成组合。检查数和字节相同不代表完整数据流形式证明；厂商指令语义仍继承既有验收，无新增ISA来源认证。

## 未闭精确边

可独立接受的是“正常匹配cmd50且普通对象门满足→历史写入→条件通知”的采样事件阶段。完整物理时间接口仍未闭：实际timer/响应延迟、MCU测量瞬间/年龄与wire物理单位、全部phase/table/handler writer、最终请求投递和有限最大断样时间、跨响应对象代际及原子快照均未知。不能给固定率、最短间隔、有限最大间隔或信号带宽保证。

保留后继种子 `0xa00a8c1a→0xa00a398c(T+0xe)` 与 `0xa00a92a0→0xa00a398c(I+0x3c)` 的真实ring reader，须父窗查重后另排；当前theme callback不能仅凭名称认作reader。本席未展开该后继、库timer、队列/driver内部或全MCU。

结束 `2026-10-24 14:39:18 UTC`，墙钟约288秒，按证据收敛提前交付；无主动等待或任务中断。两次初始只读命令受登录shell目录覆盖而未找到输入，显式login:false后继续；没有因此改动来源。工具读取/编写/检查包含墙钟，未测有效工时；token由父窗统计。

315项独立检查、JSON解析、6个本地引用、UTF-8/尾换行/无尾空格、独占路径状态和diff检查PASS，见 [交付记录](../../analysis/history-sampling-review-pr10-0041-20261024/delivery-checks.json)。只新增本报告、独立核验源码与两份JSON，共4产物；JSON按现行规则留在原路径本地忽略。未提交推送，交付后停止；由父窗整合限定接受状态，不改写作者待复核稿或管理表。
