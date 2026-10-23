# B19：正常接收状态独立复核

2026-10-23；基线 `fad8df6`，分支 `codex/re-0041-b19`。结论：**限定接受 [B18](uart-normal-parser-b18-0041-20261023.md) 两核心的 stage/escape 状态表、原值追加及写宽度，无需纠正 B18**。本次核的是 ROM 指令和保留模型，不是协议运行记录；协议模块仍部分恢复。

## 复核边界与接口

仅复核 `a00a8330`（body `[a00a8330,a00a8582)`）和其直接 helper `a00ee934`（body `[a00ee934,a00ee96c)`）。前者沿用 poll 回调入口 `a0,a1,a2`：本体不消费入口 a0 的业务值，a1 有符号负数走既有错误记录，非负但 a2 bit0 为0直接返回；正常路径从既有 ring 取 byte 至 a0。后者的 a0 低8位是追加数据，无其他消费参数、无下游调用。两者均无已认证的业务返回码；`ret` 不代表解析成功。

`a00a83f8/8400` 构造 parser base `62fcb458`。字段为解码区 `base[0..]`、计数 byte `N@62fcb487`、stage byte `S@62fcb488`、escape byte `E@62fcb489`。`a00ee938/93e` 再独立构造同一 base。stage 名称只反映局部控制流：0等待起始，1收集解码字节，2同步校验，3校验通过后的同步处理；不是认证原始枚举名。

调用关系：parser 在 `a00a857c` 直接调用 append；在 `84d8` 调用既有 CRC `a00ee8fc(0,base,N-2)`，其内部算法不重审；成功尾在 `854c` 调用 `a00ee9ce()`，输入耗尽/外层stage3门在 `844e` 调用 `a00ee96c()`，不展开发送/队列。`8538/8546` 为间接通知，分派 ABI、槽重读与调用瞬间目标未知沿用 [B03](poll-phase-review-b03-0041-20261023.md)，不重做或固定间接目标。

## 逐项接受、纠正与未核

下表“保持”仅指所核 parser/helper 局部没有直接写，不覆盖外部调用副作用。

| B18 命题 | 结论及原指令依据 |
| --- | --- |
| S=3 门先于 escape/标记判断，且已消费 ring byte | 接受。`8432` 已取 b 至 a0，`8442` lbu S 至 a5，`8446` sb 推进读游标，`844a` 比较 a5 与 s4=3（`8418` 设置）；相等落入 `844e` 既有推进调用，再返回。不能把该门解释成正常等待字段。 |
| E≠0 优先消费转义并保留原字节 | 接受。`8486` lbu E；`848a` 非零直跳 `8572`，先 sb E=0；`8576/8578` 比较保留的旧 S 与1，非1继续取字节，是1则调用 append。`8572..857c` 没有写 a0，绕过所有标记比较；因此下一字节 A5/AA/5A 也按原值追加，没有 XOR。 |
| E=0 时 A5 同时重置计数、S/E | 接受。`848c/8490` 比较0xa5；`8494` a5=1；`8496` sb N=0；`849a` **sh** a5,+0x30(s1)，写入小端半字0x0001，即 S=1、E=0；`849e` 返回取字节。不是只写stage，也不是两个独立sb。 |
| E=0 时 AA 产生 escape，与当前S=1检查无关 | 接受。`84a0/84a4` 比较0xaa；`84a8/84aa` sb E=1；`84ae` 继续。S=1检查在其后的 `84b0/84b2`。AA自身不append，不直接改N/S。 |
| S=1 的普通非标记byte直接append | 接受。`84b2` 以旧 S 决定是否继续；`84b6/84ba` 排除5A，其余跳 `857c`，此前只改 a4/a5，a0仍为原 b。S=0普通byte（含单独5A）直接继续，不append。 |
| 尾标记后stage2/3在同一回调内同步产生 | 接受。`84be..84c4` 为已有N门；`84c8` 置a4=2，`84d2` sb S=2，随后直接CRC调用；`84ea` 不等跳原清理路径，相等经 `84f2` sb s4=3至S，再进入既有处理。因此S2/3不是按字段跨byte推进。 |
| 成功共同尾只直接清S，不清N/E/buffer | 接受。`84f6/8502/8532` 的旁路和正常通知结束都汇入 `8548`：**sb zero,+0x30(s1)**；紧接 `854c` 外部调用，`8550` 回到 `8414` 重装gate常量后继续取byte。此处不是sh，也不能将随后外部调用的副作用一并断言为不改状态。 |
| helper写的是原值byte和byte计数 | 接受。`ee942` lbu旧N至a3；`ee946/94a` 计算byte截断的新N；`ee94e` 的厂商 `th.srb a0,a5,a3,0` 写 `base[旧N]=low8(a0)`，`ee952` sb 新N。编码字段和既有SLEIGH单byte语义均另核，见下文。 |
| 保留原清理宽度，不擅自统一复位 | 接受。仅静态记录：尾标记原N门转 `856c` sb S=0；CRC不等经日志到 `8568/856c` 分别sb N/S=0；append原分支到 `ee95e/962` 分别sb N/S=0，均不直接写E。未构造相应输入、未回放或审计长度。 |
| 初始化、全局写入者、真实时序、外部副作用与完整模块 | 未核且保持未知。B18没有以这些内容证明局部状态表，本次不扩大验收范围。 |

