# P-16/P-17：端口控制身份与普通响应合并非作者复核

**可独立使用阶段已闭合但接口未闭。P-16/P-17差集限定接受；无行为纠正，无作者返工。** 四个正常详情入口将两种请求选择域连接到同一数组项；反馈仍按 descriptor selector 过滤。普通 cmd63/65 的应答只是清传输状态并同步复制共享1B后返回，不能据此认定底座执行成功。

复核者 `/root/dock_control_review_01`，未参与两份作者成果。管理登记为 [23:44小节](rolling-management-0041-20261023.md:254)及P-16/P-17原行；HEAD实查 `5bbc331ab429fb76e956e50b8081c56f8d278b11`。本轮主树独占新报告及同名 analysis，不创建工作树、不改共享表或作者文件。采用 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存优先、有界静态复核。已读 reverse-design 3.1/3.2/5.1/7；不打开共享REA、不运行/导入作者验证器、不执行目标、指令模型、SIM、构建、设备或网络，不改ROM/生产/配置/分析器，不提交推送、不派下级。

预估6–10分钟：定位1–2、原字/接口3–5、交付2–3；以P17约6分钟、PR14约6分钟作类比，定位充分可提前交付。开始UTC `2026-10-24 15:45:16`，结束/实际墙钟见文末。token由父窗本轮快照统计；本子任务不能直接取得可归属input/cached input/output/reasoning，均不估算。

## 继承结论

- [PR14](port-control-review-pr14-0041-20261024.md) 已接受的请求setter、cmd63门、cmd65 len2及同步提交ABI、UI立即呈现、callback页面/mask门与借用寿命均直接继承，不重验setter。PR14保留的S+4/S+7身份桥与旧5350类型提取精度，恰是本轮P16差集。
- P17所依赖的B19/B21正常CRC/state2/活动cmd门、parser当前handler重读与第二次0x24、N01/NR01同步copy语义、PR02/P10独立cmd50遥测均沿作者列明的已验合同；不重新展开parser、队列、copy库或MCU。
- 原件沿CATALOG：`roms/0041/ap01-1.0.2_0041.bin`，长度实查6,769,704B，SHA256继承 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；RV32 little-endian，offset=VA−0x9ffff000。未重算整件hash。

## 本轮复核或纠正

作者报告 [P16](port-selector-p16-0041-20261024.md)、[P17](port-response-p17-0041-20261024.md) 与两份interface.json只作定位和受审合同；独立源码 [review_static.py](../../analysis/dock-control-review-01-0041-20261024/review_static.py) 从ROM读取原字，另读原留存指令，未引用作者验证逻辑。

来源分账：handler从 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json` 按Evidence `ev_6044e70f4a6f785a665e891cedb82fc897de52716642b9e9bbe0538f9b9d4c40` 选完整record，thead2/profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。callback/getter直接读 `reverse/rehost/charge-complete-0041.json#/records/19`、`/records/7`，Evidence分别 `ev_709b5ff51cf4fb33e1b9ae866819ac7a860e0ffe029c2c56c7e9344ac037af88`、`ev_e3f2aa4487640b81304640105603339b7213c4200fb9cd41dd4ee2535cae0480`，旧profile未知。initializer直接读 lifecycle retained-initializer的function。dispatcher分别读 buzzer-backlight 的functions[5]、uart-response 的functions[0]：同Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`、thead3/profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`。不把这些profile互贴；helper仅继承NR01已验离线body。

