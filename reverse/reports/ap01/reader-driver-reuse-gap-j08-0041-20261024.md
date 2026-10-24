# J08/1–2：reader 所选 D 的旧证据身份盘点

2026-10-24；研究基线 `608da2b`，独占树/分支 `re0041-j08` / `codex/re-0041-j08`。认领 **J08/1** 及管理窗口随后以 `bc3711a` 登记的 **J08/2**，必要继承 **A47/1**，研究基线不移动。**新增功能0、ROM读取0、新反编译0。现有选定载体没有给出实际 D 的注册实例或槽目标绑定。** 找到真实ROM `lv_fs_posix.c` 源路径及8条xref后，先报管理者登记，再仅查所指7个已定owner的旧metadata；仍没有D绑定，未沿新owner/callee展开ROM或body取证。

已全文读取主仓[reverse-design](reverse-design.md)及[唯一认领表](rolling-management-0041-20261023.md)，回报差集后工作。原件身份继承[CATALOG:17](../../../roms/CATALOG.md:17)：0041原件6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射VA−0x9ffff000；不读ROM、不重算摘要。采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存证据/事实边界规则。只读指定旧报告/JSON/索引，不重新运行A47的全rehost负搜索、不复制整函数/源码/资源、不解码照片。无SIM/QEMU、构建、回放、固件、设备、外部服务、输入或模型执行，不改生产代码/ROM/配置/分析器模型、不共享REA、不推送、不下派、不撤销他人工作，只写独占输出。

## 继承结论：已有→行为→局限→精确差集

|已有出处|可继承行为|本题差集/限制|
|---|---|---|
|[最终complete](application-rehost-complete-0041-20261017.md)、photo round3/system父级/最终ZIP的A33–A55既有复用记录|照片业务、主旋钮轮转和SIM替代已有；父级与旧body的覆盖已交叉核过|不重跑旧父级/ZIP全量查询，SIM成功不证明D注册、ROM ABI或实际I/O|
|[A33](photo-source-abi-a33-0041-20261024.md)/[A35](photo-source-review-a35-0041-20261024.md)|实际五ROM照片表descriptor指针、mode0 ROM借用已接受|默认五照片保持mode0，不能用通用source类型1分支制造真实mode1照片实例|
|[A37](photo-decoder-owner-a37-0041-20261024.md)/[A39](photo-decoder-review-a39-0041-20261024.md)、A41/A42|W成功后复制当时前缀到O，owner持有，外层归还不同对象|不重做constructor、算法、缓存/资源生命周期|
|**A47/1**：[A47](photo-reader-mode-a47-0041-20261024.md)/[A49](photo-reader-mode-review-a49-0041-20261024.md)|分类1→0xa0107d8e，0xa019d6a4(W,source)把选定D写W+4；普通D+0x0c回调 `(D,pathSuffix,2)`，D+0x10归还回调 `(D,H)`，缓存条件/重读/清槽已验|接口和条件全部继承；唯一问题是这些已验slot所属**同一个D**的来源/注册实例与目标地址，不从槽偏移认同对象|
|[A50](photo-reader-consumer-a50-0041-20261024.md)/[A52](photo-reader-consumer-review-a52-0041-20261024.md)|D+0x14 read五参、D+0x1c seek四参及C/B持有/填充/归还接线已验|不重复消费ABI或缓存算法；具体D依然未证|
|[A54](photo-reader-source-a54-0041-20261024.md)/[A55](photo-reader-source-review-a55-0041-20261024.md)|本地候选LVGL9.2.1的前缀、open/close和注册角色局部相符|候选register/get_drv源行不是ROM实例绑定；4个整文件相同、`gifdec.c`整文件不同及3个选定片段相同的差异保持，不展开差异/版本或假称整库排除|

认领差集：J08/1与A47/1共用接口而问题不同，A47/1已验部分直接继承。F11/1–2的RPC栈D/请求R/Invocation/session不是本reader D；G19/3的poll W/submit_ctx也未与本D建立身份关系。泛称driver/loop、相同字段偏移不构成同对象。P01/1已验activity与本题无交集，不重开。

## 本轮复核或纠正

本轮只验证旧载体身份/索引定位，不验ROM指令、不纠正已接受接口。A47 `evidence.json#/rows`保留0xa019d6ec..0xa019d704的源首字节/后缀处理，以及0xa019d798起 `D=s1→W+4` 的保存、配置/缓存等；**没有0xa019d708..0xa019d796这段选择来源的rows**。不能把两端已有误写为选定来源已闭，也不因这一载体缺片段断言整个历史未分析。

`whole-rom-coverage-0041-20261023-round1.json#/functions/5912` exact entry为0xa019d6a4，extent500B，Evidence `ev_859d0259f168d800653161ec3bc5f2e30ad376724ac8554d42ab611f85726f07`；direct-call Evidence `ev_1280933dca27de196ea349bb7f242f9b891487c60bddd21c237f3f9f345aaf4c`列0xa0019672/0xa008b51a/0xa008e362；`historical_dossier=null`、`dossiers=[]`。这些只是范围/直接边清单，没有给D的全局来源、注册节点或slot值。本题未沿这三个callee展开。

