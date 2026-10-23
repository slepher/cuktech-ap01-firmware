# A42：照片旧 decoder 释放顺序独立复核

2026-10-24；基线 `d493236b8802ec310e9433e8761fb1eb40e2b822`，分支 `codex/re-0041-a42`。**限定接受 A41 的非空旧 O、memory mode0 正常 setter 替换合同；没有语义纠正，新增功能为 0。** 先保存旧 O，旧 source 失效完成后检查 O+0x10，mode0 直接归还整个 O，返回后依次清 owner+0x5c、owner+0x74，最后才分类/构造新源。采用 reverse-engineer-anything 技能，只静态读取主仓 ROM 与已留存证据，没有打开共享 REA target 或数据库。

## 继承结论：已有出处→行为→局限→实际缺口

|已有出处|行为及继承结论|局限与本轮处置|
|---|---|---|
|[A41](photo-decoder-destroy-a41-0041-20261024.md) 及其 analysis/evidence.json|旧 O 释放接入、mode byte 门与两个槽清除顺序已研究|本轮唯一缺口为该合同的独立原编码验收，不重导 setter|
|[A33](photo-source-abi-a33-0041-20261024.md)、[A35](photo-source-review-a35-0041-20261024.md)|新 source descriptor+0x10 data → W+0x0c；W mode byte 为0；新源分类和 constructor ABI 已验收|全继承；初始 mode0 不等于任意运行期 O 必然 mode0，不穷举写者|
|[A37](photo-decoder-owner-a37-0041-20261024.md)、[A39](photo-decoder-review-a39-0041-20261024.md)|O 单块分配 `0x4664+5N`、复制0x664字节W状态；O+0x0c保存借用ROM输入；+0x658/+0x65c/+0x660指入同块；owner+0x5c=O、+0x74为内部输出指针|已验收布局直接引用，不重导构造、reader、算法或资源；持有不等于已证最终页面销毁|
|[A29](image-cache-invalidation-a29-0041-20261024.md)、[A31](image-cache-invalidation-review-a31-0041-20261024.md)|`a00eaa50(owner)` → `a00890e8(old_source)` 的既有cache失效接入|不重新展开cache/getter，不将失效等同O析构|
|[C03](pogo-close-callback-c03-0041-20261023.md)、[C04](pogo-close-review-c04-0041-20261023.md)|`a008ab8a(ptr)`过滤NULL/哨兵，否则保持原ptr传至`a002e14e`|释放封装可靠合同直接引用，底层heap不在本轮接受范围|
|A41 引用主仓 `photo-evidence-round3.json#/rea_records/3`，`ev_e3db1fb1f6b8b75d3ba7fbf202ad701f4cd3b8eb42987c05789f1e2626527941`；main-knob round2/system complete；A37所引weather complete/page-logic/最终ZIP|旧caller、reader/constructor片段、照片业务及替代实现已有|沿用出处和证据局限，不重复有界检索或复制body；旧custom0/截断反编译不能代替ABI；SIM/照片替代不证明ROM释放|

原字节、旧反编译限制、SIM/照片替代、未检到的精确边分别保留。主体已覆盖，本轮只补独立接受记录；未重新查五资源、整ROM引用或ZIP成员，不把旧检索未命中解释为从未分析。

## 本轮复核或纠正：逐项接受/未核