| 验收项 | 结果与边界 |
| --- | --- |
| 同W/S与四入口 | 接受。61e6..61fc取同W+0x10为S；6bf8..6c40/6cc4分派根选择18/19/1a/1b。补看各目标至getter前的28B日志接缝：没有S选择改写，callee按既有ABI保留s寄存器。四处getter参数k=1..4、call3b36、S+4保存s5与S+7写k逐一吻合。 |
| 两种请求及getter同项 | 接受。3b44减1、3b48 AND255、3b50 call53c0；四入口得到数组索引0..3。safe/switch开页必要窗保持S+4/+7；和PR14请求公式合接，证明这四个正常入口的同源请求。safe算术域的第五值1c不能增加已证入口。 |
| 5350类型提取 | 接受有限解释。ROM原word 1447b70b：opcode0b/funct3=3/rd14/rs1=15/thlsb=4/thmsb=5；5340为1447b78b，rd15。独立核本地reg.sinc的thlsb=(20,25)、thmsb=(26,31)，及thead2.sinc精确extu5,4构造的左26/逻辑右30语义，得到(a5>>4)&3。旧custom0/extraout不能被直接当作tp输入。这里只认证原字段与本地参考一致，不认证模型原厂来源，也未执行/修复模型。 |
| descriptor selector与数组序号 | 接受。标准5356..5370为type1→4、type2→5、type0且低nibble≤2→nibble+1，其余0；5b0a/5b6c两个过滤均读S+7。8aca..8b26将描述byte的bit6、低4位、bit4..5写I+24，同时另写I+13序号。两字段来源分离，原过滤没有I+13比较，不能推出selector恒等数组序号+1。 |
| P16接入策略与事实分开 | 接受。callback内复制I+13、descriptor、mask和遥测标量，应用新增双身份比较只产生“同项观测”；该比较及跨代策略属于重建设计，不是原ROM已有请求确认。 |
| 63/65普通路由 | 接受。85bc、8742/874a、8794..87a4将两cmd送共享61..68分支；9cbc设a0=62fcb50d、a1=1，a2仍为原payload，AUIPC/JALR实际目标1ad024。不是&view，不复制请求index/value。正常合同要求首byte可读。 |
| 清state、copy、返回 | 接受。helper d036原word 2e070823是SB zero到62fcb2f0，先于copy；copy语义继承NR01。9cd2只令cmd62走后继，63/65从9cd6直达85e4公共返回。没有沿该分支解释值、立即query、变更事件或UiIFace通知。该负结论限确定分支，不是全ROM负搜。 |
| 共享byte与0x24 | 接受。1B缓存不保存请求身份/索引/年龄；产品语义及reader未知。另一次parser通知重读handler且不携带63/65结果，ordinary的8856..886e又受OTA门，不能当本次控制成功或专属查询。后续cmd50遥测的年龄/因果仍未知。 |
| 所有权/失败/取消 | 接受未闭边界。请求、应答源和callback项按继承合同同步借用；标量应在有效期内复制。没有新分配/free，不能借本轮补出请求接纳、业务失败回滚、超时、取消或关闭后迟到隔离。 |

本轮没有作者行为纠正。复核脚本自身曾因uart留存assembly嵌在normalized_result而停止，以及初写类型字段错取bit25而失败；检查对应原结构/reg.sinc后修正，再完整PASS。这两项不是作者错误，未用失败检查输出作结论。

## 真正新增

新增业务恢复0。本轮独立接受两份作者差集，未开展后继。最终393项静态断言PASS：23精确窗866B逐指令边界/ROM核对，P16对原assembly，P17对两份dispatcher原assembly与原raw_ranges；另补四个28B接缝112B及实际日志call目标。总原字范围978B；计数不代表语义覆盖率。关键字段另独立解四个getter常量/JAL、八处S存储、两处厂商类型字段、应答路由B/J目标、helper目标与state SB。

原字、来源ID、检查标签和接缝留存见 [review-evidence.json](../../analysis/dock-control-review-01-0041-20261024/review-evidence.json)。来源留存未供应的profile仍未知，原dispatcher整体bad-instruction/边界警告未消除，不认证完整6044B body或完整callback CFG。

## 未闭精确边

1. 真实cmd55描述表 `desc[i+0x17] → I+0x24 → selector` 是否恒等于数组序号+1；下一有种子动作仅可沿8ad0/8aea/8b02及已留上游传表合同查实际条目顺序。第五入口、物理/远端内部端口映射仍未知。
2. `0x62fcb50d` 首byte产品意义及真实reader/对外暴露；后继仅从已有精确xref找消费方，不因本轮没查reader而判全局不可见。
3. 提交接纳、底座应用/持久化、遥测年龄/因果、跨快照代际、并发取消/关闭后迟到应用均未闭。两段可用阶段已验，不改写为完整端口控制接口已闭。

交付仅本报告、review_static.py、review-evidence.json三文件；JSON按既有规则ignored并留原路径。JSON解析、三文件尾换行/尾空白、7个本地引用及限定路径git diff --check通过；状态仅两份未跟踪源码/报告及ignored证据，未修改作者/共享文件，无提交推送。

UTC结束采时 `2026-10-24 15:49:40`，自开始采时墙钟264秒（4分24秒）；因留存完整且未见争议而提前收敛，未凑估时。无主动等待、排队或任务中断；shell/静态读取及工具往返包含于墙钟，未独立测得有效工时或工具等待总量，不据返回片段估算。一次默认GBK读取错误改为显式UTF-8；一次错误根部reverse-design路径随后定位到reports/ap01，无写入影响。token由父窗本轮快照实测统计，本子任务直接可归属计数不可用。
