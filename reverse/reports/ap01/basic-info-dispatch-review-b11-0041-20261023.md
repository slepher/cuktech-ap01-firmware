# B11：基础信息分派调用局部独立复核

2026-10-23；分支 `codex/re-0041-b11`；固定基线 `aabf574`。限定复核 [B10](basic-info-dispatch-caller-b10-0041-20261023.md) 的 `a00a8582..a00a873d` 和 `a00a53c0..a00a53ed`，共490B；不是完整响应函数、全部生产者或状态机验收。结论：**限定接受 B10，无需纠正**。以下均为静态证据，不表示观察过执行。

## 逐项验收

| 项目 | 结论及原指令依据 |
| --- | --- |
| 入口参数和 selector 宽度 | 接受。`85a0 sb a0,-0x50(s0)` 只保存低byte，没有把a0截断；`85ac/85b0`、`85bc`、`85c0/85c4/85c8`、`8602/8606`、`860a/860e`、`8616/861a` 使用a0完整32位值，沿本路径最终只让 `a0==0x52` 进入 `861e`。`85ba c.mv s1,a2` 保存payload；不把a1或注册userdata当作index。 |
| U8 index 与直接调用参数 | 接受。`8626` 原word `00064b03` 为 `lbu x22,0(x12)`，不是LB/LW；`862a c.mv a0,s6` 后 `862c jal ra,a00a53c0`。`8734 c.mv a0,s6` 后 `8736 jal ra,a00a389c`。人工检查中间顺序指令，s6在此段仅由8626写入，8674仅把s6读入a5。跨callee保留仍依赖既有callee-saved ABI，不证明不透明callee内部实现。 |
| lookup owner/count 门控 | 接受。`53c6/53ca` 读 word[`62fcb2cc`]，`53ce c.beqz a5,53e2` 在owner=0时直接把零返回；非零才 `53d0 lbu a4,6(a5)`。`53d4 bgeu a0,a4,53ea` 为无符号比较，超界令a5=0，再回到共享尾部。 |
| lookup 地址计算及返回 | 接受但保留模型依赖。`53d8 c.lw a5,0(a5)` 取base；`53da addi a4,zero,0x1a8`；`53de` 原word `20e5178b` 的opcode=0xb、rd=15、funct3=1、rs1=10、rs2=14、funct7=16，与既存模型 `th.mula a5,a0,a4` 一致，表达 `base+index*0x1a8`（32位）。`53e4 c.mv a0,a5`、`53e8 c.jr ra` 返回。未新增上游ISA来源验证；不保证计算结果非零或地址有效。 |
| lookup 返回门控 | 接受。`8630 c.mv s5,a0` 保存返回值；`8632 c.bnez a0,8638`，零值经8634跳 `a00a9aac`，不进入后续局部。 |
| 栈word magic 条件 | 接受。`8638/3a/3e/42` 调用 `a000589c(frame-0x48,payload+1,8)`；日志 `8680` 之后才 `8684 lw a4,-0x48(s0)`。`8688/868c` 构造完整常量 `0x2b010112`；`8690 beq` 只在word相等时到8698，否则8694跳 `a00a9a8a`。不认证opaque实际复制了任何内容。 |
| opaque返回与p检查顺序 | 接受。`8698 lw s2,0x28(s5)`；`869c/86a0/86a2/86a8` 调 `a00501be(p,payload+5,0x14)`，`86a4` 另存payload+5到frame-0x64。`86ac c.bnez a0,86b2` 先检查返回非零，零值86ae跳9aac；随后 `86b2 bne s2,zero,86ba` 才检查p，零值86b6跳9aac。没有把非零命名为相等/不同，也不重排p检查。 |
| 第二opaque及首word覆盖 | 接受。`86ba` 重载先前保存的payload+5，`86be/86c0/86c2` 调 `a000589c(p,payload+5,0x14)`；随后读取p字段并在872a调用日志。`872e c.lui a5,4` 得到0x4000，`8730 sw a5,0(s5)` 为整个word覆盖，无OR或读改写。然后8734/8736传U8 index分派，873a跳9aac。此序列以callee正常返回为前提。 |
| 下游 callback ABI及对象同一性 | 本次未重新核B08/B09的下游间接调用，沿用其限定结论。B10明确指出分派器重新读取owner/base，本次接受该未知边界：不能认证分派/清零对象必然等于先前lookup对象。 |

