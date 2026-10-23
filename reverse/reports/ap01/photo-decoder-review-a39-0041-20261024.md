# A39：A37 照片 decoder 对象持有独立复核

2026-10-24；基线 `db28e9987da77c12ae83b1167d69a537215edf50`，分支 `codex/re-0041-a39`。**限定接受 A37 指定的正常分配→W 状态复制→返回 O→owner 保存槽合同；没有语义纠正，新增功能恢复为 0。** 采用 reverse-engineer-anything 技能，仅静态重读必要原字节，未打开或共享可写 REA target/数据库。

## 继承结论：已有出处→行为→局限→本题缺口

|已有出处|已解释行为|证据局限与本题处理|
|---|---|---|
|[A37](photo-decoder-owner-a37-0041-20261024.md)、其 `evidence.json`/`verify.py`|W→O 的 0x664 字节状态复制、分配式、内嵌区域及返回保存槽已研究|本题只独立核其正常成功闭包的 ABI、厂商原字及宽度，不声称首次恢复 decoder|
|[A33](photo-source-abi-a33-0041-20261024.md)、[A35](photo-source-review-a35-0041-20261024.md)|source/class0 的可信 data 实参、清零栈 W、W+0x0c=data、mode/cursor 初值和 constructor 调用边已接受|全继承；不重导 setter/分类、五项表或资源；A35 当时保留的内部持有边由 A37 补查，本题审 A37|
|A37 引用 `weather-calendar-complete-0041.json#/evidence/30`，address=`A010A302`|旧 reader/seek 原序与 constructor 开头已留存|stdout 自带截断，不能代替后段；本题沿用 A37 已补留的稀疏原字节，不重导旧 body|
|A37 引用 `page-logic-0041.json#/records/15`，`ev_794a176f91454b7304c06fbfaff53024aa96bf8a3a51698dbb831f8b9359f9ef`；whole-ROM extent/direct-call Evidence|清零 helper caller 清单、constructor 地址范围早已有|地址/引用记录不等于对象值流；不把查询未命中称为此前未恢复|
|[A29](image-cache-invalidation-a29-0041-20261024.md)、[A31](image-cache-invalidation-review-a31-0041-20261024.md)，以及 A25/A30/A32、G03/G04|旧 source 同 cache 失效、allocator/copy helper 接口已有|直接继承 `a008aea0(size)` 与 `a000589c(dst,src,n)`；不套用 PNG cleanup 或将失效当 O 析构|
|A33/A35/A37 引用旧照片 round3、system complete、最终 ZIP 和 SIM 验收|五资源与照片业务、替代实现已有|不重读/执行资源或 ZIP，不以 SIM、文件名或字节形状认证 ROM 格式/库版本|

原字节局部核、旧反编译局限、SIM/照片替代和未闭精确边分别保留。既有成果已覆盖主体，本题没有重搜完整 decoder、资源或全 ROM 负引用。ROM 身份及 `offset=VA-0x9ffff000` 继承 A33/A35/A37。

## 本轮复核或纠正：逐项处置

