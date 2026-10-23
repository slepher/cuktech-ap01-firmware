# E18：uv 时间的固定分母除法与商返回

2026-10-24；基线 `df35f44`，独立分支 `codex/re-0041-e18`。**E16/E17 的实际正常输入上，`a001b302` 返回精确无符号商，a0=t、a1=0；t是H15/H16同一次读取的U32计数值。** 故该次 `a0098b60` 最终写 `loop+140=t`、`loop+144=0`。这是数值恒等式，不认证实际计数每毫秒递增、epoch、单调性或刷新节奏。无需认证helper的任意64位分母或整库来源。

采用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只读主仓ROM与留存证据，不打开/切换共享REA target/database，不运行固件、模型、SIM、算术输入回放、构建、设备或网络；无下级agent。仅本路独占报告/analysis写入，未改其他树、共享索引、ROM、配置、生产代码或模型。伪代码及符号变量是原指令的结构化解释，不是原源码。

## 继承结论：已有出处→行为→局限→实际缺口

|已有出处|已有行为与证据强度|实际缺口/本轮处理|
|---|---|---|
|[E16](uv-time-producer-e16-0041-20261024.md)、[E17](uv-time-producer-review-e17-0041-20261024.md)|已独立接受writer、ID1→a002645a、UMAR64返回pair、分母a3:a2=0:1000000、a001b302调用及loop低后高写回/dispatch接线|除法只稀疏DIVU/REMU/MUL推断；本轮只补该实际输入的必要正常路径，不重复timer/caller/source导出|
|[H15](clock-source-offset-h15-0041-20261024.md)、[H16](clock-source-review-h16-0041-20261024.md)|a002645a只读一次U32 t，输出t/1000和(t%1000)*1000000，返回0；后者最大999000000|继承已复核宽度/公式；不重做clock、selector0、offset或counter writer|
|[E14](uv-timer-deadline-e14-0041-20261024.md)/E15|缓存用于ADD64和unsigned64期限比较|直接继承；数值恒等式不能代替实际时钟来源/物理单位/epoch|
|whole-rom-coverage-0041-20261023-round1.json 的a001b302|extent `ev_eb17f4f13ef5eac03fcaa04ed2418d64adcb212e25b792b6d2312c675e0fffa3` 为b302..b661，864B；direct_calls `ev_485d5b2e35e38f3eb354c3e6ab4d95cda85cf7adf2efcf19cc1c03ccfdb5a26d`为空；无source/dossier|旧清单只定位；不把整body当语义已证，不重导864B，不靠外观命名标准库|
|最终complete、pass3、最终源码ZIP|本轮精确token a001b302 / __udivdi3 / udivdi 对2文本及ZIP的35文本成员查询无命中，见reuse.json|只说明这些载体/词项；不代表此前从未分析。旧SIM/照片/替代服务不能证明ROM quotient ABI|

四层证据保持区分：E16/E17/H15/H16可靠原字节合同直接继承；旧反编译/清单仅定位；SIM/照片/安全替代不证明ROM算术；本轮新增必要原字与实际范围的数学证明。确切上游数值库仍未知，不新增开源排除。

## 本轮复核或纠正

仅稀疏复核helper入口寄存器搬移及E17已有DIVU/REMU/MUL字段，作为新必要路径的接入锚点；不是重新恢复旧writer或ISA。E16/E17的“完整除法尚未认证”在其原报告范围正确，本轮把**固定非零分母及继承实际分子范围**提升为已证合同，未纠正旧语义，未认证整个helper。

入口 `b302..b30a` 将原分子低L→a7/t1，高H→a5，分母低D→a6，高→a0。`b30c` 检查原a3；本路径恒0。没有将a0/a1顺序倒置，返回也不是余数pair。

## 真正新增：必要路径与数值证明

### 实际分子范围先于算法收缩

继承H15/H16，令 `t∈[0,2^32−1]` 是那一次U32读取，`c=t/1000`，`r=t%1000`。E16/E17的正常source把细word先符号扩展，再用UMAR64计算：

```text
N = sign_extend32(r*1000000) + unsigned32(c)*1000000000
  = r*1000000 + c*1000000000
  = t*1000000.
```

`0≤r≤999`，故细word≤999000000<2^31，符号扩展没有改变数值。最大N=4294967295000000<2^52，不发生64位累加回绕；`H=floor(N/2^32)≤999999<D=1000000`。因此 `b318 BGEU a1,a2→b3d6` 恒不走，不需要认证高商word路径、分母高word非零分支或零分母路径。t=0是该正常U32范围的一部分，不新增排除门。

### 固定分母归一化：只用一个表byte

`b31c` 置a4=65536，`b31e BGEU D,65536→b3c8` 取跳。`b3c8` 置a0=0x1000000，`b3cc` 置a4=16，`b3ce BLTU D,0x1000000→b32c` 取跳。`b310/b314` 形成表基址`a01bb7f0`；`b32c..b33c`：

```text
index = D >> 16 = 15;
table[15] = load_u8(a01bb7ff) = 4;  // 本轮只读取此一个实际使用byte
bit_length = 16+4 = 20;
shift = 32−20 = 12.
```

`b340` 比较32和20，不跳；`b344..b352` 按原序构造归一化分子高/低及分母：

