# L03：设置 mode 的两处 UI 调用、字节持有及通知/写服务接入

2026-10-24；基线 `565dc6e`；独占树/分支 `re0041-l03` / `codex/re-0041-l03`。**两处旧 UI call 都把正常选择值送入 `a00ab478`；它只在旧 U8 与完整传入 a0 不等时，将低 byte 写到 `62fc909a`，随后同步调用通知 `a00a5bbe(3)`，再调用系统配置写入口 `a00ab274`。两处 UI 都覆盖返回 a0 后继续显示调用，不据保存结果决定后续。** 这是静态接入合同，作者验证已通过，尚待独立技术复核；不认证实际文件落盘成功或原 ROM 全部设置恢复。

采用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。用户明确恢复取代历史停止条款，其余约束继承。仅在独占输出写报告/静态检查；ROM和旧忽略证据从主仓绝对路径只读。未打开/切换共享 REA target/database，未运行固件、SIM、构建、历史回放、输入实验、设备或外部服务，未改生产代码、ROM、配置或分析器模型，无下级 agent。函数名/伪代码是映射，不是原源码。

## 继承结论：已有→行为→局限→精确缺口

|既有出处|已有行为/证据|本轮边界|
|---|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、[J03](settings-persistence-reuse-gap-j03-0041-20261024.md)、system/guide complete|设置 UI、ScreenSave/ScreenOff 消费、SIM 保存及跨进程读回已留存；SIM服务以宿主文件/回滚实现|直接继承，passed-in-sim 不证明 ROM 字段、回滚、flash或文件成功；不重跑、不重计|
|旧 `settings-0041-round2b.json#/records/10`，`ev_d2c060238142516e1df7a388e5984d96623578a75366a96c1472e9ed8c8df9fb`；system-complete cached settings|旧 handler 已完整留存，两处 call、type1c 对象查找、状态 3b/3c 分支和后续显示调用早有|仅核实参、返回消费及必要接入；不重导大 handler，不把已有 caller 当新地址发现|
|J03 的 whole-ROM extent `ev_5334e642630bb4d54d7d94302fc3589476d1f18aa9d513ec57bf017024348c9d`|a00ab478 为48B，callee目录 a00a5bbe/a00ab274 已有|extent/目录不自动证明字段或保存语义；本轮补必要原字段|
|旧 `whole-rom-private-20261023-071.json`，`ev_cf4c97ae60f1edbe9156a19d0427799c7c068d79ed1d916e7d8cdc3dd61c3c58`|a00ab274 的完整原汇编/伪码早已保留：路径、mode、非零返回门、8/1写服务、关闭|复用原 body，只核接入锚点；这一写服务本体不是本轮首次恢复，不复制原 body|
|[普通配置后端报告](knowledge/0041-sim-wifi-selection-gaps.md:65)、J03 的背光/蜂鸣/地点专项|`/data/sysconfig.bin` 8B 样本已知且与 PSM 区分；其他配置调用已有独立合同|不把本文件混成 ck_config/PSM 或 SIM AP01SCF1；不重做后端/NVS/CRC/安全主题|
|[L01](settings-mode-entry-l01-0041-20261024.md)|只有未验证脚本草稿，新增0|不继承为技术通过；口头进展及草稿不当成果|

J03已完成旧 complete/final ZIP、父级 cached settings 和近期报告的范围去重。本轮复用其有界结论，并再次核旧 caller/parent/writer 身份；相关近期非管理 Markdown 精确 token `a00ab274/62fc909a/SysSettingsWrite` 查询没有其他已验收合同命中。这个限定载体查询不表示历史从未分析，不据无标题另开题。备选 `a00ab4a8` 不在本题范围。

## 本轮复核或纠正

原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，`file_offset=VA−0x9ffff000`。本路 [verify.py](../../analysis/settings-mode-contract-l03-0041-20261024/verify.py) 不执行 L01 草稿；使用只读离线指令工具读取必要锚点，并独立解算 JAL、BEQ 和压缩分支字段。结果见 [evidence.json](../../analysis/settings-mode-contract-l03-0041-20261024/evidence.json)。没有新 REA Evidence ID、全函数导出或模型规则。

|核验点|结论及限制|
|---|---|
|a00fd1d0 / d1e8|原字 `374afc62` / `130aca02` 得 `s4=62fc402c`。L01 草稿将首字误写为 `375afc62`；本轮修正独占新脚本，未修改旧草稿。这只是未验稿纠正，不是已接受功能合同推翻|
|a00feac4/ac8|`03451a00` 为 `LBU a0,1(s4)`：从 `62fc402d` 零扩展一 byte，JAL 目标独立解算为 a00ab478。另一处 adc/ade 传立即数3到同目标|
|a00feacc..ad4 / ae2..aea|两路径都重取 local58、设置 a1=0/1、以 local58+8 的 word 覆盖 a0，再调 a018f232。两 call 之间无返回判断；不把显示提交称为存储成功反馈，不展开既有 UI callee|
|a00ab480/484|LBU 旧 `G+2`，`6301a702` 是 `BEQ a4,a0→a00ab4a6`。比较零扩展旧 byte 与完整 a0；setter本身没有先将输入mask到8位。当前两 UI 输入分别为U8/3，不研究其他输入|
|a00ab490/494/496/49a|`SB a0,2(a5)` 写 `G+2=62fc909a`，然后 a0=3 调通知，再调写入口；相等臂直接返回，无写入/通知/写服务。写入先于两个调用，没有失败回滚门|
|a00ab49e..4a6|两出口仅尾声/ret，没有显式布尔成功值。不能把该 helper 的残留 a0 当稳定保存状态；当前两 UI 也不消费它|

