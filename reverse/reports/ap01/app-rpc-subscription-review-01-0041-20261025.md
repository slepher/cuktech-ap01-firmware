# Q26 非作者复核：property/event RPC订阅结果本地生命周期

限定接受作者 `9dc5fd4af492bd1ef180a5833cd83b05d56e51cd` 的四条 staged→ACK状态回填→结果输出→清链→reply 合同。语义纠正0，新增业务0；复核新增原字0（独立重读13窗2784 B）。这只关闭本包待复核状态，不能称真实订阅生效或完整接口闭合。

认领 Q26；非作者 `/root/app_rpc_subscription_review_01`。独占树 `D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/rpc-subscription-review01`，分支 `codex/app-rpc-subscription-review-01-20261025`，启动基线 `7e4f4dca88af733319500704ddfeb2046ec2006b`。已读主仓 reverse-design §3.1/3.2/5.1/7、rolling-management-0041-20261023 顶部/Q26补位行，以及预调研 S-P38:435/444。只改本报告及同stem analysis，不回退其他协作者。

## 证据与方法

原件 `roms/0041/ap01-1.0.2_0041.bin`，独立读取6,769,704 B，重算 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射 offset=VA−0x9ffff000。地址/偏移以下为十六进制，B大小为十进制。

独立 verifier 直接从该ROM连续解码各限定窗口，使用 Capstone 5.0.7 RV32+C；随后与作者 static-windows.json 比较原字、逐窗SHA、指令地址/字节/助记符。未调用作者 extract.py，未运行作者模型。结果13/13窗、2784 B完整解码、8/8无效分组目标通过。自行编写 verifier 的初次运行遇到证据回退路径和 bnez 别名识别遗漏，均仅影响复核脚本，修正后通过，不构成作者结论纠正。

| 独立重读范围（含首尾） | B | 用途 |
|---|---:|---|
| a00c6368..657b / a00c657c..6787 | 532 / 524 | property sub/unsub result |
| a00c6788..6993 / a00c6994..6b9f | 524 / 524 | event sub/unsub result |
| a00c0492..04ab / a00c04ac..04c5 | 26 / 26 | property error |
| a00c2148..2161 / a00c2438..2451 | 26 / 26 | event error |
| a00c1fd8..208f / a00c2090..2147 | 184 / 184 | 两serializer |
| a01adbd4..adc0d / a01adb9a..adbd3 | 58 / 58 | 两matcher |
| a00c187c..18d7 | 92 | event stage |

复核源码 [verify.py](../../analysis/app-rpc-subscription-review-01-0041-20261025/verify.py)。机器记录 [independent-windows.json](../../analysis/app-rpc-subscription-review-01-0041-20261025/independent-windows.json) 和 [独立解码](../../analysis/app-rpc-subscription-review-01-0041-20261025/independent-disassembly.txt) 为ignored转存产物。原始机器记录保留VA及原字，不新造 REA EID。

作者报告 [app-rpc-subscription-research-01-0041-20261025.md](app-rpc-subscription-research-01-0041-20261025.md) 以及同stem extract.py/static-windows.json/session.json、四root摘录只读。交付期间主树尚未包含作者ignored时从作者树读；verifier优先主树，缺失才取作者树。

四root沿 upper-complete.evidence.json records280/56/50/135，profile digest `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`；读取 inherited-roots.json 的四个完整记录身份及摘录，未遍历其他metadata。EID按序为 `ev_db33625e03f3e24175d2c317d0ae631e60913589eb0092b638ac297783c535d4`、`ev_258c7b21e4dc01703c69987989b83a48d23b1119eba1ef1453d59850fc304916`、`ev_23b0ebaa7eb99216dc55fee2bae1a78df430f63d4a6bf4d7d2e5575e8cbfb7cb`、`ev_64e2320c9090aa5a2752dcf26591052825d7913ac7b0d0458e233b965b70d383`。不将 upper-miio-b 另一profile EID互换。

## 接受项与具体依据

四head保持对象身份独立：root a00c1144/a00c13f2/a00c2162/a00c2452 分别使用 ctx+2e4/+30c/+334/+35c；各DID为 +2c4/+2ec/+314/+33c。根的stage参数H、result中的s5、matcher首参、serializer首参和clear首参对应同head；ctx+6c/+70安装分别是6368/0492、657c/04ac、6788/2148、6994/2438。四根有效解析/成功保链/失败清链只继承既有接口，不重验完整root字节。

