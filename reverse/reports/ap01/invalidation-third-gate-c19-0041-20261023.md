# 0041 C19：失效入口第三门局部合同

结论：`a00ddab4(obj,area)` 把第二参数作为**可原地改写的四word区域**。通过候选对象身份门后，它先用原对象的扩张区域做交集，再沿 `obj+4` 指针链检查标志并逐级裁剪。机器返回为0或1；`a00ddbf6` 在 `a00ddc7a` 仅消费零/非零，零时直接公共尾部，非零才继续尚未恢复的后段。返回0也可能已经改写area，不能解释成无副作用拒绝；返回1不证明最终提交或显示刷新。部分变换callee仍不透明，准确LVGL版本/厂商修改未知，无新增开源排除。

## 范围、来源与方法

固定基线 `dde1cfd`，分支 `codex/re-0041-c19`，工作树 `D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c19`。已读rolling-management共同规则/C19任务书、REA技能和native guide。工作树文件及输出父目录、工作树到盘根未发现适用AGENTS.md。先检索本树后续报告：C17/C18仅留第三门边界，没有其内部合同，故未重复已验收的前两门/复制实现。

三个核心函数完整范围为 `a00ddab4..a00ddbf5`（322B）、`a00892ac..a00892cf`（36B）、`a00892f4..a0089349`（86B）。入口仅重核既有调用消费窗口 `a00ddc70..a00ddc7d`（14B）及共同尾部 `a00ddd82..a00ddd8f`（14B），没有展开入口后段。总计5窗口472B/169条指令；这不代表失效入口全函数恢复。

[verify.py](../../analysis/invalidation-third-gate-c19-0041-20261023/verify.py)只读主仓库ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，沿用 `file_offset=address-0x9ffff000`。普通指令用Capstone逐条重解码；四条厂商字独立拆opcode/rd/funct3/rs1/rs2/funct7，与既有只读 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 的 `th.mvnez` 构造及语义核对，未修改模型。没有打开或共享可写REA会话/数据库。

[instruction-evidence.json](../../analysis/invalidation-third-gate-c19-0041-20261023/instruction-evidence.json)保留每条原字节、地址、解码、40个直接控制目标及分支字段、69项断言、三个inventory记录和来源字符串。继承whole-rom inventory `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2`；三个extent Evidence依次为 `ev_52b6741c49402fea0118bbbe5b45ed257faff994d30e0c79e42ec57854d94da5`、`ev_23a3dc62223675713fb06135f3b88a3b419c6e0d044ab1c2d756dabebd15510c`、`ev_c22822040d3e133823f243f0a1c5e93e26b2f3e8d5744cfbe43c23f14a22c166`。本次证据是本地静态核验，非新REA运行观察；三个历史记录均没有dossier/合同，均未认证开源排除。

## 参数、局部和分支事实

