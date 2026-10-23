# A11：62fc6c18 一个参数化写者的局部合同

2026-10-23；基线 `f712c40483ced6c44df786822dc9c512042f5e3a`，分支 `codex/re-0041-a11`。**已定位 `a0027340 → a00272d4` 的写入路径：前者在一个调用臂将 `a1=62fc6c18`、`a0=入口 node`；后者在 `a002730c` 或 `a0027338` 以 C.SW 将 node 写入该 word。** 该局部将全局用作双向链表的 head 槽；不能据此证明 A09 适配入口在运行时读取的对象就是 A07 创建的对象。

已读 REA 技能及 native guide、管理 A11/共同约束和 A09/A10。检查本树及其祖先、reverse 子树和主仓库根未见适用 AGENTS.md。只在独占目录写证据和报告；ROM、既有 inventory/留存引用从主仓库绝对路径只读。未开共享 REA 会话/数据库、未执行固件、连接设备或外部服务、研究缺陷、修改模型/生产/安全检查/ROM。以下命名与伪代码均为分析表达。

## 范围与来源

仅恢复两个核心：`a0027340..a00273cb`（140 B）与直接依赖 `a00272d4..a002733f`（108 B）。入口来自既有 `whole-rom-coverage-0041-20261023-initial.json` 的 source-path references：`sched/sched_addreadytorun.c` 指向前者，`sched/sched_addprioritized.c` 指向后者。两条源路径的引用 Evidence ID 分别为 `ev_a211305edb1b01f1ca7fbbccb4c66448cba716f544d3904cbf7a5605ee974a24`、`ev_d0005438e1eb7978fa99f0dac29eb36cb4eead77d7456502fd2b1325bd713e30`；完整边界、直接调用与限制保存在本任务 JSON 的 `inventory`，沿用 Ghidra 12.1.4 body address-set，未重建全 ROM 边界。

