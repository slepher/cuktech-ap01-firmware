# E10：主 app 根退出的成果复用与有界断边

2026-10-24；分支 `codex/re-0041-e10`，研究基线 `bccdd65`。使用 reverse-engineer-anything 技能；仅静态读取主仓原 ROM 和已有成果。成果待独立技术复核。

**现存材料已覆盖普通浏览、宿主主动销毁及显示退出后的条件删除路径；尚不能把其中任何一个写成原 ROM 某个正常业务动作必然删除真实主 app。新增退出闭包为 0。** 本题收缩为对象来源接入复核和旧证据边界归一，不继续扫描所有 UI 删除者。

## 已有成果 → 实际缺口

| 既有出处 | 已经解释的行为 | 证据类型与局限 | 本轮处理 |
| --- | --- | --- | --- |
| [E05](ctk-app-close-e05-0041-20261023.md)、[E06](ctk-app-close-review-e06-0041-20261023.md)；E05 retained `ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866` | `a005cd68` 取 parent，经栈保存/重读传入 `a00b2f6c`，返回主 W 保存 s4；parent child array 保存 W；主 DELETE `a00ab8ec` 与递归删除原序 | 已有原字节和独立复核；没有实际正常退出触发者 | 完全继承 W、state8、G 和 DELETE 身份，只补 parent getter 的短接入身份；不重做 DELETE、注销键或同头搜索 |
| [多应用宿主](multi-screen-app-host-0041.md) §3、[append](screen-host-append-validation-20261020.md)、[H07](weather1-navigation-h07-0041-20261023.md) | 主 W 内保留九页，更新 active/prev、x 与动画；普通旋钮切出保留对象 | 旧原汇编、受限历史执行及设计历史混合；早期 obj_del 名称已被后续纠正 | 继承导航，不将滑出当删除，不重新运行历史检查 |
| [宿主 lifecycle](screen-host-lifecycle-20261020.md) §结论/实际验证、[接口](screen-host-interface-0041.md) §1/2；`screen-host-delete-abi-20261020.json` | `a00ded6c` 才是公共删除；后加宿主可销毁/重建原厂九页；宿主额外按函数与窗口解绑订阅 | 原件删除器静态证据可继承；销毁触发来自后加 UI 探针，额外解绑来自重建实现。不能认证原 ROM 原有退出动作或 `a00adabc` 注销 | 只读并明确来源；不把候选探针/补充策略画进原 ROM 调用图 |
| 主仓 `reverse/rehost/guide-complete-0041.json#/numeric_state_audit/evidence/0`、`#/saver/wake`；ZIP `tools/ap01/ap01-ui.h:651` | mode3 醒来路径 `a00a75e6` 查 kind1 W、pause W+58、调用 `a00b2d6a`；旧 SIM 注释已解释选择 Power0、Time3 或 Settings6。其他分支查 kind10 并删除该对象 | 旧 GNU 原汇编已经存在；ZIP 为重建语义，不能证明原 ABI。不能因同函数出现公共删除而把 kind10 对象换成主 kind1 W | 继承旧分支分类；只核实际 a1=10 与 callsite，核 `a00b2d6a→a019d422` 是滑动选择 |
| `system-complete-0041.json#/cached_evidence/main_a00afc88`、`#/integration/object_lifetime`、`#/reconstruction_boundaries`；`guide-complete...#/hooks` | 主导航旧反编译；SIM 服务不直接删除对象，parent clean/reset/redraw 等重建接口 | 旧反编译含省略参数；SIM factory_reset、restartpureUI、root clean 不是 ROM 正常 root 删除 ABI | 不将模拟服务/安全替代或重建 reset 当原 ROM 触发证据 |
| [F03](miio-loop-close-f03-0041-20261023.md)、[F04](miio-loop-close-review-f04-0041-20261023.md)、[F05](miio-exit-callback-f05-0041-20261023.md)、[F06](display-exit-review-f06-0041-20261023.md) | `a005cec6` 调 loop 容器；返回后 `ceca` 重读 out 显示再调用 `a0081554`；显示删除器经屏幕数组调用公共删除，再按已有对象树合同递归孩子 | 已有原字节及复核；只证明“容器返回后”的条件路径，没有正常业务动作使容器返回，也未证明执行期间所有显示/parent 别名不变 | 直接引用，不新增记账为另一条显示恢复；只核数组删除实参接点 |
| 主仓 `photo-evidence-round3.json#/rea_records/3`、`main-knob-0041-round2.json#/records/1` | 较晚 round3 已留主导航反编译，round2 已有具体 `a00b053e/a00b0576` 删除指令及创建详情窗口的导航 | 部分旧反编译缺实参；不能把临时详情 W 与初始主 W 合并。H03/H04 已证 type19 临时 W 返回删除 | 先检查较晚材料，不将旧 round2 remaining 判成新缺口；不重追已解释详情删除 |

