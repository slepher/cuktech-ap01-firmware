# A77：固定format引擎已交付片段的非作者复核

2026-10-24；J08/12；非作者`/root/f12`，独占`review-close-a77` / `codex/re-0041-a77-review`，基线`bd457a6`。**限定接受[A76](reader-driver-format-engine-gap-a76-0041-20261024.md)已交付部分：入口S/va保存、literal `/` 的真实S+4(S,47)调用、本地s2计数与S.count分离、续读/零终止尾声及固定s已选门到3abe→3ae0一致。语义纠正0，复核新增业务0。** 可关闭A76这份交付的待复核状态；不代表`%s`取参/输出或完整ROM已闭合。

授权取自主仓最新[管理记录](rolling-management-0041-20261023.md)顶部“当前限定复核并关闭”与J08/12 A77进行行，非旧树认领表。先读最新[流程](reverse-design.md)、[保留规则](../../analysis/README.md)，采用已读REA技能。只做本轮三项中的本席复核，无滚动补位或后继研究；不运行作者check.py/旧脚本、目标/模型/输入试验、固件、SIM/QEMU、构建、回放、IO或外部服务，不切换共享REA，不改生产ROM配置/共享表/主树，无下级agent、提交推送。

## 继承结论

|已有来源|本轮继承与边界|
|---|---|
|[A75](reader-driver-format-review-a75-0041-20261024.md)限定接受A74|count256栈S六word=`{0,b536,b4d8,af2e,buf,255}`；先SB0至buf，再经旧d770显式前五word交`(S,0,0,fmt,va)`，fmt为旧ROM `/%s\0`，va首word为suffix；不认证最终NUL/返回含义|
|[A79](reader-driver-format-stream-review-a79-0041-20261024.md)限定接受A78|S+4 target使用low8(a1)栈byte转交b4d8；stream夹取/计数/NUL与任意copy n域前提保留。本题只验engine callsite，不重复三个body|
|F18及[A80](reader-driver-format-copy-gap-a80-0041-20261024.md)|n4有限旧域与n1作者域分开；A80本轮由A81独立复核，本席不自验copy、不将n1扩大任意suffix长度|
|A76旧metadata与查重|extent EID `ev_2ef71c21882936bf466e0db84b206e01d8bbb3b3e0343c9e8fed1cac5674caca`与direct-call EID `ev_f187bdf2006f155ea0d84318bf9db0b86db2f47bb49daf66f0e0501025fcb75c`仅定位，不等于引擎合同；不重做全历史负搜索|

旧索引profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3` / `f71eaf7d63ce1b1fa1671fe1932e6a44e275d3716b51411a6bb6af26d7663a44`保持原定位身份；旧d770 EID/profile沿A75。不为新字段虚构REA生产EID/profile。原件主仓`roms/0041/ap01-1.0.2_0041.bin`实核长度6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`、offset=VA−0x9ffff000，不重算摘要或套其他版本/SIM。

## 本轮复核或纠正

已读A76报告、contract、check.py与evidence，**未执行或导入作者脚本**。[review.py](../../analysis/reader-driver-format-engine-review-a77-0041-20261024/review.py)独立从原件取七个已登记半开窗：37d2..3852（128B）、3852..38c0（110B）、38e4..3950（108B）、4408..4430（40B）、38c8..38e4（28B）、3a78..3ad8（96B）、3a46..3a78（50B），均为a01a前缀，共560B。没有读取3ae0、其他case或新helper。Capstone5.0.7 RV32/RVC只用于静态宽度/普通效果/停界核对，关键普通I/S/B/J及压缩寄存器/立即数/槽偏移另独立拆字段，共 **65项PASS**。

