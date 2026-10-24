# Q-32 / S-P47：串行主动请求接受与异步结果准备

作者 app_serial_uplink_research_01；状态：静态研究交付，待非作者复核。基线 `5f50102e56012e2e1e0fa8f9d8010d3c8e8214fd`，分支 `codex/app-serial-uplink-research-01-20261025`。只覆盖三新函数 818 B；不与 Q-30 下行 poll 合并生命周期。

## 已有与方法

首工具 UTC 2026-10-24 18:14:49。预估 4–6 分钟中置信，据已定位 818 B 与 Q25 247秒；提前闭合立即交付。技术/提交/停止时间分列于交付记录；工具没有提供 token 用量，不估算。命令等待属于墙钟，未计为有效计算工时。

原件只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−0x9ffff000。本地 Capstone 按原字长逐条静态解码，未知保留，不改分析器/ISA。无目标执行、模型、SIM、QEMU、回放、构建、设备、网络或共享 REA 状态修改。

旧根继承主树 `evidence/rea-0041-20261017/evidence/upper-miio-b.md`：json_send §a00be264 / `ev_23a9d38ca3701fb5f9aa16709171f4d4f30838bd6c6ad0eb382ea1dedcc14eca`，call §a00be8a0 / `ev_a493a0895eeb379f14ad7198eb6850423737ae07e73cc81ca47cdb1c2490dabe`。前者检查busy0、有效非零id，submit0才busy1/serial ok；后者busy0原a0/a1委托，busy非0输出error。不重读旧body，不补丢失伪码参数语法。

SDK `a0111ff6` 的根合同沿同目录 `miio-recovered.md` RPC段 Evidence `ev_a42727108b8c080cc1e6f348c20a0f735f6a4eb0100a6d68a74ad5f596e5eff7`；D+4→SDK同步payload copy、callback/context浅持有是派发已验 F11/F12/Q24 前提，本题不重读SDK body，不把同步copy扩大成ctx全寿命证明。

JSON公开API沿 `upper-miio-a.md` §a0060cac / `ev_ef671cfe67f99dd21ef27cd00e2cdc899ef9290bb26bcf3eda835733efdad3e6` 及 §a0061d20 / `ev_e2fddcc18b0cb267920386c48c0532eb64af7a17b28b70619d951fba00af4a2d`：parse0成功、path返回借用token，token type3字符串，doc token vector经a01b38b6清理。输入原文与token vector是不同所有权。

新extent来自 `reverse/analysis/whole-rom-coverage-0041-20261023-round1.json` 精确address项，仅定位并未继承业务body：a00be6d8..e89f 456 B（extent ev_6cc8939465be79277b6102d963d06a0c3e4b1d2b78d0d1dd8d2e1079b11c391e），a00ba8b2..a993 226 B（ev_46d9b585dc67cdaa9e35de6bc786c90da614cf6c90a11d81821be6e3ba5f7b91），a00ba536..a5bd 136 B（ev_05e14d97f45fdd7125fa9df5b2e15fc5694d09f54219966175d4c742633861d9）。本次完整原字在同stem analysis/instructions.json，可用 extract.py重提取；JSON每项含VA、offset、hex、asm，jal目标按PC相对计算。

## 新行为：call构造与SDK接受

令 C=入口a0，文本=入口a1；s1=C。a00be712调用tokenizer `a00b7878(text,stack_tokens,64," ,")`。count<=0跳serial error，共同返回void；其语法/非法输入处理止公开API。正count记s5，`a0110984(C[0])`返回32位id记s4。

a00be72e..756清零64 B方法暂存区，formatter `a002d7fc(method,64,"_sync.%s",tokens[0])`；formatter截断/转义止API。scratch取 **C+0x200指针、C+0x204容量**，容量无符号截到min(cap,0x558)。这不是旧log/store的+0x74/+0x78。

builder在stack，scratch与容量装入后调用a01a4e04；a01b3872开始对象，a01b3574写id，a01b69d2以(methodptr,strlen(method))写method，a01b3480开始params。s2=1，与count比较；count==1直接结束数组/对象。否则a00be880处原字 `8b452b45`（word0x452b458b）未由通用Capstone认证：rd=11(a1)、rs1=22(s6 tokens)、rs2=18(s2)、funct3=4、high5=8、shift=2。其后s2++，a1经strlen后以(a1,len)调用raw API a01b67e6，再回比较。符合索引tokens后的raw追加形状，但本报告不将这一个厂商word升级为已认证indexed-load语义，正常多参数精确指针选择留下限定；不补异常/grammar测试。

