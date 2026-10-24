# Q22 普通 action / action_v3：异步 ACK 到 reply 与本层归还

作者静态阶段完成，待非作者复核；完整 action 接口仍有断边。技术起点 UTC 2026-10-24 17:35:12。分支 `codex/app-rpc-action-research-01-20261025`，基线 `a4979f031d0799f97913c9496213394ab02abb58`。独占本报告与同 stem analysis，不修改主树、ROM、模型、生产代码或共享 REA 会话。

## 证据与继承

原件 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，文件偏移 `VA-0x9ffff000`。本轮新增静态原字证据为五个精确窗口：`a00bec0c..a00beeaf` 676 B、`a00c5b8c..a00c5e23` 664 B、`a00bd924..a00bd937` 20 B、`a00c0b5a..a00c0b6d` 20 B、`a00bd7fa..a00bd90f` 278 B，共1658 B。Capstone 5.0.7/RV32+C离线解码；一条厂商指令保留原字，未运行私有模型或目标。

继承 `evidence/rea-0041-20261017/evidence/upper-miio-a.md` §a00bb110 的 `ev_6bde5d9aff5af2968564572019754faaba3c3c75e5f78ebb490d47b2fdc0e97b` 与 `upper-miio-b.md` §a00c0b96 的 `ev_e88416f40cb09d4f766cc0b49a71bfce06f52bcca97488565cae5c8171f8aef2`，不重做请求/parser/context。

另一 profile 的真 root 是 `upper-complete.evidence.json /records/297` 的 `ev_ecf6e8c1592c11cde466318e02e74ee337b4493e2c4cff9d3f3fe3a4aecdda71`，以及 `/records/54` 的 `ev_24a567d316d2266ca0c3faa04db22e09e5ea377b4dc6d3a88fbdb09be4bc6d16`；profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。只核安装点：v1 `a00bb450..462` 把 result/error 写 ctx+6c/+70；v3 `a00c0ea4..eb6` 同样安装本轮两个目标。原 root 的 serial writer 实际是 ctx+0x14，`+20` 旧文字为十进制；不与回复 ctx+0x64 混用。新回调字节不冒用旧 EID。必要安装原字摘录见 ignored `parent-links.json`。

继承 tokenizer 补充卡：v1 `a00b7878`（`ev_a257a7cd32815c2f931657625dc044b0b3a01ba811a1932e29999fc6702b803d`）是非空转 `a00b7776`、空返回0的包装；不深化其定界合同。v3 `a0191d52`（`ev_a81349569cb931f335ad69d594b206a00853f48a9fbdb7b851eeea61695106cf`）原地最多64 token、quote/object/array span分隔，非通用JSON校验。`cmd.result a00ba5be` 及root alias的state/deadline清理继承，不将其移到本回调。

## 回调合同

所有偏移下文均为十六进制。result入口只使用 `a0=ctx,a1=ACK文本`；token指针数组位于本层栈。返回不是应用动作成功标志。

| 阶段 | 普通 action `a00bec0c` | action_v3 `a00c5b8c` |
| --- | --- | --- |
| token门 | 调`a00b7878(ACK,stack_tokens,64,0)`；必须n>2且奇数，失败走invalid ACK | 调`a0191d52(ACK,stack_tokens)`；必须n>3，失败走invalid ACK；无奇偶限制 |
| 匹配ID | token0/1经`a005fcba(ptr,strlen)`转换，比较ctx+258/+25c；不访问+254/+250 | token0/1/2同转换，比较ctx+254/+258/+25c；不读+250版本字节 |
| 结果对象 | `id=ctx+3c,result:{did,siid,aiid,code,...}`；did为ctx+230最多32字节；siid/aiid用ACK token0/1原文写入 | `id=ctx+3c,result:{did,iid,code,...}`；did同左；iid用ctx中三个32位ID按`%lu.%lu.%lu`格式化至32字节栈区后写为字符串 |
| status | token2交`a0053f46`，得到32位code；无额外本地范围/词法检查 | token3同左 |
| out门与形状 | 仅code==0且n>3写`out:[{piid:raw(t3),value:raw(t4)},...]`；每次索引+2 | 仅code==0且n>4写`out:[{value:raw(t4)},...]`；每次索引+1，最多60输出token |
| 失败与返回 | token/ID/finalize失败调用共享error(ctx,-9998,"user ack invalid")，随后强制返回-1；成功返回reply间接调用的返回值 | 同左 |

