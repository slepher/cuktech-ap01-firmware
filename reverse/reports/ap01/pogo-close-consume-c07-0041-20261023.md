# C07：PogoPin 四组关闭登记之后的局部退出边

2026-10-23；分支 `codex/re-0041-c07`，基线 `c3797ab`。**有界结论：现有容器的四组登记之后，没有直接回到已恢复 pending 消费片段的局部控制边；后续为清理尾部和返回。** 这不证明 callback 不会执行，也不证明 timer 已停止。局部恢复完成，待独立技术复核；完整生命周期仍部分恢复。本文伪代码为分析者表达，不是原始源码。

## 回答的问题与范围

任务只问已有容器 `a005a736` 的四组 PogoPin 关闭登记之后，是否有一条直接控制流回到 [C05](pogo-close-dispatch-c05-0041-20261023.md)/[C06](pogo-close-dispatch-review-c06-0041-20261023.md) 已恢复的 `a005c166/c802` pending 消费局部。本次选定同一容器内三段，共590 B：已有消费及其相邻条件 `c166..c19d`、消费体和退出选择 `c802..c83d`、四组登记至返回 `c8f8..cad1`。不重新认证容器全部函数边界、入口参数或整体业务返回，不恢复完整 loop、MiIot 清理、timer 或下层库。

结论分两层：

- **指令事实：**四组条件登记位于 `c90c/c93e/c974/c9aa`；从该尾部的正常调用返回位置继续，六个局部分支均向前，十二个 JAL 均为调用（目标只含日志 `a008b51a` 与关闭登记 `a009fb96`），五个 AUIPC/JALR 配对也均为调用。尾部恢复保存寄存器后于 `cad0` 执行 `C.JR ra`；没有直接跳往 `c166/c802` 或其他早前容器块。
- **有界推断：**这条尾部没有新提供一次已恢复 pending 消费机会。各 callee 若正常返回，局部控制流最终离开容器；callee 内部、副作用、外部调用者重入/再次消费和实际调度仍未知。因此不能把“未见局部回边”写成“关闭永不完成”或缺陷结论。

## 证据与原指令合同

[instruction-evidence.json](../../analysis/pogo-close-consume-c07-0041-20261023/instruction-evidence.json) 保留每条原指令地址、原字节、普通 RV32/RVC 解码、8个32位条件分支位域核对、5个 AUIPC/JALR 目标重建和尾部调用表。[check-static.py](../../analysis/pogo-close-consume-c07-0041-20261023/check-static.py) 仅静态读取主仓库 `roms/0041/ap01-1.0.2_0041.bin`，VA 基址 `9ffff000`，只写本任务 analysis 目录。

已有完整容器证据为 [retained-initializer.json](../../analysis/factory-test-0041-20261023/retained-initializer.json)，Evidence ID `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`。本次核其保留 raw ranges 与 ROM 一致；只解释选定局部，没有把完整反编译文本视为语义证明。沿用已有 ROM 身份记录，没有新增哈希清单。适用共同任务书、REA 技能已读；检查本树和 reverse 的适用目录以及主仓库对应目录，未发现 AGENTS.md。

| 函数/局部 | 参数、返回、调用和指令事实 |
| --- | --- |
| `a005a736` 已有消费片段 `c166..c19d` / `c802..c80d` | 沿用已验收 s1=loop 局部合同。`c166` 从 loop+d4 取 head 到a0；`c16a` 清head；`c16e` 非空转 `c802`。`c802` 先读 next@handle+28 到s5；`c806` 调 `a009f524(a0=handle)`；`c80a/c80c` 回非空测试。空head从 `c16e` 落到 `c172`，调用 `a0098b60(loop)`、`a009d304(loop)`；其副作用未展开。`c17e..c198` 所见 loop+4、+10、+24及+d4条件不满足时转 `c830`，否则 `c19c` 跳早前 `beac`。仅描述这些直接边，不恢复目标块。 |
| 同容器退出选择 `c80e..c83d` | `c80e` 读 word(loop+18)；`c810` 非零转 `c836`。否则 `c812..c81a` 调上述两个helper，再在 `c830/c832` 读取同字段，零则跳 `bfd2`，非零顺序至 `c836`。`c836` 将loop+18清零。`c83a` 把s1改为常量 `a01c4000`，进入既有deinit区域；此后s1不能继续按loop解释。只恢复一个退出边，不确认+18写者或完整退出条件。 |
| 四组PogoPin登记 `c8f8..c9cb` | 沿用s2=ctx。依次读32位有符号字段 ctx+4、+12c、+c8、+64；对应 `BGE zero,a5`（`c8fc/c92e/c964/c99a`）跳过登记，故仅字段>0才调用。`c900/c904` 等将 a1构成 `a00a3bc6`；a0分别为ctx+8、+130、+cc、+68；四个JAL目标均 `a009fb96`，返回值在本局部不作业务消费。已验收C05/C06负责登记器到pending链合同，本次不重开它们。 |
| 后续清理 `c9cc..ca99` | `c9e6` Pogo deinit日志返回后，进入MiIot日志与清理：`ca12/ca16` 调 `a01b2b5c(a0=62fc9480)`，`ca22/ca26` 同函数(a0=62fc9228)，`ca32/ca36` 调 `a01b2cb0(a0=62fc9894)`；`ca44` 调 `a009fb96(a0=62fc9894,a1=0)`。`ca52` 和 `ca6a` 是跳过 fd=-1 清理的向前分支；实际清理调用配对 `ca56/ca5a`、`ca6e/ca72` 均重建到 `a01aca1a`，正常返回后分别写-1。第二fd来源经 `word(s0-118)` 间接读取，其全局别名沿用旧证据，不在此重新认证。各 callee 内部保持未知。 |
| 容器返回 `ca9a..cad1` | `ca96` 最后一次日志调用后，`ca9a` 从sp+18c恢复ra，后续恢复s0..s11；`cace` 恢复sp+190；`cad0` 原字节 `8280` 即 `C.JR ra`。这里是返回，不是落到 `cad2` 及后续容器内的其他块。a0未建立业务返回合同。 |

