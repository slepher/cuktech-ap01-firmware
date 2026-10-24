# Q-26 v3 property/event subscribe/unsubscribe：staged→ACK→输出/清链

作者静态恢复，待非作者复核。认领 Q-26（口头 Q26），完整派发 S-P34。只回答四条 RPC 的本地结果生命周期；callback 返回值不代表设备或后台订阅已经生效。未运行固件、模型、SIM/QEMU、回放、构建、设备或外网，未改生产/ROM/分析器/共享 REA。

## 合同、身份与证据

主仓 `reverse/reports/ap01/reverse-design.md` §3.1/3.2/5.1/7 和绝对主仓 `rolling-management-0041-20261023.md:333` 的 Q-26 行已读。工作树 `D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/rpc-subscription01`，分支 `codex/app-rpc-subscription-research-01-20261025`，基线 `9100a552b6862e9a3f884182b9da4f45eeac68ee`。未更改他人文件。

以下地址/字段偏移均为十六进制；明确标为 B 的大小为十进制。

ROM `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，重算 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射 `file_offset=VA−0x9ffff000`。新增是离线读取的 shipped-artifact 原字和 Capstone 5.0.7 RV32+C 解码，不新造 REA Evidence ID。十三窗共2784 B，逐窗原字、SHA、offset、逐指令地址与相对控制流绝对目标在同 stem analysis/static-windows.json；extract.py 可复验。不将 Capstone 的 jal 相对数当绝对地址。

| 新窗 | 字节 | 作用 |
|---|---:|---|
| a00c6368..a00c657b / a00c657c..a00c6787 | 532 / 524 | property sub / unsub result |
| a00c6788..a00c6993 / a00c6994..a00c6b9f | 524 / 524 | event sub / unsub result |
| a00c0492..a00c04ab / a00c04ac..a00c04c5 | 26 / 26 | property error |
| a00c2148..a00c2161 / a00c2438..a00c2451 | 26 / 26 | event error |
| a00c1fd8..a00c208f / a00c2090..a00c2147 | 184 / 184 | property / event output serializer |
| a01adbd4..a01adc0d / a01adb9a..a01adbd3 | 58 / 58 | property / event ACK matcher |
| a00c187c..a00c18d7 | 92 | event staging |

四个旧根只继承有效请求解析/安装/成功保链/失败清链接口。父卡为主仓 `evidence/rea-0041-20261017/evidence/upper-miio-b.md` 四地址；其 EID 依次 `ev_790146c2658bc4f0705d54d3515b34e162566b36bd4c28d0d17db5e7fc55ed87`、`ev_7e388cdc7b77a16a8cf3ceb82eb6694b9a4209aa9fa70bd6958cd13d7b6fbfa9`、`ev_d1be944ad55ee4d06a920d328d83b3f62e6fdc82b5cb63ca85dbfa234ff590a1`、`ev_bb7cfc79fe6b9e1a145136959ed6f377984b3f6c747fb9f7529a580575bd2f43`。另一个 profile 的真根来自同目录 upper-complete.evidence.json records280/56/50/135，完整记录保留 inherited-roots.json，不混写 profile。

| root | head H | DID槽 | result / error | upper-complete EID |
|---|---|---|---|---|
| a00c1144 property sub | ctx+2e4 | ctx+2c4 | a00c6368 / a00c0492 | ev_db33625e03f3e24175d2c317d0ae631e60913589eb0092b638ac297783c535d4 |
| a00c13f2 property unsub | ctx+30c | ctx+2ec | a00c657c / a00c04ac | ev_258c7b21e4dc01703c69987989b83a48d23b1119eba1ef1453d59850fc304916 |
| a00c2162 event sub | ctx+334 | ctx+314 | a00c6788 / a00c2148 | ev_23b0ebaa7eb99216dc55fee2bae1a78df430f63d4a6bf4d7d2e5575e8cbfb7cb |
| a00c2452 event unsub | ctx+35c | ctx+33c | a00c6994 / a00c2438 | ev_64e2320c9090aa5a2752dcf26591052825d7913ac7b0d0458e233b965b70d383 |

上述四份真根 profile digest 同为 `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。安装 result/error 的旧根地址分别 12a2/12ac、1550/155a、22c4/22ce、25b0/25ba（均 a00c 前缀），写 ctx+6c/+70；stage 调用点 131a/15c8/235c/2628。根内缺/空 iid array 可本地接受仅作为继承前提，不推出后台效果。输入 serializer a00c10f6/a00c16a0 与 clear a01afb26/a01afae6 停在 API。

