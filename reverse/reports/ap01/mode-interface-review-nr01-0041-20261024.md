# NR01：N01 模式请求、应答与协调接口独立复核

**限定接受；修正差集已确认，可独立使用的正常协调阶段闭合，完整接口未闭。** N01 报告唯一要求修正的 dispatcher Evidence/profile 归属错配已由作者修正，并在同题续核中确认与原留存一致。本轮没有发现需改变模式业务合同的指令、ABI、对象身份或控制流错误；未重跑全批。

认领仍为 N01，复核者 `/root/nr01`，非作者；基线 `5bbc331`，独占本报告和同名 analysis 目录。按主树最新 [流程](reverse-design.md) 及管理 N01 行核整个相关差集和必要继承，不逐 helper 派发。使用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)；只复用留存和离线原字节，不打开或切换共享 REA，不执行作者验证器、固件、模型、回放、构建，不接设备/网络，不改主树、原件、生产配置或分析器，无下级代理、提交或推送。

## 继承结论与证据适用性

原件为 [CATALOG](../../../roms/CATALOG.md) 中 0041：6,769,704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；VA 到文件偏移为 `VA-0x9ffff000`。本轮复用既有身份记录，只核长度和选中原字节，不重做哈希清单。

必要继承为 mode-control 的生产入口/UI 合同、B19/B21 的正常解析/四槽复制和逻辑归还、MiIO 延后设置的共享 timer 合同、UART retry 的耗尽合同、dock 的局部清理合同。已直接复核生产入口、submit、快照变化/分发、缓存 helper、retry 和两个局部清理器的必要指令；parser 的 CRC/state2/cmd-match 门、驱动 write 内部及 MiIO 全生命周期仍按原已验范围继承，没有把继承未知转换为已闭。

N01 源报告及 analysis 只读自主树 `reverse/reports/ap01/mode-interface-n01-0041-20261024.md` 和 `reverse/analysis/mode-interface-n01-0041-20261024/`。应答留存为主树 `reverse/analysis/uart-response-0041-20261023.json`：

