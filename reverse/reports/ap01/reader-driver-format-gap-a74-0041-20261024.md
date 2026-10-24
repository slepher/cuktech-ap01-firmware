# A74：路径格式调用的实际适配与输出断边（0041）

认领 J08/11，作者 `/root/g23`。固定 worktree `re0041-a74`、分支 `codex/re-0041-a74`、基线 `bd457a6`。本题只解释已验 `0xa008ab4c → 0xa0053252(buf,256,fmt,va)` 后的适配，未恢复格式引擎。结论：非零 count 臂先写 `U8(*buf)=0`，构造包含 buf、count−1 和三个函数地址的栈结构，再经既存 32B wrapper 交给 `0xa01a37d2(S,0,0,fmt,va)`；两层正常返回原样传递 a0。**实际输出路径字符串仍未证**，目前只能证明调用前的首字节为零，不能把它外推为调用后的 NUL 或字符串内容。

## 1. 继承结论与查重

事实：继承 [A67](reader-driver-open-close-review-a67-0041-20261024.md) 对 A66 的限定接受：mode2 的路径 callback 经 `0xa008ab4c` 使用 256B 栈 buf，fmt 指向 `0xa06371e4` 的 `2f257300`（`/%s\0`）；suffix 指针作为原 a3 保存到 wrapper 的 varargs 包，a4..a7 后续保存；wrapper 把包地址作为 a3 传给 `0xa0053252`。路径 callback 忽略格式调用返回，继续 fd-open 接口。该原调用、literal 和 42B wrapper 本轮不再读字节。

事实：先查较晚 [C14](text-update-entry-review-c14-0041-20261023.md) 与 [C24](text-entry-source-review-c24-0041-20261024.md)。C13/C14 验的是另一 caller 对 `0xa0053252` 的两遍调用、首返+1 分配、第二返被忽略；没有验本函数输出。C23/C24 的 LVGL 候选来源和 `lv_vsnprintf` 语境不能认证原 ROM formatter 的长度、NUL、va 推进或精确版本。0031 的同名符号也不作为 0041 证据。此次差集是 0041 真实 formatter 适配体，不重做这些已验调用。

旧索引 `whole-rom-coverage-0041-20261023-round1.json` 的 functions1350 仅给 `0xa0053252..0xa00532c9`（120B），extent EID `ev_c9f66f32e2dd4210bcc045e7ce80bc06a1a7ffae5e64ec58b29d9453e12f295f`，direct-call EID `ev_179646298e8c44991c312b52a8eec64b5f992f60e570bbd88220fddf81722ead` 指向 `0xa002d770`；没有该入口 dossier 或历史合同。functions617 的 `0xa002d770` 有旧 32B dossier，EID `ev_2fc7174be7213a9616dc6d46d18c0831acd1c06324cba526633b36c29ab2f22e`。主窗据此登记 120B 原字段增量及仅复用旧 d770 dossier；没有读取新引擎或函数指针目标 body。

## 2. 本轮复核或纠正

本轮没有纠正 A66/A67 或 C14/C24 的已验语义；它们的“实际路径输出未证”边界保留。`snprintf`/`vsnprintf` 是候选家族命名，不据此补标准原型、字节输出和 return 含义。

原件只读主仓 `roms/0041/ap01-1.0.2_0041.bin`，长度 6,769,704B，继承 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，VA−file=`0x9ffff000`。本轮仅新读 `[0xa0053252,0xa00532ca)` 120B。工具为 Capstone 5.0.7 RV32/RVC 静态解码，并由自写字段检查独立核 32bit I/U/S/JAL 与压缩 branch/jump 字段；没有运行目标、输入枚举、指令模拟或作者旧脚本。

旧 `0xa002d770` assembly 从主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json` 精确 EID 取出；其 `upper-coverage.json` 对应记录仅含边界，不把 metadata 误作 body。旧 profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`，language `RISCV:LE:32:ap01thead2`。本轮不更改或执行该模型，不切换共享 REA。新体未遇未知编码；完整解码覆盖 120B 只说明该窗口可解码，并非整个格式器已闭合。

## 3. 真正新增：实际参数、局部状态与正常返回

以下是静态事实及推导，不是原源码。入口 a0=buf、a1=count word、a2=fmt、a3=va 包；s0 被设为入口 sp。局部 `S=s0−0x28`，六个 word 槽在本函数栈帧内。

