# N03：0041 应用订阅接入与退出接口

后续状态：已获[非作者复核限定接受](subscription-interface-review-nr03-0041-20261024.md)，阶段闭合、完整接口断边保留；以下“待复核”是原作者交付时状态。

**可独立使用阶段已闭合但接口未闭；作者交付，待非作者复核。** 已形成注册→同步通知→屏保/详情 DELETE 摘链的可用合同；主 app 的原厂注销和订阅节点最终归还仍未闭合。原 ROM 事实与下文新实现寿命合同分开，后者可作为完整重建接口的实现起点。

认领 N03；基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`；独占工作树 `.worktrees/batch-20261024-n/n03`。只写本报告和同名 analysis。估算约30分钟（参考20–40），无须凑时。首次可得开始时间 `2026-10-24 13:16:41 UTC`；结束及实际墙钟见[会话记录](../../analysis/subscription-interface-n03-0041-20261024/session.json)。父窗通知存在模型容量等待，但该段起止未向本代理提供，不能量化或算作有效工时；中途未切题。工具未提供 token 用量，本代理记不可得，由父窗实测统计。墙钟不等于有效工作时长。

使用 reverse-engineer-anything skill；主树最新 reverse-design、管理顶部批次N和N03认领行只读。未创建下级代理、切换共享 REA、执行固件/模型/设备/网络/SIM/QEMU/历史回放/构建，未改生产/ROM/配置/分析器，未提交或推送。

## 继承结论

原件为主仓 `roms/0041/ap01-1.0.2_0041.bin`，身份沿已有记录 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，`file_offset=VA-0x9ffff000`。未另造哈希/原件副本。主仓前缀统一为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/`。

| 已有出处 | 已有行为与本题继承 | 不可外推的边界 |
| --- | --- | --- |
| [UiIFace 生命周期](uiiface-lifecycle-0041-20261023.md)、[模式控制](mode-control-0041-20261023.md) | 控制头 `0x62fcb554`、注册/摘链、三个业务注册键；同步分发与掩码清零 | 旧“未找到 remove caller”只是当时直接边，不否认较晚 DELETE 证据 |
| [E01](uiiface-item-ownership-e01-0041-20261023.md)/[E02](uiiface-ownership-review-e02-0041-20261023.md) | item 头 `0x62fcb530` 与控制头不同；item 及嵌套缓冲区由生产侧持有，消费者借用 | 不将 item 转换、全局 deinit 或节点归还混为一个所有权闭包 |
| [E05](ctk-app-close-e05-0041-20261023.md)/[E06](ctk-app-close-review-e06-0041-20261023.md) | 主 W、state8、T1/T3/class timer 身份；主 DELETE `0xa00ab8ec` 条件释放 T1/state；另一 DELETE 的 `0xa00f3952` 控制摘链和 `0xa00f5288` item 摘链 | 主 DELETE 本体没有订阅注销；另一 callback 的注销不能跨套主 W |
| [I03](saver-time2-lifetime-i03-0041-20261024.md)/[I04](saver-time2-lifetime-review-i04-0041-20261024.md)，旧 guide 和 weather-calendar complete | 屏保 root R 的控制注册、真实 DELETE `0xa00a4edc` 及正常唤醒条件删除种子早已留存 | root state8、子页 wrapper20/ctx40 和订阅 node 是不同资源；ctx40/node 最终 free 未证 |
| [E10](main-app-root-exit-e10-0041-20261024.md)、[E11](ctk-round3-coverage-review-e11-0041-20261024.md)、[E12](ctk-snapshot-consumer-e12-0041-20261024.md)、[E13](ctk-offline-transition-e13-0041-20261024.md) | 导航保留对象、较晚 round3、stack view 及离线切回已有覆盖 | 离页、滑出、端口离线、栈归还都不能自动称作 app 销毁或注销 |

查重差集为同详情对象的两次订阅与真实 DELETE 安装接线，加上面向重建的接口整合。N01 控制请求与 N02 遥测字段转换不在本题；未重跑全 ROM 同头负搜、公共删除 caller 扫描或旧验证器。

### 原 ROM 接口合同

以下类型/伪代码为分析视图，并非原源码。函数地址均为0041。

