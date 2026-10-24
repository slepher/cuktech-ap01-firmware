# P-19：ordinary 详情历史图的创建、首次消费与换端口生命周期

2026-10-25 Q-03整合纠正：[独立复核02](app-history-review-02-0041-20261025.md)核原字`0xa01afdbe→0xa00d7806`，该callee仅class walker，不能据此声称完整公共删除或free(W)。原“删除W”措辞现已限定；本注由管理窗口依据新复核补入，原历史验收保留，其余差集及P最终归还未知不变。

**可独立使用阶段已闭合但接口未闭；待非作者复核。** 已闭合正常路径的“选端口→新建 P/chart/series→首次与增量消费→返回后另建 P”，并纠正一个容易补造的行为：首次并不保证回填180点；maximum=0 不复位页面 cursor，普通离线显示分支也不等于图表整体复位。原详情历史 UI 已由父级恢复，本轮新增业务页面/算法为0；新增贡献是初始化和跨阶段接入合同。P 最终内存归还与公开 chart 内部所有权仍不冒认完整。

认领 P-19，代理 `app_history_research_01`；独占树 `.worktrees/batch-20261024-p/app-history-research-01`，基线 `5bbc331`。只写本报告与同名 analysis；主仓、其他人的文件只读。使用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 留存优先方法；未开/切 REA、修改模型、创建代理、执行目标/设备/网络/SIM/QEMU/回放/模型/构建，未改 ROM/生产/配置，未提交推送。首次可得起点 `2026-10-24 15:07:26 UTC`，计划约30分钟，证据收敛允许提前交；结束/墙钟见末节，token由父窗统计。

## 继承结论与查重

先读主树 reverse-design、管理顶部当前规则和 P-19 行；先核完整 [charge-complete](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/rehost/charge-complete-0041.json) 的 scope、native_creators、service_contract、verification、limitations、parent_runtime_verification，再核实际 creator 的较早完整记录及较晚 continuation。没有把旧 round4 pending 当成缺功能的证明。

父级普通详情 creator 为 `0xa01afd56`，后半在 `charge-complete#/creator_continuations/2`，`0xa01afea8..0xa01b0643`。父级 SIM 最终验收是本地服务/重建显示验收，独立180点 milliwatt/head/count 的服务设计不能反写为原 ROM 生命周期。chart styling/port scroll content arrangement 被父级明确列为 reconstruction。本轮不新增页面或重新计算 SIM 覆盖。

继承 [P12](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/history-reader-p12-0041-20261024.md)/[PR12](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/history-reader-review-pr12-0041-20261024.md) 已限定接受的 **I inline ring→P chart 标量接缝**，以及 [P10](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/history-sampling-p10-0041-20261024.md)/[PR10](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/history-sampling-review-pr10-0041-20261024.md) 的普通响应事件轴和非固定时基限制。writer 的物理顺序沿纠正后的结论：先写 next cursor，再写 samples[old_slot]，必要时再 cursor=0；本轮未重做算法或声称并发原子性。

与 summary 专席 `0xa00abd70/0xa00ac2d0` 的在线业务接口无本题增量重叠；仅共享 app/item 的上层身份。此处研究 page id `0x13` 的独立 P，绝不将 `I+0x3c/+0x1a4/+0x1a6` 与 `P+0x3c/+0x4c/+0x60` 合并；T+0xe reader完全未研究。

## 本轮复核或纠正：证据身份与必要边界

原件沿 [CATALOG](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/CATALOG.md)：0041 `ap01-1.0.2_0041.bin`，6,769,704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，RV32 LE，`file_offset=VA-0x9ffff000`。未另做原件哈希账。

