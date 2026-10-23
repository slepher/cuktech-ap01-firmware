# 0041 一次排队命令消费：槽选择、活动副本与释放时点

2026-10-23，B20，基线 `b105687`。**局部正常合同已恢复，模块仍为部分恢复。** `a01915bc` 每次最多消费一个槽：按槽地址顺序挑首个占用项，活动传输空闲才复制命令到活动区；调用发送启动器返回后，才将原槽占用 byte 清零。清槽不取决于发送成功，也没有向调用者返回业务成功状态。

应用 REA skill，复用保留 dossier 并直接只读核对原 ROM；没有打开共享 REA 会话、数据库或执行历史脚本。原件与历史证据身份沿用 [USB interface OTA 报告](usb-interface-ota-0041-20261023.md)，不新增哈希或复制清单。当前静态证据不能认证原始源码、厂商库来源/版本或整机行为。

## 前序覆盖与本轮边界

先检索已有报告及分析中 `a01915bc`：USB/OTA 报告已有“固定槽顺序、空闲搬运后清槽”的概述；[dock 报告](dock-presence-polling-0041-20261023.md)已有四槽初始化/生产上下文；UART retry 报告已有 `0x24` 调用消费器的说明；B18/B19 是正常解析与回调顺序。本轮补明复制布局、调用 ABI、复制后重读状态、发送启动器调用与原槽清理顺序，不重做这些上层链。

仅完整解码两个核心函数 `a01915bc`、直接依赖 `a00ee9ce`。另一个直接调用 `a000589c` 只核调用点三参数与目标，为已有 memcpy 合同边界；未重新恢复其函数体。发送启动器的两个 callee 保留为外部边界，不扩整帧发送、重试/超时失败、完整 OTA、长度审计或输入验证。

## 证据与地址

[指令证据](../../analysis/queued-command-consume-b20-0041-20261023/instruction-evidence.json)保存 70 条原字节/文件偏移/独立 Capstone 解码与历史 Ghidra 文本、27 个精确指令断言、4 条原始编码调用目标核对。地址映射 `file_offset = VA - 0x9ffff000`，ROM 固定为主仓库 `roms/0041/ap01-1.0.2_0041.bin`。

| 函数范围（含末字节） | 保留 Evidence ID | 历史 dossier |
| --- | --- | --- |
| `a01915bc..a0191651`，150 B | `ev_ad6980ba30e890b1edbd867ee513c9b556d5bd335ba0e9cb745945b2964585b9` | `whole-rom-usb-closure-20261023-006.json` |
| `a00ee9ce..a00eea07`，58 B | `ev_313ec1bbe3f041925d5f81e95f82eac99ccabf8b54ebeebb31fe2ad1b0536a2f` | `whole-rom-usb-worker-20261023-002.json` |