| 入口 | 输入/行为 | 返回与所有权 |
| --- | --- | --- |
| `0xa01b29a0` | `a0=callback,a1=userdata`；按 callback 单键查重；命中直接返回且不更新旧 userdata；未命中尾追加16B node | 未恢复可用成功/失败返回 ABI；注册点未检查返回。只保存借用 userdata；不调用用户 callback、不立即补发当前快照 |
| `0xa00a536c` | 初始全局快照非零才走控制列表；对非空 callback 以 `(userdata,current_global_snapshot)` 同步调用 | 不消费 callback 数值返回；每轮重读全局快照，callback 后重读头偏移及 node.next；结束向当时全局快照 `+0xc` 写半字0 |
| `0xa01b2966` | `a0=callback`；找到首个同 callback 节点则调用 `0xa0089d02(head,node)` 摘链，未找到返回 | 本调用链不 free node、不析构 userdata、不提供已证 quiescence/取消确认码 |
| `0xa01b28ce` / `0xa00a389c` | 独立 item 头的 callback-only 注册 / `(userdata,item)` 同步通知 | 不能用控制注销器移除 item 节点；借用和分发后清 item mask 合同沿 E02/E06 |

控制 head 为 `{link_offset=8,first,last}`；node 为 `{callback@0,userdata@4,back_link@8,next@12}`，分配16B。前驱语义与厂商字沿已有局部模型合同继承；本轮不重新认证链表实现。原注册器对 append 失败后的字段写原序不改写成新增失败恢复，不作异常验证。

重建调用者可依赖：一次注册不会主动送一份初始化数据；变化掩码只在同步通知内有效；UI 如需延后使用，应在回调内复制所需数值。不能依赖：跨回调快照指针恒定、深层指针持久有效、取消时立即销毁 userdata、回调内增删/重入安全、线程同步或原厂节点最终回收。deinit 的离线通知和快照释放不自动清订阅表。

## 本轮复核或纠正

本轮对旧证据重读均记复核，不冒称新增函数。注册、分发、两种删除身份、旧 GNU 行与当前 ROM 稀疏比对见 [static-checks.json](../../analysis/subscription-interface-n03-0041-20261024/static-checks.json) 的 `retained_anchors`；每行保留主仓来源和 JSON pointer。

| 对象 | 注册与通知 | DELETE / 离页事实 | 资源边界 |
| --- | --- | --- | --- |
| 主 app W | `0xa005d134/138` 注册 `(0xa00ad07e,W)`；邻接 `0xa005d146/14a` 注册 item `(0xa00adabc,W)` | E05/E06 的 `0xa00ab8ec` 只在 state8/T1 非空门下删 T1、free state8、清 W+10；没有本体注销边。E10 未取得正常上层退出同 W/S 的实参种子 | 原控制/item 节点移除、T3及最终回收未知；不把普通浏览等同退出 |
| 屏保 root R | `0xa00a79ce/79d2` 注册 `(0xa00ac54e,R)`；timer callback 另借 R | 旧 `0xa00a7a14/7a18` 安装 `0xa00a4edc`/0x29，event userdata=timer。DELETE 匹配且 R+10 state8、event+0xc timer 均非零才：`4f50`删 timer → `4f54..60`按 `0xa00ac54e`摘控制节点 → `4f64/66`free state8 → `4f6e`清 R+10 | I03 早有该链；不是本轮首次恢复。node没有被本路径 free；state为空或timer为空时不执行这组清理 |
| 详情对象 D | 同 s5 作为控制/item 两节点 userdata；新接线见下一节 | DELETE `0xa00f2f38` 接受归一 bit15 后的0x29；event+4=D、D+10=S。S非零才按控制键摘链→按 item 键摘链→free S→清 D+10；S为0走原诊断返回 | free实参为保存的S，不是 node、D或snapshot；S尺寸/分配根本题不认证 |

无需推翻 E05/E06/I03；纠正的是早期“页面销毁未知”和“无 remove direct caller”被误读成全历史未覆盖的可能性。屏保 kind10 正常唤醒条件删除沿 I03/I04；主 kind1 W 的真正退出不能借它补齐。

## 真正新增

新增是**详情同对象注册→真实 DELETE 的接线精度**，没有新增完整函数导出、完整退出保证或原厂节点归还结论。两短窗共112B：`[0xa00b0774,0xa00b07c8)` 84B、`[0xa00f2f38,0xa00f2f54)` 28B；后接既有 E06 指令，无新 callee 展开。原指令及文件偏移见 `static-checks.json#/new_glue_windows`。

| 原位置/必要字节 | 接线事实 |
| --- | --- |
| 已有 `0xa00b075e/0768`，`0766:d685`，`076c/0770` | a0=`0xa00f3952`，a1=s5，AUIPC/JALR→`0xa01b29a0` |
| 新 `0xa00b0774:37550fa0`、`0778:d685`、`077a:13058528`、`077e/0782` | a0=`0xa00f5288`，a1仍为同 s5，AUIPC/JALR→`0xa01b28ce` |
| 新 `0xa00b07b4:b7350fa0`、`07be:938585f3` | a1=`0xa00f2f38` |
| 新 `0xa00b07b8:8146`、`07ba:13069002`、`07c2:5685`、`07c4:efc01f69` | a3=0、a2=0x29、a0=同 s5，JAL→`0xa01ad654`；是同对象事件安装，非另一个 weather 创建者 |
| 新 `0xa00f2f38..44` | 读event+8、AND `0xffff7fff`、比较0x29，不匹配跳 `0xa00f2fd0` 返回；匹配后接旧 `2f54` 的 event+4→D |
| 已有 `0xa00f2f8c/90/94`、`2fa4/a8`、`2fba`、`2fbe/c0/c4` | 注销控制键=`0xa00f3952`；item比较键=`0xa00f5288`；item摘链后 a0=s2=S 调free，再清D+10 |