v3 tokenizer a0191d52 继承补充卡 EID `ev_a81349569cb931f335ad69d594b206a00853f48a9fbdb7b851eeea61695106cf`：原地最多64 tokens、quote/object/array span 分隔，非通用 JSON 校验；卡引用见主仓 Q22 app-rpc-action-research-01-0041-20261025.md。不读 tokenizer 或 Q22 shared-error body。

## 两种 staged 对象与所有权

property stage a00bb67e 沿 Q18 已交 API：calloc(1,84)，失败−5，成功0；N+0/+4 为双向 links，memcpy(N+8,R,72)，N+50 为独立32位 status 初值−4004，追加 H 尾部。本包不重读该body，也不借 Q18 的 ctx+228 或 ACK matcher 条件。

event stage 原字 a00c188e..18c4：调用 a0058386(1,0x5c)，失败分支 1898→18d4 返回−5；成功 N+58=0xfffff05c（−4004），N+0/+4 先自链，memcpy(N+8,R,0x38)，随后按旧尾插入 H，返回0。分配92 B、复制56 B；N+40..57 是未被该copy覆盖且由 calloc 置零的区域，本包不赋予业务含义。不能套成 property 的84 B节点/72 B payload。

有效根先清零局部 R，再解析 iid 的三个32位数到 property R+24/+38/+3c 或 event R+24/+28/+2c。根中的“type=3”选择器是 JSON array-index 路径对象；不能据其名称给 staged record 的 type 字段造一次写入。对本包有效根，payload 只需保留数值和已复制的 inline 字节，不持留栈 R/token 指针。memcpy 是字节浅复制；该结论不授权把任意其他入口传入 R 中的指针解释成 owned 深拷贝。

| 字段 | property R / N | event R / N |
|---|---|---|
| 三段 IID | R+24/+38/+3c → N+2c/+40/+44 | R+24/+28/+2c → N+2c/+30/+34 |
| 独立 status | N+50 | N+58 |
| payload / 分配大小 | 72 / 84 B | 56 / 92 B |

H=旧根 stage a0=result 保存的 ctx+对应偏移=matcher a0=serializer a0=clear a0，始终是同一条请求链。DID 使用各自 ctx 独立槽，不以“同一 ctx”把四条链混合。

## ACK 分组与首项状态覆写

四 result ABI 可见 a0=ctx、a1=ACK 可写/适配文本，调用 tokenizer(a1,stack_tokens)。正常回填门均为 signed n>3 且 (n&3)==0；每四 tokens 为 ID0/ID1/ID2/code。每组清零局部 R（property72 B，event56 B），前三项经 strlen a002dcae + a005fcba 数值转换写上述三个32位字段；第四经 strlen+a005fdfa 转 code，再调用族对应 matcher。转换容错、符号/溢出细节留公共 API，不能称严格数字校验。

| result | 分组门不满足的实际本层路径 | 原字分支 |
|---|---|---|
| property sub a00c6368 | 返回−1；不做输出、clear、finalize或reply；原 staged 链仍在 | 639e→6578→6550；63aa→6550（a0已为−1） |
| property unsub a00c657c | 跳过所有ACK回填，继续输出、clear、finalize/reply | 65b6 / 65c0 →6656 |
| event sub a00c6788 | 同上，使用 event 链 | 67c2 / 67cc →6862 |
| event unsub a00c6994 | 同上，使用 event 链 | 69ce / 69d8 →6a6e |

这是限定正常结果路径外的静态分支观察，不进行了异常注入。其余三路跳过回填时会输出节点已有 status（通常−4004），不能等同error wrapper或虚构统一invalid ACK error reply。

property matcher a01adbd4..adc0d：从 *H 起遍历，分别读 N+2c/+40/+44，与 R+24/+38/+3c 作32位相等比较；首个三字段全部相等即 `*(uint32_t*)(N+50)=code` 并返回；未命中走 next，到 H 返回。event matcher a01adb9a..adbd3 **分别**原字证明：N+2c/+30/+34 对 R+24/+28/+2c，首命中写 N+58=code。关键读/写原字地址 property dbe2/dbe6、dbec/dbf0、dbf6/dbfa、dc00；event dba8/dbac、dbb2/dbb6、dbbc/dbc0、dbc6（均 a01a 前缀）。

两 matcher 都没有 type==3 分支，没有 DID 文本比较，没有 −4004 状态门。它们与 Q18 a01adc0e 不同：重复 ACK 三元组可再次覆写同一首节点，重复 staged 三元组中后继节点不因此命中；未匹配节点保留初值/已有值。无 done 位，也未将 ACK token/string 指针保存在 N。matcher 返回不作为命中/成功信号；四 result 忽略其 a0。

## 输出与归还顺序

