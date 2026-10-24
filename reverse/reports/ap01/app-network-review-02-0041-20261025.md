# Q-06 非作者独立复核：正常关联、DHCP与同链路关闭

**已覆盖无新增；接受作者所述局部阶段和40 B关闭清槽胶水，整个网络接口未闭。** 没有发现需作者纠正的业务结论。关联返回0仍不能代表取得IPv4、通知投递成功或云ready。复核新增业务功能0。

复核者 `/root/app_network_review_02`，并非作者；独占分支 `codex/app-network-review-02-20261025`，启动基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`。按主树rolling-management顶部及Q-06本轮S补注登记，遵循reverse-design 3.1/3.2/5.1/7。仅写本文和同stem analysis，不修改管理表、作者材料或其他协作者成果。旧review01无交付，其analysis保留，未执行或导入其中脚本。

使用 reverse-engineer-anything 技能；全程静态原件读取和既有证据核对，没有运行固件、模型、SIM、QEMU、回放、构建、设备或外网，也未打开、切换REA会话。未深入公共DHCP、网络或通知库。

## 继承结论

从主仓绝对路径只读作者 [Q-06报告](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-network-research-01-0041-20261025.md)、同stem `verify.py` 和 `verification.json`（未执行或导入作者脚本）；作者材料尚未提交，故独占worktree没有其副本。继承主仓 `evidence/rea-0041-20261017/evidence/miio-recovered.md` §2–6：N=`0x62fca7f8`，N+0指M，注册与连接主体、同wlan0 down及monitor业务已有旧根合同。本次不重新恢复整个monitor，不把其已有覆盖计作新发现。

证据主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json`：`#/records/248` 的 `ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a`，`#/records/273` 的 `ev_d76ebf1841cb72027270b5feeea0b8b57e1281117d0b6694a25563737919b983`，`#/records/252` 的 `ev_c8b063daf96a046bac562fcfecfea5ece175e337890f17070b1a548e6f9c01dd`。三记录自身profile均核为 `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`；不转贴到miio旧profile或新原字读取。

## 本轮复核或纠正

独立 [review.py](../../analysis/app-network-review-02-0041-20261025/review.py) 使用标准库及既装Capstone5.0.7 RV32/RVC，仅读取主仓ROM与upper证据。重验原件6769704 B和SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射 offset=VA−`0x9ffff000`。8个窗口共592 B完整解码，18项显式断言通过；完整原字、逐指令和必要留存汇编在本地ignored [review-results.json](../../analysis/app-network-review-02-0041-20261025/review-results.json)。没有新REA Evidence ID。

| 复核点 | 独立观察与结论 |
| --- | --- |
| 注册槽 `a006580c..5840` | `a5=N+180`；五个C.SW为32位存储，偏移依次6c/70/78/7c/74，折合N+1ec/1f0/1f8/1fc/1f4。构造值分别b8bc/b99e/cda4/87d0/7a5e；cda4落N+1f8。安装指针，不是直接调用。 |
| 关联与DHCP分离 | `a006d064`调用a0075d6a，`d068: 2a89`为s2=a0；关闭临时fd后d070只在s2==0转DHCP。`d1a4`调用a00992d2，`d1a8: aa8a`为s5=a0，d1aa为有符号非负门。d0c2检查s2，零时SB stage3并加关联计数；`ce14`以s2作为a0返回。DHCP结果没有替代关联返回。 |
| DHCP/IPv4与通知 | 通知4后open的返回存全局62fc99e4；空句柄通知7。request负值通知7再helper，非负路径调用IP setter，并按非零字段选择netmask/router/DNS，随后helper和通知6。setter返回未判断，因此6仅证明到达该分支；空open路径没有该helper。均与留存及原字一致。 |
| 同接口down | flags+18掩码4为零且wlan0比较相同后，a0067230重读同全局62fc99e4；非零调用a0098a98，随后通知5。本局部无store清槽；不是已证明的释放。 |
| 关闭helper40 B | `a005face/fad2`构造62fc99e4，fad6读句柄；fad8为0跳尾声。`fada: ef906301`按JAL立即数独立解出a0098af0，返回后`fade: 23a00400`为SW zero,0(s1)，整32位清槽。与down的a0098a98是不同公开API。 |

人工核对留存中的事件4/7/6/5调用均到a01b32d6；仅接受调用边界，不证明投递、同步或接收顺序。Capstone显示的PC相对操作数没有直接当绝对地址使用，JAL按原字重解。首轮脚本返回窗口截得过短且匹配漏压缩别名，扩至ce1c并识别C.MV后通过；这是本复核脚本问题，未改变作者业务结论。

## 真正新增

新增业务及新helper恢复均为0。本次独立确认作者新增的40 B胶水：全局静态槽拥有open所得应用句柄，down借用该槽发中断；关闭路径将句柄交给a0098af0后清槽，不以API返回值作门。MAC和request输出使用栈地址，临时无线fd与DHCP handle是两种资源。这里未发现新的应用heap分配或需要扩范围的专有对象。

## 未闭精确边

公开API a0098af0/a0098a98内部释放、取消、request退出及并发顺序未知；a01b32d6实际投递与跨线程次序未知；实际无线关联、IPv4配置、云就绪未观测。不能由槽清0推断底层同步释放或无竞争。保持作者原断边，无需要另派的专有业务后继种子；未来若必须沿用厂商二进制并出现具体并发ABI需求，再以该调用/线程问题登记，不自动深入库或重开monitor。

UTC首个可用开始 `2026-10-24T16:38:09.628Z`，技术检查结束 `2026-10-24T16:39:47.994Z`，约98秒；报告与提交收尾另计，见交付回报。预估2–4分钟短复核，不凑时。正常本地Python工具调用约5秒/次，无外部排队或中断；独立token用量不可得，不能估填。主窗仍须按交付commit整合并转存ignored JSON，本文不表示已在主树合并。