|A37 结论|处置|独立核对与接受范围|
|---|---|---|
|W 保存为 s2，正常路径分配 O|接受|`a010a678` 原字 `2a89` 为 C.MV s2,a0；`a010a79e` 原字 `b38a6b03` 独立拆为 RV32 MUL s5,s7,s6。`7ae` JAL 目标为 `a008aea0`，`7b2` 保存返回 s1，`7b4` BEQ a0,zero 到 `a010a6b4`。只接受分配非零之后的正常路径，不外推所有失败臂。|
|请求大小为 `0x4664+5N`，N 为两维乘积|接受|`7a2` C.LUI a0,4，`7a6` ADDI +0x664；`7a4` a5=5。`a010a7aa` 小端原字 `0b95fa20` 的 opcode/f3/f7/rd/rs1/rs2 为 `[11,1,16,10,21,15]`，与只读局部 `th.mula` 规则 `rd += rs1*rs2` 对应，得 RV32 分配实参 `0x4664+5N`。没有遗漏额外 0x4000，也未认证其用途或异常算术域。|
|copy(O,W,0x664)，O+0x0c 按值保留原 ROM 指针|接受|`7b8` ADDI a2,zero,0x664，`7bc` C.MV a1,s2；a0 仍为分配返回 O。`7be/7c2` 的 AUIPC/JALR 独立合成目标 `a000589c`。既有 copy 接口直接继承，并抽核 `a00059e8/59ec` 的 LW/SW +0x0c 均为32位。复制的是 W 的状态字节，含源指针值；不是保存 W 地址，也不等于克隆整个输入 payload。|
|尺寸字段和内嵌派生区|接受|`7e8/7ec` 独立 S 型拆解为 SH 到 O+0x1c/0x1e；`80a` 得 O+0x664，`80e` 取 O+0x600，`812` 的 C.SW +0x58 即 O+0x658。`814` 原字 `0b155505` 的位域为 `[11,1,2,10,10,21]`，shift bits26:25=2；局部 `th.addsl` 得前值+4N，`818` 写 O+0x65c。`838` LW 该槽，`83e` 加到 s5(N)，`840` SW 到 O+0x660，得 O+0x664+5N。槽均为32位，派生区共享同一次分配。|
|O 经 `a0107dea` 原样返回|接受|`a010a880` C.MV a0,s1 先置返回 O，之后才恢复 s1、返回；wrapper 的 `a0107e1e` JAL 目标为 constructor，`7e22..32` 只恢复 ra/s0/s1/sp 并 JR ra，不改 a0。未由栈 W 的生命周期推断 O 只能依赖 W。|
|非零 O 保存 owner+0x5c，输出派生指针保存 owner+0x74|接受|`a00ed83c` 调 wrapper；`840` C.MV s2,a0；`842` BNE s2,zero 精确到 `a00ed884`。`884` SW s2,0x5c(s1)，`888` LW a5,0x658(s2)，`88c` C.SW a5,0x74(s1)。保存的是 O 与 O 内部区域的32位指针值，没有第二次独立分配的依据。|
|局部表字节复制及正常初始化不等于 payload 完整克隆|接受其边界|A37 已区分 O+0x340 的表读取与 0x664 状态复制。本题不否认这些输入字节复制，不把状态按值复制改写成“constructor 完全不复制输入”。不扩压缩/像素算法。|
|reader/seek、五资源、cache cleanup、完整析构/格式来源|继承或未另核|前者按上述可靠合同继承；完整析构/格式来源继续未核。两条局部厂商规则匹配不升级为整模型或整库版本认证。|

没有语义纠正。必要分析关系可写为下式，非原源码，也不代替 header 检查、初始化和失败原序：

```c
// W 的清零/data/mode/cursor 接入由 A33/A35 继承。
N = dim0 * dim1;                 // RV32 MUL
O = a008aea0(0x4664 + 5*N);
if (!O) goto existing_failure;
a000589c(O, W, 0x664);           // 包括 load32(W+0x0c) 的指针值
store32(O+0x658, O+0x664);
store32(O+0x65c, O+0x664+4*N);
store32(O+0x660, O+0x664+5*N);
// 正常构造返回 O；wrapper 不覆写返回 a0。
if (O) {
    store32(owner+0x5c, O);
    store32(owner+0x74, load32(O+0x658));
}
```

业务与生命周期含义：照片新源仍借用已知 ROM data；栈 W 的 reader 状态被复制到新分配 O，O 保存相同 ROM 输入指针和独立状态/内嵌区域。owner 同时持有 O 与指入 O 的输出区。该持有关系可使 W 返回后结束生命周期；“持有/分配”不含尚未证明的最终释放、引用计数或运行时成功显示。

## 真正新增

新增功能、资源恢复、算法恢复及来源排除均为 **0**。新增的是上述 A37 合同的限定独立接受记录及 [review-evidence.json](../../analysis/photo-decoder-review-a39-0041-20261024/review-evidence.json)。未重跑 A37 写证据脚本，未导入其解码器；局部原指令阅读复用了既有只读反汇编 helper，最终断言由本题标准库位域脚本独立生成。

## 未闭精确边、实际验证与后续闭包

- O 最终析构、正常替换/离页连接、owner+0x74 撤销及其相对 O 释放的顺序仍未知。A29/A31 的旧 source cache 失效不能代填；唯一后续闭包可追 owner+0x5c 旧 O 到实际析构/+0x74 撤销，先检索完整旧阶段。
- 整体输入上界、`0x4000` 额外区用途、正式结构名、格式/库版本仍未知。当前 state-copy 合同不产生输入总长度，也不认证算法来源。
- 不接受运行时实际命中、分配/解码/显示成功、所有失败路径、动态文件模式或完整压缩算法的结论；本题没有相应执行证据。

[verify.py](../../analysis/photo-decoder-review-a39-0041-20261024/verify.py) 只读主仓 ROM/现有模型，独立按 RV32 I/S/J/B、压缩字和厂商位域作 **40项** 稀疏检查，并核两条局部厂商规则，结果 PASS。JSON 可解析，报告相对链接与 `git diff --check` 通过。没有执行固件、资源、SIM、构建、回放、设备或网络操作；没有修改 ROM、生产代码、配置、模型或共享索引。独占产物为本报告与对应 analysis 目录。
