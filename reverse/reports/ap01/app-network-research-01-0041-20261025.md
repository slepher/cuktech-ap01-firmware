# Q-06：正常关联、IPv4与同链路断连接线

**已覆盖无新增（业务主体）；新增40 B正常句柄清槽胶水，作者待非作者复核。** 注册→关联→DHCP→IPv4调用／通知→wlan0-down的局部接入合同可独立使用；不认证实际无线、IPv4或云服务成功，也不宣称整个网络管理接口递归闭合。

认领 Q-06；作者 `/root/app_network_research_01`；基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`。唯一管理表的Q-06行及 [最小包](../../analysis/interface-batch-r-20261024/network-next-package.md)授权。本轮只写本报告与同名analysis目录；主树共享，未创建worktree、不撤销他人改动、不提交。

使用 [reverse-engineer-anything](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只读留存／原件；未打开或切换REA会话，未运行目标、模型、SIM、构建、网络或设备；不输出SSID/password/token/密钥值，不研究认证、安全、异常输入或漏洞。标准网络／无线／DHCP／线程／容器API到边即止。

原预测4–5＋6–9＋6–9＋4–6＝20–29分钟，中低置信；查到旧根合同明确覆盖后立即收缩，不以原预测凑量。UTC首个可用开始时间 `2026-10-24 16:11:58`；结束及实际墙钟见文末。工具等待仅包含本地读取／Python正常耗时，无排队／外部等待／中断。实际token/cached由父窗统一单列，本环境没有该任务独立用量，不能估算。

## 继承结论

| 已有出处 | 已解释行为及限制 | 本次处理 |
|---|---|---|
| [mijia-task-dependencies](mijia-task-dependencies-0041-20261017.md)、`reverse/rehost/miio-dependency-0041.json#/findings/2` | 注册点、monitor创建、连接回调a006cda4内DHCP位置已定位；驱动存在不等于联网 | 继承地址和任务身份，不把旧locator计新功能 |
| `evidence/rea-0041-20261017/evidence/miio-recovered.md` §2–5；同名JSON `#/seeds/10`、`11`、`24` | N=0x62fca7f8，N+0指M；注册和连接完整局部逻辑、关联结果不等于DHCP结果、wlan0-down打断同DHCP请求已有 | 主体直接继承，仅精确原字复核，不重新恢复整函数 |
| 同`miio-recovered.md` §6、JSON `#/seeds/25` | **netMonitorTask 0xa006d260已有父级完整函数体的局部合同**：事件0..11、超时计时、正常/自动配网分支；helper及间接依赖明确未递归闭合 | 不重开monitor。它消费网络事件并推进策略，本题仅到同事件调用点与资源槽。旧合同已解释，不存在“整个monitor无人研究”的新种子 |
| [upper-layer](upper-layer-0041-20261017.md) | 162根局部审阅并非依赖闭包；当前315函数profile及限制明确 | 不用“complete”名称冒充整网络闭合 |
| [localhost](localhost-service-0041-20261017.md) | a0066296的loopback监听和RPC已有 | 不重做监听、整个事件loop或RPC |
| [I05](wifi-config-cache-i05-0041-20261024.md)、[I06](wifi-config-cache-review-i06-0041-20261024.md) | wifi_configured是1 B配置缓存，非无线/IPv4/云ready | 不重做配置cache或writer，不移植其布尔标签到网络状态 |
| [application complete](application-rehost-complete-0041-20261017.md) | SIM已验应用使用替代无线/云服务 | 不外推到本ROM真实连接行为 |

旧`miio-recovered.md`保留其各历史Evidence/profile；同名JSON较晚的profile为`0ba751932e6730a6db2135e50d55bd95ec51a024426c4772add6d7c256bbc401`，不能把它们贴成upper的4825 profile。`miio-recovered.md` §5原Evidence为 `ev_202cde32876caa2238be46b6c3a34cee18f05e5e0646f624334e1a706b9e5c28`，§6为 `ev_9b70d58fedec1914e2521f9e05d3b8898cd374d372d1f98a37a32032157b8a09`。JSON的较晚seed24/25又各有独立Evidence，均按原记录使用。

