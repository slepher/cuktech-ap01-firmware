# L04：设置 mode 接入的独立技术复核

2026-10-24；基线 `dbd788a`；独占树/分支 `re0041-l04` / `codex/re-0041-l04`。**限定接受 L03：两 UI 实参、G+2 差异发布、通知 ABI/顺序、旧 writer 服务接入及返回不消费均由独立原字段核对支持。语义纠正0、新增功能0。** 只证明改变 RAM 后通知并尝试写服务，不证明持久化成功、整个设置家族或原 ROM 完整恢复。

使用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，复核者未参与 L03 生产。未运行或导入 L03/L01 脚本；独立标准库代码直接读取原 ROM，解算字段和控制目标。没有共享 REA target/database、固件/SIM/模型/构建/历史回放/设备/外部服务执行，没有输入实验、异常或缺陷验证，没有修改主树、生产代码、ROM、配置、分析器模型或他人文件，无下级 agent。

## 继承结论

|出处|继承范围|本轮必要缺口|
|---|---|---|
|[L03](settings-mode-contract-l03-0041-20261024.md)、[L01](settings-mode-entry-l01-0041-20261024.md)|L03 补充接入解释；L01 只是未验证草稿|独立核字段/ABI/目标与纠正，不将作者自检或草稿作为验收|
|[J03](settings-persistence-reuse-gap-j03-0041-20261024.md)、旧 settings-round2b records[10] / system-complete cached settings|两旧 caller、大 handler、父级设置 UI/ScreenSave/ScreenOff 消费已留存|不重导 handler/资源或重复 ZIP 盘点，不从标题缺失推历史未恢复|
|旧 `whole-rom-private-20261023-071.json`，`ev_cf4c97ae60f1edbe9156a19d0427799c7c068d79ed1d916e7d8cdc3dd61c3c58`|a00ab274 writer 完整旧 body；路径、mode、非零返回臂、写/关闭原序已有|只独立核与本 setter 相连的必要边界，不重做文件服务/NVS|
|[最终应用验收](application-rehost-complete-0041-20261017.md)及 J03 的保存服务分界|SIM 设置/文件事务与跨进程保存已有验收|passed-in-sim 不证明 ROM RAM/文件 ABI、回滚、flash 或真实保存成功；旧通过不重计|

