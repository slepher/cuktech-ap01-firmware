# A53：drop/drop_all 局部来源映射独立复核

2026-10-24；基线 `85cf93c`，独立分支 `codex/re-0041-a53`。**限定接受A51：三文件123行与留存相同，单drop原序、drop_all的零ref cleanup/warning及随后整树/链释放责任有对应，无语义纠正。** 新增ROM功能0、确证未改可排除项0、整库排除0；没有认证ROM精确版本或构建来源。

采用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，未参与A51生产。只读已选本地候选必要行及既有报告，不读取/导出ROM、不运行A51脚本或候选，不打开/切换共享REA target/database。无SIM、构建、历史回放、设备、外网或下级agent；未修改主树共享文件、生产ROM、配置、模型或候选。

## 继承结论：已有→行为→局限→本题缺口

|已有出处|已解释行为和限制|本题处理|
|---|---|---|
|[A46](image-cache-drop-a46-0041-20261024.md)、[A48](image-cache-drop-review-a48-0041-20261024.md)|同backend表+18=`a00ebf7c`、+1c=`a00ec084`；正常NULL-source all-key接线；drop命中后cleanup/计量/移除，drop_all零ref cleanup后整树释放|已独立复核的ROM合同直接继承，不重新核字节、函数、参数或NULL-source调用者|
|[A51](image-cache-drop-source-a51-0041-20261024.md)及[候选摘录](../../analysis/image-cache-drop-source-a51-0041-20261024/candidate-excerpts.json)|两个body与必要树/链清理的三文件123行局部来源映射；未发现新硬差异|仅独立读取同123行、人工核映射与来源强度；不重新运行生产验证器|
|[A43](image-cache-source-a43-0041-20261024.md)、[A44](image-cache-source-review-a44-0041-20261024.md)|同一LVGL候选的class声明、entry/backlink、计量/key等局部对应，drop/drop_all当时未展开；自报9.2.1身份有局限|既有字段/helper合同及候选身份限制继承，不重复9文件/ZIP比较、header或版本认证|
|A27/A34/A38及对应复核；F07/F08和旧complete/最终ZIP复用边界|payload/entry、OrderNode→TreeNode→payload、链端点、key和清理分层已有；旧SIM/照片/服务替代不认证ROM ABI|继承，不重做PNG、heap、树平衡、旧资源或无xref消费者搜索；局部源码同形不消除既有全库差异|

实际缺口仅是A51所选源行与既有正常ROM合同之间的映射是否可以接受；候选函数名是分析对应，不是恢复的ROM符号或原源码。

## 本轮复核或纠正：逐项接受

`S=Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`。独立读取`src/misc/cache/lv_cache_lru_rb.c:343–406`、`src/misc/lv_rb.c:257–291`、`src/misc/lv_ll.c:160–179,294–297`；逐行与A51相等，共3文件123行。[review-evidence.json](../../analysis/image-cache-drop-source-review-a53-0041-20261024/review-evidence.json)只保存路径、区间、计数和校验判定，不复制第二份源码。