| 地址 | 原指令合同 |
| --- | --- |
| `a00ddab4..dac8` | 建80B帧，s0=sp+80；s1保存a0原obj，s2保存a1区域指针。指令本身没有空obj检查。 |
| `daca..dada` | `a00dcdd8(obj)` 返回存s3，原样交 `a00dce2e`，返回存s4，再原样交 `a0080eba`；s3与其返回相等才进 `dade`，否则去 `db84`。不能把这些返回值统称原obj。 |
| `db84..dbf4` | s5先取s4；s4非零则读s5+0x2d0；否则读 `word@62fc9590` 为回退，回退非零也读+0x2d0。两者均零时调用 `a008b51a`，若返回则继续比较。`dbb8`比较s3与s5，相等入 `dade`；否则分别以s4（仍可能为零）调用 `a0080f9e/a0080f06/a0080f52` 并比较s3；任何相等入 `dade`，全不等去 `dbda`清s3。日志返回属性、各getter内部和字段正式名称未核。 |
| `dade..dafe` | 读 `word[obj+8]`，交已验收 `a01ad6d8` 取扩张量e，暂存s0-68；已验收 `a008b43a` 从obj+0x14复制四word到s0-64（本帧sp+16..31），随后调用 `a00892ac(local,e,e)`。依赖的复制/取值合同继承C15/C16。 |
| `db02..db10` | `a00892f4(area,area,local)`；返回存s3；为零跳 `dbda`。该调用在判断前已写area四word。 |
| `db14..db22` | `a00dbff4(obj)` 非零时调用 `a00dca48(obj,area,1)`，其返回不参与判断。该callee可能修改area，内部未恢复。 |
| `db26..db32` | s1=`word[s1+4]`；为空直接尾部（保留s3=1）。非空以 `a00d7446(s1,1)` 查询已验收flags；非零去 `dbda`返回0。此处obj+4解释为父链是结构推断；读宽与迭代事实明确。 |
| `db34..db5c` | `a000589c(s0-48,s1+0x14,16)` 返回被覆盖；复制语义为常见memcpy形状推断，内部未核，不能将其与已验收a008b43a混同。临时区域s0-48为sp+32..47。`a00d7446(s1,0x100000)` 非零则取 `a01ad6d8(word[s1+8])`，调用 `a00892ac(temp,e,e)`。 |
| `db60..db80` | `a00dbff4(s1)` 非零时调用 `a00dca48(s1,temp,1)`；随后 `a00892f4(area,area,temp)`。返回非零回 `db26`读下一级，零到 `dbda`。循环没有把最终交集返回另存s3，但s3已是首次交集的1。 |
| `dbda..dbee` | 失败统一s3=0；尾部恢复寄存器并将s3搬到a0再返回。成功只由父链空结束，a0=首次交集保存的1。条件均以不透明callee正常返回为前提。 |
| `a00ddc70..dc7a` | caller以a0=原obj、a1=s0-80（96B帧的sp+16局部副本）调用本helper；BEQ a0,x0到 `a00ddd82`，其14B尾部不改a0；零早退机器值为0。非零落入 `a00ddc7e`，本次不恢复其后段。 |

上表省略地址前缀 `a00d` 的daxx/dbxx均为完整证据中的对应地址。主helper完整直接callee集合与inventory15项一致：`a000589c/a0080eba/a0080f06/a0080f52/a0080f9e/a00892ac/a00892f4/a008b43a/a008b51a/a00d7446/a00dbff4/a00dca48/a00dcdd8/a00dce2e/a01ad6d8`。其中两短依赖无callee；范围内间接控制仅JR ra返回，无未解厂商指令。ABI边核对不等于这些callee内部已恢复。

## 两个短依赖和必要伪代码

最小区域结构为按偏移0/4/8/12读取的四个32位word：描述为x1/y1/x2/y2由signed交集模式支持，并非原C类型认证。`a00892ac(a0=area,a1=ex,a2=ey)` 按机器模2^32计算 `[x1-ex,y1-ey,x2+ex,y2+ey]`，直接写回四项，a0始终保留输入指针；本helper内两个调用都不消费其返回。

`a00892f4(dst,left,right)` 以signed32比较，先逐项写出 `[max(left.x1,right.x1),max(left.y1,right.y1),min(left.x2,right.x2),min(left.y2,right.y2)]`，再判断x2>=x1和y2>=y1返回0/1。边界相等允许返回1。写入发生在有效性交集判断之前，0返回也保留已写值。每项都先读对应left/right项再写同偏移，支持本调用中的dst==left；不延伸到其他重叠形式。

四条厂商指令 `a0089304/9314/9322/9330` 原字分别为 `0x42e7980b/0x42d7178b/0x4317168b/0x42c5970b`，字段均opcode=0xb、funct3=1、funct7=33。既有模型语义是rs2非零时rd=rs1，否则保留rd。前两条结合 `9300/9310` 的signed SLT选择max，后两条结合 `931e/932c` 选择min；`9338` BLT和 `933c` SLT/`9340` XORI 1给出inclusive有效判断。未仅凭反编译器名称判定min/max。

以下是结构描述，不是原C源码，也没有执行：

