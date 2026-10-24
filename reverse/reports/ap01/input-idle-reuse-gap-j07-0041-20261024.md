# J07：输入/idle 旧覆盖去重与 activity 消费精度候选

2026-10-24；基线 `a462ff5`；独占树/分支 `re0041-j07` / `codex/re-0041-j07`。**盘点新增功能0、新ROM读取0、新反编译0。** 最终complete已覆盖唤醒首事件消费、长按返回、ScreenOff/ScreenSave阈值；E05/E06已独立接受1000ms timer的注册/app userdata。只保留一条旧合同局部精度复核候选：主输入 `a00afd5c` 置 `62fc403a` → 周期callback既有尾段按次序清两个counter、重读activity并最终清该byte。不是新输入算法、屏保功能或首次恢复。

使用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。仅读已有JSON/报告/pass3/索引，不读ROM、开REA会话或反编译，不执行SIM、构建、回放、固件、输入实验、设备、外部服务或模型；不修改生产代码、ROM、配置/模型、他人或主树文件，无下级agent。只写本题独占报告/analysis。J05的transport/Pogo、J06的MiIO退出、M01/M02算法、已验L/K/D批次不接管。

## 继承结论：已有→行为→局限→精确缺口

|旧出处|已有正常行为|本题裁定|
|---|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、system/guide complete父级|SIM中首个唤醒事件消费、3秒长按返回、空闲/关屏期限、功率/时间/黑屏等已通过；guide hooks包含activity返回woke并consumeinput|继承SIM能力与旧ROM留存；不重跑、不把SIM通过等同原ROM所有输入/驱动恢复，不研究OTA/保护分支|
|`guide-complete-0041.json#/saver/idle`、`#/bounded_local_disassembly/saver_idle_gates_asm`和`saver_idle_branch_asm`|a00afb42 ScreenOff、a00afbec ScreenSave的旧门与60/600/1800、180/600/1800/禁用已解释；相邻activity/计数原汇编也已留存|时长/业务算法直接引用；仅剩下述字段/原序未见针对性独立接受，不将旧完整片段重计新恢复|
|[背光第二轮](buzzer-backlight-round2-0041-20261023.md:129)|a00a769a按`62fc4039`恢复背光/关屏保并返回是否消费唤醒|主体已覆盖，不再恢复同wrapper、PWM或其上层全部按键|
|旧`main-knob-0041-round2.json#/records/1`；system cached main；[H03](weather-page-close-h03-0041-20261023.md)/[H04](weather-page-close-review-h04-0041-20261023.md)|主/详情输入先标activity再唤醒、非零返回消费等已有；主caller完整body也早有|真实生产者可定位，不全GUI找全部writer；H04等已接受的详情门不重复|
|[E05](ctk-app-close-e05-0041-20261023.md)、[E06独立接受](ctk-app-close-review-e06-0041-20261023.md)|T1=`a008bc64(a00af262,1000,app)`，app借用作userdata；真实app的DELETE挂接/清理已验|timer注册/borrowed app不是新缺口；本题不接注册或销毁生命周期|
|[主host边界](multi-screen-app-host-0041.md)、[append验证](screen-host-append-validation-20261020.md)|a00af262按固定页面索引刷新，app+4c动画忙门已有，默认模型仍有未恢复片段|不是整个callback未分析；不重做全刷新/所有页面或外部host实现|
|[I03](saver-time2-lifetime-i03-0041-20261024.md)/[I04](saver-time2-lifetime-review-i04-0041-20261024.md)、G05/G06及L03-L06/K03-K06/D19-D22|Time2页/wrapper/ctx、显示事件/计时器接口、setter与局部UI/动画均已有范围限定接受|同对象/主题已验边界直接继承，不能因屏保/输入同词再次派发|

早期round2的剩余/unsupported不能覆盖父级complete的较晚结论。`guide-complete`的历史status保留“awaiting-parent-runtime-validation”，但最终application已记父级SIM验收；不能据旧status重开已验业务。反过来，最终SIM成功也不认证当前候选原字段精度。

## 本轮复核或纠正

本轮只核留存身份/地址文本，不作ROM原字节技术验收。已纠正初步候选的对象混同：`screen-host-append-20261020.json#/functions/4/assembly` 在 a00af280记 `timer+0c→s1`，而 idle尾段的s2在 a00af78a/af79a构造 `62fc402c` 全局基址。**s2不是timer的app userdata。** E05/E06已验timer注册，不应再次以“userdata→s2缺口”派发。此为本轮盘点定位纠正，不推翻旧合同或新增功能。

