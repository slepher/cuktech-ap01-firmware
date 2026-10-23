# 0041 E07：CTK item+34/+38 消费者的有界定位与未解断边

本轮未定位到 `item+0x34/+0x38` 的实际页面数值读者，**没有完成新的页面消费闭包**。创建、cmd52 原位覆盖、同步通知及类型变化/失活清理仍采用 E01/E02 已验收合同。本次新增的是两条可复查的引用边界：14 个指向 item getter 的直接编码候选、3 个指向 item 注册器的候选；并区分了同偏移的其他对象，以及一个不能归入既存函数体的 getter 调用点。不能将“本范围未找到”写成“ROM 没有读者”、死字段或永久不使用。

本报告为分析命名和伪代码，不是原源码。基线 `072416762c074df3118a7b37bc6366cccae84626`，分支 `codex/re-0041-e07`，独占本报告和同名 analysis 目录。只读取主仓库 ROM/既存证据，未切全局 REA target、打开共享数据库、运行固件或历史回放、联网、连接设备、编译、修改 ROM/生产代码/配置/模型。使用 REA 技能的留存证据、原字节、事实/推断/未知分离方法。

## 问题与实际覆盖

原问题是“cmd52 生产/通知 → 新实际读者 → 数值转换/主要下游 → 借用复用清理”。本轮将第一段和所有权作为既验收合同针对核；没有把诊断日志当新页面消费，不重做 E03/E04 的 port1 栈视图或 E05/E06 root DELETE 搜索。

| 节点 | 本轮实际职责与恢复状态 |
| --- | --- |
| `a00a8582` cmd52 subtype2/6 片段 | 原位复制后实际按值日志读取、mask 发布；针对核，不恢复整个 response 容器 |
| `a00a53c0` | `(index word) → borrowed item* / NULL`；原指令针对核，新增精确调用候选索引 |
| `a00a389c` | `(index) → callback(userdata,item*)`，最后清 mask；针对核 |
| `a01b28ce` | `(callback,userdata)`；新增 3 个直接注册候选身份，非动态注册全集 |
| `a00a3c8a` | 内部诊断 callback：只把 item 普通字段转换成日志标量；完整 86 B 原指令核，非两扩展组读者 |
| `a00adabc` | E03/E04 callback；保留 item=s2，+34/+38 无已证新读者边；大函数未重新恢复 |
| `a00f5288` | 另一个 item callback；item=s1，`a00f58b8` 的 +34 基址为 panel s5，不是 item |
| `a01917d0` | `(index,value)`；完整原指令核，只读 item+24 的 bit6 决定 cmd63 提交，不读扩展字段 |
| `a00a1aa8` | 精确 getter call；没有可认证的函数归属，保留断边 |
| `a00f4740` | 已验收只读 +28/+2c/+30；不能作为这两组的消费者 |
| `a00a3d80` 尾片段 | 两组非零逐一 free 后清 word；沿 E02 针对核 |

这些是搜索/接口节点，不是“已恢复 11 函数的新完整业务闭包”。其余 getter caller 只用于限定候选范围，下表逐条列出，不扩展成页面恢复工作。

## 来源与可定位证据

ROM：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；映射基址 `9ffff000`；沿用既存 SHA-256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，未新增机械哈希清单。

既验收边界来自 [E01](uiiface-item-ownership-e01-0041-20261023.md)、[E02](uiiface-ownership-review-e02-0041-20261023.md)、[E03](ctk-view-dataflow-e03-0041-20261023.md)、[E04](ctk-view-review-e04-0041-20261023.md)、[E05](ctk-app-close-e05-0041-20261023.md)、[E06](ctk-app-close-review-e06-0041-20261023.md)。

新增 [原指令窗口](../../analysis/ctk-extra-consumers-e07-0041-20261023/instruction-evidence.json)含 17 窗口、262 条原字节/文件偏移/分支目标/厂商字段，以及三条 ROM 原字符串；[精确调用索引](../../analysis/ctk-extra-consumers-e07-0041-20261023/focused-call-index.json)保存 17 个匹配和各自 retained body 来源；[留存范围](../../analysis/ctk-extra-consumers-e07-0041-20261023/retained-search-boundary.json)保存 16 个选定 dossier 的 Evidence ID、profile digest、body、同偏移候选和 callback incoming refs，不重复复制大函数。

