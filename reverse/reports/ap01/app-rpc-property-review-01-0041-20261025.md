# Q18 property staged record / callback / 清链非作者复核

## 结论与范围

**限定接受作者交付 `72a10cb66106a1a1a66ba4f62a75c4213fa58dac`；语义纠正0。** 同一 `H=ctx+0x228` 的 stage浅复制、matcher默认状态门、result输出及清链次序、error清链与callback槽保留均得到独立静态核对。四条get vendor指令仍未知，原set raw跨ACK寿命与完整ctx并发/取消未闭；本结论不等于完整接口或ROM恢复。

复核者 `/root/app_rpc_property_review_01` 不是作者；认领Q18，分支 `codex/app-rpc-property-review-01-20261025`，固定基线 `8782ea6916e6879af8c044af60d2e5aa6988fb74`。仅本报告和同stem analysis，未改主树管理表或其他协作者成果。先读主仓 `reverse-design.md` §3.1/3.2/5.1/7、rolling顶部及Q18补位行；作者未整合时按派发绝对路径读报告与四份analysis，只阅读作者脚本，未执行它。

原件沿CATALOG身份：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；offset=VA−`0x9ffff000`。本轮不重算整ROM摘要。复读七窗共1382 B，无新增业务窗口：stage92、get430、set404、error26+26、serializer308、matcher96。使用本地Capstone静态解码与原字比对，不执行固件、模型、SIM、QEMU、回放、构建、设备或外网；不切共享REA，不修改ROM、生产配置或分析器，不派下级。

## 证据分层与接合

父级 `evidence/rea-0041-20261017/evidence/upper-miio-a.md` 的root EID `ev_ccf8947ba0ace57f9a4011dc3f0596e163b52e67c237c5a2e8e0ab7161b3f7a0` / `ev_356b7dc60bc5a619a8c2c7af6a983114de52ca84bdf70843a8c5379ef8af65ce` 直接继承，不重做root/list/JSON。

独立读取主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json` 的 `/records/59` 与 `/records/164` 必要assembly接合；EID分别 `ev_29f77800b52f12cedb687a2038119b3cf1012aabd3390128a8e525a327669e0a` / `ev_7de861b43b55102a6679af754b6a5508870ea194da05c0545639ff53ec2960c3`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。与作者 `parent-links.json` 一致，保持独立profile，不重标父级EID。新复读原字不是新REA Evidence ID。

root59在`0xa00bb89e/8a4/8a8`、root164在`0xa00bbb8a/90/94`建立同H及两link。root59的`0xa00bb970..97e`交72 B栈record给stage且清R+40/+44；root164的`0xa00bbcb4..cce`由原请求slice构造R+44与长度R+40，字符串包括引号。各自在释放parse doc后调用既有`0xa00bb80e(H,writer)`；finalize成功才存result/error槽：get=`0xa00be8ca/0xa00bb0c2`，set=`0xa00bea78/0xa00bb0dc`。未读取`0xa00bb80e`本体。

## 独立逐阶段核对

| 阶段/原字锚点 | 接受的合同与限制 |
|---|---|
| `0xa00bb690..6b2` | `(1,84)`分配，失败−5；`memcpy(N+8,R,72)`，N+50独立写−4004，接入H旧尾，成功0。没有复制raw内容或retain；72 B覆盖N+8..4f，不覆盖N+50。 |
| `0xa01adc24..60` | 遍历H，仅type3附加比较N+2c/local+24；始终比较N+40/local+38、N+44/local+3c；没有DID比较。仅首个ID匹配且N+50=−4004的节点写status、ptr、len并返回。status写回−4004仍满足门，无donebit，不能泛称一次性。 |
| get `0xa00be8f6..902`、set `0xa00bea9c..aaa` | 可见callback入口a0=ctx、a1=输入；文本适配`a00b7878(input,token_ptrs,64,0)`。set标准lw三元组循环与局部72 B清零已证；get亦逐组清零，status0才取value的周边控制流已证，但四处load语义保留未知。两者将同H、&local、status交matcher，忽略matcher返回。 |
| `0xa00bb774..808` | serializer输出DID，type3输出格式化iid，普通type输出siid/piid，所有节点输出code。仅ptr与len均非0才raw写value，之后清N+4c/+48；本窗没有free该指针或移除节点。 |
| get `0xa00bea02..20`、set `0xa00beb22..40` | JSON object结束→清H→finalize；finalize非0返回−1，此时链已经清。清链不是等待上层callback成功后才发生。 |
| get `0xa00bea22..4e`、set `0xa00beb42..74` | stack descriptor D：D+0=request id，D+4起清0x24 B，再填D+1c=响应长度、D+20=buffer。a0=&D、a1=ctx+68，间接调用ctx+64；其返回值原样穿过epilogue。四callback无ctx+6c/+70清零写。 |
| `0xa00bb0c2..f5` | 两error仅以ctx+228调用clear后返回−1；不构造JSON，不调用ctx+64。clear内部止于API，不认证free细节。 |

get四原字（VA→little-endian bytes）为`0xa00be922→8bc92a45`、`0xa00be940→8bc9fa44`、`0xa00be95e→8bcb3a45`、`0xa00be980→0bc53a45`。仅编码字段可直接提取：opcode0x0b、funct3=4、hi=0x22；rd=s3/s3/s7/a0、base=s5、index=s2/a5/s3/s3。周边及set对称只能支持候选解释。既有SINC仅在字段可对应时有参考意义，不能认证这四条语义；本轮未运行或修改模型，profile记录中的历史SINC绝对路径在当前环境不可用，未据其存在性作认证。

## 保留的断边与验收限度

1. set原raw只浅复制。跨ACK是否须保活依赖`0xa00bb80e`实际消费合同，本包未读；parse doc释放不能推出deep copy，matcher命中清零也不能证明全部pending raw早已消失。
2. get响应raw借用需至少活到本次同步raw写；JSON API内部复制策略止于公开API合同。不能据本窗声称异步持有安全。
3. 四vendor load未知；tokenizer grammar、64项边界内部与异常输入不展开；clear/list/allocator内部不展开。
4. ctx并发、取消、超时、回调槽外围清理、stack descriptor的下游异步保留均未知。准备成功0或callback返回0不代表实际设备应用成功。

## 检查、产物与时间

独立源码 [review_windows.py](../../analysis/app-rpc-property-review-01-0041-20261025/review_windows.py) 只读ROM与限定留存，实跑PASS：7窗1382 B逐字节/offset/窗SHA一致、每窗指令宽度完整覆盖、17个关键指令锚点、2个root profile/EID接合；恰4个未知word保持未知。未执行作者`verify_windows.py`，其内容已阅读。人工逐指令核对上述分支、顺序、字段和ABI；机器锚点检查不冒充完整语义证明。

作者合并与ignored转存后，优先使用主树同路径材料再次运行独立脚本，仍PASS；没有继续依赖作者树已移除的ignored源副本。ignored待父窗口同路径转存：`reverse/analysis/app-rpc-property-review-01-0041-20261025/review-results.json`。报告与复验源码本地commit，不推送。提交与停止时间由交付消息分列；token用量当前不可得，不估造。首工具UTC起点 **2026-10-24 17:29:23**，技术检查结束 **2026-10-24 17:32:25 UTC**，可观测技术墙钟182秒（3分2秒），无异常等待/中断；实际墙钟不称有效计算工时。预计4–6分只是派发预测，提前完成因材料已定位且无解码等待，不补凑窗口或等待；作者成稿317秒与外层348秒仍按不同口径分列。
