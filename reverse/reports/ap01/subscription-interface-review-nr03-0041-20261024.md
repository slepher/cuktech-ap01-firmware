# NR03：N03 应用订阅接口合并非作者复核

**可独立使用阶段已闭合但接口未闭；N03 差集限定接受，无语义纠正。** 注册→同步通知→屏保/详情 DELETE 摘链可作为重建的接入阶段合同；原主 W 正常退出/目标注销、订阅 node 最终回收、在途 callback 排空仍未闭。新实现的 close/串行化/延后回收是设计选择，没有因本次验收变成 ROM 事实。

本复核挂认领 N03，复核者 `/root/nr03` 未参与作者工作。基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`；独占工作树 `.worktrees/batch-20261024-n/nr03`，只写本报告和同名 analysis。已读主树最新 reverse-design 流程、管理记录批次 N 顶部和 N03 行，未通读管理历史。作者 `/root/n03` 已停止；待核成果为主树 [N03 报告](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/subscription-interface-n03-0041-20261024.md) 及同名 analysis。

采用 reverse-engineer-anything skill，复用原件和既有静态证据，未打开/切换共享 REA、执行目标、设备、网络、SIM/QEMU、指令模型、回放或构建。没有改 ROM、生产、配置、分析器、管理表或他人成果，没有创建下级代理、提交或推送。本轮没有新增 REA Evidence ID；新增业务恢复为 0。

首次可得开始 `2026-10-24 13:28:12 UTC`；结束/墙钟见 [session.json](../../analysis/subscription-interface-review-nr03-0041-20261024/session.json)。估算约30分钟，可提前闭合即交；实际墙钟包含工具等待，不等同有效工时。无量化容量等待或中断；开头两次读取因 PowerShell 登录配置改变工作目录失败，之后显式 `login=false` 与工作目录，未写错路径。工具不提供 token，用量由父窗统计。

## 继承结论

0041 原件只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，长度 6,769,704B；身份沿既存 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射 `offset=VA-0x9ffff000`。未复制原件或重造摘要清单。

必要旧前提只按本题连接继承：

| 旧出处 | 接受的前提 | 保留边界 |
| --- | --- | --- |
| UiIFace 生命周期、模式控制、E02 | 控制 head `0x62fcb554`、独立 item head `0x62fcb530`；callback/userdata word；同步借用、通知后清 mask | 控制 mask 是半字，item mask 是 word；深层资源没有转移给消费者 |
| E05/E06 | item callback 单键注册；事件注册 ABI `(object,callback,filter,userdata)`；event+4 为 original target、event+0xc 为 descriptor userdata；摘链和 free 是不同动作 | 不重新认证通用链表/allocator；E06 厂商 lrw 语义仅继承，不把字节匹配说成上游厂商认证 |
| I03/I04 | 屏保 root R 已有真实 DELETE、timer 非零门、控制摘链与 state8 释放 | 不是 N03 新恢复；不能填主 kind1 W 的退出/注销断边 |
| E10–E13 | 导航、离页、离线、stack view 等已研究 | 不等同真正销毁 W，也不意味着订阅 node 被回收 |

复核直接审阅 E06 和 E02 的相关 ABI/对象/位宽裁定，没有重跑历史验证器、全 ROM 负搜或深入公共库。

## 本轮复核或纠正

[独立检查源码](../../analysis/subscription-interface-review-nr03-0041-20261024/verify_nr03.py) 完全新写，仅使用 Python 标准库读取 ROM 数据和 JSON，不导入或执行作者脚本。作者 `static-checks.json` 仅提供待核的 222 条旧字节锚点清单；新增窗口的指令长度、字段、符号扩展和调用目标由本轮重新拆解。结果 [independent-checks.json](../../analysis/subscription-interface-review-nr03-0041-20261024/independent-checks.json)：282项检查 PASS，222 条旧锚点与 ROM 字节一致，134B 新接线相关连续解码（112B 作者新增 + 22B 既有控制注册前缀）。这个数量不表示独立重证了222条旧指令的全部语义，也不取代下面逐项裁定。

| 接口问题 | 裁定及证据 | 限定 |
| --- | --- | --- |
| 控制/item 身份与注册 ABI | 接受。`0xa00b075e/0768` 合成 `0xa00f3952`；`0xa00b0774/077a` 合成 `0xa00f5288`；`0766/0778` 均把 s5 放 a1，调用目标分别 `0xa01b29a0`、`0xa01b28ce`。控制/item 头不能混用 | callback 是键，userdata 不是第二个查重键。控制注册 `0xa01b29e0` 只比较 a0/callback，命中 `0xa01b29ea` 直接返回；不更新 userdata。旧 append/16B 布局继承，不扩失败恢复或返回码 |
| 同一详情对象 D 安装 DELETE | 接受。`0xa00b07b4/07be` 构造 `0xa00f2f38`；`07b8` a3=0，`07ba` a2=0x29，`07c2` a0=s5，`07c4`→`0xa01ad654`。从控制注册至安装之间无写 s5 指令；中间三次事件安装亦调用同注册器 | 同 s5 依赖既有 RV32 callee-saved ABI；事件 userdata=0 不是对象 D。仅证静态安装路径，未观察安装成功或实际 DELETE 交付 |
| DELETE 过滤与对象/state 位宽 | 接受。`0xa00f2f38` word 读 event+8；`2f3a/3c` 符号扩展构成 `0xffff7fff`，`2f3e` AND，`2f44` 非0x29跳 `0xa00f2fd0`。`2f54` 从 event+4 word 取 D，`2f56` 从 D+0x10 word 取 S，`2f5a` 仅 S非零进入 `2f8c` | 这是清 bit15，不是截断成低15位；S为0走诊断/返回，不能忽略此门 |
| DELETE 两种摘链和 free 参数 | 接受。`0xa00f2f8c/90` 构造控制键 `0xa00f3952`，`2f94`→`0xa01b2966`；随后 head=`0x62fcb530`、键=`0xa00f5288`，`2fba`→`0xa0089d02`。`2fbe` a0=s2=S，`2fc0`→`0xa008ab8a`，`2fc4` word 清 D+0x10 | free 的是 S，不能据此称 free(node)、free(D) 或 free(snapshot)。item 未找到也会落入 free(S)/清字段；节点遍历厂商字语义沿 E06 |
| 同步通知、变化掩码寿命 | 接受。`0xa00a5394` 每轮 word 重读全局 snapshot 到 a1；`53ac/53b0` word 取 callback/userdata，`53b2` 间接同步调用；`53b4` 回调后重读 head offset；`539a` 对当前 a1+0xc 做 halfword 清零。item 语义沿 E02 | 无证跨回调 snapshot 恒定、深层指针持续有效、重入/增删安全或跨线程同步；callback 数值返回不作为通知确认。attach 不主动调用 callback，不能当作初始快照读取 |
| 三种 owner 的生命周期分账 | 接受。N03 正确区分 W、R、D，以及 state/timer/node/snapshot；已有屏保注销只继承。主 DELETE `0xa00ab8ec` 的 T1/state 清理不能跨套详情两键摘链 | 原 W 的 stop/注销没有被这112B接线补齐；全局 deinit、普通离页不提供该闭包 |
| 新实现寿命合同 | 接受为设计起点。显式冲突返回、UI上下文串行化、close停止未来通知、延后在途回调结束再回收、双链记录分别释放，均清楚标为新设计 | 没有实现/测试；不是精确原 ABI 返回合同，也不是原 ROM 已有 quiescence 保证 |

作者 275checks/222锚点/112B 的自查口径与材料一致；本轮不运行其脚本、不把275项当独立复核结果。没有要求作者修改，语义纠正为0。所有接受均为静态事实/继承合同及明确推断，未声称运行结果。

## 真正新增

本复核新增的是对 N03 差集合并后的独立裁定和标准库字段解码证据，新增业务连接为0。作者真正新增仍只计详情 `0xa00b0774..0xa00b07c8` 的84B接线和 `0xa00f2f38..0xa00f2f54` 的28B过滤入口，接到已有 E06 摘链/state归还事实。没有将旧屏保注销重计为新增，也没有新增完整函数导出。

静态验证还包括本报告相对引用、JSON解析、独占路径及 `git diff --check`。无构建、回放、设备或外部服务验证；未开新 REA 会话。

## 未闭精确边

1. **原主 W 真实正常 stop/退出 → 同 W/S 公共删除 → 以 `0xa00ad07e`、`0xa00adabc` 为键的控制/item 注销。** 详情 `0xa00f3952/0xa00f5288` 和屏保 `0xa00ac54e` 的链不能替代它。
2. **三类 owner 的订阅 node 摘链 → node 最终 free。** state8/S、timer、page/context、snapshot 与 node 是不同资源；本轮没有对应 node 的实际 free 实参。
3. **通知与注销/删除 → 在途 callback 归零/串行化确认。** 回调后重读 next、全局 pointer 或 mask 清零不提供这条保证。重入、回调内增删、跨线程删除仍无原厂保证。
4. **全局 deinit 的逐项嵌套资源回收，以及 T3/context 最终归还。** 保留旧报告未知，不因可选新 close 设计标完成。

有种子的后继仍只建议：取得原 W/S 的实际 stop/公共删除实参，或直接带 `0xa00ad07e` / `0xa00adabc` 的真实注销片段，再核同对象和顺序。无新种子不重复全 ROM 负搜。

可关闭 N03 本次交付的“待非作者复核”状态；不能关闭完整原接口。替代实现可使用这些合同并另行实现明确寿命责任，不能称其已移植/实机成功。独占成果未提交推送，等待父窗整合；本代理交付后停止本题。
