# E16：uv 缓存时间的实际刷新写者

**已定位 `a0098b60(loop)`，并接通实际 source 调用→64位返回→loop+0x140/+0x144 回写→已有 deadline 消费。** source 是 `a019e1a2 → a002696a(1,out8) → a002645a(out8)`；selector 1 跳过 H13 selector 0 的全局偏移合并。单位只获得换算形状，未认证底层 pair 单位或 epoch。新增 ISA/完整业务功能0；真正增量是这条此前 opaque 的刷新接线及其精确断边。

2026-10-24，基线 `d493236`，树 `re0041-e16`，分支 `codex/re-0041-e16`。采用 reverse-engineer-anything 技能。只读主仓原 ROM/留存证据与既有规则文本；没有打开或切换共享 REA target，没有新建数据库，没有运行或修改分析器模型，没有固件/SIM/回放/构建/设备/网络。只写本报告与独占 analysis，未创建下级 agent，待独立技术复核。

## 继承结论：已有→行为→局限→实际缺口

| 已有出处 | 已有行为 | 本轮处理 |
| --- | --- | --- |
| [E14](uv-timer-deadline-e14-0041-20261024.md)、[E15](uv-timer-review-e15-0041-20261024.md) | start 从 loop+140/+144 读64位 now，ADD64 后写 timer+40/+44；dispatcher 按 unsigned64 判断 deadline<=now | 全继承，不重做算术、heap、repeat、callback 或 close；唯一缺口是时间槽生产者 |
| [C07](pogo-close-consume-c07-0041-20261023.md)、[C08](pogo-close-consume-review-c08-0041-20261023.md) | `c172/c174` 以 loop 调 opaque `a0098b60`，随后 `c178/c17a` 调 `a009d304`；另一条 `c812..c81a` 同序 | 已有真实调用种子，不需要扫描全 ROM 字段 |
| [F02](miio-deferred-review-f02-0041-20261023.md)、[F03](miio-loop-close-f03-0041-20261023.md) | s1=loop；caller 栈512 B区域身份及生命周期 | 继承，不把缓存 pair 当成新分配对象 |
| [retained initializer](../../analysis/factory-test-0041-20261023/retained-initializer.json) | `a005a736` 完整留存；初始化 `a005a822` 及调度阶段调用刷新 helper | Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`；只抽必要 caller 锚点，不重导大容器 |
| 较晚 round3 initial bundle `records/5` | initializer callee/target_procedure 元数据已列 `a0098b60..8b93`，以及 `a019e1a2..e1e9` | 是 callee 边界元数据，**不是这两函数的已导出指令/伪码**；后者停在厂商字前，不能据旧边界省略尾部 |
| [H13](weather-clock-abi-h13-0041-20261024.md)、既有 `tooling/scripts/qemu-ap01-cpu.patch:311` | UMAR64 旧规则及 opcode：unsigned32×32 累加至64位偶数寄存器对 | 仅复用规则，不复用天气 selector 0 source、单位或 epoch。本轮 selector 1 由实际原字独立接入 |

round3 的确切范围为主仓 `evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json`；归一化 callee 锚点 `/records/5/normalized_result/callees/27` 与 `/62`，raw/normalized 重复不算多次独立证据。旧 graph `whole-rom-graph-20261023-2881.json` 的 `procedure_callees(a005a736)` 也已有这两个地址，只作复用线索。不声称全历史不存在其他研究。

## 本轮复核或纠正

### 实际刷新入口和双word写回

`a0098b60..8b93` 的 a0=loop，`8b6a:aa84` 保存至 s1。`8b6c:97501000 / 8b70:e7806063` 的 AUIPC/JALR 精确目标是 `a019e1a2`。返回 a0/a1 后，`8b74:37460f00` 与 `8b78:13060624` 构造 a2=0xF4240=1000000，`8b7c:8146` 令 a3=0；`8b7e:ef2048f8` 调 `a001b302`。

`8b82:23a0a414` 存 a0 到 s1+140；`8b86:23a2b414` 存 a1 到 s1+144，然后恢复寄存器并返回。两次32位写有固定低后高顺序；这个局部没有加锁或原子双word指令。它没有检查算术 helper 的状态，没有分配/释放，也不保留局部栈 pair。返回 a0/a1 是所写 bits，但不能因此断言原 C 返回类型必为时间值。

调用接线具有实际原序：`a005c172` a0=s1，`c174` 调刷新；`c178` 再置 a0=s1，`c17a` 调到期分派。`a005c814/c81a` 是另一同序调用点；`a005a822` 已在初始化阶段调用刷新。这里只认证这些静态控制边，不保证每次循环必经、刷新频率、运行时串行化或实时时刻。

### source 的 selector、64位组合与返回尾部

`a019e1a2` 创建0x20 B栈帧；`e1aa:930584fe` a1=s0-18 指向本帧8 B输出，`e1ae:0545` a0=1，`e1b0/e1b4` 调 `a002696a`。返回0在 `e1b8` 直接跳 `e1d0`；非0先调用 `a0019672`，本轮不将该 callee 假定为绝不返回，也不补造错误时间合同。下列只描述 source 返回0的正常路径。

`a0026974` selector&7；`6976/6978` 将1匹配到 `6982`。该处 a0=a1，即上游 out8；`6984:eff07fad` 直接调用 `a002645a`，返回保存 s1，非负在 `698a` 跳 `69f0`，以原返回值返回。源返回0时完整传播0。负返回经已有 errno 分支；本轮未深入 errno helper。selector 1 不经过 `699c..69ec` 的 selector 0 全局偏移相加/归一化。因此 H13 的 `62fc5c74/+4` 不属于这条正常 selector 1 路径的已观察加法。

上游输出 pair[0]/pair[1] 分别由 `e1d4`/`e1d0` 读至 a4/a5。原序先恢复 ra/s0，再令 a0=a5、a1=a5算术右移31，以符号扩展第二word为累加初值。`e1e2/e1e6` 构造 a5=1000000000。`e1ea:7715f7a4` 即 LE word `a4f71577`：opcode77、f3=1、f7=52、rd10、rs1=14、rs2=15，精确匹配既有 UMAR64。两个乘数是单寄存器 unsigned32 a4、a5，累加目的为 a1:a0；不是两对64位寄存器相乘。`e1ee` 归还栈、`e1f0` 返回，均不覆盖结果。

故在继承旧 UMAR64 条款下，真实 source 返回 bits 为：

```c
// 正常路径的局部表达，非原源码；不是原 typedef / 返回类型认证。
uint32_t out[2];
rc = call_a002696a(1, out);         // 实际进入 a002645a(out)
if (rc == 0)
    return_pair_a0_a1(
        bits64(sign_extend_32(out[1])) + (uint64_t)out[0] * 1000000000u);