查重限于上述父级合同、近期报告精确地址及管理表，不据一次搜索无命中声称全部历史没有分析。与F11/F15/Q04只共享公共初始化，所问槽位／对象连接不同；与I05/I06只共享Wi-Fi领域而非同一状态。

## 本轮复核或纠正

原件 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B；继承CATALOG摘要 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重hash。映射offset=VA−0x9ffff000。

本次引用 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json`：

| JSON pointer | Evidence | 本次必要部分 |
|---|---|---|
| `#/records/248` | `ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a` | callback slot注册 |
| `#/records/273` | `ev_d76ebf1841cb72027270b5feeea0b8b57e1281117d0b6694a25563737919b983` | a006cda4的门、关联返回和DHCP分支 |
| `#/records/252` | `ev_c8b063daf96a046bac562fcfecfea5ece175e337890f17070b1a548e6f9c01dd` | 同wlan0-down局部段 |
| `#/records/89` | `ev_4150d456a78d9d2a6c00fda793101e8915ff107084a8356d31e91552e2b072de` | 仅函数身份／5644 B边界消歧，未展开body |

上四条记录分别核其自身`analysis_profile.digest`为 `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`，提供方Ghidra12.1.4、RV32私有语言；不更换或重标旧Evidence。

| 接线点 | 原序／宽度／返回合同 | 判断 |
|---|---|---|
| 注册a006580c..5840 | a5=N+0x180；SW到+0x6c/+0x70/+0x78/+0x7c/+0x74，故N+0x1ec=b8bc、+1f0=b99e、+1f8=cda4、+1fc=87d0、+1f4=7a5e；cda4由a006d000−0x25c构造 | 安装32位函数指针，不是调用；不证明任务已调度 |
| 入口cdb8..cdca | 参数a0存s1=N；LW N+1e0非零则lock(handle,−1)；LBU N+1e4为0走返回0／unlock路径 | started是完整byte门，lock返回未在此判断；不由返回0推联网 |
| 公共锁范围 | 候选选择／复制／排queue在锁内；cf78..cf7e可选解锁；d0b6..d0be重新读取N+1e0并可选拿锁；cdf8再重读并可选解锁 | 保留重读与释放／再持有顺序；不保证未知并发情况下句柄恒定 |
| 关联d02a..d070 | config调用非负才建临时socket，fd非负才继续；设置接口参数后a0075d6a返回保存s2；close临时fd后，仅s2==0进DHCP | a007577c返回未检查；close返回未检查；fd与DHCP handle不同资源 |
| DHCP d124..d1aa | 通知(4)，读wlan0 MAC，open(wlan0,&mac)结果SW到全局0x62fc99e4；0为未建handle；非0则request(handle,&result)，返回保存s5，以有符号`>=0`进IPv4段 | request输出是调用栈借用，不是向通知传整包；库内部不展开 |
| IPv4 d1fc..d254 | IP setter(wlan0,s0−5c)必调；LW s0−58非0才netmask；LW s0−50非0才router；LW s0−54非0才DNS；随后a005fac4，再通知(6) | 四setter返回均未检查；事件6表示走到该正常分支，不证明每个设置成功 |
| DHCP未取得结果 | open为0或request<0均通知(7)；request<0分支另调用a005fac4；open为空不调用该helper | 保留原返回判断／清理差异，只静态描述、不执行失败输入 |
| 回调返回d0c2..d0d6/d25a | 后续判断的是**s2关联返回值**，不是s5 DHCP结果；s2==0则SB N+100=3、LW/SW N+c0加1，否则SB为0；最终a0=s2 | DHCP失败仍可能stage3且返回0。不是IP-ready或云ready |
| 主loop同链路down | NEWLINK局部过滤后，重读报文flags+18的bit2（掩码0x4）为0、比较接口名wlan0最多0x10 B；a0067230重读**同全局0x62fc99e4**；非0调用a0098a98(handle)，之后通知(5) | 这里打断请求，不释放／清槽；通知返回未检查，不是断连处理已完成 |

