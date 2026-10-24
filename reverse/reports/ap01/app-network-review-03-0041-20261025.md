# Q09 非作者复核：同 N 四计时动作门及 caller 分流

结论：**限定接受 Q09 作者报告的四 helper 与 caller 合同，无退回项、无语义纠正；新增业务恢复 0。** 可独立使用的计时决策阶段已闭合，完整应用接入／重连接口仍未闭。返回 1 表示 caller 的动作门，不证明联网、探测、云端应答或重启完成。

复核者 `/root/app_network_review_03`；分支 `codex/app-network-review-03-20261025`；基线 `5d38f2cc27d67cb5d28539228cca6b2da47b38c8`。被复核作者 commit `675db193a57e78bebb787d5a388b3a5ffcc3d391` 已停止、已由主窗合并；作者报告为主仓 `reverse/reports/ap01/app-network-research-02-0041-20261025.md`。只写本报告与同 stem analysis；唯一认领表和主仓流程只读，不回退其他协作者。

## 依据及独立性

- 读取主仓绝对路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/reverse-design.md` §3.1/3.2/5.1/7、rolling-management 顶部及 Q09 认领；继承 Q06，不重新验收注册、关联、DHCP、IPv4 或 40 B 归还胶水。
- 使用 [reverse-engineer-anything](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的静态证据分层规则。未打开、切换或修改共享 REA；无新 REA Evidence。未执行或导入作者 verify.py；作者报告只作命题与定位输入。
- 独立脚本 [review.py](../../analysis/app-network-review-03-0041-20261025/review.py) 静态读取主仓原件 `roms/0041/ap01-1.0.2_0041.bin`，核长度 6769704 B；沿既存 CATALOG SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，未重新声称全 ROM 摘要认证。映射 `offset=VA-0x9ffff000`。
- 独立顺序解码 A `0xa0067aec..0xa0067b93` 168 B、B `0xa0067b94..0xa0067be5` 82 B、C `0xa0068854..0xa0068913` 192 B、D `0xa0068914..0xa0068a25` 274 B，共 716 B；普通 RV32/RVC 使用 Capstone 5.0.7。两厂商字保留完整 4 B，继承主仓 SINC 语义并独立核字段，不冒充普通解码或 ISA 认证。
- caller 仅用主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/89`；Evidence `ev_4150d456a78d9d2a6c00fda793101e8915ff107084a8356d31e91552e2b072de`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。该 profile 属旧 Ghidra 私有模型，不属于本次 Capstone。caller 留存 `0xa006e350..0xa006e85c` 加正常模式必要前提 `0xa006e200..0xa006e224` / `0xa006e348`；未恢复整个 monitor。

## 原字复核结果

N=`0x62fca7f8`，M=`u32(N+0)`，elapsed 为既有整秒增量，不能替换为调用次数。以下加、减、比较均为 RV32 unsigned／模 2^32；静态事实不等于运行实测。

| 对象 | 独立核对的必要顺序与门 |
|---|---|
| A | `7b08..7b18` 读 `N+1c0`、加 elapsed、先存 sum，再以 BGEU(3599,sum) 走不触发支；故 unsigned sum>3599 才触发。`7b24` 清零，返回 1；否则返回 0。仅日志称 reboot，没有真实重启调用。 |
| B | `7bb0..7bbc` 累加 `N+1d0`；`7bb8` BLTU(14,sum) 到 `7bde` 清零并返回 1；不触发才写 sum 并返回 0。越阈路径没有先写 sum。 |
| C | `8870..887e` 累加并先写 `N+184`，threshold 正是 `N+188`；sum<threshold 返回 0，否则 `888c` 清零，经诊断调用端返回 1。不是固定调用次数或读取 N+18c 作阈值。 |
| D 采样 | `8930..8946` 对 `u32(N+188)` 做 DIVU 10；`N+190 += elapsed` 先存。未到间隔返回 0；到达后 `894e` 清计时，固定移动一格，无补跑多格、无余秒保留。 |
| D 差与复位 | `8958..895e` 从 H[1] 到 H[9] 顺序左移到 H[0]..H[8]；`8966/896a` 当前 `N+18c` 入 H[9]，`8968/896e` 使用已经移过的 H[0] 求 unsigned 差。`8970` 与 `N+1bc` 比较；达到阈值后诊断，再 `89c2` **重读** N+18c、`89c6` 清计时、`89ce..89d4` 将十项重置为该重读值，返回 1。 |

H[0..9] 是 `N+194..N+1b8`。这只证明累计计数差窗口，不能把窗口保证成严格墙钟时长，也不认证 N+18c 所有生产侧。

厂商原字独立核对：