同索引`#/source_paths/239`的0xa02631a8是`.../src/misc/lv_fs.c`，source-xref Evidence `ev_c2b3a58114d1e9a99fd3b411b6f87a1f2cd76db0fb6e7b144f9c9b1697f56ee7`。它指向0xa008b888、0xa008e3ac和0xa019d6a4内部诊断owner，只识别通用fs接口代码来源，不识别具体D或文件系统实例，不能拿此路径作为注册证据。

必要caller反向direct-call metadata（同索引，非重新扫描ROM）列：0xa019d6a4的用户为0xa0082c8c、0xa00e4bb4、0xa00eb7b6、0xa0107d8e；0xa0107d8e唯一列出caller为0xa00ed7f4。后者就是A47已核setter的类型1分支，其存在不证明实际source类型1对象。前三条也只是通用接口用户，没有实参/注册身份合同；本题不沿这些新caller body追路径。原索引/profile身份沿载体保留，不把metadata改标成新ROM观测。

## 真正新增：盘点功能0与J08/2旧metadata消歧

|候选/实际载体pointer/Evidence|已知端|待找端/必要增量|
|---|---|---|
|**J08/2已登记旧消歧**：同whole-ROM索引 `#/source_paths/321`，实际ROM字符串 **0xa056b8e0**，`.../src/libs/fsdrv/lv_fs_posix.c`；`#/source_paths/321/references/0`为0xa00ef4e4，owner0xa00ef468，owner定位Evidence `ev_c7fbfbb3b7a7b5ac455671bc5f2260f64d184a1561280781c60b1b1bfe2c9440`|该原件确有此源路径的xref metadata，8条引用对应7个已定owner和1个owner未知；这是实际ROM来源定位，不是A54本地候选源码|已获准仅查这些owner/caller/dossier旧metadata；未有初始化/注册实例地址、driver字节/槽填充、注册到selector同一D的身份桥，不能把源码basename直接当“D已确定为POSIX”|
|同表references/1..7，具体pointer及各EID见本题JSON|已定owner还包括0xa00ef502、0xa00ef55e、0xa00ef5c8、0xa00ef69c、0xa00ef706、0xa00ef778；0xa00ef67c的owner未定|只保留这些地址，不赋open/close/read/seek名称，不据地址顺序或邻近构造注册函数/回调表，本题没有读取这些body或沿callee扩展|
|原认领 **J08/1**，后登记 **J08/2**，相交 **A47/1**；F11/G19无已知同对象连接|已知D端是0xa019d798的W+4和已验槽接口|J08/2旧证据问题是“上述实际fsdrv代码的注册实例是否连接到selector选定D，以及具体slot身份”。本轮只metadata消歧，无新ROM/反编译授权，必要增量仍为实例/注册桥，不接全部文件系统/driver或候选版本|

登记后核 `#/functions/3409..3415`：上述7个owner全部 `historical_dossier=null`、`dossiers=[]`、`historical_contracts=[]`，只留extent/direct-call清单；各owner的extent/direct-call Evidence ID及目标保留在本题JSON的new_connection_request.owner_metadata，只作定位，不复制清单或沿callee展开。逆direct-call清单对这7个owner均无列出caller；这不排除函数指针/注册使用，也不能找到哪个slot引用它们。0xa00ef67c未归属任何本索引已列extent，仍保留owner未知，不能从邻近函数补造边界/身份。

元数据找到了一个可交管理者筛选的**模块定位端**，没有找到真实绑定种子，不认证D注册链、具体回调目标、H资源类型、真实mode1照片或I/O成功。本轮无新函数/算法/ROM字节/来源认证/整库排除，未将候选源代码中的清零/register指针保存算法映成具体ROM函数。

## 精确未闭与实际验证

J08/1–2旧证据盘点完成：所选载体中D保存和槽消费端可信并继承，selection链来源/实际D实例/槽目标端仍缺；J08/2的“source_paths/321→同D”身份关系未知，7个owner的现存metadata不足以生成注册/slot绑定种子。报告此缺口不是全历史不存在证明，不能授权无种子全文件系统、全部driver或重跑全rehost负搜索。

唯一新连接先按规则报告“原J08/1、新连接/问题、相交A47/1、旧source_paths/321及8条xref、必要实例桥”，管理者已以J08/2授权上述旧metadata消歧。本研究者完成后停止在metadata，不自行新增ROM取证或沿新注册callee展开；下一步是否取得其他定址留存/稀疏原字段证据仍须由管理窗口登记具体问题与种子后决定，不能因metadata不足直接扩为全部driver研究。没有把新文件/任务名当作扩范围授权。

[reuse.py](../../analysis/reader-driver-reuse-gap-j08-0041-20261024/reuse.py)只读旧报告/JSON/index和CATALOG：**27项检查PASS**，核认领/原件既有身份、selector缺dossier及A47窗口边界、A49/A52/A55已验限制、4整文件/1GIF差异、相关caller/源xref和7个J08/2 owner的metadata身份。结果见 [reuse-result.json](../../analysis/reader-driver-reuse-gap-j08-0041-20261024/reuse-result.json)，保留每候选pointer/EID/地址和待找端，无整body/源码/资源副本。JSON、报告相对链接和diff检查通过；无ROM读取或目标执行，盘点检查不是技术验收。
