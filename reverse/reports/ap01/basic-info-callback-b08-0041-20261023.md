# B08：基础信息 callback ABI 与 userdata 首个使用点

2026-10-23；分支 `codex/re-0041-b08`，基线 `ffac598`。本任务只恢复两个核心函数：`a00a389c` 的相关分派合同及 `a00a3c8a` 全入口。结论待独立复核。以下均为静态指令恢复与可读伪代码，不是原始源码或实际运行观察。

## 回答的问题

**userdata 位于 callback 的 a0，记录指针位于 a1。** B06/B07已证注册在同一 `62fcb530` 链表节点写 `+0=callback`、`+4=userdata`。本次在 `a00a389c` 核到：`a00a38ee` 读取节点+0至a5，非零才由 `38f2` 读取节点+4至a0，`38f4` 把所选记录指针送a1，`38f6` `c.jalr a5`。该边在运行时节点目标为 `a00a3c8a` 的前提下闭合其机器级ABI；不把静态登记等同于实际发生调用。

`a00a3c8a` 对入口userdata的第一个直接使用是 `3c94` **a5=a0**。随后a5不再改写，被作为日志调用的第一个可变参数传给 `a008b51a`，格式为 `UserData = 0x%lx`。本函数没有将该userdata用作记录索引、地址或分支条件；它从a1所指记录读取字段并记录日志。注册循环中的i属于被存储的userdata；不能将i混同于分派器自己的记录选择入参。B06/B07关于同callback去重、不更新userdata的条件结论继续适用，不能据此宣称运行时userdata必为某个固定i。

## 函数与局部结构

| 地址，范围含尾指令 | 参数、返回及调用关系 |
| --- | --- |
| `a00a389c..a00a3902`，104B | 入口a0作为乘数计算 `index*0x1a8`。读取 `word[62fcb2cc]`，为零直接ret；非零时以其首word为记录base。读取header `62fcb530` 的head并逐节点间接调用。callback参数a0=node+4，a1=base+index*0x1a8。调用返回后重读header的size，取next；结束时将所选记录首word清零。未认证业务返回类型/值。 |
| `a00a3c8a..a00a3cde`，86B | a0=userdata word；a1=记录指针。只调用 `a008b51a`，返回前不再重写a0，因此寄存器保留该调用返回形状；其语义/原返回类型未认证。 |
| `a008b51a`，不透明直接依赖 | 调用点传日志级别4、文件字符串、行号0xc5、函数名字符串、格式串及下述参数。没有展开日志实现。 |

```c
// 字段偏移/访问宽度是指令事实；名称只是分析标注。
struct RecordPartial {
    uint32_t observed_word_00; // 分派完成后由dispatcher清零；本任务不认证业务含义
    uint16_t observed_u16_04; // 格式串标签V
    uint16_t observed_u16_06; // 格式串标签C
    // +08..0c 未在callback读取
    // +0d unsigned byte，格式串标签Mode
    // +0e unsigned byte，格式串标签Dev
    // +24 word，低4bit和bit5:4送格式串port
};
// 链表业务字段：node+0 callback word；node+4 userdata word。
// 链字段next在 node+word[header]+4；不据此认证固定节点C类型。
```

```c
// 伪代码只表达已核本地机器合同；U32/U16/U8保留原访问宽度。
void dispatch_partial(word index) {
    word owner = U32(0x62fcb2cc);
    if (owner == 0) return;
    word base = U32(owner);
    word offset = index * 0x1a8; // 原32位乘法，无本地索引范围检查投影
    word record = base + offset;
    word h = 0x62fcb530;
    word node = U32(h + 4);
    while (node != 0) {
        word callback = U32(node);
        if (callback != 0)
            indirect_call(callback, U32(node + 4), record); // a0,a1
        // 此处在callback返回后重读size，不是入口快照。
        node = U32(node + U32(h) + 4);
    }
    U32(base + offset) = 0; // th.srw zero,s4,s2,0：既存本地模型解释
}

word callback_partial(word userdata, word record) {
    word packed = U32(record + 0x24);
    word low = packed & 0xf;
    word high = (packed >> 4) & 3; // th.extu a4,a4,5,4：既存模型
    // 寄存器a0..a7依次为下列前8实参；后4实参在sp+0,+4,+8,+12。
    return opaque_log_a008b51a(
        4, 0xa02684f0 /* "PogoPinMng/UiIFaceMng.c" */, 0xc5,
        0xa026a5d0 /* "TestItemInfoChangeCallBack" */,
        0xa0268540 /* "UserData = 0x%lx, V = %d, C = %d, Mode = %d, Dev = %d, port = %d:%d" */,
        userdata, U16(record + 4), U16(record + 6),
        U8(record + 0xd), U8(record + 0xe), high, low);
}
```