同一旧callback伪码已明确把activity与`62fcbcc4/62fcbcc8`两个计时器联系起来；旧汇编也保留两次读取/两次清counter/最后清byte。它仍带unreachable/extraout警告，不能把整大函数伪码当可信已验原字段模型。候选应收缩到这些普通指令与真实生产者，不展开相邻大callback控制逻辑。

## 真正新增：盘点功能0，唯一真实候选

|种子/载体/JSON pointer|既有定位|真正未闭与最小范围|
|---|---|---|
|主生产者：主仓`reverse/rehost/main-knob-0041-round2.json#/records/1/normalized_result/assembly`，Evidence `ev_daf583e6c481f2d7f53eb8443cd04003d53c22365147ac088957c1415a947da7`；system父级`#/cached_evidence/main_a00afc88`含同调用|a00afd52/56构造base62fc402c；afd5a/5c存byte1到base+0e=62fc403a；afd60调既有a00a769a|原生产者已留存。后继只稀疏核其基址/byte宽度和与消费字段身份，不重做醒门/整主键handler|
|消费：本仓`reverse/analysis/screen-host-append-20261020.json#/functions/4`，procedure a00af262，Evidence `ev_4cd9ffcadd54fe381d075066b194c8af6fb2cd7098d35012c9c14281446c9463`；`#/functions/4/assembly`及`pseudocode`|af78a/af79a得s2=62fc402c；afa78读s2+0e；afa7c/80得62fcbcc4，afa8c零分支去afb42；非零臂afaa8清该word。afab0重读s2+0e，afab4/b8得62fcbcc8，afabc零去afbec；非零臂afac0清word，afac4才清activity byte，afac8回共同尾声|未见本轮核过的较晚报告对这条**双counter清零、重读activity、最后消费byte**原字段顺序作针对性独立接受。最小后继为旧合同精度复核/必要纠正，新功能0；保留原顺序，不改成单counter/单读取/提前清flag|
|父级与定时定位：guide-complete `#/bounded_local_disassembly/saver_idle_gates_asm`、`saver_idle_branch_asm`；pass3:2831；whole-ROM exact extent|旧pass3已写1000ms创建；索引a00af262 extent Evidence `ev_85aaccb6976b29241a47959644bd7912f7c6ead13bdaddd7bf53fad0431bc7f9`确含afab0；E05/E06已验注册/持有|仅提供定位/继承，不把函数目录当语义，不重复timer注册、threshold或DELETE。后继不需整函数导出|

上述是已有文本中可复查的序列，**不是本轮独立读取ROM后确认的新行为**。两counter的期限算法沿guide继承；本题不判断真实经过秒数、物理旋钮去抖、所有输入writer或异步并发语义。新报告唯一增量是缩窄派发范围和纠正app/global别名，新增业务/ROM/算法/ISA规则/来源排除均为0。

候选排除相邻主题：全a00af262刷新/弹窗/安全/OTA分支、全输入回调或GPIO、所有屏保页面创建和ctx释放、已验L/K/D批次、G通用显示事件、timer生命周期、物理按键和实际设备效果。既有writer足够定位，不为凑题再扫全部writer。独立技术复核若发现这些普通门已经被其他可靠合同覆盖，应直接引用结束，仍新增0。

## 精确未闭与实际验证

本题完成既有证据去重，交管理者一条可派发精度复核种子。精确未闭只有上述生产者→同activity byte→两counter清零/byte消费原字段与目标的独立限定认证；不将本候选写成新正常控制器恢复。其他领域是否存在任务不由此候选判断，本题不自行接后继。

[reuse.py](../../analysis/input-idle-reuse-gap-j07-0041-20261024/reuse.py) 只用Python标准库读取旧JSON/报告/pass3/index：**29项定位/父级/旧锚点检查PASS**。检查结果见 [reuse-result.json](../../analysis/input-idle-reuse-gap-j07-0041-20261024/reuse-result.json)，含生产者/消费者pointer、Evidence ID、地址及后来I03/I04/G05/G06精确词项查询边界；无body/资源/源码复制，未读取原ROM。JSON、报告相对链接、diff检查通过。旧文命中/未命中不是全历史不存在证明，盘点自检不是原ROM技术验收。
