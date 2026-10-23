# 0041 C17：失效区域入口两道返回门

结论：`a00ddbf6(obj,area)` 正常非空入口先调用 `a00dce2e(obj)`，将其机器返回指针直接传给 `a0081804`；后者返回0时立即走公共尾部。通过第一门后复制四word区域到本帧，再调用 `a00d7446(obj,1)`，返回1时同样立即返回。第一门的直接依赖检查候选对象 `+0x268` 的完整32位 word 是否**有符号大于0**，第二门检查原对象 `+0x24` word的bit0是否置位。两个早退路径的机器a0分别为0、1，但不能据此定义整个入口的成功/失败返回类型。通过两门后仍有第三门，**没有认证区域提交、显示刷新或完整失效流程**。来源为LVGL候选，精确版本/厂商修改未认证，无新增开源排除。

## 范围、基线与证据

固定基线 `f482b78b026a01558e3df76fc8b241f437f47cd7`，分支 `codex/re-0041-c17`，本树 `D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c17`。已读本树 rolling-management 的共同规则/C17任务书、REA SKILL.md及native guide；本树递归、逐级父目录至盘根与主仓库根均未发现适用AGENTS.md。只写C17独占目录/报告，不操作共享可写REA会话或数据库。

先检索既有成果：[C15](text-precondition-c15-0041-20261023.md)/[C16](text-precondition-review-c16-0041-20261023.md)恢复了 `a00dddf4(obj)` 以局部四word区域调用本入口的合同，但明确未恢复下游；C11/C12仅消费flag查询返回，没有展开查询实现。继承 [inventory](../../analysis/whole-rom-coverage-0041-20261023-round1.json) 中本入口和两个查询函数均 `dossiers=[]`、`historical_contracts=[]`，没有重复已恢复合同。

本次三个核心函数范围为：入口仅 `a00ddbf6..a00ddc7d` 与公共尾部 `a00ddd82..a00ddd8f`（150B）；两个直接依赖 `a0081804..a008184d`（74B）和 `a00d7446..a00d749d`（88B）完整读取/解码，诊断callee仍保持边界。入口inventory完整范围510B不等于本次全函数恢复。`a00dce2e`只保留原始调用ABI边，未恢复其内部或对象身份映射。

ROM绝对只读路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；沿用 `file_offset=address-0x9ffff000`。[本次证据](../../analysis/invalidation-gates-c17-0041-20261023/instruction-evidence.json) 的 `windows` 给逐指令原字节/反汇编，`raw_checks`给独立位字段断言，`targets`给全部直接控制目标，`strings`给新读字符串。没有执行固件或业务模型。

历史REA范围Evidence：入口 `ev_01b096f6f3978697c38250d5d77ccdbbef1a5ecb1d99a5940e5612aaa53b2ab1`，第一依赖 `ev_8b1d910f2dbb08d1fe09f84f1332189ca90dd78d266faa7db74048f6c74e9eff`，第二依赖 `ev_15996d55207e4d9b5c5e32341513b80ce5a198f2e065915ff9c3d3cf5bd7f782`；入口直接边 `ev_22c77e0c90ca0918b5dfd2a9e0cc5cb837635259cf4948b958a4842b621f7207`。这些是继承静态来源，新结论另以本次ROM原编码建立，不是运行观察。

## 参数、字段与分支合同

| 地址 | 原指令事实及合同 |
| --- | --- |
| `a00ddbf6..a00ddc04` | 建96B栈帧，s0=sp+96；非空a0在 `dc04` 跳 `dc46`。空对象路径调用日志/诊断，未进入其callee或认证普通NULL返回。 |
| `a00ddc46..dc50` | a1=area保存到s0-84，s1=a0保存原obj；`dc4c` JAL `a00dce2e`，`dc50`立即JAL `a0081804`，中间无a0变换。故第二个callee的输入是前者返回量，不可替换为原obj。 |
| `a0081804..180e` | 输入a0=d；非零跳 `1844`。零输入则LW读取word@`62fc9590`，该值非零也跳 `1844`；这不是指向该地址的直接对象，而是该地址存放的指针。 |
| `a0081844..184c` | LW a0,0x268(a0)，随后原编码 `SLT a0,x0,a0`（显示为SGTZ），返回严格0/1。只有该word按RV32有符号解释大于0才返回1；不是任意非零测试，负word返回0。 |
| `a0081810..1842` | 输入和回退指针均为空时，调用日志 `a008b51a`；若日志正常返回，`183e`明确置a0=0并返回。不把诊断实际执行/返回保证为运行事实。 |
| `a00ddc54` 第一门 | BEQ a0,x0 跳 `a00ddd82`。因此上述query返回0时立即返回，尚未调用本入口的区域复制。返回1才继续。 |
| `a00ddc58..dc60` | 从保存槽重载area到a1，a0=s0-80，调用 `a008b43a(dst,src)`。四word同步复制合同沿用C15/C16，本次核实本调用的两个参数及目标，未重做该已验收依赖。局部四word位于本帧sp+16..31。 |
| `a00ddc64..dc68` | a1=1，a0=s1（原obj），JAL `a00d7446`。不是传候选对象，也不是传区域地址。 |
| `a00d7446/7492..749c` | 非空obj跳到 `7492`，LW读取obj+0x24完整word到a0；C.AND a0,a1；C.SUB a0,a1；SLTIU a0,a0,1（SEQZ）；返回严格0/1，即 `(flags & mask)==mask`。正常路径没有写对象字段，没有其他callee。一般mask=0将返回1；本调用固定mask=1。 |
| `a00ddc6c` 第二门 | BNE a0,x0 跳 `a00ddd82`。所以原obj的bit0置位时早退；bit0未置位才继续。此门发生在局部复制之后，不能说两门都在复制之前。 |
| `a00ddd82..ddd8e` | 两门共同尾部只恢复ra/s0/s1/s2/s3/sp并JR ra，未改a0。所以第一门机器返回0，第二门机器返回1；未认证原始C返回类型或整个函数统一业务状态码。 |
| `a00ddc70..dc7a` 范围边界 | 通过两门后，a0=原obj、a1=s0-80，调用 `a00ddab4`；其返回0也跳公共尾部。这里只记录第三门存在及参数，不恢复其内部、不推出通过两门即提交。 |

