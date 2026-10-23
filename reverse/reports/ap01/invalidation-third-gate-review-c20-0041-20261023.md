# 0041 C20：第三门局部合同独立复核

结论：**限定接受 C19，无需修改 C19 正文**。三个核心的机器参数、局部读写、身份选择、祖先循环、原地交集及直接 caller 零值消费与 ROM 一致。交集返回 0 前已写四个 word；第三门返回 1 只表明这条局部路径通过，不证明失效提交或显示刷新。两个 opaque 变换 callee 及其副作用仍未恢复，不将本次验收扩为上层业务完成。

## 范围、来源和证据

固定基线 `9270abb`，分支 `codex/re-0041-c20`，本树 `D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c20`。已读本树 rolling-management 共同规则/C20 任务书、C19 报告及脚本、REA 技能与 native guide。本树递归查找及盘根至本树祖先检查未发现适用 AGENTS.md。未发现已有 C20/C21 报告；未改主树、共享状态或 C19 文件。

独立复核只读主仓库 ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，沿用已建立映射 `file_offset=address-0x9ffff000`。没有新哈希或复制清单。三个核心完整窗口：`a00ddab4..a00ddbf5`、`a00892ac..a00892cf`、`a00892f4..a0089349`；caller 仅 `a00ddc70..a00ddc7d` 和 `a00ddd82..a00ddd8f`。共 472B/169 条指令，没有扩大 caller 后段。

本轮编写独立 [review.py](../../analysis/invalidation-third-gate-review-c20-0041-20261023/review.py)，从 ROM 重新取字节、按编码宽度逐条 Capstone 5.0.7 解码并与 C19 留存逐项比对；自行重算直接 JAL/B/C.J/C.B 目标；四个厂商字直接提取字段。没有执行 C19 脚本、固件或分析器模型。保留 [review-evidence.json](../../analysis/invalidation-third-gate-review-c20-0041-20261023/review-evidence.json)（每条原字节、地址、文件偏移、解码、目标、903 项机械检查）和便于定位的 [instructions.txt](../../analysis/invalidation-third-gate-review-c20-0041-20261023/instructions.txt)。机械比对证明字节/解码一致，以下合同判断另经人工逐条寄存器与控制流核对；903 不是独立语义证明数。

继承 C19 whole-ROM inventory Evidence `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2`，三个 extent Evidence 分别为 `ev_52b6741c49402fea0118bbbe5b45ed257faff994d30e0c79e42ec57854d94da5`、`ev_23a3dc62223675713fb06135f3b88a3b419c6e0d044ab1c2d756dabebd15510c`、`ev_c22822040d3e133823f243f0a1c5e93e26b2f3e8d5744cfbe43c23f14a22c166`；本轮不新开 REA 会话/数据库，新增证据是本地静态复核，不是新 REA 运行记录。未重新认证 inventory 来源、源码版本或开源身份。

## 逐项裁定

