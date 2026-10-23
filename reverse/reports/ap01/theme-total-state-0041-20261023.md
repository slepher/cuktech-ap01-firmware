# 0041 主题总信息：动画延后、功率/模式显示与温度状态

后续补充：[主题在线、特殊状态与离线清理](theme-online-0041-20261023.md)，包括设置页动态标志、型号/版本和固定0查询；本文保留当时已核范围。

后续已补[窗口切换/完成回调与总量、端口180点功率历史](window-history-0041-20261023.md)，细化 render_enabled 及先前未知的数据尾部；本文保留当时范围。

本轮展开[UiIFace 生命周期](uiiface-lifecycle-0041-20261023.md)定位的应用级消费者 `a00ad07e`。ROM 路径/日志表明它是 `lv_power/ui/lv_ui_theme.c` 的 `j_win_ui_theme_total_info_change`，不是另一个发送到 MCU 的控制入口。此前已补两个页面 callback；本轮选择这个剩余消费者，以连接快照、主题端口状态字和主页面显示。

状态仍为**部分恢复**。本文为分析命名的功能合同，不是原始源码。原厂 ROM SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。只做静态分析，未运行固件、连接设备/服务、开展缺陷验证、改正式 ROM/安全检查、提交或推送。

## 证据与对象字段

- [保留的完整 callback 观测](../../analysis/theme-total-state-0041-20261023/retained-function.json)：历史 `whole-rom-private-20261023-079.json`，`ev_48c0198ff89867a929bd03b8b4df8db7f898c5b0579e9cf06545a71c3dc77bc4`；来源哈希、修复 profile、1032 B 原字节、汇编/伪代码均保留。
- [三个指令窗口](../../analysis/theme-total-state-0041-20261023/instruction-windows.json)：callback、动画计数查询 `a00891b8`、端口状态字 setter `a00a5cae`。通用 Capstone 未识别的厂商字不被删除，修复模型的解释作为独立来源。
- [资源字节](../../analysis/theme-total-state-0041-20261023/resources.json)、[合同清单](../../analysis/theme-total-state-0041-20261023/contracts.json)、[核对记录](../../analysis/theme-total-state-0041-20261023/review-index.json)及[采集脚本](../../analysis/theme-total-state-0041-20261023/collect-evidence.py)。

注册点已核为 `a005d134..a005d138` → `a01b29a0(callback=a00ad07e,userdata=s4)`。userdata 在 callback 中作为 root 使用。只给已观察偏移命名，不认证整个 root 的原始类型：

| 对象/地址 | 字段事实与局部含义 |
| --- | --- |
| root `+0x4c` byte | 非零才执行正常显示更新，分析名 render_enabled |
| root `+0x50` word | 动画期间保存的变化掩码；完整更新后清零 |
| snapshot `+4/+7/+8/+12` | unsigned halfword 功率、signed byte 温度、byte 模式、halfword 变化掩码 |
| snapshot `+0/+6` | 端口数组指针、byte 端口数；项步长 `0x1a8`，活动标志位于项 `+0x0d` |
| 全局 `62fc4034` word | 本轮确认按端口活动位图更新；保留其他位，不是普通指针或单纯端口数量 |

## 门控顺序与延后掩码

实际执行顺序是：检查 root/snapshot → 查询动画 → 检查全局状态字 → 检查 render_enabled → 更新主题。

```c
void theme_total_change_local(Root *root, UiTotalView *s) {
    log_enter();
    if (root == NULL || s == NULL) { log_reason(); return; }
    if (animation_count_query_a00891b8() != 0) {
        root->word50 = (uint32_t)s->change_mask;
        log_animation_in_progress();
        return;
    }
    if (word_at(0x62fc4034)==0) { log_no_state(); return; }
    if (root->byte4c==0) { log_disabled(); return; }
    // 正常主题更新见下文。
}
```

`a00ad11c..a00ad128` 是 halfword load 后 word store，**覆盖** root 的延后值，没有 OR 累积，也不保存 snapshot 指针/旧字段副本。动画查询使用全局链表，无 root 参数；将它命名为动画计数由调用日志及列表计数行为支持，精确库版本未认证。

正常路径的每个显示组分别检查 `(s->change_mask & bit) != 0 || (root->word50 & bit) != 0`。这只是描述条件，不表示原代码先构造一次固定 combined mask；原代码会重读相关字段。两块页面更新完成后，若 root.word50 非零便清为 0。全局状态字为 0 或 render_enabled 为 0 的提前返回路径没有清它。

本轮未定位“动画结束后由谁再次调用以应用延后位”的完整链；不能把存掩码本身说成已经排定重放任务。后续使用的是当次 snapshot 字段，没有恢复出历史数据队列。

## 端口活动状态字

在进入各显示组之前，即使当前变化掩码为 0，callback 也先读取 mode、功率、温度并更新端口活动位：

