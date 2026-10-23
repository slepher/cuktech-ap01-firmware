# B07：基础信息注册合同独立复核

2026-10-23；worktree `re0041-b07`，分支 `codex/re-0041-b07`，基线 `2125a49`。结论：**限定接受 B06，无需纠正**。只复核注册函数及其 append/两个短链字段访问器；调用点仅作实参对照。没有展开 callback 消费者、分配器、对象构造或生命周期。以下是指令分析与可读伪代码，不是原始源码，也不是实际运行观察。

## 回答的问题与验收

| 项目 | 结果与原指令依据 |
| --- | --- |
| 去重键 | 接受。`a01b28d6` 取 head，`a01b290c` 读取 node+0 至 a2，`290e` 是 a0/a2 的 BEQ，目标 `2918`。只比较原 a0 callback word；路径中没有读取 node+4 或比较 a1。 |
| 命中是否更新 userdata | 接受。命中直接到 `2918` 的 `c.jr ra`，没有进入 `28de` 的栈帧或 `28fa/28fc` 写入；遍历回边也没有节点存储。此结论只覆盖本函数命中路径，不能推广为全系统 userdata 不变。 |
| 两种 a0 返回形状 | 接受。查找路径不改 a0，命中返回原 callback word。追加调用 `28f2/28f6` 精确指向 `a008af14`，返回后两次 sw 均以 a0 为地址，随后恢复栈、返回，不改 a0；append 自身在 `af60` 显式由 s2 送回节点/零。本任务不认证原返回类型，也不统一成 bool/索引/稳定句柄。 |
| 遍历 next 偏移快照 | 接受。`28d8` 读 header+0，`28da` 加4，至 `2912` indexed load期间没有重写 a3；`2916` 回 `28dc`，不重读 size。 |
| 新建参数与固定 payload 写入 | 接受。`28ea/28f0` 把原 a0/a1 保存在 s1/s2；`28ec` 重新传 header；`28fa` 写 word[node+0]，`28fc` 写 word[node+4]。顺序与 B06 一致。 |
| append链字段及header更新 | 接受。`af22/24/26` 请求 size+8；`af2c` 零值到返回尾部。非零路径先设新next=0，再设新prev=旧tail，旧tail非零才写其next；`af4e` 先读旧head，`af50` 写tail，`af54/56` 旧head为空才写head。 |
| 两个 indexed 指令 | 接受原编码字段与既存本地解释。`a01b2912` 字节 `0b47d740`：op=11/funct3=4/funct5=8、rd=a4、rs1=a4、rs2=a3、shift=0；`a0089ce4` 字节 `0bd6f540`：op=11/funct3=5/funct5=8、数据寄存器=a2、基址=a1、索引=a5、shift=0。现有模型分别解释为32位 indexed load/store；没有认证新上游ISA来源。 |
| 调用点边界 | 接受。`a00a8b50` a1=s1；`8b52` a0=s2-0x376；`8b56/5a` 调注册；`8b5e/60` 增量回循环，不消费 a0。callback绝对值及整个循环的可达前提沿用 B04，本次不重核其范围外初始化前奏。 |

## 函数、结构与可读合同

| 地址（含尾指令） | 入参 / 返回 / 直接关系 |
| --- | --- |
| `a01b28ce..a01b2918` | a0=callback word，a1=userdata word；用header `62fcb530`，未命中调用append。命中a0保留callback；追加路径a0保留append返回寄存器。 |
| `a008af14..a008af66` | a0=header；调用不透明 `a008aea0(size+8)`、下述两访问器；a0回节点/零。 |
| `a0089cda..a0089cec` | a0=header，a1=node，a2=value；node非零时 word[node+word[header]]=value。 |
| `a0089cee..a0089d00` | 同上；node非零时 word[node+word[header]+4]=value。 |

head/tail、prev/next、callback/userdata 是根据使用关系的推断命名。已核的32位字段布局是 header+0=size、+4=head、+8=tail；本次不认证 size 初始化为8。节点业务字段固定为 +0 callback word、+4 userdata word；链字段由运行时size定位，不能凭本报告把节点认定为固定四word结构。

```c
// word表示原32位访问；只投影已核指令，保留两种返回寄存器形状。
word register_partial(word callback, word userdata) {
    word h = 0x62fcb530;
    word p = WORD(h + 4);
    word next_offset = WORD(h) + 4;
    while (p != 0) {
        if (WORD(p) == callback) return callback;
        p = WORD(p + next_offset); // 既存本地indexed模型解释
    }
    word n = append_a008af14(h);
    WORD(n) = callback;
    WORD(n + 4) = userdata;
    return n;
}
```

伪代码保持原控制流与存储，不补安全检查，不开展分配失败测试。B06 对重复注册同一callback不能直接视作每个i独立订阅的条件推论成立；必须保留链表有效、相关调用返回、范围外没有改写等前提，不能据此宣称实际启动时只存在某个i。

## 原始证据和实际验证

证据入口：[B06报告](basic-info-register-b06-0041-20261023.md)及其 [instruction-evidence.json](../../analysis/basic-info-register-b06-0041-20261023/instruction-evidence.json)。本次直接只读原ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA-9ffff000`，未创建共享REA会话或数据库。

独立脚本 [review.py](../../analysis/basic-info-register-review-b07-0041-20261023/review.py) 与实际输出 [review-results.json](../../analysis/basic-info-register-review-b07-0041-20261023/review-results.json) 记录：

- 四窗口共218字节（注册76、append84、访问器40、调用点18）逐条字节匹配原ROM且边界连续；89条普通指令用Capstone RV32+C重新解码，与保留证据一致。
- 30项独立编码检查通过：直接从压缩内存指令位域核寄存器和偏移，从BEQ位域重算命中目标，从SW位域核两个payload写入及head/tail更新；直接解码两个厂商word字段、两个AUIPC/JALR目标以及关键参数保存、next偏移和返回编码。
- 本地 `ap01thead2.sinc` 第6564、6596行起两段indexed模型原文与既存证据逐行一致。这个检查证明使用的是保留模型，不把模型一致性当作独立上游语义认证。

实际命令：`python reverse/analysis/basic-info-register-review-b07-0041-20261023/review.py D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware`；输出 `passed`、89 ordinary decode matches、30 independent encoding checks。未运行B06会写回其证据的脚本；未执行固件、连接服务/设备、生产构建、异常输入或缺陷验证。没有生成哈希或基线复制清单。

**事实**：原字节、标准指令字段、局部控制流、参数保存和word读写顺序。**推断/模型依赖**：业务字段命名、注册含义、indexed指令沿用本地观察模型的解释。**未核/未知**：header初始化、callback ABI/消费时序、并发、清空删除、分配器内部、原语言typedef、indexed指令新上游来源认证。代码来源仍为厂商/未知，没有可核实开源版本依据，不新增开源排除。此局部合同已限定验收，完整基础信息模块仍部分恢复。

后续一个小任务：仅恢复 `a00a3c8a` callback入口与userdata的首个直接使用点；使用 B04 注册调用点与 whole-rom inventory 对应body作为入口，先确认ABI，不假定i位于哪个参数，不扩展全部通知消费者或生命周期。
