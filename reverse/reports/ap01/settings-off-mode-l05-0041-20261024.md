# L05：另一设置 mode 的 byte 发布与共用服务接入

2026-10-24；基线 `1dcbfe6`；独占树/分支 `re0041-l05` / `codex/re-0041-l05`。**a00fe9f2 传立即数3，a00fea0a 传 `62fc402f` 的零扩展 byte，均进入 a00ab4a8。该 helper 比较旧 `62fc909b` U8 与完整 a0，相等直接返回；不等则先写低 byte，再通知 reason=4，最后进入 L03/L04 已接受的共用 writer。UI 两处均不消费 helper 返回。** 本题为局部正常接入解释，作者验证通过、待独立复核，不证明实际持久化成功。

使用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。仅静态读取主仓 ROM/既有证据，独占报告及 analysis 写入；没有共享 REA target/database、固件、SIM、构建、历史回放、输入实验、设备、外部服务或模型执行，没有生产代码、ROM、配置、分析器模型改动，无下级 agent。其他 agent 正在工作，本题未撤销或写入其文件；M01 的 a00a46e8 算法不接管。

## 继承结论：已有→行为→局限→精确缺口

|既有出处|已知行为与覆盖|本题处理|
|---|---|---|
|[J03](settings-persistence-reuse-gap-j03-0041-20261024.md)、旧 settings-round2b records[10]、system-complete cached settings|a00fd1ac 大 handler 的两个真实 call 与 type1b UI 分支早有完整留存；a00ab4a8 的48B extent也已有|不是新地址或新页面发现；仅核不同 caller/字段/reason/返回接入，不重复 handler/ZIP/资源盘点|
|[L03](settings-mode-contract-l03-0041-20261024.md)、[L04独立接受](settings-mode-review-l04-0041-20261024.md)|另一个 setter a00ab478 的 G+2、reason3、两 UI 接入已接受；共用 a00a5bbe 通知 ABI与 a00ab274 writer 服务接入已接受|服务内部直接引用，不因相邻或等长套用当前 helper；本题独立核实际 G+3、reason4、两个目标|
|旧 settings-round2d records[3]，`ev_c07160bdb96703feb18244c1eb8d977b82457a383130b34ee98c317357ab7765`|旧 constructor 的 type1b 分支按 `62fc909b!=3` 调同显示接口设置选择；另一个type1c分支读取909a|直接继承消费者关系，不重计初始化/选择行为，不将两个byte混同|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、guide/system complete、J03|设置 UI、ScreenOff/ScreenSave 的旧消费及 SIM 保存服务已有|passed-in-sim 只在其受控SIM范围成立，不证明当前 ROM 字段/回滚/flash或持久成功；不重跑、不重计|

J03已完成早期SIM/final complete/ZIP与较晚专项的去重，本轮再核父级 `settings_a00fd1ac` 确实包含 a00ab4a8、旧记录的两个 direct refs、constructor字段和extent身份。当前非管理 Markdown 对 a00ab4a8/62fc909b/62fc402f 的限定查询命中J03/L03/L04，后两份都明确本题备选未读/未验证；这不等于历史从未分析，也不把旧完整字节自动算已解释合同。

## 本轮复核或纠正