原件均在主仓库 `evidence/rea-0041-20261017/`：`whole-rom-private-20261023.evidence.json` 为 162 个 analyze_function record 加引用/过程清单的 bundle，不是全 ROM 每函数的完整数值流。provider 为 Ghidra 12.1.4、私有 `RISCV:LE:32:ap01thead2`；profile digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。函数边界另读 `whole-rom-graph-queue-20261023.json` 精确映射到现有 `procedure_info` 文件，未调用新分析引擎。

关键 dossier：response `ev_70c4f2e4ab81d16f68ee9e092f50824c912cdae172d69b06e93511cdc1f54e18`；内部 callback `ev_0d64ebd9da37487a253776f36efd79021421859ed0b498eda428293e008e0cec`；theme callback `ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5`；detail callback `ev_9d0ee2cee775acd425c5c8d8b5f208f878585b72f627a0865f70fcd2165002bc`。GUI、allocator、copy、log/format、协议结构准确源码版本未认证；本次新增可排除上游实现数量为 0。

## 两组已知数值读取究竟是什么

两组各 24 B，item 持有指针；以下局部布局只由响应日志支持，不补造协议单位、完整类型或电池业务解释：

| 字段 | 已核原数值读取与日志参数 | 更新 mask |
| --- | --- | --- |
| item+34 | `u16@0 → BC`，`u8@2 → BN`，`u8@3 → Type`，`u16@4/6/8/a/c → V1..V5` | `0x10000` |
| item+38 | `bits7..4(u16@2) → PB`，`bits3..0(u16@2) → PE`，`u8@3 → Type`，`u16@4/6/8/a/c → P1..P5` | `0x40000` |

原字节例：`a00a9bae:03a94a03` 是 `lw s2,0x34(s5)`；`a00a9ac8:03a98a03` 是 `lw s2,0x38(s5)`；`a00a9b0e:8bb7471c` 为 `extu a5,a5,7,4`，msb/lsb 从编码提取，不依靠省略厂商操作数的反编译文本。V/P 的五值都是 `lhu`，没有在这里做除法、缩放、符号扩展或页面 setter。格式串分别位于 `a02698a8` 的 `BC/BN/Type/V1..V5` 和 `a0269934` 的 `PB/PE/Type/P1..P5`。

```c
// 两条响应分支的局部顺序；不是原源码。
p = load32(item + (subtype==2 ? 0x34 : 0x38));
src = payload + 5;
diff = compare(p, src, 24);       // 先compare，后判NULL；保留原顺序
if (diff == 0) goto advance_query;
if (p == 0) goto advance_query;
copy(p, src, 24);                 // 不换指针，不分配
// log的实参为上表的零扩展标量；不是把p作为格式串或新持有资源
log_fields(...);
store32(item, subtype==2 ? 0x10000 : 0x40000);
notify(index);                   // a00a8730..873c -> a00a389c
advance_query: /* 原查询推进合同；非页面消费者 */;
```

这给出两个真实诊断数值消费者，但它们在生产分支内部，没有据此发现“实际页面/业务下游”。24 B 的 +0e..+17 在这些日志里没有数值读取；“拷贝24 B”不能证明全部字节都有用途。

## 注册与 getter 搜索的精确边界

[验证脚本](../../analysis/ctk-extra-consumers-e07-0041-20261023/verify.py)仅在已有代码候选区 `a0000000..a01b9800` 半字对齐位置匹配两个指定目标的 RV32 JAL 和相邻 AUIPC/JALR。它不是任意常量/全函数扫描，不产生跨函数语义。局限明确：不覆盖间接调用、非相邻取址、其他编码形式、计算出的表别名或 descriptor。每个匹配比对现有 body；恰有一个不落在 body，保留 owner=null。

3 个注册候选均由原字节/既存函数上下文核身份：

