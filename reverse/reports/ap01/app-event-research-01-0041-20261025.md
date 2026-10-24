# Q-19：cmd.event 输入持有、单项 flush 与本层归还

0041；作者静态研究，待非作者复核。分支 `codex/app-event-research-01-20261025`，启动基线 `841a7a194a9ecdd02935d429c2cdc57e68ae5ab8`。本阶段已恢复 borrowed name/argv 到独立记录、即时旁路提交、flush 选取与描述符交接、本层正常归还。外部提交是否复制 payload/descriptor、callback 消费、实际网络送达及并发结果未闭合；root 的 `ok` 仅依赖记录函数返回零。

## 证据与范围

- 主仓绝对根：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware`。原件 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，继承 SHA-256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射 `offset = VA - 0x9ffff000`。本轮只核长度，不重新制造整件摘要。
- 已验 root 卡：主仓 `evidence/rea-0041-20261017/evidence/upper-miio-a.md` §0xa00ba444，Evidence `ev_a443a9d8aa26648e225c4f146153d31ea375d78457793653893e2aac63e5e293`。真实 root：同目录 `upper-complete.evidence.json#/records/233/normalized_result`，Evidence `ev_b7f9c05652b41f5486cbdecf96f07079792f9d25bf48dcfb216ec0448259d9a0`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`；两份不同来源/profile分账，未混作一次分析。
- 管理 Q-19 登记、upper 领域卡及较晚报告精确地址搜索：四 callee 旧覆盖为 extent/directcall，本轮补业务 body。Q15 UI 数组、Q18 staged-property 对象及 F11 loop 不作本对象身份证据。未修改主树/管理表。
- [原窗提取脚本](../../analysis/app-event-research-01-0041-20261025/extract.py)固定四窗 `a011408a..4149` 192 B、`a0113f6c..4089` 286 B、`a011c204..c3af` 428 B、`a01af798..fa2b` 660 B，共1566 B。离线 Capstone5.0.7/RV32/RVC，逐条保留 raw；无新 REA Evidence ID，不借 root profile为新解码背书。忽略产物 `raw.json`、`inherited-root.json`、`checks.json` 留同名 analysis 供转存。
- 厂商九字按主仓只读 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 精确规则拆字段；不执行或修改模型，不认证原厂 ISA 来源。原 decoder 的 UNDECODED 保留，补义只限本报告列出的 `th.lrw/srb/lwia/mvnez`。

## 输入与持有

`a011408a(C,name,argv,n)`：`a01140a6` unsigned `n>16`、name空、`strnlen(name,32)+5>32` 均返回−10；正常 name 最长27 B，后续格式 `event.%s` 最长32 B加NUL。`a0060296(name)` 非零原样返回；零时逐项读取 `argv[i]`（`a0114126` 原字 `8bca9b44` = `th.lrw s5,s7,s1,2`），累加 `strnlen(arg,901)`，总和大于900或 `a0062568(arg)` 非零返回−10。这些是正常输入验证调用合同，不深入验证器/异常输入。

验证全过，先调用 `a011c204(C,name,argv,n)`；其返回不控制后续。随后 `a005f3d8(word(C+0xe4),−1)`，调用 `a0113f6c(C+0xdc,name,argv,n)`，保存返回值，再 `a01b3c8c(word(C+0xe4))`，最后返回保存值（`a01140e6..4124`）。锁服务返回未被判断；本层顺序不能单独证明并发安全。

令 `H=C+0xdc`，`R` 为 owned event record。`a0113f6c` 从 `word(H)` 沿 `+0` 遍历至哨兵，预存记录数大于15即返回−3。否则先算 `S=sum(strlen(argv[i])+1)`，调用分配服务 `a0058386(1,0x88+S)`，空返−5；本层无更晚失败出口。以该 zero-allocation API 合同为前提，默认字段保持零；本轮未展开分配器内部。

|R相对偏移|写入/消费合同|
|---|---|
|+0,+4|intrusive next/prev；`a0113ffe..400c` 尾插H，显式写四个双向链接|
|+8..+0x28|formatter `a002d7fc(R+8,0x21,"event.%s",name)`；原name地址不入记录|
|+0x2c..+0x68|最多16个argv指针，均指向本次分配尾部 `R+0x88+offset`|
|+0x6c|argc=n|
|+0x70|显式byte清零；flush序列化成功后置1|
|+0x74|flush选用的request id；只在序列化成功后写|
|+0x78|`a005fa36()`返回word；JSON键timestamp|
|+0x7c|`a005f9e2()`返回word；JSON键tick及过期检查输入|
|+0x80|显式写0x1b7740；与 `a005fa54(R.tick)` unsigned比较；不凭名称推时间单位|
|+0x84|flush读为signed retry，JSON键retry；本四窗无增量写，初始化依赖zero-allocation API|
|+0x88起|argv字符串逐个复制 `strlen(arg)` B，再显式NUL；每项尾部间隔strlen+1|

