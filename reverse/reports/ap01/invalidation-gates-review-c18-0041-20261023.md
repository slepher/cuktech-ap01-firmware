# 0041 C18：失效区域两道返回门独立复核

结论：限定接受 [C17](invalidation-gates-c17-0041-20261023.md)，无须纠正。第一门拒绝候选 `+0x268` word 按 RV32 **有符号解释小于等于0**的情况；候选为空时先加载 `word@62fc9590` 作为回退指针。通过第一门后复制区域，再以原 obj 检查 `+0x24` word 的 bit0，置位则早退。两门共用尾部不改 a0，机器返回分别是0、1，但这不是原始函数业务返回类型的认证。通过两门仍会遇到第三门，不能视为提交或刷新。来源仍为 LVGL 候选，版本/厂商修改未知，无新增开源排除。

## 基线、范围与复核方法

固定基线 `e29de84`，分支 `codex/re-0041-c18`；工作树 `D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c18`。已读本树 rolling-management 的共同规则/C18任务书、`C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md` 及 native guide。本树文件检索、输出路径各级父目录、工作树至盘根和主仓库根均未发现适用 AGENTS.md。仅写 C18 独占报告/分析目录；未改 C17 或共享索引。

先读 C15/C16 和 C17，避免把四word复制的已验收内部实现作为新成果。核心函数仍为三个：入口 `a00ddbf6` 仅前段 `a00ddbf6..a00ddc7d` 与尾部 `a00ddd82..a00ddd8f`；两个查询完整字节范围 `a0081804..a008184d`、`a00d7446..a00d749d`。共4窗口312B、101条连续指令，不代表入口510B全函数已恢复。入口第三门仅保留调用参数与分支边界，未进入 `a00ddab4`；`a00dce2e` 也只保留调用ABI。

[独立核验脚本](../../analysis/invalidation-gates-review-c18-0041-20261023/verify.py)重新读取主仓库只读 ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，沿用 `file_offset=address-0x9ffff000`。本次另写解析器，未运行/复制 C17 脚本；Capstone 全窗口重解码并与 C17 留存原字节/解码逐条比较，关键38处另解析 RV32/RVC 位字段。所有17个直接控制目标均从 ROM 编码重算并与既有目标交叉比较；这不认证诊断 callee 的内部行为。

[本次证据](../../analysis/invalidation-gates-review-c18-0041-20261023/review-evidence.json) 的 `windows` 有原字节、反汇编和字段，`contract_checks` 有地址化断言，`direct_targets` 有控制目标，`strings` 有新读名称字符串。它是本地静态复核证据，不是 REA 新执行观察。继承 REA 范围 Evidence：入口 `ev_01b096f6f3978697c38250d5d77ccdbbef1a5ecb1d99a5940e5612aaa53b2ab1`，第一查询 `ev_8b1d910f2dbb08d1fe09f84f1332189ca90dd78d266faa7db74048f6c74e9eff`，第二查询 `ev_15996d55207e4d9b5c5e32341513b80ce5a198f2e065915ff9c3d3cf5bd7f782`；来源/函数边界以 C17 所引历史 inventory 为准。本次没有打开或共享可写 REA 会话/数据库。

## 逐项验收

表中同一行后续地址省略相同前缀；完整地址以证据为准。

| C17命题 | 结果 | 原指令依据与限制 |
| --- | --- | --- |
| 正常入口参数 a0=obj、a1=area | 接受 | `a00ddc04` C.BNEZ a0 到 `a00ddc46`；`dc46` SW a1,-84(s0)，`dc4a` MV s1,a0。空obj诊断路径不认证普通返回合同。 |
| 第一查询输入为 `a00dce2e` 的机器返回量 | 接受 | `dc4c` JAL `a00dce2e` 后，紧邻 `dc50` JAL `a0081804`，中间没有a0改写。不能将其改称原obj；候选身份/选取机制未核。 |
| 空候选取全局回退 | 接受 | `a0081804` C.BNEZ a0 到 `a0081844`；零时 `1806` LUI a5,0x62fc9，`180a` LW a0,0x590(a5)，`180e` C.BNEZ a0 到同处。回退是地址内的word指针，不是把常量地址当对象。 |
| `candidate+0x268` 是有符号严格大于0测试 | 接受 | `a0081844` LW a0,0x268(a0)，`1848` 原编码 `3325a000`：opcode=51/funct3=2/funct7=0/rd=10/rs1=0/rs2=10，即 signed SLT a0,x0,a0。返回0/1，0和负word均返回0。 |
| 两个候选指针都为空时的静态零返回 | 限定接受 | 该路径含 `a0081836` 到日志 `a008b51a` 的调用，`183e` 明确 LI a0,0，再恢复并JR ra。仅在该日志正常返回前提下成立，不认证诊断系统运行结果。 |
| 第一门返回0早退 | 接受 | `a00ddc54` BEQ a0,x0 到 `a00ddd82`。尚未读取area内容或调用复制；前面的不透明callee副作用未排除。 |
| 区域复制发生在两门之间 | 接受，复制内部继承 | `dc58` LW a1,-84(s0)，`dc5c` ADDI a0,s0,-80，`dc60` JAL `a008b43a`。96B栈帧、s0=sp+96，故目的为本帧sp+16；四word覆盖sp+16..31的复制合同沿用已验收C15/C16，本次未重做其28B函数体。 |
| 第二查询参数是原obj和mask=1 | 接受 | `dc64` LI a1,1；`dc66` MV a0,s1；`dc68` JAL `a00d7446`。不是候选对象或area参数。 |
| flags合同为 `(flags & mask)==mask` | 接受 | 非空 `a00d7446` 跳 `a00d7492`；该处 C.LW a0,36(a0)，`7494` C.AND a0,a1，`7496` C.SUB a0,a1，`7498` SLTIU a0,a0,1，`749c` JR ra。32位word、模2^32差值为零测试，正常路径无字段写入/其他callee。 |
| obj+0x24 bit0置位时第二门返回 | 接受 | 固定mask=1；`a00ddc6c` BNE a0,x0 到 `a00ddd82`。bit0未置位才继续；此时已复制局部区域。bit0正式枚举名称未核。 |
| 共同尾部保留a0，两个早退分别返回0/1 | 接受，C类型未核 | `a00ddd82..ddd8a` 只LW ra/s0/s1/s2/s3，`ddd8c` sp+=96，`ddd8e` JR ra，没有写a0。不能据两条路径为整个入口定义统一成功码。 |
| 通过两门不等于区域提交 | 接受 | `dc70` a1=s0-80，`dc74` a0=s1，`dc76` JAL `a00ddab4`，`dc7a` BEQ a0,x0 到同一尾部。这足以保留第三门边界，未进入其内部或其后提交/队列/刷新。 |
| LVGL候选识别、精确版本/修改未知 | 限定接受 | 重新读取 `lv_obj_invalidate_area`@`a056a378`、`lv_display_is_invalidation_enabled`@`a025f608`、`lv_obj_has_flag`@`a05699b4`；诊断构参/源路径关联继承C17，字符串和局部形状不足以证明未修改实现。 |