原件只读路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA−0x9ffff000`。[verify.py](../../analysis/settings-off-mode-l05-0041-20261024/verify.py) 用Python标准库直接读取并解算I/S/B/J字段，不导入L03/L04检查器、不运行旧草稿或目标。结果见 [evidence.json](../../analysis/settings-off-mode-l05-0041-20261024/evidence.json)。不新建REA会话/虚构Evidence ID，不保存完整helper/handler/body副本。

|原字锚点|本题事实与限制|
|---|---|
|a00fd1d0/d1e8|`374afc62` 与 ADDI+2c 得 s4=62fc402c，继承的caller基址在本题必要接入处再次核对，不算新恢复|
|a00fe9f0/f2|C.LI a0,3；JAL独立目标 a00ab4a8。返回后取local58、a1=0、a0=word(local58+8)，再调 a018f232|
|a00fea06/0a|LBU a0,3(s4)，得到 `62fc402f` U8；JAL独立目标同helper。返回后同样覆盖a0，a1=1，再调同显示接口|
|a00ab4a8/ac/b0|LUI/ADDI 构造 G=62fc9098；LBU a4,3(a5)，旧值为G+3=62fc909b，而不是L03的G+2|
|a00ab4b4|BEQ字段 rs1=a4、rs2=a0，目标a00ab4d6。比较零扩展旧byte与完整a0，比较前无输入byte截断；当前两个caller输入已为3/U8，不研究其他输入|
|a00ab4c0/c4/c6/ca|SB a0,3(a5)，然后 C.LI a0,4，依次JAL a00a5bbe和a00ab274。没有把reason3套到本题，也没有交换通知与writer|
|a00ab4ce..d7|差异臂只恢复/ret，相等臂直接ret；无显式保存成功值。两个UI分支在覆盖a0前均无保存/条件判断，不把残留a0解释为成功或失败|

与 L03 共有的普通门/顺序没有旧语义纠正；本题必要新解释是另一 byte 与两个 caller 的真实连接。值得保留的差异是 **常量3→显示flag0，编辑byte→显示flag1**；L03的编辑byte/常量与显示flag次序不同，不能用同类模板推导。两个类型的旧UI状态数值（type1b中的38h/39h及constructor选择）已有留存，本题只引用，不重新命名事件或扩键处理。

## 真正新增：局部差异合同

```c
// 正常接入的结构表达，非原源码，不声明稳定返回状态。
set_other_mode(value):                 // a00ab4a8
    if (load_u8(G+3) == value) return;
    store_u8(G+3, value);
    known_notify(4);                   // a00a5bbe，L03/L04合同
    known_write_system_settings();     // a00ab274，L03/L04合同

UI_branch_38h:
    set_other_mode(3);
    existing_display_call(word(local58+8), 0);
UI_branch_39h:
    set_other_mode(load_u8(62fc402f));
    existing_display_call(word(local58+8), 1);
```

`known_notify(4)`沿L04已接受的同步遍历合同，将 live G 与 reason=4 传为 `callback(node.word4,G,4)`，不复制当前状态快照。G+3 写在通知之前；共用writer在通知返回后读取live G，尝试其系统配置文件写服务，写/关闭结果本层不消费。G+6 的后续半字更新、path/mode、非零handle门及 `(G,8,1,H)`/关闭接线直接继承 L03/L04，不重新核验或重计本题成果，不借共用服务扩大为完整NVS/文件实现。

本题helper没有新分配、free、指针保留或所有权转移；编辑byte为值传递，G为既有全局对象，显示对象取自旧local58。通知订阅节点和文件handle的生命周期/下层释放保证继续受L04边界限制。发布后没有本helper的失败回滚门；UI显示调用不依赖可证明的持久化成功。不把静态调用存在写成实际回调执行、落盘或屏幕效果已观察。

新增业务解释只限本caller/字段/reason/顺序/返回消费；旧完整handler、extent、constructor、通知/writer和SIM通过都不重计。没有新增算法、来源认证、开源整库排除或ISA规则。

## 精确未闭与实际验证

本题两个call到G+3发布/通知reason4/既有writer接入的静态问题已得到证据，待独立技术复核。仍未知：该byte的完整正式枚举/所有真实写者、subscriber身份及生命周期、下层文件服务完整返回/资源保证和实际落盘/重启效果；全8B正式结构和writer低层算法沿旧边界保留。M01正在独占研究a00a46e8，不由本题重复。

后继建议只需新独立agent复核本题差异：两输入/显示flag配对、G+3 U8/full-a0门、SB宽度、reason4及两个既有目标、返回不消费。服务内部沿L04直接引用，不再开整通知/全writer复核。除此以外本题未取得新的必要功能种子，不以字段相邻或全ROM搜索凑后继。

实际验证：独占 `python -X utf8 -B .../verify.py` **PASS：24个稀疏记录、6个独立JAL目标、1个BEQ字段/目标**，另核旧caller两ref、父级、constructor与48B extent身份。JSON解析、报告相对链接及git diff检查通过。没有目标/输入/SIM运行，作者检查不等于独立验收。
