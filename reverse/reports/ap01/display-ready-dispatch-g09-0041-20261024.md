# G09：既有 ready 消费器到显示 watcher 的条件连接

2026-10-24；基线 `bccdd65`，分支 `codex/re-0041-g09`。**局部补齐 ready 记录按 fd 选中同一 watcher、读取 callback 并传入 adapter 的静态连接；未证明 OS/驱动实际产生 ready，也未认证底层事件提交或记录生产。** 作者静态检查通过，待独立技术复核。新增页面业务 0、来源排除 0；主要增量为已有两端之间的字段/对象绑定。

## 继承的旧结论：已有成果→实际缺口

|既有出处、证据类型|已经解释的行为|证据局限、本轮只补什么|
|---|---|---|
|[G07](display-alternate-work-g07-0041-20261023.md)、[G08](display-alternate-review-g08-0041-20261023.md)，原字节及独立复核|state+60 是 poll；poll+34 是 watcher；watcher+0 安装 a009f8ea；start 的 events=2 转 mask4；poll+30 保存 a00806d0。adapter、stop、刷新、清 pending 原序已有|全部继承，不重导或重记业务。仅补 backend 记录如何按 fd 找到 watcher+0|
|[factory initializer 留存](../../analysis/factory-test-0041-20261023/retained-initializer.json)，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`|**原汇编、原 raw 和旧反编译已经完整留存** a005c704..c780 的 fd 桶遍历及间接分发；不是此前没有分析，也不是本轮首次发现 ready 消费器|旧反编译不能独自认证厂商 indexed 指令/节点别名；只复核五个必要窗口，并与 a009ec98 注册节点连接，不再导出整个 initializer|
|[C03](pogo-close-callback-c03-0041-20261023.md)–[C08](pogo-close-consume-review-c08-0041-20261023.md)、[F03](miio-loop-close-f03-0041-20261023.md)/[F04](miio-loop-close-review-f04-0041-20261023.md)|公共 poll/init/start、loop pending/close、原 handle callback 与关闭消费已有合同|直接引用；ready 消费不是 close drain，不能借本题声称退出后会继续消费|
|[whole-ROM 旧索引](../../analysis/whole-rom-coverage-0041-20261023-round1.json)，a009ec98 extent Evidence `ev_5416066f1d33e0cf502d76d276fa7b492d767a369619ba0665f04dbd0c259461`，direct calls `ev_e3587bc8aa05da298435a39736b94ca720a66de55831c3a0877b0fe78079c435`|已知登记函数范围 a009ec98..ee15、libuv 源路径候选及直接调用；没有认证整库来源|沿用索引定位，不做全 ROM incoming 字节重扫，只读登记内部三个必要窗口|
|优先最终报告/矩阵/工厂映射、领域 complete、page-logic、较晚 round3 与 pass3；ZIP 只读成员，检索结果见 evidence.json 的 reuse|SIM 重建、local service、安全替代及最终 passed-in-sim 已有成果；不能证明本 ROM backend ABI/版本|精确地址检索仅说明所检文本集合未命中，不说明从未分析；近期 retained initializer 实际已有重要原证据。旧 pending/旧失效链接不作为缺失依据|

旧模型 custom0/unaff 或 no-return 不用于证明本轮字段值。本轮只依赖普通正常前置路径与明确编码；a009ec98 的 assert 分支没有被当作必不返回。REA retained summary 对精确 procedure 的当前会话返回 matching_records=0；这不能否定仓库中的上述旧 Evidence，也没有因此创建/切换共享数据库或重新分析。

## 本轮复核或纠正

对 retained initializer 五个窗口共 294 B 与原 ROM 局部逐 byte 比对通过，均标为**旧结论复核**。原 raw/整汇编没有再存一份。重点是旧反编译 `puVar34[-5]` 实际是 `node-0x14` 的 callback 字段，不是另一个 owner callback。

厂商字按现存只读模型的 `th.addsl`/`th.lrw` 规则拆编码字段：

|位置、原字节|独立字段核对后的意义|
|---|---|
|a009eda6 `8b17d706`、edaa `0b47d746`|地址 `loop->buckets + (fd<<3)`；从同地址取 bucket 首节点，分别是 addsl a5,a4,a3,3 和 lrw a4,a4,a3,3|
|a005c706 `0b98e706`、c70a `8bc7e746`|ready record 的 fd 再计算同一个 8 B bucket，并读取首节点，分别是 addsl a6,a5,a4,3 和 lrw a5,a5,a4,3|

上述 raw 以 evidence.json/vendor_checks 为准；四条按 opcode/funct/寄存器/shift 拆字段，不靠把 custom0 当通用 load。这里只认证所用规则和原字，不修改模型，不外推全部厂商指令。

## 本轮真正新增

### 注册端：watcher 的 fd 桶节点

a009ecc4 从 watcher+24 取 signed fd，ecc6 保存 watcher 到 s2，ecea 保存 loop 到 s3；ece8/ecec/ecee 以 word 读/OR/写 watcher+1c 的 desired mask。G07 本次 start 输入给它 mask4 的合同沿用。

a009ed70/ed74 比较 watcher+20 与 +1c，已相同则 ed78 跳到返回；不同才可能进入更新登记。ed7c..ed9a 将 watcher+c 的节点挂到 loop+2c 的待更新链（已挂时不再重复）；这只是软件登记，不等于底层 OS 已接受。

ed9e/eda2 读 watcher+24 fd、loop+34 bucket 数组。eda6/edaa 计算 bucket 哨兵与首节点。已有节点时 edae 转 ee0a，将 node-14 与同 watcher 比较，相等即返回；否则 ee12 读 next，ee14 回 edae，抵达哨兵才执行下述尾插。这个12 B身份接点纳入本轮必要窗口，不据此认证分配扩容算法。空 bucket 的 edae..edc2 将 **watcher+14** 插入 bucket 双链尾：watcher+14=哨兵，watcher+18=旧尾，旧尾.next=watcher+14，哨兵.prev=watcher+14。edc4..edca 增 loop+3c。节点与 callback 本体相差 0x14，不能将 bucket 内的 node 当 watcher 本体。

### 消费端：复用旧 ready 分发，接到已认证 adapter

原 initializer 的 a005c334..c342 以 `(saved_backend_object, frame-0xc0, 8)` 调 a010d7da，将返回值保存为 s10；仅在返回记录数正常为正的后继消费这些记录。本题没有恢复 a010d7da 的生产算法或命名其底层系统调用。

c424..c452 的记录指针初值 frame-0xc0；c4da/c4de 从当前记录+8读 fd，-1 跳过；另一特殊 fd 分支不属于本 display watcher 的普通 fd 分发。普通分支 c6ea..c704 要求 signed fd>=0 且 unsigned fd<loop+38 的 bucket 数量，再读 loop+34。c706/c70a 的 indexed 指令与注册端是同一 `base + fd*8`。

bucket 为空时转另一路处理，不伪造 callback；非空时，令 node 为首节点，c72a **先保存 node.next**，随后：

```c
// 偏移视图和伪代码是分析者表达，不是原源码。
watcher = node - 0x14;
mask = (word(node+8) | 0x18) & word(record+0);
if (((mask - 8u) & ~8u) == 0)
    mask |= word(node+8) & 0x17;
