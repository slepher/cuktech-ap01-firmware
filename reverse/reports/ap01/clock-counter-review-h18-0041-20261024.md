# H18：counter writer 有界定位的独立复核

2026-10-24；基线 `ed4735b`，分支 `codex/re-0041-h18`。**限定接受 H17：指定留存查询和所选317条record没有提供 `62fc6c64` 的可靠ROM writer种子；四条目标引用是READ，不能把值流的output.location当作真实存储。** 没有语义纠正，新增ROM功能0。结论始终是“这个证据边界内未得到writer”，不表示原程序不存在writer，也不表示已恢复完整时钟来源。

使用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，复用已有Evidence，不打开/切换共享REA target。仅写本题独占产物；未执行固件、SIM、构建、回放、设备或外网，未修改生产ROM、配置、模型或共享文件，未创建下级agent。

## 继承结论：已有→行为→局限→精确复核缺口

|已有出处|已解释行为及局限|本轮处理|
|---|---|---|
|[H15](clock-source-offset-h15-0041-20261024.md)、[H16](clock-source-review-h16-0041-20261024.md)|`a002645a(out8)`单次读取32位counter，unsigned除余1000，余数乘1000000，顺序写两word返回0。候选只支持数值表示及条件性单位解释，不证明节奏/起点/epoch|可靠合同直接继承；未重读其函数或重做上层offset/selector消费者|
|[H17](clock-counter-writer-h17-0041-20261024.md)、[collect.py](../../analysis/clock-counter-writer-h17-0041-20261024/collect.py)、[review-result.json](../../analysis/clock-counter-writer-h17-0041-20261024/review-result.json)|限定目录的名称/文本查询没有新writer；四个文件均为a00992d2；upper bundle四READ；候选位置在clock_initialize.c|只审查询边界与解释强度，核317 records及四个已知命中文件；不重跑目录查询、文件名清单、全ROM或IRQ搜索|
|H17 [candidate-excerpts.json](../../analysis/clock-counter-writer-h17-0041-20261024/candidate-excerpts.json)|候选g_system_ticks初始化及条件clock_timer atomic加1；未绑定ROM|重读三个固定路径及已有42行相等性，不复制源码、不新增版本认证，不把候选函数当ROM writer|
|H13/H14、H15/H16引用的旧complete/最终ZIP/SIM边界|上层正常ABI与替代服务已有；候选源代码/宿主时间不能替代ROM保存指令证据|全继承，不重新查ZIP、不恢复服务、不搜索62fc5c74 offset writer|

本题只回答H17的无种子交付是否证据充分、是否把未命中或候选夸大；不承担寻找新writer。

## 本轮复核或纠正

