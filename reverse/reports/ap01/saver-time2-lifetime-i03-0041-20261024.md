# I03：屏保Time2/type2f生命周期的既有覆盖与责任边界

2026-10-24；基线 `472f076`；独占树/分支 `re0041-i03` / `codex/re-0041-i03`。**本题主体已有覆盖，收缩交付：旧guide完整留有Time2的page、wrapper20、ctx40、天气登记和DELETE安装；旧weather-calendar evidence[22]已留DELETE清ctx字段→天气同键注销→free(wrapper)→清page+10原序。新增ROM功能0，无新函数/窗口导出。** ctx40最终归还仍未证，不能把wrapper20或屏保root的8B状态归还当成free(ctx40)，也不作缺陷结论。

使用reverse-engineer-anything skill，仅读主仓原ROM/历史证据与ZIP成员，不打开、共享或切换REA target/database。未执行固件、SIM、构建、模型、历史回放、设备或外网；不创建下级agent、不改共享/主树、生产ROM、配置或模型。下面是机器合同的分析视图，非原源码或完整类型声明。

## 继承结论：已有出处→行为→局限→精确缺口

|已有出处|已有行为/证据范围|本轮处置与精确缺口|
|---|---|---|
|主仓 `reverse/rehost/guide-complete-0041.json#/saver`，`#/bounded_local_disassembly/saver_window_asm`、`saver_time_creator_asm`|mode2创建type0x2f Time2，随机两GIF、两种活动布局；creator及各挂接原objdump已在父complete|显示/分类/活动setter全继承；不把旧remaining当新缺失。只衔接page/wrapper/ctx/DELETE身份|
|[总信息消费者](ui-total-consumers-0041-20261023.md)，Evidence `ev_cffa17d3476afc7dff436d5c3681efe88c2f448f51d542b45398ee7a45bc2dd5`；[主题后续](theme-total-state-0041-20261023.md)及后续theme-online/window-history|a00ac54e、ctx+24严格0/1、功率除10/格式/布局、后续主题状态已恢复|全部继承，不复做callback/主题业务，不能按较早报告“第三消费者未展开”重开题|
|[A15](weather-subscriber-a15-0041-20261023.md)、[A16](weather-subscriber-review-a16-0041-20261023.md)、A17/A18、A19/A20|a00a7fc2尝试登记(a00ab6b0,page)，登记后才挂type2f/context；callback借用天气和page，range/temp/icon消费已独立核|同一Time2已有明确callback身份，不当成本题首次发现；实际插槽成功/运行存活不因此证明|
|主仓 `weather-calendar-complete-0041.json#/evidence/22`，address=`A00A4DF8`，tool=`local GNU objdump, bounded offline ROM window`|同一a00a4f82和屏保root a00a4edc完整旧原指令已保留|本地行比对与少量字段检查即可解释清理；不重导函数，不伪造新REA Evidence ID|
|[UiIFace生命周期](uiiface-lifecycle-0041-20261023.md)、[天气数据流](weather-dataflow-0041-20261023.md)|控制订阅a01b29a0/a01b2966与天气五槽a00b3a68/a00b3abe有不同键/责任；控制注销只摘链不证节点回收，天气注销清首个双word匹配|可靠接口继承，仅核本对象传入键；天气page与控制root不可混同|
|system-complete `#/native_page_state_ledger/47`；旧page-logic、较晚round3、pass3、最终ZIP|system父complete已把0x2f映射Time2；page-logic早期字符串/后续旧阶段和SIM替代来源有界筛选|SIM实现不能认证ROM所有权；筛选记录见verification.json。无命中不表示所有历史从未分析|

