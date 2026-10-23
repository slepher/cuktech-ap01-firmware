# G10：G09 ready→watcher 连接的独立复核

2026-10-24；基线 `3ba6b96`；独立分支 `codex/re-0041-g10`。结论：**限定接受 G09，未发现需要纠正的语义；新增 ROM 功能 0、来源排除 0**。接受范围是已返回的普通 fd ready 记录按同一 bucket 选中 watcher 后，使用 `(loop, watcher, mask)` 调用其 callback 的条件连接。不是实际 ready、提交成功或运行时必达的证明。

## 继承结论：已有出处→本轮实际缺口

|已有出处 / 证据|已解释的行为|局限 / 本轮缺口|
|---|---|---|
|[G09 原报告](display-ready-dispatch-g09-0041-20261024.md) 及其 [evidence.json](../../analysis/display-ready-dispatch-g09-0041-20261024/evidence.json)|a009ec98 登记 watcher+14；旧 initializer 通过 fd bucket 找节点、node−14 取 callback|本轮独立核节点身份、四条 indexed 厂商字、保存槽和间接 ABI；不重复其有界复用搜索|
|factory-test [retained-initializer.json](../../analysis/factory-test-0041-20261023/retained-initializer.json)，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`|已完整留存 a005c704..c780 汇编/raw/旧反编译；入口 a005a77a 保存参数0到 s1；ready 输出指针、fd、stride16 消费已在旧 body 内|G09/G10 不是首次发现后端；不依赖旧反编译 custom0/unaff，局部原字节校核仅记旧结论复核|
|[G07](display-alternate-work-g07-0041-20261023.md)、[G08](display-alternate-review-g08-0041-20261023.md)|poll=state+60，watcher=poll+34=state+94；watcher+0 安装 a009f8ea；events2→mask4；adapter 再经 poll+30 调 a00806d0；stop→刷新→清 pending、退出计数已有合同|直接继承，不重做业务 callback、stop 或退出；本轮只审 ready 接入这些已认证两端的 ABI|
|G09 对旧 complete/矩阵/最终 SIM/ZIP/近期 retained 的复用分层|已有 SIM 重建和服务替代；retained initializer 其实早已有 ready 消费器|不重做文本/ZIP扫描；SIM 通过不认证 ROM backend，所检集合无命中不等于此前没有分析|

本轮使用既有 REA 留存 Evidence 和只读 ROM 作离线字段核验；没有打开、切换或写入 REA 会话/数据库。没有创建新 target，不依赖并发会话的活动状态。所有新输出仅在本任务独占目录。

## 本轮复核或纠正

|核查项|结果|定位依据及解释|
|---|---|---|
|登记实参身份与字段宽度|接受|ecc4 以 word 读 watcher+24 fd；ecc6 保存参数1为 s2，ecea 保存参数0 loop 为 s3；ece8/ecee 读写 watcher+1c desired mask。ed70/74/78 比较 +20 与 +1c，相等跳 edce 返回。普通前置路径成立才论本合同，不假定断言必不返回|
|watcher+14 的 bucket 节点|接受|ed9e/eda2 读同 watcher fd 和 loop+34。edb2 写 watcher+14=哨兵；edb6 取旧尾；edb8 构造 watcher+14；edbc 写 watcher+18=旧尾；edc0/edc2 更新双链。ee0a 把现有 node−14 与 s2 比较，ee0e 相等回 edce，ee12 读 next。它不是另一个 owner 对象，也不是 watcher 本体直接入链|
|两端 indexed 地址相等|接受|eda6 `8b17d706` 的字段为 opcode=0b/funct3=1/top5=0/rd=15/rs1=14/rs2=13/shift=3；edaa `0b47d746` 为 0b/4/8/14/14/13/3。c706 `0b98e706` 为 0b/1/0/16/15/14/3；c70a `8bc7e746` 为 0b/4/8/15/15/14/3。分别是 base+(fd<<3) 与该地址的 32-bit 首节点读；后两条 `th.lrw` 不写回 base。用现存只读模型对应规则核意义，没有将 custom0 泛化为普通 load，也没有认证全套厂商 ISA/整库来源|
|ready 的 node 别名和 mask|接受|c704 仍读 loop+34；c72a 先读 node.next；c730 读 record+0；c732 读 node+8，即 watcher+1c。c734..744 的 `(desired\|0x18)&events` 及特殊 mask 补位原序与 G09 一致，word 宽度保留；c74c 才构造 watcher=node−14。mask4 输入可保留4，只是静态条件路径|
|特殊 watcher 的身份|接受|c434 构造 loop+150、c44a 保存至 frame−178；c754 重载它，c75c 比较 watcher 并跳 c79e。故 G09 将普通 callback 分支排除这个特殊 watcher 有直接身份依据，不把它外推为所有 fd 的统一行为|
|callback 前后的重读与 ABI|接受|c746 保存 mask 至 frame−17c；c750 保存 node 至−170；c758 保存 watcher 至−16c；c762/766 保存 next/哨兵至−158/−154。c76a 调 a009d382；其后 c76e/c772/c776 恢复 node/mask/watcher，c77a 才从 node−14 读取 callback；c77e 置 a0=同一 s1 loop，c780 `c.jalr a5`，即 `(a0,a1,a2)=(loop,watcher,mask)`。返回值没有被这一段消费|
|保存 next 后继续遍历|接受|c782/786 恢复原哨兵/next，c798 把 saved next 置为当前 node，c79a 再读这个新 node 的 next。不是在旧 callback 返回后重读旧 node.next；不能因此声称生命周期/重入安全已证明|
|接入业务端|接受，继承|按 G07/G08 的实际安装，目标 watcher+0=a009f8ea；本普通分支选中同 watcher 后，c780 的 ABI 满足 adapter 输入。adapter→poll+30→a00806d0 的后继仍归旧成果，不另算发现|

无技术语义纠正。G09 的伪代码仅为偏移视图，不是原源码；其 `saved_next` 行旁已明确实际读取在 c72a。本轮报告直接展开保存/恢复时点，避免读者把该示意行当成重排后的读取。a009d382 之前已保存 mask，之后只重读 callback；不能改写成该调用后重新计算 mask。

## 真正新增

仅新增独立技术复核记录和可重跑的字段校验。**新增功能 0**；登记/消费之间的字段连接仍归 G09，整个 initializer 原汇编仍归旧 ev_dc0e，业务 callback/stop/退出仍归 G07/G08 及更早成果。

[review.py](../../analysis/display-ready-review-g10-0041-20261024/review.py) 静态执行通过；[review-result.json](../../analysis/display-ready-review-g10-0041-20261024/review-result.json) 记录：G09 三个登记窗口共46条原 raw 与主仓 ROM 对应位置一致；旧 c704..c79e 及 c434..c44e 共180 B 与 retained raw 一致；52项编码字段、分支目标、保存槽及 ABI 检查通过。I/S/B/压缩访存/压缩 mov/JAL 和四条 THead 字按原编码拆字段，不仅比较旧 asm 文本。没有再次导出 initializer 或整函数；结果不复制原 raw/整汇编。

## 未闭合的精确边

- **未核**：a010d7da 怎样生产 ready record，登记待更新链经 a009e0e6 到 backend 的真实成功合同，以及设备/驱动是否实际产生显示 ready。G09 记录布局仅是消费者视图，不是已认证系统调用 ABI。
- **未核**：运行时 fd 是否复用、目标节点是否仍挂、多 watcher 情况下是否调用恰好一次、callback/stop 与并发或重入间的生命周期安全。保存 next 是指令事实，不是安全性证明。
- **未核，继承**：a009d382 内部副作用；退出后是否继续 drain、owner+180 全部写者、默认 display 与注册 display 的运行时同一性、具体 libuv 来源版本。

一个后续闭包如有必要，只应针对 a010d7da 的记录生产与登记提交身份，保留正常调用的对象/实参/返回数据合同；不要重做本次 fd bucket/间接调用或 G07/G08 业务。由管理者另行定题，本任务不自行展开。

只做静态原字节与留存证据核验；未执行固件、SIM、构建、历史回放或设备/网络操作，未修改生产代码、ROM、配置、模型或共享索引。
