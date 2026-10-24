# P-R06：底座 handle/fd 接入阶段非作者合并复核

**限定接受 P-06：可独立使用的创建、借用、注册及同 owner 退出登记阶段已闭合，完整关闭接口未闭。** 没有要求作者纠正的对象身份、ABI、调用或来源错误。这里的“阶段闭合”是有条件的静态接口合同，不表示 init/start 已成功、注册后必 ready 或退出后必排空。`P=ctx+8` 是内嵌 poll 对象；它不是 fd，也不是全局 fd 槽地址。`0xa00a8330` 的 read 使用回调执行时的当前全局 fd，不能认作捕获注册时 fd。

认领 P-06，复核者 `/root/pr06`，不是 P-06 作者；独占 worktree `.worktrees/batch-20261024-p/pr06`，基线 `5bbc331`。仅写本报告及同名 analysis。已读主树[流程](reverse-design.md)、管理顶部 P 段和 P-06 行；主树只读，不撤销他人修改。采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存证据及必要原件短窗方式，未打开或切换共享 REA/模型，未执行目标、设备、网络、SIM、QEMU、回放、构建或模型；未改 ROM、生产或配置，未提交推送，未创建代理。估算约30分钟，可提前收敛；实际时间见末段。

## 继承结论

被复核的是作者[报告](dock-handle-lifetime-p06-0041-20261024.md)及同名 analysis 的合并差集。C01–C06、G07/G08/G19–G28、D03/D04/D10/D12 的通用 helper、driver 和归还合同直接继承；本轮新增 helper body 为0。仅阅读 C04/C06 与 P-R01 的必要合同以核相接边界，没有重解它们的公共实现。

- C04：close callback `0xa00a3bc6(P)` 先从 `word(P)` 取得 ctx，再递减 `word(ctx+0x198)`；RV32 写回后 signed 值大于0返回，否则把 ctx 交释放封装。封装过滤 NULL 和 `0x62fc95e0`，再交底层 free；这不是 fd close 或 timer delete 合同。
- C06/G：正常 type8 close 登记软件停止和 pending；只有 consumer 后续消费时，才给 callback 原 P。没有必定再次消费、恰好一次或全局释放时序保证。
- P-01/P-R01：局部离线/UI和缓存清理、重新发现及四槽清理有其独立条件；这些入口未因此获得模块 deinit 的 close 登记。D10/D12 的 DMA、driver、IRQ 和硬件边界是另一个对象层。

原件沿 [CATALOG](../../../roms/CATALOG.md)：0041 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，既有 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，文件偏移为 `VA-0x9ffff000`。本轮独立核长度及所选原字节，未重做机械摘要账。

## 本轮逐项接受、纠正与未决

| 问题 | 判定与原字节支持的精确合同 |
| --- | --- |
| loop 原参数/保存 ABI | 接受条件身份。`0xa005a77a` 的 `aa84` 是 `s1=a0`；`0xa005b2f4` 的 `2685` 是 `a0=s1`。直接扫描原留存 `a77c..b314` 的首操作数候选，只有 `a8cc` 的 SW 以 s1 为源，没有普通显式目标写入。callee 正常返回且遵守保存寄存器 ABI 是前提；未认证整个 CFG、间接入口或厂商隐式副作用。 |
| 成功分配门与 ctx | 接受。`0xa005cbca` 给 a0 请求 `0x19c`；`cbe2` 的 JAL 独立重建目标 `0xa008e362`；`cbe6` 的 `2a89` 把返回 a0 保存到 s2。`cbe8` 是零值到 `cbee`，非零经 `cbea` 的 JAL x0 跳 `0xa005aa68`。零路径日志与 `cc1c` 自环按 C02/原留存继承，不补成 return NULL；请求数值不是 allocator 容量或初始化认证。 |
| open 与两个 fd 槽 | 接受。`0xa005ab1c` 目标 `0xa003f4f6`；返回 a0 在 `ab20` 写 `word(s2+4)`，`ab24` 留给 s5。`ab2e` 原字段为 signed `0<a0`，直接跳 `b214`。`b214/b226` 给 s6 构造 `0x62fc91b0`，`b232` 把同 s5 写入该地址。中间清零 callee 按保存 ABI；两个独立槽初值数值相同，不是内存别名，也不证明以后一致。路径/flags43h/属性错误日志沿 D04；不能把错误日志当提前 return。 |
| P 身份和 init | 接受。`0xa005b2e6` 取 `word(ctx+4)` 到 a2；`b2ea` 给 s3=`ctx+8`；`b2ee` 给 a1=P；`b2f0` 的 SW 把 ctx 写入 P 首 word；`b2f4` 给 a0=L；`b2f6` 目标 `0xa009e4f6`。前一 read 的 a0 是全局 fd，但 init 的 fd 实参随后独立来自 ctx+4，不能混作同一次加载。 |
| 计数/start/返回 | 接受。`b2fa` 构造 ctx+180，`b2fe/b30a` 为偏移18的 word 读写，故字段为 ctx+198；`b308` 加1。`b300/b304` 构造 a2=`0xa00a8330`，`b30c` 给 a1=1，`b30e` 给 a0=P；`b310` 目标 `0xa009f9b6`。init 返回后直接增计数/start；start 后所选后缀直接准备日志参数并跳转，无返回成功判断。不能把调用或计数增加当成功回执。 |
| callback 的 fd/ABI | 接受且必须保留限制。`0xa00a839a` 对 a2 events 做 AND1；`839c` 零则离开所选 read 臂。`839e/83a2` 构造 s2=`0x62fc91b0`；`83ae` 从该当前全局 word 取 read 的 a0；`83b2` 给 a2=1，`83b4` 给 a1=`s0-0x41` 的栈 byte，`83b8` 目标 `0xa003f6a2`。本次 read 没有从 P.fd 或 ctx+4 读取。未认证全局 fd 不变、重开顺序或 parser 全部后续。 |
| 同 ctx 退出登记 | 接受条件身份。`0xa005c8f8` 读 `word(s2+4)`；`c8fc` 的原字段为 signed `0>=fd` 到 `c910` 跳过，否则 `c900/c904` 构造 a1=`0xa00a3bc6`，`c908` 给 a0=`s2+8`，`c90c` 目标 `0xa009fb96`。原留存 `aa68..c8f8` 中 s2 首操作数候选仅四条以 s2 为源的 SW；支持保存 ABI 下同 ctx，不证明所有路径必走此处。 |
| 退出控制与局部离线 | 接受分界。`c830/c836` 读/清当时 s1+18，非零门后 `c83a` 已重新赋值 s1；`c83e` 的 s4==0 边到 `c8f8`。因此只在注册调用点称 s1 为原 L，不能把退出阶段此后所有 s1 仍称 loop；作者已用“当时loop”并保留其他 owner 的非相邻路径。模块退出 close 登记不覆盖 P-01 三条局部离线入口。 |
| 关闭、归还与错误范围 | 接受“未闭”。继承 C04/C06 的条件消费/计数/释放，不认证 OS fd close、全局槽清理、timer stop/delete、pending drain、exactly-once、所有计数写者、ctx 安全最终释放或硬件停机。这里看到调用不等于整个业务取消成功。 |
| 来源/profile | 接受。initializer `/function` Evidence 为 `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`；其原留存语言为 `RISCV:LE:32:ap01thead3`，基址一致。callback 来源是 usb-interface-ota JSON 的 `address=0xa00a8330`，Evidence `ev_6f900403de24d247461a1e302c564c71481c3d43d481acdc83bbb716318e1159`，独立 profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。两者未混套。整 initializer 9448B 是工具 body 元数据，不是本轮全函数或厂商指令认证。 |

