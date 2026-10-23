# 0041 UiIFace 快照与控制订阅生命周期

功能续作见[底座ID接入、周期轮询与不透明MCU载荷边界](dock-presence-polling-0041-20261023.md)，补齐物理ID判断到UiIFace释放的局部链；不沿历史缺陷验证方向继续。

后续补充：[主题在线、特殊状态与离线清理](theme-online-0041-20261023.md)，包括设置页动态标志、型号/版本和固定0查询；本文保留当时已核范围。

后续已补[窗口切换/完成回调与总量、端口180点功率历史](window-history-0041-20261023.md)，细化 render_enabled 及先前未知的数据尾部；本文保留当时范围。

后续已展开[主题总信息消费者的动画延后与显示状态](theme-total-state-0041-20261023.md)，并补证 `62fc4034` 的端口活动位更新；本文保留当时已核边界。

本轮沿[模式控制合同](mode-control-0041-20261023.md)继续恢复 `PogoPinMng/UiIFaceMng.c` 的对象创建/销毁、订阅注册/摘链和实际注册入口。此前蜂鸣/背光、天气、工厂门控和模式生产路径已有局部合同；普通响应的全部字段、UI 消费者、无线私有适配和内嵌 MCU 等仍未覆盖。本轮选择此处，是为了补齐模式通知依赖的对象生命周期。

模块仍为**部分恢复**。以下为分析命名的伪代码及字段视图，不是原始源码。原厂 0041 SHA256 为 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；仅静态分析，未执行固件、访问设备/服务、开展缺陷验证、修改正式 ROM 或安全检查、提交或推送。

## 证据入口与边界

- [保留的初始化容器](../../analysis/uiiface-lifecycle-0041-20261023/retained-initializer.json)：修复模型 `a00a8582`，`ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`，附完整来源路径/哈希、原字节、汇编和伪代码。本轮只认证 `0x55` 分支中的 UiIFace 初始化片段，不认证整个普通响应函数。
- [三份函数观测](../../analysis/uiiface-lifecycle-0041-20261023/retained-functions.json)：`a00a3c48` 测试消费者、`a00a3d22` deinit、`a00a3d80` CTK 单项清理，来源为历史 `whole-rom-private-20261023-027/030/031.json`。原反编译省略的 free 参数按汇编恢复。
- [17 个指令窗口](../../analysis/uiiface-lifecycle-0041-20261023/instruction-windows.json)：引导、订阅/摘链、链表及内存接口、在线分发、创建/销毁片段、测试消费者和三个业务注册点。厂商指令未知字保留；通用 Capstone 不覆盖的含义不伪装成独立解码认证。
- [合同清单](../../analysis/uiiface-lifecycle-0041-20261023/contracts.json)、[调用前沿](../../analysis/uiiface-lifecycle-0041-20261023/caller-frontier.json)、[核对记录](../../analysis/uiiface-lifecycle-0041-20261023/review-index.json)；[采集脚本](../../analysis/uiiface-lifecycle-0041-20261023/collect-evidence.py)仅读取原件及已存证据。

## 总快照、端口数组与分配语义

`62fcb2cc` 是总快照全局指针。创建明确申请 `0x17c=380` B；首 word 指向单独分配的端口数组，每项 `0x1a8=424` B。不能再把前一轮已核的 14 B 前缀当整个快照大小。

```c
// 分析视图；未知区不能用推测的原始类型/字段名填满。
struct UiTotalView {
    uint32_t item_array;      // +0：端口项数组指针
    uint16_t total_power;    // +4：日志 Power；单位/缩放待完整读者核对
    uint8_t item_count;      // +6：日志 Number
    int8_t temperature;      // +7：日志 Temp，有符号 load
    uint8_t mode;            // +8：上一轮控制变化来源
    uint8_t unknown09[3];
    uint16_t change_mask;    // +12：同步通知期间可见，分发后清零
    uint8_t unknown14[0x17c - 14];
};
struct UiItemPrefixView {    // 仅为 424 B 端口项的已核局部字段
    uint8_t unknown00[0x13];
    uint8_t index;           // +0x13：初始化循环的低字节索引
    uint8_t unknown14[0x10];
    uint8_t descriptor_bits;// +0x24：来自描述字节的 bit6、低4位、bit4..5
    // 其余字段及嵌套对象另行恢复，不以这个前缀确定完整 C sizeof。
};
```