| 注册位置 | callback / userdata | 对本问题的含义 |
| --- | --- | --- |
| `a005d146` | `a00adabc / app` | E03 已连接实际通知；旧闭包消费前3组，不补充后2组 |
| `a00a8b56` | `a00a3c8a / 循环索引` | s2=`a00a4000`，a0=s2-0x376；内部 callback 只诊断普通项字段 |
| `a00b077e` | `a00f5288 / s5 app` | a0=`a00f5000+0x288`；不能由 callback 存在推断它消费任意 item 字段 |

`a00a3c8a(userdata,item)` 读 `u32 item+24` 的端口位、`u8 +e/+d` 和 `u16 +6/+4`，以标量交 `a008b51a`；然后恢复 0x20 B 栈返回。完整原指令中无嵌套指针加载、无 item 写、无 retain/free。它不是新 CTK 两组消费者。

14 个 getter 候选的结果如下。表中“普通字段”是紧随调用的既存 dossier/原字节局部读取，用来排除把这些读取误叫扩展组消费；不声称整 caller 全部副作用已恢复。

| call 位置 | 已认证 owner / 原读取线索 | 扩展字段状态 |
| --- | --- | --- |
| `a009c6a4` | `a009c662`；item+14 byte | 普通状态 |
| `a00a1aa8` | **未知 owner**；a0 在 `a00a1acc` 保存至 s0-e4，`a00a1b20` 仍读 item+a halfword | 真实函数/后续别名断边，未排除其其余路径 |
| `a00a5426` | `a00a53ee`；item+e 类型 | 查询选择 |
| `a00a862c` | `a00a8582`；cmd52 生产指针 | 已知生产/日志，非新 UI |
| `a00aca0c` | `a00ac93c`；item+a halfword 是否非零 | 普通状态 |
| `a00f3b50` | `a00f3b36`；普通数值填 view | 已存函数无 literal +34/+38 指针加载；不等于全部别名证明 |
| `a00f3ffa` | `a00f3eaa`；item+d byte | 普通在线状态 |
| `a00f41f4` | `a00f40ee`；item+a halfword | 普通开关状态 |
| `a00f476c` | `a00f4740`；+28/+2c/+30 | 前3组已验收，非本问题 |
| `a00f4d08` | `a00f4cf4`；普通项 +20/+21、+4/+6/+8/+e | 普通快照 |
| `a00f794e` | `a00f61ae`；item+c byte | 普通状态复制 |
| `a00f7df6` | `a00f61ae`；非空后 item+e byte | 普通类型 |
| `a01917f6` | `a01917d0`；item+24 byte bit6 | cmd63 控制门，见下文 |
| `a01b273c` | `a01b272c`；item+14 byte | 普通状态/命令 |

`a01917d0` 是此前所选 dossier 中缺失、此次全原指令针对核的一个入口：先要求 `load32(62fcb2d0)!=0`，再要求 word index `<u8(62fcb01c)`，借 item 非空且 `load8(item+24)&0x40` 才建立栈命令 `{u16 0x0263@0,payload*@4}`，payload 两 byte 为截断后的 index、传入 value，调 `a01951e2` 后恢复栈。无有效业务返回值认证；没有读取/拷贝/持有扩展指针。提交器对栈载荷如何复制沿原发送合同保留，不能从栈描述符推定异步保留。

## 同偏移假候选与未解函数边界

`a00f58b8: lw a1,0x34(s5)` 在 `a00f5288` 里是特别容易误接的一条边。该 callback 的 `a00f52b6:ae84` 明确将入参 item 放 **s1**；这里 s5 是由页面查找返回的 panel。a0 从同 panel+30 取，传 `a00f4f90`；它不是 `item+34` 的真实读取。不能凭地址偏移命中把它升级成 BC/V 消费。其余已存 +34/+38 指令仅按 literal 输出，脚本明确不具备 alias 证明能力。

