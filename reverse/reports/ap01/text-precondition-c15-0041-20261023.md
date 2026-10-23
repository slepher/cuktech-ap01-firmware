# 0041 C15：文本入口的区域准备调用

结论：`a00dddf4(obj)` 在正常非空对象路径中，把 `obj+0x14` 起的四个 word 复制到栈，再以 `a01ad6d8(word[obj+8])` 的返回量对前两项做减、后两项做加，最后调用 `a00ddbf6(obj,&local)`。自身没有正常条件早退，也不把读取量作为布尔门控。C13 的文本入口忽略返回，随后读取旧文本。ROM 的函数名字符串为 `lv_obj_invalidate`；这支持 LVGL 来源候选，但精确版本、厂商修改和下游最终提交行为仍未知，**无新增开源排除**。

## 范围、来源与复用

固定基线 `c021206`，分支 `codex/re-0041-c15`，工作树 `D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c15`。遵守 rolling-management 的共同规则/C15 任务书，已读 `C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md` 及 native guide。逐级检查本树至盘根、主仓库根，未发现适用 AGENTS.md。仅写本报告及 C15 专属分析目录。

先检索已有报告：C11/C12 仅记录 `a00dddf4` 调用边，C13/C14 明确没有展开其内部。[既有 coverage inventory](../../analysis/whole-rom-coverage-0041-20261023-round1.json) 中该函数 `dossiers=[]`、`historical_contracts=[]`，只有函数体范围/直接边/来源候选，因而本次补的是尚未恢复合同。“前置 helper”只是本任务相对文本入口的标签，不是断言或参数验证职责的命名。

完整恢复范围为三个函数：主函数 `a00dddf4..a00dde99` 166B，直接依赖 `a01ad6d8..a01ad6eb` 20B、`a008b43a..a008b455` 28B。另核 C13 调用后续 `a0091f42..a0091f4d` 12B。曾只读查看 `a00ddbf6` 相邻反汇编以判断范围；没有把该 510B 函数纳入恢复/验证，不据此提出内部合同。

本次不打开共享可写 REA 会话/数据库。继承的 REA 范围 Evidence 依次为 `ev_78a1b6c59ae47ef1857c565c37c495d3aca62b1af47147ab7196295a005414d0`、`ev_bb62d13f093eb196ceb0e2d9212d4b3454f9ec97f84ef7f6df5195d3dfb9bca5`、`ev_ba5e69e512eb6d0f6f74db5d84b44c03157ca7a957e43afb96689e829f2d5f94`；主函数直接边 Evidence 为 `ev_c56ec829cd902650b88377bad49644eb79f1fe3008d4f58fe4c8768751cd50aa`。它们是历史静态来源，不是新执行观察。

## 原始指令合同

所有地址可在[新读 ROM 指令与原编码核对](../../analysis/text-precondition-c15-0041-20261023/instruction-evidence.json)的 `windows`、`raw_checks`、`targets` 定位。ROM 只读路径为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，沿用 `file_offset=address-0x9ffff000`。

| 地址/函数 | 参数、行为与返回 |
| --- | --- |
| `a00dddf4` | 正常输入 a0=obj；`dde00 c.bnez a0,+0x42` 到 `dde42`。NULL路径构造诊断调用 `a008b51a` 及 `a0019672`；不展开断言系统，不把它认证为普通 NULL 返回或必不返回。 |
| `dde42..dde4a` | s1=a0 保存 obj；`dde44 c.lw a0,8(a0)` 后 `dde46` JAL `a01ad6d8`，s2 保存 a0。输入实际是 obj 的 +8 word，不是 obj 自身。 |
| `a01ad6d8` | a0=p。`d6de c.beqz a0,+0xa`；非零 `d6e0 c.lw a0,0x2c(a0)`；零路径 `d6e8 c.li a0,0`。两路共同恢复栈并返回。返回 0 或 p+0x2c 的完整32位 word，没有额外截断/符号扩展。 |
| `dde4c..dde54` | a1=obj+0x14，a0=s0-0x20（当前栈首）；JAL `a008b43a`。 |
| `a008b43a` | a0=dst、a1=src；顺序以 word 读取 src+0,+4,+8,+12 并写 dst 同偏移，覆盖16B。没有调用/条件分支/申请/释放。a0没有改写，机器返回仍为原dst；原始C返回类型未认证。 |
| `dde58..dde86` | 从 s0-0x20,-0x1c,-0x18,-0x14 读取四项，前两项各减 s2，后两项各加 s2，再按 word 写回。RISC-V 32位算术，不从静态指令补造有效数值范围。 |
| `dde5c/dde60/dde8a` | a1=&local，a0=obj；在四次写入后 JAL `a00ddbf6`。这是整个正常非空路径的无条件调用；该 callee 的内部是否接受/拒绝区域仍未知。 |
| `dde8e..dde98` | 只恢复 ra/s0/s1/s2/sp并返回，不读取或判断 callee 的 a0，也不合成成功码。机器上 a0 沿用末次 callee 的结果；该值的类型/含义未知。 |
| `a0091f42..1f4c` | C13入口在 `1f46` 调用 `a00dddf4`；`1f4a` 随即 `c.lw a0,0x2c(s1)` 覆盖返回寄存器，再判断旧文本。故该调用点不以 helper 返回值门控文本更新。 |

