# B25：cmd56 的 item+18 写入接入合同

**正常有效 item 路径中，`a00a991c` 的目的确为 `load32(load32(62fcb2cc))+index*1a8+18`，与 B22/B23 的 cmd51 半字读者属于同一总对象/数组/索引布局。cmd56 在 len 精确为13、整12B内容比较不同后，将 payload+1 的12B原位复制到 item+18；首半字随整个区间一同覆盖。** 这不是新增 SH 指令或原子半字写合同；物理单位与两条命令的实际生产先后仍未知。

2026-10-24；基线 `565dc6e`，独占树/分支 `re0041-b25` / `codex/re-0041-b25`。用户明确恢复覆盖旧冻结条款，其余共同限制保留。使用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，仅本地静态原件/旧证据读取；未打开共享 REA target/database，未运行固件、模型、SIM、构建、历史回放、设备或外部服务，未作漏洞/异常输入/缺陷验证，未改生产代码、ROM、配置或分析器模型。没有下级 agent、全函数导出、全资源/源码复制或机械哈希账。伪代码是分析表达，非原源码。研究者自检待新独立 agent 技术复核。

## 继承结论

| 既有出处 | 已解释行为/局限 | 本题处理 |
|---|---|---|
| [B24](cmd51-item-field-producer-b24-0041-20261024.md) | 98d0..991c 是未复核候选，未认证 same-item writer | 仅补其指令/字段、正常对象别名及写入时序，不能把 B24 线索当既有验收 |
| [B22](cmd51-device-type-b22-0041-20261024.md)、[B23](cmd51-device-type-review-b23-0041-20261024.md) | cmd51 每轮重读 total/count/array，三个二级 ID 从当前 item+18 以 LHU 读 h；分类、低16位域门和阈值已独立接受，生产者/单位未核 | 分类树直接继承。本题只核建立同址所需的93c6/93ec..9404锚点，不再认证全部分类 |
| [E01](uiiface-item-ownership-e01-0041-20261023.md)、[E02](uiiface-ownership-review-e02-0041-20261023.md) | 总对象62fcb2cc、首word数组、u8 count+6、item步长1a8；零初始化、失活清零、五指针生命周期及通知借用 ABI 已接受 | 直接继承；零填充不算新 writer，内联12B区域不是嵌套缓冲区指针 |
| [旧 UART 应答报告](uart-response-0041-20261023.md) | 已保存正常 cmd56 len13、内容变化时复制12B的历史回放观察；夹具与其他范围不证明当前 ROM 合同 | 只引用已有正常观察，不重跑回放、不采用异常用例作本题证明；copy存在本身不算首次发现 |
| [application complete](application-rehost-complete-0041-20261017.md)、[J01](charge-reuse-gap-j01-0041-20261024.md)及最终SIM边界 | 充电/服务主体早已 passed-in-sim；硬件协议等为服务替代，非原ROM完整运行或 ABI 验收 | 不重开整UI或分类，不把 SIM 成功当物理单位/协议证据 |
| `buzzer-backlight-0041-20261023.json#/functions[address=0xa00a8582]` | 旧完整6044B dispatcher原字节/汇编/伪码已经留存，Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c` | 原件稀疏窗口与旧raw一致；只留必要接入，不重新导整个函数 |

四份旧 charge/system complete、charge-round4、page-logic 对 `a00a98d0/a00a991c/UiIFaceMngBmsChange/DCap` 的精确词项有界查询未命中，见 [reuse.json](../../analysis/cmd56-item-field-contract-b25-0041-20261024/reuse.json)。这些无命中不证明历史未分析，也不覆盖所有旧成员；已有 UART 观察和近期合同优先继承。

## 本轮复核或纠正

原件只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA−9ffff000`。[evidence.json](../../analysis/cmd56-item-field-contract-b25-0041-20261024/evidence.json) 保存必要原字、字段、目标和局部规则来源。B24 没有已认证行为需要纠正；本轮把其候选提升为如下受限合同，不重新计旧 copy/比较库、通知 ABI 或分类功能。

| 原字锚点 | 已核正常行为 | 限定 |
|---|---|---|
| 85ba `b284`；860a/860e/8612 | s1 保存入参 payload；cmd==56 跳98d0 | dispatcher入口 `(cmd,len,payload*)` 沿 E01；本段无新的返回值合同 |
| 98d4 `2388072e`；98d8 `b547`；98da `639ef51c` | 先 SB 清62fcb2f0，再比较原a1与13；不等去9ab6 | 写入发生在精确 len==13 的分支；不分析其他长度路径或外层帧 |
| 98e2 `03a9c72c`；98e6 `83490600`；98f0/98f4 | total=load32(62fcb2cc)，index=LBU payload[0]；正常 total非零且index<u8(total+6)到98f8 | count比较是 BGEU，索引为零扩展byte。本文只认证此有效item路径，不验证其他分支行为 |
| 98f8/98fc；9900 `0b99f920`；9904 `6109` | array=load32(total)，stride=1a8；mula s2,s3,a5 后加18，得到 D=array+index*1a8+18 | mula字段 op0b/f3=1/f7=16/rd18/rs119/rs215，与已有局部 `rd+=rs1*rs2` 规则相容；私有模型不是独立厂商规范 |
| 9906..990e；9912 `6302051a` | S=payload+1，`compare(S,D,12)`；返回0跳9ab6，非零继续 | 比较沿 E01/E02 的0相等合同；比较顺序是源在前、目的在后。不要求首半字自己有差，只要求12B任一差异 |
| 9916..991c | a0=D、a1=S、a2=12，调用既有 `a000589c` 字节复制 | 沿既有copy接口覆盖 `[item+18,item+24)`；并未核/重导1080B优化复制算法，因此不声明底层每次store的宽度、次序或原子性 |
| 9920..9938 | copy返回后重读62fcb2cc/count/array；再用同index及1a8偏移定位当前item | 复制前缓存 D 与复制后当前数组分开；不能用静态正常身份推断跨调用的稳定性/线程串行化 |
| 993a/993c；9940 `0bc6e640`；994a/994c `0bd6e640` | 以word加载当前item+0，OR 0800，再word写回 | 这是保留旧mask的 OR；不是 E01 cmd52 的直接赋值。indexed load/store字段与局部lrw/srw规则相符，shift0 |
| 9950/9954/9958；997c；9980/9982 | 取当前item+1a/+18/+1c 的 LHU 值作日志参数，然后 `a00a389c(index)` 同步通知 | 日志在copy/置mask后、通知前；通知清mask/借用责任沿 E01/E02，不另称新恢复 |

