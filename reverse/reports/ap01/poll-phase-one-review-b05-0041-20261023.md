# B05：cmd0x55 phase=1 局部分支独立复核

2026-10-23；基线 `3bc3001`，分支 `codex/re-0041-b05`。复核对象为 [B04报告](poll-phase-one-b04-0041-20261023.md)。结论：**本任务限定核心合同接受，无核心纠正；完整初始化、被调函数内部和实际运行可达性未验收。** 不修改B04报告，也不把该局部验收推广为完整响应函数恢复。

## 问题与逐项验收

| 项目 | 结论 | 原指令依据和限制 |
| --- | --- | --- |
| cmd0x55 判别 | 接受 | `a00a85a0` 把a0低byte存栈视图，但 `a00a8602/8606` 比较的仍是原a0与0x55。入口 `85b8` 复制a0而未替换a0；`85c8` 跳到 `8602`。不能把任意低byte为55的参数都算此分支。 |
| helper后缓存gate | 接受 | `a00a88f6..8904` 调 `a0191652(62fcb004,0x18,s0-0x50)`；返回后 `8908` 重建缓存地址，`8930/8934` 以lhu读 `62fcb014/62fcb016`，`8938` OR，`893a` 提取低16位，`893e` 非零跳 `8950`。控制量不是helper返回值。 |
| 独立类型映射是否额外gate | 接受B04的否定结论 | `8918` 到 `8928`、`8922` 到 `8928`，两路汇入byte store并继续上述缓存gate；映射值本身不提前离开。只限这段局部控制流。 |
| 初始化分配成功是否必要 | 接受B04的否定结论 | `a00a8a2e` 调用后，`a00a8a3c` 的a0==0直接跳 `8a82`，没有绕过后续phase写入。该路径还须先前调用及逐项前奏返回；“存在此控制边”不证明真实运行到达。 |
| 逐项前奏参数及目标 | 接受 | `a00a8a22` 以lbu取得s3快照，`8a82/8a88` 用s1=0和signed blt控制；`8b50/52` 传a1=s1、a0=`a00a4000-376=a00a3c8a`；`8b56/5a` 的AUIPC/JALR目标为 **a01b28ce**。返回后 `8b5e` 加1。较早未核消息中的a01428ce不适用。 |
| phase/done/sent/selector次序 | 接受 | `a00a8a96` 先取groups指针快照，`8a98` sb phase=1，`8a9c` sb done=0，`8aa6/8aaa` 进入逐组sent清零循环，循环退出后 `8aae` 调 `a0191746`。组数为0时没有sent写入；selector返回后sent是否为0不在此保证。 |
| 8-bit清零循环 | 接受 | `a00a8aa6` 每轮lbu重读controller+6，`8aaa` unsigned bltu；`8b62` 用旧index算group地址，`8b66` 先加index，`8b68` 才向旧group+6写零，`8b6c` 把index与0xff后回比较。B04伪代码把局部index更新写在store后，保持相同内存写入目标与读取顺序；本报告下方另保留寄存器的准确先后。 |
| 两个厂商word | 限定接受 | 原word `3c07370b` 与既有模型的extu(a4,a4,15,0)一致；`06f6168b` 与addsl(a3,a2,a5,3)一致。复核了ROM字段及模型token/构造器文本；这不是新获得的上游ISA来源证明。 |
| 完整初始化和间接副作用 | 未核 | `896a..8a22` 的完整构建、`8aca` 的内部循环、callee内部没有扩大恢复。B04对此的摘要不能替代单独验收。本复核仅接受所列入口/分支边、null分配捷径及公共末段。 |

## 函数合同与局部状态

唯一核心函数是 `a00a8582` 响应callback的限定投影，a0=command、a1=length、a2=payload；栈视图为 `{u8 command,u8 length,pad[2],ptr payload}`。本次cmd55通路没有已认证的业务成功返回值。函数完整边界沿用原保留provider记录，不把5个窗口当完整函数。

