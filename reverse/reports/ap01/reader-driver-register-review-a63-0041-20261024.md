# A63：reader真实header到节点D保存桥的非作者复核

**限定接受A62在J08/5的注册桥，语义纠正0、新增业务0。** 正常路径实际把 `0x62fc9740` 作为a0交insert-head helper，返回N非零才跳过错误块，到 `0xa008e826/e82a` 将 `D=0x62fc974c` 按word保存到N+0。s1来自旧LUI的 `0x62fc9000` 高位常量，不是A60阶段的G值；两次helper正常保存s1是接受前提。

沿A21/A22的既验helper合同，**helper先接头发布N，caller随后才填N.word0=D**。本复核保留这个原序，不改成先填D后发布，不认证并发可见性/原子性、实际注册已发生、D槽/盘符或节点/D寿命。

2026-10-24；非作者 `/root/f12`，任务A63挂原认领 **J08/5**；固定基线 `bd457a6`，独占 `re0041-a63` / `codex/re-0041-a63`。A62作者 `/root/g23` 已交付停止，主仓[唯一管理记录](rolling-management-0041-20261023.md)已登记本轮复核。遵循最新 [reverse-design](reverse-design.md)、[材料规则](../../analysis/README.md)及REA技能，限定原字段/正常控制与必要旧端点。

只写本报告、[独立复核源码](../../analysis/reader-driver-register-review-a63-0041-20261024/review.py)、[必要合同](../../analysis/reader-driver-register-review-a63-0041-20261024/contract.json)；[证据JSON](../../analysis/reader-driver-register-review-a63-0041-20261024/evidence.json)本地原路径忽略保留。不跑A62/A60/A21或历史技术脚本，不执行目标/指令/模型、固件、SIM/QEMU、构建、回放、设备或外部服务；不读helper/slot目标/其他caller body、不展开源路径或整个fsdrv，不切换共享REA，不改生产/ROM/配置/模型/主树/共享表，不提交或推送，无下级agent。

## 继承结论

|已有出处|已解释行为及实际边界|本轮处理|
|---|---|---|
|[A56](reader-driver-selection-a56-0041-20261024.md)/[A57](reader-driver-selection-review-a57-0041-20261024.md)|reader用head槽0x62fc9744及stride槽0x62fc9740，N.word0为候选D；选择/ready/open已验|用真实header数值作两端，不重读144B选择或接口|
|[A60](reader-driver-global-init-a60-0041-20261024.md)/[A61最新独立复核](reader-driver-global-init-review-a61-0041-20261024.md)|A61现已限定接受初始化word4→0x62fc9740、word0→0x62fc9744的正常条件合同|**A62写作时“A60待A61”是历史状态。** 本复核引用最新限定验收，不重跑初始化脚本或把初始化值当运行恒定值|
|[A21](png-info-lifecycle-a21-0041-20261023.md)/[A22](png-info-review-a22-0041-20261023.md)|0xa008aec0(list*)正常返回已接头节点或NULL，更新head发生在caller填payload之前；PNG header是另一个0x62fc968c|只继承泛型helper与ABI，不重验helper或套PNG28B payload/业务字段到reader|
|[A62作者交付](reader-driver-register-gap-a62-0041-20261024.md)|实际header实参、成功返回门、N.word0=D连接；偶遇s2基址/槽写仍未知|本轮只复核注册差集；不沿s2/callback展开。source path和相同helper不是同D实例认证|

原件按 [CATALOG](../../../roms/CATALOG.md)：主仓 `roms/0041/ap01-1.0.2_0041.bin`，实查6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算机械摘要；映射 `file_offset=VA−0x9ffff000`，不套0031/unsigned/SIM。

必要旧端点来自主仓本地忽略 `reverse/analysis/png-info-lifecycle-a21-0041-20261023/instruction-evidence.json` 的0xa008e75e、0xa008e764两行；本轮原字独立核相同端点。旧initializer extent EID `ev_0a98ac5c6ce40886b07dc5c8869a8f6084d079f6348f1129e0c660555462062d`、directcall `ev_e6785d9ce3c5fd6458d9a903371b4aef0c06f3a5b4733b657bbc006d6cc4410b`仅为地址出处，不替代语义。没有新REA profile/Evidence ID，旧A21/A22/A60/A61各自来源保持不动。

## 本轮复核或纠正

