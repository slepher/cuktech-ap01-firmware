# H08：type2/time1 天气 callback 复用及 DELETE 所有权增量

2026-10-24，基线 `bccdd65`，分支 `codex/re-0041-h08`。使用 reverse-engineer-anything 技能，仅静态读取原 ROM 与保留材料；不运行 SIM、构建、回放或归档脚本，不改生产代码、ROM、配置、分析器或共享索引。结果待独立技术复核。

结论：登记键 `(a00ab754,page)`、type2、context挂接、DELETE `a00aba9c` 以及 callback 的原指令均是旧成果。本轮只补该对象的清理参数身份和原顺序：借出 `ctx+0x78` → 清25个word → `a008ae58(timer)` → `free(ctx)` → 注销原双word键 → `free(wrapper)` → `page+0x10=0`。该页是 time1 天气消费者，ctx **136 B**、wrapper **20 B**；不得套用 type4/weather1 的68 B或type19详情的116 B释放结论。

## 已有成果→实际缺口

|既有出处|已经解释的行为|证据局限|本轮增量|
|---|---|---|---|
|主仓 `reverse/analysis/0041-20261013/0041-ghidra-pass3.txt` 2295–2302、2488–2494行|page/20 B wrapper/136 B ctx；a00ac6f8调用、登记a00ab754、type2、挂接、安装a00aba9c|旧大函数含custom0；不按整个反编译推断ABI或清理|仅核分配常量、成功登记/挂接窗口、对象别名；不计首次发现|
|主仓 `reverse/rehost/weather-calendar-complete-0041.json` evidence[18]，address=a00ab754，工具为GNU objdump|完整callback a00ab754..a00ab833，带原指令；当前温度/湿度/图标/arc等消费已经留存|stdout还包含相邻函数，但止于a00aba9a，未含本题a00aba9c DELETE；不能将相邻其他对象清理套入|78条callback旧指令与当前原件一致，仅为旧结论复核；只留必要ABI片段|
|同complete的 time/weather；最终 application-rehost-complete-0041-20261017.md、application-function-matrix-0041.json；factory-reference-map-0041-20261020.md|SIM时间页天气状态及tiny图标、归一化已实现，父级passed-in-sim覆盖旧pending口径|证明重建行为，不能证明原ROM ABI/所有权/运行时触发|不重做分类、文字、图标资源；无SIM功能新增|
|page-logic-evidence.json records[3] normalized_result[99]/[147]及asset-index.json font_string_evidence[175]/[176]|留存time1天气更新名称字符串|地址a0294a0c/a02963e8等不是本轮当前代码中的a037be30；字符串不能独立认证本题版本/对象|仅保留检索出处，不混作当前指令ABI证明|
|最终ZIP成员 `tools/ap01/ap01-ui-pages.h` 第560行附近及 time model|time1 UI构造/温湿度显示的重建合同|模拟服务和重建控件生命周期；未提供ROM DELETE原序|只读成员，无全量解包/复制/执行|
|[weather-dataflow](weather-dataflow-0041-20261023.md)、[H02](weather-lifecycle-review-h02-0041-20261023.md)、[E06](ctk-app-close-review-e06-0041-20261023.md)|同步callback(data,userdata)、首个同双word键注销、a008ae58摘链/changed byte/free、a008ab8a归还适配|公共合同不能自动等同本页实际实参|直接继承，只核本页接入点；不重复导出公共helper|

检索覆盖主仓reverse/rehost、reverse/reports/ap01、tooling、pass3及ZIP文本成员，以精确地址和time1 callback字符串查找；同时核近期天气A15–A20、H01–H07职责。当前检索未见本DELETE清理合同独立认证，不据此声称此前从未分析。旧a00ab754入口并非A15 callback a00ab6b0；A15窗口的结束地址a00ab754不能算其已恢复本函数。

## 继承的旧结论

`a00b3be6` 同步分发 `callback(data,userdata)`，userdata为登记page，不消费callback返回。本页正常登记 `a005e1f2..e1fc` 实参为 `(a00ab754,s3=page)`；调用后才写 `wrapper.type=2`、`wrapper.ctx=s2`、`page+0x10=wrapper`，接着安装 `(page,a00aba9c,0x29,0)`。登记返回未检查，称“登记尝试”，不能保证插槽必然成功。

旧callback通过 `LW(page+0x10)→LW(wrapper+4)` 访问ctx；LH(data+8/+10/+12)为有符号16位，LHU(data+26)为无符号16位，LW(data+28)为32位；其条件/arc/文本/tiny消费者依旧evidence[18]，不再重新计恢复。不重解a00a6998/a00a6d34/a0198946等已有业务语义。

