# A51：默认 cache drop/drop_all 局部候选来源认证

**A46/A48 已核的两个 backend body 与既有本地 LVGL 9.2.1 候选的 `drop_cb/drop_all_cb` 正常合同相符；本题未发现新的硬差异。** 单drop的cleanup先于重新计量/移出；drop_all仅零引用cleanup，随后仍整树释放payload和树节点，再清链/清计量。候选没有把非零引用改成invalid延迟回收。新增ROM功能0、确证ROM未改可排除项0；不认证精确ROM版本或构建来源。

2026-10-24；基线 `1edfc57`，独占树 `re0041-a51`、分支 `codex/re-0041-a51`。采用 reverse-engineer-anything 技能，继承A46/A48 ROM合同，不再读取ROM或运行其脚本。仅只读既有本地候选三文件的必要源行，无共享REA target/database、模型/固件执行、SIM、构建、历史回放、设备、外网或下级agent。仅写本报告及同名analysis，不改主树共享、生产代码、ROM、配置、模型或候选，不撤销其他任务改动。候选函数名与ROM地址的对应是分析映射，不是恢复了原符号/源码。

## 继承结论：已有 → 行为 → 局限 → 实际缺口

| 已有出处 | 已解释行为与证据局限 | 本轮处理 |
| --- | --- | --- |
| [A46](image-cache-drop-a46-0041-20261024.md)、[A48](image-cache-drop-review-a48-0041-20261024.md) | 原ROM表+18=`a00ebf7c`、+1c=`a00ec084`，NULL source→同image-cache all-key；单drop门/ABI/清理顺序，零ref cleanup与全树/链释放；已有独立复核 | 全继承，不重导ROM、不重核字节或实际调用者；本轮只作候选body映射 |
| [A43](image-cache-source-a43-0041-20261024.md)、[A44](image-cache-source-review-a44-0041-20261024.md) | 本地LVGL候选class初始化111..123行有drop/drop_all槽；旧key、计量、LRU、entry/header、cleanup和部分源码映射已核；当时明确未核这两个body | 直接沿用候选文件和已留槽名称，不重做已核业务/源码或ZIP比较；真实缺口为两个body及必要树/链清理适配 |
| A27/A28、A34/A36、A38/A40 | entry→payload运行期偏移、ref/invalid层级、OrderNode→TreeNode→payload、backlink及计量/key合同 | 可靠ROM合同直接继承；不把`a019cfbe`叫backend drop，不重做PNG/heap/树平衡 |
| F07/F08、A43/A44的候选身份及complete/最终ZIP复用边界 | 候选自报9.2.1，但解包树无自身Git、本地ZIP不是可信上游认证链；旧SIM/照片/服务替代不认证ROM ABI | 全继承，不扩版本/整库搜索，不重读ZIP或复制源码库；未有地址/xref种子的真实消费者不搜索 |

证据分层保持：A46/A48是已独立复核的原字节正常合同；旧反编译/函数清单仅定位；SIM/照片/安全替代不证明ROM；本轮新证据只是指定本地候选源行及局部比较。A48已查的complete/最终验收精确词项边界不重跑，不宣称此前未分析。

## 本轮复核或纠正：匹配、差异、配置条件、未知

候选根沿用 `S=Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`。本轮只新增 `src/misc/cache/lv_cache_lru_rb.c:343–406`、`src/misc/lv_rb.c:257–291`、`src/misc/lv_ll.c:160–179,294–297`，共3文件123行。必要原文见 [candidate-excerpts.json](../../analysis/image-cache-drop-source-a51-0041-20261024/candidate-excerpts.json)。A43对backend文件的本地ZIP相等结果继承；邻接两个文件本轮没有新的ZIP/来源身份认证，不据同目录自动升级信任。

