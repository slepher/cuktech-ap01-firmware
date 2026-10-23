# C08：关闭后消费机会的限定独立复核

2026-10-23；分支 `codex/re-0041-c08`；基线 `0af470d`。**验收结论：接受 C07 的局部控制流和有界否定，无核心语义纠正。** 四组关闭登记之后的直接尾部没有回到既有 pending 消费窗口，callee 正常返回时走至容器返回；不能据此判断 callback 不会执行、关闭永不完成或 timer 已停止。

本任务只复核 [C07 报告](pogo-close-consume-c07-0041-20261023.md) 三个既定窗口 `a005c166..c19d`、`a005c802..c83d`、`a005c8f8..cad1`。未扩展 callee、完整 loop、容器边界或 timer 生命周期。伪代码均为分析者表达，不是原始源码。

## 逐项结论与指令依据

| 项目 | 验收 | 原指令事实及限制 |
| --- | --- | --- |
| pending 消费局部 | 接受 | `c166` 读 word(s1+d4) 到 a0，`c16a` 清槽，`c16e` 非零分支至 `c802`。`c802` 先保存 handle+28 至 s5，`c806` JAL 到 `a009f524`，`c80a` 把 s5 送回 a0，`c80c` 压缩跳回 `c16e`。仅沿用 C05/C06 已验收的 s1=loop 局部合同，不重新证明全局别名。 |
| 一个退出选择及其断边 | 接受 | `c80e` 读 word(s1+18)；`c810` 原半字 `e39d` 为 C.BNEZ a5，目标 `c836`。零路径经 `c814/c81a` 调 `a0098b60/a009d304`；`c830` 重读同槽，`c832` BEQ a5,zero 到 `bfd2`。目标块未展开，不称其完整循环/退出状态机。 |
| 清零与 s1 别名切换 | 接受 | `c836` 原 word `0004ac23` 为 SW zero,18(s1)；随后 `c83a` 原 word `a01c44b7` 为 LUI s1,a01c4，将 s1 改为 `a01c4000`。该点之后不能继续把 s1 解释为 loop。未认证 `c83e..c8f7` 中间资源清理。 |
| 四组条件登记 | 接受 | `c8fc/c92e/c964/c99a` 是有符号 BGE zero,a5，向前跳过登记；字段分别来自 ctx+4/+12c/+c8/+64。严格大于0时 a0=ctx+8/+130/+cc/+68，a1由 LUI/ADDI 构成 `a00a3bc6`，`c90c/c93e/c974/c9aa` JAL 目标 `a009fb96`。返回 a0 未在此建立业务合同。 |
| 五组 AUIPC/JALR | 接受 | 按原 word 的 PC相对有符号 U立即数与 I立即数重建；rd=ra、rs1=ra。`ca12/ca16→a01b2b5c`，`ca22/ca26→a01b2b5c`，`ca32/ca36→a01b2cb0`，`ca56/ca5a→a01aca1a`，`ca6e/ca72→a01aca1a`。这些是保存返回地址的调用，不是本地回跳；callee 内部未核。 |
| 尾部无直接回消费边 | 接受 | `c8f8..cad1` 全部6个条件分支目标严格向前且位于尾部内；12个直接 JAL 的 rd均为ra，目标仅 `a008b51a/a009fb96`；另5组调用如上。没有 C.J、C.JAL 或其他局部间接跳转。`ca9a` 开始恢复ra与保存寄存器；`cace` 恢复sp；`cad0` 原半字 `8082` 为 C.JR ra，结束此返回路径。该尾部的直接后继没有 `c166/c802`。 |
| 未回消费的含义 | 接受其限定表述 | 正常调用返回是讨论尾部后继的条件；静态片段不能保证 callee 返回。callee 间接消费、外部调用者重入、异步调度均未核。没有补造“关闭后再调用一次loop”行为。 |

必要局部表达如下，参数和返回只保留已经证明的寄存器合同：

```c
// s1=loop 仅适用于本局部；不是完整状态机。
if (word(loop, 0x18) == 0) {
    opaque_a0098b60(loop);
    opaque_a009d304(loop);
    // c81e..c82c另有两项栈写，未赋予业务意义。
    if (word(loop, 0x18) == 0) goto unreviewed_a005bfd2;
}
set_word(loop, 0x18, 0);   // c836
s1 = 0xa01c4000;          // c83a，loop别名结束
// 中间清理未展开；四组登记和后续尾部见C07。
// 尾部所有被调函数若正常返回，恢复保存寄存器并于cad0返回。
```

## 证据与实际验证

[review-static.py](../../analysis/pogo-close-consume-review-c08-0041-20261023/review-static.py) 只读主仓库 `roms/0041/ap01-1.0.2_0041.bin`，VA基址 `9ffff000`；只写本任务 [review-evidence.json](../../analysis/pogo-close-consume-review-c08-0041-20261023/review-evidence.json)。C07原证据仍为 [instruction-evidence.json](../../analysis/pogo-close-consume-c07-0041-20261023/instruction-evidence.json)，上游保留 Evidence ID `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`。本次不新增哈希清单或基线副本。

实际执行 `python reverse/analysis/pogo-close-consume-review-c08-0041-20261023/review-static.py` 通过：590 B、163条指令逐项原字节与ROM吻合，普通解码遗漏0 B。原编码独立重建全部所选控制转移，特别核了3条压缩控制边 `c19c/c80c/c810`、尾部6个向前分支、12个JAL和5组配对调用；另断言 `c836/c83a` 的精确编码与先后。C07脚本的 `tail_all_local_branches_forward` 字段本身只是写入布尔量，本次通过每个实际分支目标的断言补足该验证；不需要改变 C07 报告或程序语义。

未运行 C07 生成器，避免修改其独占输出；没有打开共享可写 REA 会话或数据库。已读 REA 技能及管理共同约束；本树及研究适用目录未发现 AGENTS.md，主仓库根/reverse对应目录也未发现。提交前进行 `git diff --check`、独占路径与暂存差异检查。未执行固件、连接设备/外部服务、编译生产代码或开展缺陷验证。

## 来源、恢复程度与剩余问题

**事实**为上表原编码和局部调用合同；**推断**仅为该直接尾部不额外提供既有消费窗口机会；**未核**包括 callee 内部、全函数边界、外部再消费、callback实际时序、ctx计数不变量、timer停止/删除。没有新的开源来源或版本识别，私有/来源未知分类继续保留，新增开源排除为0。C07局部结果获得本次限定验收，PogoPin整体生命周期仍部分恢复。

下一小任务建议：由主窗口转现有 UI 总状态消费者报告中的 gate word `62fc4034`，限定一个直接写入者或清理点；不继续重复 timer 负搜索。本次未对该新问题开展技术分析。