分支锚点：v1门`a00bec4a..56`，ID比较`a00becd0..dc`，code/out门`a00bed92..b4`，out循环`a00bedd6..bee2a`，finalize/回复`a00bee46..82`；v3门`a00c5bc6..c8`，ID比较`a00c5c6c..80`，code/out门`a00c5d30..52`，out循环`a00c5d6c..9e`，finalize/回复`a00c5dba..df6`。ID转换的精确容错/截断是API边界；本轮不能声称严格数字校验。普通piid也是raw写入，没有单独数值转换；输出value不做JSON类型检查，字符串、数组、对象的接受度受继承tokenizer及raw-builder API限制。上述JSON形状是调用顺序/成员名/既有builder API角色支持的静态合同，不是执行产生的报文，更不保证非法raw被校验或转义。

普通版n=3、v3 n=4时即使code为0也省略out；非0 code即使跟随输出token也不写out，不对其作额外验证。状态非0仍可成功生成/交付reply；回调返回0也不能解释为action执行成功。

v3 `a00c5d74` 原字字节`0b463b45`（word `0x453b460b`），字段opcode0x0b、funct3=4、hi=0x22、rd=a2、base=s6、index=s3。结合s6=stack_tokens、s3从4递增与紧随strlen/raw value写入，支持`token[s3]`索引装载解释；Capstone不解码此字，未执行模型，保留为推断而非本轮已独立认证的自定义指令语义。普通版输出循环全为标准lw。

## error、reply与归还

两个20 B error wrapper分别在 `a00bd92c` / `a00c0b62` 直接调用 `a00bd7fa`，不修改a0/a1/a2，返回其返回值。共享helper ABI是(ctx,32位status,可空NUL终止message)。无action版本分支。

共享helper先用ctx+74 buffer及`min(unsigned ctx+78,0x558)`容量初始化栈builder，写顶层`id=ctx+3c,error:{code,...}`。`a00bd864..878` 以无符号`status+10000 <=5000`保留[-10000,-5000]，其余归一到-10000。message为空或strlen==0省略，否则作为字符串成员message写入。关闭对象后调用`a00602e6(builder,0,0)`；非0返回-1且不调reply，成功调用reply并直接返回其值。invalid ACK的-9998在保留范围内；result忽略此helper的返回值，强制-1。因此result返回-1也可能已发起error reply，不能据此重复发送另一错误。

三个builder最终交付路径一致：40 B栈descriptor先将+4起36 B清零，然后设+0=`ctx+3c`、+1c=`bounded_strlen(buffer,capacity)`、+20=`ctx+74`，调用`(*(ctx+64))(&descriptor,*(ctx+68))`。对应v1 `a00bee56..82`、v3 `a00c5dca..df6`、共享error `a00bd8d0..8fc`。没有判空reply；不推断本层具备防空保护。descriptor和字符串中间栈区仅在调用期间有效；reply若要异步持有，必须由其自身复制/接管，当前未证明。

ACK原串由tokenizer/转换/strlen以及raw写入同步消费；token只借用该串，本层不保存其指针到ctx，也不释放ACK。输出缓冲借用ctx+74，无本地malloc/free。request/parser原生命周期继承，action在本层没有Q18 property staged-list；本轮五窗不归还任何链、不清ctx+64/+68/+6c/+70、不清+230/+250/+254..25c、不清state/deadline，也不释放ctx共享缓冲。返回时只归还本层栈帧/临时builder/token表/descriptor；是否下一请求覆盖由上层合同决定。

## 验证、交付与停止边界

已核ROM整体SHA/长度、五窗1658 B长度/offset/逐窗SHA、字节覆盖、唯一未解码原字、精确父record/profile和安装地址、成员名字面量。字符串原件地址：id a01c3280、result a06124b8、did a060f238、siid a0564d04、aiid a0564d28、piid a0564d4c、iid a0564dbc、code a056bd3c、out a0259268、value a0569390、error a06189f0、message a0618098、invalid ACK a05652b8。复验源码与可提交合同见[verify_windows.py](../../analysis/app-rpc-action-research-01-0041-20261025/verify_windows.py)、[contract.json](../../analysis/app-rpc-action-research-01-0041-20261025/contract.json)。ignored原字/解码/父定位不入commit，待主窗同相对路径核SHA转存。

本轮未执行固件、模型、SIM/QEMU、回放、构建、设备或外网，未改变共享REA状态。静态阶段覆盖ACK门、ID/状态/out形状、error归一、回复ABI和本层归还；未认证厂商自定义索引指令、数字/JSON/formatter内部语义、reply复制/传输、激活writer、实际action/权限异常/并发取消。后继只能从ctx+64真实目标/调用方持有合同或既有cmd.result状态卡接续，不能把本阶段写成完整action或实际执行闭合。

时间分列：技术/必要检查 UTC 2026-10-24 17:35:12→17:39:31，259秒（4分19秒）；提交/交付与停止时间由最终交付消息另报，不混入技术时长。预测8–13分，本轮提前闭合静态阶段；保留一条厂商指令和API边界，没有为补时扩挖库。墙钟包括正常文件/工具时间，不等于有效计算工时；无排队/异常等待事件可单列，token遥测不可得，不造数。
