# Q-07 MiIO 默认正常 hook、规则与节点寿命

状态：作者静态交付，待非作者复核。已恢复可独立采用的“默认 hook 调用→正常规则判断→handler 或回复”和同 P 的 add/delete 节点阶段；不宣称完整 MiIO 接口或运行时全生命周期闭合。

认领 Q-07；作者 `/root/app_miio_research_02`；分支 `codex/app-miio-research-02-20261025`，启动基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`。依据主树 reverse-design 3.1/3.2/5.1/7 与 rolling-management 顶部、本轮 S 补注及 Q-07。主树资料只读；未切共享 REA、未新开 provider、未派下级；未执行固件、模型、SIM、QEMU、回放、构建、设备或外网，未改 ROM/生产/配置/分析器。

## 已有出处与真实差集

原件沿用 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B（本次实核长度），既验 SHA-256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，没有重算摘要。ROM 定点文件偏移为 VA−0x9ffff000；低 RAM 必须另用启动映射。

继承 Q-04 作者/独立复核与 upper-routing：M+0x174 的 OTU context+0x28 指向 P=0x62fc4944；OTS 对应槽为 NULL。安装 self-link P+0/+4，并按需设 add/delete 槽+0x10/+0x14；普通 dispatcher 在 0xa012172e 经 P+0xc 以六实参 `(P, descriptor, origin_u8, request+4, replycb, context)` 调用。a6 是间接目标，不是第七业务参数；dispatcher 后续自身返回 0。upper-complete records248/272 及 Evidence `ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a` / `ev_d7381a8523524525f03bf4e08e0ea5380a9ff1fc4e0b4814db227954884a818c` 仍属旧 profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。

本次改变输入：已验启动 ROM→RAM copy 能为 Q-04 未知槽给出静态初值。父窗已定位的 `policy-initializer-seed.json`、本任务同名主树 analysis 内 `hook-static-window.json`、两份 add/delete retained 和 index-selection 是继承材料，不称为本次新导出。旧 `upper-miio-b.md` 已有 add/delete 语义卡，本次只把它们与实际默认 P 及 hook 消费连起来，复核必要原字，不冒称新发现两函数。

## 初值映射复核

`buzzer-backlight-round2-0041-20261023.md` 已核启动 `0xa0029d2e..0xa0029d46` 及循环 `0xa0029e40..0xa0029e48`：ROM `[0xa00027d4,0xa0005124)` → RAM `[0x62fc2cc0,0x62fc5610)`。本次原字复核起止寄存器构造，并保存循环原字；循环厂商字 `0x5847460b/0x5847d60b` 沿用既验 post-increment 4 的 load/store 模型，Capstone 自身不能解释这两个字，没有改模型或把它们跳过当普通指令。

P 落在此区间，`0xa00027d4 + (0x62fc4944−0x62fc2cc0) = 0xa0004458`。原件24 B为 `0000000000000000b88525a00a8611a00000000000000000`，六个 u32 LE 为 `0, 0, 0xa02585b8, 0xa011860a, 0, 0`；+8 字符串是 `OTU`，+0xc 初值是 hook 入口。该证据只证明 copy 初始化映像，不证明运行时 hook 从未替换；本次不重跑 writer 负搜。

## 默认 hook 正常合同

原件 `0xa011860a..0xa0118711` 完整连续264 B，98条基础/压缩指令；与父窗现存窗口每条 raw 独立逐字节相同。没有厂商未知字或未解释跳出。入口把 a0..a5 分别存为 P、descriptor、origin、request view、reply callback、context；本体不读取第七实参。

| 阶段 | 可重建行为与锚点 |
| --- | --- |
| 来源条件 | `0xa0118654` 以 lbu 读 descriptor+0x10，`0xa011865a..62` 检查 `((origin_u8 | descriptor_flags_u8) & 3) == 3`。不把该 OR 改写为双方都必须含同一位；其余位在此条件中不参与。这里仅恢复正常规则，不做绕过/异常实验。 |
| 规则查找 | 条件满足后在 `0xa01186b4` 取 P.next；到达 P sentinel 才允许执行。逐节点以 `strcmp(node+8, *(char **)(descriptor+4))` 比较完整方法名：`0xa01186ec..f4`，非零走 `0xa011870c` 的 next。首个相等即走共同不可用回复。 |
| 允许执行 | `0xa01186c2` 读 descriptor+8 handler；`0xa01186c4..ca` 调用 `handler(request+4, replycb, context)`。handler 返回值被忽略，hook 在 `0xa01186cc` 明确返回 0；hook 不额外发送成功回复。handler 自行回复/异步持有的合同属于具体 handler。 |
| 不可用回复 | 来源条件不满足或规则名命中，均在 `0xa0118680..94` 调 `0xa0110c76(request+4, -30020, "service not available.", replycb, context)`，随后固定返回 -1。reply helper 返回值被忽略；不能把 hook -1 或0当成 dispatcher 返回值。 |

本体只遍历 P 节点、读 descriptor 和转交请求/callback/context，没有对这些业务对象做 retain、copy、free 或修改 hook 槽。普通路径没有本地锁，也没有对 P+0x10/+0x14 的调用；add/delete 是独立控制入口。

### 正常错误回复边界

本次必要原字窗口 `0xa0110c76..0xa0110d7d`，264 B，完整返回，未深挖 JSON 内部：

- 入参 a0..a4 是 request view、signed code、message、replycb、context。先清栈上工作区；将 request view+0/+4/+8 三个 u32 和 +0xc 的 u8 复制至栈上响应头。若该 u8 非零，直接返回 -1，不调用 callback（`0xa0110ccc..d4`）。
- 使用 `id/error/code/message` 原件字符串和传入 code/message 组织回复。可推断正常 JSON 结构为 `{"id": request_id, "error":{"code":-30020,"message":"service not available."}}`；JSON 的逐字节格式及公共 writer 扩容/错误语义在此不认证。初始化 writer 使用128 B的栈区，不能仅由此推出所有情况下 payload 永不分配。
- `0xa0110d5a` 调最终化 helper `0xa00602e6`，返回非0则返回 -1且不调用 callback；为0时 `0xa0110d64..6a` 同步调用 `replycb(stack_response_header, context)`，其返回值直接成为 helper 返回值。响应头指针借用仅至 callback 返回；需要异步保留者必须按接收端合同复制，不能持有此栈头。本次不认证最终 payload 的独立所有权。

调用方 hook 固定返回 -1，即使 helper 失败也不再尝试其它回复；不是 callback 必然发生或网络必然送达的承诺。

## 同一 P 的规则节点生命周期

安装 `0xa00650ba..e2` 的两个 default slots 与本次 P 初值一致：+0x10 默认 `0xa0121886`，+0x14 默认 `0xa011f186`；安装阶段 self-links 仍按既验前提。接口为 `(P, const char *method)`；对象+8 是日志名，节点+8 才是规则字符串，二者不混淆。

add 继承主树 retained Evidence `ev_0d6acb4558537efb6e333ea0eaa1fce1c3ce1981c5e0a01d84a5292ef29173eb`；delete 为 `ev_0069d25e97d82b1d926080b00bb63e6c0fa2cb15b6a149cf89b87c5d0e1af328`，均旧 profile4825fb58。与 `upper-miio-b.md` 旧卡 `ev_14da31b6cbdb5394b475453b38c17abfa65baa7539940cc46a1a7f1b4001f2eb` / `ev_cdb2fcc39beda665d3c6b06d64543bdae5a3bd2ee10088223d1b9b42673dd69f` 分列，不替换旧 ID。

- add 遍历 next，完整 strcmp 已存在返回0，不分配。到 P sentinel 后取 strlen，分配 len+9；分配失败返回 -1，原链不变。成功清整节点，自链，复制 len 字节至 node+8，并再次 strlen 后显式 NUL（0xa01218c0..0xa0121906）。caller 的 method 不被保存为指针；必须在本次同步调用期间保持稳定，不能把重复 strlen 优化成原程序仅取一次长度的事实。
- 插入原序 `0xa0121900..12`：令 old=P.next；old.prev=node，node.next=old，node.prev=P，P.next=node，即加到链首；返回0。节点布局 `u32 next@0, u32 prev@4, char name[]@8`，总分配 len+9，P 拥有节点副本。无单独字符串分配。
- delete 预取 next 后按名扫描；首个相等时先调用 unlink `0xa006929a`，再 free `0xa002e14e`（0xa011f1d4..dc），立即返回；无匹配不修改。接口无可用业务状态返回值，不把某个残留 a0 当成功码。
- unlink 原字 `0xa006929a..b5` 表明 `node.next.prev=node.prev; node.prev.next=node.next; node.next=node.prev=0`，随后 delete 才 free。这里仅核必要摘链；allocator 内部及 libc 不继续展开。

两入口及 hook 无本地锁、无节点引用计数；可用重建阶段须由拥有 P 的外部环境保证遍历与修改串行/互斥。原厂如何调用槽、具体启用/移除哪些方法、外部同步、manager关闭是否逐节点销毁/再次初始化时的处置，现有精确 incoming references只给安装槽，尚未闭合。不得由本阶段推出释放完整 manager 的合同，或运行时规则从未改动。

## 检查、产物与断边

本次实际静态检查：独占分支/基线；原件长度；启动原字和P初值24 B；hook98条留存指令逐字节；hook/错误helper/add/delete/unlink完整必要窗口；八窗合计916 B及六个必要字符串原字；retained JSON解析与 profile/Evidence 分离；精确输出范围、JSON解析、`git diff --check`。没有测试生产代码或独立技术验收。

跟踪产物：本报告、同名 analysis 的 `verification.json`。中间导出（ignored，留待父窗转存至主树相同相对路径）：`bounded-raw.json.tmp`、`retained-selection.json.tmp`；前者含 VA/offset/hex/Capstone 指令及字符串，后者仅继承 add/delete 必要伪码/assembly。主树早已有同stem的4份继承输入，未复制覆盖它们；目标新文件命名不冲突。首轮直接打印 retained 过大，截断输出不用作证据，后续精确选择字段。

可独立使用阶段：默认 hook 六参 ABI、规则谓词/遍历/handler交接与不可用回复路径；P 字符串规则增删与单节点所有权。新增是“低 RAM 初始化→实际 hook→规则及handler/回复”的连接和必要错误helper局部合同；add/delete 旧语义为继承核对。接口仍部分恢复，精确断边为：运行时 P+0xc 替换历史；实际 add/delete 间接调用者及其同步/配置来源；manager关闭/再次初始化对仍在链上节点的清理；具体 handler 与 replycb 的外部持有/发送完成。公共 JSON/allocator/string 内部止步，不把它们作为必须继续逆向的任务。

## 时间

预测11–20分钟，中低置信；现存窗口已完整且 add/delete 原有语义卡使真实差集缩短，提前交付，不扩扫补时。UTC开始 `2026-10-24T16:38:27Z`（首次计时；此前首轮技能读取约1秒），结束和墙钟见交付消息补注。shell等待含在墙钟，未遇外部阻塞；无新 provider 等待。token/cached本作者无独立计量，不估造。
UTC结束 `2026-10-24T16:43:41Z`；主体取证与撰写墙钟314秒（5分14秒），随后仅作提交/交付检查。shell工具等待已包含在墙钟，未独立汇总累计值；其中一次留存文件种子检索跨多次poll，非目标执行或外部阻塞。计时不等同有效CPU/人工工时。
