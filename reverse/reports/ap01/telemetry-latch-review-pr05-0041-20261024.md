# P-R05：P-05 raw latch 写入与条件复位合并非作者复核

**接受：可独立使用的写入/条件复位阶段已闭合；完整消费接口未闭。** P-05 的 cmd50 置位、cmd55 缓存门与全半字清除顺序可以用于重建。没有发现须改作者产物的技术错误。不能将此半字命名为告警、成功、待确认或端口故障，也不能把清除路径当作已找到消费者。

认领 P-05 下的 P-R05，复核者 `/root/pr05`，非作者；作者已停止。基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`，独占 `.worktrees/batch-20261024-p/pr05`，只写本报告及同名 analysis。先读主树 reverse-design、管理顶部批次 P 与 P-05 行；不通读历史。使用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，只复用留存和必要离线原字段；未调用共享 REA、切换模型或建立分析数据库。

## 继承结论

[P-05 作者报告](telemetry-latch-p05-0041-20261024.md)及其 [static-evidence.json](../../analysis/telemetry-latch-p05-0041-20261024/static-evidence.json)为本轮验收对象。父窗已验 P-02/P-R02 的 cmd50 writer 前提：`u16(record+4)&0x6000==0x6000` 后 OR 写 `u16[0x62fcb50a]`；本轮只核该前提和清除段的衔接，不重做功率、历史、item/total 通知。

原件只读主仓 `roms/0041/ap01-1.0.2_0041.bin`，长度 6,769,704B；既有 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，地址映射 `file_offset=VA-0x9ffff000`。本次确认长度和必要窗口字节，没有重新计算全 ROM 摘要。

主 dispatcher 来源为 `reverse/analysis/buzzer-backlight-0041-20261023.json#/functions[address=0xa00a8582]`；Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`，Ghidra 12.1.4，`RISCV:LE:32:ap01thead3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`。独立核其 Evidence ID/profile 与原来源 `evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json#/records/2` 一致。原来源既有摘要 `689b060f96eaba167291ecf78c8998e5aea590555e793cac735d448265d1d385` 沿用，不新建摘要清单。

缓存 helper 的同步通知合同继承 [UART 普通应答](uart-response-0041-20261023.md)、[B02](poll-phase-writer-b02-0041-20261023.md)/[B03](poll-phase-review-b03-0041-20261023.md)；必要 helper 指令复读自 `reverse/analysis/uart-retry-receive-0041-20261023.json#/functions[address=0xa0191652]`，Evidence `ev_3a861f94ddb2b4481b6d96b4f46d593f35e2729ecb9022aa64949e92b607615c`，profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。这是另一份 helper 留存的来源标识，未将其误写成 dispatcher profile。比较/复制内部、allocator、关闭复位与轮询选择器合同均不重开。

## 本轮复核或纠正

| 合同与判断 | 原字段/控制流核对与结果 |
| --- | --- |
| cmd50 只在两位均置时 OR latch | 接受。`9212 LHU record+4`，`9216 C.LUI=0x6000`，`9218 AND`，`921c BNE→9238`。`9220/9224` 构造 `0x62fcb50a`，`9228 LHU`，`922e SLL`，`9232 OR`，`9234 SH`；RV32 可变移位只用低5位，SH 只保留低16位。未满足条件不在此段清对应 bit。 |
| cmd55 路由和 helper 参数 | 接受。`8602 LI 0x55; 8606 BEQ→88f6`。`88f6..8904` 为 `cache_helper(0x62fcb004,24,s0-0x50)`；入口 `85a0/a4/a8` 的 descriptor 保存沿 B03 已验前提。不把 helper 返回值当成功条件。 |
| 基础信息有效门 | 接受其机器含义。`8930/8934` 分别 LHU 缓存 `b014/b016`，OR 后 `893e C.BNEZ→8950`；零进入既有另一分支。`893a` 厂商原字 `0b37073c` 保留，字段为 rd=rs1=a4、上界15/下界0；语义沿匹配 profile 的 extu 留存，未加载/执行模型。两个 LHU 的 OR 本已只占低16位。这里的“有效”只是这个非零门，没有额外协议成功含义。 |
| count=0xff 跳过清除 | 接受。`8950` 从 `b01a` 取 byte，`895a` 先写 `b50c=1`，`8966 BEQ→8a22` 跳过 `8a1e`。阶段写先于 ff 判断，不能颠倒。 |
| 保存与第一次重读 | 接受。`898e SB saved_count→b01c`，`8992` 日志 call，`8996 LBU b01c`，`899a C.BEQZ→8a22`。决定跳过清除的是日志之后的这次重读；不能折叠为原 payload/count 快照。 |
| 后续重读与 mask loop | 接受。第一次非零后经过三缓存指针检查/必要分配 callsite，`89e0` 再次 LBU b01c 至 a6；`8a06 BLTU→8ab4`、有限 byte count 的递增 loop，`8ac8` 返回 `8a06`。循环完成后经过 `8a0a/0e/10` 到 `8a12`，没有新增 latch 条件。第二次 count 变0可直接走到清除；不据此声称运行时会变化或存在锁。 |
| 清除的宽度与顺序 | 接受。`8a1a LUI 0x62fcb; 8a1e SH zero,0x50a(a5)`，无读取旧 latch 的门，清整个半字，再到 `8a22` 既有重建。正常返回及前置内存有效是该静态路径的必要限制；不认证 allocator 的异常/不返回行为。 |
| 通知早于清除 | 接受条件措辞。helper 先比较/复制，变化且槽非空才在 `a01916d0` 同步间接调用；`16c0/16c8/16cc` 得 `(descriptor.command+0x20)&255`，本入口对应0x75。调用在 `8904` 内发生，返回后才有上述读点与 `8a1e`，所以0x75不是 latch 已清确认。未证明本次一定通知或回调无副作用。 |
| 读者及引用覆盖 | 接受。dispatcher 原记录精确目标引用仅 `8a1e WRITE`、`9228 READ`、`9234 WRITE`；9228 load 供 OR 写回，不能当业务消费。只核该 body/provider recognized 集，不推广为全局 xref 全集。 |

