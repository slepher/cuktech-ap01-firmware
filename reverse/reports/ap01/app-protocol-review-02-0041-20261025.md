# Q14 非作者复核：cmd59 状态生产与后续 refresh

结论：**接受作者限定的静态阶段合同，无须作者修正**。正常 cmd59 分支把缓存记录的两个无符号 byte 写入 item+0x14/+0x15，按变化覆盖 mask 后同步通知；与 Q11 的接合仅为后续真正 refresh 时的条件可见性。本轮新增业务恢复为0，新增独立技术复核。不能将该阶段闭合扩大为某次 cmd67 已确认或协议物理生效。

认领 Q-14，复核者 `/root/app_protocol_review_02`，非作者。独占分支 `codex/app-protocol-review-02-20261025`，启动基线 `b6e97800516598807a11fc3dca8d8f085c97cdb6`；作者提交 `1f3f86fa7f376d0bbd78d94b17f0e3ce9f19fb9b`。初读作者独占树材料；确认主树同路径已整合该提交后，以主树材料为引用定位。只读主树 reverse-design 3.1/3.2/5.1/7 与 rolling-management 顶部/Q14，不修改认领表，不创建下级代理。

采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存证据方法；不启动或切换共享会话、不执行固件、模型、SIM、QEMU、回放、构建或作者脚本，不连设备或外网，不修改 ROM、生产配置或分析器。独立 [verify.py](../../analysis/app-protocol-review-02-0041-20261025/verify.py) 只读取原字及留存文本。

## 身份与复核依据

作者 [报告](app-protocol-research-02-0041-20261025.md)、同 stem contract.json/verify.py/instruction-evidence.json 已读取；脚本仅阅读。直接真源为主仓 `reverse/analysis/uart-response-0041-20261023.json#/functions/0/normalized_result`，EID `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`。复核重读原 ROM `roms/0041/ap01-1.0.2_0041.bin`：6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−0x9ffff000；留存函数整段 raw 字节和摘要匹配。

同时核来源 bundle `evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json` 的留存 SHA `689b060f96eaba167291ecf78c8998e5aea590555e793cac735d448265d1d385`，原 profile digest `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279` 对应 `RISCV:LE:32:ap01thead3`、base 0x9ffff000、private profile ap01-0041-20261023-v3。局部厂商语义另对照主树 `processor/data/languages/ap01thead2.sinc:6410/6596`（位于 evidence/rea-0041-20261017），明确这是本地保留模型，不能当独立上游 ISA 认证。

## 独立核对结果

| 环节 | 原字与控制流核对 | 结论 |
| --- | --- | --- |
| 分派与请求长度 | 0xa00a874e/8752/8756 比较0x59并跳0xa00a973e；9742 LBU、9752 shift3、9758 ANDI f8 | n=(u8[62fcb01c]<<3)&f8；不是 T.count*8，不能补 min/统一数量合同 |
| source 与循环 | 974e 读全局中的目的指针，975c helper；976a 再取S；9786/978a 每轮重读T/count，97b8读该T的A | S缓存，S+1缓存；T/count/A逐轮重读；首次T非零检查不证明后续替换安全或全局寿命 |
| 第一字段 | 97bc 原word 0x8779480b，indexed rd=a6/base=s2/index=s7/shift3；97ce SB a6,+14(t1) | S[8*i]为 unsigned byte，整byte比较并写item+14 |
| 第二字段 | 97f4 原word 0x877cc80b，base=s9=S+1，其余同上；9800 SB a6,+15(t1) | S[8*i+1]写item+15，不是S+8或word load |
| 变化发布 | a7初始0，第一变置1000，第二变OR2000；9828 indexed word store，rd=a7/base=s6/index=s5/shift0 | mask直接覆盖item+0；单变1000/2000、双变3000，无旧mask RMW |
| 通知与相等 | 982c ANDI i,ff，9830 JAL a00a389c；9836无变化直接983a迭代；9792 JAL a0191746 | 每变化项一次同步借用通知；相等不通知仍query推进；T初空也推进 |

逐条读取分派和 writer 共74条边界，并按 ROM 的低两位复验2/4B长度；独立解码3处 indexed 字段、2处 SB 源寄存器/byte宽度/偏移、3处 JAL 目标，另核分派 JAL x0。源byte各只加载一次；报告伪代码的重复load是表达压缩，不误解成机器指令重读。日志call之间保留t1/a7的栈保存恢复顺序也与最终写入相容。

继承公共 a0191652 copy、E01/E02 的 a00a389c 同步借用和清mask、P10查询推进合同，不再深入内部。缓存 S 与 item 无新所有权移交；同步通知不能支持异步持有item，mask不能当持久状态值。

## 与 Q11 的接合及断边

继承已独立验收的 [Q11复核](app-protocol-review-01-0041-20261025.md)：a009c662 在getter成功后从同一item+14取byte，与槽byte2整byte比较；相等不反解，不相等更新byte2，并仅以四映射开关变化决定bool。本轮不重验转换器。由此接受“cmd59 byte0生产后，在后续实际refresh可见”的条件接合；未从通知callsite找到或声称直接即时refresh边。+15变化/2000通知不自动成为Q11输入。

沿正常handler调用门使用B19/B21，不扩大到所有入包。继承P10调度只给查询机会，不给固定响应年龄或采样率。未闭边保留：全局S/T寿命与两种count的初始化不变量、+15应用消费者、特定cmd67请求与cmd59响应的相关确认、持久化和物理协商。不得从普通查询报告值推定这些阶段完成。

## 检查与交付

独立静态脚本通过 ROM身份、全raw匹配、74边界、3indexed、2SB、3JAL及dispatch检查；合同JSON解析与git diff --check通过。未运行作者脚本，无业务模型或固件执行。

预计2–4分钟，中置信（派发依据作者154.379秒、Q11复核144秒、Q10复核131秒）。首次可得UTC为2026-10-24 17:06:31，原字检查完成17:07:47，检查窗口76秒；完整启动与文档/提交结束另见交付消息。没有排队或中断；同步工具等待未独立计量，token不可得，不造有效工时。

ignored中间产物 `reverse/analysis/app-protocol-review-02-0041-20261025/instruction-evidence.json`，11651 B，SHA256 `7913bacc404eb0cb147d61fe864dbdb2f353fa990f474c33b2f6f2a6b942b3b6`。父窗转存核对前保留本树副本，不自行清理。报告、复验源码、合同按精确路径本地提交，不推送。