字段 `+4/+6/+7` 的名字有实际消费者 `a00a3c48` 支持：其日志格式位于 `a0268508`，依次打印 `Number, Power, Temp`，指令分别读取 `+6` byte、`+4` unsigned halfword、`+7` signed byte。日志名称不单独认证功率单位或温度缩放。

内存边界：`a008e362(size)` 调 `a002fcc8(size)` 分配，成功则调用 `a0080d8e(ptr,size)`；后者把长度移到 a2、a1 置 0，调用 `a0024906` 清零，最后返回原指针。`a008e38c(size)` 非零时转到上述零初始化分配，零时返回静态地址 `62fc95e0`。释放接口 `a008ab8a(ptr)` 对 NULL 和这个静态地址直接返回，其他指针交 `a002e14e`。这说明两个创建调用的清零语义及零长度边界，不将其误写成普通 malloc/free 的全部行为，也未认证这些库实现的准确来源和版本。

## 底座基础信息触发快照重建

普通响应入口 `a00a8582` 的 `cmd==0x55` 分支读取基础信息并取得端口数 `62fcb01c`，随后在 `a00a8a22..a00a8a81`、冷片段 `a00a8aca..a00a8b4f` 重建 UiIFace。该响应分支前面的设备识别、原始数据对象分配仍不是本轮完整认证范围。

```c
// 内联片段；不是 ROM 中独立的 init 函数/返回合同。
uint32_t count = u8_at(0x62fcb01c);
ui_deinit_a00a3d22();
UiTotalView *fresh = zeroed_alloc_a008e362(0x17c);
global_snapshot = fresh;
if (fresh != NULL) {
    fresh->item_array = zeroed_alloc_or_static_a008e38c(count * 0x1a8);
    for (uint32_t i = 0; (uint8_t)i < count; i++) {
        UiItemView *item = at(fresh->item_array + i*0x1a8);
        // desc 是此内联片段读取的描述字节视图，其完整生产合同待核。
        uint8_t flags = desc[i + 0x17];
        item->byte24 = (item->byte24 & 0xbf) | (flags & 0x40);
        item->byte24 = (item->byte24 & 0xf0) | (flags & 0x0f);
        item->byte24 = (item->byte24 & 0xcf) | (flags & 0x30);
        item->byte13 = (uint8_t)i;
        log_item_descriptor();
    }
    fresh->item_count = (uint8_t)count;
    a00a45d8();   // 已有底座固件头部选择合同，不替换成快照字段设置
    a00a5b5c();   // 下游职责尚未在此展开
    online_dispatch_a00a385a(1);
}
// 原外层随后仍进行端口测试订阅等工作；此处不补造 early return。
```

这是“先销毁旧快照，再申请新快照”，不是分配成功后交换。指令在端口数组分配返回后直接进入已有循环，没有本轮补造的额外分配失败恢复路径；只记录原错误边界，不执行验证。三个掩码更新的次序按原指令保留，不能推导原程序做了一次原子字段合并。

## 离线通知先于释放

`a00a3d22..a00a3d7f` 的日志名为 `UiIFaceMngDeInit`。已核局部生命周期：

```c
void ui_deinit_local(void) {
    if (global_snapshot != NULL) {
        online_dispatch_a00a385a(0);
        // 原代码在同步回调之后重新读取全局指针，不锁定通知前的局部副本。
        if (global_snapshot->item_array != 0)
            free_adapter(global_snapshot->item_array);
        free_adapter(global_snapshot);
        global_snapshot = NULL;
    }
    log_deinit();
}
```

在线 dispatcher `a00a385a..a00a389b` 遍历另一个链表头 `62fcb548`，调用 `callback(userdata, online_value)`，online 是调用者原始 word。离线通知发生时旧快照尚未释放；真正释放的地址随后又从全局重读。不擅自增加回调之后的 NULL 检查或假设回调不能改变状态。

这个 deinit 没有逐项遍历端口数组、没有调用 `a00a3d80` 的 CTK 嵌套字段释放，也没有清控制订阅链表。`a00a3d80` 是另一个局部清理器，已有观测显示它释放单项 `+0x28/+0x2c/+0x30/+0x34/+0x38` 的非空指针并逐项清零；其与全局销毁的完整衔接仍未知，不把这段独立代码自动拼入 deinit。

