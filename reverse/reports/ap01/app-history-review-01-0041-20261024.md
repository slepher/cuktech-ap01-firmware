# P-19 非作者复核：普通详情历史初始化、消费与换端口

2026-10-25 Q-03整合纠正：[独立复核02](app-history-review-02-0041-20261025.md)核原字`0xa01afdbe→0xa00d7806`，该callee仅class walker，不能据此声称完整公共删除或free(W)。原“删除W”措辞现已限定；本注由管理窗口依据新复核补入，原历史验收保留，其余差集及P最终归还未知不变。

**可独立使用阶段已闭合但完整接口未闭；限定接受。** 本轮非作者 `app_history_review_01` 接受 P-19 正常创建、首次消费、maximum=0 保留 cursor、返回及再次选端口的差集。行为纠正0，新增业务0。P 最终归还、任意子对象排列下的正确删除对象、所有间接关闭/resume 及跨生产重置代际一致性仍未闭。

基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`；管理登记为 [23:44 HKT 当前节及 P-19 行](rolling-management-0041-20261023.md)。按父窗明确授权直接在主树写本报告和同名 analysis，不建 worktree、不改共享表或作者成果。预计8–12分钟（定位2，生命周期原字4–6，交付2–4）；实际起止及提前收敛说明见末节。

已读 [reverse-design](reverse-design.md) 3.1/3.2/5.1/7，以及 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，使用留存优先、原字核查和事实/推断/未知分账。未打开或切换共享 REA、执行目标/模型/SIM/QEMU/构建/历史回放/网络，未改 ROM、生产、配置、分析器，未派下级、提交、推送或 reset/clean。

## 继承结论

- [PR12](history-reader-review-pr12-0041-20261024.md) 已接受 I inline ring→P 图表的标量接缝、0x400 门、maximum/cursor 分支、模180消费及图表胶水。本轮不重做 ring 算法或公开 chart 内部。writer 先发布 next cursor、再写 old slot、按需回绕的纠正直接继承；不推并发原子性。
- [P-19 作者报告](history-init-reset-p19-0041-20261024.md) 及同名 analysis 是待核载体，不是非作者证明。父级 `charge-complete-0041.json` 的 scope/service_contract/verification/limitations/parent_runtime_verification 已核：独立180点 milliwatt/head/count 是宿主 SIM 替代设计，passed-in-sim 不能证明原 ROM 首次回填、物理时间或库所有权。
- 原件身份继承 [CATALOG](../../../roms/CATALOG.md)：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，RV32 LE，`offset=VA-0x9ffff000`；没有新造摘要清单。

必要来源：`charge-0041-round4.json#/records/2`，Evidence `ev_e30acc99f01e5e79a06965e472ec0c1aee39a56a7c3e8ae8ad7fdef09673d74e` 是旧 creator；`charge-complete-0041.json#/creator_continuations/2` 是 Capstone5.0.7 RV32+C 静态续体；前者 no-return/custom/profile 缺失局限不由续体抹去。增量 callback record19 的 Evidence `ev_709b5ff51cf4fb33e1b9ae866819ac7a860e0ffe029c2c56c7e9344ac037af88` 及其 profile 缺失沿 PR12 保留，不贴 later thead2 digest。

普通 caller 实际留存路径为 `reverse/rehost/system-complete-0041.json#/cached_evidence/charge_a00f61ae`。作者所写 `system-complete.json` 在本主树不存在，本报告明确补全文件名；这是来源定位补充，不改变行为结论。snapshot 为 `charge-complete-0041.json#/records/7`，Evidence `ev_e3f2aa4487640b81304640105603339b7213c4200fb9cd41dd4ee2535cae0480`；其通用模型、unreachable/custom 局限照留，不把 pseudocode 当独立完整执行证明。

## 本轮复核或纠正

