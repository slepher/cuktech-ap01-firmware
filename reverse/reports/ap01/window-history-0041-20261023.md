# 0041 窗口切换回调与 180 点功率历史

后续补充：[主题在线、特殊状态与离线清理](theme-online-0041-20261023.md)，包括设置页动态标志、型号/版本和固定0查询；本文保留当时已核范围。

本轮从[主题总信息](theme-total-state-0041-20261023.md)的动画门控向前追窗口切换，恢复开始/执行/完成三个入口；随后展开 UiIFace 共用的功率历史 helper，补齐总快照和端口项尾部的数据结构。模块仍为**部分恢复**：动画完成入口已核，完整重放触发和所有调用者尚未闭合。

原件 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。只做静态分析；无固件运行、实机/服务连接、缺陷验证、正式 ROM/安全检查修改或提交推送。字段名、结构体和伪代码是分析视图，不是原始源码。

## 证据

- [两份保留观测](../../analysis/window-history-0041-20261023/retained-functions.json)：`a00ab628` 完成回调和 `a019d422` 窗口切换，历史 `whole-rom-private-20261023-073/146.json`；保留来源哈希、profile、全部汇编/伪代码及原字节。Evidence id 为 `ev_6284955279e3fe7628b002dcf25b72407bbdab81296fb6c51d4d97a69fbebe46` 和 `ev_e7bd3e426378c573fd751364a9c83bf470389ad186beb9c23f1d7faa89b4acec`。
- [8 个指令窗口](../../analysis/window-history-0041-20261023/instruction-windows.json)：窗口切换、子项包装/执行/完成、历史 helper、两个历史调用点及动画模板初始化。
- [历史调用者来源](../../analysis/window-history-0041-20261023/retained-history-callers.json)、[厂商半字访问模型](../../analysis/window-history-0041-20261023/vendor-memory-model.json)、[合同清单](../../analysis/window-history-0041-20261023/contracts.json)、[核对记录](../../analysis/window-history-0041-20261023/review-index.json)。[采集脚本](../../analysis/window-history-0041-20261023/collect-evidence.py)仅读取 ROM/既存证据及已绑定模型，未修改或重跑解码器。

## 窗口开始与执行：先关闭正常更新门控

`a019d422(root,target)` 的日志名是 `lv_window_set_active_by_idx_duration`。NULL root 走原断言日志/循环；正常路径只在 child_count(root) 非零且 target 不等于 root `+0x34` 时切换。不能依据名字推断原始完整签名和时间单位，以下按实际参数使用恢复。

```c
// 正常路径局部合同；外层索引约束和断言辅助未改写。
void switch_window_local(Root *root, uint32_t target) {
    if (child_count(root)==0 || target==root->current_at_34) return;
    animation_control_a01b2eb4(0,0); // 完整库语义仍待来源/实现核对
    Object *old_previous = child(root,root->previous_at_38);
    Object *incoming = child(root,target);
    Object *outgoing = child(root,root->current_at_34);
    position_x_a00d8c12(old_previous,320);
    root->previous_at_38 = root->current_at_34;
    root->current_at_34 = target;
    root->render_enabled_at_4c = 0;

    init_animation_template_a008df3c(&local_anim);
    // 原始模板字段见下表，未猜造未确认的成员名。
    position_x_a00d8c12(outgoing,0);
    position_x_a00d8c12(incoming,-320);
    start_animation_a008bf6e(&local_anim);
}

// a00b3080：由动画系统间接传入 root 和数值 value。
void move_windows_local(Root *root, int32_t value) {
    Object *outgoing = child(root,root->previous_at_38);
    Object *incoming = child(root,root->current_at_34);
    position_x_a00d8c12(incoming,value-320);
    position_x_a00d8c12(outgoing,value);
}
```

子项包装 `a00b3036(root,index)` 在正常分支保持 a0/a1 并调用 `a00dcee4(root,index)`；NULL root 走断言循环。窗口执行回调每次从 root 重读 current/previous 索引，不保留开始时的两页指针快照。

动画模板初始化 `a008df3c` 清零 96 B 并写默认值，窗口切换随后覆盖的字段如下：

| 模板偏移 | 写入事实 |
| --- | --- |
| `+0` | root，执行回调的对象参数视图 |
| `+4` | 执行 callback `a00b3080` |
| `+0x10` | 完成 callback `a00ab628` |
| `+0x1c` | root，完成回调从此取 userdata |
| `+0x20` | 路径函数指针 `a008a93e` |
| `+0x24/+0x28/+0x2c/+0x30` | `0 / 0x80000000 / 320 / 0` |

320 已有明确的位置跨度证据；模板其他数值字段的准确 ABI/时间语义、库复制/释放及调度约束仍未完整认证。模板在栈上，交动画库入口；本轮不把它的布局与任意版本 SDK typedef 直接等同。

## 完成回调：重新启用更新，不直接重放掩码

`a00ab628(anim)` 的日志名为 `win_set_active_anim_completed_cb`。它从 `anim+0x1c` 取 root，首先将 root `+0x4c` 置 1，然后处理特殊页面：