| 留存 | 用途与准确限制 |
| --- | --- |
| `charge-0041-round4.json#/records/2` / `ev_e30acc99f01e5e79a06965e472ec0c1aee39a56a7c3e8ae8ad7fdef09673d74e` | creator body `0xa01afd56..0xa01b0643`，2286 B；旧 pseudocode 在 memcpy-like no-return 处被截断，不能当完整控制流。载体未保留 profile，不贴后来的 thead2 digest。 |
| `charge-complete-0041.json#/creator_continuations/2` | 较晚原 ROM Capstone5.0.7 RV32+C 静态续体，633条；本轮仅保留必要字段/公开API窗口，不复制大函数。它不是新 Ghidra profile。 |
| `charge-complete#/records/19` / `ev_709b5ff51cf4fb33e1b9ae866819ac7a860e0ffe029c2c56c7e9344ac037af88` | 增量 callback 原留存；沿 P12/PR12 的地址/厂商指令修正和 profile缺失局限。 |
| `system-complete.json#/cached_evidence/charge_a00f61ae` | 已有普通按键选择/返回流程；保留旧 custom/no-return/ABI局限，本轮补必要 caller原字节。 |
| `whole-rom-graph-20261023-4872/4873.json` | timer callback `0xa00a4d72` 的真实body134 B及公开chart callees。Evidence `ev_d070a07dec336b7b059eda11df8484b19f96194fdad1f6deacbe668fa6efcf99`、`ev_ea23526eac13e9e18f87b13b678a21823ea9ceee6c83a12f5a942c9cca9cd761`；Ghidra12.1.4 / `RISCV:LE:32:ap01thead2` / digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。未将其profile转贴旧creator。 |

本轮 [static-evidence.json](../../analysis/history-init-reset-p19-0041-20261024/static-evidence.json) 是只读原字节/地址核对结果：15窗842 B、278条指令，107断言PASS。工具为现有 E05 Capstone helper；厂商未知保留opaque，不改模型，不执行指令。完整creator/调用者留存阅读不是“完整算法新恢复”。

`P+0x60` 是 **byte消费cursor**，并非已确认的“首次装载完成flag”。后续相等分支不emit，以及初始化为0，并不提供独立首次/已回绕状态。`maximum=0` 是历史分支门，不能与 online/offline 一一等同。

## 真正新增：正常接入生命周期

### 选端口、对象来源与字段初始化

`0xa00f61ae` 普通列表按下 C1/C2/C3/A 分支，先调用 `0xa00f3b36(&snapshot,port)`，再保存当前/返回页面选择状态及端口，然后在 `0xa00f6ecc / 0xa00f6f78 / 0xa00f7024 / 0xa00f70d0` 调同一 creator `0xa01afd56(parent, snapshot scalars...)`。C1 的原窗 `6e44..6e7a` 明确 port=1、snapshot栈地址、parent=s2；其余端口沿既有完整caller。snapshot helper `0xa00f3b36` 取当前 item 并复制普通数值、连接/类型等标量，未把 I/ring指针交给creator。这里是短时借用并按值复制，不能跨回调保存原 item。

creator依次建立GUI对象W、分配0x14 B登记对象R、再分配0x6c B **P**；R=s7，P=s1，W=s2。`0xa01afde0..afdec` 的 `a0=0x6c→0xa008e362→s1` 直接绑定P。零化不是由函数名推断：`a008e362` 成功返回后重取原size，调用 `a0080d8e(ptr,size)`；后者改为 `(ptr,0,size)→a0024906`，沿已验通用fill合同，因而 **整个P初始为0，包括byte P+60、word P+4c和point输出槽**。不展开heap或memset内部。

| P字段 | 构造/保留行为 |
| --- | --- |
| `+0x3c chart*` | `0xa01affa0` 写入新chart对象；后续chart配置都通过该指针。 |
| `+0x40 series*` | `0xa01b0208→0xa019c64e(chart,color)` 的返回在 `020c` 保存。随后原序调用 `0xa019c82a(chart)`、`0xa019c89e(chart,series)`；保留API形状，不认证公开精确符号或库内部存储。 |
| `+0x44 marker*` | `0xa01b0224` 保存新GUI标记；设置大小6×6后隐藏；它不是样本缓存。 |
| `+0x4c cached_max` | 初始零化后 `0xa01b0266` 再显式word清0；与C=P+3c的C+10为同字段。 |
| `+0x50/+0x54 point输出` | 初始零；随后由图表取坐标API写入，沿P12。 |
| `+0x58 timer*` | `0xa01b026e/0272` 调 `0xa008bc64(0xa00a4d72,1000,chart)`，返回在 `0276` 保存。 |
| `+0x60 u8 cursor` | 来自P整块零化；本creator没有从I当前cursor装载它，也没有本题ring读入/180点回填循环。 |
| `+0x64 empty-state GUI*` | `0xa01b02b2` 保存；callback maximum分支切其可见性。 |