| C19 项目 | 裁定与原指令依据 |
| --- | --- |
| 第三门参数/帧 | 接受。`dab4` 建80B帧；`dac2` s0=sp+80；`dac6/dac8` 保存 area 到 s2、obj 到 s1。入口无空 obj 分支。区域为四个32位word，局部初始区域 s0-64=sp+16，祖先区域 s0-48=sp+32。 |
| 身份首分支 | 接受。`daca/dad0/dad6` 依次调用 `a00dcdd8(obj)`、`a00dce2e(root)`、`a0080eba(d)`，分别保存 root=s3、d=s4；`dada` BNE 才转 `db84`，相等直接 `dade`。不能把 root/d 均称原 obj。 |
| 身份 fallback | 接受。`db84` s5=s4，`db86` 非零去 `dbf0` 读 s5+0x2d0；否则 `db8a/db8e` 读 word@0x62fc9590，`db92` 非零也去同一读取。两者零则诊断调用，若返回 s5仍为0。`dbf4` 回 `dbb8` 比 s3/s5。fallback 没有回写 s4。 |
| 其余身份候选 | 接受。`dbbc/dbc6/dbd0` 均重新 a0=s4，再调用 `a0080f9e/a0080f06/a0080f52`；`dbc2/dbcc/dbd6` 相等转 `dade`，最后不等落 `dbda`。即使 fallback 非零，这三次仍传原 d，可能为0；不推定 getter 内部行为。 |
| 原 obj 扩张和首次交集 | 接受。`dade` 读 obj+8，`dae0` 取 e；`dae4` 保存，再 `daf0` 以 (s0-64,obj+0x14) 调已继承复制 helper。`daf4..dafe` 调 expand(local,e,e)。`db02..db0a` 调 intersect(area,area,local)，`db0e` s3保存返回，`db10` 零转清零尾部。 |
| 原 obj 的条件变换 | 接受边界。`db16` 查询 a00dbff4(obj)，非零才 `db22` 调 a00dca48(obj,area,1)，返回不直接参加判断。只认证这些实参和极性，不认证内部变换或副作用。 |
| 祖先链/flag | 接受。`db26` 每轮执行 s1=word[s1+4]；`db28` 空直接成功尾部。非空 `db2a..db32` 调 flags(s1,1)，非零失败。父链称谓是结构推断。 |
| 祖先临时区 | 接受参数、保留未核语义。`db34..db3e` 调 a000589c(s0-48,s1+0x14,16)。`db42` LUI 形成0x100000，flags非零才读取s1+8取e并扩张 temp。没有把这个 opaque copy 认证为已核 memcpy。 |
| 祖先变换/循环返回 | 接受。`db62/db70` 采用与原 obj 相同条件门及第三参数1，但传 temp；`db74..db7c` intersect(area,area,temp)，`db80` 非零回 db26，否则 db82转 dbda。s3始终保留首次交集1；任一失败 dbda清0；`dbe8` a0=s3。 |
| 四word expand | 接受。`a00892ac(area,ex,ey)` 对偏移0/4做减、8/12做加，32位模运算；直接 store 顺序为8、0、4、12。无 a0 改写，机器返回原指针，但本路径不消费它。 |
| 原地 intersect | 接受。`a00892f4(dst,left,right)` 四组同偏移先读双方再写dst，支持此处 dst==left；依次写 max(x1)、max(y1)、min(x2)、min(y2)。不扩张到任意部分重叠。`9334` 最后一写早于 `9336..9340` 的有效性判断，零结果不回滚。 |
| caller 零早退 | 接受。`dc70` a1=s0-80，`dc74` a0=s1，`dc76` 调第三门。`dc7a` BEQ a0,x0 到 `ddd82`；该14B尾部不改a0，所以零值原样返回。非零落 dc7e 后段，未核后段。caller 局部副本/其建立来源继承 C17/C18/C19，本轮仅核调用点偏移，不重新认证此前复制过程。 |

以上缩写 dax/dbx/dcx 均为 `a00d` 前缀对应完整地址；所有原字节和偏移可直接在 instructions.txt 依地址定位。没有发现需精确修改 C19 的实质性错误。原 C19 三个核心的局部机器合同获复核接受，其他 callee 内部不因此获得认证。

## 厂商指令与交集边界

四个原32位字与字段（opcode=0x0b、funct3=1、funct7=33）均直接从 ROM 提取；既有只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 的 `th.mvnez` 文本保存在本轮 evidence。模型规则是 rs2==0 保持rd，否则 rd=rs1；这是静态模型依据，未声称硬件执行观察。

| 地址/原字 | rd,rs1,rs2 | 与前置 signed SLT 合并的意义 |
| --- | --- | --- |
| `a0089304 / 42e7980b` | x16,x15,x14 | `9300` a4=(right.x1<left.x1)，非零把a6改为left.x1；得到max。 |
| `a0089314 / 42d7178b` | x15,x14,x13 | `9310` a3=(right.y1<left.y1)，非零把a5改为left.y1；得到max。 |
| `a0089322 / 4317168b` | x13,x14,x17 | `931e` a7=(left.x2<right.x2)，非零把a3改为left.x2；得到min。 |
| `a0089330 / 42c5970b` | x14,x11,x12 | `932c` a2=(left.y2<right.y2)，非零把a4改为left.y2；得到min。 |

