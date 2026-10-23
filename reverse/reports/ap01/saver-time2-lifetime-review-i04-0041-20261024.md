# I04：Time2/type2f局部生命周期独立复核

**限定接受I03：旧guide及weather-calendar evidence[22]已留同一Time2对象链，A15/A16已核同天气callback；DELETE清九个ctx word→同键注销→free(wrapper20)→清page+10成立。语义纠正0、新增功能0。** kind10唤醒路径只给出有状态/查找门的公共删除条件连接，不证明运行匹配对象就是本次root；ctx40最终free仍未认证，不能跨套其他type或父root状态的释放。

2026-10-24；基线 `a789ebf`，独占树/分支 `re0041-i04` / `codex/re-0041-i04`。复核者未参与I03生产，采用reverse-engineer-anything技能。只读主仓原ROM/旧JSON和既有报告，不打开或切换共享REA target/database，不运行模型、固件、SIM、构建、历史回放、设备或网络，不创建下级agent。仅写本报告及同名analysis，不改主树共享/生产ROM配置模型或其他任务；不再写旧树。对象/字段名为分析视图，不是原源码或完整类型声明。

## 继承结论：已有 → 行为 → 局限 → 复核缺口

| 已有出处 | 已解释行为与证据范围 | 本轮处理 |
| --- | --- | --- |
| [I03](saver-time2-lifetime-i03-0041-20261024.md)，主仓`reverse/rehost/guide-complete-0041.json#/bounded_local_disassembly/{saver_window_asm,saver_time_creator_asm,saver_wake_asm}` | 原root/page、20B wrapper、40B ctx、type2f/天气登记/DELETE安装及正常唤醒旧GNU指令早已留存 | 只核必要接线/宽度/分支；不重导creator、旧完整窗口或扩大根析构 |
| 主仓`reverse/rehost/weather-calendar-complete-0041.json#/evidence/22` | address=`A00A4DF8`，tool=`local GNU objdump, bounded offline ROM window`；其中含`a00a4f82` DELETE原指令 | 独立按原行取编码与当前ROM稀疏比对，九word/注销/free实参另拆字段；不运行I03验证器，不把其JSON当原件 |
| [A15](weather-subscriber-a15-0041-20261023.md)/[A16](weather-subscriber-review-a16-0041-20261023.md) | `a00a7fc2`以`(a00ab6b0,page)`登记，登记后挂接type2f/wrapper/context；回调从page+10→wrapper+4借ctx，消费天气标量 | 可靠同对象合同继承，不重做完整天气callback/range/temp/icon；A16已纠正图标首参为字段值，不能退回字段地址简写 |
| [weather dataflow](weather-dataflow-0041-20261023.md)、[UiIFace](uiiface-lifecycle-0041-20261023.md) | 天气注销`a00b3abe(cb,arg)`只清首个双word匹配；控制注销`a01b2966(cb)`是另一层、只摘节点 | 继承接口，核本次实际键；不把天气page和控制root混同，不补节点回收 |
| [H04通用公共删除合同](weather-page-close-review-h04-0041-20261023.md)、I03已列screen-host旧验收 | 公共删除可在正常条件下同步DELETE、递归子对象/析构、摘链归还；旧SIM/宿主动作不能认证ROM当次对象身份 | 只继承公共机制，不继承H04/type19业务ctx释放，不重做类型2/4/19或所有根删除者 |
| I03已做guide/system complete、pass3、round3、最终ZIP边界对照；[总信息消费者](ui-total-consumers-0041-20261023.md) | 显示状态、ctx+24活动byte和SIM屏保替代已有覆盖 | 不重复ZIP/全目录检索或运行验收；旧“页面销毁未知”不抵消旧DELETE本体已经存在 |

