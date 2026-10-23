# 0041 C21：变换前置谓词局部合同

结论：`a00dbff4(obj)` 是沿对象链搜索的只读谓词。它对当前节点先读 `word[obj+8]`，非零才读该指针 `+0x32` 的无符号16位值；若 `(value & 0x0c00)==0x0800` 则返回1，否则沿 `word[obj+4]` 继续，链终止返回0。没有区域参数，也没有对象/区域写入；唯一store是自身栈帧保存s0。C19/C20两处非零门因此表示“当前对象或链上节点命中两位字段值2”，不表示本函数已经完成区域变换。该新合同已按原指令核验，**待独立技术复核**；没有恢复a00dca48。

## 范围与证据

固定基线 `fe1fcd4`，分支 `codex/re-0041-c21`，本树 `D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c21`。读rolling-management共同规则/C21任务书、C19/C20报告、REA技能及native guide。检查盘根至本树祖先和reverse输出目录，未发现适用AGENTS.md。先检索已有报告/分析；仅C19/C20引用此callee的两处调用，没有其内部合同，未重复前序交集/第三门分析。收到收尾指示后未扩范围，不创建agent或接后继任务。

唯一核心完整范围 `a00dbff4..a00dc01f`，44B/19指令；仅重核caller窗口 `a00ddb14..a00ddb25` 和 `a00ddb60..a00ddb73`，38B/14指令。总计82B/33指令。ROM只读路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，沿用 `file_offset=address-0x9ffff000`，核心偏移 `0xdcff4`。没有打开或共享可写REA会话/数据库，没有新哈希或复制清单。

[verify.py](../../analysis/transform-predicate-c21-0041-20261023/verify.py)重新取ROM字节，以Capstone 5.0.7按编码宽度逐条解码；独立重算11个直接控制目标并核3个关键I型编码字段，完整比对核心19指令序列及C20既有caller字节。[evidence.json](../../analysis/transform-predicate-c21-0041-20261023/evidence.json)保留原字节、地址、文件偏移、解码、目标、70项机械检查和该函数inventory记录；[instructions.txt](../../analysis/transform-predicate-c21-0041-20261023/instructions.txt)供按地址定位。人工逐条读相同33条指令，机械检查数不是独立语义证明数。

继承whole-ROM inventory Evidence `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2`；extent `ev_bccfc2ce2ae63881bb671e9332979d174d626a00de69b5e0e3462c88480928f3` 给出44B连续body；direct calls `ev_a95ab7e4112973408e57c106ac40300aef1e946e97b75c90f7581c51e578bce4` 为空。新增证据是本地静态核验，非新REA运行记录。该inventory没有来源路径、family、dossier或历史合同，未认证开源排除。

## 参数、返回及读写

| 原指令位置 | 局部合同 |
| --- | --- |
| `bff4/bff6/bffa` | sp减16，保存s0到sp+12，s0=sp+16。没有保存ra或任何调用。 |
| `bff8/bffc` | a4由LUI 1和ADDI -0x400形成0x0c00；不是0x400。 |
| `c000` | C.BNEZ a0到c008，a0为零则落公共尾部c002，保留a0=0返回。入口机器支持零起点；这不认证上游所有对象状态。 |
| `c008/c00a` | 从当前a0+8读32位指针到a5；零时去c018，直接移到下一节点，不读取halfword。 |
| `c00c/c010/c012/c016` | LHU读取a5+0x32，AND 0x0c00，再ADDI -0x800。为零跳c01c，故检查位11:10等于二进制10；其他位不参与结果。 |
| `c018/c01a` | a0=word[a0+4]，C.J回c000重查是否终止；搜索包括起点和后续节点。 |
| `c01c/c01e` | a0=1，跳c002；c002/c004恢复s0/sp，c006 JR ra返回。成功返回恰为1，链终止恰为0。 |

表内bxxx/cxxx均为a00d前缀的完整地址。核心没有厂商扩展、间接调用、全局访问或区域地址获取；唯一间接控制是JR ra返回。直接外部读取仅每个节点的+4/+8及非零aux的+0x32，返回没有暴露匹配节点；a1等传入寄存器完全不读。除栈保存s0外无store，也无callee能隐藏写入。因此在正常ABI/有效对象链前提下，本函数不改写对象、aux或区域，不保留输入指针。无有限迭代计数；本报告不把正常链解释扩为任意输入的终止保证。

最小结构和伪代码（描述机器行为，非原C源码）：

```c
// Node: +4 next/parent word, +8 aux pointer word.
// Aux: +0x32 unsigned halfword; named fields and enums remain unverified.
uint32_t predicate(Node *p) {
    while (p != 0) {
        Aux *aux = load32(p + 8);
        if (aux != 0 && (load_u16(aux + 0x32) & 0x0c00) == 0x0800)
            return 1;
        p = load32(p + 4);
    }
    return 0;
}
```

“parent/祖先”沿用C19结构解释，机器事实只是+4链。“两位字段值2”是掩码等价解释，不认证原C bitfield布局声明或枚举名字。与LVGL对象/变换功能相关是上下文推断；没有本函数来源字符串或准确源码版本证据，故不直接命名为已认证的lv_obj_is_transformed或某个layer_type枚举。

## 调用消费

`a00ddb14/db16`传a0=s1当前原obj；`db1a`零跳db26，非零则 `db1c/db1e/db20/db22`传 `(obj, area=s2, 1)` 给a00dca48。另一窗口 `db60/db62`传a0=s1当前祖先节点；`db66`零跳db74，非零则 `db68/db6a/db6e/db70`传 `(node, temp=s0-48, 1)`。谓词没有接收这两个区域地址；调用期间残留a1不被读取。

由核心链搜索可知，第一门会考虑原obj及其后继链，第二门会考虑该祖先及其后继链。a00dca48收到的仍是caller当时的s1，不是谓词命中的节点；谓词只返回布尔值。两处变换callee的返回均未被此窗口消费。a00dca48具体写入、持有地址、变换参数及完整业务结果均未展开，不能把谓词只读性质推广给该callee或整个第三门。

## 验证、来源状态和未知

实际运行 `python reverse/analysis/transform-predicate-c21-0041-20261023/verify.py`：**passed，82B/33指令/70检查**，核心完整extent与inventory相符，caller字节与已接受C20一致。首次脚本运行因把C20证据字段名误写为pc/raw而失败；按既有address/bytes结构修正后通过，属于证据读取脚本修正，非ROM或前序结论差异。没有运行固件、分析器模型或历史回放，没有连接设备/外部服务，没有畸形输入、漏洞或缺陷验证；未改生产、安全检查、ROM或模型。

原字节、位字段、读宽、分支极性和0/1返回是事实；对象父链、aux和变换枚举业务含义是不同程度的结构推断。局部机器合同已恢复并留存可复核证据，尚待独立技术复核；原源码、准确LVGL版本、厂商修改、字段正式名字、设置该字段的生产者、对象链生命周期、a00dca48内部和完整GUI/失效流程仍未知，无新增认证开源排除、不计算全ROM百分比。按收尾要求停止此处；仅保留小后续建议：未来独立复核此44B谓词后，再另立a00dca48正常区域变换任务，本轮不启动。

提交操作记录：首次明确四个独占文件的git add因 `.git/worktrees/re0041-c21/index.lock: Permission denied` 失败，按已有本地提交授权申请Git元数据操作升级，未改变权限或绕过限制；提交前核明确路径、暂存差异和空白检查。
