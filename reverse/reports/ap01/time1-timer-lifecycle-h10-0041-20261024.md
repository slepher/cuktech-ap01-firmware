# H10：type2/time1 timer 创建接入有界调查

2026-10-24；基线 `c41b360`，分支 `codex/re-0041-h10`。使用 reverse-engineer-anything 技能；只读0041原ROM及主仓旧材料，静态分析，无SIM/构建/历史回放/设备/网络；无共享可写REA target，无新REA Evidence ID。结果待独立技术复核。

**未闭合 ctx+0x78 timer 创建及正常 callback；新增timer功能0。** 本轮核实唯一已有构造候选 `a0198d3e(ctx+0x5c,page,page)` 的接入ABI及直接字段写入：该helper没有通过保存的入参对象写入 `+0x1c`（即ctx+0x78）。因此不得把这一调用、旧天气callback名字或SIM服务timer填作实际安装证据。此为限定排除，不声称ROM不存在timer或此前从未分析。

## 既有出处→实际缺口

|来源|已解释行为|局限与本轮处理|
|---|---|---|
|[H08](weather-type2-lifecycle-h08-0041-20261024.md)、[H09](weather-type2-review-h09-0041-20261024.md)|type2、136 B ctx、20 B wrapper；DELETE借ctx+78后删timer/free ctx/注销/free wrapper/脱挂|完全继承，不能外推实际创建；本轮不重导DELETE|
|`reverse/analysis/0041-20261013/0041-ghidra-pass3.txt` 2295–2494，尤其2483–2489|ctx[31]=2；a0198d3e(ctx+5c,page,page)；a00ac6f8使用ctx+54/+58/+5c/+68/+84；登记a00ab754|含custom0的大构造不是timer安装证明；仅核已知helper入口ABI及直接写字段|
|主仓 `reverse/rehost/weather-calendar-complete-0041.json` evidence[18]、time/weather摘要|a00ab754完整天气callback；温湿度、文字、arc显示已覆盖|该callback是同步天气发布消费者(data,page)，不是本轮timer callback种子；直接继承|
|主仓 `page-logic-evidence.json` records[3] normalized_result[99]/[147]；`asset-index.json` font_string_evidence[175]/[176]|`lv_ui_time1_update_wx_data_cb`名称|records[3].subject明确是0031，asset上下文亦带v0031路径；H08已指出地址差异。这些不是0041 timer对象/ABI证据，不追错误版本名称|
|主仓 `photo-evidence-round3.json` time_mini_cards及rea_records；`main-knob-0041-round2.json` records[1]；`detail-knob-0041-round2.json`|较晚round3 mini-card构造及正常导航留存|先按a0198d3e/a00ac6f8/ctx+78/[0x1e]查；未得到time1 ctx78实际writer或callback种子。导航中其他页的1s/30s timer不跨用|
|最终 `ap01-ui-0041-complete-source.zip` 只读文本成员 `tools/ap01/ap01-ui-pages.h` 560附近|time1的58px圆/日期及温湿度重建布局|模拟服务和重建源码不能认证原ROM timer；未解包、复制或执行|

检索只读主仓上述JSON、pass3、现有H报告及最终ZIP相关time/pages文本成员；未对全ROM timer/callback作扫描。未把局部未命中说成全历史缺失。上层主app teardown共同未知保持原状，不再搜索DELETE上层。

## 继承结论

`page+0x10 → wrapper{word type=2, ctx@+4}`；ctx分配0x88 B。旧天气登记尝试键为 `(a00ab754,page)`，返回未检查；a00ab754由page取wrapper/ctx。H08/H09已认证 `a00aba9c` 的原序：读取ctx+0x78 → 清25个离散word → a008ae58(timer) → a008ab8a(ctx) → a00b3abe(a00ab754,page) → a008ab8a(wrapper) → page+0x10=0。本轮不复核完整callback或清理，不套用type4的68 B或type19的116 B。