当前模型列出 deinit 的直接调用者为 `a00a41f2`、`a00a4708` 和响应处理器 `a00a8582`。其中 OTA 退出复用 deinit 的行为已有[UART/OTA 合同](usb-interface-ota-0041-20261023.md)；本轮没有将所有断连/任务销毁分支标为完成。

## 控制订阅链表的布局、注册与摘链

引导函数 `a00a55ba` 的已核片段将 `62fcb554` 头部设为 `{8,0,0}`，即链字段偏移 8、first=NULL、last=NULL；同时初始化在线、端口项等其他链表，并将总快照指针置 0。此处只是服务引导中的局部合同，不认证全部前置 helper。

```c
struct ControlListHeadView { uint32_t link_offset, first, last; }; // 12 B
struct ControlNodeView {
    uint32_t callback;       // +0
    uint32_t userdata;       // +4
    uint32_t back_link;      // +8：前驱含义由通用摘链/设置器推断
    uint32_t next;           // +12
};                          // 分配 8+8=16 B
```

next@12 有普通 load/store 及 dispatcher 的直接证据。back_link 的部分访问是厂商 load/store 字；本轮保留原字，不把通用 Capstone 的未知字称为已独立解码。偏移 8 来自明确初始化与辅助调用，前驱含义为交叉推断。

`a01b29a0(callback,userdata)`：按 first/next 遍历，若 callback 指针相同便返回，不比较或更新 userdata。未命中则调 `a008af14(head)` 申请 `link_offset+8=16` B 并追加到尾部，然后写 callback 和 userdata。分配器本身返回 NULL 的边界与注册器紧随的字段写入均保留在原指令证据中，不补造失败恢复。

`a01b2966(callback)`：查找 callback 相等的首节点，调用 `a0089d02(head,node)` 摘链后返回；找不到直接返回。通用摘链路径更新 first/last 或相邻链接，**本调用链没有 free**。因此本轮恢复的是“注销可达关系”，没有证据可把它写成“释放订阅节点/销毁 userdata”；脱链节点最终回收方仍未知。不继续进行缺陷或可利用性验证。

控制 dispatcher 沿用[上一轮](mode-control-0041-20261023.md)：尾追加决定正常遍历为注册顺序；调用 `callback(userdata,current_snapshot)`，完成后清总快照变化掩码。callback 与对象寿命在这里是借用关系，订阅者未随一次快照重建自动消失。

## 已定位的消费者入口

| 注册点 | callback | userdata 来源 | 本轮已核范围 |
| --- | --- | --- | --- |
| `a00a569c..a00a56a0` | `a00a3c48` | 100 | 引导注册的日志测试消费者，已核字段读取 |
| `a005d134..a005d138` | `a00ad07e` | 当时 s4 应用上下文 | callback 地址构造、a1 赋值及注册调用；未认证整个应用构造器 |
| `a00a79ce..a00a79d2` | `a00ac54e` | 当时 s3 UI 上下文 | 同上；消费者完整行为待展开 |
| `a00b076c..a00b0770` | `a00f3952` | 当时 s5 页面上下文 | 同上；页面销毁/撤销订阅待展开 |

这些函数地址由 LUI/ADDI 和 AUIPC/JALR 原指令确认，不依赖模型能否识别函数指针边。首轮直接调用前沿中没有 `a01b2966` 的调用者；这个有界结果不能证明整个 ROM 不会间接注销，也不能替代页面销毁分析。

## 剩余未知

本轮新增 380 B 总对象/424 B 项步长、零初始化接口、创建→在线→离线→释放顺序、订阅头/节点布局、callback 去重/尾追加/摘链语义、四个消费者注册入口，以及总功率/温度字段证据。仍缺完整基础信息描述字节来源、端口全部字段和嵌套内存归属、消费者正常生命周期、所有注销/节点回收路径及回调期间增删约束；普通响应数据流也未全恢复。

本轮新增开源认证排除 0。链表和分配适配具有库实现形状，精确来源/版本及厂商修改仍未确认，不能直接从恢复范围剔除。原字节、来源指纹和局部链接核对通过不等同于完整模块认证，全部非开源逻辑的持续目标仍未完成。