`AUIPC ra; JALR ra,ra,imm` 的目标由原编码的有符号上20位/低12位重建，结果在证据中单列；不因反汇编地址相邻将它们当成跳入本地循环。选定窗口均可由普通RV32/RVC解码器完整解码，未将厂商未知指令替换为猜测语义。其他未选定窗口仍可能含厂商指令，未一并认证。

## 局部数据视图与可读伪代码

偏移均为十六进制，只复用既有字段视图：loop+d4为32位pending head；handle+28为32位next；ctx四个poll偏移为+8/+130/+cc/+68；对应 fd候选为+4/+12c/+c8/+64。loop+18在本次仅称“退出选择中读取并清零的word”，不补造原始字段名或所有写入者。

```c
// 同一容器中已恢复的一个局部退出选择，不是完整loop。
if (word(loop, 0x18) != 0) goto exit_observed;
opaque_a0098b60(loop);
opaque_a009d304(loop);
// 原程序还写两个栈局部常量，此处不赋予调度语义。
if (word(loop, 0x18) == 0) goto opaque_block_a005bfd2;
exit_observed:
set_word(loop, 0x18, 0);
// 进入既有其他UI资源deinit，未在本任务恢复；随后到四组登记。

// a005c8f8开始；a0/a1的局部传参，保留原signed > 0条件。
if ((int32_t)word(ctx, 0x004) > 0) close_a009fb96(ctx + 0x008, a00a3bc6);
log_uart_done();
if ((int32_t)word(ctx, 0x12c) > 0) close_a009fb96(ctx + 0x130, a00a3bc6);
log_port_done();
if ((int32_t)word(ctx, 0x0c8) > 0) close_a009fb96(ctx + 0x0cc, a00a3bc6);
log_temp_done();
if ((int32_t)word(ctx, 0x064) > 0) close_a009fb96(ctx + 0x068, a00a3bc6);
log_adc_and_pogo_done();
opaque_miiot_teardown_calls_and_fd_cleanup(); // 已列直接目标；不虚构内部行为
restore_saved_registers_and_return();         // cad0；此尾部无直接消费回边
```

完整消费者仍采用C05/C06的 `next=handle.next; finish(handle); handle=next` 表达，本次无需复制其callback和释放伪代码。没有新证据表明上述四次登记后的pending链必为空，也没有新证据表明它必被外部再消费。

## 来源、恢复边界与实际验证

**事实：**本尾部六个局部分支均向前；全部十二个直接JAL为调用；五个配对间接调用有静态可重建目标；最终返回边已核。consumer窗口在此之前，不能仅凭它存在就补出登记后的调度边。调用正常返回是描述尾部后继的条件，不是本任务对所有callee的保证。

**推断：**已恢复消费机会和四组deinit之间存在局部阶段转换；本次未闭合“登记之后再次消费”的生命周期边。日志名称可辅助识别模块意图，不能替代退出/释放证据。

**未知：**callee是否间接消费pending，调用者是否再次运行loop，异步/重入/多线程时序，+18的完整写者合同，callback实际执行次数和ctx全局计数不变量，timer停止/删除。上述未知均未展开或验证，不构成缺陷判断。

来源状态：PogoPin私有封装和底层库继续按私有或来源未知管理；没有可核实新来源/版本，新增开源排除为0。恢复程度仅为容器三个局部与直接退出边，未完成PogoPin/loop/timer生命周期。

实际运行 `python reverse/analysis/pogo-close-consume-c07-0041-20261023/check-static.py`：590 B全部普通解码、未解码0 B；保留raw ranges与ROM一致；8处32位条件分支位域、5处配对调用目标核对通过；尾部6分支/12 JAL及返回边检查通过。脚本初次把终端 `C.JR ra` 也纳入“禁止局部间接跳转”断言，已仅为已核终端地址cad0放行，并重跑通过；未修改ROM/模型或目标行为。提交前完成 `git diff --check` 及独占路径检查。没有打开共享可写REA会话/数据库，没有执行固件、外连、连接设备、编译生产项目或开展缺陷验证。

下一小任务建议：独立复核C07三个短窗口，重点检查 `c80e/c830` 的退出边、`c83a` 的s1别名改变、五个AUIPC/JALR目标和“无局部回边”的有界含义；不扩展完整loop。通过后才由管理窗口另选一个有证据入口的外部再消费问题。
