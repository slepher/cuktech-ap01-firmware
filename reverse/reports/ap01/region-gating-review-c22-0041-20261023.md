# 0041 C22：区域门控与祖先谓词独立复核

结论：**接受 C21 的局部机器合同，无语义纠正；限定接受本闭包所需 C15/C17/C19 合同。** `a00dbff4` 是只读链搜索，检查无符号 halfword 的 `(v & 0x0c00)==0x0800`，返回恰为0/1。它不接收区域、不返回命中节点，也不执行区域变换。两处非零结果只开启 `a00dca48(current_node, writable_area, 1)`；传入的 current_node 仍是 caller 当前节点。区域请求通过前置门和祖先裁剪后，caller 只在第三门返回非零时到达 `a00ddc7e`。这一合同串接**不构成完整区域提交或物理刷新验收**。

## 范围和方法

固定基线 `2ee39b3`，分支 `codex/re-0041-c22`，独立 worktree `D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-c22`。已读共同规则、C22完整任务书、REA技能和 native guide，及 C15/C17/C19/C20/C21报告；本树、输出目录及逐级祖先检查未发现适用 AGENTS.md。只修改 C22 独占目录/本报告，没有修改原报告、主树、共享索引或其他树；没有创建下级agent。

复核10个函数合同：`a00dddf4/a01ad6d8/a008b43a/a00ddbf6/a0081804/a00d7446/a00ddab4/a00dbff4/a00892ac/a00892f4`。其中 `a00ddbf6` 只核 `dbf6..dc7d` 和公共尾部 `ddd82..ddd8f`，其余九个按前序已知完整连续extent核字节。总11窗口、1014B、354指令；不是 `a00ddbf6` 全函数恢复。身份getter、诊断、`a000589c` 和 `a00dca48` 均保留调用边合同，不加算内部已核。

独立 [review.py](../../analysis/region-gating-review-c22-0041-20261023/review.py) 只读主仓库 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，沿用 `file_offset=address-0x9ffff000`。脚本自行按编码宽度从 ROM 取字节、Capstone 5.0.7重新解码、重算直接控制目标，关键 I 型指令/四个厂商字直接拆位；仅对照前序留存字节，不执行旧脚本。未新开或切换任何REA会话/可写数据库。没有新哈希或复制清单。

[evidence.json](../../analysis/region-gating-review-c22-0041-20261023/evidence.json) 保留本次取出的原字节、地址、文件偏移、解码、目标、477项机械检查及只读厂商模型原文；[instructions.txt](../../analysis/region-gating-review-c22-0041-20261023/instructions.txt) 按地址定位。477是字段/字节一致性检查数，不是独立语义结论数；下面判断另经人工完整阅读354条指令及寄存器流。未用反编译伪代码代替原指令。

## 逐项裁定