没有要求作者修改的纠正项。补充强调退出时 s1 在 `c83a` 改写，是对已有限定的解释，不改变作者合同。`s2` 在 callback 是独立函数的局部寄存器角色；不能与 initializer 的 s2=ctx 跨函数认同。对象保持是正常 callee-saved ABI 条件下的有界静态推断，不是实机观测。

## 真正新增与独立检查

新增业务恢复0、helper body0、开源来源认证0。这是同 P-06 的非作者验收，不把旧字节复读另计恢复。公共 poll 可按既有功能等价方案重建；本题仅认证业务胶水的必要参数/对象合同，未认证原库版本。

独立 [review_static.py](../../analysis/dock-handle-review-pr06-0041-20261024/review_static.py) 仅用 Python 标准库读取原 ROM，手写提取所选 RV32+C 普通指令位域；未读、执行或导入作者验证器，也未使用作者验证器生成的断言作运行输入。窗口由本题地址边界明确列出，再直接对比原留存 raw_ranges 对应片段。结果为9窗300B、86条普通指令，44项独立列出的关键寄存器/偏移/分支/JAL断言通过，2项直接从原留存 assembly 提取的保存寄存器摘要通过。所有选窗指令均在这份有限解码器覆盖内，无未知编码补 NOP；摘要并非全 CFG/所有指令隐式写入证明。

[independent-checks.json](../../analysis/dock-handle-review-pr06-0041-20261024/independent-checks.json) 保留每条原字节、独立字段解码、两来源的 Evidence/profile 和保存寄存器候选。所核300B与原件及各自来源完全一致。完整 initializer 其他范围、厂商指令、间接控制流及其他 owner 未重解。

重建可用的最小阶段是：借用 L；成功获得 ctx 后，在到达对应 fd>0 注册臂时令 P=ctx+8，保存回指，以 ctx.fd 初始化并启动读兴趣；退出到达同 ctx 的 fd>0 登记臂时，将同 P 和既有关闭 callback 交 close。运行 callback 必须按实际当前全局 fd 读取。新实现若绑定 fd 快照、同步关闭 fd、等待 timer/pending 排空或引入 generation，均属于额外设计，不能标作本题证明的原行为。

## 未闭精确边与交付

真正断边为：模块 close 登记后是否还有同 loop 的 pending 消费机会，以及消费/ctx释放与 fd关闭或重开、timer删除和 driver/DMA/IRQ 归还的顺序。没有在所选 caller/既有 callback 中看到 fd close 只构成有界结果，不是全 ROM 无 close。

保留作者已经定位的后继种子 `0xa005c9e6` 退出末端到 `0xa005cbb6/0xa005cbba` 冷分配附近的业务延续；本轮没有追踪或取该后继的新字节，也没有把 listing 邻接写成必达/重新分配。若另行派发，应只问同 loop 是否在 owner 替换/释放前再次消费已验 pending，继承 `c166/c802` consumer，不展开公共 poll、walker、timer 或无种子 fd 扫描。当前不能标完整关闭接口已闭。

首个精确 UTC 为 `2026-10-24 14:15:59`；结束和墙钟见 [delivery-checks.json](../../analysis/dock-handle-review-pr06-0041-20261024/delivery-checks.json)。无主动等待或外部中断；工具等待计入墙钟，不冒充有效工时；token 由父窗遥测统计。初始默认 shell 被启动配置带到其他目录，前两次相对读取未取得任务文件且没有写入，后续均显式绝对路径及 login=false；只写独占输出。阶段证据收敛即提前交付，不凑预算。
