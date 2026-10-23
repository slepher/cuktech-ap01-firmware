# 0041 H14：天气时钟正常 ABI 独立复核

H13 的正常调用链、两次 signed32 DIV、既有 UMAR64 单寄存器无符号乘数到 a1:a0 累加、既有 URL `%lld` 接入均接受。唯一需要收紧的文字是“10⁹归一化”：原字节只证明有符号上界检查后的**单次进位**，不单独保证任意输入的细 word 都进入 `[0,10⁹)`。新增功能0、ISA规则0、完整函数导出0。

基线 `d493236b8802ec310e9433e8761fb1eb40e2b822`，树 `re0041-h14`、分支 `codex/re-0041-h14`。使用 reverse-engineer-anything 技能，只读主仓 ROM、已有证据与模型文本；没有打开共享 REA target、运行或修改模型、SIM、构建、固件、设备、历史回放或网络，没有创建下级 agent。其他 agent 同时工作，本轮仅写本报告及独占同名 analysis 目录，未改主树/生产ROM/配置。

## 已有出处 → 行为 → 局限 → 精确复核缺口

| 既有出处 | 已有行为与局限 | 本轮处理 |
| --- | --- | --- |
| [H13报告](weather-clock-abi-h13-0041-20261024.md)与其 `static-result.json` | 参数0调用 `a002696a`，pair局部输出、单次10⁹进位、两次DIV及厂商字；来源/epoch未知 | 对 source 留存窗口及原件逐byte比较，仅复核正常链与措辞 |
| [weather-dataflow](weather-dataflow-0041-20261023.md) / `instruction-windows.json:clock_ms` | helper全窗口旧证据包含 `a00a9d5a` 原字，但通用解码曾不能解释 | 比较既有hex与原件；不再整函数导出 |
| `tooling/scripts/qemu-ap01-cpu.patch:147,311–339` | 旧opcode条款和 `trans_ap01_umar64`：单寄存器unsigned32乘积加到偶/奇目的对，模2⁶⁴ | 只读匹配编码、取源、无符号乘与成对写回；不是本轮新规则或硬件验证 |
| [weather-location-request](weather-location-request-0041-20261023.md)“MAC、时间和摘要输入”及其指令窗口 | 既有 a0/a1→保存/恢复→签名字符串和URL `%lld`，RV32可变参对齐 | 合同继承；仅独立解码两处helper JAL，不重做URL、摘要或天气分类 |
| H13所列较晚round3、complete、ZIP与旧SIM服务 | 截断body/宿主替代均不能认证ROM时钟source/epoch | 不重查整库、不重复ZIP/complete搜索，不移植E14 uv时钟 |

实际缺口仅是上述局部合同的独立接受/纠正；底层来源不在本轮扩大范围。

## 继承结论与逐项复核

| 项目 | 复核结果 / 可定位依据 | 判定 |
| --- | --- | --- |
| helper参数与输出pair | `9d1e`建0x20 B帧，s0为入帧前sp；`9d2a:930584fe`令a1=s0−0x18，即新sp+8的8 B；`9d2e:0145`令a0=0；`9d30` JAL=`a002696a` | 接受 |
| selector0正常source路径 | `a0026974` selector&7仍0，跳过1/4分支；`699c`存输出指针，`69a0`非零分支不取；`69a6` JAL=`a002645a`，`69aa/ac`保存返回并仅0继续；`69f4:2685`把保存的状态s1返回a0 | 接受，仅正常成功 |
| pair合并与保存 | `69b0`保存/清mstatus bit3；`69bc..ce`分别合并全局 `62fc5c74/+4` 与底层pair的两个32位word；`69e8/ea`向调用者输出+0/+4，`69ec`恢复mstatus | 接受，不能替代offset写入来源 |
| 归一化措辞 | `69d0/d4`构造999999999；`69d8:6358f600`为 signed BGE(a2,a5)，成立直接到69e8；否则 `69dc/e0`构造−1000000000，`69e4/e6`只减一次、粗word只加1 | 纠正文案边界，见下文 |
| 两次除法 | `9d36`取pair+4；s1=1000；`9d42:b3c49702`为 DIV s1,a5,s1；`9d4e:b3c7e402`为 DIV a5,s1,a4，a4=1000。独立字段校验两者opcode33/funct7=1/funct3=4 | 接受 signed32、两次向零截断，不是DIVU或单次/1000 |
| 厂商字与乘数身份 | `9d5a:7715e9a4` little-endian word=`a4e91577`，opcode77/funct3=1/funct7=52、rd10、rs1=18、rs2=14；严格匹配**旧**UMAR64 | 接受 unsigned32(s2)×unsigned32(a4)，不是源寄存器对乘法 |
| 累加器与返回 | `9d54:3e85`把第二次商置a0，`9d56:93d5f741`算术右移31置a1；旧条款目的rd&~1=10即a1:a0。`9d5e..62`仅恢复s2/栈并ret | 接受 sign-extended商作64位累加器，返回low=a0/high=a1 |
| 签名/URL接入 | `a00aaca0`、`a00aae98`的原JAL均到helper；既有消费者合同把同一返回bits送 `%lld`，ID初始格式时间a4/a5，最终URL时间a6/a7 | 接受继承，不新增URL行为 |

