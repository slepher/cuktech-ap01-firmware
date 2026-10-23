# B18：正常 UART 接收阶段与转义标志

2026-10-23；管理基线 `319dbdf`，分支 `codex/re-0041-b18`。限定恢复 `a00a8330` 与其直接追加 helper `a00ee934` 两个函数。结论：接收 stage 是 `0` 等待起始、`1` 收集解码字节、`2` 同步校验、`3` 校验通过后的同步处理；escape 是独立 byte，`AA` 置位，下一字节先清标志，并在 stage 为1时原样追加。没有 XOR 或其他还原运算。阶段名称是依据读写顺序赋予的分析名，不是原源码枚举。

先检索本树全部 `reverse/reports/ap01` 中的函数地址/EsUnitProtocol 引用，核对 [UART/OTA 报告](usb-interface-ota-0041-20261023.md)、[历史接收专项](uart-retry-receive-0041-20261023.md)和 [B02/B03 分派局部](poll-phase-review-b03-0041-20261023.md)：已有逐字节、CRC、追加和分派描述，但未给完整 stage/escape 状态表。本报告补该缺口；历史专项的缺陷调查、回放和长度审计不属于本次工作，未运行其脚本。

## 接口、字段与调用边界

| 项目 | 指令证据与局部合同 |
| --- | --- |
| `a00a8330(a0,a1,a2)`，body `[a00a8330,a00a8582)` | poll 回调；a0 在本体无业务消费，a1 有符号小于0时只记录错误并返回；否则 a2 bit0 为0直接返回。正常接收路径每次调用读取 helper `a003f6a2(fd,&byte,1)`，随后消费已有环形区。不认证其他 poll 位的含义。无显式业务返回值写入，不能把残留 a0 当解析成功码。 |
| `a00ee934(a0)`，body `[a00ee934,a00ee96c)` | a0 低8位为当前解码字节，无其他参数、无业务返回。`a00a857c` 直接调用；helper 没有下游调用。 |
| `62fc91b4 / 62fc91b5 / 62fc91b6` | 环形读取/写入游标 byte 和字节区；`a00a8422..8446` 先取一字节并推进读游标，再检查 stage。只记录输入到 parser 的顺序，不恢复完整环形区/驱动合同。 |
| `62fcb458` | 解码区 base，s1 由 `a00a83f8/8400` 构造；首解码字节在此，cmd/length 分别在 `+1/+2`。首字节业务语义未由接收代码认证。 |
| `62fcb487 = base+0x2f` | 解码计数 byte：起始标记清零，append 读、增、写；成功尾处理不直接清零。 |
| `62fcb488 = base+0x30` | stage byte，不能与传输状态 `62fcb2f0` 混用。 |
| `62fcb489 = base+0x31` | escape byte；`a00a8486` 读、`84aa` 写1、`8572` 写0；`849a` 的半字写同时写 stage 和 escape。 |

CRC `a00ee8fc(0,base,count-2)` 的算法和返回合同沿用 [UART/OTA 已核 CRC](usb-interface-ota-0041-20261023.md)，不再恢复其函数。`a00a84dc..84e8` 将最后两字节按低字节在前组合后比较。匹配响应的复制与两次 callback 参数、重读槽顺序沿用 B03，本次只核 stage 写入与此调用位置的关系。成功尾调用 `a00ee9ce()`，环形区为空/外层 stage3 门调用 `a00ee96c()`；只引用已有发送合同，不向它们内部或队列扩展。

## 正常字节转换与状态顺序

下表按实际优先级排列。`S` 为 stage，`E` 为 escape，`N` 为计数，`b` 为已取出的原始 byte；“保持”只表示本局部没有直接写入，不约束同步 callback 的副作用。

| 先决条件/当前 byte | 动作及下一阶段 | 原指令 |
| --- | --- | --- |
| 已取字节，S=3 | 不解释该 byte，调用既有发送推进 `a00ee96c`，返回 poll 回调。正常尾路径会在继续取字节前先清 S，因此不能把此门写成正常的“等待下一字段”。 | `8442..8452` |
| S≠3，E≠0，任意 b | 先 E=0；旧 S=1 时 append(b)，否则不追加。A5/5A/AA 均走这一条，因此被转义的标记只作为原值数据。 | `8486..848a → 8572..8580` |
| S≠3，E=0，b=A5 | N=0；半字写 `0x0001` 至 `62fcb488`，即 S=1、E=0；不追加 A5。 | `848c..849e` |
| S≠3，E=0，b=AA | E=1，S/N 保持；不追加 AA。本条在 S=1 检查之前。 | `84a0..84ae` |
| E=0，S=1，b 为普通非标记 byte | append(b)，S 维持1（helper 自身的原有计数复位分支另见下）。 | `84b0..84ba → 857c` |
| E=0，S=1，b=5A，N>4 | S=2 后调用 CRC。CRC 相同后 S=3，再按原有活动传输/命令条件决定是否分派；两条成功后处理路径共同 S=0，调用 `a00ee9ce`，继续消费输入。结束标记不追加。 | `84be..84f2`、`84f6/8502 → 8548`、`8548..8550` |
| E=0，S=0，普通 byte（包括单独5A） | 不追加、不改变 stage，继续取字节。 | `84b0..84b2` |

正常完整帧的局部阶段线为：`A5 → S1 → 解码字节及可选 AA+字节 → 5A → S2/CRC → S3/同步响应处理 → S0`。S2 和 S3 的生产和后继在同一 poll 调用内完成，不是每接收一个字段推进一次的枚举。普通字节、AA、解码计数均可跨 poll 调用保留；环形区耗尽到 `844e` 不直接清 parser 字段。