|映射项目|独立候选定位|与继承ROM合同的裁定|
|---|---|---|
|单drop参数/命中门|backend`:343,354–359`：cache,key,user_data；rb_find；miss return；node.data|接受与`a00ebf7c:c00c..c020`对应。候选void签名不认证ROM返回类型，userdata仍为原第三参数|
|cleanup与计量原序|`:361–362` free_cb(data,user_data)后size减get_data_size_cb(data)|接受`c028..c03a`的cleanup→重读计量callback→扣word顺序，不把计量前置或将userdata全归0|
|entry/backlink及移除责任|`:364–371`先求entry和lru_node，再rb_remove→entry_delete→ll_remove→free链节点|接受`c03c..c06e`原序；entry_delete与payload基址的关系继续继承A27/A43，不新增其内部来源认证|
|单drop门范围|`:343–372`为选中完整body，无get_ref/invalid/victim门|接受A51限定：本body不插入通用失效/延迟回收协议。不将`a019cfbe`改名backend drop，也不认证上层任意引用状态的合法调用前提|
|drop_all遍历及零ref cleanup|`:374,384–391`，userdata为第二参数；链项→tree.data→entry，get_ref==0才free_cb|接受`a00ec084:c0e0..c0fe/c158..c182`对应。此遍历仅执行cleanup，不是逐entry_delete|
|warning/count与汇合|`:393–400`非零ref分支per-entry warning并used_cnt++，遍历后有引用时summary warning；`:402–405`位于循环/分支之后|接受warning后继续同一整树清理，不把非零ref条目改成invalid或延迟保留。第二次getter位于日志参数，是否生成实际第二次调用/加载取决于未认证的日志展开/优化；不把源语法冒称ROM指令|
|整树销毁责任|rb`:265–290`，left/right下行，叶节点取parent并断父边，free(node.data)→free(node)→回parent，最后root=NULL|接受`c126..c130/c1aa..c1e4`局部对应。该body无entry ref/invalid筛选、无payload cleanup callback，故第二阶段全部payload分配/树节点释放与第一阶段仅零ref cleanup是不同责任；不升级为完整RB树来源认证|
|清链责任|ll`:294–297`以NULL cleanup调用clear_custom；`:165–177`先保存next，NULL分支remove/free当前链节点，再移到保存next|接受`a008ae42→a008adf4`及既有`ae1c..ae3a`合同：清OrderNode，不再解引用已释放的TreeNode，不重复cleanup payload。非零cleanup分支不在本实际适配范围|
|最终顺序与容量边界|backend`:402–405` rb_destroy→ll_clear→size=0|接受整树结束后才清链/计量；不释放cache对象/表，不认证capacity重建、实际运行条目状态或外层调用时序|

没有需要纠正A51的技术结论；本题选定正常body与必要适配未发现新的硬差异。A46/A48的参数保存、word宽度、重读和原序保持原合同，源码阅读不替代ROM证据。

## 真正新增与来源强度

新增ROM功能0、语义纠正0、ISA规则/模型修改0、ROM函数导出0、精确版本认证0。独立源行读取和12项局部源合同检查仅为复核，不重复记作功能恢复。

|来源类别/条件|复核裁定|
|---|---|
|候选局部合同相符|接受drop/drop_all及树/NULL-callback清链的上述对应，可作为同一家族的局部语义参考|
|确证ROM未改或整库可排除|0项。三文件选中源行相符不足以认证精确commit、原始编译输入或未修改实现|
|候选身份|沿A43/A44/F07/F08保留：解包候选无自身Git、父仓状态不认证被忽略树、本地ZIP没有可信上游认证链。本轮邻接rb/ll文件没有新增ZIP或上游身份认证|
|ABI/配置条件|32位指针/size_t下局部字段/word计量相容；不以宿主sizeof/候选enum或锁结构覆盖已证ROM偏移。断言、显式NULL门、日志展开、helper内联/优化及诊断路径不因正常body相符而自动认证|
|保留差异与未知|本题新硬差异0；F07/F08既有display/list差异继续有效，不能由本次局部匹配消除或归因为厂商改动。完整ABI/同步/重配置仍未知|

所有权解释保持分层：cleanup callback处理payload所持owned资源；payload分配/TreeNode与OrderNode由后续容器路径归还。drop_all非零ref分支只warning/count，之后不再按ref排除树数据；这只是正常静态路径对应，不能推出有引用条目实际发生过all-key清理，更不作缺陷结论。

## 未闭精确边与实际验证

仍未知ROM精确版本/commit/构建宏、真实来源是否未改、table+18真实上层消费者及其引用前置条件、业务实际何时传NULL source、动态同步/重配置、allocator内部与运行时状态。候选没有新增真实消费者地址/xref，本轮不扩大搜索。已有正常原件合同和本题来源强度保持独立。

[review.py](../../analysis/image-cache-drop-source-review-a53-0041-20261024/review.py)实际通过：独立固定区间流式读取3文件123行，与A51逐行一致；12项局部源合同检查通过。没有导入/执行候选或A51脚本，没有读取ROM/ZIP或保存完整源码。WSL按已授权固定本地只读范围require_escalated访问；无新拒绝或权限修改。JSON解析、报告本地链接、`git diff --check`通过。

本题独立复核闭合，无需再派同一源行/版本扫描；单一后续闭包仅在获得table+18真实调用者xref及正常引用前置条件种子后，核该调用点的参数/持有边，不因本次局部匹配扩大至所有cache或无种子消费者。