| 类别/项目 | 精确候选源行（相对S） | 与A46/A48的映射及边界 |
| --- | --- | --- |
| **匹配：单drop入参与命中门** | `lv_cache_lru_rb.c:343,354–359` | 候选 `(cache,key,user_data)`，tree find→NULL直接返回→data=node.data；对应 `a00ebf7c` 正常 `c00c..c020`。候选void签名不把ROM未认证返回类型升级为已知 |
| **匹配：单drop cleanup/计量** | 同文件`:361–362` | `ops.free_cb(data,user_data)`在`size -= get_data_size_cb(data)`之前；对应 `c028..c03a` 的cache+18调用、随后重读+3c及word扣量。userdata来自第三实参，不因已有all-key入口传0而一律归0 |
| **匹配：单drop entry/backlink与释放次序** | 同文件`:364–371` | 先得到entry和lru_node，再`rb_remove_node`→`entry_delete`→`ll_remove`→free链节点，对应 `c03c..c06e`。entry/payload身份及delete内部基址free沿A27/A43继承，不重做 |
| **匹配：单drop无ref/invalid/victim门** | 同文件`:343–372`完整选中body | 有显式参数/查找门，但body没有引用数筛选、invalid标记或victim选择；与A46/A48直达正常命中路径相符。不把通用`a019cfbe`的协议插进本body，也不推断上层允许任意引用状态调用 |
| **匹配：drop_all零ref cleanup与warning** | 同文件`:374,384–400` | `(cache,user_data)`，链条目→tree.data→entry，ref==0才free_cb；非零只warning并计数，循环结束另作汇总warning；对应 `c0e0..c0fe/c158..c1a8` 的已核门与汇合。warning的第二次getter语法不是ROM必然第二次加载/调用的证明 |
| **匹配：warning后继续全部树清理** | 同文件`:402–405` | 分支合流后无ref筛选地`rb_destroy`→`ll_clear`→size0；对应 `c126..c13a`。不能把warning解读成跳过树释放，也不把候选日志文字视作实际运行记录 |
| **匹配：树销毁实际责任** | `lv_rb.c:265–290` | 从root下行left/right，叶节点断parent相应边，再free(node.data)→free(node)→回parent，末尾root0；对应 `c1aa..c1e4/c130`。无entry_ref/invalid门或payload callback，支持A48“遍历阶段仅零ref cleanup，但第二阶段全部树payload/node释放”的局部对应，不扩大成平衡树认证 |
| **匹配：清链实际责任** | `lv_ll.c:294–297`及`:165–177` | `ll_clear_custom(ll,NULL)`；循环先保存next，再remove/free当前链节点，末尾推进到已保存next；对应 `a008ae42→a008adf4`及`ae1c..ae3a`。不重复解引用已free的TreeNode，不再cleanup payload。链端点写入仍沿A34继承 |
| **差异** | 本题上述正常body/必要适配 | 未发现需要反转A46/A48语义的新硬差异；这不等于编译产物/全backend无差异。F07/F08已有display/list差异继续有效，不作新的归因或整库排除 |
| **配置条件：宽度和布局** | 与A43/A44已核声明共同解释上述源行 | 指针/size_t普通RV32为32位时，与ROM word大小、size扣量及两级节点关系局部相容。enum/OS锁完整布局和编译输入未认证，不从宿主或候选sizeof计算ROM偏移；现有ROM偏移仍由A46/A48确定 |
| **配置条件：assert/log与优化** | `lv_cache_lru_rb.c:347–352,378–382,394,399`；`lv_rb.c:259–263` | 候选有assert与显式NULL return，日志展开受配置影响。ROM本题只验正常有效对象路径；不借候选补认证诊断/NULL输入合同，不新增source非NULL门。日志参数getter和helper内联/重读形状可能受优化影响，未作编译对应或回放 |
| **未知** | 不由上述源行解决 | ROM精确commit/版本/编译宏/ABI、unmodified来源、table+18上层消费者、业务何时NULL source及外部ref前置条件、动态重配/同步、allocator内部和实际运行时刻均未知 |

本轮没有改写A46/A48合同。所有权/生命周期结论仍是：callback负责image payload所持owned资源，payload分配与TreeNode/OrderNode另由已核清理路径释放；cache对象及表/capacity本题不重建或释放。候选`drop_all_cb`在非零ref分支也只warning/count，后面的无条件`rb_destroy`确实支持已观察原序，不能因一般缓存直觉替换为延迟回收。只认证正常静态合同相符，不推断有引用条目实际出现或任何缺陷。

## 真正新增与四类来源裁定

新增仅为这两个body和必要邻接清理的**局部来源映射**；ROM功能新增0、ROM语义纠正0、厂商规则/模型修改0、函数导出0、确证未改可排除项0。A43/A44旧key/meter/LRU匹配不重复计入成果。

| 来源分类 | 裁定 |
| --- | --- |
| 确证ROM未改、可排除继续恢复 | 0项；选中源行相符不认证准确构建/上游身份 |
| 候选局部合同相符 | 接受drop/drop_all、树销毁payload→node与NULL-callback清链的上述局部对应，待新独立技术复核 |
| 家族可识别、版本未知 | 沿用image-cache/LRU-RB家族与本地自报9.2.1候选背景；不升级ROM版本/commit |
| 差异/封装/未认证部分保留 | 本题新硬差异0；旧已知差异不消失，编译配置/诊断/完整ABI、动态同步及来源仍未认证 |

## 实际验证、精确断边与后续闭包

第一次普通WSL只读访问返回 `Wsl/E_ACCESSDENIED`；按已有明确授权，以`require_escalated`固定读取同一本地候选与三个已定位相邻函数，成功；没有安装/修环境或访问网络。读取器 [read_candidate.py](../../analysis/image-cache-drop-source-a51-0041-20261024/read_candidate.py) 不导入/执行候选，只流式读取选中行及函数边界；没有保存整文件或ZIP副本。

运行本路 [verify.py](../../analysis/image-cache-drop-source-a51-0041-20261024/verify.py)：PASS，3文件/123选中行、7项源合同检查，包括签名/lookup门、cleanup与计量/移除顺序、候选单drop无ref/invalid/victim门、全清遍历/分支汇合、树销毁和清链适配。结果 [verification.json](../../analysis/image-cache-drop-source-a51-0041-20261024/verification.json)。这是源文本校验，不是目标或模型执行；没有重新认证A46/A48原字。交付JSON解析、相对链接及 `git diff --check` 通过。

本题断边已到“局部候选合同相符”闭合，精确构建来源仍无可认证材料；table+18真实消费者和业务引用前置条件也未得到新地址/xref种子，不能为凑题扩扫。单一后续建议是由新独立agent仅复核本题3文件123行与A46/A48之间的映射/限定强度，不重启ROM/key/meter/LRU/heap或全库版本搜索；是否派发由管理者决定。本轮不自行接后继。