注册到事件安装之间没有改写 s5 的指令；因此两个节点 userdata 与安装事件的对象相同。根据既有事件交付 ABI，original target 通过 event+4 给 DELETE，事件 userdata=0 不应被误当 D。静态安装尝试不等于实际运行交付成功；本题未恢复哪个业务动作触发该详情对象的公共删除，也不将完整大导航函数纳入证明。

### 新实现的明确寿命合同（设计选择，不是 ROM 观测）

保持上层兼容所需的 callback 单键、尾追加通知顺序和同步借用，采用普通容器即可，无需复制厂商通用链表/分配器。以下为接口设计而非已实现代码：

```text
attach(cb, owner) -> added | already_attached | owner_conflict | no_memory
notify(snapshot) -> synchronously visit currently attached callbacks in order
close(owner) -> stop future delivery; settle in-flight callbacks; reclaim records
```

1. 每个 callback 同时只有一个 owner。重复同对登记幂等；同 callback 不同 owner 返回 owner_conflict。原 ROM 对后者静默保留旧 userdata；新增显式错误属于重建选择。原始二进制互操作如须精确兼容，不能把这个扩展返回码冒充原 ABI。
2. owner 持有自己的注册记录；快照/item 由生产侧持有，callback 只在本次同步调用内借用。attach 不补发；需要初始显示的页面另做明确读取并复制数值。失败不建立注册、不转移 owner 所有权。
3. 所有 attach/notify/close 在一个 UI 执行上下文串行处理；close先撤销未来通知资格，再等待该 owner 的在途 callback 归零，归还两个链的记录，最后归还 timer/state/page/owner。回调中请求 close 仅标记并延后到本轮 notify 返回后完成；在清理完成前不复用 callback 给新 owner。
4. 以一个 owner 关联控制/item 两条订阅，close 同时解除两条；重复 close 无动作。节点回收与 userdata 回收分别负责，不能只靠通用对象递归 free，也不能把原 ROM 的只摘链直接当作已经回收节点。

这给出可独立采用的完整替代寿命责任；没有执行、实现或测试该设计，不宣称已移植/实机成功。它不依赖找到原 ROM allocator 或通用列表的精确上游版本。

## 未闭精确边

- 原主 W 的 `0xa00ad07e` 控制节点、`0xa00adabc` item 节点：真实正常退出触发→同 W/S 公共删除→目标注销仍无实参种子。E10 的 loop返回/显示删除仅为条件链，不重开无种子全局搜索。
- 三应用各订阅 node 的最终 free；控制注销本体、详情 item 摘链以及屏保 state free 均不能补齐它。userdata/state/page/snapshot/node 不同对象必须分账。
- 回调增删/重入、全局快照替换、跨线程通知/DELETE的串行化及在途排空仍无原厂保证；新实现采用上述明确寿命合同，不把它描述成 ROM 已有行为。
- 全局 deinit 的嵌套逐项回收与T3/context最终归还沿原报告未知，N03不扩字段转换/公共库。

后续只建议有种子的一项：取得**原主 W/S 的实际 stop/公共删除实参，或直接以 `0xa00ad07e` / `0xa00adabc` 为键的真实注销调用片段**后，再核该对象身份与清理次序；没有种子不重复全 ROM负搜。若要求原厂退出/回收完整闭合，所需增量时间当前不可可靠估算；仅对既有112B接线与替代合同的非作者复核可估约10–15分钟。

### 实际静态验证

[verify.py](../../analysis/subscription-interface-n03-0041-20261024/verify.py) 本轮新写并运行，结果PASS：275项检查，222条旧指令锚点与ROM原字节匹配，112B新增短窗连续标准RV32/RVC解码；原编码独立拆解 callback常量、AUIPC/JALR及JAL目标、同s5实参、DELETE filter与free(state)实参。新短窗无custom0；E06的厂商lrw字段与语义只继承其来源，不伪装成本轮独立厂商认证。初次核验遇E06厂商行无assembly键，改为显式保留vendor/fields后通过，未改任何原证据/模型。

另检查JSON解析、报告相对链接、独占路径和 `git diff --check`。作者静态自查不代替非作者技术复核；没有新增 REA Evidence ID。所有成果留独占树，无提交推送。
