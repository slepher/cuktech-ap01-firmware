# I02：启动配置/端口门与 userdata 责任独立复核

2026-10-24；基线 `46fa469`，独立树/分支 `re0041-i02` / `codex/re-0041-i02`。**限定接受I01的getter返回合流、cache整U8、端口word提前快照、2B尾跳以及repeat_count=0→free(userdata)顺序；没有语义纠正，新增功能0。** 原件不是固定2秒硬件ready接口，`wifi_configured`也不等同已联网或硬件就绪。

本轮未参与I01生产，采用 reverse-engineer-anything 技能，复用旧证据并独立拆必要原编码/寄存器/分支目标。没有运行I01采集器、导入其解码器或重导callback/getter/驱动/初始化；没有打开/切换共享REA target。只写独占报告与analysis，其他agent的修改未撤销。无固件、SIM、模型、构建、回放、设备、外网、下级agent或生产ROM/配置/模型修改。

## 继承结论：已有出处 → 行为 → 局限 → 复核缺口

|已有出处|既有行为/覆盖|本轮处理与限制|
|---|---|---|
|[I01](boot-ready-increment-i01-0041-20261024.md)及其evidence.json|39个旧raw锚点、遗漏getter 2B尾跳、28B旧timer挂接复核；新功能0|独立稀疏回源，不重导函数、不把I01补证说成首次恢复整个启动流程|
|主仓`guide-complete-0041.json`的boot、boot_timer_asm、boot_delete_asm、boot_cb_asm；`system-complete-0041.json`的boot_final及local_disassembly|1000ms timer、计数两次、完成、configured/index8与窗口删除原汇编已有|主体直接继承，不能因旧SIM未执行原条件或近期报告未单列就称原件未分析|
|theme-total-state、theme-online，I01复用链|`62fc4034`活动位图word；不是纯设备数量或一般指针|本轮只判word快照0/非0，不扩全部writer或物理意义|
|buzzer/backlight第二轮已有`a008c280`合同|setter写timer repeat_count；不是立即free timer|接口语义直接继承，只核本call的timer与0实参，不扩timer最终回收实现|
|I01已复用pass3:2892、main-knob旧records/1、较晚round3 records/5和page-logic|旧timer挂接已写明；getter范围及cache初始化相关refs已定位|沿用有界覆盖与局限，不重做初始化，reference不等于writer完整合同|
|最终ZIP `tools/ap01/ap01-ui-guide.h:299`|宿主替代按`lv_tick_elaps(boot_start)<2000`阻止结束|只证明替代源码阈值，不能证明ROM原完成条件、真实调度或硬件ready|

