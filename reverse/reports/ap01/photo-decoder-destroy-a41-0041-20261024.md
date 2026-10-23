# A41：照片内存 decoder 旧对象替换与派生槽撤销

2026-10-24；基线 `2844cc4`，分支 `codex/re-0041-a41`。**已闭合 setter `a00ed7f4` 对非空旧 O、内存 mode byte 为零路径的归还连接：先完成既有旧 source cache 失效，再 `a008ab8a(O)`，返回后清 owner+0x5c，继而清 owner+0x74，最后才进入新 source 分类与构造。** O 的内部输出区不独立归还，借用 ROM 输入不被作为归还实参。采用 reverse-engineer-anything 技能，只读原 ROM/既有证据；未打开共享可写 REA target。

## 继承结论：已有出处→行为→局限→精确缺口

|已有出处|行为及继承范围|局限与本轮处理|
|---|---|---|
|[A33](photo-source-abi-a33-0041-20261024.md)、[A35](photo-source-review-a35-0041-20261024.md)|新 ROM source 的 descriptor+0x10 data → 清零 W；W+0x10 mode=0；setter 正常内存构造入口已有|不重做新 source ABI、分类、五资源或轮转；本轮只读旧 O 分支|
|[A37](photo-decoder-owner-a37-0041-20261024.md)、[A39](photo-decoder-review-a39-0041-20261024.md)|O 单块分配 `0x4664+5N`，复制 W 的0x664字节状态；O+0x0c保留借用ROM输入，O+0x658/+0x65c/+0x660指入同一块；owner+0x5c=O、owner+0x74=O+0x658的值|原状态复制不是整体payload克隆；这些结论均继承。本轮唯一缺口是旧O直接callee与派生槽清除原序|
|[A29](image-cache-invalidation-a29-0041-20261024.md)、[A31](image-cache-invalidation-review-a31-0041-20261024.md)|旧O非空时 getter `a00eaa50(owner)` → `a00890e8(old_source)` 接入既有cache失效|cache失效不是O析构；不重导callee或cache cleanup|
|主仓 `reverse/rehost/photo-evidence-round3.json#/rea_records/3`，`ev_e3db1fb1f6b8b75d3ba7fbf202ad701f4cd3b8eb42987c05789f1e2626527941`；main-knob round2；system complete|旧照片轮转及setter caller已有；最新轮次不能被较早custom0局限覆盖|本轮按setter及清理地址有界检索主仓rehost全部顶层JSON，命中仍为上述三份caller留存；这不是证明此前从未分析setter|
|A37引用 weather-calendar-complete `#/evidence/30`、page-logic `#/records/15`；最终ZIP照片/pages实现与旧SIM验收|reader/constructor早期原指令、caller清单及照片替代实现已有，局限由A37明确|继承出处和边界，不重导旧body，不读取/解码ZIP资源，不用SIM证明ROM归还ABI|
|[C03](pogo-close-callback-c03-0041-20261023.md)、[C04](pogo-close-review-c04-0041-20261023.md)|`a008ab8a(ptr)` 对NULL/哨兵`62fc95e0`返回，否则把原ptr交`a002e14e`；已有释放封装合同|本轮直接复用，不重新恢复heap，不声称观察实际内存复用|

## 本轮复核或纠正

没有纠正A37/A39。必要原字节区间仅 `a00ed802..a00ed82f`，见 [evidence.json](../../analysis/photo-decoder-destroy-a41-0041-20261024/evidence.json)。该窗口的普通RV32/压缩指令足够回答本题，不需要厂商指令推断或另开数据库。旧报告所留“最终析构/+74撤销未知”现仅收窄正常setter替换分支；页面最终销毁来路仍未知。

`a00ed802` 的LW先将owner+0x5c保存s2，`806`保存owner为s1；后续free使用此旧值s2，并非cache getter返回值，也不是重新取owner+0x74。`80a` 为BEQ s2,zero，零时直接到`830`，同时跳过本块两次清槽；不能把“进入setter”改写成无条件清槽。