- `0xa006895a` bytes `8bd64758` = word `0x5847d68b`，op=11、f3=5、top=11、rd=13(a3)、rs1=15(a5)、imm=4、shift=0。主仓 `ap01thead2.sinc:6615` 为 `th.swia`，先 `[a5]=a3` 后 a5+=4；与 `895e` 的循环终点 N+1b8 合成九次左移。
- `0xa00689ce` bytes `8b56f944` = word `0x44f9568b`，op=11、f3=5、top=8、rd=13(a3)、rs1=18(s2)、rs2=15(a5)、shift=2。SINC:6596 为 `th.srw`，写 `[s2+(a5<<2)]` 且不更新 s2；a5 从 0 到 9，共十次复位。均未把后半字误作压缩指令。

四入口均保存 N 与 elapsed；进入前读 `N+1e0` 非零则 `a005f3d8(handle,-1)`，出口分别 `7b4c/7bc2/88ce/89da` **重读** mutex 槽，非零到 `a01b3c8c`。返回值由保存寄存器明确设 0/1 后赋 a0，不消费 lock/unlock 返回；不得保证两次句柄相同、锁成功或网络成功。无本题内 heap 申请、所有权转移或 mutex 销毁；N/M 借用及有效性沿 caller 前提。

## record89 caller 核对

正常模式前提保留：`e222` a4=1，`e348` 仅 s11==a4 才进入 `e350`，故 `e786` 的 s11 在该分流为 1。state 从受 M+cc 锁保护的 M+c8 byte 读取；ready 为独立 `M+0x2000-0x510=M+1af0` byte。二者不能互相替代，也不能以 Q06 的底层阶段替代。

| 路径 | 接受的执行合同 |
|---|---|
| state2、ready 非零 | N+1cc 加 elapsed，并分别清 A/C 计时；旧 crash 处理继承。`e5a6` 旧 a0067be6 后 `e5b0` D；D=0 共同更新；D=1 到 `e768` a0067c20，只有许可返回 0 才请求 a01b3d12(N)。 |
| state2、ready 为零 | 旧状态处理后 `e6ae` B；B=1 请求 a0195ce4(M,N)。随后可加 N+1c8；`e6d4` A，A=1 调 a0069356 后跳共同更新，绕过 C/D；A=0 到 `e760` C。C=0 才 D，C=1 或 D=1 均经 a0067c20 门。 |
| state1 | B 后 s6==0 直接共同更新；否则 A，A=1 同上跳出。A=0 到 `e7b2` C；C=1 在 `e7ba/e7be` 请求 a01b3d12，**仍落到 e7c2 并调用 D**。D=1 经 `e7cc→e76e` 再请求 a01b3d12。C/D 两路均不经 e768 的 a0067c20，可在同轮产生两个请求。 |
| 其它 state | 旧 a0068d84 后 N+1c4 加 elapsed；s6==0 时在 N 锁下清 N+190、十项置当前 N+18c；然后 A；A=1 跳共同更新，A=0 才 C。`e83a→e7ca` 消费 C 结果，非零直请求 a01b3d12；此路径不调用 D。 |

因此作者的“state1 C 触发后仍 D 且不经许可门”与其它状态的区别成立。调用参数 N／M 来源、a1=elapsed 和动作门分流一致；不由日志或符号补成实际联网、重启或异步完成。

## 精确断边、验证与交付

止于 `a0067c20` 许可策略、`a0069356` 具体动作、`a0195ce4` 探测／配网及 `a01b3d12` 请求调用端；诊断 `a01ac568`、锁 `a005f3d8/a01b3c8c` 为公共 API 边界。未读新 callee body、未搜 N+18c 全部 writer；实际联网、云应答、线程完成、并发句柄稳定性及运行回绕均未认证。若需完整接口，应另行登记这些精确边，不能自动续派。

独立检查：四段顺序解码终点与总量 716 B、20 处关键原字断言、15 条 caller 边断言、2 条完整厂商字及 SINC 字段人工核对；脚本成功，`git diff --check` 通过。该脚本仅静态提取／断言，无固件、模型、SIM、QEMU、回放、构建、设备或外网执行，也未改 ROM、生产配置或分析器。

tracked 交付为本报告、同 stem `review.py`。ignored 中间产物清单为 `reverse/analysis/app-network-review-03-0041-20261025/review-evidence.json` 与同目录 `inspection.txt`，请父窗按原相对路径转存、核对后再清理任务树；不强制加入 commit。

计时：首个可得 UTC `2026-10-24 16:53:22`；报告落盘前采集 `2026-10-24 16:56:24`，可核实区间 182 秒，含材料读取、独立原字与 caller 检查及报告编写，不代表派发到交付全时。预测 4–6 分钟属派发估计，未以其倒算耗时。无外部队列或中断；本地工具等待包含读取／静态解析，未单独累计，不能当有效算力时间；token/cached 遥测不可得，不编造。提交收尾另计。
