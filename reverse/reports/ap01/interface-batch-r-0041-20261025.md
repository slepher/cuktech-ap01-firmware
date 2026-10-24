# R：持续三席的底座与应用接入静态研究

**滚动检查点，仍在进行，不是整ROM或本批全接口完成。** 用户于香港2026-10-24 23:54明确要求持续三个agent、结束补位。新任务全部fork_turns:none，领域/类型序号递增；未重用旧上下文换题。管理表唯一维护者为主窗口。

## 当前成果与边界

|认领|关键进展|状态/断边|
|---|---|---|
|Q-01 摘要五槽|普通/非零类分类、0x60→0x8840→0x8→0x10覆盖、C2借C1 mode、同S零初始化|[独立复核02](app-summary-review-02-0041-20261025.md)限定接受；早期u16快照时点纠正1项，经作者修正确认；全writer/重入/并发/退出未闭|
|Q-02 底座描述表|cmd55原payload+23，与24B缓存分离；count ff沿旧值；撤旧再建|[独立复核02](dock-control-review-02-0041-20261025.md)限定接受；实际远端条目值/顺序仍缺，不证selector=i+1|
|Q-03 历史页关闭|具体base class、E.original_target、timer→freeR→清W挂接；同P helper止外观|[独立复核02](app-history-review-02-0041-20261025.md)限定接受；纠正旧P19失败callee仅class walker，不证明freeW；P最终归还未知|
|Q-04 MiIO hook有限输入|六业务实参与a6目标寄存器分离；有限xref无writer|[独立复核01](app-miio-review-01-0041-20261025.md)限定接受其检查范围；当时未得实值；Q07以新映射种子另行接续|
|Q-05 MiBLE双角色ATT|role0本机UUID16、role1对端value handle；本地submit/同步临时帧copy/完成边界|[作者01](app-ble-research-01-0041-20261025.md)已交付，app_ble_review_01运行中，旧M03身份措辞待非作者确认后补注|
|Q-06 Wi-Fi连接→IPv4|主体旧根已有；新增40B handle close清槽，区别link-down interrupt不清槽|[作者01](app-network-research-01-0041-20261025.md)已交付，app_network_review_01运行中；真实DHCP/通知/并发止API|
|Q-07 MiIO hook新种子|既验启动复制覆盖62fc4944，ROMa0004458+0xc初值a011860a|app_miio_research_02运行中；新初值不是运行时从未覆盖的证明，尚未验|

底座MCU三载荷仍是不透明输入，无架构/解封装新种子，不将高熵当已证加密；不重开架构猜测、b50a/b50d reader负搜或无种子P释放搜索。公开库止API，已覆盖netMonitorTask不再重派。

## 时间、token及估时校准

派发/会话创建/平台完成事件及实际token见[usage-snapshot.json](../../analysis/interface-batch-r-20261024/usage-snapshot.json)；各作者/复核采时、同题修正与中断见[task-timing.json](../../analysis/interface-batch-r-20261024/task-timing.json)。采集源码[capture_usage.py](../../analysis/interface-batch-r-20261024/capture_usage.py)只读本root、本轮新增子会话，跨午夜读取24/25两个日期目录。

本轮基线是用户继续指令UTC15:54:21.864之前最后token遥测；root只算差值，旧Q三组/P批次不重加。cached input单列且已包含于input；reasoning已包含于output，不重复相加。快照不含其后输出、不可见内部审批/工具用量，不是账号计费。实际墙钟含正常工具等待，不冒充有效计算工时；任务报告有可得等待数字时单列。

研究先拆阶段再合成同接口包。实际Q01主研究699.047秒，Q02 337秒，Q03 227.555秒，Q04 188.698秒，Q05 434.98秒，Q06检查339秒，均因充分定位/覆盖收缩/公开API或外部输入边界而提前；原20–30分钟预测继续偏高。新题必须先核是否有真正未闭多阶段，不把预算作预测，不追库凑量。充分定位短复核实际约100–143秒，Q01较大差集359.964秒含65.240秒中断；后续按差集校准。

## 代理生命周期与保存

环境仍只有中断，无关闭/释放工具。按用户最新授权，完成保存整合后新建独立上下文补位；没有声称completed代表已释放，没有增加上限。若运行时拒绝新建，保留拒绝事实并报告，不跨题复用绕过。

一次补修顺序错误已记录：先于16:09:30.825唤醒摘要作者，16:09:41.533才中断复核，约10.708秒四席重叠；随后恢复三席。作者修完停止后16:10:46.773恢复同题复核。以上为工具调用发出时间，不是有效工时边界；后续先暂停再启补修。

全部原有tracked/untracked/ignored成果保留；只写独占新报告/analysis及主窗口管理/索引/交接补注，不reset/clean、不建删worktree/分支、不暂存提交推送。旧P19及复核01保留原历史并增加class walker精度纠正，未回写成旧作者已验证。HEAD保持5bbc331ab429fb76e956e50b8081c56f8d278b11。没有执行固件/模型/SIM/构建/刷机/网络或修改ROM/生产配置/分析器。