表内 `dcxx/ddxx` 均为 `a00dxxxx`。本入口正常所见直接调用顺序是 `a00dce2e → a0081804 → a008b43a → a00d7446 → a00ddab4`；全函数其他直接边保留inventory，但不作为已恢复下游。完整两个小依赖中可见的其他调用只在诊断路径，`a00d7446`空路径含 `a008b51a/a0019672`，均未扩展。选择窗口没有未解厂商指令或间接业务调用，JR ra是返回。

## 必要结构与伪代码

只建立32位机器视图：`obj+0x24`为flags word；第一query候选指针 `d+0x268`为被signed测试的word；`word@62fc9590`为query空输入时的回退指针。未认证完整对象结构、字段生产者、LVGL枚举名称或计数器用途。obj、d与area不能混为同一对象。

```c
// Descriptive normal-path pseudocode, not recovered C signature or an executable model.
query_enabled(d):
    if (d == 0) d = load32(0x62fc9590);
    if (d == 0) { opaque_log(); return 0; } // if log returns normally
    return signed32(load32(d + 0x268)) > 0; // strict 0/1

query_flags(obj, mask):
    // obj != 0; NULL diagnostic contract is outside scope.
    return (load32(obj + 0x24) & mask) == mask; // strict 0/1

entry(obj, area):
    // obj != 0
    d = opaque_a00dce2e(obj);
    r = query_enabled(d);
    if (r == 0) goto epilogue;    // machine a0=0
    copy_four_words(local, area);
    r = query_flags(obj, 1);
    if (r != 0) goto epilogue;    // machine a0=1
    r = opaque_a00ddab4(obj, local);
    if (r == 0) goto epilogue;    // boundary only
    // Remaining invalidation workflow is not reconstructed.
epilogue:
    // For the two investigated early exits: restore registers, preserve machine a0.
```

第一门前没有读取area内容，只有保存指针；第二门前已发生栈内复制。两门正常路径本体没有写原obj或area；不由此排除 `a00dce2e`、日志或后续callee的其他副作用。C15局部area在同步调用期间有效，本次只确定复制到另一栈局部；该局部在后续callee是否被复制/持有仍未知，不认证完整生命周期。

## 来源、恢复程度与验证

事实：新读字符串 `lv_obj_invalidate_area`@`a056a378`（入口诊断a3构参）、`lv_display_is_invalidation_enabled`@`a025f608`（getter诊断a3）、`lv_obj_has_flag`@`a05699b4`（flag诊断a3），以及对应 `lv_obj_pos.c`、`lv_display.c`、`lv_obj.c`源码路径，与本次指令合同一致。推断：第一query可描述为显示失效使能检查，第二是对象flags匹配；bit0的正式枚举含义不由常见库习惯补造。`a00dce2e`返回量可能关联显示对象，但本任务不认证其选取机制、有效性或跨调用身份稳定性。

准确LVGL版本、本地可核来源和厂商修改仍未知；未重复C13已有无可靠候选的泛搜，不外连。字符串/结构相似不等于未修改开源实现，未新增排除。两门及两个依赖正常合同已局部恢复，入口其余队列、屏幕刷新、第三门内部及诊断系统未恢复，整体功能尚未完成。

运行 [verify.py](../../analysis/invalidation-gates-c17-0041-20261023/verify.py) 结果 `passed`：4窗口312B、101条连续解码、42项独立原编码断言、17个全部直接控制目标；关键断言包括位宽、signed SLT、flags AND/SUB/SLTIU、两个分支的寄存器/方向/同一目标、参数保存/重载/常量1、公共尾部原字节和三条函数字符串。三个核心函数inventory边界相符；继承完整范围不被当作本次覆盖。无固件/模型/历史回放执行、设备或外部服务连接，无异常输入/缺陷验证，无ROM、生产代码、安全检查或分析器模型变更，无新哈希/复制清单。

小后继建议：先独立复核本次两门及signed判定，随后可单独恢复 `a00ddab4(obj,&local)` 第三门，保持完整失效队列/刷新为边界。

提交前明确三个独占路径的首次 `git add` 被Git元数据 `index.lock: Permission denied` 阻止；遵照已有本地提交授权申请升级，不改权限或绕过安全限制。最终暂存范围和差异检查由提交步骤记录。