两 serializer 按链顺序逐节点输出 object，**始终输出三段 iid**，不按 type 切换普通 siid/piid 或其他分支。property 用 N+2c/+40/+44、code N+50；event 用 N+2c/+30/+34、code N+58。以 `%lu.%lu.%lu` 在32 B栈缓冲格式化，随后 bounded length(32)作为字符串 iid 写入，code 走32位数值成员API。没有输出 value/raw payload，没有修改节点字段，没有删除/free节点。格式/长度超限行为停在 formatter API，不许假定任意32位三元组都能完整容纳在32 B。两族字符串 member 调用位置 2072/207e 与212a/2136；分别读 2044..2048 和20fc..2100。

四条 result 输出形状为（静态 builder 调用支持，非执行报文）：

```json
{"id":0,"result":{"did":"DID","sub_result":[{"iid":"ID0.ID1.ID2","code":-4004}]}}
```

unsub 使用 `unsub_result`。示例 id=0/DID/IID 均为占位；实际 id 读取 ctx+3c，code读取节点状态。字面量原件地址 id a01c3280、result a06124b8、did a060f238、sub_result a0565bd0、unsub_result a0565bdc、iid a0564dbc、code a056bd3c；extract.py 同步保留其原串。

正常四路共同顺序：

1. 取 ctx+74 输出缓冲和 `min(unsigned ctx+78,0x558)` 容量，栈 builder 的第三字段清0，调用 a01a4e04 初始化。
2. 开顶层对象、写 id，开 result 对象，写对应 DID（最多32 B有界长度），开 sub_result/unsub_result 数组，调用本族 serializer。
3. 关闭数组、result对象、顶层对象，**先清本族 H，再调用 finalize a00602e6(builder,0,0)**。property clear 点6506/6716→a01afb26；event clear点6922/6b2e→a01afae6。对应 finalize点6512/6722/692e/6b3a。clear内部free保证沿既有API，不读其body。
4. finalize非0直接返回−1，链也已委托清理；不会调用reply。finalize为0则清零栈descriptor的+4起36 B，设+0=ctx+3c、+1c=bounded_strlen(buffer,capacity)、+20=ctx+74，然后调用 `(*(ctx+64))(&descriptor,*(ctx+68))`，直接返回该间接调用的返回值。

serializer借用栈buffer、N和builder；ACK token仅同步转换成数值，本包没有响应 value 指针跨调用借用。reply descriptor为40 B栈对象，输出buffer借用ctx+74；需要异步保留者必须自己满足复制/接管合同，本层未证明。没有reply判空；不做ctx+64/+68/+6c/+70清零，不清DID槽，不归还ctx本身/共享输出缓冲，也未修改请求state/deadline。只归还本地栈帧和通过clear API归还链，完整ctx寿命留上层。

四error均是26 B：计算本条H，调同族clear，强制返回−1。真实调用点049e/04b8→a01afb26、2154/2444→a01afae6；不序列化error JSON，不finalize，不调ctx+64，不清callback槽。不得套Q22共享error helper。

## 交付检查与断边

已核：ROM长度/整体SHA、13窗2784 B/完整指令步进/逐窗SHA/VA映射，0 UNDECODED；八处分组门跳转绝对目标，四root记录身份/profile与安装对应，八个成员/格式原串；逐一对照两matcher的三字段/32位store、两serializer字段读取、clear在finalize前、reply返回值与未清槽。解析/解码只是静态检查，作者未冒充独立技术验收。

已恢复有效请求的四条 staged→ACK状态→输出→清链→reply接口及两族差异。未闭/排除：真正后台订阅施加及ACK来源、权限失败/异常实验、并发取消、完整ctx生命周期、云送达/传输、generic clear内部free保证、通用JSON/数字转换/formatter内部。property sub早退保链的后续归还责任没有在这13窗中闭合；只保留该分支事实，不扩读上层。返回0仅可解释为上层reply返回0，不能认证订阅生效。四根输入serializer只继承API，不因此声称其内部行为已验。

可提交产物：本报告与同stem analysis/extract.py。原字、父根完整profile及便于审阅的解码导出为ignored中间产物，清单与SHA见交付消息；由父窗停止后转存。分支本地精确路径commit，不推送；不改管理表。

时间：第一工具UTC起点 2026-10-24 17:49:30；技术结束/提交结束/停止见末尾记录。实际墙钟包含读文件、工具和写报告；独立排队/中断未观察到，工具等待未单独计量，token不可得不估造。预估11–16分是派发预测，非最低工作时限；提前闭合即交。

技术结束：2026-10-24 17:54:30 UTC；自首工具起300秒（5分00秒）。提交/停止时间随后以本轮session.json和交付消息单列；不把其算作技术结束。