pair只存在调用者栈帧，未见heap分配、持久保留或所有权转移；返回即随帧归还。恢复s0/s1/ra的原顺序不覆盖已准备的s2/a4或最终商/返回对。

## 本轮纠正：归一化的精度边界

H13所称“按10⁹归一化细单位word”可用作正常时间pair的语境，但应明确为**一次有条件进位**。signed BGE并不排除负细word，原窗口也没有下溢借位或循环进位，因此这些字节不能单独证明所有可能输入均已规范化。此处只收紧证据表述，不开展异常输入调查，也不推断原厂正常source会产生这些情况。

正常成功路径的必要伪代码（非原源码；位宽与顺序保留）为：

```c
// source wrapper: 成功时，先取底层pair，再在保存/清中断状态期间合并offset
coarse = add32(base_pair[0], offset[0]);
fine   = add32(base_pair[1], offset[1]);
if ((int32_t)fine > 999999999) { fine = add32(fine, -1000000000); coarse = add32(coarse, 1); }
out[0] = coarse; out[1] = fine; // 随后恢复原mstatus，返回0

// helper: call_a002696a(0, stack_pair) 返回0后
q1 = div_s32((int32_t)stack_pair[1], 1000);
q2 = div_s32(q1, 1000);
ret_bits = (bits64(sign_extend32(q2)) + (uint64_t)(uint32_t)stack_pair[0] * 1000u) % 2^64;
// a0=low32(ret_bits), a1=high32(ret_bits)
```

源码式 `% 2^64` 只表示位运算模宽，不是新推断的一条原指令。正常秒/纳秒pair语境下，该形状支持既有毫秒解释；只有把细word解释为纳秒才有“丢弃到毫秒”的物理单位含义。`%lld`在消费者端按signed64解释返回bits，不能反向把UMAR64的第一个乘数改为signed32，也不能给selector0、来源或epoch命名。source非零分支绕过pair加载，不纳入上述正常公式，不补造有效时间/错误值合同。

## 真正新增

新增功能0、ISA规则0、完整函数导出0。本轮独立接受H13正常ABI，补一处正常返回状态的稀疏锚点，并收紧“归一化”文字，均为旧结论复核。

## 未闭精确边与后续闭包

仍未核：`a002645a`底层source、`62fc5c74/+4` offset实际写入者/校时政策、selector0正式接口定义、精确来源版本、epoch，以及source非零路径的业务合同。本轮未以旧QEMU测试声明代替天气原件执行证据；未把较晚反编译截止59当作覆盖5a之后的CFG，也未套用E14 uv deadline来源。

单一后续闭包仍可沿 `a002645a` 正常pair生产者与 `62fc5c74/+4` 一个已定位写入者核对来源/offset身份；先复用complete/较晚留存，只有真实命名或换算证据支持时才认证epoch。本轮不自动接题。

## 实际静态验证

[verify.py](../../analysis/weather-clock-review-h14-0041-20261024/verify.py)与[static-review.json](../../analysis/weather-clock-review-h14-0041-20261024/static-review.json)记录本轮静态检查：旧helper/source窗口与当前原件一致，4个JAL独立解码、2个DIV字段、厂商字字段、旧UMAR64函数内部条款及6处稀疏原字节锚点均通过。没有运行模型、固件或时间输入回放；URL保存/恢复参数合同按已有报告继承，没有重复整函数证据导出。报告相对链接和 `git diff --check` 通过。结果只覆盖本题正常链，不宣布完整时钟或天气模块完成。
