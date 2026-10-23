# 0041 E12：CTK 快照 caller / 消费寿命的既有覆盖纠正

本题已经由 [E03](ctk-view-dataflow-e03-0041-20261023.md)恢复，并由 [E04](ctk-view-review-e04-0041-20261023.md)独立技术复核。E01/E02 的“a00f4740 实际 caller、dst 消费未核”是当时断边，不能继续作为当前缺口。本轮收缩为复用核对，**新增业务恢复0、函数导出0、ROM窗口0**，不递归复核已接受的闭包。

基线 `173ee40`，独占分支 `codex/re-0041-e12` / worktree `re0041-e12`。采用 reverse-engineer-anything 技能；仅静态阅读既存报告、证据和 ZIP 成员，不打开共享 REA target，不执行固件、SIM、构建、历史回放、设备或网络，不修改主树、ROM、模型、生产代码或他人成果。

## 继承结论：已有出处 → 行为 → 局限

| 出处 | 已解释行为 | 证据局限与处理 |
| --- | --- | --- |
| E01/E02 | `a00f4740(dst,port)` 借 item 的 +28/+2c/+30，只写数值到 dst，失败0/成功1 | 当时未追 caller；被 E03/E04 补足。它不是 item+34/+38 读者 |
| E03/E04 | `a005d146/14a → a01b28ce` 注册 callback=`a00adabc`, userdata=app；`a00a389c` 从 `62fcb530` 调 `callback(app,item)` | 节点仍挂链、正常通知条件下的静态可达合同，不是执行命中观察 |
| E03/E04 | `a00adabc` 三处直接 converter call：`a00ae238/a00aef62/a00af17c`；正常 port1 已完整接主要消费 | offline 第三处不判断返回，不能推广在线0返回跳消费合同 |
| 主仓只读 `reverse/rehost/charge-complete-0041.json` records[8]/[9]/[19] | 原指令早已留存 `a00f4610/a00f44e8/a00f5288`，分别数值、名称、详情普通项消费 | 硬件服务/部分布局被本地模型替代；不能从 SIM 成果推出 ROM 对象别名 |
| `charge-0041-round4.json` observed.overview_bank、records | 已有 `a00ef1d4/a00ef2da` 的 SOC、时间和前三组显示资料 | 旧 remaining 须服从 complete 的后续整合；无需重新恢复数值显示 |
| `details-0041-round4.json`、main/detail-knob round2、page-logic | 旧页面/旋钮路线与 Date/Weather detail 材料 | details 文件名不代表 CTK；同偏移不能跨对象拼接。限定文本核查未出现本 getter/caller 地址，不是全局无消费证明 |
| 最终 ZIP 的 `tools/ap01/ap01-ui-charge.h:352..377`，及 `ap01-ui-details.h` | 电池、remaining_minutes、ports[] 的服务字段已有实现 | 只读成员；服务模型字段不认证 wire ABI，也不证明其与 dst 同身份 |
| E09/E11 与较晚 round3 | `a00a1aa8` 的另一 getter/保存槽链已有覆盖纠正 | 与本 caller 闭包不同；直接继承，不重做。对 round3/evidence JSON 的本题两地址精确文本检索无命中，只是有界检索结果 |

上述旧文件均从 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/` 绝对路径只读。旧目录别名不是原件缺失；本轮没有新建复制/哈希清单。

## 本轮复核或纠正

仅纠正任务现状：E03/E04 已闭合本题所要求的一条真实正常 caller 与数据 alias。保留 E04 的纠正：port1 与 port2 使用同一局部槽的静态布局，但端口谓词互斥，不能描述成一次 port1 通知后连续执行 port2 转换。本轮不是新的独立指令验收；接受 E04 已有技术裁定，未重新运行会写旧结果的验证器。

可定位来源为 E03 `references.json` 中 callback Evidence `ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5`，以及 E03/E04 的 instruction-windows / independent-checks。原件为主仓 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json`；profile 为 `RISCV:LE:32:ap01thead2`。E04 已从同 ROM 原字节核三处 call 和主要消费者，而本轮仅核保留引用与旧资料身份，不重复整函数导出。

## 已接受的快照身份与业务闭包

`a00adabc(app,item)` 以 `s0=entry_sp` 建0x100 B frame；dst=`s0-0x94`，先 fill0x52。正常 port1 分支要求 `62fc4062==1 && port==1`，`a00aef62` 传 `(dst,1)`，`a00aef66` 返回0跳 `a00af12e`。panel 从 `child(app,1)+0x10` 的 wrapper+4取得，不能把 panel 与 item 或 dst 混同。

view +08/+0a/+0c/+0e 是 u16 SOC整数/小数/小时/分钟，+50 是 u8小数模式；四个 row 位于 +10+16*j，含 u8 active/direction、u16功率/电压整数小数/电流整数小数及 u8 kind/ordinal/有效标志。名称消费者 `a00f44e8(slot,kind,ordinal,total)` 收标量，total 为第四参数；值消费者 `a00f4610(slot,row)` 读零扩展标量并传控件 setter；`a00ef2da(panel,view)` 读 SOC/时间并传标量。状态0跳过、1先名称再置2、unsigned >=2更新值；每槽保留 item.mask/app+54 的短路重读，0x20000门控行值、0x8000门控电池。精确原序、厂商字、布局和伪代码直接引用 E03/E04，不重新抄写替代实现。

这些主要消费者不向持久对象存储 row/view，也不将该指针转交下游，因此不延长快照寿命。port2 执行时用同地址，但与 port1 谓词互斥；公共 epilogue 归还0x100 B栈使 view 失效，没有 heap free。item 的三嵌套资源继续由 item 持有，converter 仅借用；app/订阅节点所有权与 view 的栈寿命是不同问题。

## 真正新增与实际验证

新增仅为“任务书旧断边已被 E03/E04 覆盖”的出处纠正及独占复用检查。执行 [verify-reuse.py](../../analysis/ctk-snapshot-consumer-e12-0041-20261024/verify-reuse.py)验证 E03 的3处转换引用、注册 PARAM 锚点、E04 接受/互斥/栈寿命表述、complete 三条 record 地址及 Evidence、四份旧 JSON 可读和指定 ZIP 成员服务字段；[结果](../../analysis/ctk-snapshot-consumer-e12-0041-20261024/reuse-result.json)为 PASS。这只是来源与既有覆盖核对，不是重新认证全部指令或运行显示。交付另作 `git diff --check`。

## 未闭精确边与一个后续闭包

本题正常 port1 caller→dst→主要消费→栈归还已由既有材料闭合。本轮不声称 item+34/+38 实际读者、全部 CTK、offline消费者、完整 app/订阅注销、GUI文本内部所有权或物理显示已恢复，也不以局部未命中证明它们不存在。E07/E09/E11 的另一getter槽链不纳入新成果。

若管理者另派，应只从一个已经定位的真实 item 扩展指针跨调用/快照 alias 边，追首次 +34/+38 数值读取与借用结束；没有该种子则保留未知，不重扫全ROM getter/字段。本题不自动接后继；恢复程度维持既有 E04 局部验收，无需为数量重复逆向。