dossier 原位置在主仓库 `evidence/rea-0041-20261017/evidence/`；本轮读取既有 [USB/OTA 机器记录](../../analysis/usb-interface-ota-0041-20261023.json)，逐函数 raw_ranges 与原 ROM 对比相等。保留 profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`，其来源状态沿用既有记录，不将本轮 Capstone 结果重贴旧 Evidence 身份。

## 数据布局与所有权

四个固定槽基址为 `62fcb354 / 62fcb384 / 62fcb3b4 / 62fcb3e4`，步长 `0x30`。以下是分析结构，不是恢复到的 C 类型：

```c
struct QueuedSlotView {       // 48 B；生产布局沿用已有合同
    uint8_t occupied;        // +0；非零即被消费器选中
    uint8_t command;         // +1
    uint8_t length;          // +2
    uint8_t payload[45];     // +3；大小来自已核槽步长/布局
};
// 活动区：state@62fcb2f0, attempts@b2f1, wait@b2f2,
//         command@b2f3, length@b2f4, payload@b2f5。
```

事实：`a01915d0..a01915e6` 依次检查四个 occupied byte，第一个非零项胜出，四槽全空直接到清栈返回；`a0191638/163e/1648` 的选择落点分别把 s1 设为前三槽，第四槽在 `a01915e8..15ec` 选择。每次只走一个槽，没有循环继续取下一项，没有移动其他槽内容或更新队首索引。因此这是固定槽优先次序，不能视为保持到达顺序的独立 FIFO。

`a01915f8..15fc` 读取活动 state，非零立即返回；该路径不复制、不清槽。状态0才读取 slot.length，在 `a01915fe..1614` 形成 `a0=62fcb2f3, a1=slot+1, a2=zero_extend(slot[2])+2` 并调用 `a000589c`。被复制的是 command、length 和 payload 字节，occupied 不在源范围内；目的区不保存槽指针。这里仅解释正常格式的字段搬运，不进行长度审计。

所有权推断：正常顺序下，槽在复制及发送启动器调用期间仍标为占用；活动区持有独立字节副本，随后原槽可被生产者重用。消费器没有分配、释放 payload 指针，也没有清零槽的 command/length/payload。清 occupied 是逻辑释放槽，不是清除残留数据。这只证明本函数的静态读写顺序；没有锁/原子操作证据，不能补造并发安全保证。

## 两函数 ABI、调用和返回

`a01915bc(void)` 没有使用传入寄存器作为业务参数。`a01915bc..15c6` 建16 B栈帧，保存 ra/s0/s1/s2，`a019162c..1636` 全路径统一恢复并返回。复制函数返回值没有被消费。`a0191618` **在复制后重新加载 state**，仅仍为0时写1；然后无论此次是否写1，都调用 `a00ee9ce`。`a0191628` 在该调用正常返回后无条件清所选 occupied byte，再走同一清栈返回。没有根据 a0 判定是否清槽，也没有显式构造“消费/发送成功”返回值；伪接口应按 void 使用，不能给调用者增加成功回执。

`a00ee9ce(void)` 同样建16 B栈帧、保存并恢复 ra/s0/s1/s2。`a00ee9e2..9e8` 将 state 保存在 s2，只有值1才依次调用构帧边界 `a01a4ff8()`、写出推进边界 `a00ee96c()`；两者正常返回后，`a00ee9f4` 将保存的1写 attempts，`a00ee9f8` 将 wait 清0。没有使用两个 callee 的返回值决定这两次存储。state非1时仅恢复返回。本函数本身不保证传输完成，不直接清所选队列槽；下游 state 变化保留为已有发送合同边界。

四个调用地址通过 ROM 编码独立计算：`a0191610/1614` AUIPC/JALR→`a000589c`；`a0191624` JAL→`a00ee9ce`；`a00ee9ec` JAL→`a01a4ff8`；`a00ee9f0` JAL→`a00ee96c`。这两函数无厂商扩展或未知指令，未使用反编译参数省略作为 ABI 依据。

```c
void try_consume_one(void) {
    QueuedSlotView *slot = first_occupied_in_address_order();
    if (slot == NULL) return;
    if (state != 0) return;
    memcpy(active_command_address, &slot->command,
           (unsigned)slot->length + 2);
    if (state == 0) state = 1;  // 保留复制后重读
    start_if_prepared();
    slot->occupied = 0;          // 正常返回后释放；不检查业务成功
}

void start_if_prepared(void) {
    uint8_t saved_state = state;
    if (saved_state != 1) return;
    build_frame();             // a01a4ff8，边界
    advance_write();           // a00ee96c，边界
    attempts = saved_state;
    wait = 0;
}
```

## 实际静态验证、恢复程度和后续

执行本任务新建的 [verify_static.py](../../analysis/queued-command-consume-b20-0041-20261023/verify_static.py)：`python -B reverse/analysis/queued-command-consume-b20-0041-20261023/verify_static.py`。两段原字节与保留 raw_ranges 完全相等；从 ROM 前缀独立切分并解码70条指令，覆盖两个函数全部208 B；27项关键参数/门控/清理/返回指令断言及4条原编码调用目标全部通过。Capstone 5.0.7 输出分支相对位移，证据同时保留 Ghidra 绝对目标，断言明确按 PC 加位移解释，不把文本差异当控制流差异。验证最初因将相对位移期待为绝对地址而失败，修正验证脚本表示后通过；未修改原 ROM 或任何模型。

已回答：一次消费的字段布局、固定选择顺序、忙/空返回、复制三参数、复制后重读、发送启动器条件/调用顺序及槽释放时点。部分回答：a000589c 仅沿用复制语义与核实调用点；发送启动器下游两函数本轮不重新恢复。未知：完整并发/回调生命周期、下游传输结果、全部状态写入者与来源版本。正常返回只说明函数局部流程返回，不证明线缆或底座已接受命令。本轮没有新增已认证开源排除，也不宣称 UART/OTA 或全 ROM 完成。

建议后续小任务 B21：独立逐指令复核本报告两个函数的正常 ABI、复制后重读和清槽顺序，最多一个必要直接依赖；不新增 OTA/超时或长度分析范围。
