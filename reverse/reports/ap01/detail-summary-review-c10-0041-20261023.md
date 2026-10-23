# 0041 C10：详情摘要 helper 独立技术复核

结论：**限定接受 C09，无需语义纠正**。原 ROM 支持 `a00f3844(ctx)` 先取全局模式、再从 `ctx+0` 所指对象选择 child0→child2，最后向 `a0091ee4` 传 `%s` 与模式名称指针。两处 indexed word load 的寄存器/编码已核；其语义仍依赖已有本地厂商指令模型，不升级为新取得的上游 ISA 认证。完整文本接口内部、对象所有权以及 callback snapshot 与全局 snapshot 的一致性仍未知。

任务基线 `b885567`，独立分支 `codex/re-0041-c10`。只复核 [C09](detail-summary-c09-0041-20261023.md) 的三个核心函数及已有两个调用者局部，不回已解决的 gate，不展开 `a00f388c` 或完整 UI。本报告是分析产物，伪代码不是原始源码。无新增开源排除。

## 证据与实际核验

- [独立静态核验脚本](../../analysis/detail-summary-review-c10-0041-20261023/review.py)只读主仓库原 ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；映射 `offset=address-0x9ffff000`，输出只写本任务目录。
- [复核证据](../../analysis/detail-summary-review-c10-0041-20261023/review-evidence.json)保留5窗口的原字节及解码、独立拆出的跳转目标/字段、厂商编码与本地模型原文位置。
- 与 [C09指令证据](../../analysis/detail-summary-c09-0041-20261023/instruction-evidence.json)逐条比对原字节及通用解码；不是把 C09 脚本成功运行当作技术验收。
- C09 保留的 inventory Evidence `ev_7d1d5f852e61f0a8a4ccc377f66435bc628b7cb37a96562712e54dc205878972` 为 helper body `a00f3844..a00f388b`。本次从入口按2/4字节指令走至 `a00f388a: c.jr ra`，共72B，未因反编译边界跳过尾部。

实际命令：在 C10 worktree 执行 `python reverse/analysis/detail-summary-review-c10-0041-20261023/review.py`，结果 passed：5窗口328B、106条普通指令、2个厂商 word、独立拆解8个 JAL目标和6个压缩条件分支、5个普通load编码、4个表指针及5段文本。通用解码器 Capstone 5.0.7。没有运行固件或业务参考实现，没有设备/服务连接，没有共享可写 REA 会话/数据库，没有修改分析器模型，没有进行缺陷验证或生产编译；不新增哈希清单。

## 逐项验收

