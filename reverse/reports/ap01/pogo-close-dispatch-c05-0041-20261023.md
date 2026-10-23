# C05：PogoPin close 登记、待处理链与 callback 实参

2026-10-23；分支 `codex/re-0041-c05`，基线 `616d3f8`。**局部合同已闭合，待独立技术复核；完整关闭/timer 生命周期仍部分恢复。** 本文伪代码为分析者表达，不是原始源码。仅静态读取 ROM；未执行固件、连接实机或外部服务、开展缺陷验证或修改分析器模型。

## 本次回答

`a009fb96(a0=handle,a1=callback)` 将 callback 存入 handle+0xc，不在该登记点直接调用。type byte 为8的分支调用 `a009f972(handle)`，返回后进入 `a009c228(handle)`，以 handle+0x28 和 loop+0xd4 构成单向待处理链。既有初始化容器中的消费片段先摘走 loop+0xd4，再对每个节点调用 `a009f524(handle)`。后者的 type=8 路径进入共用尾部，在 `a009f8e6` 间接调用 handle+0xc，a0 保持为原 handle 地址。

因此 [C03](pogo-close-callback-c03-0041-20261023.md)/[C04](pogo-close-review-c04-0041-20261023.md) 的 `a00a3bc6` 收到的是 poll/handle，而不是 context；它在 `a00a3bd0` 读取 poll+0，才取得已有初始化窗口保存的 context。此处没有 container_of 减偏移，也没有分派器把 context 当 a0 提前传入。

核心范围是上述三个函数的相关路径：`a009fb96`、`a009c228`、`a009f524`。仅引用既有 initializer 的两个短消费窗口、poll init 的 type/loop 保存短窗口以及既有 callback 的入口作参数佐证，不恢复这些容器全函数。`a009f972`、链表摘除封装、assert处理和其他类型分支保持未展开；没有扩大成完整 libuv/poll/timer 分析。

## 原指令事实与调用合同

证据：[instruction-evidence.json](../../analysis/pogo-close-dispatch-c05-0041-20261023/instruction-evidence.json)；生成/核对：[check-static.py](../../analysis/pogo-close-dispatch-c05-0041-20261023/check-static.py)。ROM 为主仓库 `roms/0041/ap01-1.0.2_0041.bin`，映射基址 `9ffff000`。沿用既有 ROM 身份证据，不另制哈希或复制清单。既有 initializer 证据为 `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，脚本验证其保留 raw ranges 与 ROM 一致。

| 函数/局部 | 参数、返回与指令依据 |
| --- | --- |
| `a009fb96` 关闭登记的 type=8 路径 | a0=handle，a1=callback。`fbaa/fbac/fbb0` 要求原 flags@+2c 的低2位为0，否则转assert参数构造路径；不对assert处理器是否返回作新判断。`fbc2/fbc6` 写原 flags OR 1；`fbc8` LBU type@+8；`fbcc` SW callback@+c；`fbd0` s2=handle。`fc04/fc06` 比较type=8后转 `ffbe`；`ffbe` 调 `a009f972`，`ffc2` 回 `fcde`，`fcde/fce0` 以a0=s2调用 `a009c228`，`fce4` 转恢复/返回片段 `a00a0026..0038`。没有确认业务返回值，不能把最终a0解释为成功码。 |
| `a009c228..c268` 待处理链插入 | a0=handle。`c230..c254` 核flags bit0为1、bit1为0，否则走assert处理；`c256` a5=word(handle+4)，`c258` a4=word(a5+d4)，`c25c` word(handle+28)=a4，`c25e` word(a5+d4)=handle，然后返回。正常路径不读写handle+0的context和handle+c的callback；无确认业务返回值。 |
| initializer 既有消费片段 | 沿用既有s1=loop合同。`a005c166/c16a` 取loop+d4到a0并清空该head；`c16e` 非空转c802；`c802` 先把word(a0+28)保存到s5，`c806` 调 `a009f524(a0)`，`c80a/c80c` 取保存的next并回c16e。这是静态调用关系，不是实际执行/调度顺序观测。 |
| `a009f524` 完成消费的 type=8 路径 | a0=handle；`f538..f564` 检查bit0=1/bit1=0并设置bit1；`f566` LBU type；`f56c` s1=handle。`f580..f58e` 计算 `(1u<<type)&0x275e`，type=8时非零，直接转 `f8b6` 共用尾部，无需展开其他类型清理。`f8b6..f8d4` 处理原flags bit3，必要时清位及调整loop+4计数；在本路径bit0已置1，bit0非零分支跳过该尾部的loop计数减一。`f8d6/f8da` 把handle+10交 `a0098b4a`；该callee未展开。`f8de` 读callback=word(s1+c)，空则返回；`f8e4` a0=s1，`f8e6` C.JALR a5；随后f8e8跳恢复/返回片段f5ba。callback返回值在本局部未被消费，函数业务返回值未知。 |

新增短佐证：`a009e5f6/e5fc` 将type byte8保存到原poll参数s5+8；`e600` 初始flags写8；`e604` word(s5+4)=s3（loop，沿用该初始化器入参保存关系）。这里只重核这些普通指令，不认证该初始化器完整成功合同、早期厂商指令或fd有效性。PogoPin四组内嵌poll及其首word=ctx关系沿用C03/C04，不新作全ROM类型枚举。

## 偏移视图与伪代码

所有偏移均为十六进制；此视图只表达已观察字段，不代表完整ABI或原始结构体。

```c
struct HandleObserved {
    void *context;         // +00，PogoPin自己的回指，登记器不替换它
    LoopObserved *loop;    // +04
    uint8_t type;          // +08；本任务只跟type=8
    // padding omitted
    void (*close_cb)(struct HandleObserved *); // +0c
    // +10: list node，底层摘除未展开
    // +28: next_pending
    // +2c: flags word
};
// LoopObserved +d4: pending_head；+04为另一计数字段，不等于ctx+198。

