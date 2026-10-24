# Q-29 / S44 v3 property结果与raw消费非作者复核

## 结论与范围

**限定接受作者最终提交 `47653c4018021e18b3942d9d922baf3a1531a6c6`（含 `f9ef0f47` 前件）；语义纠正0、新增业务原窗0。** 五窗1074 B的可解码控制流、同H接合、raw清槽时点、归还与reply ABI一致。get五个厂商word继续未知，不能将候选token load提升为已认证ISA；仅本地阶段合同获得接受，不标完整接口闭合。

复核者 `/root/app_rpc_property_review_02` 非作者，认领Q-29成熟后备S44；分支 `codex/app-rpc-property-review-02-20261025`，基线 `5f50102e56012e2e1e0fa8f9d8010d3c8e8214fd`。先读主仓reverse-design §3.1/3.2/5.1/7、rolling顶部与Q-29精确补位行，以及预调研S-P44初包/ready动态。父窗已建树，未另add；只写本报告与同stem analysis，不回退其他协作者。

作者尚未合并到本树基线，材料只读自 `D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/rpc-property02` 的 `reverse/reports/ap01/app-rpc-property-research-02-0041-20261025.md`，及同stem analysis的metadata.json、windows.json、windows.txt与verify_windows.py。只读作者源码，没有执行作者脚本。后续合并转存后应优先主树同路径材料。

原件主仓 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，本轮独立重算SHA256为 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；offset=VA−`0x9ffff000`。独立读ROM后与作者五窗逐字节、offset、length、SHA256比对，再用本地Capstone5.0.7静态解码；没有执行目标、模型、SIM、QEMU、回放、构建、设备或外网，不修改ROM、生产配置、分析器或共享REA，不派下级。

## 证据与继承边界

主仓 `reverse/analysis/whole-rom-coverage-0041-20261023-round1.json` `/functions` 的精确address项只作extent/directcall定位，独立核extent边界：get `0xa00beeb0..0xa00bf083` 468 B、set `0xa00c59d4..0xa00c5b8b` 440 B、error `0xa00bb0f6..0xa00bb10f`及`0xa00c0478..0xa00c0491`各26 B、request serializer `0xa00bb80e..0xa00bb87f` 114 B，总1074 B。本轮ROM复读不是REA EID；不将metadata当body。

v3两根继承作者引用的主仓upper-miio-b §0xa00c04c6 / §0xa00c07cc，EID `ev_80a2dc60a59bad76a166cdbcb8c8b28b62e8b7c503b55cc858a83c2257d5331e` / `ev_7ddfcaa6358f1207bc34e7ad785509a50da2179e4b02d2fe8cc2a30f47bc7b7b`，同H=ctx+228、三元IID/type3、72 B local record。主仓Q18非作者报告 `app-rpc-property-review-01-0041-20261025.md` 的stage/matcher/response serializer完整1382 B合同直接继承，没有重新读取其原窗：N+8浅copy，N+50初值−4004，matcher比较N+40/+44及type3的N+2c，不比较DID，仅首个仍为−4004的匹配项可回填。写回−4004仍可再匹配。不得套Q26四head和无默认门matcher。

## 逐阶段核对

| 原字锚点 | 接受的合同和限定 |
|---|---|
| request `0xa00bb842..85e` | type=3才先输出N+2c，再无条件输出N+40/+44；writer由a1保存。遍历同H，未删节点。 |
| `0xa00bb862..874` | ptr=N+4c、len=N+48均非0才调用0xa00b5636；**调用返回后**先清ptr再清len，不检查API返回，不free raw。任一为0则跳过且不清。可确认正常request raw不留到后续ACK默认输出，但API复制保证仍未知。 |
| set `0xa00c5a0c..1e`、`0xa00c5afc..b8a` | count非零且count&3=0才循环，signed比较仍是实际循环门。每组清72 B local，标准lw读取三IID与status，IID写L+24/+38/+3c，L+20=3，a2=status交同H matcher；不回填value，不检查matcher返回。空/不整组直接转正常result输出。 |
| get `0xa00beef0..faa` | count≤3转输出；每组先清72 B。可解码的index/count比较证明三IID/status分组及不足转输出，status非0不读value而推进四项，status=0必须还有第五项才进入value路径并匹配。local字段/length/类型写入与matcher ABI一致；五处token取得word未知，故整个token-load语义仅保留候选解释。 |
| get `0xa00befae..f00e`、set `0xa00c5a22..84` | ctx+74输出buffer，容量min(unsigned ctx+78,0x558)；object id取ctx+3c，result array调用既有serializer。空/残缺/未匹配ACK仍输出余留默认节点，不统一转error。 |
| get `0xa00bf014..28`、set `0xa00c5a8a..9e` | result输出完成后clear H，然后finalize(writer,0,0)。finalize非0返回−1，此时链已清；不是reply成功后才清链。 |
| get `0xa00bf02a..56`、set `0xa00c5aa0..d2` | 栈D+0=id，D+4清0x24 B，D+1c=有界长度、D+20=buffer；a0=&D，a1=load(ctx+68)，间接调用load(ctx+64)，返回值原样返回。a1不是ctx+68地址；不能借用旧普通callback描述替代本窗ABI。 |
| 两26 B error | 加0x228得到H，调用clear，返回−1；不输出、不finalize、不reply。四callback本体均无清ctx+6c/+70写，clear H不等于callback槽清零。 |

get五未知word精确保留：`0xa00bef08:0bca2a45`、`0xa00bef26:0bcafa44`、`0xa00bef44:0bcafa44`、`0xa00bef62:8bcb4a45`、`0xa00bef84:0bc54a45`（little-endian bytes）。opcode0x0b/funct3=4/hi=0x22可按编码读取，周边及set标准lw仅支持候选indexed token-pointer load，未认证语义、未改ISA或跑模型。

## 断边与检查

Q18旧request raw跨ACK残留断边被本轮同一serializer收窄：正常ptr/len由同步raw API返回后清零。这个事实不证明格式API已deep copy，不证明请求buffer可立即释放；公共formatter/tokenizer/JSON止API。get value借用至少到同步response raw调用，API内部持有和reply下游对栈descriptor/buffer的持有仍未知。完整ctx、并发取消/超时、callback外部槽管理、真实设备属性应用与权限不闭合。返回0不能作为设备应用成功证据。

独立 [review_windows.py](../../analysis/app-rpc-property-review-02-0041-20261025/review_windows.py) 实跑PASS：原件大小/整ROM SHA、五窗1074 B逐字节及各窗SHA、完整指令宽度、五unknown原字、七关键指令锚点与主仓metadata精确extent。人工逐指令核对上表门、字段、调用顺序、归还与ABI；机器锚点不冒充完整语义证明。作者脚本未运行，无构建/设备/回放检查。

ignored待父窗转存：`reverse/analysis/app-rpc-property-review-02-0041-20261025/review-results.json`。只提交本报告及复核源码，不推送；不修改主仓管理表。完整UTC技术/提交/停止分列回传，token不可得，不估造。首工具UTC **2026-10-24 18:21:42**；技术结束时点在完成正文及末次检查后补记。

技术正文/独立静态检查结束UTC **2026-10-24 18:23:32**，首工具起110秒（1分50秒），含正常读取/工具时间，不称有效计算工时。无异常等待/中断；PowerShell启动的InitializeDefaultDrives提示不影响退出码与产物。派发预测3–5分，仅为估计；五窗材料已定位、标准指令可直接核对、旧1382 B不重做，故提前交付，不补凑窗口。提交和停止另列，token用量不可得。