`9336` 先a0=0；`9338` signed BLT x2,x1 则保留0返回；否则 `933c` signed SLT y2,y1，`9340` XORI 1 给0/1。相等边界允许1。无无符号比较、无“先判断再写”分支。这一结论直接依赖指令和上述模型，不依赖反编译 min/max 名称。

## 最小合同与必要结构

结构仅为 `AreaWords { word32 x1,y1,x2,y2; }`，偏移0/4/8/12；坐标名称是 signed 交集模式推断，不认证原C typedef。第三门 a0=obj、a1=可写area，正常返回0/1；expand a0=area,a1=ex,a2=ey；intersect a0=dst,a1=left,a2=right，返回0/1。后两个无直接 callee。

```c
// 结构伪代码；opaque 函数正常返回是继续分析的前提。
root = opaque_a00dcdd8(obj);
d = opaque_a00dce2e(root);
if (root != opaque_a0080eba(d)) {
    p = d ? d : load32(0x62fc9590);
    previous = p ? load32(p + 0x2d0) : 0; // p==0 路径先诊断
    if (root != previous && root != opaque_a0080f9e(d) &&
        root != opaque_a0080f06(d) && root != opaque_a0080f52(d)) return 0;
}
e = inherited_aux(load32(obj+8));
local = inherited_copy4(obj+0x14);
expand(&local,e,e);
first = intersect(area,area,&local); // 四项先写，后判
if (!first) return 0;
if (opaque_a00dbff4(obj)) opaque_a00dca48(obj,area,1);
p = obj;
while ((p = load32(p+4))) {
    if (inherited_flags(p,1)) return 0;
    opaque_a000589c(&temp,p+0x14,16);
    if (inherited_flags(p,0x100000)) {
        e = inherited_aux(load32(p+8)); expand(&temp,e,e);
    }
    if (opaque_a00dbff4(p)) opaque_a00dca48(p,&temp,1);
    if (!intersect(area,area,&temp)) return 0;
}
return first; // 已核 intersect 保证 first==1
```

主 helper 完整直接 callee 集合为 `a000589c/a0080eba/a0080f06/a0080f52/a0080f9e/a00892ac/a00892f4/a008b43a/a008b51a/a00d7446/a00dbff4/a00dca48/a00dcdd8/a00dce2e/a01ad6d8`；本轮核调用边和实参，不展开这些 opaque/继承依赖。三个核心只有 JR ra 作为间接控制返回；没有扩查其他调用者。

## 验证、恢复程度与未知

实际运行 `python reverse/analysis/invalidation-third-gate-review-c20-0041-20261023/review.py`：**passed**，5窗口/472B/169指令/903机械检查，40个直接控制目标及4个厂商位字段核对；人工完整阅读相同169条指令。首次脚本测试因两处预期助记符错标压缩前缀失败，依实际编码修正检查脚本后通过；这属于复核工具记法修正，不是C19或ROM差异。

事实是原字节、32位读写宽度、参数传递、分支极性和0/1返回。矩形/祖先关系属于有指令支持的结构解释；候选对象的正式名字与LVGL对应仍是来源推断。本轮未重新读取来源字符串、未外连搜源，没有新增已认证开源排除，准确LVGL版本与厂商修改仍未知。源码没有恢复；局部机器合同通过复核，完整业务恢复仍受 opaque 依赖限制。

未核包括两个变换callee的内部/区域写入和地址持有、getter内部、诊断是否返回、a000589c内部复制、正式字段/flag名称、caller完整返回类型、完整失效队列和最终显示刷新。本轮没有执行固件、连接设备/外部服务、历史回放、畸形输入或缺陷验证；未改ROM、生产代码、安全检查或模型，未共享可写REA状态。

后继建议（仅据 C19，未展开）：C21 先限定恢复 **a00dbff4** 正常参数/返回以及是否有区域副作用。它的非零结果是两处 a00dca48 调用门；先确定门的语义，再另立任务研究 a00dca48，会使区域变换解释有明确前提，继续不扩GUI或失效队列。

提交操作记录：首次明确四个独占文件的 git add 因 `.git/worktrees/re0041-c20/index.lock: Permission denied` 失败；按既有本地提交授权申请 Git 元数据写入升级，不改变权限、不绕过限制。提交前核暂存路径和差异。
