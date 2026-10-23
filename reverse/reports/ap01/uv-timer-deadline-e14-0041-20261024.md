# E14：timer deadline 的已有 ADD64 条款与到期合同

两条 F01/F02 的 UNKNOWN 已被既有私有模型 `ap01thead2.sinc:6667` 的 ADD64 精确条款覆盖，round3 继续包含它。UNKNOWN 是这些报告使用通用 Capstone 的局限，不能外推成既有 REA 模型未支持。**本轮新增 ISA/业务功能恢复0、函数导出0；增量为复用纠正及该条款在两个原字上的局部接入合同。** 未将私有条款提升为厂商规范或准确上游来源认证。

基线 `beb2b7a3cc7695eca7c7e03284801ed7dd9a1989`，独占树 `re0041-e14`、分支 `codex/re-0041-e14`。采用 reverse-engineer-anything 技能，主仓原件只读。没有打开/切换共享 REA target、运行或修改模型、固件、SIM、回放、构建、设备或网络；没有异常/溢出输入实验。伪代码是机器合同表达，不是原源码。

## 继承结论：已有出处、行为、局限、实际缺口

| 已有出处 | 已解释行为 | 局限及本轮处理 |
| --- | --- | --- |
| [F01](miio-deferred-lifecycle-f01-0041-20261023.md)、[F02](miio-deferred-review-f02-0041-20261023.md) | start 的 a0=timer、a1=callback、a2/a3=delay、a4/a5=repeat，flags/登记/repeat/活动计数，以及 stop、callback 请求清理 | 原字窗口完整；通用解码两处 UNKNOWN。只补这两处与期限写入、消费比较，其他直接继承 |
| 既有 `ap01thead2.sinc:6638..6677`、`ap01thead2.reg.sinc:1148..1153` | 成对寄存器与64位 ADD64 的源值拼接、加法、低高word回写 | 早于本轮已存在；只读条款，不运行、不修改，不记为本轮新恢复 |
| 既有 `ap01thead3.slaspec:17..19` | include thead2，再追加 thead3 | round3 新增条款为 SUB64，非这两字所需；不得把本题称为新修复 round3 |
| 较晚 round3 `whole-rom-round3-open-20261023-004.json` 与 `whole-rom-round3-initial.evidence.json` | a01b24c0 天气 start caller 已留存，包括调用 a009d146 | 在 round3/evidence 的 JSON 有界地址检索中，仅命中这些 caller/其bundle，未命中 d18c/d1bc；不声称全历史没有其他 timer 分析 |
| [F03](miio-loop-close-f03-0041-20261023.md)、[F04](miio-loop-close-review-f04-0041-20261023.md)，F01/F02 callback kind0..6 | loop close walker、静态 timer 与请求生命周期的已核边界 | 完全继承，不回退 F02 当时未知作为新缺口；本题不重做销毁、提交者、heap |

主仓只读模型来源前缀：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/`。其中 thead2 的精确 ADD64 条款使用 `op=0x77, funct3=1, funct7=0x60`；thead3 加载上述条款。round3 caller Evidence 为 `ev_7fbfe06c4fd42cba1566477dac4d2768c174d596b4c44e0a51849df76a980564`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`。它不是 timer body Evidence。

## 本轮复核或纠正

### 两条原字与成对 ABI

原 ROM 为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `VA - 0x9ffff000`。必要原字窗口与34条逐指令复核见 [verification.json](../../analysis/uv-timer-deadline-e14-0041-20261024/verification.json)，只含 `a009d182..d1cd` 与 `a009d314..d335`。

| 地址/原字节 | 独立位域 | 继承既有条款后的机器合同 |
| --- | --- | --- |
| d18c `7715aac0`，LE word `c0aa1577` | op77/f3=1/f7=60，rd10、rs1=20、rs2=10；pair selectors5/10/5 | `(a1:a0) = (s5:s4) + (a1:a0)`；输入 delay 加 loop 时间，结果64位 |
| d1bc `7716c5c0`，LE word `c0c51677` | 同opcode，rd12、rs1=10、rs2=12；pair selectors6/5/6 | `(a3:a2) = (a1:a0) + (a3:a2)`；右侧为已装入的0:1；a0/a1不变 |

pair selector在旧寄存器条款中分别取bits8..11、16..19、21..24，附着表映射至偶数低寄存器及下一奇数高寄存器。两处均是偶数寄存器编码，故不涉及zero/奇数选择器特殊情形。条款先把源低/高32位零扩展拼为8字节，再计算并分别回写低/高32位；没有32位有符号扩展，没有饱和加法或额外标志输出。加法的64位位串结果来自既有条款；本轮没有运行算术模型或测试极端数值。