|项目|独立检查与结果|接受范围|
|---|---|---|
|有界文本/文件名查询|审H17脚本及结果：三个根为主仓`evidence/rea-0041-20261017/evidence`、`round3/evidence`、`reverse/rehost`；文本query为counter地址及四个候选名称，限制`*.json`并排除`*.evidence.json`；完整bundle另行选择。filename查询只筛source-xref/global-ref/globalref形名|接受这是有边界的留存检索。本文不重新枚举根目录，不独立声称当前目录全体无其它artifact；文件名未命中不表示从未产生全局引用，排除的其它bundle也不能视为全部检查|
|所选complete的317条筛选|独立读主仓`upper-complete.evidence.json`，仅对各record.normalized_result筛与H17相同五个词；317条中仍仅index108命中|接受选定bundle的命中结果，不等于检查全ROM或所有历史record。Evidence=`ev_4d6c9f986061ce8306d891bf4fe062d0411c134c2aeb388cd1253c071e04a722`，参数procedure=a00992d2|
|四个单文件命中身份|直接读已知`final-seeded-roots-135.json`、`root-collection-044.json`、`upper-final-collection-020.json`、`v2-all-roots-240.json`的structuredContent；四者均procedure=a00992d2|接受四份采集同一读者，并非四个writer。不重新执行root文字搜索；各Evidence ID索引见本轮review-result|
|四条reference性质|index108的目标xref为a00993a2/a00993ca/a0099412/a009948a→62fc6c64；逐项`kind.type=READ,read=true,write=false`，与H17保存项一致|接受这些是READ引用，不能以它们作为WRITE种子。Reference Manager记录不覆盖所有computed地址或未留存代码|
|必要原字节确认|仅对上述四个PC各读取4B，分别为`83ac49c6/83a749c6/03ad49c6/83a749c6`；独立I字段为opcode=3、funct3=2、rs1=s3、imm=-0x39c，rd为s9/a5/s10/a5|四条均LW，不是SW。有效地址身份沿xref记录；本轮未追s3或重导502B函数，不声明整个函数所有可能间接写行为已穷尽|
|native_value_flow解释|核index108 operations[1]/[11]：分别在a00992fa/a009930c，opcode=INDIRECT、is_dead=true，output.location虽为62fc6c64|具体样例支持H17的审慎解释：值流输出字段本身不是原ISA的STORE事实。没有将这些dead元数据推成writer、也未把全部值流视为可靠原源码|
|候选实际位置|三个固定路径状态与H17一致：clock_timer.c及clock_systimer.c不存在，clock_initialize.c存在；已有42行逐行相同|接受仅为此本地树的路径事实。候选定义中的INITIAL_SYSTEM_TIMER_TICKS与条件atomic加1没有ROM地址/调用点绑定；文件不存在也不否定ROM存在同类函数|

H17的查询regex名称包括`clock_initialize`；报告按前四项查询再追加位置名称叙述，与最终脚本的合并query不矛盾。其“候选位置纠偏”只纠正检索预期路径，不纠正H15/H16已验收的ROM读者合同。

## 真正新增

新增ROM功能0、writer/increment/reset/周期合同0、来源版本认证及开源排除0。独立补充仅16B的四条LW复核和两个值流样例的性质索引；没有新函数、算法、伪代码、结构体、计数状态机或所有权合同。H17没有实际writer种子，故不存在可在本轮认证的writer参数/返回、存储次序或驱动调用连接。

本地候选`clock_initialize.c:52–55`的条件volatile初始化、`:399–411`的非TICKLESS/ALARM_ARCH/TIMER_ARCH条件函数及TIME64/普通atomic加1仅可作为后续来源假设；`:377–383`的另一累加语境也不能补成ROM校时或重置策略。H17没有越过此边界。

## 未闭精确边与实际验证

真实ROM writer入口/保存指令、正常increment/reset、驱动调用、更新节奏/计数起点/epoch、硬件timer及精确来源全部继续未知；没有把数值单位对应升级为实际每1ms递增，也没有把“没有可靠种子”升级成“不存在writer”。offset writer未知直接继承，本轮完全不搜索它。

[review.py](../../analysis/clock-counter-review-h18-0041-20261024/review.py) 实际通过：所选317 records一命中、四个已知文件的procedure、四READ/nonWRITE一致、16B独立LW位域、两个INDIRECT样例、三个候选路径及42行相等；[review-result.json](../../analysis/clock-counter-review-h18-0041-20261024/review-result.json)仅保存索引/判定/稀疏字节，不复制dossier或第二份源码。WSL沿已授权固定本地只读范围require_escalated读取，未运行SIM或修改参考树；本轮未重复触发普通WSL拒绝。JSON、报告链接及`git diff --check`通过。

单一后续闭包仍是先获得针对62fc6c64的真实WRITE xref或直接将ROM函数绑定clock_timer的命名/来源证据，再只核正常保存及直接调度调用；当前无种子时应停止，不派无地址的全IRQ/全ROM重复搜索。H18在上述范围独立接受H17，不能据此宣布时钟模块完成。
