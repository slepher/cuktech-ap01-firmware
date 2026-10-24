# A60：J08/4 已知global初始化门到reader两槽的确切写入

2026-10-24；固定研究基线 `bd457a6`，分支 `codex/re-0041-a60`，认领 **J08/4**，作者 `/root/g23`。**已从真实初始化指令找到两槽writer：正常`0xa008e4c4→0xa008e506`路径、s1保持已验G=0x62fc957c时，`0xa008e51c`置a5=4，`0xa008e51e`把word4写G+0x1c4=0x62fc9740，`0xa008e522`把word0写G+0x1c8=0x62fc9744。** 这补上初始化状态；仍未恢复registry节点登记、N.word0=D、具体D及其slot绑定或寿命。

G整块初始清零0x210及UI caller→initializer是A21/A22/A25/A26既验，继承新增0；本轮新增是这两条专用word写的地址、数值及正常基址链，不把整个initializer或driver注册称为新增完成。A56的`next_off=word(G+0x1c4)+4`在该初始化值未被后续改变时得到8；不把这个条件结果升级为实际registry已有节点、默认照片mode1或具体driver。

已读主仓 [流程](reverse-design.md)、[保留规则](../../analysis/README.md)、[唯一认领表](rolling-management-0041-20261023.md#链条认领表) 的A60/J08/4与逐次增量登记，采用 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 留存优先规则。先只查三个已知G owner的必要旧指令；发现已验初始化callsite后先登记才查A21/A25旧窗。旧留存缺精确区间后，再由管理者明确准许 **[0xa008e4c4,0xa008e612)** 最多334B原字段升级；实际只读两个48B探索短窗、找到目标即停止，不继续剩余缺窗或1226B全initializer。

没有切换共享REA/开数据库或修改profile模型，没有目标/指令/模型执行、固件、SIM/QEMU、构建、旧技术脚本、回放、异常输入、设备或外部服务；未改生产ROM配置、主树/共享表，无下级agent、提交或推送。原字段解码是静态观察，非执行；本文伪代码非原源码，作者自检待非作者复核。

## 继承结论

|出处|已有行为与局限|本轮处理|
|---|---|---|
|[A56](reader-driver-selection-a56-0041-20261024.md)/[A57](reader-driver-selection-review-a57-0041-20261024.md)，J08/1|精确G、head0x62fc9744、stride0x62fc9740及next偏移、节点word0候选D与正常reader选择门已验|不重读144B或来源/接口，使用两精确槽作本轮目标|
|[A58](reader-driver-writer-gap-a58-0041-20261024.md)/[A59](reader-driver-writer-review-a59-0041-20261024.md)，J08/3|旧metadata及有限文本查询不足；同+0x1c4的0xa005a8f4 store未获G身份；screen owner已纠正|本题改变输入为实际G定义/用途，不重复全载体负搜索、不重做栈对象排除，不声称全局无writer|
|[A21](png-info-lifecycle-a21-0041-20261023.md)/[A22](png-info-review-a22-0041-20261023.md)|a008e3ac清零G的0x210B及PNG registry局部合同已验|清零完整覆盖两目标word，直接继承；PNG注册主体不重开|
|[A25](pixel-memory-contract-a25-0041-20261023.md)/[A26](pixel-memory-review-a26-0041-20261023.md)|a005cd36→a008e3ac调用及G/s1、像素三表真实写入已验|复用caller/init和基址，不把caller发现或初始清零算新writer；像素表算法不接管|

原件身份沿 [CATALOG](../../../roms/CATALOG.md)：原厂AP01 `1.0.2_0041`，主仓`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射`file_offset=VA−0x9ffff000`。升级原字段时仅核文件长度并引用旧身份，不重算摘要，不混0031/SIM。旧dossier EID/profile与旧原字段导出的各自来源保留，不伪造新REA Evidence ID。

## 本轮复核或纠正

### 三个已知G owner的必要旧定义/用途

|旧owner及留存|本轮必要连接|界限|
|---|---|---|
|0xa005cc1e，`whole-rom-retained-20261023-000.json#/structuredContent/normalized_result`；EID `ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866`|a005cc68 LUI0x62fc9；cc6c读G.byte0，cc70形成G，cc74存帧槽−0x3c4；cc78零门跳cd36调用已验initializer|发现真实G条件调用端，但早有A25/A26合同；不是新发现callsite|
|同owner的G帧槽后继|cd62重读后仅展示G+0x68 store；ced2重读后以LBU G+0覆盖a5；ee9a重读后以LBU G+1覆盖a5；eeaa将该帧槽重用于返回值0|精确−0x3c4/s0引用仅这六条，不把重用后的slot或被byte加载覆盖的a5继续当G；不解释其他字段功能|
|0xa005a736，`whole-rom-retained-private-20261023-000.json#/structuredContent/normalized_result`；EID `ev_06476b86aac1e3cfbfd38e938f8f5eddb97e919fafdf21781b11f1c0fdee62bc`|be32 s5=0x62fc9000；be3a a4=G，be48/be4c只写+0x9c/+0xa0；be54重建G、be58存−0x160；c8ae重读后清同两字段|精确−0x160/s0引用只有保存/重读两条；s5在bebe被重定义、a4在相关后继也被重定义，不能把后续同寄存器任意偏移接成G；不展开那些字段/调用|
|screen owner0xa00b2f6c，`screen-host-append-20261020-v2.evidence.json#/records/3/normalized_result`；EID `ev_4886172901a9e225dff9550469d68d48bc8dbcc6aeafe83649d8f5674acc0127`|b2f94/98形成G，b2f9c读+0x40，b2fa6写+0x40；之后以其他a0值调用opaque服务，G在caller-saved a5中不跨调用强行延续|这是G直接用途的局部边界，无G+0x1c4/+0x1c8身份桥；不接screen其他字段或混同旧records8立即数|

三个owner这批必要展示用途没有直接给出两精确槽writer，不能据此排除其未知callee副作用或所有运行/别名路径。普通寄存器定义/帧槽引用筛选不是新完整CFG、别名分析或整个global重建。

### 旧initializer覆盖与改变输入

A21已有原字段窗口仅：e3ac..e3d8、e4bc..e4c4、e612..e628以及BIN/PNG相关片段；A25 initializer留存为e3ac..e4b8。它们证实`e3c4/e3cc`形成G、`e3c8`长度0x210、`e3d0`调用已验清零服务，`e3d4`得到s1=G，`e4c0`得到s4=G+0x100。两槽的**初始清零**由旧合同直接覆盖。

但这些选定导出不含[e4c4,e612)的中间片段；旧e61a的`s2+0x18`又没有该局部片段里的s2定义，不能猜成两槽。缺窗只指这两份选定导出，不声称所有历史都无该代码。管理窗口查旧pass1..5未得完整callee后，明确登记了上述精确缺窗原字段升级，才进入下一节；没有以缺材料为由重复全ROM/资源导出。

旧语义纠正0。此前“writer未知”按当时载体成立，本轮改变输入后补出明确初始化writer，不删除旧有限盘点/接受记录。

## 真正新增

### 正常基址链、目标地址及原写入顺序

新探索指令窗为 **[0xa008e4c4,0xa008e4f4)** 与 **[0xa008e506,0xa008e536)**，共96B；找到精确SW后停止。第一窗`e4c4`为C.BNEZ a0→e506；零分支在e4c6会改写s1，故本报告只沿**a0非零跳过该分支**的正常路径保留已验s1=G，不把错误分支拼成普通继续。

到目标前有`0xa008e516→0xa0087b06`，这是旧initializer directcall已列的opaque helper；本题未展开。s1是callee保存寄存器，以下地址链以正常调用遵守该保存约定为前提，不由此认证helper内部、副作用、初始化成功或实际运行。`e51a`只改a0，`e51c`改a5；所读短路径没有另定义s1。

|地址/原字节|独立解码/字段|确切意义|
|---|---|---|
|`0xa008e4c4` `29e1`|C.BNEZ a0→0xa008e506，独立压缩branch字段核目标|a0非零的所选路径保留此前s1=G；不覆盖零路径|
|`0xa008e51c` `9147`|C.LI a5,4；独立rd/imm/funct核对|准备完整word值4|
|`0xa008e51e` `23a2f41c`|SW a5,0x1c4(s1)；独立`(opcode,f3,base,src,imm)=(0x23,2,9,15,0x1c4)`|word(**0x62fc9740**)=4，真实stride槽writer|
|`0xa008e522` `23a4041c`|SW zero,0x1c8(s1)；独立同字段src=0/imm0x1c8|word(**0x62fc9744**)=0，真实head槽显式初始化|
|`0xa008e526` `23a6041c`|SW zero,0x1cc(s1)，src=0/imm0x1cc|同原序第三次word0写0x62fc9748；只保留锚点，不由此恢复容器全布局或另追该槽|

G+0x1c4/G+0x1c8的地址算术、32位SW宽度、数值4/0及原序均独立核过；未知厂商编码没有被补成NOP，本次选定锚点全是普通RV32/RVC。后续注册节点、分配、N.word0写D或slot回调没有出现在本题已证差集中，不能由stride4推它们都已恢复。

局部伪代码（非原源码）：

```c
// 继承：已验initializer此前清零(G,0x210)，s1=G。
// 新差集仅所选a0非零正常分支，跨helper遵循s1保存约定。
if (a0 != 0) {                      // 0xa008e4c4 -> 0xa008e506
    /* 其他字段原操作及opaque helper保持边界 */
    store32(G + 0x1c4, 4);          // e51e
    store32(G + 0x1c8, 0);          // e522
    store32(G + 0x1cc, 0);          // e526，同序锚点
}
```

新增是**确切初始化状态**，不是新整函数、整LVGL来源认证、实际driver注册/注销或服务执行。继承清零0x210/caller新增0；不以导出文件/指令数为功能完成标准。

## 未闭精确边、实际验证及后继

初始化两槽现在有有定位的写入者，但N.word0=D节点创建/登记、将节点发布到head、具体D及open/close/read/seek目标、实际初始/后续source盘符对应、对象寿命、注销及并发仍未闭。所选正常分支的入口条件与helper正常保存约定是证据前提；没有设备/SIM或真实执行观察，不宣称五ROM照片走mode1。

[collect.py](../../analysis/reader-driver-global-init-a60-0041-20261024/collect.py) 实际 **73项有界检查PASS**：旧owner必要定义/帧槽引用、已验初始化覆盖，以及 **12个新稀疏指令锚点/38B**、三条SW/CLI/压缩条件门的独立字段和地址核验。新解码为Capstone 5.0.7离线RV32/RVC，没有新反编译、原指令/模型执行、旧脚本或REA生产分析。[evidence.json](../../analysis/reader-driver-global-init-a60-0041-20261024/evidence.json) 保存探索范围、必要原字/VA、旧EID/profile和局限，按规则留本地原路径并忽略，不提交逐指令结果。

另查JSON、报告引用、Git忽略、独占文件及diff；没有重跑A58/A59全载体查询或A21/A25技术脚本。作者自检待非作者独立接受。

有种子后继仅为同 **J08/4** 的A61非作者复核：核`e4c4→e506`正常分支、继承s1=G/跨e516保存前提、`e51c/e51e/e522/e526`确切数值/宽度/地址和新增/继承边界，不重导全initializer。节点注册要另从这些精确槽的已有write-xref/后续发布种子登记，本题不自行派生新callee或扩大剩余缺窗。
