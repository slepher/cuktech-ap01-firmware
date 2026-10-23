# 0041 总信息消费者：功率详情页、屏保与模式名称

后续已展开[主题总信息消费者的动画延后与显示状态](theme-total-state-0041-20261023.md)，并补证 `62fc4034` 的端口活动位更新；本文保留当时已核边界。

本轮在[UiIFace 生命周期](uiiface-lifecycle-0041-20261023.md)定位的消费者入口上继续展开，恢复功率详情页 `a00f3952`、屏保 `a00ac54e` 及其页面查找接口。状态仍为**部分恢复**：callback 的局部职责已形成合同，全部页面渲染/销毁及其他订阅者尚未闭合。

原厂 ROM SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。所有命名与伪代码为分析视图，不是原始源码。仅静态分析，未执行固件、访问实机/服务、验证缺陷、修改正式 ROM/安全检查、提交或推送。

## 证据入口

- [三份修复模型观测](../../analysis/ui-total-consumers-0041-20261023/retained-functions.json)：页面查找 `a00a72ae`、屏保 `a00ac54e`、功率详情 callback `a00f3952`，来源历史 `whole-rom-private-20261023-057/077/121.json`，保留原始路径/哈希、profile、完整 dossier 和原字节。
- [七个指令窗口](../../analysis/ui-total-consumers-0041-20261023/instruction-windows.json)：两个 callback、查找接口、模式 getter 的可达 NULL 尾部、child-count 正常入口/尾部、屏保活动样式 helper。未知厂商字保留。
- [模式原字节表](../../analysis/ui-total-consumers-0041-20261023/mode-labels.json)、[合同清单](../../analysis/ui-total-consumers-0041-20261023/contracts.json)、[核对记录](../../analysis/ui-total-consumers-0041-20261023/review-index.json)和[采集脚本](../../analysis/ui-total-consumers-0041-20261023/collect-evidence.py)。

三份观测 evidence id 分别为 `ev_f7f4d6d300c6d2e5441239850f4b90c26d94ccf9be71c3e99883e83128f320bb`、`ev_cffa17d3476afc7dff436d5c3681efe88c2f448f51d542b45398ee7a45bc2dd5`、`ev_7d6c56896bed2824364df179e913f092c19d407d5825bd03537b0aed00eb0915`。

## 模式显示名称已确认

ROM 指针表 `a01c473c` 的四项直接指向 UTF-8 文本；详情 callback 在 `a00f3b1e..a00f3b30` 从 snapshot `+8` 读取 mode，以 `th.lrw` 按 4 B 索引加载字符串并交给文本接口：

| mode | 原厂 UI 文本 | 文本 ROM 地址 |
| ---: | --- | --- |
| 0 | AI 智配 | `a01c3fc0` |
| 1 | 极速单充 | `a01c3fcc` |
| 2 | 均衡输出 | `a01c3fdc` |
| 3 | 自定义 | `a01c3fec` |

这补齐了[模式控制报告](mode-control-0041-20261023.md)保留的 0/1/2 产品显示名。名称不能证明 MCU 如何分配功率、是否使用学习算法或各端口的实际优先级，底座内部逻辑仍待恢复。

## 页面查找接口与输出合同

`a00a72ae(root,tag,out_child,out_ctx)` 从 root 的直接子项中找页面 metadata tag：

```c
int lookup_page_local(Root *root, uint32_t tag, Child **out_child, void **out_ctx) {
    if (root == NULL) { log_no_root(); return 0; }
    uint32_t n = child_count_a00dd144(root); // a0 仍是 root；旧反编译遗漏参数
    for (uint32_t i = 0; i != n; i++) {
        Child *child = child_at_a00dcee4(root, i);
        *out_child = child;              // 每次循环就写，不等匹配后才写
        Metadata *meta = ptr_at(child + 0x10);
        if (meta->word00 == tag) {
            *out_ctx = meta->word04;
            return 1;
        }
    }
    return 0;
}
```

metadata 的最小已核布局为 `{u32 tag@0; u32 page_context@4; ...}`。失败并不统一清输出：零 root/零子项时没有输出写入，遍历未匹配时 out_child 保留最后一次子项，out_ctx 不改。下述消费者在每次查找前分别清两个局部输出，并检查返回值及两个指针，不能将这些调用者行为搬进查找 helper。

child_count 的正常分支从 `root+8` 取内部指针，非空则读取其 `+0x30` unsigned halfword，空则返回 0；原调用点 a0 保持 root。它的断言路径及 LVGL 的完整类型/精确版本不在本轮重新认证。查找过程中不分配、不复制或释放 page_context，返回值是现有页面的借用视图。

## 功率详情页：只处理 bit2，并逐段重查

`a00f3952(userdata,snapshot)` 的源码路径/日志为 `lv_power/ui/lv_ui_power1_dtl.c` / `j_win_ui_power1_dtl_total_info_change`。userdata、snapshot 为空或全局 word `62fc4034` 为 0 时记录并返回；未给该全局额外推测生命周期意义。

