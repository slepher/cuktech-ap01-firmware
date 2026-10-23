# A35：A33 照片新源 ABI 独立复核

2026-10-24；独立基线 `f2c1458f2fe731a01e849d669f1884918c0d2ef9`，分支 `codex/re-0041-a35`。**限定接受 A33 的新 source ABI 与工作区指针交接，没有语义纠正，新增功能恢复为 0。** 原字节重读只作旧结论独立复核；没有重新恢复照片业务、五表资源或 GIF 解码。采用 reverse-engineer-anything 技能，未打开共享可写 REA target/数据库。

## 继承结论：已有出处→行为→局限→实际缺口

|已有出处|已解释行为|证据局限|本轮处理|
|---|---|---|---|
|[A33](photo-source-abi-a33-0041-20261024.md)、其 `analysis/evidence.json` 与 `verify.py`|照片新源表加载、setter 的两个实参、descriptor+0x10 到内存输入工作区|研究交付尚待独立核厂商字、寄存器及偏移宽度|唯一技术复核对象，见逐项处置|
|A33 引用 `photo-evidence-round3.json#/rea_records/3`，Evidence `ev_e3db1fb1f6b8b75d3ba7fbf202ad701f4cd3b8eb42987c05789f1e2626527941`；main-knob round2 `ev_daf583e6c481f2d7f53eb8443cd04003d53c22365147ac088957c1415a947da7`；system complete|五项照片轮转、type7 查找、setter 调用和写回索引早已留存|旧反编译 source 是 `custom0.rd()`；整函数存在不能认证该厂商字|继承业务与旧证据定位，不重导 callback|
|A33 的五项表及资源身份；最终 ZIP `tools/ap01/ap01-ui-pages.h`、旧 SIM/照片验收|ROM 五项描述符及照片/宠物页业务已有；SIM 用 `ap01_pets` 重建|SIM 替代实现不能认证 ROM ABI；五项存在不等于实际显示成功|直接引用，不重读资源表、不提取/解码或命名资源、不执行 ZIP|
|[A29](image-cache-invalidation-a29-0041-20261024.md)、[A31](image-cache-invalidation-review-a31-0041-20261024.md)|对象+0x5c 门、getter +0x2c 旧 source、同 image-cache 指定 key 失效接入已闭|不证明运行时命中或每次切页满足门；A31 当时未核的新 source 由 A33 补查|旧源链全继承，不重导失效/getter/cache；不能继续把新 source 记为未认证|
|A23–A28，A33 引用的分类 helper 与清零合同|source 分类、PNG/session/Pixel/raw 所有权及 cleanup 已有|不能套到 GIF 构造器内部所有权|只继承必要 helper 合同，不重做分类、PNG、cleanup|

证据类型分开：本轮是原字节局部核；旧 `custom0.rd()` 是已定位的反编译限制；SIM/照片验收是替代实现；构造器内部及运行时切页是未核边。没有把旧 pending 或查询未命中解释为此前从未分析。

## 本轮复核或纠正：逐项处置

