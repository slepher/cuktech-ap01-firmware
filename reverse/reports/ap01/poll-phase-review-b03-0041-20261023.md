# B03：cmd 0x58 phase 写入局部独立复核

2026-10-23；管理基线 `bf38793`，分支 `codex/re-0041-b03`。结论：**接受 B02 核心局部合同，补充负结论范围说明**。整体模块仍部分恢复。本报告的伪代码是分析视图，不是原始源码。

## 回答的问题与验收

| B02 命题 | 复核结果及指令依据 |
| --- | --- |
| cmd0x58 先调用缓存 helper，再检查条件 | 接受。`a00a8780` 直接调用 `a0191652`；返回后的 `a00a8784` 从保存在 s1 的 `62fcb504` 读取 word；`a00a8786` 为零跳 `a00a8aae`。条件不是 helper 返回值，也不是 payload byte。 |
| 非零时清 phase byte | 接受。`a00a878a` 构造 `62fc5000`；`a00a878e` 为 `sb zero,-0x4cb(a5)`，目标 `62fc4b35`。另直接拆 S 型编码核 opcode/funct3/rs1/rs2/有符号偏移，确为单 byte 写零。 |
| 两条路径汇入轮询选择器 | 接受。零分支与 `a00a8792` 均到 `a00a8aae`，该处直接调用 `a0191746`；`a00a8ab2` 到共同尾部。未根据返回寄存器赋予业务成功含义。 |
| response_view 和分派参数 | 接受。入口 `a00a85a0/a4/a8` 分别保存 byte command、byte length、word payload 至 `s0-0x50/-0x4f/-0x4c`。`a00a8514..8546` 以 lbu 取 command/length，length=0 时 payload=NULL，否则为 `s3+0x34`；第一次间接调用后重读槽，再以 `(0x24,0,NULL)` 调用。 |
| helper 可先写 round_done，再通知 | 接受其局部次序。`a0191688` 组遍历结束后 `a019168e` 写 `controller+7=1`；发现仍可选组时 `a01916f2` 跳 `a0191692`，保留旧值。比较结果为零时 `a01916a8` 直接到尾部；非零时调用既有复制依赖，然后读 handler 槽并可在 `a01916d0` 同步间接调用。均先于 caller 的 phase 条件读取。 |
| 不清 sent / round_done | **限定接受**。cmd0x58 局部没有这些直接清零；整个 helper 的直接 store 仅栈保存/局部保存、传输 byte 清零、round_done 置1。不能扩大为整条调用链 sent/round_done 不变：`a0191746` 有既有 sent 推进合同，未解析的间接 handler 也不能排除副作用。B02 的“本分支没有重置”应按这个局部边界理解。 |
| 安装点证明实际间接目标 | 接受 B02 保留的未知。`a00a4718..4724` 只证明将 `a00a8582` 写入 `62fcb6c0` 的一个安装点；不能保证调用瞬间仍为该值。第一次调用后重读槽的事实同样不能替换为固定目标。 |

没有发现需要改变 B02 核心地址、指令宽度、条件或调用顺序的错误。上表是对已交付内容的复核，不新增 phase=1、完整解析器或 USB 状态机恢复。

## 核心局部合同

| 入口 / 范围 | 参数、返回及关系 |
| --- | --- |
| `a00a8330` 的 `a00a8514..8547` | 被调 handler 收到 `(uint8 command,uint8 length,payload-or-NULL)`；随后槽重读并通知 `(0x24,0,NULL)`。未认证外层返回值与上游帧接受条件。s3 基址由 `a00a83fc/8404` 得 `62fcb2f0`，三字段地址为 `62fcb322/323/324`。 |
| `a00a8582` 的 cmd0x58 分支 | a0/a1/a2 为 command/length/payload；栈 view `{u8 command@0,u8 length@1,未初始化间隔@2..3,ptr payload@4}`。调用 `a0191652(62fcb504,4,&view)`，可清 phase byte，然后调用 `a0191746()`；无已认证业务返回。 |
| `a0191652..a01916ff` | a0=destination，a1=n，a2=view；保存参数后清传输状态，检查旧 phase 的组完成状态，可能置 done=1，再经既有比较/复制依赖，变化时通过当前槽通知。handler 参数为 `((view.command+0x20)&255,0,NULL)`，本调用对应0x78。未认证业务返回。 |

只保留需要证明读取时机的伪代码：

```c
// 分支入口已判断原 a0 == 0x58；不表示整个 callback。
cache_helper(0x62fcb504, 4, &view); // 过程中可能调用当前 handler
if (load_u32(0x62fcb504) != 0)    // 必须保留 helper 返回后的读取
    store_u8(0x62fc4b35, 0);
poll_selector();                  // 不代表 sent 保持不变
```

事实是上述读写、参数、分支、宽度和先后顺序。`phase/sent/round_done` 名称及比较/复制职责沿用 B01 已验收结构与依赖识别；本次并未重新认证比较/复制目标内部实现。`phase=0` 的业务名称、缓存四字节的业务含义、全部槽写入者、实际间接目标/副作用及其他 phase 写入者仍未知。原代码先检查旧 phase 下是否完成再清 phase，不在伪代码中调整顺序或补复位。

## 证据、验证和恢复程度

- [B02 原报告](poll-phase-writer-b02-0041-20261023.md)及[保留逐指令证据](../../analysis/poll-phase-writer-b02-0041-20261023/instruction-evidence.json)是入口；其每个窗口已有 provider 来源路径与 Evidence ID，不重新制作哈希/基线副本。
- [B03 只读复核脚本](../../analysis/poll-phase-review-b03-0041-20261023/review.py)从主仓库 `roms/0041/ap01-1.0.2_0041.bin` 只读取字节，对7个窗口逐条对比保留字节，并以 Capstone RV32+C 独立解码138条普通指令，核连续边界及关键控制流目标；脚本只写自身目录的[验收结果](../../analysis/poll-phase-review-b03-0041-20261023/review-result.json)。关键 byte store 另作位域核对。窗口无厂商指令；函数完整边界沿用既有证据，不把窗口当作全部函数。
- 实际执行 `python reverse/analysis/poll-phase-review-b03-0041-20261023/review.py D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware` 成功，输出 `accepted_with_scope_clarification`、7窗口、138指令。手工检查上述寄存器生存期、helper 的分支与全部直接 store；结果 JSON 保留 helper store 枚举，便于核查负结论范围。
- 未运行 B02 的写文件脚本，未改其证据；未打开共享 REA 会话/数据库，未修改模型、执行固件、连接设备或外部服务。来源仍为厂商/未知私有逻辑，本次无新增开源认证或排除项。

本任务为限定技术验收，其他 command、完整帧校验、selector 函数体和间接目标集合未重新验收。下一小任务建议：单独复核同一 callback 的 phase=1 局部分支与其直接复位写入，保持与本次分离。