getter call `a00a1aa8` 的此前最近过程入口是 `a00a12d0`，但 graph `whole-rom-graph-20261023-4778.json` 的 body 实际为 `a00a12d0..a00a144f`（Evidence `ev_2ecf5b8ded9c350a2da4c8206066d7cc73f0e3f9f2e80eb4fc229f111a5aeceb`）；因此脚本拒绝给该候选 owner=`a00a12d0`。原 JAL 目标和后续保存/普通 halfword 读取可核，**函数入口、完整正常 CFG、栈保存的 item 别名后续走向仍未认证**。这不是“该最近函数就是消费者”，也不据此修补 analyzer 或作异常路径调查。

## 所有权、事实与未恢复范围

正常所有权仍是：item 持有两个 24 B buffer；cmd52 原位写入；通知将 item 借给 callback；完成遍历后清先前固定 item 的 mask。回调能够取得 item 仅证明访问机会，不证明读取该两字段、建立 view、数值复制或 retain。

清理 `a00a3dd2..3dea` 先加载 +34，非零调 `a008ab8a`、返回后清 +34；再同序处理 +38。没有整组先置零。E02 已验收的类型变化/失活来路仍适用。**未知页面读者的借用结束时刻、dst 生命周期、主要转换与下游 ABI 本轮均未恢复**，不能把 item 清理替代这些缺失环节。E05/E06 的 app DELETE/注销断边没有重复搜索或改变结论。

事实：上述字节、宽度、掩码、精确目标编码候选、注册身份和 body 不覆盖 a00a1aa8。推断：BC/BN/V 与 PB/PE/P 为日志支持的分析名；“cells/power”不是完整协议结构认证。未知：存在于未覆盖函数/间接数据链的实际读者、潜在非相邻取址注册、全局总快照或数组别名的其他暴露点、协议数值单位、硬件实际显示及所有未认证源码来源。没有关于无消费者/死代码/缺陷的结论。

## 实际验证与一个后继闭包

运行 `python reverse/analysis/ctk-extra-consumers-e07-0041-20261023/verify.py` 成功：17 个精确目标编码候选（getter14，注册3）、17 个窗口262条原指令、16个限定 dossier；`a01917d0` 无所选 retained analyze_function dossier但已全原指令核。脚本检查指定 raw bytes、copy/log 直接目标、窗口边界，并保留 a00a1aa8 的 body 不匹配。标准 Capstone 与显式 THead 字段只在局部使用，解码以 E05 helper 为基础补充 E01 已用 `th.mula`；不改分析器。未运行项目/固件测试或历史回放。

后继只建议一个有界问题：从 `a00a1aa8` 原调用和 `s0-e4` 保存槽出发，核实真实正常函数入口/CFG及 item 指针的局部后续传递，回答是否沿该别名到达 +34/+38 读取；如果只用普通字段则准确关闭这一候选，随后再另派数组别名入口。不得假定它就是新数值消费者或扩大为全 ROM 扫描。本轮交付状态为**定位部分完成、真实页面消费闭包未解，待独立技术复核**。


## 继承：早期 SIM/ROM 研究交叉对照

按管理者转达的用户要求，补读主树的早期研究后，本轮将已存在的行为全部列为继承。旧 `tools/ap01/...` / `artifacts/ap01-research/...` 引用不代表资料缺失：当前可从 `reverse/rehost`、`reverse/reports/ap01`、`reverse/analysis/0041-20261013` 和最终 source.zip 找到相应原件。交叉检索既用业务标题，也用 getter/callback/注册器地址、+34/+38 的 byte/word 表达及更新 mask；[简短定位结果](../../analysis/ctk-extra-consumers-e07-0041-20261023/inherited-source-crosswalk.json)只存出处和少量定位信息，没有重新导出旧函数。