- `/functions/0`：dispatcher `0xa00a8582`，Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`，profile **`bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`**。
- `/functions/1`：缓存 helper `0xa0191652`，Evidence `ev_3a861f94ddb2b4481b6d96b4f46d593f35e2729ecb9022aa64949e92b607615c`，profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。

N01 报告“本轮复核与真正新增”第一段原把第一项 Evidence 配成第二项 profile；作者已将该处修正为 `bcefdee...`。同题续核仅读取修正句和旧 JSON `/functions/0`，确认 Evidence、profile 与 dispatcher 地址一致；N01 的 instruction-evidence.json 原已正确记 `bcefdee...`。复核者未改作者原件。旧 whole-dispatcher bad-instruction 警告仍有效，不能以本轮选择窗口认证其他分支。

## 本轮逐项复核

| 接口合同 | 结果及独立依据 |
| --- | --- |
| 输入、位宽与返回 | 接受。`0xa019537a..53f5` 先写低 byte 到 `b512/b01d`，通知后从栈恢复原 32bit mode，原值等于 3 才走自定义。`0xa019530a..5379` 首 byte 需为 3，后三 byte 在同步通知返回后才读。各出口没有业务结果/请求身份定义。 |
| submit 与持有归还 | 接受。`0xa01951e2..5309` 使用 descriptor `cmd@0,len@1,payload*@4`，同步复制到活动区或四固定槽；去重和满槽直接返回。没有保存 descriptor 或源 payload 指针，没有请求级 free。保留 occupied 先写、复制后重读 state 等原序；不增加并发保证。槽消费/正常 parser 继续继承 B21。 |
| cmd60 与 ack_copy | 接受。`0xa00a87ac..87d1` 设 `a0=b50d,a1=1`，`a2` 沿入口仍为 raw payload；不是 view 指针。`0xa01ad024..d049` 调 copy 前以 sb 清传输 state；返回后 caller 重读 `b01d`，等于 3 才查询。没有检查应答 byte 或宣布业务成功。 |
| cmd57 阶段与对象身份 | 接受。`0xa00a983e..98cf` 固定 6B 缓存到 `b510`，缓存 helper 的同步回调先返回，随后才读取 `b51d/b512/b01d`。阶段0采纳收到 mode、写阶段1、调用 `(10,0)` 控制值设置和自定义查询；阶段1不同 mode 重发期望，期望3用 `b518`；mode相同时才比较两个16bit控制值。其他阶段仍走变化检测和既有 selector。`b512` 同时被本地入口覆盖，不能命名成永久独立 reported mode。 |
| control16 与必要应答续接 | 接受。`0xa00a417c..41b9` 将 u16 旧值与完整 `a0` 比较，值不同或 force 非零才截低16bit写 `b51e`，submit cmd62/len2。`0xa00a9cbc..9d05` 先保存1B应答/清state；cmd62才按独立 `b516` 与100比较，必要时写100并构造 cmd61/len2。`b516` 与 `b51e` 不能合并或推单位。 |
| cmd5e 与 UI | 接受。`0xa00a4158..417b` 构造 cmd5e/len0/NULL。`0xa00a99f0..9a89` 固定3B缓存到 `b000`，cache回调后重新取全局快照；非NULL才比较/写 `+9/+10/+11`，有变化以 sh 覆盖 mask=4并同步分发。`0xa00a536c..53bf` 每轮重读快照，最终清当前 mask。通知是借用指针，不能当持久完成凭据。 |
| 缓存派生事件与重入顺序 | 接受。`0xa0191652..16ff` 先清 state、比较固定 n、变化时复制，再取当前 handler 同步调用 `((cmd+0x20)&255,0,NULL)`；cmd57/5e 的0x77/0x7e在 caller 后续协调/UI之前。没有把它们合并成请求成功事件，后续全局读取不能前移。 |
| 失败、耗尽与协调期限 | 接受限定合同。`0xa00eea08..ea81` 只有state2推进，wait byte回绕，达到阈值且 attempts>=5 时清state，调用非空当前handler `(0x24,0,NULL)`，再启动器。该body没有模式回滚或业务错误结果。cmd57重发分支没有协调总次数/期限字段；不能把传输attempts上限当整个协调上限。真实调度和驱动错误仍属继承边界。 |
| 取消/关闭 | 接受“未闭”结论。直接核 `0xa00a5558..55b9` 的 `b01d/b51e/b516` 清零和 `b518=3`，以及 `0xa00a3ab6..3b21` 的局部free/清指针与 `b51d/b50c` 清零；两者不足证明与在途响应、四槽和 MiIO timer 的全局先后。没有可取消请求句柄的证据，不得补造取消/迟到工作保证。 |

## 真正新增与实际独立检查

新增业务恢复为 **0**；本轮是非作者复核和上述 profile 纠正。原字节、访存宽度、调用参数和分支是静态事实；“期望/阶段/协调”等是分析命名。静态值相等不证明底座执行、持久化、实际接收或产品码含义。

[独立脚本](../../analysis/mode-interface-review-nr01-0041-20261024/review_decode.py) 从 ROM 半字前缀推进并用 Capstone 解码；未导入或执行 N01/历史验证器。实际检查：20个限定窗口、601条指令、215条与旧应答/cache raw_ranges直接比对；另以独立位字段运算核21个JAL或AUIPC/JALR目标、12个关键条件分支目标。独立完成后与 N01 留存逐行比较，184条原字节和解码全部一致，三个新增 body 的36+62+38=136B均覆盖。机器证据为 [JSON](../../analysis/mode-interface-review-nr01-0041-20261024/independent-decode.json) 和 [可读指令](../../analysis/mode-interface-review-nr01-0041-20261024/independent-decode.txt)，不赋予其新 REA Evidence 身份。

检查中曾把 ack续接窗口临时多选至 `0xa00a9d1e`，在不属N01合同的 `0xa00a9d0e`遇到不可解码；最终限定回N01选中的 `..9d05`，未改写未知编码、未认证后缀。其他临时窗口尾越过已知指令边界的断言失败已按真实ret/既有extent修正；最终20窗口均无未解码项。没有将脚本PASS替代上表的寄存器生存期、同步重读、所有权和状态审查。

## 未闭精确边与交付

完整接口仍未闭：`0xa00a3b10` 清协调阶段、`0xa00a557c` 清期望，与在途 cmd60/57、排队 mode 和 `0x62fc9428` 共享 MiIO timer 的取消/排空/迟到应用先后未知。后继只建议在原认领下核同对象停机阶段，不扩 MCU、订阅销毁或公共库内部。`b50d`结果码、两个控制值的产品含义、custom参数0、完整handler寿命及UART驱动持有/并发写者仍保持未知。

最终状态：**N01 业务差集逐项限定接受；证据归属修正已确认；正常协调阶段可独立使用；完整接口未闭。** 本次续核只确认该文字差集，不重跑 ROM/脚本、不扩题，所有技术断边保持原状。

预计约30分钟工作量，可提前完成；实际开始UTC `2026-10-24 13:27:59`，结束与墙钟、工具情况见 [交付记录](../../analysis/mode-interface-review-nr01-0041-20261024/delivery-checks.json)。无主动等待/中断，短工具调用不单独累计；墙钟不等于纯有效工时。token由父窗口实测，本报告不估算。

原技术计时保留；修正差集续核开始UTC `2026-10-24 13:35:45`，结束和本次墙钟另记交付记录，不把两次之间的停止间隔计为工作时间。