[collect-static.py](../../analysis/current-object-writer-a11-0041-20261023/collect-static.py) 只读主仓库 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`（映射基址 `9ffff000`）及上述 inventory；[instruction-evidence.json](../../analysis/current-object-writer-a11-0041-20261023/instruction-evidence.json) 保存两函数全部原字节、91 条指令、39 项独立编码检查与来源记录。不另建哈希或复制清单。

这些路径支持 NuttX 来源候选，未核版本或逐实现等同，两个函数均不新增开源排除。`62fc6c18` 作为 head 槽的解释来自指令和链指针读写，不单靠源码文件名。

## a0027340：确定 head 槽实参的一个调用者

分析签名 `int add_ready_local(Node *node)`；入口 node 在 `7354` C.MV 保存到 s1。只说明局部值流，不恢复 node 的分配/创建来源。字段 `node+0x10` 为 unsigned byte，`old_head+0x20` 为 signed halfword；用途不扩展成完整调度合同。

| 地址 | 原指令事实与合同 |
| --- | --- |
| `734c/7350` | LUI a1,`62fc7`；LW s2,-`3e8`(a1)，即 old_head=`load32(62fc6c18)`。 |
| `7356/735a` | LH a5,`20`(s2)；BGE zero,a5 → `738a`，因此 signed halfword ≤0 进入目标调用臂。这里先解引用 old_head，没有全局非空保护，不能替代码补保护。 |
| `735e/7362/7366` | 若 halfword >0，读 old_head/node 的 unsigned byte+`10`；BGEU old_byte,node_byte → `738a`。 |
| `738a/738e/7390` | ADDI a1,a1,-`3e8`；C.MV a0,s1；JAL `a00272d4`。这一臂 a1 仍为 `62fc7000`，没有中间 call，故 head-slot 实参精确为 `62fc6c18`。 |
| `736a..737c` | 其余臂重新构造 a1=`62fc6c0c`，同样调用 `a00272d4`；该臂不是目标 global 槽，随后 byte(node+`1c`)=1、a0=0。 |

因此到目标槽调用的前置条件为 `load_s16(old_head+0x20) <= 0 || load_u8(old_head+0x10) >= load_u8(node+0x10)`，第二项只在第一项为假时读取。它只是选择调用臂，不保证该调用必然改 head。callee 返回 0 时 `7394` 去 `73c4` 写 byte(node+`1c`)=2；返回非零时走 `7396` 的局部检查，正常臂写 node 状态 3 和其 next 状态 2。诊断调用 `a0019672` 的返回性质/寄存器保持未恢复，不把越过诊断后的 a0 定义为可用返回值。未触发诊断时函数普通返回臂保留 callee 的 0/1；另一槽调用臂显式返回 0。

## a00272d4：参数化链头写者

分析签名 `int insert_local(Node *node, HeadTail *list)`，其中入口 a0=node，a1=list；读写宽度均以指令为准。局部布局：node+0 为 next word，node+4 为 prev word，node+`10` 为比较 byte；list+0 为 head word，list+4 为 tail word。该结构仅覆盖本函数实际访问字段。

`72d4/72d8` 读 byte(node+`10`) 并在非零时直接去 `72f4`。以下合同限这个非零分支。若 byte 为零，代码构造路径/行号/0 并在 `72f0` 调 `a0019672`；若它返回则落 `72f4`，但 a0/a1/a4 是 caller-saved，本任务未证明其保存，不能沿用原 node/list/byte 的合同。

从 `72f4` 读取 head，循环在 `72f8/72fc` 读取 current+`10`，若 unsigned current_byte ≥ node_byte 则 `7310/7312` 沿 current+0 继续。相等项被越过，不能将条件写成严格大于。

| 写点 | 可由原指令建立的条件及效果 |
| --- | --- |
| `a002730c`：`88c1` C.SW a0,0(a1) | 找到非空 current 且 current_byte < node_byte；`7300/7302` 读 current.prev 为零。此前 `7304/7306/730a` 已按 word 写 node.next=current、node.prev=0、current.prev=node；此处将 list.head=node，`730e` 跳 `733c` 返回 1。 |
| `a0027338`：`88c1` C.SW a0,0(a1) | 当前指针为零，`732c/732e` 再读 list.tail 也为零；`7330/7334` 清 node.next/prev，此处写 list.head=node，`733a` 写 list.tail=node，`733c/733e` 返回 1。 |
| 其余插入臂 | `7322..732a` 插入非头位置，或 `7314..731c` 接 tail；只改 node/邻居链接与必要 tail，不写 list.head，`731e/7320` 返回 0。不假定 head/tail 一定一致；head=0 而 tail≠0 也按编码走 tail 臂。 |

两处 C.SW 的 quadrant/funct3、源/基址压缩寄存器与立即数均独立按原半字解码：都是 `reg=10(a0), base=11(a1), offset=0, width=word32`。callee 不含其他 call（非零 byte 路径）或未知厂商 word，入口 node 值到这两个写点没有重写 a0/a1。当调用者上述 `738a` 臂选中时，存储目标精确为 `62fc6c18`，值精确为该调用者入口 node；这也是“参数化直接存储”而非全局地址内嵌于 callee 的区别。

```c
// 仅 node.byte_10 != 0 的普通入口分支；前置内存可读写条件未验证。
cur = list->head;
while (cur && cur->byte_10 >= node->byte_10) cur = cur->next;
if (cur) {
    prev = cur->prev;
    node->next = cur; node->prev = prev;
    cur->prev = node;
    if (prev) { prev->next = node; return 0; }
    list->head = node; return 1; // a002730c
}
tail = list->tail;
node->next = 0; node->prev = tail;
if (tail) { tail->next = node; list->tail = node; return 0; }
list->head = node; list->tail = node; return 1; // a0027338
```

## 实际验证与有界未知

宿主 Python/Capstone 5.0.7：248 B、91 条普通指令，无不识别厂商 word；39 项 load/store 宽度/源与基址/立即数、signed/unsigned 分支、两个直接调用目标、全局地址和返回编码检查通过。完整原字节保存在 JSON；人工核循环及插入臂控制流、目标槽调用臂无中间 call。脚本、JSON 解析、报告相对链接与 `git diff --check` 为本地验证；没有编译生产项目、执行固件或运行算法模拟。

定位过程先检索 A09/A10、旧 pass2/pass3 和 inventory。inventory 函数字段无目标明文并不证明无引用；最终以 source-path owner 候选和原指令闭合。曾展开 `init/nx_start.c` owner `a0028f40` 的只读原字节作定位，未恢复其完整功能、未形成第三核心合同。一次目录/检索输出过宽被截断、一次全目录小 JSON 文本尝试在完成前中止，均不计作“未找到所有写者”的负证据；随后只取明确 inventory 和本两函数。PowerShell初始化驱动提示存在，显式 Set-Location 后实际操作成功。

恢复程度：**一个写者局部合同已恢复**，含入口值来源、调用臂前置条件、实际写条件、word 宽度与 callee 0/1 返回。未知仍包括 node 在更上层的来源、所有其他写者（含 gp 相对/参数化/厂商指令写入）、全局作为“当前任务”的完整维护规则、并发/中断时序、A07 对象与 A09 snapshot 的运行时同一性，以及诊断返回合同。链头更新不能证明线程调度或启动，也未新增蜂鸣退出关联。

Git 首次暂存因 worktree `index.lock` 写入权限被 sandbox 拒绝；依本次用户明确本地提交授权，用升级工具完成同一精确路径暂存，未更改权限或绕过限制。暂存差异仅本任务三文件，`git diff --cached --check` 通过。

下一小任务建议：独立复核这两个函数的 `738a` 槽实参、`730c/7338` 写条件、unsigned 相等项遍历和零优先级诊断边界；不扩完整调度器。