旧 final report/matrix 的 passed-in-sim 仅为重建验收；本题没有重跑验收，也不把它提升为原 ROM 生命周期/来源完整恢复。最终 ZIP 只读成员，没有执行脚本、全量解包或复制。按地址检索未命中只表示本次检索边界，不能宣布此前未分析。

## 继承的旧结论

真实主 app W 是 `a005cd7c→a00b2f6c(parent)` 的返回值，`cd80` 写 s4；不是 `62fc95bc` 保存的独立输入/组句柄 G。W 的 class/parent 持有、item 注册、真实 DELETE 和 state/timer 清理都沿用 E05/E06。H07 的普通浏览覆盖结论保持：weather1 type4 页面是 W 的孩子，切出通过滑动保留对象；type19 详情窗口另有临时 W 和独立 DELETE，不能套到主 W。

F05/F06 已经解释 `a0081554` 的显示对象身份与删除路径。其 `a008163a` 从 display+2bc 取屏幕指针数组，`163e` 取首屏，`1640→a00ded6c`，再回到 `15c2` 重读 display+2d8 的计数。此是已有原字节，不是 E10 新发现。它给出了一个**显示删除发生时**的父树清理候选连接，不能给出原业务触发者。

宿主 lifecycle 中真正的“两轮删除/重建成功”也保留其原证据价值，但这属于后加候选的 UI 探针动作。报告明确记录专用 probe 和额外解绑策略。它不证明 ROM 日常操作原有这一行为，也不能填 E05 item 节点注销的断边。

## 本轮复核或纠正

