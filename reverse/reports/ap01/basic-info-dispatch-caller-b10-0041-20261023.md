# B10：基础信息分派的一个直接调用局部

2026-10-23；分支 `codex/re-0041-b10`，基线 `446cfec`。仅展开 `a00a8582` 内到 `a00a8736` 的一个调用局部，以及 `a00a53c0` 查找 helper；不恢复完整响应函数或全部生产者。本文为静态恢复和可读伪代码，不是原始源码或运行观察；结论待独立复核。

## 回答的问题

**`a00a8736 → a00a389c` 的 index 来自入口 a2 指针的第一个无符号 byte。** `a00a8626` 的 `lbu s6,0(a2)` 零扩展为 32 位，`8734` 再以 `c.mv a0,s6` 传给分派器。中间本地没有第二条 s6 写入，按既有调用 ABI 的 callee-saved 合同跨越直接调用保留；不是注册循环 userdata，也不是入口 a1。B08/B09 已恢复的下游间接 ABI 继续为 callback 的 a0=节点 userdata、a1=所选记录指针，不能把这两层 a0 混同。

入口 a0 的可见局部分派路径要求 **完整 word 等于 `0x52`**（`85ac..861a`）；入口先保存的低 byte 不改变这些比较的宽度。该路径先写 byte[`62fcb2f0`]=0，再读上述 index，调用 lookup，并要求返回非零。随后还须通过以下局部门控，才到本次分派点：

1. 调用不透明 `a000589c(frame-0x48, payload+1, 8)` 并完成日志调用后，word[`frame-0x48`] 必须等于 `0x2b010112`（`8684..8694`）。其常见“拷贝 header”解释尚未在本任务证明；精确已证条件是**该调用之后栈槽的实际 word 值**。
2. 从 lookup 返回对象 `+0x28` 读出指针 p，调用不透明 `a00501be(p,payload+5,0x14)`；返回 a0 必须非零（`86a8..86ae`）。此处只认证机器返回条件，不擅自把它改称“相等”或“不同”。
3. 随后才要求 p 非零（`86b2..86b6`）。保持原判断次序，不把这个检查提前至上一步调用前。
4. 调用不透明 `a000589c(p,payload+5,0x14)`，读取 p 的一组字段并调用日志，正常返回后直接写 word[lookup返回对象]=`0x4000`（`872e..8730`），然后以 byte index 调分派器。

这些是从入口沿已核分支到该点的局部路径条件；不认证不透明 callee 的终止、返回、副作用、异常或实际可达性。未展开原函数其他入口/跳转路径，也不宣称这些条件构成整个函数所有可能进入该地址的必要充分条件。

## 函数、字段和调用关系

| 地址 / 局部范围 | 参数、返回与已恢复合同 |
| --- | --- |
| `a00a8582`；本次窗口 `8582..873d` | 入口 a0=word selector（命令命名为推断），a1仅低 byte保存到frame-0x4f，a2=payload指针（保存到s1）。原函数保留范围 `8582..9d1d` 共6044B，本次只核前444B。`8736` 为直接 JAL ra 到 `a00a389c`；`873a` 跳到 `a00a9aac`，该续接未展开；不认证原返回类型/值。 |
| `a00a53c0..53ed`，46B | a0=word index；owner=word[`62fcb2cc`]。owner==0返回0；否则读无符号 byte[owner+6]，index>=count（无符号比较）返回0；否则按现存 MULA 模型返回 word[owner]+index*`0x1a8`，32位环绕。该计算结果自身也可能为0，本任务不保证分配/地址有效性。 |
| `a00a389c`（沿用 B08/B09） | a0=word index；重新读owner/base，选记录，遍历注册链表，以a0=userdata、a1=record间接调用，完成后清记录首word；返回语义未知。本任务没有再展开其指令。 |
| 不透明直接依赖 | `a000589c` 两处调用参数如上；`a00501be` 返回非零条件如上；`a008b51a`为已有报告的日志入口，内部均未展开，不据常见函数形状确认开源归属。 |

局部结构投影：owner+0 是 base word，owner+6 是 unsigned count byte；记录步长0x1a8；record+0 是本路径写0x4000的word，record+0x28 是 p word。字段名称只是标注，未认证原 typedef、对象完整布局或业务单位。