复制原字关键点：`a0114044/4066` 为 `argv[index<<2]` 读取；`a0114062` 调copy；`a0114074` `0bd0a700` = `th.srb zero,a5,a0,0`，在目的+strlen处写NUL；`a0114078` `0b454b58` = `th.lwia a0,s6,4,0`，读当前pointer槽后将槽指针加4。尾部偏移再按strlen+1前进。成功返回0，不保留root的borrowed切片或borrowed pointer数组。

## 即时旁路提交

`a011c204` 单独取 `id=a0110984(C)`，申请0x558 B临时payload P；失败直接返回，不影响随后记录路径。将 `event.%s` 写栈内33 B名字，初始化 builder `{P,0x558,0}`；组织 `id`、`method`、`params`（各argv按原始token文本追加），关闭数组/对象。name经string builder，argv经raw-token builder；不把原始token都改成JSON字符串。

`a00602e6(&builder,0,&length)` 非零只走诊断/释放；零则 `a01ac1c4(&D)` 初始化栈描述符，再写 `D+4=id`、byte `D+0x10=0`、`D+0x20=length`、`D+0x24=P`、`D+0x2c=0xa0116db0`、`D+0x30=0`。另一栈对象K清零0x58 B，byte0=6、K+4最多31 B复制原name，K+0x23显式NUL。调用 `a011c0da(C,&D,&K)`；其返回不被使用。随后释放P（`a011c348..34a`），描述符/名字/K均随栈消失。

因此本层已证明提交的payload为临时owned buffer，并在调用返回后回收；callee是否在返回前复制/完成使用仍未知。本层也未把即时提交成功作为record返回0的条件。callback `a0116db0`只记录地址与ctx=0，不读其body。

## flush选择、交接和归还

`a01af798(C)` 先申请0x559 B P，空直接返回；builder容量0x558。先取 `id=a0110984(C)`，随后锁 `word(C+0xe4)`。从H首项遍历，预读next，行为如下：

1. byte `R+0x70 !=0` 跳过。否则若 `a005fa54(word(R+0x7c)) >= word(R+0x80)`，调用 `a006929a(R)`后立即 `a002e14e(R)`，继续；节点服务内部不展开，不能只由本body声称四链写细节。
2. 若signed `R+0x84 >0`，读R+0x74；`a01af840` 原字 `0b99f742`为 `th.mvnez s2,a5,a5`：旧id非零才替换当前id。这个s2随后沿遍历保留；不能简化成每记录必取新id。
3. builder `{P,0x558,0}` 写id、method=R+8、params=R内owned argv原token，以及retry、timestamp、tick三整数。`a00602e6(&builder,0,&length)` 非零继续下一节点；本轮不标该节点pending，也不释放它。
4. 首个序列化成功节点写word `R+0x74=id`、byte `R+0x70=1`，停止遍历并解锁。没有合格节点也解锁，直接释放P。
5. 有成功节点时，解锁后 `a01ac1c4(&D)`，再写 `D+4=id`、byte `D+0x10=0`、`D+0x20=length`、`D+0x24=P`、`D+0x2c=0xa0116b5a`、`D+0x30=C`。调用 `a0113340(C,&D)`。
6. submit返回非零：重新锁，调用 `a0116ad0(H,id,0)`，再解锁。submit返回零不调用此恢复服务。本四窗不能证明恢复服务删记录、清pending或改retry，必须保留callee断边。
7. 两种返回均 `a002e14e(P)`，函数void返回；R不在正常交接路径直接free。只在上述过期分支本层free R。一次flush最多交接一个序列化成功节点。

同一P既是builder首字段又是提交D+0x24；D为栈对象，submit返回后P释放。因此外部submit的复制/持有时机、callback触发时机/同id匹配及C寿命都是必要外部合同。不能套F11 loop，也不能推“异步队列必持有这份P”。root调用flush后即输出ok；flush的分配/序列化/submit失败不会改root的零返回判断。

## 交付检查与未闭边

[静态复验](../../analysis/app-event-research-01-0041-20261025/verify.py) PASS：4窗1566 B、508条指令raw覆盖、20个JAL或AUIPC/JALR原字目标、9个vendor字字段与只读规则、7个精确NUL字符串。第一次手算节点服务目标误写a006529a，raw-call断言发现后修为 **a006929a**，最终检查通过。未运行固件、模型、SIM、QEMU、回放、构建、设备或外部服务；没有新REA会话。

阶段可独立用于重建：borrowed输入验证边界→owned记录及双链→单项JSON交接→本层临时资源回收/过期记录释放。仍需外部合同：`a011c0da(C,&D,&K)`、`a0113340(C,&D)`的复制与返回语义；callback `a0116db0`/`a0116b5a`消费者；`a0116ad0(H,id,0)`恢复语义及retry变化；C初始化/终止与并发；实际传输/云接收。上述不阻碍本层阶段陈述，但不等于完整event接口已验。

时间：首个可获得UTC `2026-10-24 17:19:36 UTC`在初始读取后；结束见analysis/checks.json。初始读取未计时，不能把该区间冒作全任务耗时或有效计算时间。工具等待未独立采样，无人为sleep；token数据不可得，不估算。
