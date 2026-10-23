# J01：充电旧成果复用与精确缺口检索

**充电UI/本地服务主体早已完成SIM验收；本轮不重新恢复。只保留一个有既存函数/字段种子的合同认证候选：`a00a8582` 的 cmd51 完整正常设备类型分类，连接到 item+0x0e 的类型更新。** 这不是新发现函数或新增功能；E01/E02明确未认证完整分类，原函数已经留存，应优先复用。其余候选按后续覆盖收缩；无新别名/触发种子的未知不派全ROM搜索。

2026-10-24；基线 `7119b59`，独占树/分支 `re0041-j01` / `codex/re-0041-j01`。采用 reverse-engineer-anything 技能的既有证据优先规则，本题只读报告、JSON元数据及既存汇编锚点是否存在，不读取ROM、不解码原字、不新反编译、不裁决技术争议。未开共享REA target/database，无模型/固件/SIM/构建/历史回放/设备/网络或下级agent。仅写本报告及同名analysis，不改主树共享、生产ROM配置模型或他人成果，不再写旧树。

## 继承结论：已有 → 行为 → 局限 → 实际缺口

旧 ignored 文件统一从 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/` 绝对路径只读；旧 `artifacts/tools` 别名不当作材料缺失。下表引用近期正式报告作合同依据，未把旧JSON伪代码或SIM模型提升为新的技术验收。

| 旧出处 | 已解释行为 | 局限与真实精确缺口/处理 |
| --- | --- | --- |
| [application complete](application-rehost-complete-0041-20261017.md)、[function matrix](application-function-matrix-0041.json)、主仓`reverse/rehost/complete-nuttx-sim-verification.json`和`complete-live-verification.json` | charge家族12项`passed-in-sim`；全应用最终同一SIM二进制502步/99截图及30步/15截图；六个mode/port/safe/protocol服务入口已有本地验收 | 只是可达应用重建/本地服务验收，不是原ROM运行、硬件协议/物理持久化认证。不能以模型成功反证ROM完整或重开整UI |
| [factory-reference-map](factory-reference-map-0041-20261020.md)及其analysis JSON；`charge-complete-0041.json` | 文件/seed/资源索引可定位；充电complete含12构造器、screen/state及service contract，明确外部服务替代和部分布局重建 | factory map“待补关联”不是整个文件未分析；先服从后续专项。模型布局/scroll/chart不能当ROMABI证据，不重建矩阵/资源 |
| `charge-0041-round4.json`→`charge-complete-0041.json`；complete records[8]/[9]/[19] | C1/C2四槽IN/OUT/P/V/A、SOC/H/M、详情普通数值/历史业务已有；`a00f4610/a00f44e8/a00f5288`有旧原件记录 | round4 connected-device/protocol/safe动画“未恢复”已被complete的SIM整合取代；不能将旧pending作为现状。原记录存在也不等于全部厂商ABI已核，依专项范围引用 |
| `details-0041-round4.json`、page-logic及旧main/detail knob材料；[E07交叉索引](ctk-extra-consumers-e07-0041-20261023.md) | 旧导航、页面/旋钮和构造资料可复用；details文件实际是Date/Weather，不是CTK detail | 文件名或同偏移不能作对象别名；E07已读最终ZIP charge/details的服务字段，不重复ZIP复制/解包。没有新真实扩展指针别名种子 |
| E01/E02→[E03](ctk-view-dataflow-e03-0041-20261023.md)/[E04](ctk-view-review-e04-0041-20261023.md)→[E12](ctk-snapshot-consumer-e12-0041-20261024.md) | item+28/+2c/+30借用转换、真实注册/dispatcher→`a00adabc`→stack view→主要标量消费→栈归还已闭；port1/port2谓词互斥 | E01/E02旧“caller/dst未核”不得重开。item+34/+38真实值读者依旧未知，但本轮无新跨调用/快照别名，不能派全ROMgetter/字段扫 |
| E07/E08→[E09](ctk-caller-alias-e09-0041-20261023.md)/[E11](ctk-round3-coverage-review-e11-0041-20261024.md) | 较晚round3已有`a00a12d0..a00a24a5`正常body及`a00a1aa8`保存槽普通字段使用 | 旧body边界失识已解决；该直接链不是+34/+38读者。不得再派入口/CFG恢复、重复函数导出或以未命中断言字段无消费者 |
| [E13](ctk-offline-transition-e13-0041-20261024.md)与旧round4 records[4]/[5]、已知滑动合同 | 旧非零→新零门、同app选择器、对应活动C1/C2切回Power、四槽reset→SOC、同stack view寿命已整理 | 专项未展开helper不等于旧成果缺失；E13明确不再另立selector/滑动研究题。其作者局部校核不扩成整个callback独立验收 |
| [total consumers](ui-total-consumers-0041-20261023.md)→[theme total](theme-total-state-0041-20261023.md)→[window history](window-history-0041-20261023.md)/[theme online](theme-online-0041-20261023.md) | 模式文字、活动位、动画延后掩码、切换执行/完成、180点环形历史及最大值重扫已有原件合同 | 旧“a00f3844/a00f388c未核”由C09–C12细化；延后重放最终触发、采样时间/全部绘图仍有限定。本轮没有新的触发/绘图消费者种子，不重做已知环形算法/动画库 |
| C09–C12→[C14](text-update-entry-review-c14-0041-20261023.md)/[C23](text-entry-source-c23-0041-20261024.md)；B20/[B21](queued-command-review-b21-0041-20261023.md)、D01/D02 | 详情摘要/模式控件与文本入口局部所有权已核，C23有局部候选来源；正常len1..45命令同步复制到槽/活动区，栈描述符不被持有 | 不再以旧C10/C12或E01的历史未知重开formatter入口或提交器栈载荷复制。C23独立来源复核由正在运行C24负责；完整formatter/allocator仍非本题 |
| E14/E15→E16/E17→[E19](uv-time-division-review-e19-0041-20261024.md)对E18的复核 | uv deadline/unsigned门、真实时间槽生产者、实际固定分母下返回pair=(t,0)已有局部闭包与独立复核 | 不以E16/E17当时“完整除法未核”重开实际调用；任意分母、物理单位/epoch/cadence仍受限定。通用uv/clock并非充电专属新业务，不另派计数writer/时钟搜索 |
| E05/E06→[E10](main-app-root-exit-e10-0041-20261024.md) | 真实主app持有、DELETE timer/state清理、显示删除时条件递归路径与host probe区别已有 | 原业务动作→主W/S实际删除、目标item节点注销/回收仍缺真实触发种子。E10明确无种子不重复派root退出搜索；不把SIM重建销毁等同ROM动作，不与I01启动/I03屏保/A54reader争范围 |

## 本轮复核或纠正：只纠正复用口径

技术语义纠正0。本轮确认complete/最终验收真实可读、matrix充电12项均为SIM口径；最终两份报告绑定同一binary标识。`details-0041-round4.json`的scope确为Date/Weather；charge complete明确继承charge round4并声明外部服务替代。旧E07 body缺口、E01 caller缺口、C10/C12文本入口缺口均须以较新覆盖为准。以上是索引/覆盖核对，不重新验收既有原字或裁决其全部语义。

只提出一个精确候选，交管理者决定：

| 问题/种子 | 已有可靠定位 | 真正认证缺口、复用边界与重叠检查 |
| --- | --- | --- |
| **cmd51正常设备类型分类→item+0x0e更新前的new_type** | [E01](uiiface-item-ownership-e01-0041-20261023.md)列`a00a93a4..940c`、fallback `a00a9454..947c`和`a00a9504`比较/类型变化接点；[E02](uiiface-ownership-review-e02-0041-20261023.md)明确完整分类未核。`reverse/analysis/buzzer-backlight-0041-20261023.json#/functions`已有`a00a8582`，Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`，extent `a00a8582..a00a9d1d`，上述3地址锚点均存在 | 只从旧留存提取正常分类树各输入记录/位宽/分支到new_type的合同，必要时后继才做稀疏校核。E01/E02已核类型变化后的五指针清理/分配/通知完全继承；不恢复整个dispatcher、其他response、UART/driver/物理硬件。当前服务模型语义类型不能替代ROM分类。近期报告精确`93a4/9454/9504/类型分类`检索仅E01/E02指出该边；B/D发送与普通响应验收不宣称完整分类，与运行I01/I03/A54范围不同 |

