# A73：实际D条件生命周期合成的非作者复核

2026-10-24；J08/10；非作者 `/root/f12`，独占 `re0041-a73` / `codex/re-0041-a73`，基线 `bd457a6`。**限定接受[A72](reader-driver-lifetime-a72-0041-20261024.md)：source分类1确实首匹配此D且所需字段/正常服务前提成立时，既有generic reader持有与归还合同可接到D=0x62fc974c。语义纠正0，复核新增业务0。** A69/A71现已非作者限定接受，A72的待验文字保留为写作时历史状态，本复核更新继承状态，不重验原字段。

授权为主仓最新[认领表](rolling-management-0041-20261023.md) J08/10 A73进行行；采用已读[流程](reverse-design.md)、[保留规则](../../analysis/README.md)与REA技能的旧合同优先规则。只读既有报告/合同，ROM0B，不跑A72 check.py或任何旧技术脚本，不执行目标/模型/host输入枚举、固件、SIM、构建、IO或外部服务，不切换共享REA。不改主树/共享表/生产配置，无下级agent、提交推送。

## 继承结论

|可靠来源|本轮直接继承与实际边界|
|---|---|
|[A49](photo-reader-mode-review-a49-0041-20261024.md)|分类1→mode1 W、H/D/C前缀、普通open、配置重读及close(D,H)后条件归还/清槽；mode1不等于五照片实际路径|
|[A52](photo-reader-consumer-review-a52-0041-20261024.md)|五参read/四参seek、C字段/B懒申请、回调后C重读、计数/状态分离及低31bit copy限定|
|[A57](reader-driver-selection-review-a57-0041-20261024.md)、[A63](reader-driver-register-review-a63-0041-20261024.md)、[A65](reader-driver-slot-review-a65-0041-20261024.md)|动态next/首匹配/optional门；实际header9740与D974c保存；同D盘符、配置初值及四槽；先发布N后填D的原序和ABI条件保持|
|[A67](reader-driver-open-close-review-a67-0041-20261024.md)|mode2 flags1、format输入与返回被忽略、非负fd编码H、close解码与结果门；实际输出/IO不随接口被认证|
|[A39](photo-decoder-review-a39-0041-20261024.md)、[A42](photo-destroy-review-a42-0041-20261024.md)及A49|W当前0x664字节复制入独立O、owner持有O/内派生指针；正常替换时外层另归还O、清owner槽；最终DELETE未闭|
|[A69](reader-driver-read-seek-review-a69-0041-20261024.md)、[A71](reader-driver-result-map-review-a71-0041-20261024.md)|现在均限定接受；read下层signed r>=0含零写count后callback0，seek只以a0 signed门折0；负分支映射第二getter实际word，0→0，不反推IO成功|

原件身份/VA映射沿各来源0041、6,769,704B、既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`及VA−0x9ffff000；本轮没有读取/重算原件。旧EID/profile归各原报告，不为文档合成虚构新REA记录。

## 本轮复核或纠正

独立检查的是A72**合成强度与出处一致性**，不是重做作者脚本或原字段验收。[review.py](../../analysis/reader-driver-lifetime-review-a73-0041-20261024/review.py)用标准库定位32处必要报告锚点、比较12项机器合同不变量；[reference-evidence.json](../../analysis/reader-driver-lifetime-review-a73-0041-20261024/reference-evidence.json)保存精确来源行号和结果，本地原路径忽略保留。锚点匹配用于可定位性；下列顺序/对象意见来自逐项阅读，不能将文本命中自动说成语义证明。

- **选择与字段前提**：source首byte相等不能跳过首匹配顺序、可选D+8门与open槽门。给定source分类1且本次实际选中此D才可接线；注册/初始化静态正常路径不证明已执行、letter唯一、后续无writer或注销。D+4初写4096不等于之后每次配置读取都是4096。
- **对象身份**：slot_base=0x62fc96fc=D−0x50只是initializer寻址根，绝非A50的cache_buffer。D为借用global，H是low32(fd+1)值，既有caller/callback未以D/H作deallocator对象；不把它们合成FILE*或独立heap handle。H往返对应同次资源仍需配对来源/fd未提前关闭或复用。
- **C/B/W/O**：普通配置域的C为单独16B申请，reader+8持有；小读需填充且B为空才按当前k申请，C+c持有B。want>k可直读，无每读申请4096结论。W→O复制当时状态和C指针，不复制B数据、另建C或保存栈W地址。W可在所继承成功copy/使用合同下结束，C/B继续存活；O为另一个根，owner+74内部指针不独立归还。
- **消费精度**：read status和got/filled都是独立word；传NULL省对外写而不省内部计量。回调后重读C、原status==0位置门、跨缓存copy低31bit掩码与全word总消费分别保留；seek返回未用作随后read门，不补成功检查或简化成无条件min。
- **close与归还原序**：D或close槽空会跳过内部清理/清槽。真正调用close(D,H)并正常返回后，generic层不测试其status作清理门，重新读reader+4→D+4及reader+8。当前配置0跳过C/B；非零且C非零，配置非ffffffff并C+c非零才归还buffer，再重读reader+8归还C；配置ffffffff跳buffer仍归还C。随后该已调用回调路径清前三word，外层另归还O并清owner+5c/+74。不把callback前旧D/C替代重读，不把“close成功”当缓存free必要门。最初持有那一组C/B确为后来归还对象仍需字段保持、有效独立归还根及兼容别名/并发效果前提。

无语义纠正。A69/A71最新接受只是依赖状态刷新：正常下层r>=0是可组合的给定成功域，callback status0本身不充分，因为第二getter word可能0且map返回0。A72已经明确隔离这种反推，不能因待验状态消失而放宽为全部负分支/IO资源成功。

## 真正新增

**业务/字节恢复/语义纠正均0。** 本轮仅给A72条件组合提供非作者限定接受与引用检查；32锚点+12一致性检查PASS，ROM读取0B，作者/历史脚本运行0。没有把旧A50/A52计数算法或A69/A71结果重新计作新增功能。[机器合同](../../analysis/reader-driver-lifetime-review-a73-0041-20261024/contract.json)保留对象身份、字段保持、清理顺序及最新依赖状态。

## 未闭精确边

实际类型1实例及本次registry首匹配身份、实际format输出/截断/NUL、底层IO与物理关闭效果、后续writer/注销/heap复用、所有失败臂及最终DELETE继续未知。A74在其独立范围研究format，A73不补它的输出断边；默认五ROM照片仍为已验mode0。

有种子后继仍需实际source分类1调用点/字节及本次N.word0身份，或已持有O+4/O+8、D+4/槽、C+c的具体后续writer，才可谈同次资源保持；本题无新增这样的种子，不扫描registry/FS/heap。成果JSON、相对链接主仓后备解析、空白/git diff --check、忽略与独占路径检查通过；交付停止，未提交推送。
