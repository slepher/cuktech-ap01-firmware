# G23：G19/4 条件服务的状态门、局部副本与完成记录消费

2026-10-24；研究基线 `32f9c9e`，分支 `codex/re-0041-g23-resume`；挂唯一认领 **G19/4**。本轮管理窗口恢复三席后明确派发，只研究 `0xa009e1f0→0xa009dfcc(backend_fd,C,S)` 的callee差集。**该入口不能被写成已成功提交环条目：入口有非−1门和两组counter条件，非零差值路径明确写常数0x26并读错误槽候选；后半消费另组counter所指的16 B记录，先增consumer，再读记录。局部16 B副本与op3重新接入均有原字，但到达这些后段的正常前提没有闭合。** 不把诊断之后的线性排列当作可达性证明，不作缺陷推断或输入试验。

使用 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的既有留存优先与证据边界规则；读过主仓最新 [流程](reverse-design.md) 和 [认领表](rolling-management-0041-20261023.md#链条认领表)。没有打开/切换共享REA、运行目标/指令/模型、SIM/QEMU、构建、历史回放、设备或外部服务，没有修改ROM、生产代码、配置、分析器模型或共享表，没有下级agent，没有提交或推送。本文伪代码均为静态分析表达，非原源码；作者自检仍待独立复核。

## 继承结论

|已有出处|已解释行为与局限|本轮差集|
|---|---|---|
|[G19](pogo-poll-cancel-backend-g19-0041-20261024.md)/[G20](pogo-poll-cancel-review-g20-0041-20261024.md)，G19/1–2|W=P+0x34的取消、fd聚合、六参调用端与stack16已有独立限定接受|只继承该输入来源，不重做stop/ready/close与计数释放|
|[G21](pogo-poll-submit-g21-0041-20261024.md)/[G22](pogo-poll-submit-review-g22-0041-20261024.md)，G19/3|实际op2先写tail、copy16、zero64并构造条目；`((head^tail)&mask)==0`才以原S基址调用本题入口，返回未被上层判断|不重读op2本体、不认证别名/对齐/容量/发布成功；本题只展开已登记G19/4|
|G11/G12及G03/G04|fallback和对齐copy16/zero64的限定合同已验|只继承`0xa000589c`的正常对齐16B值复制；不重新导出库函数，不重做fallback或其他op|
|[whole-ROM旧索引](../../analysis/whole-rom-coverage-0041-20261023-round1.json)，`/functions/2356`|entry `0xa009dfcc`；extent `0xa009dfcc..0xa009e0e5`，282B，Evidence `ev_3389f9eb111676b5aa1d29ed405d754612ba2d22d0899a45d361148734f89779`；directcall Evidence `ev_6e8ac40e4549bbf220c9a7869277a91b8ca2984a1a2baa6431d765f3bab83edd`|`historical_dossier=null`、`dossiers=[]`、无旧合同；这些metadata不能回答本体。本轮按已证callsite补原字，不把extent当语义|

原件为 [CATALOG](../../../roms/CATALOG.md) 已认证的原厂 AP01 `1.0.2_0041`：主仓 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射 `file_offset=VA−0x9ffff000`。本轮只校长度和引用旧身份，不另重算摘要，不混0031/unsigned/SIM。

查重读取近期G19–G22、G11/G12与上述索引；精确`0xa009dfcc`报告搜索命中既有callee锚点/认领，没有该本体已验合同。相交G19/3仅条件callsite与S来源，既验范围直接继承；与F11、J08的对象/问题不相交。索引的`libuv`源路径家族候选不是精确SDK/版本/实例认证。

## 本轮复核或纠正

本轮没有推翻G21/G22的op2合同；需收紧“条件提交服务”的称呼：这只是上层按条件调用的未知服务，**原字没有给出本题路径已完成native提交的证据**。旧锚点本来就未认证提交成功，本轮不将新报告名当已有成功结论。

证据见本题 [verify.py](../../analysis/pogo-poll-ring-consume-g23-0041-20261024/verify.py) 与 [evidence.json](../../analysis/pogo-poll-ring-consume-g23-0041-20261024/evidence.json)。Capstone 5.0.7只作离线RV32/RVC解码；JAL和B型分支另按位核目标，厂商实例按现存只读私有规则核字段。没有新REA生产分析/Profile或Evidence ID；旧metadata各自原profile不重标，本轮证据身份是原件地址/原字、脚本和工具版本。

## 真正新增

### 入口门、counter重读与下层边界

`C=a1`、`S=a2`、`backend_fd=a0`是来自已验调用端的分析记号。只有`word(C+0x3c)!=−1`才直接从`0xa009dfe4`到`0xa009dffa`；相等分支以`(0xa01c39b8,0x4f4,0)`到`0xa0019672`。此callee的no-return/寄存器合同未恢复，不能把它返回之后的a0/a1/a2仍当入口值。

|必要原字地址|原序与字段事实|解释边界|
|---|---|---|
|`0xa009dffa..0xa009e008`|取`hp=word(C+0)`、`head=word(hp)`，再取`tp=word(C+4)`、`tail=word(tp)`；保存C，令`delta=tail−head`（RV32低word），相等跳`0xa009e042`|和G21上层masked-XOR不是同一个判断；本体比较完整word，不沿用上层mask|
|`0xa009e042..0xa009e048`|相等路径准备`a2=0,a1=0x4f5`，跳`0xa009dfee`重建路径串并调用`0xa0019672`|不是空环普通返回，不假设诊断返回后状态|
|`0xa009e00c..0xa009e024`|非相等路径保存原backend_fd到s3、S到s2；s6=0x26、s5=4；`0xa009e016→0xa00267c0`，向其返回地址写word0x26；`0xa009e01e`再调同服务，读其返回地址的word，等于4跳回`0xa009e016`|`0xa00267c0`作可写错误槽候选的名称只是继承的形状推断；不展开callee，不假设两次必为同一地址或无副作用|
|`0xa009e028..0xa009e040`|以`a0=0xa01c39d0`调用`0xa0134716`；随后仅当原s4即delta==−1才去`0xa009e04a`；否则以line0x500进入共同诊断入口|此处没有原生提交callsite；实际调用列表是错误槽候选和日志候选。不能跨未展开callee宣称全ROM没有native提交，也不能凭日志名称解释格式/返回|
|`0xa009e04a..0xa009e05c`|再次读取C+0/C+4指针和各自word值，重读后相等才到`0xa009e05e`，不相等以line0x502到共同诊断|这次读取在上面两服务/日志之后，不能用首次head/tail值替代；从已证正常非诊断路径如何满足该门仍未知|
|`0xa009e05e..0xa009e066`|以`(s0−0x30,S,16)`调`0xa000589c`；入口栈s0=sp+0x30，因此目的为本函数局部16B，源是原S基址|值复制在完成记录循环前只做一次；不能写成每次消费都从S按index读取，也不据此认证局部index的范围|

若将`0xa00267c0`视为稳定、无相关counter副作用的错误槽访问器，则非零delta进入段很像设置不支持错误的占位路径；这只是可解释形状的**推断**，不作为ROM缺陷、实现意图或实际执行事实。本题保持原字，无任何修补、异常输入或试运行。

### 另组counter、16B记录与局部副本的使用

以下是`0xa009e05e`已经到达且上述callee正常返回的**后段条件合同**，不宣称入口总会到达：

```c
// 静态分析表达，非原源码；全部word运算/地址为RV32。
copy16(local16, S);                   // 只复制S开头16B一次
for (;;) {
    consumer_p = load32(C + 0x14);
    producer_p = load32(C + 0x18);
    old = load32(consumer_p);
    end = load32(producer_p);
    if (old == end) return_a0_unchanged();
    store32(consumer_p, old + 1);     // 先于mask、record和result读取
    mask = load32(C + 0x1c);
    records = load32(C + 0x24);
    Q = records + ((old & mask) << 4);
    result = load32(Q + 8);
    if (result == 0) continue;
    low = load32(Q + 0);
    high = load32(Q + 4);
    tag = low & 3;
    index = low8(wexti_pair(low, high, 2));
    if (tag == 2) continue;
    if (tag != 1) diagnostic_boundary(line=0x51c);
    if (result != -17) diagnostic_boundary(line=0x51f);
    // 无诊断的该臂：tag==1且result==-17。
    opaque_a009e0e6(backend_fd, C, S, 3, high,
                    local16 + (index << 4));
}
```

`0xa009e070/072/074/076/078`核实另组counter使用C+0x14/+0x18，与入口C+0/+4分开，不凭相同“head/tail”名认成同一对象。`0xa009e090/094`先增加consumer；`0xa009e096/098`之后才读mask/base；`0xa009e09a..0xa009e0a0`形成stride16的Q并读Q+8。没有在此归还Q、S或环存储，也没有清Q字段；不能把consumer增加当成底层已完成/所有副本可复用的证明。

`0xa009e0a2`的result0跳循环头；非零才读low/high。`0xa009e0ac`原字`f70726de`（word`0xde2607f7`），字段`(opcode,f3,top7,rd,rs1,shift)=(0x77,0,0x6f,15,12,2)`匹配现有私有模型`ap01thead2.sinc:6658`的`wexti`：将寄存器对a2/a3组成64bit，逻辑右移2后取低32bit到a5；随后`0xa009e0b0`再AND0xff。因此index数值等于`(low>>2)&0xff`，但报告保留实际pair操作，不把未知编码改为NOP。该本地规则不等同独立厂商ISA认证，未执行模型。

`0xa009e0b4`tag2直接回循环头；`0xa009e0b8`tag1才到result门。其他tag经line0x51c跳共同诊断；result不等−17经line0x51f诊断。两者均不能假定返回继续普通处理。正常tag1/result−17臂`0xa009e0d0..0xa009e0e2`实际以`a0=s3,a1=s1,a2=s2,a3=3,a4=Q+4的word,a5=local16+(index<<4)`调用已知`0xa009e0e6`；不是op2，不能套G21。其callee的op3本体只保存新锚点，未展开。

完成循环相等时`0xa009e07c..0xa009e08e`只恢复保存寄存器/栈并返回，不写a0。循环中的op3返回也没有成功比较，直接再读counter。因此本函数没有已证的统一成功返回码；无op3调用时a0沿copy服务返回，有调用时沿最近op3返回，具体值仍依对应服务。S/counter/entry的分配、发布、释放及实际底层OS交付仍不是本题结论。

## 未闭精确边、实际验证与后继

已回答该本体的字段/门/重读/局部复制/完成消费/六参callsite及返回原序，但**从上层条件调用到后段普通完成循环的可达性仍未闭**。不能以线性字节越过诊断，也不能假定两次错误槽候选调用和日志不会修改相关状态；诊断是否返回、保留哪些寄存器未知。counter初始化/一致性、mask/容量、local16索引有效范围、S与entry的别名/对齐/寿命、实际native submit/完成及任何成功语义均未知。

本路实际只运行新写的静态原字检查器：**100个必要锚点PASS，含9个B型分支、5个JAL独立字段检查和1个既有模型厂商实例**；常规指令逐条Capstone匹配，无原指令/模型执行，无整函数伪代码、资源或源码导出。另做JSON解析、报告本地链接和diff检查；没有重跑G21/G22或历史技术脚本。旧metadata和现有模型都只读引用；作者自检不冒充独立接受。

有种子的后继建议仅为：在同G19/4挂非作者复核，先核本轮门/重读/consumer先增/局部copy/返回和可达性限定。若另追业务依赖，新增候选是`0xa009e0e2→0xa009e0e6(backend_fd,C,S,3,high,local16+(index<<4))`的**op3**消费与持有合同；必须管理窗口先查重登记后再读本体，不把此偶遇当扩范围授权。错误槽、日志、诊断及native服务本体均未接管。