早期 type1c constructor 读取 `62fc909a==3` 设置选项的事实沿J03继承；它与本轮实际 setter 字节一致，但不因此重新恢复整个屏保时长映射或为 3 之外各值赋正式枚举名。

## 真正新增：局部状态/通知 ABI 到旧写服务的连接

令 `G=62fc9098`。本题补充的是两 UI 实参→`G+2`→通知参数→旧写服务的连接与原序，而非新的设置页面或文件服务：

```c
// 局部正常合同，非原源码；不声明返回类型或成功状态。
set_mode(value):
    if (load_u8(G+2) == value) return;
    store_u8(G+2, value);
    notify(3);                 // a00a5bbe，同步遍历当前登记链
    write_system_settings();   // a00ab274，已有 body

UI_selection_3b:
    set_mode(load_u8(62fc402d));
    existing_display_call(load_word(local58+8), 0);
UI_selection_3c:
    set_mode(3);
    existing_display_call(load_word(local58+8), 1);
```

通知入口保存 reason=3，从 `62fcb4ec+4` 读首 node。每个 node 的 word0 非零时，原位调用 `callback(load_word(node+4), G, reason)`；word0为空则直接继续。callback返回后重读 `load_word(62fcb4ec)` 作为链接偏移，将其加到当前 node，再读 +4 得下一节点。`a00a5bf4..5c0a` 原字及三个压缩门已核。callback 的 a0 返回被后续读/取参覆盖，无成功判定。传递的是全局 live `G` 指针，没有为每个订阅者复制 byte/结构，也没有本入口的新分配、free 或所有权移交。这里只认证遍历/实参，不认证登记者身份、节点所有权、注销或并发协议；不将同步函数调用泛称异步消息。

`a00ab274` 的旧 body 与本轮原字锚点一致：以路径 `a026a21c="/data/sysconfig.bin"`、mode `a026a218="wb"` 调 `a0134856`。返回0走已有诊断并共同返回；非零 H 保存到 s1，然后调 a00a46e8，将其**低16位**以 SH 写到 `G+6=62fc909e`，再调 `a0134adc(G,8,1,H)`，最后以 H 调 `a01a8de6`。8和1是服务实参；本题不凭字符串外观认证这些函数为某个精确版本 libc 或推广其全部读写返回/单位协议。

写调用返回后的第一条 `a00ab2e0` 直接用 H 覆盖 a0，关闭调用后也只进共同尾声；本层不检查两者返回，不读回验证，不回滚此前 RAM 写。写源是通知完成后的全局 G，通知期间若其他代码修改 G，本层没有快照或重置；这里只陈述读取位置/调用顺序，不作重入、异常或缺陷验证。非零H路径中 G+6 的更新发生在通知之后，不能宣称通知回调已看到本次新生成的该 halfword。a00a46e8算法未命名为CRC/校验和；确切算法不在本题已证明范围。

因此可说“改变模式后通知，并尝试系统配置文件写服务”，不能说“模式已成功持久保存”。文件handle只在本次 writer 调用中持有并交关闭服务；成功/失败的底层资源释放由下层服务合同限制，未观察实际运行。原字节复核和旧 writer再引用均不重计新增，新的解释范围只有上述字段/ABI/返回消费/服务连接。

## 精确未闭与实际验证

本题两 caller、helper 的实际 byte/比较、通知三参、旧 writer 接入与返回不消费已得到静态证据。完整 ROM、完整设置家族和底层持久化成功仍未完成。精确未闭包括：登记链的真实 subscriber/注册与生命周期；`a0134856/a0134adc/a01a8de6` 下层完整服务返回/所有权实现与实际写入保证；a00a46e8算法、G全部8B的正式结构定义、实际设备落盘与重启效果。没有无种子扩全NVS/driver/GUI。

可交主窗口的一个后继是本题独立技术复核：仅核两caller、G+2比较/发布、通知实参及返回丢弃、旧writer非零门/SH/8,1/H/关闭接入，不重导 handler 或文件服务。J03备选a00ab4a8仍有48B extent及fe9f2/fea0a真实旧种子，但本轮未验证其差异；必须另按字段/地址去重后派发，不凭相邻/同长套用本题合同。

实际运行独占 verify.py：**43项静态检查 PASS，35个稀疏锚点（含11个独立JAL目标），3个压缩门与1个BEQ独立字段/目标校验，3个必要字串**。JSON解析、报告相对链接和 `git diff --check` 通过。L01草稿未运行，旧SIM验收未重跑，作者静态自检不替代后续独立技术接受。