|A41主张|处置|必要独立校核与接受边界|
|---|---|---|
|入口保存owner+0x5c旧O，owner和新source分存寄存器|接受|`a00ed802` `0329c505`独立拆为LW s2,0x5c(a0)；`806` C.MV s1,a0；`808` C.MV s3,a1。对象身份不是getter返回source，也不是owner+0x74|
|旧O非空才失效和清槽|接受|`80a` BEQ s2,zero精确到`a00ed830`。空路径跳过整段，包括两个清槽；不得表述为setter无条件清零|
|失效先于O析构|接受直接接入，callee继承|`80e/812`的JAL rd=ra分别至`a00eaa50/a00890e8`；owner仍为getter a0，getter返回a0接入失效调用。其后才是mode读和free|
|O+0x10是整byte零门|接受|`816` `83470901`为LBU a5,0x10(s2)，不是LW或bit掩码；`81a` C.BEQZ a5准确到`822`，跳过`81c/81e`|
|非零mode另调`a01b2e3a`|仅接受目标与实参，内部未核|`81c` a0=s2；`81e` JAL目标核实。没有把callee补成ROM输入归还，也不认证文件模式内部行为|
|mode0直接free入口保存的O|接受|`822` `4a85`为C.MV a0,s2，`824` `efd069b6`直接JAL `a008ab8a`。mode0整段没有把O+0x0c、O内部区或owner+0x74装入归还实参|
|free返回后先清+0x5c再清+0x74|接受|`828` `23ae0404`与`82c` `23aa0406`独立S型拆解均SW zero，以s1为基，偏移依次0x5c/0x74，均32位。清派生引用不是第二次free|
|然后才新源分类/构造|接受连接，构造全继承|`830` C.MV a0,s3，`832` JAL至`a00dd454`，位于两次清槽之后；其余分类/成功构造及返回O保存按A33/A35/A37/A39继承。不宣称新构造成功，也不虚构失败恢复旧O|
|借用ROM输入不free，内部派生区不独立free|接受本正常mode0路径的所有权解释|直接free实参只有O；结合已接受单块布局，内部区随该根分配归还。不是扫描所有mode/所有生命周期所得的全局否定结论|
|正常页面DELETE触发、底层heap、运行期显示/回收|未核|本轮没有这些执行/静态入口证据，继续保留未知|

必要分析伪代码，非原源码，不定义setter业务返回类型：

```c
old = load32(owner + 0x5c); // 保存在s2，owner在s1，新source在s3
if (old != 0) {
    a00890e8(a00eaa50(owner));
    if (load_u8(old + 0x10) != 0)
        a01b2e3a(old);     // 内部未核；memory mode0跳过
    a008ab8a(old);
    store32(owner + 0x5c, 0);
    store32(owner + 0x74, 0);
}
classify_new_source(source); // a00dd454，之后构造按既有合同
```

业务含义限于正常替换：原程序先撤销旧源cache，再归还旧状态/内部输出分配，撤销owner两个持有槽，才处理新源。ROM输入仍是借用数据。没有将原序调整为先清槽或先成功构造新O；不讨论或验证异常并发/缺陷。

## 真正新增

新增功能、资源、算法、库来源认证及开源排除均为 **0**。只新增A41的限定独立验收与[review-evidence.json](../../analysis/photo-destroy-review-a42-0041-20261024/review-evidence.json)。没有语义纠正。指令实参与原序为事实；单块内部区随O归还是结合A37/A39布局与C03/C04封装的所有权推断，未观察heap实际复用。

## 未闭精确边、实际验证与后续闭包

非零mode `a01b2e3a(old)`内部资源处理、照片对象最终DELETE如何接入析构、底层allocator实现和运行期实际回收仍未知。格式/库版本、全部mode写者及全部失败臂也未认证。A39当时的正常替换/+0x74撤销未知由A41研究与本次限定接受收窄，不能外推为完整页面生命周期闭合。

唯一后续闭包建议仍是先复用旧控件class/DELETE留存，从已安装的具体照片对象析构入口追到owner+0x5c旧值归还及+0x74撤销；没有实际入口种子则有界报告，不扩全部控件销毁。

[verify.py](../../analysis/photo-destroy-review-a42-0041-20261024/verify.py)仅Python标准库，按继承ROM映射`offset=VA-0x9ffff000`稀疏读取`a00ed802..a00ed835`的必要指令，独立拆RV32 I/S/B/J及C.MV/C.BEQZ位域，**16项检查PASS，14个A41原字节锚点一致**。未导入A41/helper解码器，未运行其写文件脚本，未重复保存整函数；新增分类入口两锚点仅用于核原序。JSON可解析、报告本地链接与`git diff --check`通过。无固件执行、SIM、构建、历史回放、设备、网络、资源解码或模型修改；只写本题独占report/analysis。