这里的timer名沿用既有a008ae58公共合同；DELETE的取值不足以证明安装完成、值非零或运行触发。先free ctx后注销是继承的原程序次序，不重排。

## 本轮复核或纠正

原件只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；沿用已认证0041身份和 `file_offset=VA-0x9ffff000`，不另建哈希账。[验证器](../../analysis/time1-timer-lifecycle-h10-0041-20261024/verify.py)及[局部证据](../../analysis/time1-timer-lifecycle-h10-0041-20261024/evidence.json)保存必要窗口和直接store原字节，未保存整helper导出。

`a005e192/e194` 原半字 `864e/85ce` 为a2/a1=s3(page)；e196 `05c90513` 为a0=s2(ctx)+0x5c；e19a写ctx+0x7c=2；e19e/e1a2 AUIPC/JALR实际目标a0198d3e。此点没有timer返回接收写ctx+78，返回a0后马上进入下一控件构造参数装载；不能把无消费的返回值命名timer。

helper入口 `a0198d48` 半字 `84aa` 保存入参a0为s1。静态顺序解码 `a0198d3e..a0199063` 共806 B/284条，无解码断点；除入口赋值与末尾恢复外，未见s1重赋值。仅保留6条直接经s1的写入：

|地址|原存储|换算到136 B ctx|
|---|---|---|
|a0198d7a|word a0→s1+0|ctx+5c|
|a0198f8a|word s2→s1+c|ctx+68|
|a0198fd0|word a0→s1+4|ctx+60|
|a0198fe8|word a0→s1+8|ctx+64|
|a0199020|word zero→s1+10|ctx+6c|
|a019904c|word a0→s1+28|ctx+84|

表中无s1+1c=ctx+78。a0198f8a/a0199020另用RV32 S格式位域核寄存器/宽度/偏移；入口与调用点用原半字、ADDI及AUIPC/JALR位域核。此必要窗口无custom0/unaff/extraout或厂商字依赖。Capstone 5.0.7用于静态解码；没有改变分析器模型。

限定：这只排除“该helper直接经保存的入参s1写ctx78”这一具体说法。没有对helper所有callee作跨过程别名证明，不排除间接别名写入、后续页激活初始化或其他路径；不能推出ctx78永远为零。helper正常构造多个子控件的完整业务不属本题，没有重做资源/分类。

```c
// 分析伪代码，仅表达已核接入；不是原厂源码。
Context136 *c = existing_type2_ctx;
SW(c+0x7c, 2);
a0198d3e(c+0x5c, page, page);  // 直接stores没有落到c+0x78
// 原构造继续创建控件并登记(a00ab754,page)，沿H08/H09。
// c+0x78实际writer、Timer(callback, period, userdata)仍未知。
// DELETE消费c+0x78的合同继承，不据此补造安装步骤。
```

## 真正新增

新增timer业务功能0；没有认证新的timer callback、创建周期、userdata或正常启停。增量是上列helper接入的局部原字节认证及一个受限排除结果，避免下一轮再次把ctx+5c控件构造当ctx78安装点。旧构造/天气显示/DELETE仍是旧覆盖，没有重复计数。

## 未闭精确边与必要验证

事实：构造helper入参是ctx+5c、page、page；该helper直接s1写的6个偏移；旧字符串来源为0031。推断：该helper是已有控件子结构构造，不能承担实际timer安装证明。未知：**0041 type2同一136 B ctx+78的实际writer→timer创建callback/周期/userdata→正常callback更新字段/业务→H08/H09 DELETE借用**；运行时实际触发及同页启停均未闭。共同上层teardown未知不另立搜索。

后续只有出现真实同ctx78 writer/callback种子才接着核其调用ABI与主要正常更新；不以全timer遍历或再次解天气callback填补。本轮按任务书“无真实callback种子有界交付”结束，并非完整timer生命周期验收。

实际验证：verify.py通过12项检查，284条有界helper指令覆盖、6条直接store；evidence.json可解析，报告相对链接存在，git diff --check通过。无ROM/生产/配置/模型/共享文件修改，无工具或审批阻塞。
