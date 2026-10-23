# A08：线程入口与 userdata 两层包装独立复核

2026-10-23；管理基线 `ea2d450`，分支 `codex/re-0041-a08`。结论：**限定接受 A07，无需语义纠正**。仅认证直接包装的参数透传与下层明确保存局部；最终 consumer 的 a0、启动适配器、运行时启动和调度仍未闭合。本文伪代码是分析表达，不是原始源码。

已读管理任务书、REA 技能和 native guide、A07 报告与证据。检查本 worktree、主仓库的祖先以及适用 reverse 子目录，未发现 AGENTS.md。只读主仓库原 ROM 与既有证据；没有打开共享 REA 会话/数据库、执行固件、外连、连接设备、验证缺陷或改分析器模型。首次读取命令附带一个无关且不存在的技能路径，未产生写入；随后读取正确技能路径。PowerShell 的 InitializeDefaultDrives 提示未阻止显式 Set-Location 后的操作。

## 逐项验收

| 项目 | 结果与原指令依据 |
| --- | --- |
| `a0197f02..a0197fa7` 入口与返回 | 接受。a0..a4 分别作为 out/name/entry/stack_value/userdata 的分析签名。`7f12/18/1a` 保存 name/out/entry；`7f26/2a` 分别 word 保存原 a3/a4；`7f66` 保存下层返回到 s2，`7f8e` 返回 s2。名称和类型仍是分析表达。 |
| 上层参数透传 | 接受。`a0197f50` 取原 a4，`7f54` 置 a2=s2，`7f56` 置属性区指针，`7f5a` 置 a3=原 a4；`7f5e/62` 原编码重组目标 `a0052fee`。无指令把 consumer 改成 consumer+4 后再传 userdata。A05 原 caller 的值来源沿用已验收材料，本次未重新认证 A05 全函数。 |
| 属性区及失败/发布局部 | 接受。`7f3e` word 写区+8，`7f42` byte 写区+3；12 B 区不是已认证原始结构体。申请失败去 `7fa4` 返回 -1；下层非零走 `7f6c` 清理调用，零走 `7f96` 读 *p、`7f98` 写 p 到 *out、`7f9e` 调 name 相关 callee。该 name callee 不取代 s2 返回值。 |
| `a0052fee..a0053251` 参数保存 | 接受局部。`a005300a/3010/3012/3022` 为 a1→s2、a0→s6、a2→s9、a3→s7；`305e/3062` 传 0x140 给 `a0030eb8`。不认证申请对象真实类型。 |
| 下层入口转交与两字段保存 | 接受局部。`3100/3108` 形成 a2=`a012f946`，`3106` a3=s9，`310c` a0=s1，`3104` a4=1；`310e` 直接目标 `a0030ef8`。`3126/312e` 形成 `a0051dac`，`3132` word 写 s1+0x130，`3136` word 写 s7 到 s1+0x134。这里只认证寄存器和局部存储，不证明跨未知 word 的原 entry/userdata 不变量。 |
| 输出来源 | 接受局部。`31f4` 从 s1+12 读 s2，`3206` 在 s6 非零时落到 `320a` 写 *s6=s2；不是写 s1。返回 `322c` 来自 s4。 |
| 三个厂商 word | 接受未知标记。`a00530fa:8bba5a18`、`a00531c0:8bdbe744`、`a00531e8:8bb7073c` 原字节一致，均为 4 B custom opcode；未赋语义，也未认证它们保持任何寄存器。 |
| 最终调用/运行时与来源 | 未核。`a012f946` 和 `a0051dac` 的函数体、+0x134 的实际读取者、最终 consumer a0、成功路径全集、实际启动/销毁/调度未展开。没有新增蜂鸣 exited_sem 连接。两包装及下层 callee 无已核实开源版本/出处，来源未知继续计入待恢复范围。 |

上述地址表中缩写 `7fXX` 均指 `a0197fXX`，下层无前缀局部 `30XX/31XX/32XX` 均指 `a00530XX/a00531XX/a00532XX`。

## 调用与字段分析表达

```c
// 两层直接合同；沿用 A05 已验收 caller 的 entry/consumer 值来源。
result = call_a0052fee(new4, attributes12, entry_a0126946, consumer);
if (result == 0) {
    store32(out /* A05: consumer+4 */, new4);
    call_a01a9038(load32(new4), name);
}
// 下层只列局部指令，不视为完整连续可达或跨 custom word 的值证明：
call_a0030ef8(s1, local_a1, ptr_a012f946, s9, 1);
store32(s1 + 0x130, ptr_a0051dac);
store32(s1 + 0x134, s7);
```

`+0x130`/`+0x134` 为两个 observed word 字段；“入口适配器”“userdata 保存位置”“线程属性”等仍为有依据的推断。未把相邻字段认定为同一回调一定消费的完整结构。

## 实际验证与覆盖限制

[review-static.py](../../analysis/thread-userdata-review-a08-0041-20261023/review-static.py) 只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，使用既有映射基址 `9ffff000`，只写 A08 [review-index.json](../../analysis/thread-userdata-review-a08-0041-20261023/review-index.json)。本次未运行 A07 收集器，未覆盖其证据，也未新增哈希/复制清单。

宿主 Python/Capstone 5.0.7 成功：A07 两个既有边界内 778 B、256 指令槽逐项与原 ROM 字节一致；253 普通指令重新解码与保留文本一致，3 个 custom word 保留未知。另做 36 项选定指令断言与 8 项独立原编码检查（6 个直接调用目标、2 个 word store 的 opcode/宽度/寄存器/偏移），全部通过。人工复核两窗口的分支、保存/恢复与返回段；函数范围沿用 A07 inventory 边界，并以原字节前奏/返回局部核对，未独立重建全 ROM 函数边界。

脚本测试只核静态证据一致性，不替代 ROM 语义论证；没有编译生产项目或执行参考模型。JSON 解析与报告链接核对、`git diff --check` 通过。恢复程度：上层直接透传已恢复；下层存储/入口转交局部恢复；最终原 entry 的调用与运行时边仍断开，不能称完整线程生命周期已恢复。

下一小任务：只核 `a012f946` 的入口参数和向一个直接 callee 的传递，最多入口及一个直接依赖；若不能连接原 entry 或 +0x134，明确保留断边，不扩展调度器。