if (mask != 0 && watcher != loop+0x150) {
    saved_next = word(node+0);       // 实际在 c72a 已先读取
    a009d382(loop);                 // 原调用保留；内部不在本题认证
    cb = word(node-0x14);           // c77a 在该调用之后才读取
    cb(loop, watcher, mask);        // c780；返回值未在此消费
    // 原程序从保存的 next 继续；不重排为 callback 后重新读 node.next。
}
```

`word(node+8)` 即 watcher+1c desired mask。c74c 得 watcher，c758 暂存；c76e/c772/c776/c77a/c77e 恢复 node、mask、watcher、callback，并置 a0=同 loop。内部特殊 watcher==loop+150 走延期标记，不在本题外推所有 fd。c59e..c5b2 令记录计数加一、记录指针加16，故该旧记录视图仅证 `+0 events word / +8 fd word / stride16`，没有认证完整系统 ABI。

按 G07/G08 的真实安装，目标 watcher=state+94（poll=state+60，watcher=poll+34），watcher+0=a009f8ea。因此在该 watcher 尚挂于同 fd bucket、选中其节点、mask 非零且普通分支成立的条件下，c780 的 a0/a1/a2 精确满足既有 adapter `(loop,watcher,backend_events)` ABI；adapter 再调用 poll+30 保存的 a00806d0。mask4 的返回记录在本 mask 公式下可保留4，继承 adapter 将其映射为公开 events2。回调 stop→默认 display 刷新→清 pending 的后继已由 G07/G08认证，不再计新增。

这形成**记录已返回→fd bucket选中同 watcher→真实 callback ABI→旧业务回调**的条件连接；不是记录必然返回、fd 从未复用或设备真实刷新完成的证明。

## 仍未闭合的精确边与验证

- a010d7da 对应 backend object 的真实 ready 记录生产，以及登记待更新链经 a009e0e6/底层提交到该 backend 的完整成功合同未闭。本题没有执行 OS poll/驱动，也没有证明 framebuffer ready 位的生产者。不能称实际 ready 已恢复或必达。
- 存在多 watcher 共用 fd 的 bucket；本题静态确认包含关系和消费 ABI，不证明运行时节点仍挂、fd 没有更换/复用、callback 恰好一次或整个 loop 生命周期完成。
- a009d382 为 callback 前原有调用，其内部及同步/重入影响未认证；保存 next 的事实不等于证明节点生命周期安全。退出后 drain、owner+180 全部写者、默认 display 同一性继续沿 G07/G08 的精确未知。
- libuv 路径仅为来源候选。没有用本地候选源码覆盖 ROM 差异，没有整库排除或新增源版本结论。

[verify.py](../../analysis/display-ready-dispatch-g09-0041-20261024/verify.py) 静态执行通过；[evidence.json](../../analysis/display-ready-dispatch-g09-0041-20261024/evidence.json) 保存三个新增接点窗口 150 B、五个旧结论窗口 294 B 的原字节比对索引、37 项 asm/目标检查与4条厂商字段检查。原 ROM 映射 VA-0x9ffff000；没有重复整函数导出、全 ROM incoming 重扫、资源提取、PNG 解码、源码复制或哈希账。没有 SIM、构建、历史回放、固件/设备/网络执行，没有修改生产/ROM/配置/模型或共享索引。

一个有价值的后继是独立复核本次 fd-bucket node 别名、四个厂商字与 callback 前后重读时点；若继续研究 backend，另设仅 a010d7da 记录生产/登记提交的实际断边，不重做本报告和 G07/G08 已有两端。