| 地址／原字 | 实际动作 |
| --- | --- |
| `0xa005325a 2e87`，`0xa0053260 b285` | a4=count；a1=fmt，原 a3 尚未改写 |
| `0xa0053266 29c3` | a4==0 跳 `0xa00532a8`，是零比较，没有 signed 长度门 |
| `0xa0053268..3270` | 构造 `0xa002b536`，SW 到 S+4 |
| `0xa0053274..327e`，其中 `327c 7d17` | 构造 `0xa002b4d8`；a4减1；SW 地址到 S+8 |
| `0xa005325c b7b702a0`，`3262 9387e7f2`，`3282 2322f4fe` | 构造 `0xa002af2e` 并 SW 到 S+0xc |
| `0xa0053286 232c04fc` | SW zero 到 S+0 |
| `0xa005328a 2324a4fe`，`328e 2326e4fe` | SW buf 到 S+0x10，SW count−1 到 S+0x14 |
| `0xa0053292 23000500` | **SB zero,0(buf)**，先于底层调用 |
| `0xa0053296 130584fd`，`329a 3686`，`329c efa04dcd` | a0=S；a2=原 a3；JAL `0xa002d770(S,fmt,va)` |
| `0xa00532a0..32a6` | 恢复 ra/s0/sp，RET；没有改 a0 或补写 buf |

因此真实 count=256 实例为 `S={0,0xa002b536,0xa002b4d8,0xa002af2e,buf,255}`，按上表顺序构造，并先写 `buf[0]=0`。count−1 是 32bit word 减法；没有从本函数推出参数为 signed/unsigned C size 类型。count0 臂为 `0xa00532a8..32c8`：S+4 改为 `0xa002b554`，S+8 改为 `0xa002b578`，S+0xc 仍为 `0xa002af2e`，S+0 清零，`32c8 f9b7` 跳 `3296` 共用调用。该臂没有给 S+0x10/+0x14 赋值，也没有直接写 buf；**不据此推断引擎是否读取这些槽**。不作异常域验证。

既存 d770 32B 体的必要原序是：

```text
0xa002d778 a3=a1        // fmt
0xa002d77a a4=a2        // va 包
0xa002d77c a1=0
0xa002d77e a2=0
0xa002d780 AUIPC ra,0x176
0xa002d784 JALR ra,ra,0x52  // ->0xa01a37d2
0xa002d788..d78e 恢复/RET  // a0 原样返回
```

所以引擎实际前五个参数 word 为 `(S,0,0,fmt,va)`，不是从标准函数名套的原型；a5 等残留寄存器不登记为新 formal 参数。两层适配体各自只做栈保存、局部结构构造、上述初始字节写及调用，正常返回均未解释或折叠 a0。`a0` 的数值意义、负值、计数范围与 fmt 成功域均未知。

所有权：S 和 varargs 包分别是调用层栈对象，buf 为已验 caller 栈存储；本层没有 allocation/free。能证明指针被交给下层，不能证明引擎或三个函数指针不会持有、不会访问其他对象；不能仅凭栈来源断言借用已安全结束。S+4/+8/+c 保存的是实际函数地址，但本轮尚未看引擎使用点，故“writer/callback”仅为用途候选。

机器合同见 [contract.json](../../analysis/reader-driver-format-gap-a74-0041-20261024/contract.json)。原字/逐行留存与 39 项字段或旧 assembly 检查见本地忽略 [evidence.json](../../analysis/reader-driver-format-gap-a74-0041-20261024/evidence.json)，复验源码 [check.py](../../analysis/reader-driver-format-gap-a74-0041-20261024/check.py)。这是本作者静态检查，不是非作者复核。

## 4. 未闭精确边与后继

未闭：`0xa002d780/784 → 0xa01a37d2(S,0,0,fmt,va)` 内部如何读 `/%s`、读取 suffix 包、调用 S 中函数地址、更新 buf/剩余容量以及返回，均未恢复。尤其调用前 SB0 不能证明调用后 NUL，S+0=0 不能自动认作最终字符计数，count−1 不能自动认证截断规则。有效、分离、NUL suffix 短路径/count256 是可以另登记的具体正常域，不是本轮执行过的输入。

有种子后继：先查 `0xa01a37d2` 已有 retained body 的具体 fmt 入口、`'/'` 字面字符与 `%s` 路径及对 S+4/+8/+c 的间接调用端，再由真实调用约定登记相应必要下层窗口；不要整引擎重导或恢复任意格式。旧 d770 callee metadata 给引擎非连续范围 `[0xa01a37d2,0xa01a40f6)`、`[0xa01a410c,0xa01a4430)`，总3144B，这仅为边界记录，本轮没有读取其 body。新指针种子 `0xa002b536`、`0xa002b4d8`、`0xa002af2e`（count0另有 `0xa002b554/578`）也只留地址，不认证语义或展开。

本轮定位到了实际适配、初始输出和返回透传的差集，未认证实际路径字符串。静态检查39项通过；无新 helper/body 扩展，无生产修改、提交、推送。交付后停止，由管理窗口安排限定复核或后继。
