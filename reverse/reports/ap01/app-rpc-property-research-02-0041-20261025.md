# Q-29 / S-P41：v3 property 同链 ACK 与请求 raw 消费（作者，待独立复核）

## 范围与证据

作者 `/root/app_rpc_property_research_02`，分支 `codex/app-rpc-property-research-02-20261025`，基线 `7e4f4dca88af733319500704ddfeb2046ec2006b`。先读主仓 reverse-design §3.1/3.2/5.1/7、rolling 顶部及 `Q-29`（口头 Q29）；派发完整包为预调研报告476行 S-P41。独占本报告与同stem analysis；不是唯一协作者，不回退他人。父窗预建worktree，核HEAD及干净后使用；重复add因分支已存在失败，无更动。

原件 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，沿CATALOG既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；VA→offset=VA−`0x9ffff000`。本轮核大小，不重算整ROM摘要。只静态读取，不执行目标、模型、SIM、QEMU、回放、构建、设备或外网，不修改ROM、生产配置、分析器或共享REA，不派下级。

root继承主仓 `evidence/rea-0041-20261017/evidence/upper-miio-b.md` §`0xa00c04c6`，EID `ev_80a2dc60a59bad76a166cdbcb8c8b28b62e8b7c503b55cc858a83c2257d5331e`；§`0xa00c07cc`，EID `ev_7ddfcaa6358f1207bc34e7ad785509a50da2179e4b02d2fe8cc2a30f47bc7b7b`。两root要求非空array，optional DID/default32，iid三段，type3、72B局部record经stage接同 `H=ctx+0x228`；get raw=0，set raw借用请求JSON，字符串含引号。成功装result/error、保留H；失败clear H。tokenizer `0xa0191d52` 只继承适配API，不展开grammar。

Q18作者 `72a10cb66106a1a1a66ba4f62a75c4213fa58dac`、非作者 `0e2e312b1676fb1d28e87887e6c8c9b2b62beea2` 的主仓 `app-rpc-property-research-01-0041-20261025.md` / `app-rpc-property-review-01-0041-20261025.md` 直接继承：stage `0xa00bb67e` 将72B浅copy至N+8、N+50=-4004；matcher `0xa01adc0e` 比N+40/+44，type3额外比N+2c，不比DID，只首个status=-4004匹配项；response serializer `0xa00bb6da` 输出code及条件raw并清ptr/len；clear `0xa01afb26` 停API。旧1382 B没有重读、重计。不是Q26的四head +2e4/+30c/+334/+35c，也不继承其无默认门matcher。

新原字五窗共1074 B：`0xa00beeb0..0xa00bf083`468、`0xa00c59d4..0xa00c5b8b`440、`0xa00bb0f6..0xa00bb10f`26、`0xa00c0478..0xa00c0491`26、`0xa00bb80e..0xa00bb87f`114。本地Capstone5.0.7 RV32+C逐窗解码，非新增REA EID。主仓 `reverse/analysis/whole-rom-coverage-0041-20261023-round1.json` 的 `/functions` 五地址项仅extent/direct_calls定位，分别extent EID：get `ev_47414e279280eba487649d218075c5417bb3904ae594d262583fcfc9a29bedbb`、set `ev_b1357dffebe9560bb76f3abe3a7f04ae1d0d8c8e4dc7c66c4b8bea71477d281f`、get-error `ev_ba3e0c1ba5994cc46e8e20c071da85aa9cbcd8663f171e1a5c5f82fbcf110fb3`、set-error `ev_50c50e0d8e25b60fdbceb75512abb82e5bf057e4c4dec0c3025f367ef49c0c3e`、request serializer `ev_a13ca6cfd969d83d34179ae2f573e945890780f6be02e2f42734cc52bec4a5b3`。不冒充body证据。

## 同H的阶段合同