series前原序还调用 `0xa019c508(chart)` 和 `0xa019c5d0(chart,2,180)`；到此保留公开API参数，不能仅凭180就补造“已读180个历史点”或具体点数/时轴单位。creator没有接收I ring；未认证库内部是填0、NONE还是其他默认值。

timer创建后 **紧接** `0xa01b0278/027c→0xa008bd16(returned_timer)`。非空正常路径 `0xa008bd62..bd6e` 将 timer+14 的byte OR1；pause语义沿G05/G06已验合同。因此这个构造期timer不能当普通遥测的采样时基或当前活跃history producer。分配失败/NULL进入该公共API的行为不由非空窗口保证。本轮不展开演示callback算法或追所有resume writer。

最后 `0xa01b0612..0630` 保存 `R+0=0x13, R+4=P, W+0x10=R`，注册 `0xa00f1b8e`、事件0x29、userdata0。这把creator产物和callback `0xa00a72ae(app,0x13,...,&P)` 的真实P来源闭合；不是因偏移相同猜别名。

### 首次消费、后续门与离线边界

P12/PR12的同步分支原样适用：先过app/page/selected-port门，且 `u32(I+0)&0x400` 才处理图表。没有“page刚建立就无条件请求全部历史”的新门。可用于重建的分析伪代码如下（非原源码）：

```c
// new ordinary page: P is zero-filled; chart/series/marker already created.
P.cursor = 0;  // consequence of allocation, not a distinct explicit byte store
// Upon a matching normal callback:
if (I.mask & 0x400) {
    if (I.history_max == 0) {
        api_a0090470(P.chart, P.series, 1);
        hide(P.marker); P.cached_max = 0; show(P.empty);
        // Preserve P.cursor; do not consume I.cursor here.
    } else {
        hide(P.empty);
        api_a0090470(P.chart, P.series, 0);
        show(P.marker);
        emit_mod180(P.cursor, I.cursor); // old inclusive, new exclusive
        P.cursor = I.cursor;
    }
}
```

这里 `api_a0090470` 沿P12保留opaque公开调用，常量1/0不能误说成必然“显示全部历史”或“清零cursor”。第一次 `I.max!=0` 且 `I.cursor=c>0` 时从0提交槽 `[0,c)`；`c==0` 不提交，**即使I已绕整圈**。已绕回时的旧tail并不由creator补回；没有以“首次应该完整”修正原程序。每次非零maximum分支在emit前均调用同一个系列API，不能描述为只追加并完全保持旧series内容。

maximum=0分支清 cached_max、改变图表/marker/empty可见性，但不写cursor；若之后同P、同选端口再次到非零maximum分支，就从此前保存的cursor继续计算模180范围。普通离线数值/类型分支在record19中隐藏相关label/图标，并没有额外P+60清零或新建series步骤。原程序在这些已查分支中没有完整“断连→新代际→cursor同步”协议，不能承诺跨断连无旧cursor混合。I自身历史是否被另外的生产重置改变，承继生产生命周期限制，不追MCU或新接口。

每点仍是 `u16(I+0x3c+2*k)` 零扩展→`0xa00a64e4(value,P+0x3c)`；只借I同步取标量，图表不接收I/ring地址。P保留cursor、cached_max、chart/series/marker和point输出，图表的value复制/滚动内部仍是公共API边界，沿P12不额外retain I。

### 返回与换端口：新建，而非原地改绑