没有发现需要纠正 C17 的地址、分支极性、参数、宽度或正常返回合同。诊断调用及第三门存在的静态边已核，callee内部明确未核；C17 提及完整函数其它边/inventory 仅作继承，不扩大本次认证范围。

## 必要结构与伪代码

只定义机器访问的局部结构：候选指针 `d` 的 `+0x268` 为完整word并作signed比较；原 `obj+0x24` 为flags word；`area` 指向按四word复制的区域。候选和原obj不认证为同一对象。下列为描述，不是原C签名或可运行模型：

```c
query_candidate(d):
    if (d == 0) d = load32(0x62fc9590);
    if (d == 0) { opaque_log(); return 0; } // assuming log returns
    return signed32(load32(d + 0x268)) > 0;

query_flags(obj, mask):  // obj != 0
    return (load32(obj + 0x24) & mask) == mask;

entry(obj, area):        // obj != 0
    d = opaque_a00dce2e(obj);
    a0_result = query_candidate(d);
    if (a0_result == 0) goto tail;
    copy_four_words(local_at_sp_plus_16, area); // inherited C15/C16
    a0_result = query_flags(obj, 1);
    if (a0_result != 0) goto tail;
    a0_result = opaque_a00ddab4(obj, local_at_sp_plus_16);
    if (a0_result == 0) goto tail; // boundary only
    /* remaining function not recovered */
tail:
    /* restore saved registers and stack; preserve machine a0 */
```

两门已核正常指令自身不写原obj/area；不能将其提升为所有callee无副作用。复制目的在本帧，只证明局部副本在同步调用期间存在；后续callee是否持有、复制或提交该地址仍未核。没有发现未解厂商指令；选定窗口的间接控制仅为JR ra返回，不能据此排除未恢复区域存在其它间接调用。

## 来源、完成程度与实际验证

事实为上述ROM原字节、位字段、参数与分支；描述为“失效使能查询/对象flags查询”是由名字字符串与指令一致性支持的推断。候选+0x268正式字段名/生产者、obj bit0枚举、原C返回类型、准确LVGL版本/厂商修改、本地可核源版本均未知。遵守C17/C13已有检索边界，不重复泛搜，不外连，不凭库形状排除。

运行本次 `verify.py`：**passed**，4窗口312B/101条连续重解码、38处独立字段合同断言、49项总检查、17个直接目标，以及3条名称字符串新读核对。完整字节/解码与C17留存一致；49项包含窗口逐条比较、关键原字节及源字符串检查，并不等于49个独立函数。未运行C17脚本；没有建立/执行固件模型、历史回放、异常输入或缺陷验证，没有连接设备/外部服务，没有修改ROM/生产代码/安全检查，无新哈希或复制清单。

本次仅完成入口两个门控及两个查询正常合同的独立静态复核；全失效流程尚未完成。小后继建议：另立小任务恢复 `a00ddab4(obj,&local)` 第三门及其正常参数/返回，继续将队列、最终提交与显示刷新保持为边界。

提交操作记录：首次明确三个独占文件的 `git add` 因主仓库 `.git/worktrees/re0041-c18/index.lock: Permission denied` 失败；按已有本地提交授权申请 Git 元数据写入升级后暂存成功，未改权限或绕过安全限制。差异及暂存路径检查在提交前执行。
