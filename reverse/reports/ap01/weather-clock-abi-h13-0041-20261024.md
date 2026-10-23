# 0041 H13：天气时钟正常调用与返回对

`a00a9d1e` 正常返回的具体算式已可由原字节接到**既有** UMAR64 语义：第一 word 按无符号32位乘1000，第二 word 连续作两次有符号32位除1000，符号扩展后累加到64位结果；返回 low/high 为 a0/a1。既有 URL `%lld` 接入合同继续继承。**新增 ISA 规则0、函数导出0；本轮增量只为天气调用点接入与宽度/单位校核，不能算重新恢复整个时钟或天气功能。**

基线 `bdc139a`，独立树 `re0041-h13`、分支 `codex/re-0041-h13`。采用 reverse-engineer-anything 技能；只读主仓 ROM/ignored 证据与已有模型，不打开或切换共享 REA target，不运行模型、SIM、构建、历史回放、固件、设备或网络，不修改生产代码/ROM/配置。未创建下级 agent。只写本报告和同名独占 analysis 目录；结果待其他 agent 独立复核。

## 继承结论：已有出处 → 行为 → 局限 → 缺口

| 既有出处 | 已解释行为 | 局限及本轮处理 |
| --- | --- | --- |
| [weather-dataflow](weather-dataflow-0041-20261023.md)，`instruction-windows.json` 的 `clock_ms` | 已留 `a00a9d1e..a00a9d63` 全部原字节、参数0、两次DIV、返回前未知字 `a4e91577` | 直接复用原窗口，逐byte对当前原件；不重导函数。通用反编译不能越过未知字认证计算式 |
| [weather-location-request](weather-location-request-0041-20261023.md) 第100–118行及其指令证据 | a0/a1时间、`%lld`、签名消息和两条URL的RV32可变参数对齐 | 直接继承；本轮仅核两处 helper JAL目标，不重做URL/摘要 |
| [weather-scheduling](weather-scheduling-0041-20261023.md) | helper的ms单位由调用换算与日志支持 | 继承单位语境，timer调度不重做，不从E14的deadline时钟移植来源/epoch |
| `reverse/rehost/weather-calendar-complete-0041.json`；最终ZIP的 `ap01-sim-service-impl.h`、`ap01-sim-service.h`、`ap01-ui-pages.h` | complete记录是天气/日历UI与SIM服务；ZIP service impl第31行使用宿主 `CLOCK_MONOTONIC` | 这些指定材料无helper地址；宿主替代不能证明ROM参数0的来源。仅读ZIP指定成员，未解包/执行 |
| `reverse/analysis/0041-20261013/0041-ghidra-pass3.txt`、主仓 `reverse/raw` JSON限定搜索 | 未检到helper/source地址或本厂商字 | 仅为上述范围的负搜索，不外推所有历史材料缺失 |
| 较晚round3 `whole-rom-round3-open-20261023-002.json` / `-004.json` | 同ROM retained body均为 `a00a9d1e..a00a9d59`，60 B；模型为ap01thead3 | 此次核到较晚记录仍不含5a厂商字；不能把旧UNKNOWN直接当较晚结果，但该窗口在这里确实仍被截断 |
| `round3/scripts/ap01thead3.sinc:2`，所include的ap01thead2末尾 | 已有SUB64和ADD64等条款，未含UMAR64 | 仅读，不修改或运行模型；不把SUB64套本字 |
| `tooling/scripts/qemu-ap01-cpu.patch:147,311`、`test-qemu-p.py:249`；[旧QEMU报告](qemu-rtc-display-20261017.md) | 既有UMAR64精确opcode：无符号32×32积加至rd偶数/奇数寄存器对，模2⁶⁴；旧报告已有测试声明 | **继承而非新规则**。本轮仅读规则/注释，不执行旧测试；没有以旧QEMU运行证明天气原件曾执行 |

实际缺口缩成：天气字能否匹配既有UMAR64；单寄存器乘数/累加对的身份；正常source输出两word到两次DIV，再到a0/a1的接入。来源认证和epoch另留断边。

## 本轮复核或纠正

### 正常source调用与对象身份

`a00a9d1e` 无需入口业务参数；它创建0x20 B栈帧，s0=进入前sp。`a00a9d2a:930584fe` 给a1=`s0-0x18`（即新sp+8，8 B局部输出），`9d2e:0145` 给a0=0；`9d30:efc0b7c3` 独立JAL解码到 `a002696a`。输出pair仅在本帧使用；没有heap申请、指针保留或所有权转移，返回时随栈归还。

source wrapper本轮只核参数0的必要窗口，见 [static-result.json](../../analysis/weather-clock-abi-h13-0041-20261024/static-result.json) 的 `source_windows`，不是完整函数导出：

1. `a0026974` 将selector与7相与，参数0仍为0；跳过selector1/4的分支，到 `699c` 保存输出指针，`69a0` 非零检查不跳。
2. `69a2` 给a0=本wrapper的 `s0-0x18`；`69a6:eff05fab` 调 `a002645a`，`69aa/ac` 保存返回值并只在其为0时继续正常输出。
3. `69ae/b0` 清mstatus的bit3并保留旧值；在该窗口取 `62fc5c74/+4` 两word和底层局部pair，两次32位ADD分别合并第一/第二word。
4. `69d0/d4` 构造999999999，以有符号BGE检查第二word；超出时 `69dc/e0` 构造−1000000000，第二word相加、第一word加1。`69e8:98c1`、`69ea:dcc1` 分别写输出+0/+4，`69ec` 恢复原mstatus。