|复核项|独立字段与限定结论|
|---|---|
|入口五word与保存|A75提供实际前五word，不据此补C原型或残值参数。37d2帧160B；入口保存ra、s0..s11；37f4 C.MV s6,a4保存va，37fe C.MV s1,a0保存S，3814 C.LI s2,0。入口至3832没有重定义fmt寄存器a3；不把初始a1/a2零推成它们永远为零|
|首literal选择|3832为LBU s3,0(a3)；3836等零→4410；383a设0x25，383e等值→3858。继承首byte0x2f走literal：3842/46保存fmt+1至s0−0x6c，384a先给s2+1，384c C.LW a5,4(s1)，384e a1=s3，3850 a0=s1|
|真实间接ABI与返回忽略|3852原字8297独立拆为C.JALR a5，故实际调用word(S+4)(S,47)。3854为JAL rd=zero→4408，回返a0未参与比较或s2更新。不能将本地计数等同callback实际接受n或S.word0；callback正常返回/保存约定是前提|
|续fmt与零尾声|4408 LW a3,-0x6c(s0)，440c直跳3832。零byte门直接到4410；尾声十二个栈恢复，4428先C.MV a0,s2，442a才恢复原s2，442c恢复sp，442e RET。该有限尾声无S.count读取、callback、NUL写或a0再折叠；仅证明到达它时返回本地word，不证明完整固定format已能到达|
|百分号及固定s入口|3858读fmt+1的U8 s3，385c/60保存fmt+2；3864仅双百分号回384a。固定s3=0x73不取该门；3872/74/76清s4/s5/s10。38b4为unsigned 0x3f<s10，假；38b8等0x2b，假；38bc unsigned0x2b<s3，真→38e4|
|源字符门与digit分流|38e4等0x2d为假；38e8不等0x30真→38c8。38c8/cc得到(s3−0x30)&255=0x43；38d0 unsigned9<0x43真→3a78。这个代入只用继承固定literal，非host输入枚举|
|star/dot及modifier|3a78不等0x2a→3aa8；3aa8不等0x2e→3a46。3a4a不等0x7a、3a4e不等0x74，3a52不等0x6a→3aba；3aba mask0xdf得到0x53，3abe不等0x4c→**3ae0**。各B型funct3/寄存器/目标独立核，不能误接未选数字/宽度旁支|
|va与本地计数范围|所选post-save片段没有s6使用，未见va读取/推进或suffix取出；不能由保存va直接补`%s`取参。s2仅本地计数/正常返回角色，与S.count是不同存储，不证明两者相等或标准printf长度含义|

五个旁支停解点38f4、38dc、3a80、3ad2、3a5e均按原位置保留4B未知前缀，未补NOP、执行模型或从其内部半word接续。原七窗的560B是**实际读取边界**，不代表整窗每个旁支语义全覆盖。3aa8是已独立核BNE的真目标且在授权窗内，因此可从该目标核所选片段，区别于跳过未知字强行线性续接。精确前缀与检查见本地忽略[evidence.json](../../analysis/reader-driver-format-engine-review-a77-0041-20261024/evidence.json)，不保存全引擎导出。

未发现A76语义错误；接受仍需局部栈/S/buf/fmt/va/suffix在相应使用期间有效、有适当容量/分离、无破坏性别名或不兼容修改，callback正常返回并遵守必要保存约定。S和va保存在callee-saved寄存器/局部栈，不因此外推未读case、copy或整个库全无更深持有；无源码/库版本认证。

## 真正新增

**复核新增业务0、语义纠正0、ISA/来源认证0。** 65项独立字段/覆盖界限检查与重读560B只构成A76已交付差集的非作者验收；A75/A79/F18旧接口不重计新增，A80/A81不由本席重复body。[contract.json](../../analysis/reader-driver-format-engine-review-a77-0041-20261024/contract.json)将可关闭的待复核状态与尚未闭合的固定s链明确分开。

## 未闭精确边与关闭范围

精确断边仍为 **0xa01a3abe→0xa01a3ae0**，3ae0未读。suffix何时从va取出/推进、S+8/+c实际调用端与顺序/参数、字符串长度/精度/计数协议、完整固定format能否到达零尾声、实际输出/path、最终NUL/截断及借用结束继续未知。单个literal调用与返回s2不证明slash/suffix已写出，更不能由函数名补完整printf协议。

本轮仅“复核以及关闭”，不请求展开3ae0、不派后继或新研究。JSON、报告链接主仓后备解析、空白/git diff --check、独占status及生成物忽略保留检查通过；报告/源码/合同与本地证据未提交推送。保存交付后停止，由主窗整合清理工作树/分支。