主仓绝对前缀为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/`。本轮直接读取旧system表的getter与boot键，以及I01原证据定位；未重新搜全部历史、导出初始化或复制ZIP。I01所引用旧Evidence ID与完整复用边界继续通过其报告定位。

## 本轮复核或纠正

|I01结论|判定|独立原编码/对象依据|
|---|---|---|
|缓存bypass标记不是signed正值门|接受|`a009d7be` LUI与`d7c2` LB有效地址=`62fc3fec`；`d7ca` C.BNEZ只判非零，目标`d812`。非零跳过读取服务而返回缓存，不能改成“标记>0”|
|服务返回rc与getter返回byte不同|接受|`d7d4` a3=1；a0/a1/a2按旧LUI/ADDI对应ck_config、wifi_configured、`62fc919c`；`d7e2` JAL=`a0060946`。`d7e6` C.LI a5=1，`d7f0` BEQ a0,a5→d820，即精确rc==1；失败`d80e` SB zero到cache。没有“任意非零成功”或返回rc即configured的合同|
|getter最终返回整U8、三路径合流|接受|`d816` LBU a0,19c(s1)，随后只有恢复/返回；不是LB或`&1`。成功日志后的`d83e:d1bf`独立按C.J字段解出`d812`，与失败清0路径及bypass路径共用返回尾声；旧遗漏2B已经由I01补齐，本轮不再新增窗口|
|端口word在getter前预取|接受|`a00a74c8/74cc`形成G=`62fc402c`，`74d0` LW s4,G+8即`62fc4034`；`74fa`才调getter；`7502`将返回a0保存s7，`751c`按s7==0分流，`753a`再按保存的s4==0分流。不能改成getter后重读端口或wifi-status日志byte驱动此门|
|两次计数是有条件的userdata byte更新|接受|`7552` LBU P[0]、`7558`加1、`755a` ANDI255、`755e` SB；`7556` a4=1，`7562` BGEU 1,count返回，否则`7566`跳753e。只有初始0且连续进入getter非零/word为0的正常分支时两次到完成；不能提升为全流程固定2000ms|
|timer和P身份/实参|接受|旧28B挂接片段中`ce80`以1调用分配封装，`ce86` a2=P，`ce88` SB zero到P；callback地址`a00a7472`、间隔1000及`ce98`创建目标均独立核。callback`7488` LW取timer+c为P。正常路径`74f2`保存timer到s6；P是独立1B分配，不是root或getter缓存地址|
|完成顺序与P归还|接受|配置非零/word非零或计数到门均到`753e→a00a73fe`；`7542` a0=s6(timer)、`7544` a1=0、`7546→a008c280`；随后`754a` a0=s3(P)、`754c→a008ab8a`。不同指针根与调用顺序明确。此处没有直接free(timer)|
|getter为0的完成汇合|接受旧合同|旧标记分支的SB为G+25或G+c；之后`75b0`重新LBU另一启动标记，`75b4→a00b2ea6`、`75b8→a00a73ac`，`75bc` C.J回7542；零标记臂`75e0→a00a5cea`、`75e4` C.J回75b0。index8和helper内部不重做|
|boot窗口删除与timer userdata责任不同|接受|旧guide的boot_delete_asm明确`a00a73ac`查找boot窗口、在`a00a73f8→a00ded6c`删除该窗口；callback随后归还的参数来自timer+c。窗口删除、其已附加的DELETE处理与P分配根不同，不能把free(P)当作root/window删除或timer对象最终回收|
|SIM固定阈值与ROM条件边界|接受|只读最终ZIP明确成员，:299仍为`lv_tick_elaps(g_ap01_ui_boot_start)<2000`。这是host逻辑；旧原件计数分支、配置分流和调度时序不能由此推出硬件ready或恰好2秒效果|

没有需要纠正的机器行为。I01的名称收紧和既有主体覆盖判断均接受。缓存读取服务内部、cache标记设置政策、物理端口或硬件ready接口没有成为本轮新增问题。

## 真正新增

新增功能0、ISA规则0、完整函数导出0、原字节窗口0、开源排除0。本轮只是独立接受I01的精度与责任边界；I01新增的2B尾跳和旧挂接28B均从既存证据复核，没有再次输出为“新恢复”。不另写简化callback伪代码覆盖原分支/重读顺序。

## 未闭精确边与实际验证

继续未知：`62fc3fec`的全部设置/失效政策、持久配置的实际更新时机、活动word全部writer与物理含义、真实timer调度及timer最终归还、实际设备/联网ready效果。旧round3 cache初始化refs已有种子但本题不追初始化；没有把“未执行”说成“未分析”。局部callback正常条件已覆盖，按书收缩结束。

后继无需再次恢复boot主体。若将来单立配置更新任务，只在需求明确时复用I01已指的round3 records/5相关cache写入种子；本轮不接管初始化/驱动。timer最终回收也不由repeat_count=0的call推断。

[review.py](../../analysis/boot-ready-review-i02-0041-20261024/review.py)只用Python标准库稀疏读取主仓ROM、旧system/guide与ZIP单一成员；独立拆I/S/B/J、C.LI/C.MV/C.BNEZ/C.J及宽度/实参/目标，共110项PASS，包括I01的39旧raw锚点、两条已存窗口以及必要旧表条目。未运行生产者脚本或原程序，未用新反编译替代原编码。检查索引见[review-result.json](../../analysis/boot-ready-review-i02-0041-20261024/review-result.json)。报告相对链接、JSON和`git diff --check`通过。独立技术复核在上述范围接受I01，不代表硬件初始化或整启动系统认证完成。