通知调用边界统一为 `a01b32d6(opcode)`；a0=4/6/7/5分别来自关联、DHCP正常分支、DHCP未取得结果及同接口down。未认证内部投递、去重、同步性、回调成功或服务成功。monitor对4/5/6/7的解释直接继承旧§6，不恢复整个loop或推断云端已连。

## 真正新增

父窗在本任务内确认允许沿同资源关闭边核最小helper。旧§5明确没有证明`a005fac4`实际清理副作用，upper仅给40 B callee extent；本轮读取 **0xa005fac4..faeb，40 B**，补以下事实：

```c
// 从原字恢复的语义伪代码，不是原源码；不是固定typedef。
h = load_u32(0x62fc99e4);
if (h != 0) {
    a0098af0(h);                 // DHCP handle释放侧API边界
    store_u32(0x62fc99e4, 0);   // API返回后清槽，无返回值门
}
// 调用者忽略本helper的a0结果；不声明void或可靠错误码。
```

FACE/FAD2构造0x62fc99e4；FAD6压缩LW；FAD8为零则直接到FAE2尾声；FADA `ef906301`的JAL独立解出0xa0098af0；FADE `23a00400`独立解出SW zero,0(s1)，清整32位槽。这里没有N.mutex操作。**证实的是向该API交句柄后清应用槽，未下钻或认证API内部真正释放、同步取消、request退出／并发顺序或可重入性。** 不将a0098a98中断与a0098af0释放混用；不凭地址名推完整DHCP库生命周期。

句柄由open返回并保存于静态global，正常request之后经helper交回API并清0；link-down只借用当前global发送中断。栈MAC／结果与ROM接口名为局部借用，临时无线fd在关联调用后关闭。本段不分配新的应用heap对象；候选AP链的删除／free已在旧合同，不计新增。没有证明通知或API把这些栈地址保留到返回以后。

新增网络业务／状态机功能 **0**；新增为旧合同明确未知的40 B应用句柄胶水。其余446 B原字是已有行为复核，不计新功能。不是新的REA分析：新helper保留本地原件字节与Capstone来源，无新Evidence ID或虚贴profile。

## 未闭精确边、检查与后继

已回答登记的正常路径接线、注册位宽、返回值区别、通知边界和应用资源槽归还。精确未闭项为公开DHCP调用的内部生命周期／并发、通知实际投递／跨线程先后、实际无线与IPv4成功及云服务就绪；均不能由本局部静态证据认证。

**没有本轮需要另派的专有业务后继种子。** a0098af0/a0098a98是同句柄公开API止边，a01b32d6是通知止边；不能拿它们为继续深入库内部凑时。netMonitor旧§6已覆盖，完整重连策略的helper缺口仍沿原合同保留，本轮不重开。若未来出现必须沿用原二进制的并发ABI需求，应重新登记具体调用/线程问题，不能由本报告自动续派。

[verify.py](../../analysis/app-network-research-01-0041-20261025/verify.py)仅标准库＋既装Capstone5.0.7静态读取，未运行原作者采集器或修改分析器；[verification.json](../../analysis/app-network-research-01-0041-20261025/verification.json)留10个必要窗口共486 B及旧record/EID/profile、逐指令原字。14项字段／直接跳转检查通过，所有窗口完整解码；不把Capstone的PC相对显示直接当绝对目标。作者脚本首次硬编码C.MV预期字节写错，改为独立解压缩寄存器字段后通过，ROM／旧合同无行为纠正。该检查不等于非作者验收。

正文10处链接均存在、JSON语法通过；限定路径状态为新报告与同名analysis目录，未触及共享表。非作者复核应只核注册槽、s2/s5返回分离、同global down重读和新增helper40 B，不再恢复整个monitor。

UTC结束检查时间 `2026-10-24 16:17:37`；相对首个可用开始时间的实际墙钟 **339秒（5分39秒）**，包含正常本地工具耗时；报告收尾落盘另计不足一分钟，无排队／外部等待。缩短原因是更早`miio-recovered` §2–6已完整覆盖业务主体，本轮只继承、核接线及补40 B未知胶水。不能把本次5分39秒重新标成半小时研究。
