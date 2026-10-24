# Q-32 / S-P50 串行 uplink 非作者复核

状态：**可独立使用阶段已闭合但接口未闭**。限定接受作者 `f51ccd053ff7386420558c00aa303b9a0519cc64` 与补正 `6ebe2b0f6c8aa59f2850f1c908522059369b303d`；行为纠正0，descriptor基址记号纠正1，新增业务0。只复核三窗818 B，不将状态2/3解释为idle或远端动作完成。

复核者 app_serial_uplink_review_01；独占分支 `codex/app-serial-uplink-review-01-20261025`，实际基线 `5a5b732235c5b0d1654c8bc543b92c9cc5331e0b`；原派发基线5f50102为其祖先。范围遵循主仓reverse-design 3.1/3.2/5.1/7、rolling-management-0041-20261023.md Q-32及281行补位登记、PREP S-P50初模板/ready动态；不修改认领表，不派下级。

## 继承结论与证据身份

原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，文件offset=VA−0x9ffff000。

旧根只继承主仓 `evidence/rea-0041-20261017/evidence/upper-miio-b.md` 的cmd.json_send a00be264（ev_23a9d38ca3701fb5f9aa16709171f4d4f30838bd6c6ad0eb382ea1dedcc14eca）及cmd.call a00be8a0（ev_a493a0895eeb379f14ad7198eb6850423737ae07e73cc81ca47cdb1c2490dabe）。前者submit0写busy1，后者busy0才委托新call body。两者不能互套busy写入。

SDK a0111ff6调用布局沿miio-recovered.md ev_a42727108b8c080cc1e6f348c20a0f735f6a4eb0100a6d68a74ad5f596e5eff7及派发已验F11/F12/Q24同步payload copy、callback/C浅持有前提；不展开SDK。公共JSON/parser/tokenizer/formatter与writer只核本层实参和返回门，不认证库版本或完整库生命周期。

作者报告/留存读取自独占树 `D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/serial-uplink01/reverse/` 下 `reports/ap01/app-serial-uplink-research-01-0041-20261025.md` 和 `analysis/app-serial-uplink-research-01-0041-20261025/{extract.py,instructions.json,disassembly.txt,strings.json}`。extract.py只读未执行。整合后上述相对路径以主仓为准；复验源码优先主仓留存，未转存时才回退作者树。

## 本轮复核与纠正

独立脚本 `reverse/analysis/app-serial-uplink-review-01-0041-20261025/review.py` 只读取ROM/留存，以本地Capstone静态RV32/RVC逐条核原字、地址、宽度和汇编，未调用作者代码。三个半开窗a00be6d8..a00be8a0（456 B）、a00ba8b2..a00ba994（226 B）、a00ba536..a00ba5be（136 B）共818 B、246条；全部原字与留存一致，1厂商word未认证。9个必要字符串逐项与ROM核对。关键分支与寄存器/栈偏移另作人工控制流复核。

1. **call构造/交接接受。** tokenizer分隔串为`" ,"`、上限64；count<=0发error，正count生成id、`_sync.%s`方法及params raw。C+0x200/204提供scratch/cap，cap无符号截到min(cap,0x558)。方法缓冲总64 B（首word清0，后60 B memset），不混同descriptor。a00be814原字`1305c4e6`、a00be822 `9305c4e6`分别为addi a0/a1,s0,-0x194，故D=s0−0x194。作者初稿a0frame是记号笔误，补正6ebe2b0只改此句，已确认无需重验无关body。D+4=id、byte+0x10=0、+0x20=len、+0x24=scratch、+0x2c=callback、+0x30=C均与栈存储相符。
2. **真callback literal与busy。** a00be82a `b7b70ba0`及82e `9387278b`独立位域核为0xa00bb000−0x74e=0xa00ba8b2。submit a0111ff6返回0才调用C+0x14(C+4,"ok")；此body无C+0x1fc写入，不能补写1。serial ok仅表示本地接受。两callback全部busy store仅a00ba97e `238ef91e`（s3=C）及a00ba5ac `238ea41e`（s1=C），均byte+0x1fc；没有清0。
3. **json_send全raw。** a00ba536从M+0x20/1c取原文/长，writer以C scratch初始化，写result并追加整个响应，无JSON parse、消息状态或id成功门。finalize a018fd68返回值经snez+2得到2/3后写busy，callback固定返回0。无本层M/payload/C释放。
4. **call仅result。** a00ba8b2 parse非0直达a00ba97c置3；parse0查result/type0 wildcard。NULL或空slice同样置3；有效token的start/end构成原文slice，type3时ptr−1/len+2保留引号。a00ba938归还token vector后a00ba93c/940才核ptr/len并消费原文slice：ptr是M原文借用，并非已释放token vector。有效slice才writer/finalize，返回0置2、非0置3，callback固定返回0。解析失败清理由公共API前提承担，不从本层推完整失败分配保证。
5. **所有权与边界。** 栈D/方法/builder只活到本层返回，提交依赖已验SDK同步payload copy，C仍浅持有。两callback借用M及其原文，token vector仅call成功parse路径归还；未见把slice保存至C，也未见free M或scratch。writer finalize是输出阶段调用，不能当free或云动作成功。callback返回为本层原文使用终点，外部writer具体持有止API。

原字a00be880 `8b452b45`（0x452b458b）仍RAW_UNKNOWN；字段rd=a1、rs1=s6、rs2=s2不构成已认证indexed-load语义。循环后续strlen/raw追加可证，多参数的该字精确取址仍限定，未补NOP、未改模型。

## 真正新增

新增业务0，新增取证body0。新增仅非作者独立原字/控制流验收与复验源码；必要基址记号已由原作者修正。不将旧根、SDK/API继承或818 B重读计为新增恢复。

## 未闭精确边

该阶段接受后的状态链仅为：旧busy0门→call构造→SDK本地接受/serial ok→异步M借用→全raw或result slice→finalize→busy2/3→callback0。状态2/3的消费者、串口实际发送及busy0归还不在三窗，不能套Q-30下行周期。保留厂商word、多参数精确取址、完整grammar、writer持有、SDK取消/超时/并发、C和scratch总寿命、实际云权限/动作未知。可定位的后续问题是C+0x1fc状态2/3的读取/输出/清0消费者，须另行登记有界种子后才研究；本轮不扩读。

## 时间与交付

预测3–4分钟，中置信，参照作者总205秒/技术182秒。首工具UTC **2026-10-24 18:28:01**；初次技术检查完成 **18:29:23**（82秒）。其后因记号笔误交父窗并接受中断，恢复首工具 **18:31:22**；18:29:23→18:31:22观察间隔119秒包含父窗协调/作者补正/调度，精确中断起止与纯等待不可得，不能当有效工时或纯暂停。恢复只核6ebe2b0的单句差集。最终技术、提交、停止时钟由交付消息分列，完整墙钟不冒称有效工时；token/input/cached/output用量均不可得，不估造。

只做静态读取和本地复验：未执行目标、作者脚本、模型、SIM/QEMU/回放/构建，未连接设备/外网，未改ROM、生产配置、分析器或共享REA。仅本报告与同stem复验源码提交；没有新增ignored中间产物，父窗负责合并与清理。