```c
// 只投影本次路径；opaque_* 保留未知副作用，读取顺序沿原指令。
word lookup_partial(word index) {
    word owner = U32(0x62fcb2cc);
    if (owner == 0) return 0;
    if (index >= U8(owner + 6)) return 0; // unsigned
    return U32(owner) + index * 0x1a8;  // MULA既存模型，32位
}

// a00a8582内selector==0x52的局部分支；不是完整函数。
U8(0x62fcb2f0) = 0;
word index = U8(payload);
word record = lookup_partial(index);
if (record == 0) goto continuation_9aac;
opaque_a000589c(frame - 0x48, payload + 1, 8);
opaque_log_a008b51a(/* 原窗口中的参数 */);
if (U32(frame - 0x48) != 0x2b010112) goto continuation_9a8a;
word p = U32(record + 0x28);
word result = opaque_a00501be(p, payload + 5, 0x14);
if (result == 0) goto continuation_9aac;
if (p == 0) goto continuation_9aac;
opaque_a000589c(p, payload + 5, 0x14);
opaque_log_a008b51a(/* 从p读取的字段 */);
U32(record) = 0x4000;
a00a389c(index);
goto continuation_9aac;
```

`a00a389c` 会重新读取全局owner/base，因此没有认证最后被分派和清零的对象与此前lookup对象在运行时一定相同；不透明调用可能改变全局状态，本任务不补造不变式。`0x4000` 是完整word覆盖，不是 OR 单bit；其业务名尚未知。此点是另一个基础信息生产者局部，不能视为完整更新机制。

## 指令证据与实际验证

- [instruction-evidence.json](../../analysis/basic-info-dispatch-caller-b10-0041-20261023/instruction-evidence.json)：两个连续窗口逐指令原字节、VA、文件偏移、重新解码、51项检查、厂商word位域和模型摘录。原ROM只读路径为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；映射 `offset=VA-0x9ffff000`。
- `85b0/bc/c4/c8`、`8606/0e/1a` 核selector条件；`8626/2a/2c/30/32` 核byte index、lookup与非零门控；`8684/88/8c/90` 核栈word及magic；`8698/9c/a0/a2/a8/ac/b2` 核p和原分支顺序；`872e/30/34/36` 核完整word覆盖和index参数/直接调用。
- lookup `53ca/ce/d0/d4/d8/da/de/e4/ea` 核owner/count/base、unsigned比较、乘加与返回。`53de` 原word=`20e5178b`，op=0xb、rd=a5、funct3=1、rs1=a0、rs2=a4、funct7=16；与现存 `ap01thead2.sinc:25` 的 `th.mula` 匹配，语义为rd=rd+rs1*rs2。这只认证与既存本地模型的一致性，未新增上游ISA来源证明，未改模型。
- 边界来源复用whole-ROM inventory：caller extent Evidence `ev_84d269c719f525cf12aec538463b7169bc02fc8bf8f09c45975d1aaf8a80f0f2`；lookup extent `ev_ff599978578d69cc7b3e9f094ae8625d8bb2cb7c932f50e242f674272b7a50be`。旧caller反编译存在bad-instruction警告，本任务未以其文本代替原指令。
- 执行 [verify.py](../../analysis/basic-info-dispatch-caller-b10-0041-20261023/verify.py) `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware`：**passed**，2窗口490B、157普通指令、1厂商word、51检查。Capstone RV32+C逐条解码，独立从原编码核标准/压缩branch、JAL、MV、load宽度、SW、C.LUI及MULA字段；另核局部s6写者与必要数据流。辅助脚本只读ROM，写任务专属证据。

**事实**为字节/宽度、寄存器流、可见分支和调用参数；**推断/模型依赖**为selector命令名、owner/record/count业务命名、callee-saved ABI及MULA语义；**未知**为不透明callee内部语义/副作用、magic业务解释、实际触发/可达性、调用后owner稳定性、记录字段类型、续接行为与完整状态机。代码仍属厂商/来源未知，无来源版本识别可以据以排除为开源。本次恢复程度仅为一个直接生产者路径及lookup局部，模块整体仍部分恢复。

没有执行固件、连接设备或外部服务、缺陷验证、生产构建、新共享REA会话/数据库或模型修改，也没有新增哈希清单。差异检查见任务提交。下一小任务建议 B11：独立复核本次两个窗口，重点核byte index、selector word比较、opaque返回门控的原顺序、lookup MULA与0x4000覆盖；不展开opaque实现或完整响应函数。
