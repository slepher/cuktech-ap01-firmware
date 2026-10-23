# 0041 H15：底层时间 pair 表示与 offset 来源断边

`a002645a` 的正常输出表示已闭：只读一次 `62fc6c64` 的32位值，以无符号除/余1000生成粗 word和余数，再把余数乘1000000写入细 word，返回0。它没有底层callee。结合既有天气换算和本地候选，支持秒/纳秒pair及输入每单位1ms的解释；计数器实际写入节奏、来源和epoch仍未核。`62fc5c74/+4` 的真实ROM写入者没有留存种子，本轮按任务书有界停边。

基线 `6385a09`，独立树 `re0041-h15`、分支 `codex/re-0041-h15`。采用 reverse-engineer-anything 技能，只读主仓ROM/ignored证据与本地候选；没有打开或切换共享REA target、运行固件/模型/SIM/构建/历史时间回放、设备或网络。未创建下级agent，未修改主树、生产ROM、配置或分析器模型。仅写本报告及同名独占analysis目录；其他agent同时工作，未撤销其改动。结果待独立技术复核。

## 继承结论：已有出处 → 行为 → 局限 → 实际缺口

|已有出处|已有行为及证据局限|本轮处理|
|---|---|---|
|[H13](weather-clock-abi-h13-0041-20261024.md)、[H14](weather-clock-review-h14-0041-20261024.md)|ID0成功路径：`a002696a`调用下层，保存/清mstatus bit3后合并`62fc5c74/+4`，细word有符号上界检查后单次进位；天气两次signed32 DIV、既有UMAR64到a1:a0、URL `%lld` 接入已闭|全部继承，不重导、不重做天气正常算术或失败路径|
|`whole-rom-coverage-0041-20261023-round1.json` 的`a002645a`条目|inventory `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2`；extent `ev_2c7008f9ddabbba2c7d0f277da376c3b80417efa25d9f114fa0d6e3f4dddf067` 为`645a..648b`共50B；direct calls `ev_e2f3c4c8b2774c6ad186efd9a57adff5dcdc63a5c77cd3e04fd4740ffe57396f`为空；scope unresolved，无source/dossier|已有函数边界和无callee直接复用，只补正常输出必要原字节|
|`weather-dataflow-0041-20261023/rea-generic.evidence.json`|retained `ev_433271d8c713a3078b9057437981de5ce8bb010d85d6aa81cb5fe65faa329e99` 为天气helper，callee指出`a002696a`，不是底层或offset写者的dossier|不把helper的incoming caller误当offset writer，不重复导出|
|[wait-wrapper A03](wait-wrapper-a03-0041-20261023.md)、A04|另一ID1调用者及pair/绝对超时语境；来源接口当时仅类比|不重做等待算术；E16拥有ID1→uv缓存接入，本题不核其内部|
|H13已有complete/最终ZIP服务复用结果|天气UI和宿主替代，不能认证ROM source/epoch|继承，不重新解包/复制服务源码|
|旧`0041-20261013`、较晚`round3/evidence`、`reverse/raw`|本轮限定文本查询`a002645a\|62fc5c74\|62fc5c78\|62fc6c64`均无命中文件，详见静态结果|这只是这些留存目录/地址文本的负搜索；不代表ROM无writer，也不扩大到全ROM字段扫描|

实际缺口为下层输出的宽度/除余/单位表示及offset的有定位写入连接。前者得到原字节答案，后者无真实writer种子，保留断边。

## 本轮复核或纠正

H14所收紧的“单次有条件进位”继续有效，不能用本题底层余数范围去担保未知offset合并后的所有可能细word。ID0合并的两word是独立32位ADD，不能把它改写成64位纳秒加法。

本地候选根沿[A13](scheduler-source-a13-0041-20261023.md)/[A14](scheduler-source-review-a14-0041-20261023.md)继承：`Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/nuttx`，已有本地标签`nuttx-12.10.0`、HEAD `6fc5b3e9dc51dcda46d99519f72b7f2ec6db2e64`。本轮只读四个指定文件必要行，不新作版本/整库认证或远程访问。候选是参考语境，不能替代ROM字节或把SIM源身份外推ROM。