旧ignored证据从 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/` 只读。四层分开：已复核原字节合同直接继承；旧GNU/反编译仅在本题必要处局部核；SIM/照片/安全替代不认证ROM所有权；没有真实释放种子的ctx40最终归还继续未知。

## 本轮复核或纠正：逐项接受

[review.py](../../analysis/saver-time2-lifetime-review-i04-0041-20261024/review.py)从旧GNU行提取编码，再以`offset=VA-0x9ffff000`对主仓ROM稀疏读取；调用立即数、分支条件/目标、word访存和地址常量由本路独立拆字段。结果见 [review.json](../../analysis/saver-time2-lifetime-review-i04-0041-20261024/review.json)，不虚构新REA Evidence ID。

| I03主张 | 独立锚点与限定接受 |
| --- | --- |
| **同Time2页P、M20、C40** | **接受**。`7d4a`→`a00d91c6`创建页；`7d52:5145`请求20，`7d54`→`a008e362`，`7d58:aa8c`保存s9=M；`7d70:13058002`请求40，`7d74`同allocator，`7d78:2a89`保存s2=C；`7fb0`置s8=0x2f。分配非零门、父root/creator选择和allocator合同继承A15/A16，不展开失败臂 |
| **登记先于挂接；安装同DELETE** | **接受**。`7fb8/7fbe`构成a0=`a00ab6b0`、`7fbc` a1=P、`7fc2`→天气登记；之后`7fca` SW C→M+4、`7fce` SW type→M、`7fde` SW M→P+10。`7fc6/7fd8`构成callback=`a00a4f82`，`7fd2/7fd4/7fdc`分别userdata0/filter0x29/对象P，`7fe2/7fe6`精确到`a01ad654`。不把登记/安装尝试升级为实际插槽成功或事件已交付 |
| **DELETE事件门、P/M/C读取** | **接受**。`4f82:1c45`读event+8；LUI/addi/AND清bit15，`4f8a`比较0x29，`4f8e` BNE x15,x14→4ff4返回；匹配后`4f9e:4441`取event+4→s1=P；`4fa0` LW s2,P+10=M；`4fa4` BEQ s2,0→4fe8；`4fa8` LW a5,M+4=C。原体没有新增C非空门，不把M为空返回改写成无条件清理 |
| **九个ctx word的原序** | **接受**。`4fb2/4fb6/4fba/4fbe/4fc2/4fc6/4fca/4fce/4fd2`独立拆为`SW zero,off(a5)`，偏移依次`0,4,8,0x18,0xc,0x10,0x14,0x1c,0x20`。不是free这九个字段指向对象；未写C+0x24活动byte，不重新定义未列word |
| **同键注销→free M→清P引用** | **接受**。`4fac/4fd6`构成a0=`a00ab6b0`，`4fb0: a685`使a1=P，九个SW不改这对键；`4fda`→`a00b3abe`。`4fde:4a85`为a0=s2=M，`4fe0`→`a008ab8a`，`4fe4` SW zero,P+10。当前旧handler仅有这两个直接调用，无另一间接调用：在本直接层未出现free(C40)。不从此推出全程序无ctx回收或任何缺陷 |
| **kind10正常唤醒/公共删除条件连接** | **接受有条件边**。旧`79ba:a947`置10、`79c4` SW a5,R+3c；旧wake callback的`b8aa`置0x11，`b8ac`仅匹配事件继续，`b8ba`→`a00a75e6`。后者`75fc`在全局byte非3时转`7658`，`7658`→active screen getter，`7660:a945`给kind10，`7662`→`a00a7334`；`7666`查找返回0不进删除，`7668`取栈输出，`766c`非空才→`7694`调用`a00ded6c`。这是状态/查找/非空门下的静态连接；实际匹配对象是否本次R、是否仍持P未知 |
| **旧覆盖口径与未闭范围** | **接受**。guide旧creator、weather evidence[22]和A15/A16指向同链，不是新恢复；父root自身S8/timer/控制订阅清理在I03已有证据，不属于本轮重复验收。M20、C40、父S8以及其他type的context不能合并。公共删除若正常作用于仍持P的同一R，才可沿已知递归机制到该页DELETE；未证明实际事件时序或全生命周期归还 |

以上7项限定接受，语义纠正0。局部责任可整理为下列伪代码，**不是原源码**；借用、失败/诊断和底层接口仍沿继承合同：

```text
try_register_weather(a00ab6b0, P);  // 早于metadata挂接；未认证成功返回
M20.context = C40; M20.type = 0x2f; P.metadata = M20;
on_DELETE(P):
    if M20 != NULL:
        clear_C40_words(0,4,8,0x18,0xc,0x10,0x14,0x1c,0x20);
        unregister_first_weather_match(a00ab6b0, P);
        free_adapter(M20);
        P.metadata = NULL;
// C40 final free is NOT established here.
```

天气数据和页面作为callback借用；ctx里的控件引用被清零与释放ctx本体是不同责任。注销清slot也不取得page/context所有权。唤醒调用只把查找到的对象交公共删除，没有传C40给free；父S8归还和通用对象free也不能填补这条分配根断边。

## 真正新增与实际验证

新增ROM功能0、ISA/模型变更0、整函数/完整窗口导出0、开源来源排除0。新增交付只有独立限定接受、61条稀疏原指令与旧来源对应、11个直接调用目标、6个分支条件/目标、17处word访存字段（含九次清零）及三个地址常量的校核；旧39条handler记录只用于检查其直接调用集合，不再输出本体或整窗。没有执行I03/A15/A16历史验证器。

执行 `python -X utf8 -B reverse/analysis/saver-time2-lifetime-review-i04-0041-20261024/review.py`：PASS。脚本最初将旧handler记录条数预期写成38，实际含尾部返回记录共39，已按旧证据纠正；不涉及ROM语义变化。JSON、相对链接与`git diff --check`通过。无需新厂商语义、全ROM扫描或根析构调查。

## 精确未闭边与一个后续闭包

仍未认证C40分配根的最终free/明确所有者清理、实际天气slot登记成功、运行中kind10对象与本次R同一性、DELETE交付时序、对象/ctx全程存活与串行化、父控制订阅摘链节点回收，以及准确源码/版本。旧SIM清零/宿主reset不认证这些边。

本题旧局部合同及独立技术接受已闭合。后继只有在出现**指向同一40B分配根的实际free实参或明确owner/cleanup callback**时，才核这一小边；当前没有此种子，不套H08 type2/H05 type4/H01-H04 type19，不扩根析构/全页面扫描。管理者决定换题，本agent不自行接后继。