没有需要修改的地址、写宽度、优先级或正常阶段次序。普通数据/escape跨poll保留的说法限定为本体局部：输入耗尽经 `844e` 调用外部推进，本体没有在该路径直接清N/S/E；不据此断言整个调用链不变。

## 复核后的正常局部状态表

`b` 是已取出的byte；以下按判断先后排列。S2/S3的正常产生与消费是同步控制流，不能当作等待后续输入的独立字段状态。

| 条件 | 直接动作 |
| --- | --- |
| S=3 | 已取b后调用既有推进并返回；不解释b。 |
| S≠3，E≠0 | E=0；旧S=1则append(b)，否则继续。 |
| S≠3，E=0，b=A5 | N=0；半字写(S,E)=(1,0)；继续。 |
| S≠3，E=0，b=AA | E=1；继续。 |
| E=0，S≠1，其他b | 继续。 |
| E=0，S=1，普通非标记b | append原值byte；继续。 |
| E=0，S=1，b=5A，通过原N门和既有CRC | S=2→调用CRC→S=3→按既有条件同步处理→仅S=0→既有发送启动→继续。5A不append。 |

关键伪代码仅压缩所核结构，不展开已有CRC和分派ABI：

```c
// b已从原ring取出，读游标已提交；所有外部调用保留其副作用边界。
old_s = load_u8(base + 0x30);
if (old_s == 3) { existing_send_progress(); return_poll; }
if (load_u8(base + 0x31)) {
    store_u8(base + 0x31, 0);
    if (old_s == 1) append_original_byte(b);
    continue_ring;
}
if (b == 0xa5) { store_u8(base + 0x2f, 0); store_u16(base + 0x30, 1); continue_ring; }
if (b == 0xaa) { store_u8(base + 0x31, 1); continue_ring; }
if (old_s != 1) continue_ring;
if (b != 0x5a) { append_original_byte(b); continue_ring; }
// 原N门及非成功清理保持B18记载；此处仅表示正常CRC相等路径。
store_u8(base + 0x30, 2);
existing_crc_check();
store_u8(base + 0x30, 3);
existing_conditional_response_handling();
store_u8(base + 0x30, 0); // 不附加N/E清理
existing_send_start();
continue_ring;
```

## 来源与实际静态验证

复用主仓库只读 `reverse/analysis/usb-interface-ota-0041-20261023.json` 中两个保留函数，不开启REA数据库/会话。parser Evidence ID为 `ev_6f900403de24d247461a1e302c564c71481c3d43d481acdc83bbb716318e1159`，原记录 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-067.json`；append为 `ev_245cff516eba00a8581e3daf51b32c1f5af19c347dde29f774c12b4c5be1c7d9`，原记录 `whole-rom-usb-crc-20261023-001.json`。历史profile为 `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`，语言沿用 `RISCV:LE:32:ap01thead2`。没有新哈希或复制清单。

本任务自建 [verify_review.py](../../analysis/uart-normal-parser-review-b19-0041-20261023/verify_review.py)，只读主仓库ROM `roms/0041/ap01-1.0.2_0041.bin`，按VA−`9ffff000`映射比对保留body原字节，**从ROM半字前缀位独立推进指令长度**，再与保留指令地址交叉核对。Capstone 5.0.7独立解码203条普通RV32+C指令，另核1条厂商指令字段；35项指定操作数、21项静态控制流目标通过。额外直接拆7条S型store的opcode、funct3、rs1、rs2与位移，分别确认byte/halfword写宽度，未仅信反编译的合并字段。

厂商指令 `ee94e` 字段为opcode=0x0b、funct3=5、op2731=0，源寄存器x10(a0)、base x15(a5)、index x13(a3)、shift=0。只读核对 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc:6442`：`th.srb`计算 `ea=rs1+(rs2<<shift)`，执行 `*[ram]:1 ea=rd:1`，不回写base。此模型交叉核验支持原值单byte追加；不是对完整厂商ISA或模型正确性的认证。

实际执行 `python -B reverse/analysis/uart-normal-parser-review-b19-0041-20261023/verify_review.py`，输出 `static_review_passed`、204指令、35精确检查、21控制流目标。逐条原字节/文件偏移/独立解码/保留provider文本、store编码字段、厂商语义摘录和来源保存在 [review-evidence.json](../../analysis/uart-normal-parser-review-b19-0041-20261023/review-evidence.json)。手工沿原指令核寄存器生存期、判断优先级、所有stage/escape局部写入和成功共同尾。

未运行B18或历史UART脚本，没有固件执行、输入生成/回放、设备或外部服务连接、缺陷验证、长度审计、共享数据库使用、ROM/模型/安全检查/生产代码修改。适用工作树及reverse目录未发现AGENTS.md；遵循本树滚动管理共同规则与B19任务书。

原路径 `PogoPinMng/EsUnitProtocol.c` 及日志线索只支持模块归属；精确原始源码/版本/编译选项未知，本次未新增开源认证。事实为指令、地址、宽度、局部顺序；阶段名/字段名是分析推断；真实通信时序、初始化、并发/回调副作用、全部状态写入者和MCU内部实现仍未知。恢复程度为两核心局部限定验收，不能扩大为全协议或全ROM完成。

下一小任务建议：限定查明 `62fcb488/489` 的一个初始化直接写入点，核其参数/写宽度及调用位置；不扩展完整队列、OTA或异常输入调查。