[独立脚本](../../analysis/telemetry-latch-review-pr05-0041-20261024/review_static.py)使用 Python 标准库；没有运行、导入或复制执行作者脚本。实际输出 **PASS，5窗408B，221项断言**，结果见 [review-evidence.json](../../analysis/telemetry-latch-review-pr05-0041-20261024/review-evidence.json)。221包含逐指令原字节/偏移/保留汇编一致性、原字段、来源和账目一致性，不代表221个功能或完整独立反汇编器。

作者的33项检查逐项登记：其中30项从 ROM/旧留存独立重算，结果一致；3项是 pass3/4/5 精确地址文本无命中，只检查作者记录及限定表述，按指令没有重新搜索这些文本。五窗分别为 `[a00a85ac,a00a85cc)`、`[a00a8602,a00a860a)`、`[a00a88f6,a00a8a2a)`、`[a00a8ab4,a00a8aca)`、`[a00a9212,a00a9238)`；均与作者证据及前置旧留存逐字节一致。另手工核所列相关寄存器生存期、局部 loop 回边和到清除的直达次序；不是执行、状态枚举或 ISA 模拟。

initializer `a005a736` 的精确目标 metadata 无命中，以及 selector `a0191746`/reset `a00a5558` 的保留伪代码无明示地址，已限定复核；只能说明相应记录/直接文本范围，不排除间接 callee 副作用。没有重跑全目录负搜，也没有把这些阴性证据用于证明全局无消费者。

## 真正新增

非作者验收新增为0个原厂功能；本轮新增是独立验收依据。对重建程序可用的合同是：匹配的 cmd50 record 可 OR 累积此 raw 半字；cmd55 在缓存基础信息非零、保存 count 非 ff、日志后 b01c 重读非0的路径中，正常完成必要调用及 loop 后把整个半字清0。它是写入/条件复位阶段，不是完整消费接口。

本半字是固定 RAM 状态；未恢复动态所有权转移或归还 API。cmd50 RMW 与 cmd55 全清之间的并发、重入、线程安全、超时、取消、关闭是否清除均无新增证据。原厂事实限于字节、读写、分支及调用次序；“raw latch”和“条件复位阶段”是对已见访问模式的分析命名。未新增库来源认证或开源替代结论。

## 未闭精确边与交付

**断边保留：`u16[0x62fcb50a]` 经 cmd50 OR 后的独立业务读取者 → 是否发请求/形成可见状态 → 确认/清位 → 专属通知。** 已知 cmd55 全清不能替代这条消费链。不能推出“每次cmd55都清”“断连自动清”“某record位归零则清”“置位后必在某时限清”。

后续只有在取得隔离、匹配0041/ap01thead3的已有数据库或精确 xref 留存时，才从本半字（必要时含第二字节）的真实独立 READ 追到业务输出；没有这样的新输入则保持 raw/未知，不扩扫所有 flags 或 driver。本轮无技术返工要求；建议管理行将本差集标限定接受，完整消费接口继续未闭。

独占交付仅本报告、`review_static.py`、本地忽略的 `review-evidence.json`；忽略 JSON 必须随报告原路径保存。未修改主树、作者产物、ROM、生产配置、分析器或模型，未连接设备/外部服务，未运行固件、网络、SIM/QEMU、历史回放、构建，未提交推送或创建代理。

首次可得开始 `2026-10-24 14:12:46 UTC`；结束与格式检查见末尾。预估约30分钟，本题在有界证据已足够接受且无独立消费者新种子时提前收敛，不凑时长。没有主动等待或任务中断；实际墙钟包含工具读取与检查，未测有效工时。token由父窗统计。本机 shell 初始化忽略 workdir 并改变 cwd，前两次只读相对路径失败；随后固定显式 Set-Location，所有写入均在独占树指定路径。

交付结束 `2026-10-24 14:16:33 UTC`，墙钟约227秒（3分47秒）；链接（主树继承回退）/JSON解析/无尾空格及末尾换行检查通过，`git diff --check`通过。所有新产物含 ignored JSON 均在独占范围，未提交。