普通详情Return选择0xc路径 `0xa00f719e..71ae`，从app状态+3/+4恢复原列表/选择，再调用 `0xa00ded6c(a0)`。这里必须保留原枚举细节：`0xa00f7112..7192` 遍历所有子对象，遇id0x13仅保存其P到s6；a0保持**最后一次枚举返回的子对象Wlast**，Return没有按已保存P另查W。因此正常“新详情为最后子对象”的排列下删除详情；本窗口不能保证任意重排后仍删除同一个W，也不能把s6=P说成被传给delete的W。再次选C1/C2/C3/A进入上述creator，取得**新零化P及新chart/series**，不会将旧P.cursor直接赋给新P。未发现本题creator/caller中将同P直接rebind到另一I的路径；这是所查正常路径的限定结论，非全ROM无此入口证明。

必要DELETE接缝 `0xa00f1b8e` 只在 `(event.code&0xffff7fff)==0x29` 且 W+10的R非空时继续；取P=R+4，先把多项GUI指针置0，取旧P+58 timer调用 `0xa008ae58(timer)`，再清其他指针、调用 `0xa008ab8a(R)`，最后 W+10=0。原序保留：timer值在清空其他字段前已取出，不能改成先free再读。**该callback中没有直接 free(P)、也没有P+60清零**；不要把清指针/释放R写成P最终归还已证。公共GUI对子对象/series的销毁与P是否在别的路径归还，留未知，不扩主W退出或LVGL内部。

顶层失败已可定位：W失败直接返回；R失败调用class walker(W)；P失败日志→class walker(W)→free(R)。series/marker等公共构造返回后的原creator未在所述窗口提供独立失败清理判定，不能据顶层清理保证所有库分配失败安全。

## 设计策略（与原ROM事实分开）

重建可以使用公开LVGL chart/GUI API和自有series存储，按同步标量提交，页面自有cursor与max。若产品希望首次完整180点或断连后代际复位，应另存count/generation/时间戳或显式snapshot/reset事件；这些是设计选择，原P+60没有这些语义。当前证据足以复制正常页面的0起点/模180消费及新建换端口行为，不足以保证180秒、原库版本、库内部所有权或全局关闭活性。

## 未闭精确边与交付

阶段验收边界：端口snapshot标量→0x6c P零化→chart/series安装→匹配mask门首次/后续消费→maximum=0保持cursor→普通Return状态恢复及Wlast delete API→再选端口新建P，已能独立接入。正常子对象顺序前提明示，不将枚举的P和最后W混同。真正增量是这个跨阶段合同；旧详情历史UI仍计继承。

仍未知：P最终归还位置、所有间接resume/关闭入口、公开库内部series存储/分配失败、跨I重置代际一致性、T reader、物理时轴。没有用有限搜索推不存在，也未扩大到summary专席/MCU/主W退出。

一个真实后继seed：从已注册 `0xa00f1b8e` 的 `P=word(R+4)` 与 `0xa008ab8a(R)` 接缝，核同一page0x13登记容器的payload所有权约定及P的最终释放（先查已有page/container完整析构证据，止free/GUI边界），预计20–30分钟；本席不自动接题。若已有完整接受，直接继承收缩，不新增库内研究。

实际检查：只运行本题 [verify_static.py](../../analysis/history-init-reset-p19-0041-20261024/verify_static.py)，107项PASS；其本质为有界原字节/留存及调用目标核对，不代表执行证明或非作者验收。初始两次相对路径读取被登录shell切目录而未找到文件，随后显式Set-Location/绝对路径；一次有界decoder遇未支持厂商word后保留opaque继续，未改模型。无主动等待/任务中断；工具读取等待计入墙钟，有效工时未单独计量。交付检查和结束时间见末段。

结束 `2026-10-24 15:17:03 UTC`，墙钟约577秒；依据完整阶段证据收敛提前交付，不以时长凑工作。107项有界静态核对、JSON解析、UTF-8/尾换行/无尾空格、本地引用及独占路径状态检查通过。未提交推送；作者自核不代替非作者验收，交付后停止。