独立检查器直接读原件 `[0xa008e75e,0xa008e7ec)`、`[0xa008e826,0xa008e82c)` 共 **148B**，主要为了确认正常前段的指令宽度/control和s1没有显式重定义。仅保留 **44B必要锚点**及前段地址/宽度检查点，不解释其余D槽写。**20项PASS**：普通指令由 **Capstone 5.0.7 / RV32+RVC** 解码，另独立核JAL、ADDI、C.BNEZ、C.SW字段；无UNKNOWN或厂商模型依赖。

|复核点|原字/独立控制与寄存器依据|接受边界|
|---|---|---|
|高位s1|0xa008e75e `b794fc62`，LUI s1,0x62fc9；s1=0x62fc9000|不是A60所用G=0x62fc957c，不同阶段不能沿名混用|
|D清零接口端|旧e764 a1=0x34；e768 a0=s1+0x74c；e76c独立JAL到0xa0080d8e|只继承接口/正常callee保存s1前提，不认证全部D布局或helper执行|
|正常s1连续性|从旧高位定义后到e7e6的连续指令均完整解码；无显式s1重定义/其他branch，只有e76c与e7e2两helper调用|依两callee正常返回和calleesaved s1约定；没有读helper来认证任意异常/副作用行为|
|真实header a0|e7d8 `3795fc62` LUI a0,0x62fc9；e7de `13050574` ADDI a0,a0,0x740；中间e7dc只是store，不改a0/s1|实际a0=**0x62fc9740**，数值绑定header，不是同helper推测|
|insert与N|e7e2 `efc0efed`的JAL独立解为0xa008aec0|N就是此实际list调用返回的a0；helper发布head合同继承A21/A22|
|成功跳过错误改写|e7e6 `21e1`独立C.BNEZ为reg=a0、target=0xa008e826；e7e8首条`b73426a0`会LUI s1,0xa0263，但只在本非零成功边跳过的块|N非零直接到D保存，不拼接失败诊断后继续成功。错误块其他指令/no-return均不读、不补猜|
|同D与word保存|e826 `9384c474` I-format=ADDI s1,s1,0x74c；e82a `04c1` C.SW字段base=a0、src=s1、offset0|正常成功臂D=**0x62fc974c**，写 **word(N+0)=D**，不是byte、复制driver或另一N|

无语义纠正；需要保留的精度是“高位常量s1→正常helper保存→成功边加0x74c”，不是无条件沿用任何阶段的s1。正常callee-saved前提不等于独立证明所有callee都成功/不会改相关内存。

局部表达（非原源码，仅N非零正常臂）：

```c
// s1=0x62fc9000，正常helper保存s1。
N = insert_head_a008aec0((void*)0x62fc9740);
if (N != 0) {                 // e7e6直接跳e826，避开错误块s1改写
    D = s1 + 0x74c;           // 0x62fc974c
    word(N) = D;              // helper已经发布N后才写D指针值
}
```

N来自helper管理的节点，D是明确全局地址；本caller只存D指针，不复制结构、不另retain/归还D或证明节点注销。发布与填D的原序也不证明并发一致快照或即时consumer观察。

## 真正新增

**新增业务0、语义纠正0、来源/ISA认证0、整库排除0。** 本轮提供A62同范围非作者证据并限定接受，不把复读旧端点、连续性检查或另存JSON计新恢复。A61初始化验收直接引用，不由本报告再次验收。

reader header与PNG/其他list即使共用泛型insert-helper，仍用各自真实a0区分；本题没有借相同字段偏移或文件路径认证POSIX实例。其他caller、D slots和源路径均没有本轮增量。

## 未闭精确边

仍未知D首byte/盘符、s2精确来源到D槽写基址的身份、实际callback槽及各ABI、source实例是否匹配、实际注册/服务执行、后续writer/替换/注销和N/D寿命、并发发布/可见性；默认五ROM照片mode0的旧结论不改变。初始化head0/stride4只限A61条件范围，不能当全部后续状态。

一个有种子的后继是 **0xa008e77a的s2+0x180写基址→已注册D=0x62fc974c身份桥**。管理窗口已经登记 **J08/6、A64，作者/root/g23**，本复核只注明移交，不重复派发/读取slot目标或扩大fsdrv；真实s2未证时不能直接把其后store命名为D字段。

实际检查包括20项原字段/目标/正常寄存器连续性检查、JSON解析、引用在本树或整合主树存在、空白/独占范围与`git diff --check`。报告/源码/合同未提交，生成JSON受忽略保留，复核者交付后停止。