```c
void window_complete_local(AnimationView *anim) {
    Root *root = ptr_at(anim+0x1c);
    root->render_enabled_at_4c = 1;
    if (root->current_at_34 == 7) {
        Object *page = child_at(root,7);
        void *ctx = ptr_at(ptr_at(page+0x10)+4);
        void *gif = ptr_at(ctx);
        if (ptr_at(gif+0x5c)==NULL) log_gif_not_loaded();
        else timer_resume_a008bd70(ptr_at(gif+0x60));
    }
    log_complete(root->render_enabled_at_4c);
}
```

`+0x5c/+0x60` 的资源/计时器职责由原 `lv_gif_resume` 日志和调用形状支持；GIF 内部格式、销毁和完整 timer 库实现未在此认证。完成入口没有访问 root `+0x50`，也没有直接调用总信息消费者或重新分发快照。已恢复的关系是“允许后续正常更新”；保证下一次通知、延后位最终被消费的完整触发链仍未知。

## 180 点功率历史的完整局部结构

`a00a398c(history,value)` 为总功率和端口功率共用的 130 B helper：

```c
struct PowerHistoryView {
    uint16_t samples[180]; // +0..359：环形样本
    uint16_t maximum;     // +360 / 0x168
    uint8_t cursor;       // +362 / 0x16a：下次覆盖槽
    uint8_t maximum_slot; // +363 / 0x16b：缓存最大值所在槽
};                        // 364 B
```

两个调用点的实际参数均为 `lhu`：总功率在 `a00a8c14` 读 snapshot `+4`，历史指针为 snapshot `+14`；端口功率在 `a00a9298` 读 item `+8`，历史指针为 item `+0x3c`。旧大函数反编译把总功率实参显示为 signed short，汇编证明这里是零扩展，本文据此纠正。

| 嵌入对象 | 历史起点 | maximum | cursor / maximum_slot | 结束位置 |
| --- | ---: | ---: | ---: | ---: |
| 380 B 总快照 | `+0x0e` | `+0x176` | `+0x178 / +0x179` | `+0x17a`，最后 2 B 暂未知 |
| 424 B 端口项 | `+0x3c` | `+0x1a4` | `+0x1a6 / +0x1a7` | `+0x1a8`，与项步长一致 |

总快照和端口数组的构造使用已核零初始化分配，因此正常新对象的历史初值全零，见[生命周期报告](uiiface-lifecycle-0041-20261023.md)。仅此布局算术不认证所有绘图消费者。

## 更新、缓存最大值及返回合同

下面保留原比较宽度、写入顺序与返回语义；正常已核调用者提供零扩展的 16 bit 功率，原 helper 的 a1 仍作为 word 参与比较。

```c
uint32_t update_power_history_local(PowerHistoryView *h, uint32_t value) {
    uint8_t old = h->cursor;
    uint32_t rescan;
    if ((uint32_t)h->maximum < value) {
        h->maximum = (uint16_t)value;
        h->maximum_slot = old;
        rescan = 0;
    } else {
        rescan = (h->maximum_slot == old);
    }
    uint8_t next = (uint8_t)(old+1);
    h->cursor = next;
    h->samples[old] = (uint16_t)value;
    if (next > 179) h->cursor = 0;

    if (rescan != 0) {
        h->maximum = 0; // maximum_slot 没有在这里先清零
        for (uint32_t i=0; i<180; i++) {
            uint16_t x = h->samples[i];
            if (h->maximum < x) {
                h->maximum = x;
                h->maximum_slot = (uint8_t)i;
            }
        }
    }
    if (value != 0 || h->maximum != 0) return 1;
    return rescan;
}
```

样本半字 store `a00a39b6` 和重扫 halfword load `a00a39e6` 分别按既有模型识别为 `th.srh a1,a5,a3,1`、`th.lrhu a3,a5,a4,1`。两条编码的寄存器、shift=1 与已有 Sleigh load/store 语义交叉核对；所用模型文件哈希与保留 profile 输入相符。本轮没有自行更换 ISA 模型或用猜测 NOP 填充。

重扫只在严格更大时改最大值槽：有正最大值且并列时保留扫描中首个最大槽；全零扫描没有更新槽位，因此保留原 maximum_slot。返回值也不是简单的“最大值变了”：只要新样本或当前最大值非零便返回 1；两者都为零时仍保留 rescan 值。由零初值和第一次写入槽 0 静态推导，即使第一次样本为 0，也会重扫并返回 1；这是分支算术推导，没有运行原件或构造异常输入。

两个调用者在返回非零时，将相应 total/item 的变化掩码 OR `0x400`。因而该 bit 表示历史更新需求的局部职责，不等同于当前功率值发生变化或最大值一定改变。样本间隔、180 点对应多少秒、所有图形读取/抽样路径仍待恢复。

## 剩余未知

本轮新增窗口开始/执行/完成的间接入口与几何关系、render_enabled 的关闭/恢复、GIF 特殊页恢复，以及 364 B 历史结构、180 项环形写入、最大值重扫、返回值和 `0x400` 通知关系。仍缺全体页面切换调用者、动画库字段和完整所有权、延后通知的最终触发、历史采样时间与完整绘图、页面销毁及订阅节点回收。

新增开源认证排除 0。已复用的私有指令模型是分析工具输入，不代表固件中对应库的来源/版本已认证；全部非开源逻辑恢复目标仍未完成。