| 项目 | 裁定与原指令依据 |
| --- | --- |
| C21 参数/只读 | **接受**。`bff4/bff6/bffa`仅建16B帧并保存s0；唯一store是 `c.swsp s0,12(sp)`。函数无调用、无区域地址或a1读取。外部访问只有节点+8、非零aux+0x32及节点+4；无对象/aux写、无指针保存到外部存储。 |
| C21 掩码/宽度 | **接受**。`bff8` LUI 1和`bffc` ADDI -0x400形成0xc00；`c00c`原字`0x0327d783`拆为opcode3/rd15/funct3=5/rs1=15/imm50，是LHU；`c010`AND；`c012`加-0x800后`c016`零跳成功。只取bit11:10，等于二进制10，其他位不参与。 |
| C21 起点和链 | **接受**。`c000`非零才读节点；aux零`c00a`转`c018`继续；不命中也落`c018`读取word[node+4]，`c01a`回`c000`重查空。包括起点，空起点/链尾均返回0；不声明任意输入的终止保证。 |
| C21 返回/ABI | **接受**。成功`c01c`明确置a0=1再到公共尾部；空路径到尾部时a0=0。恢复s0/sp，JR ra。没有匹配指针输出，其他参数寄存器不读，原C签名/返回typedef未认证。 |
| 两处谓词消费 | **接受**。`db14/db16`传原obj；`db60/db62`传当轮s1。`db1a/db66`零分别跳`db26/db74`；非零分别以 `(s1,s2,1)` / `(s1,s0-48,1)` 调`a00dca48`。没有把谓词命中节点作为a0传递。后一轮谓词可再次遍历后续链，不缓存前一结果。 |
| C15 请求准备 | **限定接受所需合同**。`dde42..dde54`先读obj+8取e，再复制obj+0x14四word到32B帧的sp+0；`dde58..dde86`前两项减e、后两项加e，模2^32，`dde8a`无条件传(obj,local)到入口。尾部不判断/改写callee返回。辅助getter空返回0，非空读+0x2c完整word；复制helper按0/4/8/12读写，无callee。未复核C13文本消费者。 |
| C17 第一门 | **限定接受所需合同**。`dc46`先保存原area指针；`dc4c→dc50`把`a00dce2e(obj)`返回量直接传`a0081804`，未替换为obj。query非零候选/回退word@62fc9590读候选+0x268；`1848`为signed SLT(x0,value)，严格>0。`dc54`零到共同尾部，发生在复制之前。候选getter内部未核。 |
| C17 第二门 | **限定接受所需合同**。`dc58..dc60`先把area复制到96B帧的sp+16；`dc64..dc68`查(obj,1)。`7492..7498`读word[obj+0x24]，AND mask再SUB mask、SLTIU 1，等价全mask匹配。`dc6c`非零早退。共同尾部不改a0，所以第一门机器返回0、第二门返回1，不能合并为统一成功码。 |
| C19 身份门 | **限定接受调用和分支合同**。`daca/dad0/dad6`依次取root、d和候选，返回分别保留s3/s4；`dada`不等转fallback。`db84..dbf4`先选d或全局回退并读+0x2d0，随后比较或分别以原s4查询三个候选；回退不写s4。全不匹配到`dbda`置0。getter/诊断内部仍不透明，不由此认证实际对象身份。 |
| C19 第一次局部写 | **接受**。`dade..dafe`先取e再复制obj区域到第三门80B帧的sp+16，扩张；`db02..db0a`调用intersect(area,area,local)，`db0e`存s3后`db10`判断零。交集四项先写，后判有效，故第三门0返回允许其area已改变。该area是入口栈副本，不是请求者初始area。 |
| C19 祖先顺序 | **接受**。完成首次交集及条件变换后，`db26`每轮重读s1+4；空到成功尾部，非空先查flag1、再以(dst=s0-48,src=s1+0x14,n=16)调`a000589c`；查mask0x100000，非零才重新取aux+0x2c并扩张temp；接谓词/条件变换，再交集。未认证`a000589c`内部复制语义。 |
| C19 返回和失败 | **接受**。s3只保留首次交集1；祖先交集返回只用于`db80`循环分支，失败到`dbda`清s3；`dbe8`搬回a0。祖先flag拒绝可发生在先前交集/变换后，无回滚。身份拒绝发生于本函数区域准备前，但不据此排除不透明身份callee副作用。 |
| 区域原地依赖 | **接受**。expand写序8、0、4、12，内容为[x1-ex,y1-ey,x2+ex,y2+ey]；intersect逐同偏移读left/right再写dst，采用signed32的max/min，支持本路径dst==left。`9334`最后一写早于`9338/933c/9340`的有效性判断；边相等允许1。仅认证本次别名形状。 |
| caller消费 | **接受到断边**。`dc70/dc74/dc76`传(obj,s0-80)到第三门；`dc7a`零到不改a0的`ddd82`尾部，机器值0；非零落`dc7e`，后段未核。第三门1不等价最终提交成功。 |
| a00dca48内部及实际刷新 | **未核**。只接受两处实参/条件调用/返回不用于直接判断的边合同。其区域写、读取宽度、变换规则、地址持有、依赖集合及返回含义未核；`dc7e`以后、失效队列/物理显示刷新未核。 |

表内bffx/c00x均为`a00d`前缀；dbxx/dcxx/ddxx/dexx均为`a00d`前缀；18xx为`a008`、74xx为`a00d`、93xx为`a008`。完整地址以本次instructions.txt为准。**纠正项：无**，没有修改C21及前序原文；扩张的实际store顺序已在C20列明，本报告保留而不误作新纠正。

## 厂商指令与机器状态

四个字 `a0089304=0x42e7980b`、`9314=0x42d7178b`、`9322=0x4317168b`、`9330=0x42c5970b` 均从原ROM取出，独立拆得opcode=0x0b、funct3=1、funct7=33，rd/rs1/rs2分别(16,15,14)、(15,14,13)、(13,14,17)、(14,11,12)。与主仓库只读 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 的原文对应：rs2==0保留rd，否则rd=rs1。结合前置signed SLT，前两组选择max，后两组选择min。这个语义依据是既有静态模型与原编码，不是本次硬件/模型执行观察；未改模型。

必要布局和所有权只按机器视图建立：节点+4是32位链指针，+8是aux指针，+0x14..0x23是四word区域，+0x24是flags；aux+0x2c是扩张word、+0x32是无符号16位被测字段。父/祖先、矩形、外扩等词是结构解释，正式C结构、枚举及数值域未知。

请求者`a00dddf4`的local位于其帧sp+0..15；入口`a00ddbf6`复制到自身sp+16..31（s0-80），第三门通过s2引用这份副本；第三门另有初始区域sp+16..31（s0-64）、祖先temp sp+32..47（s0-48）、e保存sp+12（s0-68）。这些sp属于不同栈帧，不能把相同sp偏移误认同一缓冲。第三门直接裁剪的是入口副本；其temp只在变换调用后作为交集右输入，结果写回入口副本。谓词无申请/释放/保留，已核四word依赖也无分配。整体callee是否持有任何栈地址仍未知，不因同步调用形式宣称完整生命周期安全或所有依赖只读。

