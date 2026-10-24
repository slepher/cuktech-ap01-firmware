# Q-09：同N的OT就绪、探测及重连计时阶段

**可独立使用的计时决策阶段已闭合，完整应用接入接口未闭；作者待非作者复核。** 四helper只返回本轮动作门，不能把它们的0/1解释成无线、IPv4或云端实际成功。本轮首次补出四个原先只列调用的callee合同；不重做monitor整体、Q06或公共库。

认领Q-09；作者`/root/app_network_research_02`；分支`codex/app-network-research-02-20261025`，基线`27c4d34abff7726fc845f26326b97325fa03d3c0`。独占本报告与同stem analysis，主树流程/证据只读，不撤销他人改动，本地提交、不推送。

采用[reverse-engineer-anything](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)：只静态读取既存证据和四callee原字；未打开、切换或修改REA会话、语言模型；未执行固件、模型、SIM、QEMU、构建、回放、设备或外网。没有读取或输出SSID、密码、密钥、token或私有账户内容。

## 继承结论

- 主仓`reverse/reports/ap01/reverse-design.md` §3.1/3.2/5.1/7及唯一认领表Q09确定边界；[Q06](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-network-research-01-0041-20261025.md)的注册、关联、DHCP、IPv4和40 B句柄归还胶水直接继承。
- 主仓`evidence/rea-0041-20261017/evidence/miio-recovered.md` §6/§10明确整个netMonitorTask已有局部合同，四helper未全恢复。因此新差集为四helper语义和同caller接线，不是5644 B monitor“从未分析”。N=`0x62fca7f8`，`u32(N+0)`为M，`u32(N+0x1e0)`为可选mutex，均沿旧合同。
- 旧`reverse/analysis/0041-20261013/0041-ghidra-pass1..5.txt`精确地址搜索没有命中四callee。此为有界查重，不声称所有历史无研究。派发中“已有旧body”随后由父窗澄清为**record89中callee extent元数据和caller**，不是四callee本体；不得用元数据冒充反编译正文。本轮停止进一步广搜，以授权的原字恢复。
- caller来自`evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/89`，Evidence `ev_4150d456a78d9d2a6c00fda793101e8915ff107084a8356d31e91552e2b072de`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。私有Ghidra语言`RISCV:LE:32:ap01thead2`，Ghidra12.1.4；仅继承所需caller段，没有新REA Evidence或把旧profile贴到本次Capstone。
- elapsed输入是旧monitor按tick折算并携亚秒余量的整秒增量。它可能超过1，本轮所有累计都必须加elapsed，不能改成“每次调用加1”。底层时间单位及运行调度仍沿旧静态推断，不声称实测。

## 本轮复核或纠正

原件主仓`roms/0041/ap01-1.0.2_0041.bin`，6769704 B；沿CATALOG SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射offset=VA−`0x9ffff000`。本轮不重新全盘hash，静态读取四callee共716 B：

| callee | inclusive VA | 文件offset / 长度 | 来源 |
|---|---|---|---|
| A：`a0067aec` | `a0067aec..a0067b93` | `0x68aec` / 168 B | 原件＋Capstone5.0.7 |
| B：`a0067b94` | `a0067b94..a0067be5` | `0x68b94` / 82 B | 同上 |
| C：`a0068854` | `a0068854..a0068913` | `0x69854` / 192 B | 同上 |
| D：`a0068914` | `a0068914..a0068a25` | `0x69914` / 274 B | 同上＋两条既存模型解释 |

以上offset注意基址是9ffff000，不是a0000000。所有普通RV32/RVC指令完整顺序读取；Capstone的相对分支显示按PC相加解释。D中的`a006895a:8bd64758`及`a00689ce:8b56f944`是完整32位厂商字，不能将其后半当压缩指令。初次Capstone在此停止；随后脚本将这两字保留为vendor-word，逐字核已有`evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc`（6596、6615起）解释，未更改分析器：

- `0x5847d68b`：rd13=a3、rs1=15=a5、立即数4、shift0、高5位11，`th.swia a3,a5,4,0`，先写word `[a5]`再a5+=4。
- `0x44f9568b`：rd13=a3、rs1=18=s2、rs2=15=a5、shift2、高5位8，`th.srw a3,s2,a5,2`，写word `[s2+(a5<<2)]`，不改s2。

厂商语义是对已存模型的继承及原编码字段核对，非独立认证整个ISA或新Ghidra分析。脚本不将未知编码当NOP，也不声称Capstone本身支持这两条。