```c
uint32_t state = word_at(0x62fc4034);
for (uint32_t i=0; (uint8_t)i < s->item_count; ++i) {
    uint32_t bit = 1u << (((uint8_t)i + 1) & 31);
    if (u8_at(s->item_array + i*0x1a8 + 0x0d) != 0) state |= bit;
    else state &= ~bit;
}
set_port_state_word_a00a5cae(state);
```

setter 的完整 60 B 入口只将输入 word 写 `62fc4034` 并记录日志，日志名 `lv_set_dev_port_num`、格式 `set dev port num = %d`。尽管名字含 num，调用者的按位更新证明这里不能简单恢复成“端口数量”。本轮只认证 bit `i+1` 的活动映射，bit0、未遍历的其他位和全部写入者仍未知。

这也补充了上一轮页面 callback 对 `62fc4034!=0` 的门控含义；没有因此假定其每一位都已解释或断连状态机已恢复。

## 两个页面视图与三类变化

callback 直接取 root 的 child 0 和 child 3，然后从 `child+0x10` 的 metadata `+4` 取得各页面 context；它不使用上一轮按 tag 搜索的查找 helper。页面 context 的完整大小/生命周期未认证。

| 组 | 判定 bit | child 0 context 的动作 | child 3 context 的动作 |
| --- | ---: | --- | --- |
| 功率 | `1` | `+0x34` 数字接口传 `raw_power/10`；`+0x38` 文本格式 `.%d`、参数 `raw_power%10`；将完整 raw_power 交图形 helper | `+0x14` 文本格式 `%d`、参数 `raw_power/10`，随后布局；将完整 raw_power 交图形 helper |
| 模式 | `4` | `+0x44` 图像控件取模式资源表；`+0x48` 用 `%s` 显示模式名称；分别布局 | `+0x4c` 图像控件及 `+0x48` 模式名称；分别布局 |
| 温度 | `2` | 更新 `+0x58` 指示控件位置，以及 `+0x4c` 状态标签/样式 | 本 callback 没有对应温度组 |

raw_power 是进入正常路径后读取的 unsigned halfword，并在这些显示组间保存在寄存器中。三个 UI 动作族的普通 helper 为：数字 `a00a5fc6`、文本 `a0091ee4`、图像 `a00ed560`、布局 `a00dbb68`、功率图形 `a00ac6f8`。本轮恢复它们在 callback 中的参数数据流，不将下游图形内部、分配或动画生命周期冒称已恢复。

模式图像指针表位于 `a0254e74`，模式文本表复用 `a01c473c`。四个文本按 mode 0..3 分别为 AI 智配、极速单充、均衡输出、自定义，原字节见[已有模式表](../../analysis/ui-total-consumers-0041-20261023/mode-labels.json)。本轮只确认图像资源指针，不认证图像描述符/字体格式或 MCU 的模式算法。

## 温度位置与标签条件

温度从 snapshot `+7` 经 signed byte load 读为 t。原指令的整数计算为：

```c
int32_t progress = 0;
if (t > 24)
    progress = trunc_signed(((int8_t)(t-25)) * 100 / 50);
int32_t x_offset = trunc_signed(progress * 66 / 100) + 8;
layout_call(ctx0->widget58, ctx0->anchor54, 7, x_offset, 0);
```

保留两个除法和整数截断，不加入进度/位置 clamp。旧反编译将 `a00ad1aa/a00ad1ce/a00ad24a/a00ad2f0` 标成移除的不可达块，但汇编保留 unsigned 除法、余数和 signed 除法，调用者实际使用其结果。本报告按原指令恢复。

只有温度 bit 生效时才更新下列状态；这里的范围是字段数值，不额外推断硬件热保护阈值：

| t 范围 | 标签行为 | 样式资源指针 |
| --- | --- | --- |
| 25..64 | 清标签，再设 `Excellent` | `a0254aa8` |
| 65..74 | 清标签，再设 `High Performance` | `a055fc0c` |
| 75..127 | 清标签，再设 `Power Limitation` | `a055fc0c` |
| -128..24 | 不改标签/该样式；位置计算仍执行 | 保留原状态 |

前两段的原条件采用 unsigned halfword 范围比较，最后一段回看保留的 signed 温度与 74 比较。对于此 signed byte 的实际值域，上表与原分支等价。低于 25 不补造“正常/低温”文字，也不主动清旧标签。

## 剩余范围

本轮恢复了第三个真实总信息订阅者的局部合同：动画期覆盖保存掩码、正常路径门控、端口活动位更新、两块页面的功率/模式数据流、温度位置及标签条件。尚缺动画结束重放触发者、root `+0x4c/+0x50` 的全部读写者、完整功率图形/数字控件 helper、页面销毁和订阅节点回收，以及全局状态字其他位的含义。

本轮新增开源认证排除为 0。LVGL 形状/路径只是来源线索，准确版本、未修改实现范围和私有适配仍待核对。全部非开源逻辑目标继续保持未完成。