该正常输出是“粗单位word＋按10⁹归一化细单位word”的存储视图。结合天气的×1000和两次/1000、既有调度日志，可支持秒/纳秒→毫秒的单位解释；**原字节不会自行给selector0、底层实现或epoch命名**。不把此形状升级为已认证的POSIX接口、Unix epoch、RTC或与uv同源。

### DIV、厂商字与64位返回

下列原序来自既有 `clock_ms`，本轮已逐byte与原ROM比较一致：

| 地址 / 原字节 | 普通指令或继承语义 | 宽度与身份 |
| --- | --- | --- |
| `9d34:09e9` | a0非零跳到9d46 | 下文正常路径仅在source返回0时成立 |
| `9d36:8327c4fe` | lw a5,-0x14(s0) | 取pair+4第二word；DIV将其视为有符号32位 |
| `9d3a:9304803e`；`9d3e:032984fe` | s1=1000；s2=lw pair+0 | 第一word保留原32位bits |
| `9d42:b3c49702` | div s1,a5,s1 | signed32、向零截断；第一次除1000 |
| `9d46:1307803e`；`9d4e:b3c7e402` | a4=1000；div a5,s1,a4 | 再次signed32向零除1000，不能说第一次已直接得到ms |
| `9d54:3e85`；`9d56:93d5f741` | a0=a5；a1=a5算术右移31 | 符号扩展该32位商至a1:a0 |
| `9d5a:7715e9a4` | **既有UMAR64**，rd=10/a0，rs1=18/s2，rs2=14/a4 | opcode77/funct3=1/funct7=52；乘数为两个单独无符号32位寄存器；累加目的为a1:a0，非s3:s2乘a5:a4 |
| `9d5e:4249`；`9d60:0561`；`9d62:8280` | 恢复s2；归还栈；ret | 没有覆盖a0/a1；返回low=a0、high=a1 |

`9d4a/4c` 已恢复ra/s0，`9d52` 已恢复s1；这些恢复不更改已加载到s2的第一word、a4的1000或a5的最终商。必须保留原顺序，不能因反编译截断把5a之后当无返回函数。

必要伪代码（只表达正常路径，非原源码）：

```c
uint32_t pair[2];                 // 本helper栈8 B，不外传所有权
int rc = call_a002696a(0, pair);
if (rc == 0) {                   // 非零路径不套本正常算式
    int32_t q1 = div_s32((int32_t)pair[1], 1000);
    int32_t q2 = div_s32(q1, 1000);
    uint64_t acc = bits64(sign_extend_32_to_64(q2));
    acc = acc + (uint64_t)(uint32_t)pair[0] * 1000u; // modulo 2^64
    return_pair_a0_a1(acc);
}
// 原非零分支跳9d46，跳过pair加载和s1=1000；
// 不能给它补造返回0、负errno或有效时间合同。本题不展开失败输入调查。
```

单位结论限定正常归一化细word：两次/1000将纳秒精度丢弃到毫秒；第一word在UMAR64中**无符号**扩宽后乘1000。`%lld`是消费者将最终bits按signed64十进制解释，不反向把第一word乘法改为signed32，也不证明时间来自某个epoch。

### 接入既有签名/URL

本轮独立解码 `a00aaca0` / `a00aae98` JAL均到 `a00a9d1e`。两个返回寄存器到签名字符串及URL的保存/恢复、RV32对齐与格式沿weather-location-request既有合同继承：ID初始消息在a4/a5、最终URL在a6/a7；地区/城市消息及URL亦使用同一low/high结果。没有增加格式转换、缩成单word或新增时间调用。未重新计算摘要、构造实际URL或发出请求。

## 真正新增与实际静态验证

新增的是5a原字与**旧**UMAR64的天气接入身份，以及source参数0的8 B局部输出/10⁹归一化、两次signed DIV到64位返回的局部合同。旧ISA语义、既有ms解释、URL/签名行为都不记新恢复；不主张完整底层时钟、全函数失败语义或全ROM完成。

[verify.py](../../analysis/weather-clock-abi-h13-0041-20261024/verify.py)已运行通过；它只读取ROM和留存JSON/规则文本，输出独占 `static-result.json`。校核包括既有helper原byte一致、厂商字段精确匹配、4个必要JAL、source普通指令窗口完整解码、两个较晚round3 AddressSet仍止59以及complete无helper地址。没有执行规则模型或算术输入回放，没有新增共享数据库/REA观测。报告链接检查与 `git diff --check` 通过。

## 未闭精确边

`a002645a`及全局 `62fc5c74/+4` 的原始来源、写入/校时政策、selector0的上游正式定义、精确库版本和epoch仍未知。归一化/单位形状不能替代这些来源证据；旧SIM的宿主时钟不能认证ROM。较晚round3截断不是完整CFG证明，UMAR64继承自已有静态规则来源而非本轮硬件执行。

一个后续闭包建议：单独沿 `a002645a` 的正常输出及 `62fc5c74/+4` 已安装写入者核来源/偏移身份，先检查完整阶段和较晚留存；仅当可定位证据给出epoch或selector定义时命名。此建议不与E14的uv deadline等同，也不在本轮扩展或自动接题。