## 合同和最小结构投影

`a00a8582` 本次局部入口a0为完整word selector，a2为payload指针；a1仅可见低byte保存。函数完整返回合同、其他路径及 `9a8a/9aac` 续接均未验收。局部调用链为 `a00a8582 → a00a53c0`、两处 `a000589c`、两处日志 `a008b51a`、`a00501be`、`a00a389c`，具体顺序见上表。

`a00a53c0(index)` 返回0或按既有MULA模型计算的32位地址。结构投影仅为owner+0=base word、owner+6=count U8、record步长0x1a8、record+0=本路径被覆盖的word、record+0x28=p word；不是原始typedef。最小伪代码保持调用和检查次序：

```c
// 只表示selector==0x52的已核局部分支，opaque有未知副作用。
U8(0x62fcb2f0) = 0;
index = U8(payload);
record = lookup_partial(index); // owner/count门控，MULA依赖既有模型
if (!record) goto out_9aac;
opaque_589c(frame-0x48, payload+1, 8);
opaque_log();
if (U32(frame-0x48) != 0x2b010112) goto out_9a8a;
p = U32(record+0x28);
if (!opaque_501be(p, payload+5, 0x14)) goto out_9aac;
if (!p) goto out_9aac;
opaque_589c(p, saved_payload_plus_5, 0x14);
opaque_log(/* p字段 */);
U32(record) = 0x4000;
dispatch_389c(index);
goto out_9aac;
```

这里的名称均为解释性投影。事实为原字节、宽度、寄存器和控制流；推断/依赖为ABI保留、业务字段名、selector命名、MULA既有语义。未核项是opaque内部语义/副作用/终止、magic业务意义、完整函数所有入边、运行时可达性、跨调用owner/base稳定性、完整对象布局、下游callback重新验收及整个模块行为。不得把这些局部条件称为全函数所有路径的充分必要条件。

## 证据、来源及实际验证

- 独立脚本 [review.py](../../analysis/basic-info-dispatch-review-b11-0041-20261023/review.py) 从原ROM读取两个相同地址窗口，不调用B10 verify.py、不执行固件。独立解析B/J/I/S和压缩MV/零分支编码，另核关键压缩立即数、载入、返回编码及厂商word字段；Capstone重新解码全部157条普通指令，并逐条与B10保留原字节、解码和窗口边界比对。
- 输出 [review-evidence.json](../../analysis/basic-info-dispatch-review-b11-0041-20261023/review-evidence.json)：**passed；2窗口、490B、157普通指令、1厂商word、64项原编码检查**。人工逐行核参数准备、callee前后顺序、s6局部写者及selector完整word路径；自动检查数不代表形式化证明或执行覆盖。
- 只读源：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA-0x9ffff000`。既有模型：同主仓库 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc:25`；只读摘义，未修改/扩展模型。
- 函数边界沿用B10及whole-ROM inventory：caller Evidence `ev_84d269c719f525cf12aec538463b7169bc02fc8bf8f09c45975d1aaf8a80f0f2`，lookup Evidence `ev_ff599978578d69cc7b3e9f094ae8625d8bb2cb7c932f50e242f674272b7a50be`。没有建立新REA会话或数据库，也未以旧反编译替代原编码核验。
- 运行命令为在B11工作树执行 `python reverse/analysis/basic-info-dispatch-review-b11-0041-20261023/review.py`，退出0。适用祖先/局部路径未发现AGENTS.md。差异检查仅含B11独占报告、脚本和证据；未修改B10。

来源版本仅确定为本仓库0041镜像标签；本次未识别上游组件来源或原源码版本，因此不新增开源排除。恢复程度为B10两个局部的独立接受，模块整体仍部分恢复。未执行固件、连设备/外部服务、运行生产构建或缺陷验证，未新增哈希/复制清单。

后继建议：仅恢复 `a00501be` 一个直接helper的参数/返回合同（最多两个直接依赖），解释非零返回的具体语义；仍不扩完整响应、对象跨调用稳定性或缺陷调查。
