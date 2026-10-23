# H09：type2/time1 DELETE 增量独立复核

2026-10-24；基线 `07d8b0b`，独立树 `re0041-h09`、分支 `codex/re-0041-h09`。使用 reverse-engineer-anything 技能；只做0041 ROM静态复核。

**H08 的136 B ctx、20 B wrapper及 `a00aba9c` 清理实参/原序限定接受，无核心语义纠正，新增功能0。** 原序确为读取ctx+0x78、清25个word、删除timer、free(ctx)、以 `(a00ab754,page)` 注销、free(wrapper)、清page+0x10。上下文先free后注销是原程序行为，不能为安全修复调换。完整callback、分类和显示仍是继承结论；本次不把局部DELETE验收提升为完整天气生命周期。

## 已有成果→复核缺口

|既有出处|已经解释的行为|局限|本轮动作|
|---|---|---|---|
|[H08正式报告](weather-type2-lifecycle-h08-0041-20261024.md)及其evidence.json|type2构造尺寸、挂接、DELETE字段/实参和清理顺序|研究结果尚待独立复核|独立读取原ROM，以位域核关键ABI/所有25条SW及释放调用|
|主仓 `reverse/analysis/0041-20261013/0041-ghidra-pass3.txt` 2295–2302、2488–2494行|20 B wrapper、136 B ctx；登记a00ab754、type=2、挂接page、安装a00aba9c|大函数含custom0，不能以整段反编译直接认证全部ABI|读取这些旧行，继承登记/构造关系，仅核所需常量和保存槽|
|主仓 `reverse/rehost/weather-calendar-complete-0041.json` evidence[18]|a00ab754完整callback原指令、天气消费与分类显示|H08已核78条旧指令；原stdout止于a00aba9a，不含本DELETE|完整继承；不再重核78条、不重导callback、分类或资源|
|[H02](weather-lifecycle-review-h02-0041-20261023.md)、[E06](ctk-app-close-review-e06-0041-20261023.md)、[weather-dataflow](weather-dataflow-0041-20261023.md)|同步callback(data,page)、同双word键注销、a008ae58摘链/changed byte/free及a008ab8a归还适配|公共helper合同不自动认证本页参数|直接引用；仅核type2调用点参数和目标|
|H08所引最终SIM验收、matrix、最终ZIP UI文本成员|time1温湿度、tiny图标和归一化重建行为已有覆盖|SIM不是原ROM ABI/所有权/运行触发证据|继承覆盖，不运行、不解包、不重做|

这次检索由H08正式增量表收缩：先读其六组来源与局限，再核pass3具体行和H02/E06公共合同。没有把旧pending、当前未命中或旧反编译边界称为此前从未恢复；没有重新扫描全部天气或全部UI。

## 继承结论

1. 登记与挂接旧合同：`a005e1fc` 尝试 `a00b3a68(a00ab754,page)`，之后写wrapper.type=2、wrapper.ctx=ctx、page+0x10=wrapper，安装 `(page,a00aba9c,0x29,0)`。登记返回未检查，不保证必占到槽。
2. callback是 `a00ab754(data,page)`；page来自userdata，ctx来自page.wrapper.ctx。完整78条旧指令、温湿度/图标/arc/文字的宽度和消费语义、weather-complete evidence[18]分类显示全部继承。H09不将这些标为新增或独立再验。
3. `a008ae58(timer)` 的公共语义为摘链→置changed byte→free(timer)；`a008ab8a` 为既有归还适配。这里认证本页接入，不重新恢复公共实现或认证标准库来源。
4. type4/weather1的68 B ctx和type19详情的116 B ctx是其他对象，不能套入本页；type19最终context释放断边仍保留。

## 本轮复核或纠正

本轮[独立验证器](../../analysis/weather-type2-review-h09-0041-20261024/verify.py)没有导入或执行H08验证器，直接把原ROM作为数据读取；RV32 I/S/B/JAL及RVC LI/MV/LW由本轮位域提取核实，不以H08的Capstone文字作为新解码。必要锚点的VA、文件偏移、原字节、实际/期望字段保存在[review-evidence.json](../../analysis/weather-type2-review-h09-0041-20261024/review-evidence.json)。共55项检查，不复制整函数或旧78条callback。未打开REA会话、切换全局target或共享可写数据库，无新REA Evidence ID。

原件只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；沿用既有0041身份及映射 `offset=VA-0x9ffff000`，不新增机械哈希清单。