|A33 结论|处置|独立校核及接受边界|
|---|---|---|
|`a00b180c` 是 `th.lrw a1,a5,a6,2`，读取表项中的指针值|接受|原字节 `8b c5 07 45`，小端指令 word=`0x4507c58b`；独立拆得 opcode=0x0b、f3=4、bits31:27=8、rd=11、rs1=15、rs2=16、shift=2。只读 `ap01thead2.sinc` 对应规则读取 `*[ram]:4 (rs1+(rs2<<shift))` 并写 rd，无 base/index 回写。不是表槽地址，也不是复制 descriptor。原模型仅作厂商语义局部依据，不认证整模型/整库来源。|
|表基址 `a055fe44`、32 位索引轮转|接受|`a00b1804` 的 LUI 高位 `a0560000` 配 `1808` ADDI -0x1bc，形成该地址。`17f8` LW a6,0xc(s1)，`17fc` RV32 C.ADDI +1，`17fe` BGEU a5,a6 精确到 `1804`，a5=4；否则 `1802` 置 a6=0。宽度/无符号比较成立；五表内容直接继承。|
|调用 `a00ed7f4(ctx[0],source)`，之后写回索引|接受|`17f2/17f4` 取 page+0x10 再+4 得 ctx(s1)；`1810` C.LW a0,0(s1)，厂商字将新 source 写 a1；`1812` SW a6 到 s0-0x144，`1816` JAL ra 目标 `a00ed7f4`；`181a` 返回后 LW 原 next，`1824` SW 到 ctx+0xc。该 caller 未以 setter 返回 a0决定写回；不推断 API 返回类型。|
|setter 保持新 a1，class0 读取 descriptor+0x10|接受|`a00ed808` C.MV s3,a1；`d830` C.MV a0,s3、`d832` JAL `a00dd454`；`d836` C.BNEZ a0 跳过 class0，返回0才执行 `d838` LW a0,0x10(s3)、`d83c` JAL `a0107dea`。读取的是32位指针值，不是 descriptor+0x10 的地址本身；不重复认证 classifier 内部。旧源分支中的 s3 保存和调用合同继承 A29/A31。|
|借用数据指针进入工作区+0xc，工作区传 `a010a65a`|接受，限定至调用边|`a0107dfe` C.MV s1,a0；`e00/e04/e06` 传 a2=0x664、a1=0、a0=s0-0x674 至既有清零 helper `a0024906`；`e0e` 重设 a0=同工作区；`e12` SW s1,s0-0x668，差值=0xc；`e16` SW zero 到工作区+0x14，`e1a` SB zero 到+0x10；`e1e` JAL ra 精确到 `a010a65a`。此窗口按值保存指针，未复制描述符/GIF payload；仅此交接可称借用，不证明构造器内部绝无复制或无所有权变化。|
|setter 仅在内存输入返回非零时继续成功路径|接受|`d840` C.MV s2,a0；`d842` BNE s2,zero 精确到 `a00ed884`。零分支日志/返回语义继承 A33，未重导；静态指针存在不能替代构造成功或显示成功。|
|五项资源内容、旧源失效、PNG/cache 内部与 GIF 完整生命周期|继承或未另核|资源和旧源可靠合同直接引用；GIF 内部复制/持久化没有接受结论，不以 PNG 所有权代填。|

没有语义纠正；为避免十六进制偏移歧义，本报告统一将 A33 的 `descriptor+10`、`s0-674`、`工作区+c` 写成 `+0x10`、`-0x674`、`+0x0c`。这是记号明确化，不是字段变化。

必要连接可表为以下分析伪代码，并非原源码或完整函数：

```c
uint32_t next = load32(ctx + 0x0c) + 1; // RV32 wrap
if (next > 4u) next = 0;
uint32_t source = load32(0xa055fe44 + (next << 2));
a00ed7f4(load32(ctx), source);
store32(ctx + 0x0c, next);              // 从保存槽重读
// setter：分类返回0的路径
uint32_t data = load32(source + 0x10);
// a0107dea：工作区 W = s0-0x674
memset(W, 0, 0x664);                    // 既有 helper 合同
store32(W + 0x0c, data);
store32(W + 0x14, 0);
store8(W + 0x10, 0);
object = a010a65a(W);                   // 内部持久化/复制未核
```

表与 descriptor/data 为既有 ROM 身份；此边没有申请、归还或释放这些 ROM 数据。W 是栈工作区，其地址只在同步调用边被传递；不能由栈属性推断 callee 不保留 W，也不能据此宣称发生了保留。返回对象的完整生命周期留在明确断边内。

## 真正新增

新增功能、照片业务、资源恢复与来源排除均为 **0**。仅新增 A33 指定范围的独立接受结论和 [33 项稀疏原字节检查](../../analysis/photo-source-review-a35-0041-20261024/review-evidence.json)。没有重复整函数、表资源、ZIP、源码导出或机械哈希账。

## 未闭精确边、验证及后续闭包

- `a010a65a` 对 W+0x0c 输入的复制、持久保存、返回对象内的输入槽及完整 GIF 生命周期仍未核。唯一后续闭包是另题连接该输入槽至返回对象保存槽；不能重做照片/PNG 来代替它。
- 实际主旋钮命中、实际切页时序、对象+0x5c 门、cache 命中/引用数及显示/解码成功没有执行观察。A29/A31 旧源边界保留；A31 当时的新 source ABI 未知已由本次限定接受关闭。
- 精确库/编译版本、其余 setter caller、正常页面退出连接不在接受范围；厂商规则局部匹配不等于整模型或整库来源认证。

[verify.py](../../analysis/photo-source-review-a35-0041-20261024/verify.py) 仅用 Python 标准库，只读主仓原 ROM，按 `offset=VA-0x9ffff000` 独立解码 LW/SW/SB/ADDI、C.LW/C.MV、BGEU/BNE、JAL 和厂商位域；33 项通过。未导入 A33 解码器、未运行其写证据脚本，未重新读取五表资源；模型只读核对应规则。JSON 可解析、报告本地链接及 `git diff --check` 通过。无固件执行、SIM、构建、历史回放、设备或外网；未改生产代码、ROM、配置、模型、共享索引，只写本题独占 report/analysis。