## 真正新增

### 四helper共享ABI与资源约束

四入口均保存a0为同N、a1为elapsed；返回a0是明确0/1动作门。进入后读取N+1e0，非零调用`a005f3d8(handle,-1)`；返回前**重新读取**N+1e0，非零经`a01b3c8c(handle)`解锁。lock/unlock返回均不参与本函数判断，不能保证并发下handle恒定，也不能把返回1理解为锁或网络调用成功。没有申请新应用heap、没有转移N/M所有权，没有销毁mutex；N与M均为借用。日志与诊断上报在锁范围内；不把这些API深入成新研究题。

所有加法、差、比较按u32模2^32运算；源码替代若使用更宽饱和计数会改变原边界。参数N有效性由caller前提提供，这些函数不验证NULL。

| 门 | 输入与字段（字节偏移） | 正常动作及返回 |
|---|---|---|
| A，监视重启计时 | `sum=u32(N+1c0)+elapsed`，先写回；与3599无符号比较 | sum>3599：清N+1c0，返回1；否则保留sum返回0。即整秒累计达到3600，不是严格“3600次调用”。日志称reboot trigger；helper自身没有重启调用。 |
| B，周期探测计时 | `sum=u32(N+1d0)+elapsed`；常量14 | sum>14：清N+1d0返回1；否则存sum返回0。即累计达到15；**超过阈值时不先存sum**，直接清零。 |
| C，离线周期 | `sum=u32(N+184)+elapsed`先写回；threshold=`u32(N+188)` | sum>=threshold：清N+184，调用`a01ac568(M,"miio_monitor","offline timeout",15)`，忽略返回，返回1；sum<threshold返回0。threshold为0则每次触发；此为静态表达，不试验异常输入。 |
| D，离线次数滑窗 | `sum=u32(N+190)+elapsed`先写回；采样间隔=`u32(N+188)/10` | sum<间隔：不移动样本返回0；否则清N+190、移动样本、求计数差；差达到`u32(N+1bc)`后诊断、重置样本并返回1，未达到返回0。 |

A关键原字：`7b10 23a0b41c`为SW到1c0，`7b14 addi a5,s2,-0x1f1`在s2=0x1000后得3599，`7b18 63f8b704`为BGEU3599,sum到未触发分支，触发路径`7b24`清槽。B：`7bb4 b947`常量14，`7bb8 63e3b702`为BLTU14,sum到清槽／返回1。

C：`887a 23a2b418`先写sum；`887e 63e6f506`为BLTU sum,threshold到返回0；`888c`清槽；`8890`a3=15，`889a/889e`目标独立PC相加为a01ac568。D：`893a b3d7e702`是DIVU threshold,10；`8946 63eaf508`为BLTU sum,quotient到返回0。四API出口锁重读、返回寄存器均核过。

D采样数组共十个word `H[0..9]=N+194..1b8`：先顺序`H[i]=H[i+1]`（i=0..8），随后`H[9]=u32(N+18c)`。比较的是`u32(H[9]-H[0]) < u32(N+1bc)`，含无符号回绕；**先移动再求差**，不是移动前十项的差。达到阈值调用`a01ac568(M,"miio_monitor","offline countout",16)`，忽略返回；重读N+18c，将全部十项置成该当前计数，清N+190，返回1。采样时只移动一格，无论elapsed跨越几个间隔；不会补跑多格，也不会保留超出的余秒。

`896a 1cdf`写H[9]，`8970 63e3e708`为BLTU差,阈值；`8958..895e`配合swia得到9次左移，`89cc`常量10及`89ce..89d4`配合srw得到10次重置。这是计数差窗口，实际经过时长受调度／elapsed影响；不能保证严格的墙钟“最近threshold秒”。本题没有展开N+18c的所有writer，故称其为累计计数槽，不武断命名“断线次数生产器”。

### 同caller中OT状态与cloud-ready分流

以下只组合record89已有caller及新增门；state=`u8(M+c8)`由M+cc锁保护读出，随后解锁；ready=`u8(M+1af0)`是独立byte。**state2不等于ready，state1也不等于IPv4失败。** 已配置正常模式由旧monitor门选择，Q06底层N+100阶段不参与替代这两个字段。

