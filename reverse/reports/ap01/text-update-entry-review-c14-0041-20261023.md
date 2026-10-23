# 0041 C14：文本更新入口独立复核

结论：限定接受 [C13](text-update-entry-c13-0041-20261023.md)，无须纠正。`a0091ee4` 的 a2..a7 连续保存区、旧文本非空且 bit4 为零才释放的条件、`a008bbd8` 的两遍调用/首遍返回加1/返回申请缓冲，以及入口 `obj+0x2c` 写回后清 bit4 的顺序，均与原始指令相符。只完成两个函数的局部静态合同复核；底层 printf、allocator、完整对象/文本生命周期、准确 LVGL 版本及厂商修改仍未认证，**无新增开源排除**。

## 范围与证据

固定基线 `a10893d`，分支 `codex/re-0041-c14`，工作树 `D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c14`。已读本树 rolling-management 的共同规则、C14 任务书和 `C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md` 及其 native guide。逐级检查本工作树到盘根、输出父目录及主仓库根，未发现适用 AGENTS.md。仅写 C14 独占报告/分析目录，没有修改 C13 或共享索引。

- [独立静态核验脚本](../../analysis/text-update-entry-review-c14-0041-20261023/verify.py)：只读主仓库 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，采用 `file_offset=address-0x9ffff000`；只向 C14 目录输出。
- [本次证据](../../analysis/text-update-entry-review-c14-0041-20261023/review-evidence.json)：`windows` 保留两窗口新读字节与连续反汇编，`raw_encoding_checks` 保留原编码字段核对，`va_layout` 保留相对入口 sp 的六槽布局，`strings/source_search` 保留来源边界。
- [C13 证据](../../analysis/text-update-entry-c13-0041-20261023/instruction-evidence.json)：用于完整字节/解码交叉比较与继承 REA 范围来源；没有执行或复制其核验脚本。入口范围 `a0091ee4..a0091f89` 的 extent Evidence 为 `ev_9bebf4d87defa0d1c2a1cf83c013b26dbd39471d91a976b647a8536709e3b442`，直接调用 provenance 为 `ev_8cb80268149667bc520907372670d32b2e912259897a9eefa88f347dbde5a4fb`；依赖范围 `a008bbd8..a008bc63` 分别为 `ev_88c00ee419366a48bd34b527f212e68bfde147e2cf7fd33216cbbee0edeb3306`、`ev_4a3a5ca0fc65f6d413a5f3e936e89d649bf616a474966461703bc3355c5c0e33`。本次未打开共享可写 REA 会话/数据库，未把历史 Evidence 当作新执行观察。

## 逐项验收

| C13 命题 | 结果 | 本次原指令依据与限制 |
| --- | --- | --- |
| 入口 a0=obj、a1=fmt，a2 起为变参寄存器 | 接受 | `1f42/1f44` 保存 a0/a1 至 s1/s2；`1ef0..1efc` 保存 a2..a7；`1f62/1f68` 将 s2 和 va 传给依赖。原始 C typedef/函数返回类型未认证。 |
| 连续 va 保存区 | 接受 | `1ee4` 的 C.ADDI16SP 原字段为 -64；`1eea` 的 C.ADDI4SPN 为 s0=sp+32。设入口 sp=S，故 s0=S-32。六个 word 槽分别为 S-24/-20/-16/-12/-8/-4；`1f5e` 为 a1=s0+8=S-24，`1f64` 另存局部不改变 a1。末槽结束于 S，与调用者栈区相接。仅证明此 RV32 寄存器保存构造，不认证具体格式类型/64位对齐/浮点传参。 |
| 旧文本非空且 bit4=0 才释放 | 接受 | `1f4a` 从 obj+0x2c 读 word 到 a0，`1f4c` 的 C.BEQZ 跳 `1f5e`；`1f4e` LBU obj+0x5c，`1f52` AND 0x10，`1f54` 的 C.BNEZ 也跳 `1f5e`。仅余路径在 `1f56` JAL `a008ab8a`，再由 `1f5a` SW zero 至 obj+0x2c。 |
| 读取旧文本在前置调用之后 | 接受 | `1f46` JAL `a00dddf4(obj)`，返回后 `1f4a` 才读旧文本。前置 helper 内部未复核，不假设旧文本在该调用前后不变。 |
| 首遍底层调用 `(0,0,fmt,va)` | 接受 | `bbe2/bbe4` 搬 a0/a1 至 a2/a3，`bbe6/bbea` 保存 va/fmt；`bbee/bbf0` 清 a1/a0，`bbf2` JAL `a0053252`。 |
| 首遍返回加1作为申请量 | 接受 | `bbf6` 是 ADDI a1,a0,1，`bbfa` 搬至 a0；`bbfc` 保存该值，`bc00` JAL `a008aea0`。只认证32位机器加法与实参，不额外认证有符号长度域。 |
| 第二遍 `(buf,size,fmt,va)`，返回 buf | 接受 | `bc04/08/0c` 从本帧重载 size/fmt/va 到 a1/a2/a3；a0 为申请返回。`bc10` C.BNEZ a0 跳 `bc52`，`bc52` 保存 a0 至 s1，`bc54` 再调同一 `a0053252`；`bc5c` 明确把 s1 写回 a0。因此忽略第二遍返回，返回最初缓冲指针。 |
| 入口先写 obj+0x2c，再清 bit4、再刷新 | 接受 | `1f6c` 先 LBU flags，`1f70` C.SW 返回 a0 至 obj+0x2c，`1f72` a0=obj，`1f74` AND -17，`1f76` SB flags 至 obj+0x5c，`1f7a` JAL `a009166e`。新指针直接入槽；没有另调复制文本 setter。 |
| bit4 表示静态/借用文本属性 | 接受为推断 | 原编码只给“跳过本次释放/随后清位”行为，不能认证原始位域名、完整所有权类型或其他路径生命周期。 |
| 首遍求长度、+1留终止符、第二遍写格式文本 | 接受为强推断 | 自报函数名与上述实参数据流支持；本次没有展开 `a0053252`，所以长度约定、NUL、格式能力以及 va 指向内容是否被修改均未核。相同 va 地址不证明内容未变。 |
| NULL/申请失败诊断的返回属性 | 未核，保留边界 | `1f00` 非零跳正常入口，零路径调日志及 `a0019672`；`bc10` 非零跳第二遍，零路径也调日志及 `a0019672`。布局上落入后续代码不证明诊断会返回。只描述正常非空对象、申请非零路径。 |
| `a008ab8a` 完整释放/allocator/GUI 刷新/对象生命周期 | 未核，保留边界 | 只核上述调用地址、实参、顺序；C13 对既有 C03/C04 释放封装合同的引用不是本次新增复核。`a008aea0`、`a009166e`、`a00dddf4` 均未展开。 |

