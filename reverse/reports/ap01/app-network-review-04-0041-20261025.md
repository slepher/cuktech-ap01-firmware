# Q17 非作者复核：ready 复位、外部许可与 probe 提交

**可独立使用阶段已闭合但接口未闭。** 限定接受作者 `bc4ed028de4aa5d60f0fc88578f2f66bd278192e`：三 helper 与旧 monitor 的接合合同成立，语义纠正0，新增业务0。这里闭合的是字段复位、许可判断和请求构造/提交阶段；probe 异步持有、完成与资源归还仍未闭合，不能表示联网成功。预估2–4分；可见UTC首采样2026-10-24 17:25:42，复核结束采样2026-10-24 17:26:43，差61秒（不含随后报告写入/提交，不冒称完整任务或有效工时）。工具等待和token无可靠独立遥测，不编造。

认领 Q17，非作者 `/root/app_network_review_04`；独占分支 `codex/app-network-review-04-20261025`，基线 `8782ea6916e6879af8c044af60d2e5aa6988fb74`。仅本报告及同stem analysis；主仓流程/认领表只读，不回退其他协作者，不推送，不派下级。采用 REA 技能的观察/推断/未知区分，不切换共享 REA、不生成新 REA Evidence ID。

## 继承结论与证据边界

按主仓 reverse-design §3.1/3.2/5.1/7 与 rolling-management 顶部/Q17补位行执行。继承Q09/复核03四计时门、state1例外及旧4000ms reboot叶，不重验计时门或monitor全体。作者报告及其 verification.json/inspection.txt仅读取定位，未执行作者verify.py。

独立读主仓原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`：6769704 B，重算SHA256为 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。字节映射 offset=VA−`0x9ffff000`；仅解码 `a0067be6..a0067c1f` 58 B、`a0067c20..a0067c9f` 128 B、`a0195ce4..a0195e59` 374 B，共560 B，并校验已有 `otn.ntp` 常量。散列读全文件不等于解码/研究全ROM。

必要caller直接读旧 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/89/normalized_result/assembly` 的有限窗口，共85行，Evidence `ev_4150d456a78d9d2a6c00fda793101e8915ff107084a8356d31e91552e2b072de`，历史profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。这是既有静态证据，不是本轮运行观测。未读任何新callee body或G writer。

## 本轮复核与纠正

| 验收项 | 独立静态证据与接受范围 |
| --- | --- |
| ready字段与顺序 | `a0067bf2` 读N+1e0；有句柄时锁API(-1)；`a0067c02` 原字 `23a8041c` 为 `sw zero,0x1d0(s1)`；有句柄时解锁调用位于c08/c0c；`a0067c12` 原字 `239af41c` 为 `sh a5,0x1d4(s1)`，a5=1。半字置一在解锁之后，空句柄仍执行两字段写。没有显式建立布尔返回；caller不检查返回。 |
| ready接入D前 | record89 `e5a6/e5a8` 传N调用ready，随后 `e5ac..e5b0` 调D；并非D成功才复位。ready前N+1cc累计elapsed、N+1c0和N+184分别在N锁下清零沿必要caller片确认。 |
| G独立对象 | `a0067c2c/c30` 得 `G=0x62fcad78`，读取G+0作为锁句柄，锁内 `c42` 读取u8(G+8)。不合并N、M、G；未证明状态生产者。 |
| 许可返回极性 | 值<=30走 `0x40108000` 掩码，置位仅15/20/30；大于30仅50命中。命中置s2=1，其他0，统一解锁后 `c98` 将s2返回。record89 `e768` 调门，`e76c` 非零跳过，0才经 `e76e..e774` 请求 `a01b3d12(N)`。日志文本不证明枚举名称。 |
| state1例外 | 继承state识别，必要caller `e7b2` 的C命中直接请求；随后 `e7c6` 的D命中跳到e76e也直接请求。均绕过e768许可函数，不能推广成统一重连门。 |
| probe输入和DNS分支 | `a0195cf4/cfa` 保存N/M；3 B prefix与16 B domain独立局部区初始化。prefix API返回不检查，随后(prefix,3)结果选择格式(domain,16,"%s.%s",prefix,默认域)或复制15 B并补NUL。`d56` DNS调用返回0才经 `d5e→dba` 构造请求；非零把s1=-1后退出，不提交。prefix/格式/DNS各止API边。 |
| R的20 B布局 | R=fp−74；+0为DNS输出IP word；+4以半字写8053；+6两字节无本helper显式初始化，保留padding未知；+8为a0068a26；+c为原N；+10为7000。7000单位未证明，IP字节序止API边。 |
| 提交参数与返回 | `e40..e52` 明确 `(M+0x128,4,"otn.ntp",R,20,M+0xe8)`→a0119638；`e56` 保存a0并经 `d9e` 原值返回。失败路径返回-1。caller `e6b4..e6bc` 和 `e794..e79c` 均传(word(N),N)，下一步不检查probe返回。 |
| 局部寿命 | probe帧0x90 B；domain、R与日志buf64属栈。buf64由首word清零加剩余60 B清零组成，仅供IP格式/日志调用。共同epilogue恢复栈；本helper无可见heap/socket取得释放或N/M转移。API是否复制R、持有多久及callback行为未知，不能由返回0或B触发推成探测/联网完成。 |

本轮独立脚本 [verify.py](../../analysis/app-network-review-04-0041-20261025/verify.py) 使用Capstone5.0.7完整解码560 B，27项寄存器/位宽/分支指令断言、掩码四值枚举、调用目标/常量算术、原件摘要、必要caller断言通过。完整原字和指令留 [verification.json](../../analysis/app-network-review-04-0041-20261025/verification.json)，文本留 [inspection.txt](../../analysis/app-network-review-04-0041-20261025/inspection.txt)。手工审阅顺序、参数寄存器与栈布局；断言不是所有权或异步完成证明。

## 真正新增与未闭精确边

真正新增业务合同0；本轮新增为独立验收证据和完整ROM摘要核验。未发现作者需要修正的行为主张。

精确停止边仍为 `a0195e52→a0119638` 的R复制/借用与任务销毁、callback `a0068a26` 的完成路径；G+8生产者未知。`a00b532c`、prefix/formatter、`a01b3d12` 与公开锁/日志API内部保持opaque，未展开新callee、writer、模型或全系统推理。若重建必须解决原二进制异步ABI，应先查已有合同并登记 `a0119638` 最小交接边；此建议不是本轮新研究授权。

全程仅静态文件读取/解码，没有执行作者脚本、固件、模型、SIM/QEMU、回放、构建、设备或外网，没有修改ROM、生产配置或分析器。tracked交付恰为本报告和verify.py；ignored待父窗转存恰为同stem analysis内verification.json、inspection.txt。本地commit交付后停止，主窗负责合并、核对转存和清理。