callback实际读取顺序为：word+24，byte+e，byte+d，halfword+6，halfword+4；伪代码按实参便于阅读排列，不表示改写原读取次序。分派器的callback目标为零时仍前进next，非零时返回后才取next；本任务不恢复回调对链表的其他副作用或所有消费者，也不认证并发/重入合同。

## 可定位指令证据

- `a00a38a0/a4` owner读及空分支，`38aa/ae` 常量0x1a8及乘法，`38c0/ce` base与record计算；`38c8/cc/d2` 同一header/head保存。
- `38ee/f0/f2/f4/f6` 目标读取、空分支、userdata→a0、record→a1、间接调用；`38f8/fc/fe/3900` 调用后重读payload size及next；`38d8` word `412a500b` 按既有模型为indexed store zero，`3902` 为owner空路径ret。
- `3c92` 首次记录读取；`3c94` userdata→a5，至 `3cd4` 调用之间没有覆盖a5；`3c9a` andi低4bit；`3c9e` word `1447370b` 按既有模型提取bit5:4；`3ca2/a4/b2/ba` 将low/high/Dev/Mode分别写sp+12/+8/+4/+0；`3cbc/cc0` 无符号halfword读取；`3cd4` 原JAL目标为 `a008b51a`。
- 字符串的ROM地址、文件偏移、逐条原字节、解码及模型摘录均在 [instruction-evidence.json](../../analysis/basic-info-callback-b08-0041-20261023/instruction-evidence.json)。映射 `file_offset=VA-9ffff000`，只读原ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`。
- 两个函数边界沿用已保留whole-rom inventory并核连续原字节：dispatcher extent Evidence `ev_9a05bdd8ae76e6994ac97a92a7f363d1303d76b44ffd7d7d2acd619f472e1588`；callback extent `ev_84c93d8edb9ab25626ad1db20f5fd014eab1d4df05e78b52f457d361d5b59a65`，body `ev_0d64ebd9da37487a253776f36efd79021421859ed0b498eda428293e008e0cec`。保留inventory的空direct_calls不代表不存在间接调用，本次38f6即为原编码证据。

## 实际验证、来源及未知

运行 `python reverse/analysis/basic-info-callback-b08-0041-20261023/verify.py D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware`：**passed**，两个窗口190B、68普通指令、2厂商word，18关键解码合同断言、16编码/目标检查。脚本直接逐条读取原ROM并以Capstone RV32+C解码，另外从位域核C.LW寄存器/偏移、C.MV、C.JALR、unsigned load宽度与原JAL目标。厂商字段另核op/寄存器/bit范围，与既有 `ap01thead2.sinc` 第3324行extu和6596行srw摘录一致；这只证明沿用既存本地模型，不冒充新增上游ISA认证。未新建共享REA会话/数据库、未改模型、未执行固件、外连、设备或缺陷测试，没有生产构建或新哈希清单。

**事实**：原指令与字节、两个callback实参的寄存器流、宽度/偏移、字符串和局部控制流。**推断/模型依赖**：userdata/record/index等命名，格式标签与业务字段对应，仅日志用途按可见调用合同解释；两个厂商word沿用本地模型。**未知**：实际链表内容、callback实际触发/调用顺序的运行时事实、记录字段业务类型/单位、owner生命周期、其他消费者、日志实现与C类型、并发重入、任何蜂鸣器关联。代码仍为厂商/来源未知，无可核实开源版本识别，本次无开源排除。此callback局部恢复，基础信息模块整体仍部分恢复。

下一小任务建议 B09：独立复核本报告两个核心函数的间接ABI、userdata首用/日志参数顺序及厂商位域；仅限定现有窗口，不扩展消费者集合或基础信息状态机。