|候选精确源行|可支持的局部类比|不能外推的事项|
|---|---|---|
|`sched/clock/clock_systime_timespec.c:45–59,62–89`|名称/注释称返回timespec；非高精度/架构timer分支用`clock_ticks2time(ts,g_system_ticks)`，返回0|ROM具体宏配置、硬件timer、上电起点和counter写者没有据此被证明|
|`include/nuttx/clock.h:343–351`|先保存tick，`tv_sec=tick/TICK_PER_SEC`，去除整秒后乘`NSEC_PER_TICK`得`tv_nsec`；与ROM两word形状对应|ROM1000与1000000只能支持此候选在每秒1000 tick时的局部对应；没有读取/认证ROM配置|
|`sched/clock/clock_gettime.c:88–115`|MONOTONIC/BOOTTIME分支直取source，REALTIME分支锁内加base；符合两条分支的结构语境|候选这里为void `nxclock_gettime`，不能代替ROM返回状态/selector masking，不能正式命名ROM ID0/1|
|`sched/clock/clock_settime.c:73–85`|参考实现以请求时间减source bias写`g_basetime`|仅源码候选writer；没有ROM地址或调用者连接，不能宣称`62fc5c74`就是其已认证实例|

这些源行保存在[candidate-excerpts.json](../../analysis/clock-source-offset-h15-0041-20261024/candidate-excerpts.json)，不是全文件副本。

## 真正新增：a002645a正常输出

原件定位为主仓`roms/0041/ap01-1.0.2_0041.bin`，映射base `9ffff000`。必要窗口`a0026460..a002648b`保存在[static-result.json](../../analysis/clock-source-offset-h15-0041-20261024/static-result.json)。这是本轮新恢复的局部合同，不是重导整个时钟系统。

|地址 / 原字节|可观察行为|
|---|---|
|`6460:b777fc62`；`6464:83a747c6`|`lui a5,62fc7`；`lw a5,-39c(a5)`，有效地址`62fc6c64`；仅一次32位读取|
|`6468:1307803e`；`646c:b3d6e702`|a4=1000；`DIVU a3,a5,a4`，粗word为unsigned32除1000|
|`6470:b3f7e702`|`REMU a5,a5,a4`，细余数来自同一已加载值，未重读全局|
|`6474:37470f00`；`6478:13070724`|a4=`f4000+240=1000000`|
|`647c:14c1`；`647e:b387e702`；`6482:5cc1`|先写out+0，再`MUL a5,a5,a4`写out+4。余数0..999，乘积最大999000000，存32位不溢出|
|`6484:3244`；`6486:0145`；`6488:4101`；`648a:8280`|恢复s0、a0=0、归还16B栈帧、ret；没有底层调用或额外状态写回|

正常必要伪代码（非原源码）：

```c
int lower_pair(uint32_t *out /* a0, caller-owned 8B */) {
    uint32_t t = load_u32(0x62fc6c64); // 单次读取，unsigned算术
    uint32_t coarse = t / 1000u;
    uint32_t remainder = t % 1000u;
    out[0] = coarse;
    out[1] = remainder * 1000000u;
    return 0;
}
```

输出两word是数值pair，不是连续64位计数值；若按候选timespec解释即秒/纳秒，输入数值单位为毫秒。该单位解释有换算与继承天气消费者支持，但ROM并未在这里命名counter，无法单靠算式证明它以真实1ms节奏增加、不会回退或来自某硬件。计数器宽度为本函数读取的32位；不另推回绕/硬件时序政策。

buffer由调用者提供，本函数同步写入+0/+4，不分配heap、不保留指针、不转移所有权；下层没有callee。ID0 wrapper调用前已将a0指向自己的8B栈局部（H13/H14），再合并offset写给上层buffer。ID1到本函数的接入归E16，不在此重复。新增功能限于这条正常lower输出合同；新增ISA规则0、整库排除0。

## 未闭精确边与停止边界

`62fc5c74/+4` 的ROM写入函数/调用点、初始化值与后续设置来源仍未知。候选`clock_settime.c`只给出可检验的结构假设，没有把其writer绑定到ROM，不能据此从相邻入口猜测setter。限定留存查询未产生真实writer种子，因此按书停止，未做全ROM常量/字段扫描，也没有开展异常输入或时序验证。

`62fc6c64` 实际writer、节奏/计数起点、ROM精确来源版本、正式selector定义、epoch、校时策略、硬件timer身份继续未知。候选上电/REALTIME注释不被提升为ROM事实；没有把天气ID0和uv ID1 epoch等同。

单一后续闭包：只有当retained xref/命名合同提供实际ROM offset writer地址与调用点时，再核其输入pair→source bias→`62fc5c74/+4`保存的原序和宽度。当前不以无地址源码候选自动扩题。

## 实际静态验证

[verify.py](../../analysis/clock-source-offset-h15-0041-20261024/verify.py)通过：必要44B普通指令窗口完整解码、8处原字节锚点、DIVU/REMU/MUL字段、有效地址与1000000常数核验；仅读四个本地候选的限定源行；三处旧留存目录文本搜索无命中。没有运行ROM、ISA模型、时间输入回放或构建。`git diff --check`及报告相对链接检查通过。验证只支持上述局部正常合同，不宣布完整时钟来源或offset闭包完成。