| 已有出处 | 已解释行为，应直接继承 | 局限与本轮剩余增量 |
| --- | --- | --- |
| `reverse/rehost/charge-complete-0041.json`，10-16，`native_creators` / `service_contract`；`records[8] a00f4610`、`[9] a00f44e8`、`[19] a00f5288` | C1/C2 四槽 IN/OUT/P/V/A、SOC 和 H/M，以及 detail普通项数值与历史图业务早已覆盖；这不是 E07 新发现 | complete 明说硬件回调由本地服务替代、部分布局为重建。`[19]` 的 +34 是 panel 字段，与本轮核 s5 的结果相符；没有建立 item+34/+38 数值读者 |
| `reverse/rehost/charge-0041-round4.json`，`observed.overview_bank` / `records[4..5]` / `[7]` | 早已记录 `a00ef1d4/a00ef2da`、前3组显示与 `a00f61ae` 中 `a01917d0` 的调用线索 | round4 的“connected-device ... not restored”被后来的 complete 的SIM覆盖取代，不能继续作为现状结论。a01917d0 线索是继承，本轮仅补其原字节的非扩展字段门控解释 |
| `reverse/rehost/page-logic-0041.json`、`page-logic-evidence.json`、`page-logic-evidence2.json`、`main-knob-0041-round2.json` / `detail-knob-0041-round2.json` | 旧主页面构造/旋钮/详情路线与 `a00adabc` 注册引用可复用；不重新发现整个 CTK 页 | `+34` 命中包括 app active-child index，mask也大量来自GUI样式。不能据文字命中宣称 item buffer alias；未找到把该两组指针连到真实值转换的新证据 |
| `reverse/rehost/details-0041-round4.json` | 该文件主要是 Date/Weather detail；+34/+38 命中在 calendar/weather对象布局 | 名称“details”不等于 CTK detail；没有按同偏移拼接消费者 |
| `reverse/reports/ap01/application-function-matrix-0041.json`、`factory-reference-map-0041-20261020.md` | 给SIM家族覆盖与原函数/资源出处；后者cuk_con部分直接指向 complete/round4 | 矩阵是覆盖索引，不能把 passed-in-sim 当原ROM全部字段已恢复；已沿其出处继续核地址 |
| `reverse/analysis/0041-20261013/0041-ghidra-pass3.txt`，含 `a00adabc/a01b28ce` 引用 | 早期 creator/注册关系原始证据可继承 | 有旧模型/custom0与截断限制；本轮仅对本问题字段/ABI具体窗口使用近期 E01..E06 和原字节复核 |
| `reverse/rehost/ap01-ui-0041-complete-source.zip` 只读成员 `tools/ap01/ap01-ui-charge.h` / `ap01-ui-details.h` | charge成员352..377行读取 `bank->battery`、`remaining_minutes`、`ports[i]`；另有 `ap01_sim_get_port` 访问 | 这些是本地服务模型字段；不存在按名字自动对应 wire `item+34/+38` 的理由。只读zip成员，未解压、构建、运行或回放 |

complete 中上述三条 ROM evidence 分别为 `ev_a5e9ee75bd0538cbf7e162f205773a29ef0b74cb51f1da0c3108f9bdce600adb`（values）、`ev_28940c3eaa4e13f7d351652eac928f4ea62a4f1961422b2f1ad27137a95d8931`（name）、`ev_709b5ff51cf4fb33e1b9ae866819ac7a860e0ffe029c2c56c7e9344ac037af88`（detail callback）。这些原指令证据可直接继承；旧反编译模型警告不使整份旧成果失效，也不免除特定宽度/厂商字的近期复核。

## 本轮复核或纠正、真正新增与精确断边

- **继承不算新增**：五组生产/所有权、前三组显示、页面/旋钮总体行为，以及 a01917d0 的调用存在。E01..E06 的近期限定复核继续适用。
- **本轮针对核/防误读**：两个生产日志的原读宽/位域；a00a3c8a只读普通项；a00f58b8的+34属于panel；a01917d0为普通item+24 bit6控制门。原有字节材料与已做的262指令窗口保留，不追加机械重导出。
- **真正新增的增量**：将指定 getter/注册器的精确编码候选与 retained body逐一对照，明确 `a00a1aa8` 不在 `a00a12d0` 的既存body，禁止错误归属。它是引用边界信息，不是新的页面功能恢复。
- **精确断边**：实际 +34/+38 页面读者、转换/主要下游/借用寿命仍未定位；旧SIM模型也没有补上此原ROM alias连接。下文后继建议仅针对 a00a1aa8 的正常函数/保存槽别名，不再扩扫或凑闭包。