`d182` 从timer+4取loop；`d184/d188` 分别读loop+140/+144至a0/a1。F02已核delay保存于s4/s5，此处中间没有调用。d18c结果在 `d1a4 a8c0`、`d1a6 ecc0` 以32位word存timer+40/+44。

中间原序不能省略：`d190 63e65501` 是 `bltu a1,s5,d19c`；`d194 6396ba00` 是 `bne s5,a1,d1a0`；高word相等时 `d198 63744501` 是 `bgeu a0,s4,d1a0`。只有双word结果按unsigned小于delay时走 `d19c/d19e`，把a0/a1均设为-1位串，再写期限。这是原件已有的限幅分支；不是本轮开展溢出测试，也不是新增修正建议。正常可表示的和直接保存。

`d1b0/d1b4` 读loop+138/+13c至a0/a1，`d1b8/d1ba` 装a2=1/a3=0。d1bc只写a2/a3；`d1c0 23acc712`、`d1c4 23aed712` 回写增量后的两个word到loop+138/+13c，`d1ca a8c8`、`d1cc ecc8` 则保存**旧**a0/a1到timer+50/+54。旧序号关联的heap排序语义直接沿既有合同，此处不展开完整heap或称为新增恢复。

### 正常期限写入到到期消费

F02已核 `a009d304` a0=loop、s3保存loop；`d314` 取loop+130的node；node=timer+34，`d320` 得timer=node-34。`d31a` 读node+10即timer+44高word；`d31c` 读loop+144当前高word。

`d324 63e8e704`：若unsigned now_hi < deadline_hi，跳d374退出；`d328 6317f700`：高word不等且前述未退出，即now_hi > deadline_hi，直接跳d336。高word相等才在d32c/d32e读node+c即timer+40低word及loop+140低word；`d332 63e1e704` 若unsigned now_lo < deadline_lo，退出。其余包括相等均到d336。

因此消费门是 `deadline <= loop_now` 的完整unsigned64比较；没有把低word单独按有符号时间差比较。此处loop+140/+144是消费时重新加载的时间槽，与start的同偏移相接，但不证明真实时钟刷新/墙钟精度或时间单位。

通过比较后，stop、repeat重排、最后重读callback并以a0=timer间接调用的合同继承F02：start/dispatcher不接管请求data本身，正常MiIO callback最终释放保存请求并清data。repeat原值作为新的delay与repeat成对传回start；没有凭期限比较推断callback必定在某个实时时刻发生。

```c
// 正常有效 start 路径的局部表达；flags/heap/返回合同继承F01/F02。
uint64_t now = load_pair32(loop + 0x140, loop + 0x144);
uint64_t result = ADD64_existing_clause(delay, now);
if (result < delay) result = UINT64_MAX;  // 原分支；未执行测试
store_pair32(timer + 0x40, result);
uint64_t order = load_pair32(loop + 0x138, loop + 0x13c);
store_pair32(loop + 0x138, ADD64_existing_clause(order, 1));
store_pair32(timer + 0x50, order);         // 旧值
// 经过继承的heap登记后，另一消费入口重新读取时间：
if (unsigned_pair64(timer + 0x40) <= unsigned_pair64(loop + 0x140))
    inherited_stop_repeat_callback_contract(timer);
```

布局仅为本路径的word视图；不是完整结构体、原typedef或sizeof。计时值、期限及顺序槽为64位位串；它们的业务名称由读写/比较关联推断，字段宽度与unsigned比较由原指令直接观察。没有新增对象或生命周期假说。

## 真正新增与实际静态验证

新增功能恢复0；新增是对F01/F02 UNKNOWN边界的纠正、两字位域/pair实例化及期限设置到消费的文档接线。既有模型语义、原窗口已存在，不能把本轮复读或闭包说明重新计入功能恢复。

运行 [verify.py](../../analysis/uv-timer-deadline-e14-0041-20261024/verify.py)：`python -X utf8 -B reverse/analysis/uv-timer-deadline-e14-0041-20261024/verify.py`，PASS，34条稀疏指令原字与F02既有窗口一致；32条普通指令重新用Capstone解码，两条厂商字独立移位解位域并匹配既有条款/寄存器表；round3有界命中2文件。没有重导整函数或执行模型。`git diff --check`通过。不声称独立技术验收，交新agent复核。

## 未闭精确边与后续闭包

仍未认证厂商原版ISA文档、准确通用库版本/修改来源；现有私有ADD64条款是可定位继承依据，不能代表所有扩展指令均正确。timer正常期限形成与比较在该既有条款下已相接；loop+140/+144的时间生产者、刷新频率和实际单位本轮未核。heap完整性、外部串行化及真实callback时刻均不因本题获证。

本题到指定窗口合同闭合即结束，不自动接题。一个后续闭包建议：若管理者确需认证计时单位，仅追loop+140/+144的一个正常时间刷新写入及上游返回单位；避免再次恢复start、heap或callback/close walker。