同址证据不是只比字面“+18”：cmd51 的93c6/93ec读取**同一个全局62fcb2cc**，93f0读取同count+6，9400取得其首word数组，93f8/93fc/9404按同1a8乘数与当前index形成 item；B23 已接受96b4/96e4/9708 的 LHU item+18。因此在同一 total/array 实例与同一 index 下，cmd56目的的前两字节就是 cmd51 的 h 来源。它们是同对象族同字段的直接连接，不是cmd51的8B record+18，也不是新独立分配。跨不同响应时 total/array 是否仍相同，不由地址公式保证。

ROM原字节的日志字符串 `a0269760` 为 `UiIFaceMngBmsChange = %d, DCap=%d,FCap=%d,RCap=%d`，函数名字符串 `a026a3b8` 为 `UiIFaceMngBmsChange`。参数a6来自item+18、a7来自+1a、栈第九参来自+1c，故可把 h 描述为日志的 **DCap 数值**；这支持容量类分析命名，但没有单位字符串/缩放操作，不能认证 mAh、Wh、比例或真实电池语义。

## 真正新增

真正增加的是 B24 候选到 B22/B23 既有半字消费者的对象/字段接线，以及精确 len门、整12B变更门、copy→重读→mask OR→日志→通知的静态顺序解释。旧 dispatcher/copy存在、比较/通知/生命周期/分类和 SIM 业务都不重计。来源排除、新ISA规则、完整函数导出均为0，没有完整 ROM/协议恢复宣称。

必要伪代码（仅正常有效item和下层调用正常返回，非原源码）：

```c
store8(0x62fcb2f0, 0);
if (len != 13) goto existing_tail;
total = load32(0x62fcb2cc);
index = load8(payload);
// 此视图选择 total!=0 && index<load8(total+6) 的正常分支。
dst = load32(total) + index*0x1a8 + 0x18;
src = payload + 1;
if (compare(src, dst, 12) == 0) goto existing_tail;
copy(dst, src, 12);
// 原程序重新取得 total/count/array；不能改成一直使用dst所属缓存对象。
current = load32(0x62fcb2cc);
if (current != 0 && index < load8(current+6)) {
    item = load32(current) + index*0x1a8;
    store32(item, load32(item) | 0x800);
    log(index, load16(item+0x18), load16(item+0x1a), load16(item+0x1c));
    notify(index); // a00a389c，合同直接继承
} // 其余既有目标9d06不在本题展开。
```

首半字的语义是12B原位字节复制完成后，后续 LHU 按该ROM既有小端语义读到 `payload[1] | payload[2]<<8`。它是复制结果/读者解释，不是把调用改写为一条 SH 或断言其他10B不影响变更门。cmd56本段没有额外active/type门，没有直接调用B22分类分支；改变 h 本身不等于立刻重新分类。

所有权：payload只在同步比较/复制时借用，未把payload指针存入item。item内联12B由既有数组持有，copy无本段新分配/free或指针转移；通知借用和mask清零继承E01/E02。未据此认证payload生产者、异步持有、对象稳定或最终数组生命周期。

## 精确未闭与实际验证

1. **物理单位/编码来源未闭**：当前只证 payload+1 原字节直达 h，以及日志DCap名。外层payload的实际生产者、单位/校准/合法业务范围不在本题获得证据，不向帧/driver扩扫。
2. **跨命令实际时序未闭**：cmd56内部顺序已证，cmd56何时相对后续cmd51发生、是否先写后读、是否另有调度/响应重排未知。h依赖关系不等于已认证的整条运行时间线；本段不直接重算分类。
3. **对象稳定与其他路径未闭**：复制前缓存目的和复制后重读数组的稳定性、全局串行化、其他writer、全部命令/外部协议仍保留，不以有界检索声明不存在。
4. **实现与来源边界**：字节copy/compare与通知内部已继承，底层copy的具体store宽度/原子性、准确上游来源及厂商ISA规范未新增认证。

[verify.py](../../analysis/cmd56-item-field-contract-b25-0041-20261024/verify.py) 已运行 PASS：6组必要稀疏窗口232B/67条指令与旧raw及原ROM一致，8个标准分支目标和分支符号字段、5个直接目标、索引/计数/半字/word字段、3个厂商字和两处日志字符串均核验；仅本地字段/静态解码，不执行dispatcher、模型或输入。首次自检修正了脚本中85ba的一处期望编码笔误（正确原字b284），未改变原件或语义。JSON解析、相对链接和diff检查通过。

一个后续闭包仅为：新独立 agent 核本题同址公式、len13/整12B变更门、copy调用ABI/首半字解释和重读后的0800通知顺序；直接继承B23/E02可靠合同，不重验整分类/dispatcher。若另追单位或跨命令时序，必须先取得真实payload生产者或调度绑定种子，当前不自行扩展。
