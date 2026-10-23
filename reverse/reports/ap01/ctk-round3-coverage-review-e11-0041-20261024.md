# 0041 E11：E09 round3 覆盖纠正独立技术复核

接受 E09 的核心纠正：`a00a1aa8 → a00a53c0` 及 `s0-0xe4 → item+0x12` 早已留存在同 ROM 的较晚 round3；E07/E08 的二轮短 body 判断不能外推为此前全部分析缺失。本轮只认证证据身份、范围及局部接入 ABI，不认证整函数业务或完整 CFG。**新增功能恢复 0，新增函数导出 0。**

基线 `3ba6b963c20ff0f6dffd503c52567c9e013cfc84`，独立树 `re0041-e11`、分支 `codex/re-0041-e11`。采用 reverse-engineer-anything 技能，先查已有材料再校核必要锚点。主仓 ROM、ignored 留存与模型只读；没有打开或切换共享 REA target，没有运行模型、历史回放、SIM、构建、固件、设备或外部服务。只写本报告和同名独占 analysis 目录，不改其他 agent 成果、共享索引或生产配置。

## 继承结论：已有出处 → 真实缺口

| 既有出处 | 已解释行为 | 本轮范围与局限 |
| --- | --- | --- |
| [E09](ctk-caller-alias-e09-0041-20261023.md)及其 `reuse-result.json` | 较晚 round3 正常延续、getter、保存槽及两个普通字段；旧 SUB64 误称纠正 | 不运行原验证脚本以免写旧结果；独立读原件并验证身份、字段宽度与接入 |
| [E07](ctk-extra-consumers-e07-0041-20261023.md)、[E08](ctk-extra-review-e08-0041-20261023.md) | 固定候选原 ROM 调用、二轮 retained body 到 `a00a144f`；拒绝最近入口误归属 | 这些判断在指定旧记录上成立；其后继缺口须结合较晚留存重新收缩 |
| [UART 近期报告](uart-retry-receive-0041-20261023.md)第75行及机器记录 `round3_model` 的 `a00a12d0` 项 | 已引用同一 round3 Evidence、4566 B body、无坏指令/halt_baddata但有删块警告 | 证明 round3 并非 E09 首次产生的材料；旧模型测试摘要仅作来源，不重跑或认证整套 ISA |
| E01–E08、`charge-complete-0041.json` records[8]/[9]/[19]及旧 complete/SIM 对照 | 五组生产与借用、前三组普通消费、清理合同 | 直接继承；SIM 合同不能替代 ROM 扩展字段 ABI，不重做消费者与资源 |

本题实际缺口仅为 E09 来源连接与结论强度的独立复核。无需再查 E10 根退出、CTK 全域编码或重新导出函数。

## 本轮复核或纠正

### 逐项判断

| E09 项目 | 判断 | 独立依据及限定 |
| --- | --- | --- |
| round3 属于同 ROM | 接受 | 两原始记录 `subject` 相同；当前原 ROM SHA-256 与记录已有 commitment 比较通过，不另建哈希清单 |
| round3/二轮 profile 不同 | 接受 | 分别为 `RISCV:LE:32:ap01thead3`/`ap01thead2`，均映射 `0x9ffff000`、32位；digest 保持分别归属 |
| `a00a12d0..a00a24a5` 完整 body 已留存且包含调用 | 接受，限定为 retained AddressSet | 单段4566 B、contains_entry；汇编从 `12d0` 至 `24a4` 的2字节跳转。不是所有路径可达、全部业务恢复或完整 ABI 证明 |
| 二轮 `a00a1450` 截断处为既有 SUB64 | 接受 | 二轮 body 最后地址 `144f`；下一原字 `0xc2e61577` 位域为 op `0x77`/funct3 `1`/funct7 `0x61`，rd/rs1/rs2=a0/a2/a4；旧 round3 模型第2行已有 sub64 条款。没有执行模型或将该条款当厂商全 ISA 认证 |
| getter/保存槽链早已留存 | 接受局部直接链 | retained 汇编、独立 JAL/存取位域解码相符，见下文；没有新发现调用或普通字段 |
| E07/E08 不能外推此前全分析缺失 | 接受纠正 | 二轮 `procedure_info` 与较晚 round3 `analyze_function` 是不同操作/profile；短记录之外已有更长 body，不得以旧 `owner=null` 宣称程序无 owner |
| item+34/+38 未命中 | 接受未知保留 | 本轮不做间接 alias 到达分析；“唯一槽读/写”仅指该 body 的直接 `s0-0xe4` 引用，不排除别名访问 |
| 全函数参数语义、间接下游与借用结束 | 未核 | E09 已声明其范围外；本轮不补全、不从局部正常栈推出全函数 ABI |