```c
void power_detail_total_local(Root *root, UiTotalView *s) {
    if (!root || !s || word_at(0x62fc4034)==0) { log_reason(); return; }
    if ((s->change_mask & 4)==0) return;

    Child *ui = NULL; void *ctx = NULL;
    if (lookup_page(root,0x0d,&ui,&ctx) && ui && ctx)
        page_summary_update_a00f3844(ctx);
    else log_missing_page_0d();

    if ((s->change_mask & 4)==0) return; // 原代码重新加载，不缓存首个检查结果
    ui = NULL; ctx = NULL;
    if (lookup_page(root,0x0f,&ui,&ctx) && ui && ctx)
        page_mode_update_a00f388c(ctx,0,s->mode);
    else log_missing_page_0f();

    if ((s->change_mask & 4)==0) return;
    ui = NULL; ctx = NULL;
    if (lookup_page(root,0x13,&ui,&ctx) && ui && ctx)
        text_set_a0091b3a(ptr_at(ctx+0x1c),mode_labels[s->mode]);
    else log_missing_page_13();
}
```

缺某一页不阻止后续页查找；三个 mask 检查顺序分别保留。该 callback 没有清 mask，没有缓存/释放传入 snapshot；mask 最终由外层 UiIFace dispatcher 清零。`a00f3844/a00f388c` 的完整控件状态/渲染仍在后续范围，不能将 callback 的一次调用当全部 UI 更新已完成。

模式 getter `a00a5c50` 的正常路径读取当前全局 `62fcb2cc->mode`；NULL 分支从 `a00a5c58` 跳到 `a00a5c60` 的日志尾部，并在 `a00a5c8e` 显式返回 0。旧模型把 hot body 限定为 16 B 并将该尾部另列，本轮人工窗口覆盖可达分支至 `a00a5c93`，不把模型范围截断误当缺失返回。页面摘要 helper 存在对此 getter 的调用，详细控件读取留待展开。

## 屏保：原始功率、固定四项活动状态

`a00ac54e(root,snapshot)` 的路径/日志为 `lv_power/ui/lv_ui_scr_saver.c` / `j_win_ui_scr_saver_total_info_change`。只检查两个参数非空，**没有读取变化掩码或总快照 item_count**。指令先缓存 snapshot `+4` 的 unsigned halfword 功率，再固定检查 item 数组的四个 `+0x0d` byte，步长 `0x1a8`，有任一非零则 active=1。

```c
void screensaver_total_local(Root *root, UiTotalView *s) {
    if (!root || !s) { log_reason(); return; }
    uint16_t power = s->total_power;
    bool active = false;
    for (unsigned i=0; i<4; i++)
        if (u8_at(s->item_array+i*0x1a8+0x0d)!=0) active=true;

    Child *ui=NULL; void *ctx=NULL;
    if (lookup_page(root,0x2d,&ui,&ctx) && ui && ctx)
        screensaver_power_update_a00ac040(ctx,ui,power,1);
    else log_missing_page_2d();

    ui=NULL; ctx=NULL;
    if (!(lookup_page(root,0x2f,&ui,&ctx) && ui && ctx)) {
        log_missing_page_2f(); return;
    }
    if (active) {
        if (u8_at(ctx+0x24)==0) {
            activity_style_a00ac4c2(ctx,ui,1);
            u8_at(ctx+0x24)=1;
        }
        text_format_a0091ee4(ptr_at(ctx+0x10),"%d",(uint32_t)power/10);
        layout_call_a00dbb68(ptr_at(ctx+0x10),ptr_at(ctx+0x0c),2,0,12);
    } else if (u8_at(ctx+0x24)==1) {
        activity_style_a00ac4c2(ctx,ui,0);
        u8_at(ctx+0x24)=0;
    }
}
```

`0x2d` 接口收到原始 power，`0x2f` 文本收到 unsigned 整数除 10 的截断值。格式常量 `a06130bc` 为 `%d`，该写值本身不含 W 字符。它支持 UI 使用十分之一比例显示功率的推断，但校准及全部消费者单位仍未知。旧反编译有“移除不可达块 a00ac6b8”警告，真实 `divu a2,s1,a2` 及后续格式化调用明确存在；本报告按汇编保留除法。

活动时仅在 ctx 状态为 0 时调用样式切换 1，但每次仍刷新数字与布局；不活动时只有状态恰好为 1 才切换 0 并清状态。不能把后者改成任意非零均清。`a00ac4c2` 的对象/样式操作原字节一并保留，但本轮不凭低层接口名称猜造全部可见性、动画和几何效果。

固定四项读取是本 callback 的指令事实，不改写成按 item_count 循环；本轮未构造输入验证其他数量，也未展开缺陷调查。

## 剩余范围

本轮新增两个真实订阅消费者的局部合同、页面 metadata 查找/输出规则、四个模式显示名、屏保功率/活动状态数据流，以及详情页 bit2 的三段门控。尚缺完整 `a00ad07e` 消费者、页面生成/销毁与注销、下游渲染 helper、全部总信息生产者及 MCU 模式实际执行。快照生命周期和摘链但未证明回收的节点边界沿用上一报告，不因此标为完成。

新增开源认证排除为 0；库形状、路径和 API 使用仍不足以认证准确版本及未修改范围。全部非开源逻辑目标继续保持未完成。