所有位置省略前缀时，`1exx/1fxx` 属于 `a009xxxx`，`bbxx/bcxx` 属于 `a008xxxx`。本次对15个全部直接控制目标从原编码位独立解算，检查 JAL 的 rd=ra，以及四条压缩条件分支的寄存器和分支极性；关键存取采用原编码的寄存器、偏移和宽度字段核对，并非仅信反编译文字。

## 局部合同与必要伪代码

`a0091ee4` 的局部参数为 obj、fmt、由 a2..a7 与后续栈区构造的 va 起点；最终 `a009166e(obj)` 后仅恢复栈/寄存器，没有独立建立可认证的业务返回值。`a008bbd8(fmt,va)` 在申请非零分支明确返回申请所得 buf。结构只需 `word@obj+0x2c`、`byte@obj+0x5c`；完整对象类型及大小未知。

以下表达指令顺序，不是原始源码、可执行参考模型或完整失败处理：

```c
// 仅 obj != 0，且申请返回非零的路径。
opaque_a00dddf4(obj);
old = WORD(obj + 0x2c);
if (old != 0 && (U8(obj + 0x5c) & 0x10) == 0) {
    release_a008ab8a(old);
    WORD(obj + 0x2c) = 0;
}
// 此段为 a008bbd8(fmt, va) 的局部展开。
n = opaque_a0053252(0, 0, fmt, va);
size = wrapping_add32(n, 1);
buf = opaque_a008aea0(size);
opaque_a0053252(buf, size, fmt, va);
// a008bbd8 返回 buf，而非第二遍返回值。
flags = U8(obj + 0x5c);
WORD(obj + 0x2c) = buf;
U8(obj + 0x5c) = flags & ~0x10;
opaque_a009166e(obj);
```

## 来源、恢复程度与实际验证

重新只读四条 ROM 字符串，确认 `lv_label_set_text_fmt`@`a02647f4`、`lv_text_set_text_vfmt`@`a0263794` 与两条 `.../lvgl/lvgl/src/widgets/label/lv_label.c`@`a02641a0`、`.../lvgl/lvgl/src/misc/lv_text.c`@`a0263224` 路径和 C13 相符。完整两窗口反汇编的诊断构参指向这些地址。它们支持命名/来源候选，不能单独证明与某一上游版本等价。

再次限定检索主仓库 `reverse/sdk`、`tooling` 两根下 `lv_label.c/lv_text.c/lv_version.h/lvgl.h/lv_mem.c` 五个文件名，0匹配。该负结果仅覆盖这两个目录/五个名字，不代表全机无源码。准确版本、厂商修改、原始 typedef 未认证；不基于库形状或函数名作开源排除。

实际执行 `python reverse/analysis/text-update-entry-review-c14-0041-20261023/verify.py`，输出 `passed`：2窗口306B、101条连续解码、51项独立原编码字段检查、15个全部直接控制目标、4条来源字符串；新读字节/反汇编逐条与 C13 证据相同。脚本没有执行 C13 verifier，没有执行固件或模型；未连接设备/外部服务、未构造输入、未运行历史回放；未改 ROM、生产代码、安全检查或分析器模型；未新建哈希/复制清单。

提交前首次显式路径 `git add` 因 `.git/worktrees/re0041-c14/index.lock: Permission denied` 失败；依已有本地提交授权申请 Git 元数据写入升级后成功。没有改变权限、Git 配置或绕过安全限制。

**事实**为原字节/连续边界、va六槽、参数/控制目标/存取宽度、释放条件和写回顺序；**推断**为 LVGL 来源候选、bit4的业务命名与两遍格式化业务意图；**未知**为下层 formatter/allocator/刷新/诊断返回、完整生命周期、版本/厂商修改及运行时可达性。两个局部合同已复核，不能据此宣称完整文本系统恢复。

小后继建议：仅在现有本地 SDK/参考材料存在可靠候选时，开展两个函数的 LVGL 来源/版本/修改边界核对；没有候选则交付有界未知，避免重做本次两目录同名负搜索。直接前置 helper `a00dddf4` 尚未展开，但其业务与私有来源也未知，不因邻接本入口将其判为私有功能。