主函数直接调用全集核为 `a008b51a`、`a0019672`（诊断分支）以及 `a01ad6d8`、`a008b43a`、`a00ddbf6`（正常路径）。两个小依赖都没有直接 callee。所有已恢复函数均未出现未解厂商指令或间接调用，`c.jr ra`为返回。

必要结构只定义实际访问，不认证完整对象布局：

```c
// 32-bit word view; descriptive names, not recovered original C types.
// obj+8: auxiliary pointer; obj+0x14..0x23: four words.
// auxiliary+0x2c: expansion word, if auxiliary != 0.
void descriptive_a00dddf4(ObjectPartial *obj) {
    // Normal non-NULL path only; diagnostic branch remains a boundary.
    uint32_t amount = obj->aux_at_8 ? load32(obj->aux_at_8 + 0x2c) : 0;
    uint32_t local[4];
    copy_four_words(local, obj_bytes(obj) + 0x14);
    local[0] -= amount; local[1] -= amount;
    local[2] += amount; local[3] += amount;
    opaque_a00ddbf6(obj, local);
    // No successful-status predicate is reconstructed.
}
```

这里 `uint32_t`只表达机器模2^32加减；坐标的原始有符号类型/范围未认证。局部内存由主函数栈持有，`a00ddbf6` 同步调用期间取得其地址；该函数是否复制/持有地址没有展开，不能由局部栈形式认证全生命周期。主函数自己未申请或释放文本，不能据此断言其 callees 无其他副作用。

## 事实、推断与未知

事实：`dde16/1a/2c` 的诊断构参指向行号 `0x354`、`lv_obj_pos.c`@`a02645f0`、`lv_obj_invalidate`@`a056a33c`；`dde0a/24` 指向 `obj != NULL`@`a0263318`。脚本重新读取这三条 NUL 结尾字符串并核值。四word复制、32位扩展及末次调用均来自正常路径原编码，不依赖反编译推断。

推断：四项可合理描述为一个区域的两角，读取量是区域外扩量，整个函数与字符串命名的对象失效区域准备职责一致。这不认证屏幕已刷新、像素改变或最终提交。两个依赖没有单独来源证据；不因相邻调用将其自动称私有。

未知：`obj+8` 的正式类型、+0x2c 字段生产者和数值域、下游 `a00ddbf6` 的内部接受门控/提交副作用/返回含义、完整 GUI/文本生命周期、原始函数返回类型、准确 LVGL 版本及厂商改动。未重做 C13 已做的无可靠候选 LVGL 泛搜，不外连，不新增开源排除。当前仅恢复三个局部合同，整体功能未完成。

## 实际验证与后继

执行 [verify.py](../../analysis/text-precondition-c15-0041-20261023/verify.py)：`passed`，4窗口226B、81条连续解码、50项独立原编码检查、10个全部直接控制目标，三函数范围与继承 inventory 相符，三条字符串相符。原编码覆盖实参寄存器、word偏移、局部加减、复制依赖、getter零/非零门以及直接目标；没有只凭 Capstone 助记符建立上述关键语义。

未执行固件/模型/历史回放，未连接设备或外部服务，未构造诊断输入或做缺陷验证；未改 ROM、生产代码、安全检查或分析器模型；未新增哈希/复制清单。差异检查仅涉及本任务独占路径。

小后继建议：单独恢复 `a00ddbf6` 开头两个正常返回门的参数与布尔结果消费，保持其余 GUI/诊断系统为边界，以确定本次最终调用是否提交区域。