|H08具体主张|判定|独立锚点与边界|
|---|---|---|
|wrapper20 B，ctx136 B，type2挂接|接受|cfa4 `5145` 为C.LI a0,20；cfa6 JAL a008e362，cfaa保存到s7；da90 `13058008` 为ADDI a0,zero,136，da94同分配目标，da98保存到s2。e182 C.LI s5,2；e204/e208/e20c分别SW s5→s7+0、s2→s7+4、s7→s3+0x10。对象贯通关系另由既有pass3局部行支持；不重做整构造体。|
|DELETE由event取page再取wrapper/ctx|接受|ababa LW s2,4(a0)，ababe LW s3,16(s2)，abac2以s3==0到abb52；abac6 LW s1,4(s3)。page与wrapper、ctx为三个身份；没有在ctx读取与使用间新增非空门。|
|事件码归一后只收0x29|接受|aba9c C.LW读event+8；aba9e的C.LUI构造ffff8000，abaa0减1得ffff7fff，abaa2 C.AND；abaa4置0x29，abaa8不等到abb60的RET。mask不是截成低15位。|
|先借ctx+0x78，再清25个word|接受|abaca原半字 `5ca8`（小端字节a85c）解为C.LW a0,120(s1)。abacc..abb2c恰为25条SW zero,offset(s1)，不改a0，因此abb30继承该timer实参。|
|timer删除→ctxfree|接受|abb30 JAL a008ae58；abb34 C.MV a0,s1；abb36 JAL a008ab8a。不是free(wrapper)，timer来自ctx内借出的word。|
|同双word键注销|接受|abb3a LUI a0,a00ab，abb40 ADDI +754得到a00ab754；abb3e C.MV a1,s2（page），abb44 JAL a00b3abe。登记键沿用旧已留存合同，不能把ctx当userdata。|
|wrapperfree→清page+10|接受|abb48 C.MV a0,s3；abb4a JAL a008ab8a；abb4e SW zero,16(s2)。注销发生在ctxfree后、wrapperfree前，page本体没有在本窗口归还。|
|timer初始化、上层实际DELETE触发、完整callback/资源|未核或继承，不扩展|本页timer安装点与上层事件仍未核；旧callback与显示按上栏继承，H09不重新验收完整消费者。|

25个word清零的原序（十六进制字节偏移）为：

```
24,1c,00,0c,08,48,34,18,14,30,44,2c,4c,50,54,58,38,3c,40,04,10,5c,60,64,84
```

这是离散100 B写入，不是将136 B整个memset；+0x78不在清零集合内。清控件地址字段也不是调用子控件delete。上述必要窗口均可按标准RV32/RVC编码解释，不依赖custom0/unaff/extraout/no-return；没有新厂商字语义需要认证。

分析存储视图：`page+0x10→wrapper20{type32@0=2,ctx32@4,其余12 B未知}`；ctx分配136 B，+0x78在DELETE时提供timer参数。这个存储视图不是原厂结构体声明，timer业务名来自接入既有删除合同，不证明安装过程。

```c
// 按原序重建的分析伪代码，不是原源码；不承诺数值返回。
void type2_delete(Event *e) {
    if ((LW(e+8) & 0xffff7fffU) != 0x29) return;
    Page *p = LW(e+4);
    Wrapper *w = LW(p+0x10);
    if (!w) return;
    Context *c = LW(w+4);
    Timer *t = LW(c+0x78);
    clear_25_words_in_original_order(c);
    a008ae58(t);
    a008ab8a(c);
    a00b3abe(a00ab754,p);
    a008ab8a(w);
    SW(p+0x10,0);
}
```

page由registry作为借用userdata持有。正常构造之后，本DELETE在指定事件且wrapper非零时推进到“清字段→timer归还→ctx归还→尝试注销同键→wrapper归还→page脱挂”。不补ctx/timer NULL门，不为安全重排，不把这个局部状态转换说成运行时一定执行或全页资源完整释放。callback返回不应被解释为稳定成功状态。

## 真正新增

**新增功能0，H08核心语义纠正0。** 新增的是独立静态核验与限定验收记录。H08的“真正新增”是相对于旧材料的特定type2清理参数/顺序补证；H09不把复核再计为第二份功能恢复，也不修改H08或生产实现。

## 未闭精确边与验证

事实：本轮原字节、尺寸立即数、对象存储槽、25条word写、各call参数与调用顺序。推断/命名：time1业务身份沿H08字符串/旧UI证据，timer来自调用既有timer-delete合同。未核：ctx+0x78的实际安装点、timer callback/正常启停；上层正常动作到此对象DELETE事件；同步发布之外的调度/动态登记可达性和子资源内部生命周期。静态序列不证明运行交错，也不作缺陷结论。

唯一后续闭包建议仍为ctx+0x78的实际写入：先查旧type2构造留存与派生结构，只有未认证安装实参才核局部字节；不重做完整callback、分类、图标资源或全UI。上层DELETE由其他任务范围处理，不能拿type4普通滑动填补。

实际运行本轮verify.py通过：55项编码/实参/顺序检查、25个word清零、新增功能0；JSON可解析、报告相对链接存在、git diff --check通过。没有运行项目、SIM、构建、回放、固件、设备或网络；未改ROM、生产代码、配置、分析器模型、共享索引或他人文件。无工具/审批阻塞。