```c
third_gate(obj, area):
    root = opaque_a00dcdd8(obj);
    d = opaque_a00dce2e(root);
    if (root != opaque_a0080eba(d)) {
        fallback = d != 0 ? d : load32(0x62fc9590);
        if (fallback != 0) previous = load32(fallback + 0x2d0);
        else { opaque_log(); previous = 0; } // only if log returns
        if (root != previous &&
            root != opaque_a0080f9e(d) &&
            root != opaque_a0080f06(d) &&
            root != opaque_a0080f52(d)) return 0;
    }
    local = copy4(obj + 0x14); // inherited a008b43a
    e = inherited_aux_word(load32(obj + 8));
    expand(local, e, e);
    first = intersect(area, area, local);
    if (first == 0) return 0;
    if (opaque_a00dbff4(obj) != 0) opaque_a00dca48(obj, area, 1);
    p = obj;
    while ((p = load32(p + 4)) != 0) {
        if (inherited_has_flags(p, 1)) return 0;
        temp = opaque_copy16(p + 0x14); // a000589c, internal semantics unverified
        if (inherited_has_flags(p, 0x100000)) {
            e = inherited_aux_word(load32(p + 8));
            expand(temp, e, e);
        }
        if (opaque_a00dbff4(p) != 0) opaque_a00dca48(p, temp, 1);
        if (intersect(area, area, temp) == 0) return 0;
    }
    return first; // exactly 1 under verified intersection contract
```

伪代码把初始取e和copy写成便于阅读的独立准备；ROM中实际先取e后copy。`opaque_copy16`表达参数形状而不认证复制内容；实际ABI为(dst,src,16)。主helper自身不直接store原对象字段，除栈外直接外部写都在已核交集/扩张依赖；其他不透明callee可能有副作用。a00dca48获得area或本帧temp地址，其复制/保存/生命周期尚未知，不能由同步调用形式排除持有地址。caller原始area已经先复制到自己的栈，第三门写的是该副本；不得声称其原始输入area被本次直接写入。

## 事实、推断、未知和验证

事实为ROM字节、参数宽度、栈布局、直接控制极性、min/max写入顺序和0/1返回。对象父链、矩形扩张/交集是指令模式支持的结构解释；候选对象/显示getter含义只作来源推断。新读字符串 `lv_display_get_screen_prev`@`a056a2ac`、诊断文本@`a0569e28`、`.../lvgl/src/display/lv_display.c`@`a025e3d8`，与上一候选路径相关，但主helper的inventory来源关联来自其直接callee族，不证明主helper就是该getter或开源原版。没有外连搜源，没有重复C13之后的无可靠版本泛搜。

未知包括obj+4/+8/+0x14及候选+0x2d0的正式结构名、mask0x100000枚举、a000589c复制内部、a00dbff4/a00dca48变换性质与写入/持有、各身份getter的内部、诊断返回属性、调用者完整返回类型、全失效队列、最终提交和显示刷新、准确源码版本及厂商修改。三个局部机器合同完成；带不透明依赖的上层完整业务功能仍未恢复。

实际执行本次 `verify.py`：**passed**，5窗口472B/169条连续指令，69项断言、40个编码重算直接控制目标、4条厂商位字段与只读模型语义核对，三个核心extent/完整直接调用集合与inventory一致。没有运行固件、模型、历史UART/回放、畸形输入或缺陷验证；没有连接设备/外部服务，未改ROM/生产/安全检查/模型，无新哈希或复制清单。

小后继建议：先独立复核本次身份分支、四条厂商选择指令和原地交集失败写入合同；随后可另设小任务仅恢复 `a00dbff4/a00dca48` 的area直接变换合同，继续保留完整失效队列/显示刷新边界。

提交操作记录：首次明确三个独占文件的 `git add` 因 `.git/worktrees/re0041-c19/index.lock: Permission denied` 失败；依据既有本地提交授权申请Git元数据写入升级后成功，未改权限或绕过限制。提交前检查暂存路径与差异。
