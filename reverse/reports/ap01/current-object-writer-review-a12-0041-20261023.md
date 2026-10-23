# A12：当前对象参数化写者独立复核

2026-10-23；基线 `139d99431cf70fbd8fc74b3e87522677f0fb0b19`，分支 `codex/re-0041-a12`。**限定接受 [A11](current-object-writer-a11-0041-20261023.md)，无核心纠正。** `a0027340` 的目标调用臂把入口 node 和槽地址 `62fc6c18` 传给 `a00272d4`；后者仅在两种已列条件下，以 32 位 word 写 head。选中调用臂不等于必然改 head；不能由此证明 A07/A09 对象运行时同一性或完整调度行为。

## 范围、来源与证据

只读复核 `a00272d4..a002733f`（108B）和 `a0027340..a00273cb`（140B），无第三核心函数、无新写者搜索。[review-static.py](../../analysis/current-object-writer-review-a12-0041-20261023/review-static.py) 从主仓库 ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin` 只读取这248B；映射基址 `9ffff000`，起始文件偏移 `282d4`。没有建立新哈希或复制清单。每条指令重新从 ROM 解码，再与 A11 记录比较；关键字段另按原编码拆解，而非仅相信反编译或 A11 的检查结果。

[review-evidence.json](../../analysis/current-object-writer-review-a12-0041-20261023/review-evidence.json) 的 `windows` 保存全字节、地址及反汇编，`checks` 保存66项编码检查。函数边界沿用 A11 所引 Ghidra 12.1.4 body address-set；不是新发现的完整 ROM 边界。A11 来源是既有 inventory 的 `sched/sched_addreadytorun.c` 和 `sched/sched_addprioritized.c` 引用，Evidence ID 分别为 `ev_a211305edb1b01f1ca7fbbccb4c66448cba716f544d3904cbf7a5605ee974a24`、`ev_d0005438e1eb7978fa99f0dac29eb36cb4eead77d7456502fd2b1325bd713e30`。本次保存引用记录并核指令语义，未独立认证该源路径归属、原源码版本或修改边界。NuttX 形状只是来源候选，不新增开源排除。

已读 REA skill/native guide、本树管理 A12/共同规则；检查本树及祖先、reverse/reports/ap01、reverse/analysis 适用路径未发现 AGENTS.md。只写本任务独占文件，不用共享可写 REA 会话/数据库，不改模型、生产代码、安全检查或 ROM；未执行固件、连接设备/服务、异常输入或缺陷验证。

## 逐项复核

| A11 主张 | 结果及独立原指令依据 |
| --- | --- |
| 入口 node 来源与槽参数 | 接受。`7354:84aa` 为 C.MV s1,a0；`734c:62fc75b7` 构造 a1=`62fc7000`，`7350` LW s2,-1000(a1)；目标臂 `738a:c1858593` 令 a1=`62fc6c18`，`738e:8526` 恢复 a0=s1，`7390` JAL ra,`a00272d4`。这段到调用无中间 call；node 上层来源未核。 |
| 目标调用臂选择条件 | 接受。`7356` LH old_head+`20`，`735a` BGE zero,a5→`738a`；否则 `735e/7362` 两个 LBU +`10`，`7366` BGEU old_byte,node_byte→`738a`。条件为 signed halfword≤0，或在其>0时 unsigned old_byte≥node_byte；先读 old_head，不补造非空保护。 |
| 另一调用臂 | 接受。`736a/736e` 另构造 `62fc6c0c`，`7372` 调同callee，`7378` SB node+`1c`=1，`737c` 显式 a0=0；不能把此臂也归为目标槽写入。 |
| unsigned 相等项遍历 | 接受。`72d4` LBU node+`10`→a4；普通非零入口 `72f4` C.LW head；`72f8` LBU current+`10`→a3，`72fc` BGEU a3,a4→`7310`，再 C.LW current.next，`7312` 跳回 `72f6`。相等时继续，只有严格较小 current 才进入其前插入。 |
| `a002730c` 写 head | 接受。非空 current 且 current_byte<node_byte，`7300` C.LW current.prev，`7302` prev≠0 跳非头插入；prev=0时先写 node.next=current、node.prev=0、current.prev=node，再 `730c:88c1` C.SW a0,0(a1)，`730e` 去返回1。 |
| `a0027338` 写 head | 接受。遍历到 current=0，`732c` 读 tail，`732e` tail≠0跳接尾；tail=0时 `7330/7334` 清 node.next/prev，`7338:88c1` C.SW a0,0(a1)，`733a` C.SW a0,4(a1)，返回1。不能凭 head=0自行假设 tail=0。 |
| 两处 store 宽度、基址和值 | 接受。半字 `c188` 的 quadrant=0、funct3=6，rs2'=2→a0、rs1'=3→a1、uimm=0，即 word32 store。普通非零byte路径直到两写点无 call、不重写 a0/a1；在上述调用臂，目标为 `62fc6c18`，值为该调用者入口 node。callee 自身是参数化槽写者，未内嵌这个全局地址。 |
| 其余插入臂与返回 | 接受。`7322..7328` 改 node/current/prev链接后 `732a` 去 `731e` a0=0；`7314..731c` 接tail且写list.tail后也返回0。head写臂去 `733c` a0=1；`7320/733e` C.JR ra。返回值是本地 head 更新指示，未上升为完整调度语义。 |
| byte+10=0诊断边界 | 接受。`72d8` C.BNEZ a4→`72f4`。零分支在 `72e2..72ec` 改写 a0/a1/a2，`72f0` JAL `a0019672`；机器布局随后是 `72f4`，但未核该函数是否返回及其寄存器合同，不能沿用入口node/list/byte。没有把落空路径当普通插入执行证据。 |
| 调用者返回及状态 | 接受。`7394` 返回0跳 `73c4`，SB node+`1c`=2；非零走 `7396..73be`，普通无诊断臂写 node+`1c`=3、node.next+`1c`=2，再返callee的1。诊断后返回值未知，详见下段。 |
| 源码版本、上层对象、运行时关系 | 未核。指令支持局部字段/链头解释；不认证源码等同、完整结构体、调度时序、其他写者或对象身份。 |

对调用者返回边界进一步精确表述：callee返回1后，`7396` 再读原 old_head+`20`；`739a` 非零直接去诊断准备 `73a2`。仅该 signed halfword等于0，且 `739c` 读 node+`0c` 经 `739e` signed BGTZ 为真时，直接去 `73b4` 完成普通状态写入并保留a0=1。否则 `73b0` 调 `a0019672`，后续a0不再有已证返回合同。这是补充 A11 “正常臂/诊断边界”的条件明细，无需更改其结论。

## 已证局部结构和必要伪代码

分析布局限实际访问：node+0=next word、+4=prev word、+`10`=比较byte、+`1c`=状态byte；list+0=head word、+4=tail word。old_head+`20`为signed halfword；node+`0c`是调用者后置检查读取的word。名称不是原始类型恢复。

```c
// 仅非零 node.byte_10 普通入口；不含诊断返回路径。
cur = list->head;
while (cur && cur->byte_10 >= node->byte_10) cur = cur->next;
if (cur) {
    prev = cur->prev;
    node->next = cur; node->prev = prev; cur->prev = node;
    if (prev) { prev->next = node; return 0; }
    list->head = node; return 1;        // a002730c
}
tail = list->tail;
node->next = 0; node->prev = tail;
if (tail) { tail->next = node; list->tail = node; return 0; }
list->head = node; list->tail = node; return 1; // a0027338
```

事实是编码中的参数流、字段宽度、条件和store；链表/head更新语义是这些读写支持的局部解释。未知包括上层node来源、内存/并发前提、诊断合同、所有其他写者、完整调度器与全局维护规则、A07创建对象/A09 snapshot的运行时同一性。恢复程度为这一个参数化写者和调用臂的局部合同已独立复核，不是当前对象生命周期闭合。

## 实际验证及后继

宿主 Python、Capstone 5.0.7 解码两窗口248B/91条普通指令，所有字节及反汇编行与A11逐项一致，无opaque word。66项独立原编码检查覆盖两个C.SW32、所有插入臂关键读写、signed/unsigned分支、直接调用和关键跳转、返回/状态常数。人工核控制流和无中间call值流；JSON解析、报告链接、脚本语法及 `git diff --check` 检查通过。不编译生产固件、不运行目标或算法模拟。PowerShell有初始化驱动提示，但显式Set-Location后的读写和验证成功。

首次精确暂存因sandbox拒绝写worktree的Git `index.lock` 失败；依已授权的本地提交范围升级执行同一暂存成功，未改权限或绕过限制。暂存差异仅本任务三个独占文件，`git diff --cached --check` 通过。

后继建议：若有可靠本地候选，只核这两个NuttX形状函数的源码来源/版本/修改边界，保留未知修改，不能只凭路径或形状排除开源覆盖；本次未开展该研究。