为准确保留原始清理，仅记静态分支：尾标记且 N≤4 在 `856c` 只清 S；CRC 不同经日志后在 `8568/856c` 清 N/S；两者均没有在这里清 E（这些路径进入时 E 已为0）。CRC 相同的 `8548` 只 `sb zero,+0x30`，不清 N 或 E，不清解码区。不得根据反编译的合并半字变量，把这些 byte 写误写为统一复位结构体。这里不构造上述分支的输入、不运行路径或研究缺陷。

追加 helper 在 `ee942` 取旧 N，`ee94e: th.srb a0,a5,a3,0` 写 `base[旧N]=low8(a0)`，`ee946/94a/952` 将 `(N+1)&255` 存回。`ee956..966` 保留原有“新 N 大于0x2f则 N=0、S=0”的分支；不写 E、不擦 buffer。这里只记录原指令，未做长度审计或输入验证。

## 可读伪代码

以下仅展开两核心函数的接收局部。外部调用仍是已有合同边界，所有 `return_poll` 均无业务返回码；callback 引起的状态改变不能假定不存在。

```c
// 输入来自原有 ring；a1<0 或 !(a2&1) 的外层门直接返回。
while (ring_has_byte()) {
    uint8_t b = ring_take_byte(); // 在 stage3 门之前已经推进游标
    uint8_t old_stage = stage;
    if (old_stage == 3) { send_progress(); return_poll; }
    if (escape != 0) {
        escape = 0;
        if (old_stage == 1) append_byte(b);
        continue;
    }
    if (b == 0xa5) { count = 0; store_u16(&stage, 1); continue; }
    if (b == 0xaa) { escape = 1; continue; }
    if (old_stage != 1) continue;
    if (b != 0x5a) { append_byte(b); continue; }
    if (count <= 4) { stage = 0; continue; }
    stage = 2;
    if (existing_crc(0, decoded, count - 2) != trailing_crc_le(decoded, count)) {
        existing_crc_log(); count = 0; stage = 0; continue;
    }
    stage = 3;
    existing_matching_response_dispatch(); // 两次同步通知，槽重读合同沿用 B03
    stage = 0;                           // 没有新增 count/escape 清理
    existing_send_start();               // a00ee9ce
}
send_progress();                         // a00ee96c；return_poll

void append_byte(uint8_t b) {            // a00ee934
    uint8_t old = count;
    decoded[old] = b;
    count = (old + 1) & 255;
    if (count > 0x2f) { count = 0; stage = 0; }
}
```

## 来源、证据与实际验证

保留 REA 来源是主仓库只读 `reverse/analysis/usb-interface-ota-0041-20261023.json`：parser 的 Evidence ID `ev_6f900403de24d247461a1e302c564c71481c3d43d481acdc83bbb716318e1159`、原记录 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-067.json`；append 的 Evidence ID `ev_245cff516eba00a8581e3daf51b32c1f5af19c347dde29f774c12b4c5be1c7d9`、原记录 `whole-rom-usb-crc-20261023-001.json`。两者外层 profile 均为 `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`，语言来自既有 `RISCV:LE:32:ap01thead2`。本次复用历史身份，不新制哈希/复制清单。

[实际静态检查脚本](../../analysis/uart-normal-parser-b18-0041-20261023/verify_static.py)读取主仓库 ROM `roms/0041/ap01-1.0.2_0041.bin`，依已知 VA−`0x9ffff000` 映射逐字节比对两份保留 body 原字节，按 provider 每条指令地址独立用 Capstone 5.0.7 RV32+C 解码203条普通指令并核连续长度，核16项关键加载/存储操作数和13项条件/调用目标。厂商 `th.srb` 另以原字编码检查 opcode/funct3/高位、源/基址/索引/shift 字段；其单 byte 写 `rs1+(rs2<<shift)` 语义对照保留 `processor/data/languages/ap01thead2.sinc:6442`，未以 Capstone 缺解码代替 NOP。此复核不等于认证整个 ISA 模型。

实际执行 `python -B reverse/analysis/uart-normal-parser-b18-0041-20261023/verify_static.py` 成功，结果 `static_instruction_checks_passed`。两函数逐条原字节、provider 与独立解码文本、证据来源以及选定控制流目标保存在 [instruction-review.json](../../analysis/uart-normal-parser-b18-0041-20261023/instruction-review.json)。手工核对字节/半字写宽度、stage/escape 判断优先级、a0 的 append 参数生存期及成功清理与返回顺序。未打开/改动共享或私有 REA 会话/数据库；没有固件执行、输入回放、设备/服务连接、生产/ROM/模型修改。

`PogoPinMng/EsUnitProtocol.c` 路径在 [whole-ROM 引用恢复](whole-rom-0041.md)及本函数 CRC 日志参数 `a00a855e` 指向的 `a02693f4` 中提供私有模块归属线索；poll 外层也引用 PogoPinMng/UartComm。函数名和阶段名均为分析恢复，原始源码、确切版本和编译选项未知，不因路径而认证开源来源。保留伪代码有移除 `a00a846e` 不可达块警告；本次以原始指令为准，未重做输入填环语义或将反编译当原源码。

两核心的正常状态/escape 直接生产消费已恢复；完整驱动、其他 parser 字段全局写入者、同步 callback/并发修改、初始化和销毁、真实通信时序及 MCU 内部实现仍未知，协议模块继续为部分恢复。下一个小任务建议：独立逐指令复核本报告两核心的状态表与清理宽度，不扩 OTA/队列或历史异常调查。