| 阶段 | 原字与合同 |
|---|---|
| 请求消费 `0xa00bb80e` | a0=H，a1=writer。遍历N；type3先将N+2c交`0xa00b55a0`，再无条件交N+40/+44。只有N+4c ptr和N+48 len都非0时，`0xa00bb86c`调用`0xa00b5636(writer,ptr,len)`；返回后`0xa00bb870/874`清两字段。不free raw、不删节点、不检查格式API返回；任一为0则跳过且不清。 |
| v3 result入口 | a0=ctx、a1=ACK文本/适配输入；get `0xa00beee6` / set `0xa00c5a04` 调同tokenizer，a1指栈token表。本窗没有像普通Q18那样显式传64/0，不把普通API参数套入v3。get s6/set s5=同H。 |
| set ACK门 | `0xa00c5a0c..1e`：count=0或count&3非0直接转输出；count非零且为4倍数才进循环（循环signed count比较）。正常每四token为IID1/IID2/IID3/status。每组先清72B局部L；前三值写L+24/+38/+3c，status作为a2，L+20=3；`0xa00c5b86`交matcher(H,&L,status)，忽略其返回。没有value回填，ptr/len来自清零L。 |
| get ACK门 | `0xa00beef0`：count≤3直接输出；每组清72B L，三个IID分别写L+24/+38/+3c，再消费status。每次读取后续项前比较index与count，不足直接输出；status非0按四项推进，status=0必须再有第五项value才调用matcher，ptr=L+44、len=L+40，经长度API得到len。L+20=3，`0xa00befa6`交同matcher；不能宣称所有get token load已解码，见未知项。 |
| 匹配回填（继承Q18） | 三IID与type3字段接合为N+2c↔L+24、N+40↔L+38、N+44↔L+3c。同H首个status=-4004项被写status/ptr/len。DID不参与。未匹配项维持默认；写回-4004仍可再次满足门，没有done位。 |
| 输出 | get `0xa00befae..0xa00bf00e`、set `0xa00c5a22..84` 使用ctx+74 buffer，容量min(unsigned ctx+78,0x558)，构建object、id=ctx+3c、result array，调用继承response serializer(H,writer)，结束object。get空/残缺ACK、set空/不整组ACK均继续这一路，输出全部余留默认节点；不是统一早返error。 |
| 清链/finalize/reply | get `0xa00bf014`、set `0xa00c5a8a`先clear H，再`0xa00602e6(writer,0,0)` finalize；失败返回-1，此时已清H。成功构造栈D：D+0=id，D+4起清0x24 B，D+1c=buffer有界长度，D+20=buffer。get `0xa00bf046..56`、set `0xa00c5abe..d2` 以a0=&D、a1=**load(ctx+0x68)**，间接调用load(ctx+0x64)，原样返回该调用结果。a1是槽内容，不是ctx+68地址。 |
| 两error本体 | `0xa00bb0fe/102` 与`0xa00c0480/484` 都把a0加0x228后调用clear，随后返回-1；未输出JSON、未finalize、未reply。两窗独立读取，不因与普通接口同形而推定。 |

四新callback本体都没有清ctx+6c/+70槽的写；不能把clear H说成清callback槽。上层槽管理、ctx并发取消、超时及完整生命周期仍未知。

## raw寿命与未知

请求raw由stage浅copy进N。此次证实只要ptr/len均非0，调用request格式API返回后就清除N两字段，随后root才finalize/装callback/发出请求。因此正常set节点不会把已消费的请求raw悬留到ACK、也不会由未匹配默认响应再次输出该raw。这一结论同样修复Q18共享request serializer的“节点是否保留至ACK”断边；不重认证Q18四vendor字。

但`0xa00b5636`是否copy/借用直到root finalize或传输仍未知，止于公开格式API，不下探；不能据字段清零宣称请求buffer可立即释放或原厂已deep copy。任一ptr/len为0则不调用、不清，不从正常合同推异常安全保证。get响应value仍借用token文本，须至少活至本次response serializer的同步raw调用；API内部复制与reply下游持有都未知。

get五条vendor word保持原字：`0xa00bef08 0bca2a45`、`0xa00bef26 0bcafa44`、`0xa00bef44 0bcafa44`、`0xa00bef62 8bcb4a45`、`0xa00bef84 0bc54a45`。均opcode0x0b、funct3=4、hi=0x22；周边index计算、store及set标准lw支持候选token-pointer indexed load，但Capstone未解码，不把候选提升成已认证指令语义。未执行模型、未修改分析器。

局部返回0或reply返回0都不证明设备属性已施加。真实设备应用、权限、传输、格式API内部所有权、reply异步持有、完整ctx并发取消均停止，库/JSON/list/allocator不展开。阶段恢复可供独立复核；不能标完整接口闭合。

## 检查与交付

同stem [verify_windows.py](../../analysis/app-rpc-property-research-02-0041-20261025/verify_windows.py) 实跑PASS：五窗1074B、ROM大小、精确VA/offset/length/hex/SHA256留存、指令宽度全覆盖、恰五vendor word显式未知，以及必要直接call target存在。它是有界提取/解码复验工具，不是执行固件或完整语义测试；人工逐指令核对门、字段、调用顺序与返回。没有构建/回放/设备测试。新raw证据不是REA EID。

ignored待父窗转存同相对路径：`windows.json`、`windows.txt`、`metadata.json`；报告与复验源码精确路径本地commit，不推送。技术结束/提交/停止UTC分列回传；首工具UTC **2026-10-24 18:05:26**。token用量不可得，不估造。预计5–7分仅预测，提前即交，不凑等待或额外窗口。
