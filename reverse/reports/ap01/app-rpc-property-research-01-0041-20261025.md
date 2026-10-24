# Q18 cmdrpc property staged record → callback → 清链（作者恢复，待独立复核）

## 范围、身份与时间

认领 Q18，作者 `/root/app_rpc_property_research_01`。分支 `codex/app-rpc-property-research-01-20261025`，基线 `841a7a194a9ecdd02935d429c2cdc57e68ae5ab8`。主仓只读流程 reverse-design §3.1/3.2/5.1/7、rolling 顶部与 Q18；独占本报告与同 stem analysis。正常 SDK 输入范围内静态恢复，没有执行固件、模型、SIM、QEMU、回放、构建、设备或外网，没有切换共享 REA。JSON/formatter/list/allocator 停在 API。不同于 Q15 的 UI count B044。

原件沿 `roms/CATALOG.md` / `application-rehost-complete-0041-20261017.md`：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，既有 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；VA→offset = VA−0x9ffff000。本轮未重算整 ROM hash。开始可观测 UTC 2026-10-24 17:17:54；结束见末段。token 用量不可得，不估造；墙钟含正常读取和工具时间，不能称有效计算工时。

## 证据分层

父级 root 合同继承主仓 `evidence/rea-0041-20261017/evidence/upper-miio-a.md` §a00bb880 / §a00bbb6c，分别 `ev_ccf8947ba0ace57f9a4011dc3f0596e163b52e67c237c5a2e8e0ab7161b3f7a0` / `ev_356b7dc60bc5a619a8c2c7af6a983114de52ca84bdf70843a8c5379ef8af65ce`。该报告明确 a00bb67e 深浅复制和 callback 尚未闭合。

另一 profile 的 `upper-complete.evidence.json /records/59`、`/records/164` 分别为真 body `ev_29f77800b52f12cedb687a2038119b3cf1012aabd3390128a8e525a327669e0a` / `ev_7de861b43b55102a6679af754b6a5508870ea194da05c0545639ff53ec2960c3`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。只核局部 record/parse doc 释放/回调槽接合，不把它们重标为前两 EID，不重做 root。`parent-links.json` 保存各自定位与必要 callee extent。

新增原字为本地 shipped-artifact 读取，Capstone 5.0.7 RV32+C 解码，**不是新增 REA Evidence ID**。精确窗 `a00bb67e..bb6d9` 92 B、`a00be8ca..bea77` 430 B、`a00bea78..bec0b` 404 B、`a00bb0c2..bb0db` 26 B、`a00bb0dc..bb0f5` 26 B、`a00bb6da..bb80d` 308 B，共 1286 B。经主窗口登记授权再加 matcher `a01adc0e..adc6d` 96 B，总新增 1382 B。

Matcher 精确 extent 来自既有 `whole-rom-coverage-0041-20261023-round1-verbose.json` address=a01adc0e /extent，EID `ev_046c61762ac9facb3625237f1e9ed11ad4fe99e4fddd09438000f129bf46ce1c`，不能当作其 body 已恢复；本轮另读该 96 B。`windows.json` 留每窗 VA/offset/length/raw hex/SHA256，`windows.txt` 留逐指令；四条 get 自定义指令原字未被 Capstone 解码，详见限制。

## 同一对象的阶段合同

| 阶段 | 可见输入/输出与所有权 |
|---|---|
| root 准备 | `H=ctx+0x228`，ctx+22c 是同一双向表头的另一 link；局部 `R` 大小72 B。get 置 R+40/+44=0；set 的 R+44 指向原请求 JSON slice，R+40 为长度，字符串含引号。DID/siid/piid 是 R 内值，不是 token 指针。 |
| stage a00bb67e | 调用 a0058386(1,84)，失败返回 -5。N+0/+4 links；`memcpy(N+8,R,72)`；N+50 独立初始化 -4004，按 H 的旧尾接到同一链。成功0。仅这一份 record 的浅复制；没有复制 raw 字符串、没有 retain/free raw API。 |
| root 成功/失败 | parser doc 经 a01b38b6 释放后，调用已继承 a00bb80e(H,request_writer)，finalize0 后装 ctx+6c result / +70 error 并发出请求，保留 H。失败调用 a01afb26(H)，返回-1。释放 parser doc 不能证明请求文本已复制。 |
| result 局部解析 | ABI 可见 `a0=ctx,a1=响应文本/适配输入`；a00b7878(a1,token_ptrs,64,0) 得 token 数。set 处理三元组 ID1/ID2/status；get 处理 ID1/ID2/status，status0 时再取一 value。每组局部 record 先清零，再调用 `a01adc0e(H,&local,status)`。 |
| 匹配/更新 | matcher 遍历同 H 的 N；N+40==local+38 且 N+44==local+3c；仅 N+28(type)==3 时额外比 N+2c==local+24。**不比较 DID 文本**。只接受 N+50==-4004 的首个匹配项，写 N+50=status、N+4c=local+44(ptr)、N+48=local+40(len)，随即返回。否则走 next；返回值无业务成功保证，调用者忽略。 |
| result 输出 | ctx+74 buffer，ctx+78 capacity，上限0x558；JSON object 添加 `id=ctx+3c` 与 `result` 数组，a00bb6da(H,writer) 输出同 N。关闭对象后立即 a01afb26(H)，随后 writer finalize。finalize失败返回-1，成功把 stack descriptor 交 ctx+64 回调，a1=ctx+68；自身返回此间接调用的返回值。 |
| error | 两 error 完全同形：a0=ctx，加0x228，调用 a01afb26(H)，返回-1。未序列化 error JSON，未调用 ctx+64。 |