主仓只读前缀为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/`。原件为其 `roms/0041/ap01-1.0.2_0041.bin`，映射 `file_offset=VA−0x9ffff000`。旧 caller、writer 身份与出处直接继承；本轮结果在 [review-result.json](../../analysis/settings-mode-review-l04-0041-20261024/review-result.json)，没有伪造新 REA Evidence ID。

## 本轮复核或纠正

|L03 主张|独立原字段/控制依据|判定与限制|
|---|---|---|
|两正常 UI 输入为 U8/3|`a00fd1d0` LUI rd=s4/upper62fc4000，`d1e8` ADDI +2c；`a00feac4` opcode03/f3=4/rd=a0/rs1=s4/imm1；`feadc` C.LI a0,3；两 JAL 目标均 a00ab478|接受 `62fc402d` 零扩展 byte 与立即数3；不为其他输入或选项赋枚举名|
|UI 不消费 setter 返回|`feacc/feae2` LW local58→a5，随后 C.LI a1=0/1，`fead2/feae8` C.LW a0,8(a5)，再 JAL a018f232|接受。覆盖 a0 前无分支或保存返回，显示调用不构成保存成功反馈|
|旧 U8 与完整 a0 比较，相等直接返回|`ab478/47c` 构成 G=62fc9098，`ab480` LBU a4,2(a5)；`ab484` BEQ rs1=a4/rs2=a0→ab4a6|接受。比较前无 a0 截断，当前 caller 输入已是 U8/3；不研究其他输入|
|差异时先 SB，再通知，再写服务|`ab490` S字段 f3=0/rs2=a0/rs1=a5/imm2；`ab494` C.LI a0,3；`ab496/49a` JAL a00a5bbe/a00ab274|接受 G+2=62fc909a byte 发布与调用原序。helper 两出口只有恢复/ret，无显式成功赋值或失败回滚门|
|通知实参为 callback(node.word4,G,reason)|`5bd6` 首节点来自 list+4，`5bd8` 保存 reason；`5bf4/5bf6` 取 node.word0 并零跳；`5bf8` a0=node.word4，`5bfa` a2=保存 reason，`5bfc` a1=62fc9098，`5c00` C.JALR a5|接受实际三参及零 callback 跳过。传 live G，不是每订阅者复制的快照，也不是异步消息|
|callback 后重读链接偏移|`5c02` LW a5,0(s2=list)；`5c06` C.ADD s1,a5；`5c08` C.LW s1,4(s1)，`5c0a` C.J→5be2|接受按当时 list 首 word 重算 next；没有消费 callback 返回的成功门。节点/登记者身份、所有权、注销及并发协议未核|
|writer 的非零 H 臂与实参|`ab27e..28a` 构成 path/mode 指针，JAL a0134856；`ab292` C.BNEZ a0→ab2c0；保存 H→s1 后调用 a00a46e8，`ab2ce` SH a0,6(a4=G)；`ab2d2..2d8` 构成 `(G,8,1,H)`→a0134adc|接受非零门、低16写 G+6=62fc909e 与四参。8/1只是已核服务实参，不由外观认证精确 libc/单位或校验算法|
|writer 不检查写/关闭结果|`ab2e0` C.MV a0,s1 紧接写返回，再 JAL a01a8de6；`ab2e6` C.J→共同恢复尾声 ab2b6|接受本层返回忽略。写源为通知完成后的 live G；G+6 更新在通知后，不能称通知回调已见本次新 halfword|
|L01 草稿基址原字纠正|独立原件 `a00fd1d0` 为 `374afc62`，字段 rd=s4；`375afc62` 不相同|接受 L03 对未验证草稿的纠正，不算推翻已接受功能或新增恢复；旧稿不改|

`ab49e..4a7` 与 `ab2b6..2bf` 仅恢复保存寄存器、调整栈并返回；这与 L03 对残留 a0 不赋稳定布尔含义的限制一致。旧 writer 的零 H 诊断与公共尾声沿既有 body 继承，本轮未深入诊断或文件服务实现。

本轮事实是原字段、直接/间接调用实参与原序；“尝试写设置”的业务解释由路径/旧 writer 及本次接线共同支持。没有观察任何真实保存、回调执行或设备状态变化。handle 在本次 writer 中保存并传给关闭服务，未核下层完整资源归还保证；G 与订阅 node 的生命周期没有因本次同步调用被扩展或转移。

## 真正新增

新增功能、原件算法、ISA规则、来源认证与整库排除均为 **0**。交付仅为 L03 局部合同的独立限定接受；没有语义纠正。L01 原字错误属于未验证草稿纠正，旧 caller、writer body、设置 UI 与 SIM 验收不重计。

[review.py](../../analysis/settings-mode-review-l04-0041-20261024/review.py) 直接读取原件，以独立实现的 RV32 I/S/B/J 与 C.LI/C.LW/C.MV/C.ADD/C.B*/C.J 字段提取作静态核对：**61条记录、11个 JAL 目标、1个 BEQ、3个压缩条件门、2个压缩直接跳转和2个字符串通过**。原字稀疏记录仅涵盖本题必要连接，没有整 handler/全文件服务导出；未使用 L03 结果 JSON 作原件或运行其检查器。另检查 JSON、报告链接及差异。

## 精确未闭

L01 的三项精确边——两处实参、返回消费、必要下层服务接入——现可按上述局部合同验收；底层实际持久成功仍未证。登记链真实 subscriber/注册注销与节点生命周期、a0134856/a0134adc/a01a8de6 的下层完整返回/所有权实现、a00a46e8 算法、G 全8B的正式结构、真实文件落盘/重启效果仍未知。本题验收范围是两 UI→byte 持有→同步通知→旧 writer 的局部静态接入，不是完整持久化合同。

L03 要求的独立复核已闭合，无需重复同一组窗口。a00a46e8 只是已留存的直接 caller 种子，算法未认证是否构成独立后继须由主窗口先去重裁定，本轮不展开。J03 的 a00ab4a8 备选仍只是另一个真实 caller/extent 种子；本轮未读取或推断其 body，不能凭相邻或等长套用本题。由主窗口先去重再决定后继，不无种子扩 NVS、GUI 或 subscriber 扫描。
