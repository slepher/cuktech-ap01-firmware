# Q11 非作者复核：packed 配置到普通提交

结论：**接受作者限定的静态接口合同，无行为修正**。闭合范围为属性4/0x0e、4/0x11的完整u32输入，经两个静态槽转换、变化门，到既验普通cmd67提交调用及低8位通知；不包含底座确认、item+0x14响应更新或物理协议生效。本轮新增业务恢复为0，新增独立技术复核。

复核者 `/root/app_protocol_review_01` 未参与作者研究；作者commit `7ab7fd20e8c765db2433abddda2ea606e4ddb53f`。独占分支 `codex/app-protocol-review-01-20261025`，启动基线 `c1b37cac196e8e41b9ae357b730f15872db59b56`。已读主仓当前reverse-design 3.1/3.2/5.1/7及rolling-management顶部/Q11；不写管理表、不派下级。采用reverse-engineer-anything技能的事实/推断/未知分离，仅读静态原件及留存，不启动或切换REA。

## 独立证据与核对

原件主仓 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，6769704B、SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−0x9ffff000。身份由本轮独立脚本复验，不导入或执行作者脚本，也未运行行为模型。

直接读取源 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-008.json`、`006.json` 的 `structuredContent/normalized_result`：真body为0xa009c8a4..0xa009cbdb（824B）、0xa009c662..0xa009c7cd（364B）。Evidence ID分别为 `ev_ed7e71f1bd106ab36710c56dfbcad813bb82ce7c1c69484bfd18f4da5eddf6d7`、`ev_32edb8a17764f474455354c17df1d950e43cd7dbf42deeec64921a33c9ad23d7`；两份profile digest同为 `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。原指令长度与body连续覆盖一致，未把未知边界补为NOP。

caller取主仓 `reverse/analysis/miio-deferred-settings-0041-20261023/retained-functions.json#/functions/1`，EID `ev_17a8de6820bfe771a96a269aef06904915c9fd915bf3dd149e40a78307a6e1e2`；继承提交取 `reverse/rehost/charge-complete-0041.json#/records/22`，EID `ev_d97cb7170ca8cb469dfadc2fa50720df6b6619ef04203b9e0d76a24f9154eaec`。所有相对证据路径以主仓为根。

| 核对点 | 独立观察及接受结论 |
| --- | --- |
| 完整输入/镜像 | caller入口d8fa保存a2到s1；dda6/dde6为SW，地址0x62fcafe8/afec；ddaa/ddea均调用c8a4，按值传完整s1，不按属性筛选端口。 |
| 两槽与映射 | c8e0/e4/ec构造0x62fc91a0，第二槽+4。原字23个EXTU字段逐个解码：输入0..3/8..11到byte0的7..4，未用输入其它位。SB只写槽+0/+4，保留低4位及byte1/2/3。 |
| 变化门/反向mask | c9b2/ca54及cb24/cbc6形成每端口任一映射位变化门；C1先于C2，各至多一次普通wrapper。仅映射byte0位为0时生成mask的3/4/5/7位，上界0xb8，无未知位透传。c9e6/cb58原字0x1c07268b是有符号提取7..0，后接BLT判断符号，等价检查byte0 bit7；不是单比特有符号提取。 |
| refresh | c6a4 getter，c6a8 NULL跳至日志再迭代，不写槽；c6ac读item+0x14，c6b0/b4先比完整byte2，相同即跳过所有反解。四组XOR/NOT、EXTU、索引字节store反解映射位；c784始终在非相同mask路径写完整byte2。s1只在映射开关变化时递增，c7a4转bool，因此仅未映射mask位变化仍可返回false。 |
| 提交接合 | ca14/cb86原AUIPC/JALR落到a01b272c，参数端口0/1及反向mask。继承wrapper仍有getter非NULL、item+14不同、a00a533a非零三门；cmd/len半字0x0267、两字节port/mask栈payload，a01951e2调用后返回。止于此及既验公共API，不认证下一层队列/MCU。 |
| 通知 | ddcc/de0c原ANDI255；两分支共用ddd4到a0195144，属性号分别0x0e/0x11，a3=0。随后dbd2返回0没有submit成功或确认判断。通知含原p低8位，不能代表C2 bits8..11或重组后的完整状态。 |

refresh先于setter且返回值被忽略；setter不写byte2。由这些静态顺序可推得：确认尚未改变item+14时，相同请求可能被本地byte0变化门抑制；这只是允许的缓存行为，未观察运行或认证重试/时序策略。NULL日志带旧临时mask不能当本槽状态。

按值输入、全局镜像和静态两槽不形成输入指针持有。B10/B11的getter仅提供借用item，本次没有保存/free item。wrapper descriptor和2B payload在wrapper栈上，仅在同步提交调用期间借用；后续复制/持有约束继承既验公共submit合同，本次不新增异步寿命保证。没有新alloc/free、超时、取消或关闭对象。协议名只沿用日志便于定位，不是产品规格认证。厂商索引字节指令按留存私有profile解释，未宣称独立认证上游ISA或原库版本。

## 验证、断边与交付

[独立检查源码](../../analysis/app-protocol-review-01-0041-20261025/check.py)通过：原件身份、824/364B连续body、23个无符号/2个有符号提取字段、9个标准SB及偏移、两SW镜像、通知截断、9处直接调用目标。人工逐条检查两完整body的NULL路径、变化计数、反向mask、索引字节写入及必要caller/wrapper接合。脚本只读ROM/JSON、解码原字，不执行目标或模型。初次脚本把符号提取误设为7..7，检查失败后读原字确认为7..0并修正本轮脚本；作者语义无需修改。JSON可解析；交付前执行git diff --check。未构建、联网、设备操作、回放、SIM/QEMU，未修改ROM、生产配置或分析器。

未闭精确边保持：cmd67普通响应到item+0x14更新（种子a00a8582，需先查P17既有覆盖）、底座实际应用/物理协商、持久化及云端格式；本复核不能把本地返回0/通知视为这些阶段闭合。不重做wrapper/MCU，不扩属性4/0x0c等相邻接口。

首个可见UTC采样2026-10-24 16:58:54；该采样前已有规则/材料读取，完整开始时间不可恢复。主体原字检查完成16:59:53；最终交付采样见本地提交前检查。工具同步等待未单独计量，无已知排队或中断；token不可得，不填估值。派发预测3–5分钟，未以名义半小时替代实测。

待父窗转存的唯一ignored文件：`reverse/analysis/app-protocol-review-01-0041-20261025/checked-words.json`，5513B，SHA256 `99a068de2361c22c281477b264fc48c07624aa204fbd31ba05a17e33f3b9b0ca`。只提交本报告及检查源码，不强加入ignored原字清单。交付后停止，由父窗合并、核对转存并清理。
