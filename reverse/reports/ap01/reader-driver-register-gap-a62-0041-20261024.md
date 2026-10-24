# A62：J08/5 真实reader list参数、返回节点与D保存桥

2026-10-24；基线 `bd457a6`，分支 `codex/re-0041-a62`，认领 **J08/5**，作者 `/root/g23`。**已定位真实注册连接：`0xa008e7d8/e7de`形成list=0x62fc9740，`0xa008e7e2`调用已验insert-head helper `0xa008aec0`；返回节点N非零才在`0xa008e826/e82a`把地址D=0x62fc974c存入N.word0。** 这不是因共用helper推测容器相同，而是具体list实参、返回值门及word保存建立的桥。

本题的s1来自旧`0xa008e75e LUI s1,0x62fc9`，值为 **0x62fc9000高位常量**，不是A60阶段的s1=G。D由该s1加0x74c形成，需正常callee保存s1；非零分支跳过空节点诊断路径的s1改写。实际D的首byte、全部callback槽写入基址关系、匹配source实例及注销/存活仍不由本题认证。

已读主仓 [唯一认领表](rolling-management-0041-20261023.md#链条认领表) 的J08/5和缺窗升级登记；遵循本批已读 [流程](reverse-design.md)、[保留规则](../../analysis/README.md)与 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。初始仅旧索引directcaller/必要留存，发现initializer具体旧缺窗及fs路径xref后先报管理登记，再仅取 **[0xa008e768,0xa008e82c)** 内短窗；找到header→helper→node.word0连接即停止。没有读取其他caller新body、helper/D槽目标body或错误块，没有全fsdrv/全ROM扫描、新反编译/REA会话切换。

未执行目标、指令、模型、固件、SIM/QEMU、构建、旧技术脚本、回放、异常输入、设备或外部服务；未改生产ROM配置模型、主树/共享表，无下级agent、提交或推送。静态表达非原源码/运行观察，作者自检待独立复核。

## 继承结论

|来源|已有合同/界限|本轮处理|
|---|---|---|
|[A56](reader-driver-selection-a56-0041-20261024.md)/[A57](reader-driver-selection-review-a57-0041-20261024.md)，J08/1|selector的head=word(0x62fc9744)、动态next依据word(0x62fc9740)+4，N.word0取D后按首byte/ready/open门选用|以精确list header0x62fc9740为目标；不重做144B选择、open/close/read/seek或五ROM照片mode0|
|[A21](png-info-lifecycle-a21-0041-20261023.md)/[A22](png-info-review-a22-0041-20261023.md)|`0xa008aec0(list*)→node/NULL`正常分配并接头；PNG的list是G+0x110=0x62fc968c，payload28|继承helper泛型角色，不能把PNG对象/节点callback布局套本registry；不重读helper全部body|
|[A60](reader-driver-global-init-a60-0041-20261024.md)，J08/4|作者找到两槽初始化stride4/head0；本研究派发时仍待A61非作者复核|仅作为待复核初始化候选，不在本报告提前标已验；本题header身份由当前实际a0构造独立建立|
|A58/A59、J08/2|旧metadata不足、同偏移对象排除及POSIX源路径owner仍不等于实例绑定|不重复旧负搜索/同偏移排除；路径只用于定位本题候选，不直接认证driver类型/SDK版本|

原件沿 [CATALOG](../../../roms/CATALOG.md)：AP01 `1.0.2_0041`，主仓`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射`file_offset=VA−0x9ffff000`。新窗口仅读必要字节并核文件长度，沿用旧摘要、不重算hash，不混0031/SIM。

## 本轮复核或纠正

### 有界helper directcaller盘点

旧首轮index的direct_calls反向筛选只列9个caller，且该index的这些条目均无dossier/historical_dossier；这不表示所有其他历史载体都无body。元数据/EID/extent逐项留在本题本地JSON，只表示该索引直接边，不覆盖间接调用/未定义函数或错误extent。

|caller|旧extent字节|实际参数证据/处置|
|---|---|---|
|0xa0082914|108|A21旧原字段0xa008291e/2922构造0x62fc968c，属PNG；不是目标header|
|0xa0084b96|10876|F05/F06已验display list=0x62fc9580；大容器不重导|
|0xa008bc64|178|C01旧0xa008bc74/bc78构造0x62fc95f0，属timer list；不同header|
|0xa008bf6e|260|D19已有动画list0x62fc9628；不从同helper认作fs|
|**0xa008e3ac**|1226|同caller有fs.c诊断源xref0xa008e800/e820和insert-head边；旧选窗缺精确注册连接，缩小为本轮唯一新窗口|
|0xa00d733a|140|E05/E06已验关联句柄list0x62fc95b0；不同header|
|0xa00d9452|1492|本index无实参body；保留地址/extent，不新取大body或凭邻近地址分类|
|0xa00e0ac8|1996|既有区域消费者合同不认证此helper所有实参；保留未知，不重导其余业务|
|0xa00ebb90|776|A34已有cache-relative list接线；不因4B节点或同helper认同全局registry，未排除全部运行别名|

initializer条目`/functions/2121`的extent Evidence `ev_0a98ac5c6ce40886b07dc5c8869a8f6084d079f6348f1129e0c660555462062d`、directcall `ev_e6785d9ce3c5fd6458d9a903371b4aef0c06f3a5b4733b657bbc006d6cc4410b`只作定位。source_paths/239的fs.c xref Evidence `ev_c2b3a58114d1e9a99fd3b411b6f87a1f2cd76db0fb6e7b144f9c9b1697f56ee7`将诊断引用定位在e800/e820，但不能凭源路径宣称注册或POSIX D。

A21旧BIN窗口止e768、PNG窗口始e82c；旧端点有e75e的s1高位定义、e764的a1=0x34。缺的只是该具体callee中196B选窗，主窗登记后才读取；未因首轮metadata无dossier就无种子扩扫。旧A21/A22语义纠正0，新增的是本题不同list/对象的真实调用与保存连接。

## 真正新增

### header→insert-head→新节点首word保存D

|原件地址/字节|独立检查事实|对象/条件意义|
|---|---|---|
|旧A21 `0xa008e75e`，`b794fc62`|LUI s1,0x62fc9，s1=0x62fc9000；此为继承原字段|绝不沿用A60的s1=G；后续callee正常保存该寄存器是前提|
|`0xa008e768` `1385c474`、`e76c` `ef202fe2`|a0=s1+0x74c=0x62fc974c，调用既验清零接口0xa0080d8e；旧e764给a1=0x34|只保留D地址/接口参数；不把期间未知s2基址的后续store自动映成D字段，helper未展开|
|`0xa008e7d8` `3795fc62`、`e7de` `13050574`|LUI/ADDI独立U/I字段得a0=0x62fc9000+0x740=**0x62fc9740**|真实list参数，数值与已验selector header相同；不是按函数家族猜测|
|`0xa008e7e2` `efc0efed`|独立JAL字段目标 **0xa008aec0**|helper的list参数已绑定，N为该调用返回a0|
|`0xa008e7e6` `21e1`|独立C.BNEZ a0→**0xa008e826**|N非零才走本题正常保存臂，跳过e7e8等对s1的改写；N零不拼成普通成功|
|`0xa008e826` `9384c474`|ADDI s1,s1,0x74c，得D=**0x62fc974c**|保持的是高位常量s1，加完才变成D；helper正常保存s1前提保留|
|`0xa008e82a` `04c1`|独立C.SW字段`(base,source,offset)=(a0,s1,0)`|**word(N+0)=D**，存指针值而非复制driver结构体或source路径|

所读正常前段未另定义s1；0xa0080d8e和0xa008aec0两次调用都按已继承的正常callee保存寄存器约定使用。没有为解释这一点运行callee或新增ABI模型。空节点分支e7e8会将s1改为ROM高位地址且进入诊断区；本题不读取完整错误块、不认证其no-return/寄存器合同，因而不把静态布局接成失败后继续成功保存。

沿A21/A22已验helper合同，节点在helper内部接头发布后返回，本caller之后才写N.word0=D。保留这一原序，不改成“先填D再发布节点”，也不据此推并发原子性、即时consumer可见性或整个注册生命周期。D地址固定于该全局区域，N与D不是同一次对象分配；本caller只保存D指针，未证D结构体深拷贝、retain或注销释放规则。

局部伪代码（非原源码）：

```c
// 旧端点：s1=0x62fc9000；正常callee保存s1。
N = insert_head_a008aec0((void *)0x62fc9740);
if (N != NULL) {                    // e7e6 -> e826
    D = (void *)(s1 + 0x74c);       // 0x62fc974c
    store32(N, D);                  // e82a，helper已接头之后
}
// 零返回诊断路径不补造普通继续；D callback及生命周期另有断边。
```

### 偶遇的新槽写锚点，只保存不展开

授权短窗还含`e776: SB a5,0x1d0(s2)`、`e77a: ADDI a5,s2,0x180`，随后`e780/e784`形成a4=0xa00ef468、`e788`把a4以C.SW写`a5+0x5c`。必要VA/原字保存在JSON。**s2精确来源尚未在本题证明**，因此没有把该store认证成D+0x0c或POSIX callback绑定，也未读0xa00ef468等新目标body。这个新关系超出当前“node.word0保存D”闭包，已报告管理窗口另登记，不能从结构相似就补基址。

## 未闭精确边、检查与后继

真实list0x62fc9740→新N→D0x62fc974c连接已获原字段答案；初始化stride4/head0仍依A60/A61自身状态，不能由本报告提前独立接受。具体D首byte/盘符、s2到D槽写身份、每个callback地址/ABI、source后缀到此实例的实际匹配、替换/注销/节点及D寿命和真实FS/设备成功仍未闭。没有把九个直接caller说成全ROM完整调用图。

本题 [collect.py](../../analysis/reader-driver-register-gap-a62-0041-20261024/collect.py) 实际 **37项检查PASS**：有界旧索引caller/实参端点，以及14个新稀疏原字锚点50B，其中注册核心9条32B；JAL、ADDI、C.BNEZ和C.SW另独立解字段/地址。Capstone 5.0.7仅离线RV32/RVC解码，无新反编译/模型执行或REA生产ID。探索请求窗为[768,798)、[794,7c4)、[7c4,7f4)、[826,82c)，均在已登记区间，合150B请求/146B唯一指令字节；找到N.word0后停止，不读其他caller/helper/D槽目标。

另查JSON、报告引用、Git忽略、独占状态与diff；未运行A21/A60或旧作者检查器。[evidence.json](../../analysis/reader-driver-register-gap-a62-0041-20261024/evidence.json) 仅留本地原路径并由Git忽略，报告/复验源码未提交推送。

有种子后继只建议同 **J08/5** 的A63非作者限定复核：核e75e高位s1、成功门跳过改写、e7d8/e7de真实a0、e7e2返回N、e826/e82a保存D和helper正常保存前提，不重导initializer/其他caller。下一独立问题若恢复D槽绑定，应先登记`e77a`的s2+0x180基址到已注册D0x62fc974c的身份桥，不能直接展开callback本体或全fsdrv。
