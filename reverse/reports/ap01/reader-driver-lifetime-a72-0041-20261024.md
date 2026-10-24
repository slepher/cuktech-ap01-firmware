# A72：实际D接入reader的条件生命周期合同

**给定source分类1、选择器确实首匹配已注册D=0x62fc974c，且所述正常路径、有效存储与服务前提成立，旧通用reader合同可以接到该D：D借用，H是fd+1的数值编码，C持有懒申请的cache_buffer，成功构造把当时W状态浅复制到独立O。** 正常替换时先调用close(D,H)，再按回调后重读的配置/指针条件归还cache_buffer和C，外层另归还O。没有free(D)、free(H)或由此转移source所有权。

2026-10-24；J08/10，任务A72，`/root/a56`；独占`re0041-a72` / `codex/re-0041-a72`，固定基线`bd457a6`。采用REA留存优先流程，本题仅合成主仓既存合同，不读新ROM/新helper、不运行旧脚本、不接共享REA。无目标/固件/指令/模型、SIM/QEMU、构建、回放、IO/设备或外部服务执行；不改生产/主树/共享表，无下级agent、提交或推送。对象名为分析命名，不认证源typedef/库精确版本。

## 继承

|已独立接受的合同|本题复用的必要边|
|---|---|
|[A47](photo-reader-mode-a47-0041-20261024.md)/[A49](photo-reader-mode-review-a49-0041-20261024.md)|source分类1→mode1 W；W前缀H/D/C位于+0/+4/+8，+0x10为mode byte；普通open/close接口、配置重读、C条件申请与归还；既有A37/A39浅复制及A41/A42外层O归还一并继承|
|[A50](photo-reader-consumer-a50-0041-20261024.md)/[A52](photo-reader-consumer-review-a52-0041-20261024.md)|read五参/seek四参；普通缓存C+0/+4/+8/+c的范围/位置/buffer；B懒申请、回调后C重读、计数/状态分离与归还字段连接|
|[A56](reader-driver-selection-a56-0041-20261024.md)/[A57](reader-driver-selection-review-a57-0041-20261024.md)|按source首byte匹配N.word0候选D；动态后继、首匹配、可选D+8及open门，通过后W+4=D|
|[A60](reader-driver-global-init-a60-0041-20261024.md)/[A61](reader-driver-global-init-review-a61-0041-20261024.md)，[A62](reader-driver-register-gap-a62-0041-20261024.md)/[A63](reader-driver-register-review-a63-0041-20261024.md)|正常初始化head0/stride4；实际list调用返回N非零后写N.word0=D。helper先发布N、caller随后填D的原序保持，不认证并发快照/初始化已实际执行|
|[A64](reader-driver-slot-bind-a64-0041-20261024.md)/[A65](reader-driver-slot-review-a65-0041-20261024.md)|同已注册D首byte`/`、D+4初值4096，以及+c/+10/+14/+1c四槽实际写端；slot_base=D−0x50只是写端基址|
|[A66](reader-driver-open-close-a66-0041-20261024.md)/[A67](reader-driver-open-close-review-a67-0041-20261024.md)|mode2实际flags1、format输入界面、非负fd→H编码、close解码/非负折0及错误槽重读边界；不读底层IO/formatter|

历史报告在当时将D绑定或C填充列未知，与后来独立接受的A65/A52可以按同地址/字段连接；不是倒改旧报告当时的证据范围。本题不重验任何原字、厂商规则或既有技术检查，原EID/profile保留各来源，不生成新REA记录。0041原件身份/映射沿既有合同，本题ROM读取0B。

## 复核与纠正

本题不是新字节恢复或上述作者成果的替代技术验收。静态引用一致性检查对实际主仓报告建立定位，验证同一D有效地址/四槽、两个分配根及浅复制、数值H、配置域和待验排除；[check.py](../../analysis/reader-driver-lifetime-a72-0041-20261024/check.py)不导入任何旧脚本。40处必要引用锚点、10项合成不变量PASS，生成`reference-evidence.json`保留来源文件与行号，忽略留本地原analysis路径。

**语义纠正0。** 特别保留三项强度：初始化4096是写端初值，不是close后的当前值；callback返回0不证明实际下层IO成功；“未见free(H)”与具体H数值表示由A67共同支撑，不以不同参数来源推对象不别名。下述合同需要实际存储有效、适当容量/不别名、正常分配和服务返回及callee保存约定；不从非零指针自动补这些前提。

## 真正新增：实际D到旧通用生命周期的连线

新增为这组**已验同D绑定与既验generic持有/归还合同的条件组合**，新字节/新业务功能均0。不是实际source实例、实机I/O、所有producer或完整FS的认证。