| 项目 | 结果 | 原指令依据和边界 |
| --- | --- | --- |
| `a00f3844` 入参/边界 | 接受 | `3850` 将 a0 保存为 s2；`3858: lw a0,0(s2)` 读 ctx 首word。`3844..388b` 的写入均为栈保存，没有直接写 ctx 字段。调用者不消费返回，C09 的 void 是使用合同而非原始 typedef。 |
| 全局模式 getter `a00a5c50` | 接受 | `5c50/5c54` 构造并读 `word@62fcb2cc`；`5c58` NULL 分支落 `5c60`，非空 `5c5a: lbu a0,8(a5)`；日志调用返回后 `5c8e` 明确设 a0=0，再于 `5c92` 返回。空分支不是 inventory 前段之外的无关函数而被遗漏。 |
| 模式值保存 | 接受 | `3852` JAL getter；`3856` 将返回 a0 保存 s1。随后两个 child 调用后，`3870` 仍以 s1 作表索引；局部不重读全局模式。没有因此证明其他调用对全局状态的副作用或并发时序。 |
| child0→child2 | 接受 | `385c` a1=0，`385e` 调 `a00dcee4`；`3862` a1=2，`3864` 同目标且沿用第一次 a0 返回对象。没有额外 NULL 检查。 |
| `a00dcee4` 正常非空路径 | 接受 | `cee4` 非空分支落 `cf30`；`cf30` 读对象+8，`cf32` 扩展为空返回；`cf34: lhu` 读扩展+0x30；`cf38` signed非负判断、`cf3c` 负索引加count、`cf3e` signed负检查、`cf42` unsigned范围检查、`cf46` 取扩展首word数组基址。NULL对象入口走日志/断言调用，不能伪造成普通NULL返回。日志/断言调用自身返回及实现仍未认证。 |
| 两个厂商 indexed load | 编码接受；语义保持模型依赖 | `3870` 原字节 `0bc69744`，op/f3/f5/shift=11/4/8/2，rd/rs1/rs2=12/15/9；`cf48` `0bc5b744`，同类字段，rd/rs1/rs2=10/15/11。对照主仓库 `ap01thead2.sinc:6564` 的 `th.lrw`：读取 `WORD(rs1+(rs2<<2))`，不回写基址。没有外查或修改该模型，通用解码器仍不识别这些字。 |
| 表与文本调用参数 | 接受调用合同；内部未核 | `3868/386c` 得 `a01c473c`，`3874/3878` 得 `%s`@`a06136bc`，`387c` JAL `a0091ee4`；a0为第二次child返回，a2为模式表选项。四指针/UTF-8文本与C09一致：AI 智配、极速单充、均衡输出、自定义。这些显示名称不能证明实际模式算法。 |
| callback→summary 局部边 | 接受 | `3a1e` tag=13，`3a2e` 调 `a00a72ae`；返回非零且两个输出非零时 `3a3e` 分支到 `3aee`，日志调用后 `3b08` 装 ctx，`3b0c` 调 summary。仅核这些已有窗口，gate和其他mask路径沿用已有报告，不新增验收。 |
| callback snapshot一致性 | 未核，保留C09未知 | helper的读取来源是全局指针，不是显式传入snapshot。静态窗口不能证明总是一致，也不能证明运行时发生过不一致。 |
| 来源/所有权/formatter内部 | 未核，保留C09未知 | 本范围没有开源版本的可核实依据。child helper 的LVGL形状/路径线索不足以认证版本、排除适配或厂商修改。ctx+0创建者、child身份、文本复制/分配/重排及完整生命周期没有恢复。 |

## 可读合同与剩余缺口

三个核心函数入参/返回及关系如下：`a00f3844` 的 a0=ctx，返回未被这个调用者使用；`a00a5c50` 不使用调用入参，返回全局对象+8的unsigned byte或NULL路径日志后的0；`a00dcee4` 的 a0=对象、a1=signed index，正常非空对象路径返回选中子对象或NULL。文本接口仅确认 a0/a1/a2 参数边界，未确认其返回和存储语义。

```c
// 分析伪代码；word_load_indexed 的解释依赖既有本地指令模型。
void summary_usage_contract(DetailCtx *ctx) {
    uint32_t mode = global_mode_a00a5c50();
    Object *child0 = child_a00dcee4(ctx->word_00, 0);
    Object *child2 = child_a00dcee4(child0, 2);
    const char *name = word_load_indexed(0xa01c473c, mode, 2);
    text_a0091ee4(child2, "%s", name);
}
```

`DetailCtx.word_00`、Object扩展+8、扩展count+0x30、扩展数组+0均为局部偏移合同，不是完整结构体恢复。C09采用32位回绕加法表达负索引路径，符合 `c.add` 的宽度；本 helper 实际索引只为0和2。上述事实不主张所有下层调用都无副作用。厂商load语义、parent/child/label等分析命名是模型解释或推断；原编码、偏移、读取宽度、直接目标和资源字节是本次指令事实。

恢复程度：这三个函数的所列局部合同限定验收通过；整个详情页仍部分恢复。无需改动C09报告。下一小任务建议：只恢复 `a0091ee4` 的入口与一个直接依赖，明确 `%s` 调用如何形成文本存储、返回及所有权合同，最多3核心函数；不扩完整UI/页面生命周期，不能仅凭接口形状认定开源来源。
