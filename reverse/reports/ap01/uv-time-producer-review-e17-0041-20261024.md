# E17：uv 缓存时间生产者独立技术复核

**限定接受 E16 的实际 writer → ID1 source → UMAR64 返回 pair → 常量除数接口 → loop+140/+144 → dispatch 前消费接线。语义纠正0，新增功能0。** `a001b302` 仍是局部指令支持的 unsigned64 quotient 推断，不能写成完整除法算法或库来源已认证；单位和 epoch 不强认。

2026-10-24；基线 `e2991b9`，独立树 `re0041-e17`、分支 `codex/re-0041-e17`。采用 reverse-engineer-anything 技能。复核者独立于 E16 作者；主仓原 ROM、旧条款只读，未打开或切换共享 REA target，没有新数据库，没有运行或修改模型、固件、SIM、构建、历史回放、设备或网络。只写本报告和独占同名 analysis，不创建下级 agent，不改主树共享文件，不撤销其他任务修改。伪代码是机器合同表述，不是原源码。

## 继承结论：已有 → 行为 → 局限 → 实际缺口

| 已有出处 | 已解释行为及证据局限 | 本轮处理 |
| --- | --- | --- |
| [E16 报告](uv-time-producer-e16-0041-20261024.md)及其 `verification.json` | writer/source/selector1/返回尾部与调用顺序已恢复；完整除法及单位未认证 | 对关键接入 ABI、宽度、厂商字和回写原序独立核原字；不执行 E16 脚本，不把其 JSON 当本轮原件 |
| [E14](uv-timer-deadline-e14-0041-20261024.md)、[E15](uv-timer-review-e15-0041-20261024.md) | start 用 loop+140/+144 加 delay；期限写 timer+40/+44；dispatcher 用 unsigned64 deadline<=now | 全继承，不重做 ADD64、heap、repeat、callback、close；本题只接生产者到已有消费者 |
| [H13](weather-clock-abi-h13-0041-20261024.md)、[H14](weather-clock-review-h14-0041-20261024.md) | ID0 合并 offset，细 word 单次有条件进位；天气两次 signed32 DIV 和 UMAR64 接入 | 全继承；不把 ID0 offset、天气消费者或来源/epoch 套给 ID1 |
| [H15](clock-source-offset-h15-0041-20261024.md) | `a002645a` 从一次32位读取生成 `t/1000` 与 `(t%1000)*1000000` 两word，返回0；无下层 callee | 直接引用其新下层合同，不重复导出或独立验收内部。候选秒/纳秒语境与实际 counter writer/节奏/epoch仍有区别 |
| E16 所列 retained initializer，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3` | initializer/同一 loop 调用种子和初始化刷新点已有；round3 callee 元数据不是完整指令导出 | 继承旧范围，不重复历史目录、ZIP、whole-ROM 搜索或大容器导出；本轮只独立检查两组 refresh→dispatch 调用锚点 |
| 旧 `tooling/scripts/qemu-ap01-cpu.patch:311` 的 UMAR64 条款 | 单寄存器 unsigned32 乘数，累加到偶/奇目的对，模2^64 | 只读旧函数内部取源/乘法/累加/写回条款，不运行模型；不提升为厂商原版规范认证 |

实际缺口仅为 E16 接线的独立技术接受与精度边界；不是重新恢复下层 clock 或全 loop。

## 本轮复核或纠正：逐项判定

本轮从主仓 `roms/0041/ap01-1.0.2_0041.bin` 稀疏读取，映射 `offset=VA-0x9ffff000`。独立提取标准 JAL/AUIPC+JALR、B 分支及 word 访存字段；必要压缩指令核原字和普通解码。过程与结果见 [review.py](../../analysis/uv-time-producer-review-e17-0041-20261024/review.py)、[review.json](../../analysis/uv-time-producer-review-e17-0041-20261024/review.json)。这些是本轮原件校核记录，不冒称新 REA Evidence ID。

| E16 主张 | 本轮原字/字段锚点 | 判定与接受范围 |
| --- | --- | --- |
| writer 保存同一 loop，调用实际 source | `8b6a:aa84` 保存 a0→s1；`8b6c/70` AUIPC/JALR 精确到 `a019e1a2` | **接受**。a0=loop 身份继承既有 caller；本轮核保存与直接调用，不扩展完整 loop |
| source 用调用者帧内 out8 和 ID1 | `e1a2:0111`、`e1a8:0010` 建0x20帧并使s0指向原sp；`e1aa:930584fe` 为 a1=s0−18；`e1ae:0545` 为 a0=1；`e1b0/b4` 精确到 `a002696a`；`e1b8:01cd` 为成功0跳 `e1d0` | **接受正常成功路径**。局部 pair 位于新sp+8/+c，不分配heap、不保留指针。非零调用 `a0019672` 的错误合同沿 E16 未核，不断言其绝不返回 |
| ID1 跳过 ID0 offset 合并 | `6974:1d89` selector&7；`6976:8547` 置1；`6978:6305f500` BEQ x10,x15→6982；`6982:2e85` a0=a1；`6984:eff07fad` 到 `a002645a` | **接受**。ID1直接进入下层，与 ID0 的 offset 路径分离；H15 负责下层内部，未重复核 |
| 下层0状态传回正常 source | `6988:aa84` 保存返回a0→s1；`698a:63d30406` BGE x9,x0→69f0；`69f4:2685` a0=s1 | **接受**。下层0按原值返回0，上层取正常输出。负返回/errno业务合同未核 |
| pair加载、累加初值和常量 | `e1d0:8327c4fe` 为 lw a5,−14(s0)，`e1d4:032784fe` 为 lw a4,−18(s0)；`e1dc:3e85` a0=a5；`e1de:93d5f741` 算术右移31置a1；`e1e2/e6` 合成a5=10^9 | **接受**。第二word先被符号扩展为a1:a0；第一word是a4单寄存器乘数。恢复ra/s0的两条在准备返回值之前，不覆盖a4/a5 |
| UMAR64 与尾部返回 | `e1ea:7715f7a4`，LE word=`a4f71577`；op77/f3=1/f7=52、rd10/rs1=14/rs2=15；`e1ee:0561` 归还帧，`e1f0:8280` ret | **接受既有条款实例**。unsigned32(a4)×unsigned32(a5) 加至a1:a0；不是64×64乘法。旧条款独立核了单寄存器取源、mulu2、add2和两word写回；尾部不覆盖返回pair |
| 除数与 helper 接口 | `8b74:37460f00`、`8b78:13060624` 合成a2=10^6，`8b7c:8146` a3=0；`8b7e:ef2048f8` 精确到 `a001b302`；`b35a/b368/b36e` 分别核为 DIVU/REMU/MUL | **接受接口和受限推断**。分子a0/a1来自source，分母a2/a3=10^6/0。稀疏 unsigned 算术支持商解释；未证明完整CFG、所有正常分支或准确库来源，不能标为完整算法验收 |
| 低后高写回，同一loop刷新后分派 | `8b82:23a0a414` sw a0,140(s1)，`8b86:23a2b414` sw a1,144(s1)。`c172/c178` 均a0=s1；`c174/c17a` 分别到writer/dispatcher；`c812/c818`与`c814/c81a`为另一组同序锚点 | **接受**。两个32位写按低后高顺序，把helper返回bits接给E14/E15既有读取。仅认证这两组静态原序；不保证每圈必经、频率、双word原子快照或外部串行化 |

全部8项在上述边界内接受。语义纠正0；“除法”仍带 E16 已有推断限定，不因本轮接受而升级。源返回pair与缓存写入可表述如下，**不是原源码**：

```c
// a002696a(1, stack_out8) == 0 的正常路径
pair v = bits64(sign_extend32(out[1]))
       + unsigned32(out[0]) * unsigned64(1000000000); // 既有UMAR64，模2^64