|角色|借用/持有与结束边界|
|---|---|
|source及suffix|选择读取source首byte；非空source的suffix按既验规则为source+1，第二byte为冒号时为source+2。可选回调前后suffix保存恢复，随后open(D,suffix,2)。此链无source归还或所有权转移；source/suffix须在这些读取/调用期间有效。已验reader前三word存H/D/C而非source，不等于证明formatter/底层IO或整个O所有字段绝不另留来源；不据此给source全栈失效时刻|
|D与registry N|D=0x62fc974c是已注册节点保存的全局地址；选择后借用于W/O及每次槽调用。reader没有归还D或N。head/stride初始化及注册的正常门不证明运行时存在节点、letter唯一、后续不修改/注销或调用时D仍有效|
|slot_base|0x62fc96fc=D−0x50仅为initializer的slot写端寻址基址。**它不是C、cache_buffer或H**；A65旧变量B与A50缓存B名字相同不构成对象身份|
|H|该D的+c绑定a00ef468。普通mode2路径将suffix作为format首vararg，buf/256/literal`/%s`交wrapper，忽略format返回，再以(buf,1,0x1b6)调fd-open接口。signed fd≥0时H=low32(fd+1)，保存W+0。H为值，不是需要free的独立heap对象。相配close以low32(H−1)交fd-close；需同次open身份与fd未被提前关闭/复用，数值往返不证明实际资源身份|
|C|普通open返回被接受并保存H后，初始化重读D+4；非零配置才请求0x10字节C并由W+8持有。C不是O内部派生区，也不是slot_base。普通缓存合同仅取当前k非零且非0xffffffff域；分配正常非空、C有效等须另外成立|
|cache_buffer|C+c是单一持有字段。小读需填充、保存B为空时按当时k申请，存C+c后重读；已有B则复用。want>k可直读dst，不必申请B；不是每次read都分配4096。B有效/实际容量匹配当前请求、输出区与其适当分离及资源未被并发归还均是前提|
|W→O|W为栈工作区，构造先消费可能更新C/B的reader状态，成功后copy(O,W,0x664)。复制的是**当时**H/D/C/mode等状态，不保留栈W指针、不另申请C或复制B数据。按既验成功copy合同完成、后续用O作reader后，W自身工作区可随wrapper退出失效；C/B须继续存活，不能随W栈帧一起归还。O是另一个heap分配根，由owner+5c持有|

这里`/%s`与实参只支持斜杠前缀拼接的family意图；实际输出/截断/NUL及路径解析未证。source首byte`/`与D.byte0相等也不能替代“本次确实选中此D”的前提：前面可能已有同letter节点，registry可变化。

**消费期间的重读与计数保持原合同。** read槽调用为(D,H,dst,want,&got)，填充时改为(D,H,cache_buffer,k,&filled)；seek槽为(D,H,position,0)。通用层保存状态与实际count为独立word，wrapper传NULL只省对外count写，不取消内部计量。缓存填充callback后重读C，更新start/end，再按原路径copy；只有原status==0门才更新逻辑position。跨缓存copy的低31位掩码与总实际消费word不能混成一个无条件min。seek返回未被通用层用作后续read门，不能补检查。D+4的读取点、C/B指针重读及服务副作用条件均不折成一次入口快照。

**正常替换归还序列接到该D的+0x10=0xa00ef502：**

1. 外层O非零、mode byte非零时调a01b2e3a(O)。入口D或close槽为空会跳过内部清理/清槽，不能无条件化。
2. D与槽均非零时调用close(D,word(O))。相配H解码fd；所选下层signed r≥0域由A67返回callback0，但generic层**不拿callback返回值作清理门**。这不是“关闭成功才free缓存”；只要这次callback正常返回便按后续原门处理。若其不返回，不能假设后续清理执行。
3. **回调后重新读O+4，再读当前D+4。** 当前配置非零且当前C=word(O+8)非零才处理C。当前配置不是0xffffffff且word(C+c)非零时先交a008ab8a归还cache_buffer；随后重新读O+8交a008ab8a归还C。配置−1跳过buffer归还但仍归还C；配置0跳过两者。不能强行代入初始化4096、缓存旧D/C或由参数表达不同证明不会别名。
4. 已调用回调的这条路径再依次清O+0/+4/+8；callee不清mode byte。外层另归还O，清owner+5c/+74。D/H不是这些deallocator的对象参数。只有在同C/B身份、有效独立归还根及无不兼容并发/别名副作用等前提下，才能把最初持有的那组C/B接到这次归还；不保证任意后续writer后的对象仍相同。

因此W栈工作区与堆C/B、O寿命分开；H资源归还请求先于缓存归还，缓存buffer先于C，外层O最后。该原序不是底层资源已物理关闭、heap地址不复用或页面最终DELETE的证明。

### 待验依赖单列

|协议|本合成如何隔离|
|---|---|
|[A68](reader-driver-read-seek-a68-0041-20261024.md) / A69进行中|实际read/seek callback作者候选包括H−1、显式word实参、read非负r写out_count后返回0、seek非负折0及两次错误槽读取。非作者接受尚待A69；本题不把候选变成已验的count/EOF/off_t/持有合同。所述“正常IO完成”须作为条件给定，不能由callback status0反推|
|[A70](reader-driver-result-map-a70-0041-20261024.md) / A71待验|A70作者报告已整合，映射独立复核仍待A71。不复制/重建数值表；本题所选下层r≥0成功域不依赖错误map。负分支、第二次错误word与实际IO状态关系继续开着，不能拿map返回0推全部成功|
|format输出|已有专席/准备A74；本题只继承输入界面，不重派、不恢复formatter|

最小机器合同见[contract.json](../../analysis/reader-driver-lifetime-a72-0041-20261024/contract.json)，显式区分source、D、slot_base、H、C、cache_buffer、W、O，以及配置域和待验协议。上述条件组合未把任何回调status0当成完整成功证据。

## 精确未闭与后继

实际source类型1路径/实例、确实选中该D、实际格式输出、IO服务行为与真实关闭效果、registry/descriptor后续写入或注销、地址独占/heap复用、所有producer/失败臂及最终DELETE仍未知。默认五ROM照片仍沿已验**mode0**，不因本合成改成mode1。

可用后继需要**实际类型1调用点及其source字节/本次registry身份**，或明确的**已持有O+4/O+8、D+4/槽、C+c的后续writer种子**，才能研究同次资源保持。当前没有新增这类种子；不派重复read/seek/map/format题，不扫描全registry/heap/FS。

实际检查仅标准库引用/合成一致性：40处定位锚点、10项不变量PASS；JSON解析、报告链接主仓后备解析、独占status、忽略原路径保留及`git diff --check`。没有新ROM字节、原字段执行、旧脚本运行或新callee。成果未提交，交付停止供主窗安排非作者A73。
