# P-06：底座 UART poll 的业务 owner 与退出接口

**可独立使用的创建/借用/注册及同 owner 退出登记阶段已闭合，完整关闭接口未闭；待非作者复核。** `s3` 在本注册点是动态 context 的内嵌对象 `P=ctx+8`，不是 fd 数值，也不是全局 fd 槽地址。初始化时 `ctx.fd@4`、全局 `0x62fc91b0` 和传给 poll init 的 fd 来自同一次 `/dev/ttyS1` open；业务回调却重读全局槽，因此不能外推为所有运行时刻始终同一 fd。

认领P-06，基线`5bbc331`；主树只读，独占本报告与同名analysis。采用[REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，只读留存及必要原ROM短窗。没有打开/切换共享REA或模型、执行固件/模型/设备/网络/SIM/QEMU/回放/构建、修改生产/ROM/配置或提交推送；未创建代理。REA只读会话观察为open=false，不由本任务关闭他人会话。预计约30分钟，可提前收敛；精确墙钟与检查见末段。

## 继承结论与查重

| 已有出处 | 直接继承；本题差集 |
| --- | --- |
| [P-01](mode-stop-p01-0041-20261024.md)/[P-R01](mode-stop-review-pr01-0041-20261024.md) | ADC确认离线、普通事件0x23、OTA退出均先UI离线再清底座缓存；局部复位与重新发现清槽分离，未证明poll注销/排空。本题仅接其`s3`真实业务注册种子，不重验57/60或局部cleanup。 |
| [D03](uart-write-object-d03-0041-20261023.md)/[D04](uart-write-review-d04-0041-20261023.md) | `/dev/ttyS1`路径、flags43h、open→ctx+4/s5→91b0，属性101→1002→102及其错误日志。File引用和write复制均继承；不重做driver/文件层。 |
| [C01](pogo-timer-lifecycle-c01-0041-20261023.md)/[C02](pogo-timer-review-c02-0041-20261023.md) | 同context请求19ch、timer首槽、四poll退出登记、fd>0门；此前未认证整个容器参数/跨片段控制流。 |
| [C03](pogo-close-callback-c03-0041-20261023.md)/[C04](pogo-close-review-c04-0041-20261023.md) | 已验UART对象ctx+8的回指、ctx+198增加和`3bc6(P)`递减/条件释放。发现这一重叠后直接继承，新增callback body为0。 |
| [C05](pogo-close-dispatch-c05-0041-20261023.md)/[C06](pogo-close-dispatch-review-c06-0041-20261023.md)、[G07](display-alternate-work-g07-0041-20261023.md)/G08及G19–G28 | init/start/stop、type8 close→pending→原handle callback、软件兴趣撤销与backend接入条件。公共poll及allocator内部均不重做。 |
| [D10](uart-dma-channel-review-d10-0041-20261023.md)/[D12](uart-channel-source-review-d12-0041-20261024.md) | DMA slot归还、lower shutdown、callback/pair及硬件排空是另外的对象/边界；poll stop不自动构成这些保证。 |

本题真正新增是**成功分配的ctx寄存器身份→同fd值两槽→ctx+8注册→同ctx退出登记**的组合合同，以及callback使用当前全局fd的限制。旧helper主体新增0；没有把已有C系列关闭成果重新计为新恢复。

## 本轮复核与新增接口

来源为主树`reverse/analysis/factory-test-0041-20261023/retained-initializer.json`的`/function`：Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile **`bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`**。只提取必要窗口及保存寄存器定义摘要，没有重解整`0xa005a736`。来源的完整body边界及其他厂商指令警告继续保留，不据它证明全部控制流。

| 阶段 | 输入、输出、错误及所有权合同 |
| --- | --- |
| 借用loop | 入口`0xa005a77a`保存原a0至s1；本题注册以s1作loop实参。留存定义摘要在a77c..b314内没有s1目标写入；`a8cc`的SW以s1为源。冷分配短窗也不改s1。此身份桥要求外部callee按保存寄存器约定正常返回，不认证全部间接入口。loop未在本阶段转移所有权。 |
| 取得ctx | 继承C02：`cbca`请求19ch，`cbe2→a008e362`，`cbe6`保存返回到s2。非零`cbea→aa68`继续外围设备注册；零分支到日志，最终`cc1c`自环。不能虚构标准NULL错误返回。分配器内部、初始全部字段与精确分配容量保证未展开。 |
| fd打开与两槽 | `ab10..ab24`按D04调用同路径，返回值写`word(ctx+4)`并保存在s5；`ab2e`仅signed fd>0走`b214`。该分支填零91b0起6ch后，`b232`把同s5写`word(0x62fc91b0)`。错误/属性日志路径沿D04，不把日志当提前失败返回。两槽是不同存储位置中的相同初始数值，不能称内存别名或fd对象本身。 |
| 注册同P | `b2d8`取全局fd作一次1B read；`b2e6`随后独立取ctx+4到a2。`b2ea`令s3=ctx+8，`b2ee`交a1，`b2f0`先写`word(P)=ctx`；`b2f4/b2f6`调用`a009e4f6(L,P,ctx.fd)`。随后读/增/写ctx+198，再`b310→a009f9b6(P,1,a00a8330)`。init数值返回未被测试便增计数/start；start返回未被测试便到日志。不能把计数增加或日志当init/start成功回执。 |
| callback借用fd | 所选`839a..83bf`窗口先检查events bit0，再构造91b0地址；`83ae`取其**当前**word为read a0，`83b2/b4`给len1及本函数栈byte，`83b8→a003f6a2`。不从P+58或ctx+4取本次read fd。callback内后续parser合同继承P-01/USB，不重验。 |
| 同owner退出登记 | `c830..c83e`在当时loop+18非零分支清该word，随后转到退出区域；s4零可直接到`c8f8`，非零先处理其他owner，不能说所有出口直接相邻。`c8f8`读同s2+4；signed>0时`c908`给同`ctx+8`，`c90c→a009fb96(P,a00a3bc6)`，否则跳过。留存aa68..c8f8的s2首操作数候选仅四条以s2为源的SW；没有目标寄存器重赋值。此检查是有界身份前提，不是全CFG/所有路径到达证明。 |
| 停止与归还 | 直接继承C06/G07/G19–G28：正常type8 close先软件stop/撤销，再排pending；若后续被consumer消费，关闭callback得到原P。C04：ctx=word(P)，next=word(ctx+198)-1按RV32写回；signed next>0返回，否则把ctx交释放封装。封装过滤NULL及62fc95e0，再交底层free。callback恰好一次、计数全局不变量、后续drain机会和ctx最终安全释放仍未知。 |

偏移均为十六进制，分析伪代码不是原源码，也不是完整错误处理实现：

```c
// 各阶段有实际控制路径/正常callee返回前提；省略其他已验poll业务。
L = original_argument_0;                   // 借用loop
ctx = alloc_like_a008e362(0x19c);          // 零分支不是标准return NULL
ctx->fd_at_04 = open_ttyS1(0x43);
if ((int32_t)ctx->fd_at_04 > 0) {
    global_fd_62fc91b0 = ctx->fd_at_04;    // 中间属性设置沿D04
    P = (uint8_t *)ctx + 8;
    word(P) = ctx;                        // userdata先于poll init
    init_a009e4f6(L, P, ctx->fd_at_04);    // 本caller不检查返回
    ctx->word_at_198++;
    start_a009f9b6(P, 1, callback_a00a8330); // 本caller不检查返回
}
// 模块owner退出阶段；不是presence变0的局部离线路径。
if ((int32_t)ctx->fd_at_04 > 0)
    close_a009fb96((uint8_t *)ctx + 8, callback_a00a3bc6);
// callback_a00a8330的read使用当前global_fd_62fc91b0。
```

借用/持有视图：ctx内嵌P及其回指，timer userdata也持ctx（C02）；loop链暂持P（C06/G19），P不能在pending消费前任意复用；fd是标量输入，不因交poll就转移底层设备所有权。最后一句是现有字段/调用关系支持的重建约束，不是完整竞态证明。不能用ctx被释放推出fd已close，更不能用fd相等推出两个slot同址。

## 与局部离线的边界及未知

P-01/P-R01的三个局部离线入口没有本题owner退出登记；本题存在真实模块deinit close caller，并不纠正P-01的局部负结果。可作接口连接的结论是“**有同owner close登记阶段，但未证明离线必走该阶段**”。底座断连/重新发现与loop退出不能合并为一个状态转换。当前没有证明注册后必ready、close后必drain、所有在途parser停用或业务请求被取消。

仍未闭：实际fd close及91b0清槽/重开与poll停止的顺序；timer最终停止/删除；全部计数写者及最终ctx释放安全性；driver/DMA/IRQ归还与硬件排空。没有在所核caller和已有callback里看到fd close，并非全ROM永不close的结论；未搜所有fd或重扫全部ROM。来源仍为原ROM静态行为；没有认证原厂源码/确切公共库版本，开源排除新增0。

一个有真实地址的后继：**模块deinit末端`0xa005c9e6`之后的owner延续→`0xa005cbb6`/`0xa005cbba`冷分配入口，是否在ctx释放/替换前再次给同loop pending消费机会**，约20–30分钟。留存末端`cbb6`为4B SW，下一记录`cbba`开始已验分配前局部初始化；这只是可定位的顺序布局种子，不能写成c9e6必达cbba或必然重新创建ctx。应只追相关业务退出路径/loop身份，继承`c166/c802`已验consumer，不重做walker、timer或其他MiIO业务；中间路线/loop身份不足即保持未知。本题未展开这个后继。

## 静态检查、差集复核包与时间

[verify_static.py](../../analysis/dock-handle-lifetime-p06-0041-20261024/verify_static.py)只读原ROM选中字节：9窗300B、86条普通RV32+C指令，逐条与对应留存raw匹配；44项操作数/独立JAL或branch位域检查及2项保存寄存器定义摘要PASS。没有运行旧作者验证器、指令模型或目标。[指令证据](../../analysis/dock-handle-lifetime-p06-0041-20261024/instruction-evidence.json)逐窗绑定Evidence及其精确profile，callback源独立标注，不把initializer的profile套给其他来源。原件身份沿CATALOG：0041、6,769,704B、既有SHA256`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射VA−9ffff000，未新增机械哈希账。

交给一个新非作者的合并差集：核L原参数保存、非零ctx→s2、fd两槽数值相同、P=ctx+8及首word、init/start实参与不检查返回、ctx+198位置、同s2退出登记及signed>0、callback当前全局fd重读、局部离线与模块退出分离。C01–C06/G/D已验helper主体全部继承；不为本题重复复核公共poll。机器[接口合同与复核清单](../../analysis/dock-handle-lifetime-p06-0041-20261024/contracts.json)列出这一差集及断边。

UTC首个精确时钟`2026-10-24 14:05:41`；此前技能读取启动未精确计量。结束、实际墙钟、JSON/链接/diff检查见[交付记录](../../analysis/dock-handle-lifetime-p06-0041-20261024/delivery-checks.json)。无主动等待或外部中断；工具等待包含在墙钟，不冒充有效工时，提前得到有界合同后即收敛，不等待凑时长。token由父窗会话遥测统计。