旧证据均从主仓 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware` 只读；JSON路径保留上表指针，未复制原body。最终ZIP相关实现实际为 `tools/ap01/ap01-ui-guide.h`，guide-complete的implementation已指向它；页面头文件不是此屏保替代实现的主要成员。不解包或运行ZIP。

## 本轮复核或纠正：旧覆盖的必要接线

|对象/阶段|旧指令定位与分析合同|范围/纠正|
|---|---|---|
|屏保父root R及状态S8|guide旧a00a78d8调用a00b2f6c，返回s3=R；78de/78e0申请8B、保存s7=S8；79ee写R+10=S8。79c4写R+3c=10这个窗口kind|这是父root自己的8B状态，与子页metadata的type32不在同一命名空间；不当成Time2 ctx|
|同Time2页P、M20、C40|mode2旧7d42/7d44进入分支，7d48/7d4a以R创建P，保存s1；7d52/7d54申请20B到s9=M；7d70/7d74申请40B到s2=C。分配零化接口沿UiIFace已有合同，失败臂保持旧诊断/清理，不改为新恢复策略|三对象不同；不能套type2 time1的136B、type4 weather的68B或type19的116B布局/释放结论|
|天气登记、metadata及DELETE安装|旧7fb8/7fbe合成a00ab6b0，7fbc以P作a1，7fc2调用a00b3a68；随后7fca写M+4=C，7fce写M+0=0x2f，7fde写P+10=M；7fd4置事件0x29，7fd8回调a00a4f82，7fdc给P，7fd2给userdata=0，7fe2/7fe6安装事件|登记在metadata挂接之前且返回未检查，沿A15/A16；不是“已保证成功订阅”。旧显示活动状态写C+24沿ui-total合同，不重做|
|Time2 DELETE入口与ctx字段清零|旧a00a4f82以event+8清bit15后比0x29；4f9e由event+4取P，4fa0保存M=P+10；M空则到尾声。非空时4fa8取C=M+4，依4fb2/4fb6/4fba/4fbe/4fc2/4fc6/4fca/4fce/4fd2清C的+0/+4/+8/+18/+c/+10/+14/+1c/+20，均SW|不是free这九个指针目标；C+24活动byte没有在该块清零。保留原零门，不新增C为空检查或重新定义返回合同|
|天气注销→wrapper归还→撤销引用|4fb0置a1=P，4fac/4fd6合成a0=a00ab6b0，4fda调a00b3abe；4fde把保存M给a0，4fe0调a008ab8a，4fe4清P+10，再原尾声返回|与登记完全同callback/page键；注销者清首匹配槽。**实际free实参是M20，不是C40或P**；直接本体未free C。下层接口不因注销取得userdata所有权|
|父root的timer和控制订阅|旧79ce/79d2尝试a01b29a0(a00ac54e,R)；79e4创建a00ac3a0、1000周期、userdata=R的timer；7a08将timer作event userdata，7a14/7a18为R安装a00a4edc/0x29。旧4efc/4f08读取R和S8；S8及event+0c的timer均非空才4f50删除timer，4f54..4f60按callback=a00ac54e注销控制订阅，4f64/4f66归还S8，4f6e清R+10|有非空门，不能写成无条件root清理；控制注销只按callback查首节点，不是天气双word注销，也不能代填订阅节点最终free。R的state8归还不填Time2 ctx40责任|
|正常唤醒/公共删除种子|guide旧saver_wake_asm已记录a00ab834事件0x11→a00a75e6；R构造kind10。非blank旧7658..766c从active screen按kind10查窗口；找到非空对象时7694调用公共删除a00ded6c|此种子早有，不重复根析构扫描。窗口kind10与子type2f不同；静态正常匹配支持删除连接，不证明某次运行查到的就是本次R。公共删除/DELETE递归ABI沿已有screen-host及H03/H04通用合同，不继承它们type19的业务释放结论|

没有旧原语义纠正；本轮修正的是任务范围判断：不能因为旧总信息消费者报告留“页面销毁未知”，就忽略父complete已保存的Time2 DELETE本体。现已解释的局部责任可以收缩为以下分析序列：

```text
weather: try register(a00ab6b0,P);
M20.context=C40; M20.type=0x2f; P.metadata=M20;
DELETE(P): clear nine C40 words in original order;
           unregister_weather(a00ab6b0,P);
           free_adapter(M20); P.metadata=0;
// No direct free(C40) in this retained handler body.
```

该伪代码只展示关系，保留登记先于挂接的原序。天气data和page是callback借用，ctx保存控件指针供既有显示使用。清指针、注销槽、释放wrapper和释放ctx是不同动作；不从本体未free C40推出整个程序无回收或任何缺陷。

## 真正新增与实际验证

新增ROM功能、显示业务、算法、库来源认证及ISA规则均为 **0**；新函数/整窗口导出 **0**。新增交付只有旧出处衔接、对象责任精度及有界检查记录。creator/DELETE早有原字，不把本轮重读称新恢复。

[verify.py](../../analysis/saver-time2-lifetime-i03-0041-20261024/verify.py) 只读主仓ROM与旧JSON，用标准库解析旧GNU行的原编码，**67个稀疏旧行锚点** 与ROM一致，**94项检查PASS**；包括九个ctx SW的原序/偏移、metadata持有槽、申请与注销/free目标。结果见[verification.json](../../analysis/saver-time2-lifetime-i03-0041-20261024/verification.json)，保存索引/出处而不重复body。VA映射VA−0x9ffff000，没有新厂商语义或模型修改。

复用筛选覆盖主仓顶层rehost JSON的三个精确地址词、指定较晚round3 records、pass3及ZIP的guide成员；旧page-logic字符串、guide/system complete和近期报告已先阅读。较晚round3/pass3未命中精确词、ZIP未含原地址只说明这些边界；SIM的saver状态重建/清零不能证明ROM ctx free。JSON、本地报告链接及提交差异检查通过，未执行任一历史验证/输入回放。

## 未闭精确边与后继种子

本题creator→metadata→同天气callback→安装DELETE→清字段/注销/free wrapper的**局部正常合同已有可定位答案**。尚未证Time2 C40最终free、实际订阅插槽成功、真实唤醒时对象身份/事件顺序和运行回收；控制摘链节点的最终回收仍沿UiIFace未知。准确来源版本、目标控件完整生命周期不在本题。

后继若要闭合C40最终所有权，需要指向**该40B分配根**的真实free实参或明确所有者/清理回调种子。当前旧材料没有此种子，不将H08/H05/H01或父root S8、子M20的free跨套C40；不另起全ROM根析构/全页面扫描。本轮按已覆盖局部合同及精确断边交付，由管理者决定换题，不自行承接。