`816` 是 **LBU** O+0x10，对整个byte是否为零作分支，没有bit掩码。`81a` 的C.BEQZ准确跳到`822`，即跳过`81c/81e`。这与继承的内存reader初始mode=0相接；本题不做所有decoder写者穷举，不把初始值外推为任意运行时对象必为零。

## 真正新增：旧O归还到两个owner槽的正常连接

|地址|参数、调用与原顺序|
|---|---|
|`a00ed80e/812`|旧O非零才以尚保留的a0=owner调getter，再以其返回的旧source调cache失效；详细callee继承A29/A31|
|`a00ed816/81a`|读U8(oldO+0x10)；为零直接跳到`a00ed822`。非零另以a0=oldO调`a01b2e3a`后汇合；本题不将该callee补成ROM输入free，也不展开文件模式内部|
|`a00ed822/824`|a0=s2=入口保存的oldO，JAL ra至`a008ab8a`。归还的是整个对象分配基址；其后不再读oldO字段，本窗口没有向free传O+0x0c输入、O+0x658或owner+0x74派生地址|
|`a00ed828`|free调用返回后，SW zero至owner+0x5c；不能改写为free前先清槽|
|`a00ed82c`|随后SW zero至owner+0x74。这是撤销owner的派生引用，不是第二次归还；O内部区域随基址分配一起归还|
|`a00ed830`以后（继承A33/A37）|才以保存的新source开始分类/构造，成功非零后重建owner+0x5c和+0x74。所以正常旧对象替换不是先成功构造新O再释放旧O；新构造失败也不能据此虚构旧O回滚|

必要分析伪代码，非原源码；仅表示本题边界内的正常连接：

```c
old = load32(owner + 0x5c);        // s2；owner保存s1，新source保存s3
if (old != 0) {
    a00890e8(a00eaa50(owner));     // 已闭旧source失效
    if (load_u8(old + 0x10) != 0)
        a01b2e3a(old);            // 非内存mode分支内部未恢复
    a008ab8a(old);                // 内存mode0从上方直接汇合至此
    store32(owner + 0x5c, 0);     // 原程序先free，后清根槽
    store32(owner + 0x74, 0);     // 再清派生槽
}
// 后续分类/构造合同直接继承A33/A37；此处不推业务返回类型。
```

所有权解释：原ROM data仍是借用输入；W状态副本O拥有其自身单块状态/表/输出区，owner持有O及内部派生地址。mode0旧O被整体归还后，两个owner槽才先后撤销。由于这段没有对借用输入做归还，也没有针对内部区的独立申请根，不能发明三次或多次free。调用顺序是原程序事实，不据此讨论异常并发、悬空访问或缺陷；本任务不作此类验证。

## 未闭精确边、来源与必要静态验证

事实为以上普通指令的保存值/直接调用/宽度/跳转和store原序；“内部输出区随单块O归还”是结合已验收A37/A39分配布局与C03/C04释放封装的所有权推断。未观察实际照片命中、heap回收、显示或页面时序；不认证格式/库版本/编译来源，不作标准库排除。

未闭边为非零mode下`a01b2e3a(oldO)`的具体文件资源处理、最终页面DELETE是否/如何调用同类析构，以及底层allocator实现。它们不是本题ROM内存mode0正常替换的必要callee。唯一后续建议：先复用旧控件class/DELETE留存，从已安装的具体照片对象析构入口核到同一owner+0x5c旧值归还；若无实际入口种子则有界报告，不扩所有控件销毁。

[verify.py](../../analysis/photo-decoder-destroy-a41-0041-20261024/verify.py) 只读主仓ROM/历史JSON，保存1个必要短窗，15项命名检查通过，另独立解码直接JAL、BEQ/C.BEQZ及LBU/SW位域，核非空门、mode零汇合、实参和两次清槽宽度/原序。JSON解析、报告本地链接、`git diff --check`通过。无固件执行、SIM、构建、回放、设备、外网、资源解码或模型修改；只写本题独占report/analysis。本报告为研究交付，待独立技术复核。