最小伪代码说明原顺序，非原源码或执行模型：

```c
predicate(p):
    while (p != 0):
        aux = load32(p+8)
        if (aux != 0 && (load_u16(aux+0x32) & 0xc00) == 0x800): return 1
        p = load32(p+4)
    return 0

// 第三门身份门通过后的部分；身份getter仍为边界。
e = aux_word(load32(obj+8))       // 在copy之前
copy4(local, obj+0x14)
expand(local,e,e)
first = intersect(area,area,local) // 先写4word，后判断
if (first == 0): return 0
if (predicate(obj)): opaque_a00dca48(obj,area,1)
p = obj
while ((p = load32(p+4)) != 0):
    if (flags(p,1)): return 0
    opaque_a000589c(temp,p+0x14,16)
    if (flags(p,0x100000)):
        e = aux_word(load32(p+8)); expand(temp,e,e)
    if (predicate(p)): opaque_a00dca48(p,temp,1)
    if (intersect(area,area,temp) == 0): return 0
return first                     // 恰为1
```

原入口调用顺序保持 `a00dce2e→a0081804→copy4→flags(obj,1)→third_gate`；第三门1只允许进入尚未核后段。`a00dddf4`仅沿用最终callee的机器a0，原C返回类型仍未知。

## 来源、验证和断边

继承whole-ROM inventory Evidence `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2`。C21 extent `ev_bccfc2ce2ae63881bb671e9332979d174d626a00de69b5e0e3462c88480928f3` /无直接callee `ev_a95ab7e4112973408e57c106ac40300aef1e946e97b75c90f7581c51e578bce4`；C19三个extent `ev_52b6741c49402fea0118bbbe5b45ed257faff994d30e0c79e42ec57854d94da5`、`ev_23a3dc62223675713fb06135f3b88a3b419c6e0d044ab1c2d756dabebd15510c`、`ev_c22822040d3e133823f243f0a1c5e93e26b2f3e8d5744cfbe43c23f14a22c166` 为历史静态来源，本次不是新的REA运行记录。本次不重新认证inventory完整性、源码来源字符串或开源身份。

来源入口为 [C21](transform-predicate-c21-0041-20261023.md)、[C19](invalidation-third-gate-c19-0041-20261023.md)/[C20](invalidation-third-gate-review-c20-0041-20261023.md)、[C17](invalidation-gates-c17-0041-20261023.md)/[C18](invalidation-gates-review-c18-0041-20261023.md)、[C15](text-precondition-c15-0041-20261023.md)/[C16](text-precondition-review-c16-0041-20261023.md)。本次重新比对字节的具体文件在evidence.json retained_byte_sources。C15/C17既有LVGL函数/路径字符串只支持来源候选，C21没有单独来源证据；准确LVGL版本、厂商改动和正式字段名未知，无新增开源排除，不计算全ROM恢复百分比。

实际运行 `python reverse/analysis/region-gating-review-c22-0041-20261023/review.py` 首次即 **passed：10函数合同/11窗口/1014B/354指令/477机械检查/68直接控制目标**。人工核C21完整19指令、整个所选控制/实参/局部区域流；原字节与保留证据一致。没有运行固件、分析器模型、历史回放、构建或项目测试；没有设备/外部服务连接、畸形输入、异常/缺陷/漏洞验证；未改ROM、生产代码、安全检查、构建配置或模型。

闭包的有证据答案是：前两门决定是否创建/继续使用入口副本，第三门控制身份、初次交集和逐级祖先裁剪，C21只决定两处不透明callee是否被调用，第三门0只触发caller早退；局部失败可能已有区域写。完整业务仍在准确可定位边上断开：`a00dca48`两处调用、`a000589c`内部、身份getter内部、`a00ddc7e`之后及物理刷新。未知还包括aux字段生产者、对象链生命周期、诊断返回属性及下游是否保留区域地址。

一个后继闭包建议（供管理者G01，不在本轮启动）：以 `a00dca48` 为唯一主callee，核它在正常第三参数1时如何读取/写回四word区域，是否保留传入指针，以及两种实参(obj,入口副本)/(祖先,temp)的不同坐标含义；只展开其必要直接依赖，保留完整变换库与刷新边界。已遇到核心边是 `a00ddab4→a00dbff4→a00dca48` 及变换后 `a00892f4`；**本次未进入a00dca48内部，其直接callee清单未知，不猜造地址**。证据入口是本次instructions.txt的 `a00ddb14..db26` 和 `a00ddb60..db80`、本次evidence.json，以及C21完整谓词证据/C19局部区域布局；后继需先读取该callee已知inventory extent和其原字节，再圈定实际5–12函数范围。不得将本次caller返回未消费解释成callee无副作用或无区域写。

提交操作记录：首次明确四个独占文件的git add因 `.git/worktrees/re0041-c22/index.lock: Permission denied` 失败；按既有本地提交授权申请Git元数据写入升级，不改变权限、不绕过限制。提交前核暂存路径、差异和空白。
