# A59：J08/3 reader注册writer旧证据盘点的独立限定复核

2026-10-24；基线 `bd457a6`，分支 `codex/re-0041-a59`；挂原认领 **J08/3**，非作者 `/root/g23`，A58作者 `/root/a56`已停止。**限定接受A58：所选旧载体未给出head/stride的真实writer身份桥；`0xa005a8f4`的同偏移store不能认成global槽writer，已存实际caller传入的是帧局部表达式；screen的G引用owner与单独0x1c4立即数owner须分开。语义纠正0、新增业务0。** 不把这些有限结果写成全局不存在writer或所有运行地址必不同。

已读主仓 [A58报告](reader-driver-writer-gap-a58-0041-20261024.md)、其本地冻结盘点结果及 [唯一管理表](rolling-management-0041-20261023.md#链条认领表) 的A59登记。遵循本批已读 [reverse-design](reverse-design.md)、[analysis保留规则](../../analysis/README.md)及 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存优先规则。本轮只读取明确选定的旧JSON/dossier必要行与摘要，不读取ROM、不新反编译/解码、不新REA查询、不重搜全载体，不运行A58/旧脚本、目标/指令/模型、SIM/QEMU、构建、回放、设备或外部服务；未改主树/共享表、生产ROM配置模型，无下级agent、提交或推送。

## 继承结论

|来源|继承内容|本轮限制|
|---|---|---|
|[A56](reader-driver-selection-a56-0041-20261024.md)/[A57](reader-driver-selection-review-a57-0041-20261024.md)，J08/1|G=0x62fc957c；head在G+0x1c8=0x62fc9744；动态next偏移使用word(G+0x1c4)+4，stride槽0x62fc9740；N.word0候选D及选择/接口门已验|不重验144B选择、厂商规则、实际D/slot或生命周期；这些槽地址是writer问题的种子|
|A47/A49、A50/A52、A54/A55及J08/2|reader接口/候选来源、POSIX路径端及既有实例绑定边界|接口、候选源码、源路径basename都不能代替注册writer；不接全fsdrv或源码认证|
|[A58](reader-driver-writer-gap-a58-0041-20261024.md)|冻结文本搜索边界、旧index缺所需facet、同偏移store与screen owner消歧|作者历史搜索hitset作为冻结记录继承，本轮独立检查命题强度及必要旧原记录，不冒充重跑或历史快照完整性认证|

原件身份沿 [CATALOG](../../../roms/CATALOG.md) 和旧index：AP01 `1.0.2_0041`，`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射`file_offset=VA−0x9ffff000`。本题**没有读原件或重新校长度/摘要**；这是所选旧metadata的身份引用，不混0031/unsigned/SIM。

## 本轮复核或纠正

独立 [review.py](../../analysis/reader-driver-writer-review-a59-0041-20261024/review.py) 没有导入/运行A58脚本、反汇编器或ROM访问，结果见本地忽略的 [review-result.json](../../analysis/reader-driver-writer-review-a59-0041-20261024/review-result.json)。旧dossier沿原Evidence ID/profile，不重标成新REA生产分析；旧assembly是历史提供器展示，不当成本轮新原字/ISA认证。

### 有限搜索边界

A58冻结查询根为主仓`evidence/rea-0041-20261017`、`reverse/rehost`、`reverse/analysis`；文本模式`62fc974[04]|166072096[04]`，大小写不敏感，选JSON/MD/C/TXT并含hidden/ignored。复核核算两个十进制拼写分别确为0x62fc9740、0x62fc9744，核冻结记录中的roots/格式/命令选项及两个已存读端文件可定位。

**历史查询命中仅A56/A57的两个JSON，是继承的作者冻结输出记录，本轮未独立重跑该查询，也没有证明当时或当前完整文件系统快照。** 因而接受的强度仅为所列根、文本表示、格式与该历史时点记录；不覆盖未留存xref、动态地址形成/别名、其他格式（例如未纳入的头文件）、其他历史或新材料。没有借当前主树多了新报告去修正原冻结hitset，更不把它升级为writer不存在。

对旧首轮index独立检查：顶层未发布含global/xref名称的facet；functions5912仍是0xa019d6a4，historical_dossier为空且dossiers空。这只说明**该载体没有直接提供此查询facet/该selector dossier**，不证明共享数据库、其他嵌套表达或全历史没有数据。

### 同+0x1c4 store的基址/实际caller

|必要旧记录|独立核到的事实|接受边界|
|---|---|---|
|`whole-rom-retained-private-20261023-000.json#/structuredContent/normalized_result`，owner0xa005a736；Evidence `ev_06476b86aac1e3cfbfd38e938f8f5eddb97e919fafdf21781b11f1c0fdee62bc`|旧行`0xa005a77a: c.mv s1,a0`；`0xa005a8f4: sw zero,0x1c4,s1`；已存caller列表只列0xa005cc1e|支持所选store基址来自a0捕获，不由偏移相同认s1=G|
|同一旧dossier的入口0xa005a736至a77a前缀|所选展示前缀为栈保存/帧形成及对其他寄存器操作；未见a0定义或call/jump；所选到store的普通s1定义筛选仍只得a77a|支持这是该展示前缀中的入口a0；普通定义筛选不是新完整CFG、未知指令/别名或所有运行控制路径证明|
|`whole-rom-retained-20261023-000.json#/structuredContent/normalized_result`，owner0xa005cc1e；Evidence `ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866`|`0xa005cc2a: addi s0,sp,0x400`；`0xa005cec2: addi a0,s0,-0x240`；紧邻`0xa005cec6: jal ra,0xa005a736`|所列实际caller传的是帧局部表达式，未给出a0=G构造；因此不能认证0xa005a8f4写0x62fc9740|

裁定保持A58原强度：**该store不是已证global槽writer**，而不是“所有caller/运行实例永不别名G”或“这个对象正式类型已知”。没有新ROM或别名分析证据可支持更强排除，也不沿该caller的其他global字段扩范围。

### screen实际owner与立即数分离

旧`screen-host-append-20261020-v2.evidence.json#/records/3/normalized_result`的owner确为 **0xa00b2f6c**，Evidence `ev_4886172901a9e225dff9550469d68d48bc8dbcc6aeafe83649d8f5674acc0127`。其referenced_names的G=0x62fc957c来源为 **0xa00b2f98**，旧assembly在该点为`addi a5,a5,0x57c`。这项G引用的owner不能写成0xa00b3252。

同载体`records/8` owner **0xa00b3252**，Evidence `ev_61d0c9e8b48e884fb9f65fb2eb3fdf60b8d7743ee37cf3969544903bbde82355`；其`0xa00b330a: li a2,0x1c4`只是常数，在该record的referenced_names未发布G引用。两个record不因同载体或同offset合成同对象/slot写端。records3所选outgoing metadata也未列两精确槽target，但这不排除未表示的动态写入。

**A58最终报告已包含上述owner纠正，故本轮新增语义纠正0。** 复核不是重新恢复screen/初始化逻辑，也没有把旧元数据缺边当成新反编译失败。

## 真正新增

复核新增业务 **0**、ROM字节 **0**、反编译 **0**、来源认证/ISA规则 **0**。交付仅为非作者对A58盘点边界与候选消歧的限定接受及必要旧记录索引。J08/1已验选择规则直接继承；J08/2 POSIX身份桥及J08/3注册writer问题都不因此闭合。

## 未闭精确边与实际检查

两槽0x62fc9740/0x62fc9744的真实初始化/注册writer、registry节点创建、N.word0=D保存桥，以及实际D/slot目标/寿命仍未获得种子。本轮所选材料不足不是全局无writer证明，不能为维持并发转为无种子全fsdrv扫描。

实际运行本路独立收集器 **37项旧metadata检查PASS**，包括有限检索参数/十进制拼写、index facet界限、入口a0与caller帧局部的展示行、screen owner/立即数分离；未重跑全载体搜索或作者检查器。JSON解析、报告相对链接、Git忽略、独占文件及diff检查通过。新逐项结果按规则留本地原路径并忽略，源码/报告未提交推送。

有种子后继仍是原J08/3的两精确槽地址 **write-xref/初始化metadata**：须管理窗口先取得新的有界owner/write记录并登记，再核该writer基址与N.word0=D连接。现有载体不含足够facet，本复核没有执行新REA查询、读取新ROM或自行扩大；不能复派同一冻结负搜索当新增研究。