[验证器](../../analysis/main-app-root-exit-e10-0041-20261024/verify.py) 只读原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA-0x9ffff000`。[局部结果](../../analysis/main-app-root-exit-e10-0041-20261024/bounded-recheck.json) 保留 10 个短接入窗口、52 条指令、27 项 raw/JAL 核对。全部标记为“旧结论复核”；没有重新整函数导出，没有全 ROM incoming 扫描，没有新 REA Evidence ID 或共享数据库变动。

1. **parent 的来源限于创建时读取的 active screen。** `a0081856:b797fc62` 与 `185a:03a50759` 读取默认 display `62fc9590`，`185e→a0080eba(display)`。后者非空分支 `80ec6` 到 `80f00:83a4842c`，读取 display+2c8；返回 join `80ef8:2685` 把该值送 a0。显示为空时重读默认显示，仍空则进入日志并走返回，不臆造有效屏幕。由旧 E05 的 `cd6c` 栈保存、`cd78` 重读和 `cd7c` 调用，可画成“创建时默认 display 的 active screen S→child W”。这不证明此后默认显示/active screen 和 out 槽永不改变，也不是从 G 推导 parent。
2. **guide 唤醒候选没有填退出边。** 旧 `a00a7642` 取 W+58 timer，`7648→a00b2d6a`。该函数 `b2dc4/b2dce/b2dd6` 产生 idx0/3/6，再 `b2dd8→a019d422(W,idx)`。retained dossier `ev_c89e4c5e84551bcc9753baab7724d1a0e8f6763e8686ce25aa38b63493780907`、`ev_e7bd3e426378c573fd751364a9c83bf470389ad186beb9c23f1d7faa89b4acec` 已保存旧实现。原字 `a019d4b4:23aa2403` 写 active@34，`d4b8:9cdc` 写旧 active 到 prev@38，`d4ba:23860404` 清 busy@4c；其后按既有 slider 回调作动画。这里只选择子页，不建立 W 删除。另一路 `a00a7660:a945` 明确 kind=10，`7668` 取该匹配对象，`7694→a00ded6c`；它不是 kind1 主 W。
3. **显示删除的数组接点复核保持条件措辞。** `163a/163e/1640` 的数组→首屏→公共删除目标与 F05 原证相符。结合创建时 parent 和 E05 递归合同，仅可说：若同一显示仍保存对应 S 且正常删除继续，删除 S 可递归到 W。没有证明应用已经退出、运行时送达成功或 item/context 全部回收。

没有推翻 E05/E06/H07 的技术结论；本轮纠正的是潜在的来源混用：host probe、SIM reset、主浏览选择、type19 临时页删除，都不能充当原厂主 W 的实际正常退出。

## 本轮真正新增

**新增正常退出闭包 0，新增业务恢复 0，新认证开源排除 0。** 本轮只是把已有 host、guide、display 合同接到同一个 W/S 身份对照，核少量接入原字，并排除已有候选被误记成新 root teardown。parent getter 接入精度不计另一份主 app 功能恢复。既存 Evidence/报告保留，不重置进度。

未重建分类表/资源、未解码 PNG、未复制全源码、未增加机械哈希清单；未改生产、ROM、配置、分析器模型或他人成果。未启动 SIM、构建、历史回放、设备或网络。

## 仍未闭合的精确边

缺口仍为：**某个原厂正常上层业务动作 → 使原主 W 或其创建时 parent S 被送到公共删除的实际 caller/实参身份**。loop 返回后的显示清理是现成条件路径，但“何种原厂业务动作使 `a005a736` 返回、返回前是否保持同一显示/S/W”尚未建立。未由此推断 W 常驻、永不销毁或任何缺陷。

retained whole-ROM inventory `whole-rom-coverage-0041-20261023-round1.json` 的 direct-call 索引包含公共删除的 24 个 caller 身份；它不是对象别名证明，也不覆盖未解析间接边。本轮没有为追数量逐一扩所有 UI，也没有重跑 E05 同头负搜索。尚未检索到精确业务种子不能等于不存在退出路径。E05 的 `a00adabc` 节点最终注销/归还、T3 及各页 context 的独立断边仍保持，不能借显示递归删除合同补齐。

后继只在取得 **真实 loop-stop/return 或主 W/S 删除实参种子** 后继续此题，届时复用已有 DELETE/显示/导航合同，只核触发调用的对象身份和门。没有这个种子时不应重复派 root 退出搜索，可由管理者换到其他已定位缺口。

## 实际静态验证

运行 `python -X utf8 -B reverse/analysis/main-app-root-exit-e10-0041-20261024/verify.py`：27 项检查、10 个连续短窗、52 条指令通过。7 个直接 JAL 由原编码独立取位并归一目标；Capstone 显示的 branch operand 是相对位移，结果明确提示，不把它当绝对地址。选定窗口没有 UNKNOWN/custom0；没有因旧反编译缺参数或 no-return 作全函数判断。

原 ROM 来源沿用 E05/F05 已有身份，不重新哈希或复制。报告本地链接/JSON 可解析与 `git diff --check` 均检查；仅提交 E10 独占报告及 analysis。恢复程度为有界复用与精确未闭边，不标完整退出恢复。