精确身份等式：`stage_a0 = H = result_s6/get或s5/set = matcher_a0 = serializer_a0 = cleanup_a0`；`stage_source = R`，`staged_payload=N+8`；`root R+38/3c = N+40/44 = callback local+38/3c`。匹配者不是重新创建另一个列表；默认 -4004 兼作尚未回填的门。若回填本身仍为 -4004，门仍满足；没有额外 done 位，不能泛称所有 status 都一次性完成。

## serializer 的真实效果与寿命

`a00bb6da` 对 H 逐节点输出数组 object。输出 DID=N+8，长度最多32（有界长度 API）；普通 type 输出 `siid=N+40,piid=N+44`。type3 分支输出 `iid`，由 `%lu.%lu.%lu` 格式化 N+2c/+40/+44。所有节点输出 `code=N+50`。只有 N+4c(pointer) 与 N+48(length) 均非0时才以 raw JSON API a01b6866 写 `value`，随后清 N+4c/+48；它不 free 指针，不删除节点。get 成功值借用响应 token text（长度来自字符串长度 API），必须至少活到这次同步 raw 写；JSON API 是否复制只能按所选 API 合同实现，不从本窗推导内部所有权。

原请求值浅复制已证，**没有证据证明其深拷贝**。matcher 命中时原 set 指针被局部全零 ptr/len 覆盖；没有命中时默认 code=-4004，节点原值可能仍保留，除非 root 的已继承 a00bb80e 接口已同步消费并清零。此次未读 a00bb80e body，不能据 parse doc 释放、get/set callback 局部清零或 clear API 反推所有 pending set raw 已消失。重建实现可在 stage 自行持有 raw 副本，或明确规定外部请求 buffer 寿命；这是替代设计选择，不能宣称原厂采用深拷贝。

result 清链顺序固定：输出数组→关闭 JSON object→清 H→writer finalize→上层 callback。即使 finalize 失败，链也已经清理；没有等待上层接收成功才清链。error 直接清 H。a01afb26 本轮仅按清链 API 调用，不展开 allocator/list internals；确认的是清理入口和时点，不认证 free 细节。四回调中无 ctx+6c/+70 清零写；外围是否清槽、异步取消/并发/超时状态与 ctx 全寿命本轮未读。

## 限制、验收与后继

- get 中四原字 `8bc92a45 / 8bc9fa44 / 8bcb3a45 / 0bc53a45` 均 opcode0x0b、funct3=4、hi=0x22；寄存器字段分别是 rd=s3/s3/s7/a0、base=s5、index=s2/a5/s3/s3。其周边及 set 标准 lw 对称地支持 token-pointer 索引解释，但 Capstone 留 UNDECODED；没有执行私有模型，也不将该解释提升为本轮已验证自定义指令语义。
- a00b7878 只继承适配入口，未追 a00b7776、token grammar、64上限溢出语义；正常缺件分支会输出余留默认状态，set 非0且数目非3倍数时不走 matcher。get 数≤2时不走 matcher。上述不是异常输入安全实验。
- 返回0仅是准备/回调链路的局部结果，不能当成设备应用成功；未追真实云应用、action/v3、SDK权限、全 ctx 并发或设备行为。
- 同 staged 链和 ID 比较、status门、raw浅复制、输出后清链时点、回调槽保留已静态恢复；原输入 raw 是否需跨 ACK 保活取决于继承的 request serializer 消费合同，当前明确留断边，不能标全接口闭合。另需非作者复核四条 custom load 与 callback ABI/上层 descriptor 布局后才能独立接受。

本轮只读必要原字，未运行全项目测试/构建；逐窗长度、原字hash、全窗口字节覆盖、96 B matcher无未解码、git diff检查为实际验证。ignored中间产物 windows.json/windows.txt/parent-links.json 待主窗口按流程转存；可提交复验脚本另列。作者已停止新增范围，交付仍待独立复核。

交付检查观测 UTC 2026-10-24 17:23:11；自首个可得时间戳17:17:54为317秒（5分17秒），此前启动/初读耗时未精确计入，提交耗时另不伪装为有效工时。比派发9–14分钟更快，原因是七窗可直接Capstone静态解码，matcher差集仅96B，无反编译器等待。复验脚本 verify_windows.py 实跑PASS，7窗1382B、四自定义word显式留未知；git diff --check无输出。