property stage a00bb67e 沿已验Q18 API：节点84 B、R复制72 B到N+8、N+50独立32位初值−4004。event stage在188e/1892给calloc(1,0x5c)，1898失败到18d4返回−5；189a/189c构造fffff05c，18a2写N+58，18a4/18a6自链，18a8..18b0复制56 B到N+8，18b4..18c2尾插，成功0。两族不能互套节点大小/布局。有效根局部R清零及只解析三数的既有合同支持同步字节复制，不由此宣称任意R指针深拷贝。

property matcher dbe2/dbe6、dbec/dbf0、dbf6/dbfa比较 N+2c/+40/+44 与 R+24/+38/+3c，dc00以32位store写N+50。event matcher dba8/dbac、dbb2/dbb6、dbbc/dbc0独立比较 N+2c/+30/+34 与R+24/+28/+2c，dbc6以32位store写N+58。三个不等分支均去next，首相等写后直接返回，无type、DID、−4004门。因此重复ACK可覆写首个同键节点；同键后继不会因此轮命中，无命中则状态不改。没有将普通property的a01adc0e条件搬来。

四result均调用tokenizer a0191d52，signed n>3 且 n%4==0才进入四token分组。前三项经strlen/数值转换后32位写入对应R字段，第四项转换code，调用对应matcher，忽略matcher返回。转换/解析公共API内部沿既有合同，不认证严格数字校验。

| result | 分组门失败目标 | 本层效果 |
|---|---|---|
| property sub 6368 | 639e→6578→6550；63aa→6550 | −1直接退出，保链，无输出/clear/finalize/reply |
| property unsub 657c | 65b6/65c0→6656 | 略过回填，继续输出及清链 |
| event sub 6788 | 67c2/67cc→6862 | 略过回填，继续输出及清链 |
| event unsub 6994 | 69ce/69d8→6a6e | 略过回填，继续输出及清链 |

两serializer沿链输出iid字符串与32位code；property在2044/2046/2048读取三IID，2076读取+50；event在20fc/20fe/2100读取三IID，212e读取+58。32 B栈格式缓冲，格式%lu.%lu.%lu，bounded长度32。无type切换、value输出或节点写入/free；formatter返回/截断保持API未知。serializer栈字符串、builder、节点均为借用。

四正常输出均为id→result对象→did→sub_result或unsub_result数组→本族serializer，输出buffer来自ctx+74，容量为min(unsigned ctx+78,0x558)。关闭数组与两层对象后，6506/6716/6922/6b2e分别调本族clear，再于6512/6722/692e/6b3a调finalize(builder,0,0)。finalize非零时已clear且返回−1；零时构造40 B栈descriptor（+4起清36 B，+0=id、+1c=buffer有界长度、+20=ctx+74），调用ctx+64并原样返回a0。64/+68 callback和cookie、6c/+70 result/error槽不清；DID/ctx/输出buffer不归还。reply需自行满足复制/接管要求，本层只证明同步借用。

四26 B error仅计算相应head、调clear、返回−1：049e/04b8→a01afb26，2154/2444→a01afae6；没有error JSON/finalize/reply或槽清零，不套Q22 shared-error helper。

## 停止边界与交付

generic clear/free保证、tokenizer、JSON、数字转换与formatter均停API；四输入serializer只继承。未执行固件/SIM/QEMU/回放/构建/设备/外网，未修改ROM/生产配置/分析器或共享REA，未派下级。

保留未知：property-sub无效分组早退后的上层归还责任、完整ctx寿命、并发取消、真实后台订阅施加与ACK来源、权限失败/异常实验、传输/云送达。reply返回0只代表该间接回调返回0，不证明订阅生效。以上unknown不因本包限定接受而消失。

首工具UTC 2026-10-24 17:59:05；技术核验终点18:00:47（102秒），文档和提交另列session/final。技术终点后仅写交付材料与必要格式/提交检查。预估5–8分来自派发类比，实际提前交付；工具等待未单独计量、未观察到排队/中断，token不可得不造。