// 仅表达满足所列flags前置条件的type=8路径，非完整实现。
void close_type8_path(HandleObserved *h, CloseCallback cb) {
    // 原程序在低2位非0时进入assert处理路径，未在此补造处理合同。
    write32(h, 0x2c, read32(h, 0x2c) | 1u);
    write_callback(h, 0x0c, cb);
    opaque_a009f972(h);
    enqueue_a009c228(h);
}
void enqueue_a009c228(HandleObserved *h) {
    // 此处原assert前置：bit0=1、bit1=0。
    h->next_pending = h->loop->pending_head; // +28 / +d4
    h->loop->pending_head = h;
}
// 既有initializer的局部调用片段，不是完整loop。
void consume_observed_fragment(LoopObserved *loop) {
    HandleObserved *h = loop->pending_head;
    loop->pending_head = NULL;
    while (h != NULL) {
        HandleObserved *next = h->next_pending; // 在callback之前保存
        finish_a009f524(h);
        h = next;
    }
}
// a009f524 type=8路径的末端：原flags处理在表中描述。
void finish_type8_tail(HandleObserved *h) {
    opaque_list_remove_a0098b4a((uint8_t *)h + 0x10);
    CloseCallback cb = read_callback(h, 0x0c);
    if (cb != NULL) cb(h); // a009f8e4/f8e6，不是cb(h->context)
}
// 已验收C03/C04入口：a00a3bc6(h)内部才读取h->context。
```

调用边闭合为：既有PogoPin deinit注册 `(内嵌poll,a00a3bc6)` → `a009fb96` 保存+0c → type8分支 → `a009c228` 插入loop待处理链 → 既有消费片段 → `a009f524` → `word(poll+0c)(poll)` → `a00a3bc6`读取 `word(poll+0)`。这是静态可达和实参合同；并不证明登记后必定再次进入消费循环。

## 事实、推断与未知

**事实：**callback字段宽度32位，type读取8位；待处理链保存的是原handle地址；消费方在调用前保存next；间接调用前a0=原handle；最终context来自callback自身的首word读取。poll init所见type=8、flags=8与该分支匹配。登记和上述链操作的已核普通指令不直接改写poll+0；不将未展开callee行为包含在这一否定结论内。

**推断：**+0c为关闭callback、+28为待处理next、loop+d4为关闭待处理head；这些命名由登记/消费指令和既有模块调用关系共同支持。虽然布局/行为与常见事件循环关闭模式相似，不能凭相似性确认libuv版本或将其排除。

**未知：**登记之后该消费片段是否继续运行、所有退出路径是否都消费head、`a009f972`实际停止动作、`a0098b4a`完整副作用、其他type清理、并发/重入合同、关闭计数全局不变量、timer停止/删除及context释放前全局时序。ctx+198与loop+4不同，不将两者合并；本任务不作缺陷结论，不构造或执行异常输入。

来源状态：PogoPin callback继续按私有/来源未知管理；三个分派/队列函数及底层库未取得可核实来源/版本，新开源排除为0。恢复程度限于type=8的登记、入队、既有直接消费及callback传参链；完整模块仍未完成。

## 实际验证与下一小任务

运行 `python reverse/analysis/pogo-close-dispatch-c05-0041-20261023/check-static.py`：12个选定窗口490 B完整普通RV32/RVC解码，未解码字节0；31项原编码寄存器/偏移/branch/JAL/C.J/C.JALR等核对通过；type8属于0x275e共用尾部掩码；既有initializer raw ranges与ROM一致。脚本只读ROM并写本C05目录，不打开共享REA会话/数据库。已阅读REA技能，使用既有保留证据及独立原指令核对；没有执行固件或生产构建。函数范围仅局部entry/调用/返回路径，不声称重新确定完整dispatcher的所有函数边界。提交前执行 `git diff --check` 和独占路径差异检查。

下一小任务建议：独立复核本次type=8登记/待处理链/间接调用合同及负结论边界；通过后只追既有deinit后是否有一次直接消费机会，保持1～3核心函数边界，不同时扩大timer扫描。