未发现 E09 核心原字节事实错误。本轮对其“完整 body”“唯一槽读/写”作上述范围限定，不把覆盖纠正算成新功能。

### 可定位证据与必要原序

主仓绝对来源前缀为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/`：

- `round3/evidence/whole-rom-round3-open-20261023-002.json`，Evidence `ev_dac9ee80a05e233e383bc1f10b5d225121efdc2db62ab51519958d8f220d15c3`，profile digest `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`。
- `evidence/whole-rom-graph-20261023-4778.json`，Evidence `ev_2ecf5b8ded9c350a2da4c8206066d7cc73f0e3f9f2e80eb4fc229f111a5aeceb`，profile digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。
- `round3/scripts/ap01thead3.sinc:2` 为已存在 SUB64 条款；仅读取。旧二轮 halt_baddata 的解释沿 E09/旧报告继承，本轮独立观察到的是旧 body 截止点和紧接的原指令，不以此声称已重验整个旧分析器因果链。

入口 `a00a12d0` 分配 `0x110` 栈，`12da` 设置 s0=旧sp；`1386..13aa` 的寄存器恢复、sp+0x110及ret仍在同一留存 body。这些支持本调用的局部正常栈身份；不从反编译 signature 推出完整参数合同。

接入原序：`a00a1aa4` 将 s10 低8位放入a0，`1aa8` 原字节 `ef309011` 独立解出 `jal ra,+0x3918 → a00a53c0`。`1aac` 的 `th.lrhu a3,s11,s10,3` 是另一表读取，其基址不是 getter 返回a0。`1acc` 的 `232ea4f0` 是32位 `sw a0,-0xe4(s0)`；`1b20` 的 `0358a500` 是无符号16位 `lhu a6,0xa(a0)`，`1b24` 随后覆盖a0为4。

后续条件分支沿旧汇编继承，不压平为无条件执行：`1cd0` 的 `8327c4f1` 重载32位保存指针至a5，`1cd4` 建立 s0-0xa8 目的基址，`1cd8` 的 `03c62701` 无符号8位读 `item+0x12`；`1cdc` 随即把a5改为索引*8，`1ce2` 用既有 `th.srb` 存 byte。两处直接槽引用与 E09 相符，局部链没有新增所有权、free或下游指针传递。

必要伪代码仅表达局部数据链，不是原源码，也不替代中间分支与调用：

```c
item = a00a53c0((uint8_t)s10);  // 借用/NULL合同继承，不补异常语义
store32(s0 - 0xe4, item);
// 保留旧汇编中的中间计算及正常分支。
ordinary_flag = load_u16(item + 0xa) != 0;
// 在原来的后续条件成立路径：
again = load32(s0 - 0xe4);
ordinary_byte = load_u8(again + 0x12);
store_u8((s0 - 0xa8) + s10, ordinary_byte);
```

round3 伪代码仍明确删除 `a00a1abc/a00a1adc/a00a23f0` 不可达块；原汇编保留这些地址。没有依赖删块结果证明全部路径、没有把已留存 body 当全局 alias 证明。

## 真正新增与实际静态验证

新增仅为本独立技术复核意见和有界验证结果；新增业务、消费者、转换、函数导出、生命周期闭包均为0。恢复程度为“来源/覆盖口径及局部接入得到复核”，不增加整 ROM 恢复分母。

[独占验证脚本](../../analysis/ctk-round3-coverage-review-e11-0041-20261024/verify.py)直接读取上述原件，检查同 ROM 身份、分立 profile、两 body 范围、16处既有汇编锚点、2处直接槽引用；从原 ROM 独立解码6条必要旧指令（JAL、SW、LW、LHU、LBU、SUB64），并检查既有 SUB64 条款与三处删块警告。原字节复读全部计为旧结论复核；没有重导函数、编码扫描或执行旧验证/模型。

命令 `python -X utf8 -B reverse/analysis/ctk-round3-coverage-review-e11-0041-20261024/verify.py`：PASS；[结果](../../analysis/ctk-round3-coverage-review-e11-0041-20261024/review-result.json)。`git diff --check` 用于交付格式检查；未构建或运行目标。

## 未闭精确边与一个后续闭包

`item+0x34/+0x38` 实际页面/业务读者、转换、主要下游 ABI、间接别名与借用结束时刻仍未知。当前候选的直接返回值/槽链只到普通字段；不能由“未命中”推出无消费者或死字段。整函数高层参数、全部普通分支和全局状态合同未认证。

本题以“既有覆盖已获得独立复核”闭合，不继续递归复核同一 body。若后续另派任务，应以一个已定位的真实 item 指针跨调用/快照别名边为起点，核身份及首次 +34/+38 读取；没有此锚点时保留未知，不重做 CTK 全域排除。由管理者另定，不自动接题。
