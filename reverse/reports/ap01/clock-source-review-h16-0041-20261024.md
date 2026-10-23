# 0041 H16：底层时间 pair 与来源强度独立复核

接受 H15 的正常局部合同：`a002645a(a0=out8)` 单次读取 `62fc6c64` 的32位值，以 DIVU/REMU 1000 拆分，再把余数乘1000000，顺序写 `out+0/+4` 并返回0。候选只支持秒/纳秒表示形状及条件性的输入刻度解释；不认证计数器实际节奏、epoch或offset写者。没有需要纠正的技术结论，新增功能0、ISA规则0、完整函数导出0。

基线 `e2991b9c7c3af7db4208647b24f6c53888ebc1cf`，独立树 `re0041-h16`、分支 `codex/re-0041-h16`。使用 reverse-engineer-anything 技能，只读主仓 ROM、已有证据和本地候选必要行；未打开共享 REA target，未建数据库、执行固件/模型/SIM/构建/历史回放、连接设备或外网，未创建下级 agent。只写本报告与独占 analysis，不改主树共享索引、生产ROM、配置或模型，不撤销其他 agent 改动。

## 继承结论：已有 → 行为 → 局限 → 精确缺口

|已有出处|行为与局限|处理|
|---|---|---|
|[H15](clock-source-offset-h15-0041-20261024.md)，其 static-result.json、candidate-excerpts.json|正常单次加载、无符号拆分、两word同步输出已恢复；来源与单位严格保留条件|本轮只核这些局部事实及证据强度，不算新增功能|
|H15引用的 inventory/extent/direct-calls Evidence `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2`、`ev_2c7008f9ddabbba2c7d0f277da376c3b80417efa25d9f114fa0d6e3f4dddf067`、`ev_e2f3c4c8b2774c6ad186efd9a57adff5dcdc63a5c77cd3e04fd4740ffe57396f`|函数边界 `a002645a..a002648b`、无direct callee；不是来源dossier|继承边界；原件窗口与H15逐byte一致，未重新请求REA导出|
|[H13](weather-clock-abi-h13-0041-20261024.md)、[H14](weather-clock-review-h14-0041-20261024.md)|selector0正常调用底层后合并 `62fc5c74/+4`，signed上界检查后单次进位；天气换算/UMAR64/URL接入已有|继承，不重导上层，不把下层细word范围用作未知offset的全局保证|
|[E16](uv-time-producer-e16-0041-20261024.md)|selector1直接调用同一下层，跳过selector0 offset合并；返回组合、uv缓存写者已有|继承其接线，不重新核除法helper完整算法，不混同两个ID的epoch|
|H15的旧complete/ZIP/SIM与限定留存目录查询|宿主服务替代不认证ROM来源；文本无命中不等于ROM无writer|继承局限，不重查ZIP、不扩大为全ROM writer搜索|

精确复核缺口仅为 H15 的正常输出合同是否可接受，以及候选证据是否被过度提升；二者均得到有边界答案。

## 本轮复核或纠正

原件为主仓 `roms/0041/ap01-1.0.2_0041.bin`，VA映射 `VA-0x9ffff000`。复用了 H15 的44B窗口，仅将它与当前原件比较；未另存整函数。独立字段校验与稀疏ABI锚点见 [static-review.json](../../analysis/clock-source-review-h16-0041-20261024/static-review.json)。

|逐项主张|独立依据|判定|
|---|---|---|
|入参为调用者8B输出区域|`645a:4111 / 645c:22c6 / 645e:0008` 只建帧保存s0，a0未被覆盖；`647c:14c1` 与 `6482:5cc1` 分别存a3至0(a0)、a5至4(a0)|接受正常指针ABI；8B是两次32位输出范围，不声称原typedef|
|只读一次32位计数值|`6460:b777fc62 / 6464:83a747c6` 的 LUI/LW字段有效地址 `62fc7000-39c=62fc6c64`；后续两次算术共享a5，窗口内无第二次全局load|接受；LW在RV32得到32位bits，后续unsigned操作决定无符号解释|
|无符号除余1000|`6468:1307803e` 置a4=1000；`646c:b3d6e702`、`6470:b3f7e702` 独立确认 opcode33/funct7=1、funct3=5/7，rs1=a5、rs2=a4|接受 DIVU a3,a5,a4 / REMU a5,a5,a4，不是两次读取或signed除法|
|余数乘1000000后写细word|`6474:37470f00 / 6478:13070724` 构造 `f4000+240=1000000`；`647e:b387e702` 为 MUL a5,a5,a4|接受低32位MUL；余数0..999，最大999000000，不发生32位截断损失|
|写入顺序、返回及所有权|粗word在MUL前写入，细word随后写入；`6484:3244 / 6486:0145 / 6488:4101 / 648a:8280` 恢复s0、a0=0、归还帧、ret|接受。无callee、heap分配、指针保留或所有权转移；同步写调用者buffer后返回|
|秒/纳秒候选形状|本地 `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/nuttx/sched/clock/clock_systime_timespec.c:62–87`、`include/nuttx/clock.h:343–351` 必要行与H15留存逐行一致|接受局部类比，未重新认证版本或ROM宏配置|
|单位/来源强度|候选 source 的普通分支调用 `clock_ticks2time(ts,g_system_ticks)` 并返回0；宏先保存tick，再求tv_sec与tv_nsec。ROM常数对应每秒1000输入单位时的形状|接受H15条件限定：若输出解释为秒/纳秒，输入每数值单位对应1ms；没有实际writer或时序证据，不能说ROM每1ms必递增|
|offset与两ID区别|H13/H14/E16已有上层连接直接继承；候选 clock_settime 只能作未绑定的writer假设|接受未认证状态；本轮不把候选符号、上电注释或REALTIME名称绑定ROM地址|

必要行为表达（非原源码）：`t = load_u32(62fc6c64); out[0] = t / 1000u; out[1] = (t % 1000u) * 1000000u; return 0;` 两word是拆分数值表示，不能直接当连续64位计数bits。无新增纠正；对“毫秒输入”的接受始终以秒/纳秒解释为条件。

## 真正新增

新增功能0、ISA规则0、完整函数导出0、来源版本认证0。独立字段、9条稀疏ABI/返回指令及两处候选源行核对均为旧结论复核，不把验证工作重复记作功能恢复。H13/H14/E16上层、旧资源/服务、offset writer及计数器writer未重新恢复。

## 未闭精确边与后续闭包

仍未核：`62fc6c64` 的实际ROM写者、更新节奏/计数起点/epoch、硬件timer身份、ROM精确来源版本；`62fc5c74/+4` 的真实ROM写入函数/调用点、初始化与校时政策；两个selector正式接口命名。源码候选、天气换算或uv消费不能代替这些证据。本轮没有全ROM常量/字段搜索，没有执行异常输入或时间回放。

单一后续闭包：只有出现 retained xref/命名合同指向实际 `62fc5c74/+4` ROM writer地址和调用点时，再核请求pair、source bias及两word保存原序/宽度；当前按无真实种子的定位断边停止，不从邻近函数猜writer。

实际运行 [verify.py](../../analysis/clock-source-review-h16-0041-20261024/verify.py) 通过：H15窗口与原件一致，独立普通指令字段/常数、9条稀疏锚点、两处本地源行区间与留存一致。脚本只做字节与文本检查，没有运行ROM或模型。初次脚本路径计算已修正；受限shell中的WSL读取失败后，仅提升执行同一静态核验以读取本地候选，最终通过。`git diff --check`、报告相对链接检查通过。本次技术接受只覆盖H15所列正常局部合同与证据强度，不宣布完整时钟来源闭包。