| 差集 | 判定、原字与边界 |
| --- | --- |
| P 来源、大小及零化 | 接受。`0xa01afde0:1305c006` 独立 I 位域为 `addi a0,zero,108`；`afde4/afde8` AUIPC/JALR 目标 `0xa008e362`；`afdec:aa84` 是 `s1=a0=P`。`e36c` 保存 size，`e370` 分配，非空后 `e378` 重取 size 到 a1，`e37c→0xa0080d8e`；`0d96:2e86` 令 a2=a1，`0d98:8145` 令 a1=0，`0d9a→0xa0024906`。沿已有 fill 合同，全部0x6c清零，故 P+60 byte 初始0；不只凭函数名推 calloc。 |
| W/R/P 身份与回调注册 | 接受。W=s2，R=s7，P=s1；`0xa01b0614/0618/0620` 独立 S 位域分别为 `R+0=0x13`、`R+4=P`、`W+0x10=R`。`0626` 事件0x29，`062a` 构造 callback `0xa00f1b8e`，`0630` 注册。故和 PR12 查找 page0x13 所得 P 是同一登记类型，并非 I 与 P 的偏移偶合。 |
| chart/series 安装 | 接受。较晚续体 `0xa01affa0:c8dc` 独立压缩 store 位域为 `P+3c=a0`。`0208→0xa019c64e` 返回经 `020c:a8c0` 保存 P+40；`0210→0xa019c82a`，`0218→0xa019c89e(chart,series)`，保留调用顺序。`01d2` 给180、`01d6` 给2，只接受 API 参数，不能据180推已消费180点。库初值、精确符号、版本和 series 内部存储不认证。 |
| cache/marker/timer | 接受。`0266:23a60404` 是 word P+4c=0；marker 保存 P+44 并配置6×6/隐藏，非样本数组。`026e/0272→0xa008bc64` 的参数为 callback `0xa00a4d72`、1000、P.chart；`0276:a8cc` 保存 P+58，`0278/027c` 即调 `0xa008bd16`。非空已验 pause 合同沿用；不能把该刚创建 timer 当活跃历史采样 producer。 |
| 首次及 maximum=0 | 接受 PR12 接入后果。初始化没有独立 loaded/generation/count；仍需匹配 app/page/port 且 I.mask&0x400。P.cursor 初值0，所以非零 max、cursor=c>0 首次提交[0,c)，c=0不提交，已绕整圈也不能区分。max=0分支不写 P+60，重新非零从旧 cursor 继续。离线 label 分支不等价整个历史复位。 |
| 换端口新建 | 接受正常 caller。`6e44..6e7a` 提交 `(stack snapshot,1)` 并保存选择状态，`6eb8..6ecc` 读 snapshot 标量参数；四 callsite `6ecc/6f78/7024/70d0` 独立 JAL 均到 `0xa01afd56`。snapshot record7 写入标量，未返回 I/ring 指针。返回后再次进入 creator 是新 P/chart/series，不复用旧 P.cursor；有限正常路径不证明全 ROM 没有别的 rebind。 |
| Return 删除对象身份 | 接受作者保留的 Wlast 限制。本轮额外核10 B `7194:3147` 为 `a4=12`，`7196:6384e700` 为 `beq a5,a4,719e`，落实 Return=0xc。枚举 `7180→0xa00dcee4` 返回 W；`7184:1c49` 取 W+10；id匹配仅 `718c:03ab4700` 将 R+4 存 s6=P。循环终结至 `719e..71ae` 没有把 s6 移入 a0，`71ae→0xa00ded6c` 使用最后枚举返回的 Wlast。正常详情最后子对象时才删除详情，不保证任意重排。 |
| DELETE 释放与原序 | 接受。event低掩码比较0x29后，`1bac` 取 W，`1bb0` 取 R=W+10，`1bb8` 取 P=R+4。`1bbc:a84c` 已把旧 P+58 timer 读入 a0，随后清 GUI 指针再 `1bea→0xa008ae58`；`1bee:4a85` 明确 a0=R，`1c10→0xa008ab8a`，最后 `1c14` 清 W+10。所查完整 callback 无 free(P)，无 P+60 store。归还 R 不能升级成归还 P 或认证 GUI 子对象内部所有权。 |
| 顶层失败 | 接受作者限定：W零直接退出，R零调用class walker(W)，P零日志→class walker(W)→freeR。不据此保证 series/marker 等每个公共构造失败时均安全。 |