直接依赖只核调用点：`a0191652(dst=62fcb004,n=0x18,view=s0-0x50)` 后重新读取缓存；`a01b28ce(a00a3c8a,i)` 的返回值没有被本循环消费；`a0191746()` 在清零循环退出后调用。helper的通知语义及selector内部行为沿用B01/B03合同，本次不重新验收函数体。`a00a3d22()`、`a008e362(0x17c)` 只用于界定前奏控制边，未新增函数体恢复。

结构命名沿用B01：controller=`62fc4b30`，groups指针@0、phase byte@5、count byte@6、done byte@7；group步长8、sent byte@6。下列为分析伪代码，非原始源码，仅投影已核局部，不补写原程序检查：

```c
// cmd == 0x55；cache helper返回并经过独立类型映射后
uint16_t bits = load_u16(0x62fcb014) | load_u16(0x62fcb016);
if (!bits) leave_via_original_other_state_path(); // 不进入下方写入
else {
    // 缓存/构建前奏不展开；分配返回0亦有边到公共8a82。
    // 到a00a8a22时s3=load_u8(0x62fcb01c)，快照不在循环中重读。
    for (int32_t s1 = 0; s1 < s3; ++s1)
        call_a01b28ce((void *)0xa00a3c8a, s1);
    // 上述调用及前奏必须先返回；不是实际可达保证。
    uint8_t *groups = load_ptr(0x62fc4b30);
    store_u8(0x62fc4b35, 1);
    store_u8(0x62fc4b37, 0);
    uint32_t i = 0;
    while (i < load_u8(0x62fc4b36)) {
        uint8_t *group = groups + (i << 3);
        i += 1;                    // 8b66，先更新寄存器
        store_u8(group + 6, 0);     // 8b68，仍写旧index对应项
        i &= 0xff;                 // 8b6c
    }
    call_a0191746();
}
```

事实为指令、编码、参数寄存器、读写宽度、目标及所列控制边。phase/sent/done和缓存“存在位”的业务名称为既有结构解释；不能由本地非零gate推断“初始化成功”。缓存halfword业务单位、前奏返回保证、回调触发时序、所有phase写入者与完整USB生命周期仍未知。来源仍为厂商/来源未知逻辑，没有新增开源认证或排除项。

## 实际验证与证据

使用REA技能的静态证据复用流程，没有打开/共享可写REA会话。[独立复核脚本](../../analysis/poll-phase-one-review-b05-0041-20261023/review.py)读取主仓库原ROM，只写B05目录；没有运行B04会覆盖其证据的脚本。执行：

```text
python reverse/analysis/poll-phase-one-review-b05-0041-20261023/review.py D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware
```

结果通过：5个连续窗口、398字节与ROM逐字节一致；120条普通RV32+C指令独立重解码，50条关键指令合同断言，2个厂商word位域断言及5段既有模型文本原位核对。结果见 [review-result.json](../../analysis/poll-phase-one-review-b05-0041-20261023/review-result.json)。这些是离线解码/证据一致性检查，不是固件运行或业务动态验证。报告和新增脚本的差异检查通过，未编译生产项目。

原始字节、文件偏移、逐指令定位仍使用 [B04 instruction-evidence.json](../../analysis/poll-phase-one-b04-0041-20261023/instruction-evidence.json)，不复制另一套基线。原Evidence ID为 `ev_70c4f2e4ab81d16f68ee9e092f50824c912cdae172d69b06e93511cdc1f54e18`，保留provider来自 `usb-interface-ota-0041-20261023.json` 的a00a8582，原来源 `whole-rom-private-20261023-068.json`。模型只读核对主仓库 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 第6/3930行，以及reg.sinc第1163–1165行。

没有执行固件、连接设备或服务、缺陷验证、畸形输入、模型修改或全ROM重新扫描；未新增哈希清单。恢复程度为此局部合同已复核，完整函数仍部分恢复。

下一小任务建议：只恢复 `a01b28ce(a00a3c8a,i)` 的一个直接合同及返回条件（最多该函数与两个直接依赖），确认它怎样处理callback和索引；不连带展开整个初始化或USB。