| caller正常分支 | 顺序与门的消费 |
|---|---|
| state2且ready非零 | N+1cc+=elapsed；分别在N锁下清A的1c0、C的184。旧一次性crash处理后经`a0067be6(N)`，调用D；D=0跳共同状态更新，D=1先过`a0067c20()`，其返回0才请求`a01b3d12(N)`。不把ready理解为这四helper刚测得的成功。 |
| state2且ready为零 | 继承`a0068d84(N,0,0)`及旧provision-stat处理后，调用B；B=1调用`a0195ce4(M,N)`，结果在此忽略；N+1d4非零时N+1c8+=elapsed。再A；A=1调用`a0069356(M,"miio_monitor")`并跳共同状态更新，跳过C/D。A=0才C；C=0才D；C=1或D=1走a0067c20门，再可能a01b3d12。 |
| state1 | B同上。旧局部布尔s6为零则直接共同状态更新；s6非零才A；A=1同上；A=0调用C，C=1直接a01b3d12(N)，随后仍调用D，D=1再次a01b3d12(N)。**此处不经过a0067c20门，也不是C触发后跳过D。** s6继承旧provisioner连接标记，不重新研究其所有writer。 |
| state既非1也非2 | 继承a0068d84，N+1c4+=elapsed；s6为零时在N锁下清D的190并将十项H置当前N+18c。调用A；A=1同上；否则C，C=1直接a01b3d12(N)，C=0共同更新；此分支没有D调用。 |

精确caller锚：state读`e350..e378`、ready读`e37c..e386`，ready清槽`e38a..e3d0`；B/A链`e6aa..e6e8`，C及a0067c20门`e75c..e778`；state1 `e786..e7cc`，其它state `e7ce..e83a`。共同状态分类与更新是旧合同`e778..e85c`，不算新增业务。

这说明正常重建必须区分“周期计时门”“请求动作”和“服务就绪”。A/C/D返回1只让caller发请求。a0069356语义沿旧诊断/监视接口边保留，日志“reboot”不足以证明该调用已经使设备重启；a01b3d12只作为线程/调度调用边，未认证异步完成或线程安全。a0195ce4跨入旧provision接口，也不能声称B=1完成了探测。

## 未闭精确边、检查与交付

四helper的字段、参数、0/1、无符号阈值、复位、调用顺序、mutex借用／解锁均已回答。没有完整恢复云接入／重连接口：`a0067c20()`的许可策略、`a0069356`具体监视动作、`a0195ce4`探测/配网处理及N+18c计数全部生产侧未由本题认证；其中后两项属于不同接口，不自动续派。线程/调度a01b3d12、mutex a005f3d8/a01b3c8c、诊断a01ac568止公开能力边，不下钻实现。实际联网、云端应答、并发与计数wrap运行结果均未知。

有种子的最小后续建议：若重建需要保留state2下的原许可策略，可另登记`a006e768→a0067c20()`，先查已有合同并确认其实际归属；该种子不是本报告自动授权，也不能拿它扩回完整monitor。

[verify.py](../../analysis/app-network-research-02-0041-20261025/verify.py)只读本地原件和record89；[verification.json](../../analysis/app-network-research-02-0041-20261025/verification.json)保留716 B原字、普通指令、两厂商完整word、10处关键宽度／比较原字断言及所需caller切片；[inspection.txt](../../analysis/app-network-research-02-0041-20261025/inspection.txt)为静态输出。脚本执行通过，不是固件执行或非作者验收。ignored交付清单仅verification.json与inspection.txt，父窗按同相对路径转存并逐字节或SHA256核对后再清理任务树。

预估12–19分钟，中低置信，阶段2–3／5–8／3–5／2–3分钟；实际从本任务首轮工具开始至最后检查见下面补记。材料定位失误引入额外本地搜索／JSON结构确认；该阶段未单独采集时钟，不能给出可靠秒数，含两次结构差异导致的只读解析失败；随后父窗明确无四callee旧body，停止搜索。无外部排队／中断；工具等待为正常本地读取及解析，不能将墙钟等同有效工时。本运行环境无独立token/cached计量，不能估算，由父窗如有遥测单列。

UTC计时补记：首次可得时钟`2026-10-24 16:44:59.395`；最后静态复验`2026-10-24 16:49:09.588`，可核实子区间250.193秒，包含原字恢复和报告落盘。首轮查重开始未采UTC，该子区间不是全任务耗时；派发至交付总墙钟若父窗有创建遥测则由父窗补列，不能从名义预测倒算。提交收尾另计。