此处“有种子”只表示旧函数/字段/接点可定位，不证明分类树尚无其他历史文字分析、也不证明任意设备类型的产品含义。后继须先复用该完整body，已有覆盖则收缩；不得因为标题新而重新导出6044B函数。

## 真正新增

新增功能0、ROM取证0、函数导出0、模型改动0、来源排除0。交付仅为短复用表、覆盖更新链和一个已有证据认证候选；没有复制完整函数/源码/资源、生成哈希清单、重建矩阵或重跑历史脚本。充电UI主体已覆盖，不能用旧remaining凑题。

## 验证、精确未知与结束

[verify_reuse.py](../../analysis/charge-reuse-gap-j01-0041-20261024/verify_reuse.py) PASS；[reuse-result.json](../../analysis/charge-reuse-gap-j01-0041-20261024/reuse-result.json)记录complete/matrix/final SIM边界、三条旧record引用、9份覆盖更新报告的定位断言、分类body元数据和锚点存在性。脚本仅读既有JSON/报告，**不读ROM、不反汇编、不执行旧验证器**；元数据或锚点存在不作为新语义证明。首版把final报告steps/screenshots数组误按标量比较，已改用step_count和截图数组长度，属于读取器纠正，未改变旧验收结论。交付JSON解析、相对链接与`git diff --check`通过。

未闭边仍按原报告限定：原硬件/云端/USB/持久化等服务替代不能升级；扩展+34/+38真实别名、主app正常退出触发、全局deinit、延后重放/采样时刻均没有本轮新增种子。J01没有作“无消费者/死字段/缺陷”结论，也没有把整个充电或ROM宣告完成。一个后续闭包仅为上表cmd51分类合同认证；无必要增量时直接报告已覆盖，由主窗口最终决定派发，本agent不自行接题。