// a0098b60(loop):
pair v = call_a019e1a2();
pair q = call_a001b302(v.low, v.high, 1000000u, 0u);
store32(loop + 0x140, q.low);
store32(loop + 0x144, q.high);
// 已有实际 caller 之后：call_a009d304(loop)，消费 E14/E15 的期限门。
```

### 单位的证据边界

`a001b302` 入参为分子 a0/a1、常量对 a2/a3=1000000/0；必要窗口可见检查分母高word、unsigned 比较、16位分块的 DIVU/REMU/MUL，以及商位拼接。**unsigned64 除法 helper 是据这组机器形状的强推断，本轮未完整认证其所有正常分支或准确上游库来源，不用函数外观将其排除为标准库。** 证据保留该调用为明确接口，不把 sparse 校核写成完整除法证明。

实际可证换算为“第一word乘10⁹加符号扩展第二word→向上述 helper 传10⁶”。若 `a002645a` 输出秒/纳秒且 helper 为 unsigned64 除法，则缓存为截断毫秒；这两个条件中，前者本轮未建立，后者仍是局部指令支持的推断。因此正式结论保持**单位未认证、epoch未知**，不从天气日志、selector名称、SIM替代或一般 libuv 常识补齐。缓存值与 delay/repeat 同量纲由 E14/E15 加法/比较关联推断，不能给 delay 立即数自行标 ms。

## 真正新增与实际静态验证

新增业务/ISA功能0、模型修复0、新 REA 函数导出0；新增文档接线为真实 writer、source selector 1 的直接底层分支、UMAR64 的本地实例及双word缓存写回。旧 initializer/dispatcher 的读写与调用原序复核不重复计入新增。round3 对 source 的旧边界截在 `e1e9`，本轮核到旧 UMAR64 字及 `ret`，不接受截断边界为完整返回合同。

运行 [verify.py](../../analysis/uv-time-producer-e16-0041-20261024/verify.py) 通过，结果 [verification.json](../../analysis/uv-time-producer-e16-0041-20261024/verification.json)：10个直接调用目标独立提取立即数，8个有界窗口原 ROM 解码，1个 UMAR64 字段精确匹配旧文本规则，5个旧 initializer caller锚点回源；round3 元数据按地址去重为2项。ROM路径为主仓 `roms/0041/ap01-1.0.2_0041.bin`，VA映射 `VA-0x9ffff000`。脚本不运行规则或算术输入，不导出整ROM，不作全ROM字段扫描。`git diff --check` 通过；结果仅为作者静态验证，非独立验收。

## 未闭精确边与一个后续闭包

已闭：真实刷新函数身份、输入 loop 保存、source 调用、正常 selector 路径、64位组合和两个word回写，以及回写后已有 dispatcher 的同一 loop 读取。仍未知：`a002645a` 的原始来源/输出单位/epoch，`a001b302` 完整除法合同及准确来源，真实刷新频率和并发保证。没有开展失败/异常输入实验，没有恢复 heap、callback、close 或全 loop。

后续只建议沿已定位 `a002645a(out8)` 正常输出核 pair 单位/原始来源，再据需要认证明确算术接口 `a001b302`；selector 0 的 offset 写者可由天气线另行处理，不能合并二者的 clock 身份。本轮到缓存生产者接线及单位精确断边交付即结束。