## 本轮复核或纠正

原件只读：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；继承已认证身份，映射 `offset=VA-0x9ffff000`，不另建哈希账。局部静态[verify.py](../../analysis/weather-type2-lifecycle-h08-0041-20261024/verify.py)与[evidence.json](../../analysis/weather-type2-lifecycle-h08-0041-20261024/evidence.json)保存6个必要窗口/370 B/113条指令及61项编码检查；另对旧callback78条GNU原指令逐条匹配ROM，但不重导该callback。Capstone 5.0.7仅解原字节；JAL、LW/SW、LH/LHU、分支、常量和调用组合另按编码核对。无新REA Evidence ID、无共享可写会话。

`a005cf9a..cfb8`：page创建返回保存s3；wrapper零填充分配0x14返回s7。`a005da90..dace`：ctx零填充分配0x88返回s2；失败臂仅引用原序class walker(page)后free(wrapper)，不擅自称完整公共对象删除。s5=2在a005e182，e204/e208/e20c三次word store确认该wrapper/context/page关系。

callback首条 `BEQ a1,zero,a00ab832` 是page空直接返回，不能把a1误作天气数据；其后先读page.wrapper再改写a1为data.low。旧反编译custom0出现在其他构造控件参数处，不用于本合同；本轮所需ABI/cleanup窗口没有依赖custom0/unaff/extraout/no-return推断。所有原字节复核均不算新增业务恢复。

## 本轮真正新增

`a00aba9c(event)` 按 `LW(event+8)&0xffff7fff == 0x29` 进入，其他码直接返回；未静态声称实际收到事件。进入后 `page=LW(event+4)`，`wrapper=LW(page+0x10)`；wrapper为零返回。否则 `ctx=LW(wrapper+4)`，本窗口没有ctx非空保护。

`a00abaca` **先**借 `LW(ctx+0x78)` 为a0，再按以下word偏移原序清零（均非控件delete调用）：

```
24,1c,00,0c,08,48,34,18,14,30,44,2c,4c,50,54,58,38,3c,40,04,10,5c,60,64,84
```

`a00abb30` 将保存的该a0传入 `a008ae58`；依E06公共合同，实参为timer，摘链→changed byte→free(timer)。此处未见timer非空分支，不补造保护，也不据此推断ctx+0x78何时初始化。然后：

```c
// 分析伪代码，RV32存储视图；不是原源码。
void type2_delete(Event *e) {
    if ((LW(e+8) & 0xffff7fffU) != 0x29) return;
    Page *p = LW(e+4);
    Wrapper *w = LW(p+0x10);
    if (!w) return;
    Context *c = LW(w+4);
    Timer *t = LW(c+0x78);            // 在清零之前读取
    clear_25_words_in_listed_order(c);
    a008ae58(t);                     // a00abb30
    a008ab8a(c);                     // a00abb34/36
    a00b3abe(a00ab754,p);            // a00abb3a..44，完全相同键
    a008ab8a(w);                     // a00abb48/4a
    SW(p+0x10,0);                    // a00abb4e
}
```

ctx+0x78和另外未列偏移不在此清零集合中；不能把“25个word”说成整个136 B都清零，也不能把零写入等同归还子控件。ctx先free、后注销，严格保留原次序，不能改写成先注销以显得更安全。wrapper余12 B的业务含义不认证；释放page本体由外层对象删除合同承担，此callback本身没有free(page)。这项增量是特定type2清理连接，不是新增天气分类/显示功能，也不是原ROM全部天气生命周期完成。

## 仍未闭合的精确边

1. ctx+0x78的实际timer安装点、callback和正常启停仍未认证。只恢复其在本DELETE接入已知timer-delete合同；a0198d3e(ctx+0x5c,page,page)等旧构造调用不能直接推断为该timer初始化。
2. 正常上层动作→此type2对象DELETE事件未闭；H07只覆盖type4/weather1普通主浏览切出，E10另追主app根teardown，不跨页套用。
3. 同步发布之外是否存在其他调度、重入或动态更换登记数据，不由本限定窗口保证。ctx先free后注销的程序原序不证明所有运行时交错。

下一精确闭包可沿旧type2构造留存定位ctx+0x78实际写入；先查现存原证据/派生结构，只有未认证安装参数再读局部字节。不重做callback、分类器、资源或全UI初始化。

验证：脚本通过；JSON可解析、报告相对链接存在、git diff --check通过。上述为静态验证，未运行项目、SIM或固件。
