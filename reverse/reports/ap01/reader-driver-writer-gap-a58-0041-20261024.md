# A58：reader head/stride 注册 writer 的旧证据盘点

2026-10-24；认领 **J08/3**，基线 `bd457a6`，独占 `re0041-a58` / `codex/re-0041-a58`。授权取自主仓[唯一认领表](rolling-management-0041-20261023.md#链条认领表)当前三席持续滚动及J08/3行，负责人 `/root/a56`；按主仓最新 [reverse-design](reverse-design.md) 和[本地证据保留规则](../../analysis/README.md)，采用REA技能的留存优先方法。

**所查旧metadata没有给出 `word(0x62fc9744)` head、`word(0x62fc9740)` stride 的真实初始化/注册writer→节点word0=D身份桥。** 偶遇 `0xa005a8f4: sw zero,0x1c4(s1)` 后，经管理者准许只查已有s1/调用端链：其s1来自入口a0，而已存实际caller传的是自身帧局部 `s0−0x240`，不能把相同+0x1c4偏移认作global G的writer。本项为有界盘点交付，新增业务0、ROM读取0、新反编译0，未证明全局不存在writer。

不打开/切换共享REA、不读取ROM、不运行目标/固件/模型/指令、SIM/QEMU、构建、历史脚本、回放、设备或外部服务；不改生产、ROM、配置、分析器或共享表，不提交/推送、无下级agent。全部输入从主仓既存路径只读；忽略JSON没有复制到Git。作者自检不是独立技术验收。

## 继承结论

|已有出处|已解释行为|本轮差集与边界|
|---|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、J08已查的较晚complete及最终ZIP覆盖|照片业务和SIM替代已有；实际无线/驱动/硬件行为另有限制|不重做业务/SIM或解包资源，最终验收不证明ROM具体driver注册|
|[A56](reader-driver-selection-a56-0041-20261024.md)/[A57独立复核](reader-driver-selection-review-a57-0041-20261024.md)，J08/1已验差集|G=0x62fc957c；head=`word(G+0x1c8)`；next_off=`word(G+0x1c4)+4`；N.word0为候选D，按U8(D)==source首byte选首匹配，经过可选ready与open槽门才存W+4|直接继承选择144B合同与厂商规则边界，不重读ROM或重验选择。本项只找两槽writer/注册桥|
|A47/A49及A50/A52|D借用及open/close/read/seek接口、缓存责任已验|接口槽偏移不识别实际D、slot目标、节点所有者或注销寿命|
|[A54/A55局部来源](photo-reader-source-a54-0041-20261024.md)|本地LVGL候选register/get_drv角色相符|候选源码不是实际ROM注册函数/实例，保持版本及载体差异，不重新认证源码|
|[J08/1–2盘点](reader-driver-reuse-gap-j08-0041-20261024.md)|selector只有500B extent与直接边；POSIX源路径0xa056b8e0及7个owner仅定位metadata|J08/2和本head/stride尚无身份桥，不以POSIX basename替代D绑定，不沿那些owner body展开|

原件身份沿CATALOG与旧whole-ROM索引：AP01 `1.0.2_0041`，`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射 `file_offset=VA−0x9ffff000`。本项没有读取/校验ROM字节或重新生成摘要，不混0031、unsigned或SIM。

## 本轮复核或纠正

所查whole-ROM首轮索引顶层包含functions/source_paths等清单，**没有发布global-slot xref表**。`functions/5912`仍是0xa019d6a4，`historical_dossier=null`、`dossiers=[]`；这只能说明该旧载体不含所需查询结果，不证明共享数据库或全历史没有数据。新worktree缺导出不作缺失依据，已使用主仓恢复的忽略文件。

在主仓 `evidence/rea-0041-20261017`、`reverse/rehost`、`reverse/analysis` 的既存JSON/MD/C/TXT中，按两槽hex及十进制拼写 `62fc974[04]|166072096[04]` 做一次有界文本检索，结果只有A56/A57的选择证据JSON。这是**所选文本表示/搜索根**的结果；不覆盖未留存xref、别名、动态地址形成、其他格式或所有历史。后续收集器引用这次冻结结果，没有为修正脚本字段路径重复负搜索。

具体候选纠正：旧 `whole-rom-retained-private-20261023-000.json#/structuredContent/normalized_result` 的owner `0xa005a736`，Evidence `ev_06476b86aac1e3cfbfd38e938f8f5eddb97e919fafdf21781b11f1c0fdee62bc`，含 `0xa005a8f4: sw zero,0x1c4,s1`。管理窗口随后准许仅沿该旧dossier必要s1定义及caller消歧，未授权新ROM。实际旧行：

```text
0xa005a77a: c.mv s1,a0                    // 所选前缀中普通s1定义
0xa005a8f4: sw zero,0x1c4,s1              // 偶遇写端

// 旧列出caller 0xa005cc1e：
0xa005cc2a: addi s0,sp,0x400              // caller帧
0xa005cec2: addi a0,s0,-0x240
0xa005cec6: jal ra,0xa005a736
```

caller留存 `whole-rom-retained-20261023-000.json#/structuredContent/normalized_result`，Evidence `ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866`。该具体调用端给出的是caller帧局部指针，不是G=0x62fc957c的已证构造。所选入口到store的旧assembly中普通s1定义筛选只列a77a；这不是新控制流/别名全证明，也不证明所有运行实例地址必不同。裁定是 **不能把这条写端认证为0x62fc9740 writer**，而非为其所有caller或对象取正式类型名。

初次状态回报将screen载体的两类命中并提，现精确区分：G引用 `0xa00b2f98` 属 `screen-host-append-20261020-v2.evidence.json#/records/3` 的owner **0xa00b2f6c**，Evidence `ev_4886172901a9e225dff9550469d68d48bc8dbcc6aeafe83649d8f5674acc0127`；另 `records/8` owner0xa00b3252的 `0xa00b330a: li a2,0x1c4` 只是相同立即数，不是这个G引用，更不是槽writer。没有把两者合并对象。

## 真正新增

新增业务/注册语义 **0**；新增ROM字节/反编译/模型规则/来源认证 **0**。新增为旧载体边界及一个假候选的可定位消歧，不把重读旧assembly或新增文件计作恢复功能。

|旧metadata必要部分|本轮结论与局限|
|---|---|
|上述owner0xa005cc1e的referenced_names/出边，G来源0xa005cc6c/70/74、cd62、ced6|是G的引用端，所选邻接旧行显示G+0读取、栈保存G与G+0x68写入等，不提供+0x1c4/+0x1c8注册身份；没有沿其他字段扩范围|
|owner0xa005a736的G names来源0xa005be3a、be58、c8ae|G地址形成/栈保存及另一字段写入只说明相同全局基址被使用，不能认证head/stride writer；必要旧clips、EID与profile沿JSON原样保留|
|screen owner0xa00b2f6c的G name/source与outgoing metadata|无精确两槽target，尚无注册桥；单个全局基址引用不能升级为本题writer|
|source_paths/239的lv_fs.c诊断owner，以及source_paths/321 POSIX模块端|通用接口/路径身份继续继承；没有把其中任一owner名称、邻近地址或同偏移当实际driver注册实例|

## 未闭精确边与实际检查

J08/3在所选旧证据中仍未闭：两槽初始化/写入者、registry节点创建及N.word0保存D的实际连接、注册D及其各slot目标/寿命。J08/1选择规则保持已验，J08/2 POSIX路径身份桥保持未知。这里没有真实writer地址可以授权新ROM窗口，也不应改成无种子全fsdrv扫描。

有种子后继仍以 **0x62fc9740/0x62fc9744精确槽地址的write-xref/初始化metadata** 为问题入口：若取得新的有界写xref/owner记录，再登记具体writer/必要窗口，回答其基址和N.word0=D保存关系。现有索引不含该facet，需管理窗口决定是否取得对应查询留存；本研究者未执行新REA查询或读取新ROM。已向管理者回报同偏移栈对象假候选，不沿其caller或其他global字段扩大。

[reuse.py](../../analysis/reader-driver-writer-gap-a58-0041-20261024/reuse.py) 本轮仅收集旧metadata，**32项检查PASS**：既有ROM身份、A56/A57种子、selector无dossier、三份必要global-base owner metadata、候选s1/实际caller/帧关系、已有报告可用性。结果见本地忽略的 [reuse-result.json](../../analysis/reader-driver-writer-gap-a58-0041-20261024/reuse-result.json)，保留精确pointer/EID/profile、最小旧clips和冻结检索边界，不复制完整body/资源/导出。检查器修正过A57摘要键名和screen记录owner假定后通过，未改旧证据。

JSON解析、本地引用及 `git diff --check` 检查完成；新JSON受现有忽略规则保护，只保留原相对analysis路径，不提交。交付后停止本题，由管理窗口决定复核/补位。盘点自检不代表新ROM技术验收或完整目标完成。