本轮原字检查使用 [独立脚本](../../analysis/app-history-review-01-0041-20261024/verify_independent.py)，只用 Python 标准库，不导入/执行作者 `verify_static.py`、E05 decoder、Capstone 或任何指令模型。作者 JSON 仅作地址/bytes 待核载体；15窗842 B、278指令边界与原件逐条比对，另独立提取必要 I/S/J、AUIPC/JALR、压缩 MV/LW/SW 及 Return 分支位域。结果 [independent-checks.json](../../analysis/app-history-review-01-0041-20261024/independent-checks.json) 916项通过；数量含机械字节/边界断言，不当业务恢复量。另按原件核 chart store2 B、Return门10 B，未导出整函数或做全ROM负搜。

## 真正新增

新增业务功能0；非作者提供 P-19 接入差集的限定接受和来源文件名补全，没有作者行为纠正。额外10 B Return门核对是既有分支的独立证据，不另计恢复功能。

正常阶段足以重建（分析伪代码，非原源码）：

```c
select_port(k): snapshot_scalars(k); new_W_R_and_zeroed_P(0x6c);
                install_chart_series_marker(); P.cursor = 0;
matching_callback(I): if (I.mask & 0x400) {
    if (I.max == 0) { opaque_series_api(1); P.cached_max = 0; /* cursor unchanged */ }
    else { opaque_series_api(0); emit_mod180(P.cursor, I.cursor); P.cursor = I.cursor; }
}
Return: restore_list_selection(); delete_gui(Wlast);
DELETE: read_timer(P); clear_gui_fields(P); delete_timer(); free(R); W.userdata = 0;
```

`emit_mod180` 为 PR12 已验标量接缝，不在此重推算法。`P.cursor=0` 是整块零化后果，不冒称显式 byte store。`DELETE` 是原序摘要，不能据此补 free(P)。

## 未闭精确边与交付

完整接口仍未闭：P 最终归还；所有间接关闭/resume入口；非正常子对象排列下 Wlast 与详情 W 的一致性；公共图表内部 series 初值、复制/滚动及失败所有权；I生产重置与P cursor 的代际一致性；T reader和物理时轴。这些不因本阶段接受而关闭。

一个后续种子仅保留作者已有边：`0xa00f1b8e` 中 `P=word(R+4)` → `0xa008ab8a(R)`，先按 page0x13 登记容器的已有完整析构证据查 payload 所有权及 P 最终释放；止通用 free/GUI API，不默认展开公共库，不自行续题。

首个可得 UTC 开始 `2026-10-24 15:45:38`。无主动等待、排队或任务中断；工具读写等待计入墙钟，未单独测量有效工时。少量来源定位失误（根目录 reverse-design、缺少 -0041 的 system-complete、一次 list/string 误判）均只读失败后按真实来源修正，未更改源文件。开始到交付约数分钟，低于8–12分钟预测：全部关键窗口已定位，沿 PR12 直接收缩，独立检查一次通过，提前收敛即交付，不补时扩题。

token 实际 input/cached input/output/reasoning 由父窗本轮可见 rollout 快照统一统计；cached input 单列。本子窗没有独立用量计数，记不可用，不估计。最终 UTC、墙钟及格式/路径检查见同目录 delivery-checks.json。

结束 `2026-10-24 15:49:04.656 UTC`，墙钟206.656秒；格式、全部本地引用、JSON解析和独占路径 diff检查通过。两个JSON按仓库规则保持原路径本地ignored；新报告及复验源码未提交。其余工作树成果不改动，交付后停止。