```c
U = (H << 12) | (L >> 20);  // a1
V = L << 12;                // t1，RV32低word
Dn = D << 12;               // a6 = 0xf4240000
```

这是`N'=N<<12`的高U/低V。N'仍小于2^64；高word通过来自L的跨word位拼入，而不是只左移H。H<<12与L>>20的位域不重叠，OR不遗漏进位/高位。由H<D得U<Dn。`b356/b35e/b362` 将Dn拆成高16位d=62500 (`0xf424`) 和低16位d0=0。两个实际DIVU/REMU除数都是非零62500。

### 两位商、修正门与返回pair

令B=65536，`v1=V>>16`、`v0=V&65535`。必要状态如下：

|原指令窗口|实际状态变化|
|---|---|
|`b35a DIVU a3,a1,a7`、`b368 REMU a4,a1,a7`、`b36c MV a0,a3`|q1=U/d，r1=U%d，a0=q1；0≤q1<B，由U<dB证明|
|`b36e MUL a1,a2,a3`、`b372/b374`|乘积d0*q1=0；a5=P=(r1<<16)\|v1，P<dB，无32位拼接损失|
|`b376 BGEU a5,a1→b38e`|unsigned P≥0恒真，跳过q1−1/−2及加回分母的修正支路；`b38e`只减0|
|`b390 REMU`、`b39a DIVU a5,a5,a7`|r2=P%d，q0=P/d；0≤q0<B。`b394/b396`保留v0；`b39e/b3a0`拼(r2<<16)\|v0|
|`b3a4 MUL a3,a2,a5`、`b3a8 MV a2,a5`|乘积d0*q0=0，a2=q0|
|`b3aa BGEU t1,a3→b3c0`|unsigned值≥0恒真，再次跳过修正。无需展开修正body，也不假定一般除法无需修正|
|`b3c0/b3c2/b3c4`|a0=(q1<<16)\|q0，a1=0|
|`b3c6 5da8 C.J→b47c`、`b47c 8280 RET`|直接返回，不改a0/a1，无后续函数调用|

原字字段独立确认：`b35a` DIVU、`b368` REMU、`b36e` MUL；第二组`b390` REMU、`b39a` DIVU、`b3a4` MUL。比较都是BGEU而非signed分支；两个商digit在16位内，最终OR等于加法，a1确实是商高word零，不是状态码。

精确恒等式：

```text
q1*B+q0 = floor((U*B+v1)/d)
         = floor(floor(N'/B)/d)
         = floor(N'/(d*B))
         = floor((N<<12)/(1000000<<12))
         = floor(N/1000000)
         = t.
```

这里舍弃v0合法，是因为归一化分母低digit d0=0；不是把任何64位除法都缩成32位除法。所有范围/门均基于实际分母和继承t，覆盖该正常U32域的符号证明，没有运行helper、模拟指令或枚举算术输入。无需推广至任意分母、任意分子、商高word非零或其他调用者。

### 写回和资源责任

E16/E17已核的调用将返回a0写loop+140，a1写loop+144；据本轮结果可写作`store32(loop+140,t); store32(loop+144,0)`，t属于source的同次读取而非写回时重新读取counter。低后高两次写的原序及非原子性沿旧合同，不补锁。该实际helper路径只读归一化表一byte，无stack/heap分配、指针保留、callback或所有权转移；caller帧及loop/timer生命周期继承旧报告。

## 未闭精确边、恢复等级与验证

- 继承：H15/H16分子拆分、E16/E17 selector1/UMAR64/source/回写、E14/E15期限消费全部直接引用。
- 本轮复核/纠正：稀疏入口和旧M指令复核；旧语义纠正0，ISA规则/模型改动0。
- 真正新增：固定分母正常uint64商的必要CFG、跨word归一化、两digit估商门、返回pair以及缓存数值=t；标准库精确来源认证0、整函数导出0。
- 未闭：helper其他调用范围/分母高word非零/高商路径及准确编译器库来源未认证；counter writer、cadence、epoch、硬件来源、单调/校时/回绕政策、真实uv刷新频率仍未知。不把数值相等提升成实际毫秒或与天气ID0相同epoch。错误状态下source合同继续沿E16/E17未知，不展开异常研究。

单一后续闭包建议：独立复核本题“实际N=t×10⁶→H<D→shift12/d0=0→两个unsigned修正门直过→a0=t/a1=0”的证明与原字；不重复timer/clock内部或扩大数值库。实际计数writer路线由其他任务单独持有，不交叉扩题。

独占 [verify.py](../../analysis/uv-time-division-e18-0041-20261024/verify.py) 从主仓只读ROM以`offset=VA−0x9ffff000`核验：5个必要短窗口、130 B、41条指令、54项原字/字段/分支目标/表byte/返回目标断言通过；无厂商字。结果与常数范围证书见 [evidence.json](../../analysis/uv-time-division-e18-0041-20261024/evidence.json)，有界复用见 [reuse.json](../../analysis/uv-time-division-e18-0041-20261024/reuse.json)。未保存helper全函数或整表。JSON解析、报告链接及git diff --check另行检查。以上是作者静态自检，待独立技术复核，不冒称完整除法库验收。