a00be7d4..7ee关闭数组/对象，`a00602e6(builder,0,&len)`非0跳error；0才初始化52 B栈D。D=a0frame−0x194：D+4=id32；byte D+0x10=0；D+0x20=len32；D+0x24=scratch；D+0x2c=callback；D+0x30=C。a00be82a原字 `b7b70ba0` LUI a5,0xa00bb；a00be82e `9387278b` ADDI a5,a5,−0x74e，精确合成 **a00ba8b2**，a00be83e存D+0x2c，a00be842存C到D+0x30。

`a00be846: a0111ff6(C[0],&D)` 非0跳error；0经a00be84e..85a调用 `C+0x14(C+4,"ok")`。**该新body没有busy=1写入**；不能把json_send旧根的写入套到call。失败也没有本body可见的busy写入、scratch归还或远端撤销。stack D/方法/builder随返回结束，scratch仍属C。成功交接只依赖已验SDK同步copy合同，C浅持有仍待寿命约束。

## 两个异步callback：准备输出与状态2/3

共同ABI形状 `int callback(M,C)`；两者返回a0=0。M只借用，读取M+0x20文本指针、M+0x1c长度；没有读取M其他状态字段、id验证或远端执行成功门。输出writer以C+0x200/204为buffer/cap、长度0，再调用 `a01a5268(writer,"result")`、raw API `a00b5636`、finalize API `a018fd68`。这些是输出文档API，不在本题展开MQ/formatter，也不能把finalize命名为buffer free。

- **json_send a00ba536**：诊断日志后，以原始 `(M+0x20,M+0x1c)`直接raw追加整个响应文本。finalize返回0则写byte C+0x1fc=2，非0写3（a00ba5a6 snez、+2、a00ba5ac sb）；随后返回0。无JSON parse、不提取result、不检查消息状态。没有free M、payload或C scratch。
- **call a00ba8b2**：stack doc的input=M+0x20、length=M+0x1c，其余五word清0，a0060cac解析。parse非0直接写状态3并返回0，没有本层a01b38b6调用；失败分配清理由JSON API合同承担，其失败realloc遗留边界不升级。parse0以path key="result"、expected type0 wildcard、count1查找。NULL则ptr/len=0；有效token取start/end，ptr=input+start、len=end−start。type3字符串时ptr减1、len加2，保留原JSON引号，并未反转义为新字符串。
- call成功parse后 **先a01b38b6释放token vector**（a00ba934..938），然后检查切片ptr和len；任一0直接写3。切片依赖的是M原文，不是已释放token。有效切片才初始化writer、raw追加并finalize；finalize0写2，非0写3（a00ba978..97e）。callback返回是M原文在本层使用的终点；本层没有保存原文指针到C，writer API具体copy/异步持有仍止外部合同。

因此两callback并非相同消费：json_send保全原响应，call选result，字符串保持JSON语法。call解析成功但没有非空result不会输出，状态3；parse失败也状态3。callback返回0只表示其本层固定返回，不能用作云操作成功信号。

## 阶段合同、清理与断边

`busy0前置 → call构造/JSON原文 → SDK同步payloadcopy（C浅持有） → serial ok表示本地接受 → 异步M借用 → [call parse/result切片/token归还 | json_send全raw] → writer finalize → state2/3 → callback返回0`。

**本层不存在busy清0，也不存在两callback直接serial sender调用。** 2/3是输出准备/finalize阶段值；何处消费输出、发往串口并清0属于后继消费者。本题与Q-30共享字段不证明同一次请求周期；不能将busy0、callback0、serial ok任何一个解释成远端动作成功。

本层可证清理：call parse成功时归还token vector；所有正常/错误出口恢复各自stack；没有本层heap buffer取得/释放，scratch仍C持有，M/原文未free。输出文档finalize与数据清理不能混称；没有证明C+0x200缓冲在finalize后立即可覆盖，也没有把caller原文长期借给SDK（同步payloadcopy前提）。

未闭：厂商word对应的多参数精确索引语义；tokenizer/formatter完整grammar；状态2/3后的输出消费及busy0复位；输出API的持有/清理细节；SDK超时/取消/并发保证；串行C与scratch全寿命；真实云权限/动作执行、消息队列内部。没有由本层证据生成新tokenizer/SDK深挖任务，也没有全接口闭合或独立验收声明。

检查：ROM大小/SHA校验；三窗边界字节数456+226+136=818；逐条原字覆盖，未知厂商指令1条保raw；callback常量及D偏移独立核；分支/返回核对。仅报告/同stem analysis，未改ROM、生产配置、模型或共享证据。

技术完成 UTC 2026-10-24 18:17:51，首工具至技术完成182秒；提前于4–6分钟预测完成，未等待凑时。提交与停止由最终交付消息单列，token不可得。工具命令等待包含于墙钟，未有独立有效工时或异常等待测量。