pair q = call_a001b302(v.lo, v.hi, 1000000, 0);      // quotient解释仍受限
store32(loop + 0x140, q.lo);
store32(loop + 0x144, q.hi);
// 两个已核caller随后重新把同一loop置a0，再调a009d304。
// 期限相加/unsigned64到期比较完整继承E14/E15。
```

这里没有新增对象或所有权转移。out8属于source调用帧，下层同步写入；值经寄存器返回后复制到已有loop字段。loop/timer的生命周期和清理由继承合同管理，不能从本题两次word写推出额外锁或资源责任。

H15 已使 E16 的“下层数值表示未知”不再是当前整体状态：本轮引用其 `t/1000` 与余数乘10^6合同；该继承支持秒/纳秒和输入数值每单位1ms的候选解释。它仍未认证真实计数写者或节奏，且本轮未完整认证除法helper，所以不把公式、通用libuv常识或天气 `%lld` 反推成已认证的实际毫秒/单调时钟/epoch。ID1未走offset合并，并不证明整个运行期无其他时间调整政策。

## 真正新增与实际静态验证

**新增功能恢复0、ISA规则0、模型改动0、完整函数导出0，E16语义纠正0。** 新交付仅为独立限定接受及本路稀疏证据。H15 新合同只作继承，不重算成果；E14/E15与H13/H14不重复验收。

运行 `python -X utf8 -B reverse/analysis/uv-time-producer-review-e17-0041-20261024/review.py`：PASS，36条稀疏指令（其中4条word访存、2条selector分支、1条UMAR64、3条DIVU/REMU/MUL的字段独立提取），另8个直接调用目标独立提取。脚本只读原件和旧条款，写本路 `review.json`，不调用E16验证脚本、不运行算术输入或模型、不读取H15下层原字。报告相对链接检查和 `git diff --check` 通过。厂商语义解释仍依赖既有私有条款，未作硬件或原版ISA认证。

## 未闭精确边与一个后续闭包

未核逐项保留：`a001b302` 完整 unsigned64 quotient 合同/准确库来源；`62fc6c64` 实际writer、节奏/起点、真实物理单位和epoch；`62fc5c74/+4` offset写入源（H15已明确停边）；错误返回后的业务合同；真实循环刷新频率、串行化、双word读取快照及callback时刻。E16旧边界不再承担H15已闭的下层数值表示缺口，但这些未知不因此消失。

单一后续闭包建议：若需要把当前数值换算提升为精确quotient合同，可只对已定位 `a001b302` 的正常调用相关分支补齐商返回证明并先复用留存；不重启下层/天气/heap/close，不自动扩题。E17所需接线独立复核已闭，按限定接受交付结束。
