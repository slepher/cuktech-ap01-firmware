# Q-30 / S48 串行 downstream 非作者复核（0041）

状态：**可独立使用阶段已闭合但接口未闭**。四窗有限阶段接受；行为纠正0，新增业务body 0。复核者 app_serial_downstream_review_01，未参与作者工作。作者commit `138119aece4883d73f0af4c1f9045f3fa5b198d5`；复核分支 `codex/app-serial-downstream-review-01-20261025`，实际基线 `5a5b732235c5b0d1654c8bc543b92c9cc5331e0b`。预测3–5分钟；实测技术、提交、停止分列于末尾与交付消息，不等同有效计算工时。

## 继承结论与证据身份

原件主仓 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−0x9ffff000。独立Python仅读原件并以Capstone 5.0.7 RV32+C解码，不执行作者脚本、目标或模型。复核窗口及逐窗摘要见[contract.json](../../analysis/app-serial-downstream-review-01-0041-20261025/contract.json)，复验源码见[verify_windows.py](../../analysis/app-serial-downstream-review-01-0041-20261025/verify_windows.py)。作者报告/原字从父窗提供的 `D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/serial-downstream01/` 同相对路径只读取得；未运行其中脚本。

旧根与result消费者仅读主仓 `evidence/rea-0041-20261017/evidence/upper-miio-a.md` §0xa00ba5be / §0xa00ba690、`upper-miio-b.md` §0xa00bdf9c / §0xa00be238 接口卡，不重读body。原EID分别为 `ev_a2fe6528d46d540d57269d307304ea1818014153926601d33c4dacbe49b6f08f`、`ev_96e86ef902fbb22924f74283bc8b4dec2f3996f006a4c10d869866010973fdeb`、`ev_1c9229862d23cdb4fcce7bd1ed003c575b74855b850d7da27b7b75b02af053be`、`ev_3f3593bae8df35a073c849005980f32b2b56e3da82559eaf7c9a3274bd48f260`。继承get_down非0 handled即返回、仅0进入既有network/MQ；json_get_down仅0写none；writer为ctx+0x14(ctx+4,text)。旧result以state+30、tick+34、timeout+38及callback+6c/+70消费，elapsed严格大于timeout；callback==0才本层成功，callback后state2抑制generic ok，再清state。json_ack只是同消费端别名。共享error只继承Q22报告的40 B descriptor/reply与归还合同，不重新研究其body。

## 本轮复核或纠正

四窗 `0xa00bdb74` 1064 B、`0xa00ba712` 174 B、`0xa00ba4b4` 130 B、`0xa00ba7c0` 242 B，共1610 B / 530指令；独立从ROM取字，逐窗offset/SHA/hex与作者留存完全一致，连续解码剩余0字节。另核19个直接字符串及13×20 B分发表的全部words与method字面量。原字与独立解码留存于同stem analysis的 ignored `independent-disassembly.txt`。这些检查证明本范围字节一致与可解码，不认证完整ISA或目标行为。

|核点|独立原字/控制流依据与结论|
|---|---|
|缓存输出优先|db8e读byte +1fc。2从+200/+204借数据，3追加5字节error；两者writer后dbec清+1fc并return1。其他非0只写mode none、return1，保持该值；不free缓存。|
|state/timeout|dc7c先读state；dc8a为unsigned timeout>=elapsed继续，故严格elapsed>timeout才可空error(-9999)、清state并写error/return1。期限内非2写error且保持state；state2 mode1写error，mode0依+1f8/+1f9/+1fa输出update_fw各变体。|
|SDK门与借用|dcdc清ctx+38起0x34 B；+5c=+74、+58=+78；SDK调用首先base+968，非0才base+174。任一路0仍须+48==0才解析，其他路径转+88；+88==0 return0，否则装6000ms/state2等待槽。不能将API非0当有效pending。|
|mode0解析与分派|parse成功取得method/type3和params/type0，字符串params退1加2；de2e cleanup在后续handler之前，切片来自P=ctx+5c。method/params指针和method长度为门，params长度不是非0门。13表项按strlen+memcmp匹配，entry+8为空转等待，未匹配默认a00ba7c0。|
|mode1与handled|df5a令method两实参0，P/N直接传a00ba4b4；df48调用后非0转等待，只有0才df50写state1，最后return1。输出writer先于poll写state1。handled只代表本层输出/等待，不是MCU执行成功。|
|mode1槽安装|a502 finalize非0返回−1，不写槽或writer；成功a50a..51e安装result a00bda7c/error a00bd910，随后writer并返回0。|
|mode0默认适配|追加method，解析params；失败直接finalize，成功若root为array且有符号长度>2只追加去括号内容，长度<=2不追加，非array或无root追加原params；成功parse路径cleanup。a872 finalize成功才装result a00bd938/error a00bd7fa，writer后返回0，失败−1。|
|MQ fallback|a73c首4 B清0，另memset 0x13c组成0x140 B栈消息；fd=−1直接失败。read后a7a4只比较−1；其他返回包含0/短读都格式化down %s并return0，formatter返回不判。仅get_down旧根消费，不装state/ACK槽。|

消息所有权接受作者的限定：D=ctx+38、输入P/N及reply/context=ctx+64/+68保留于ctx，本层无消息release、无free(P)，不清reply/result/error槽；token cleanup不等于释放P。栈builder仅本次API调用可见，writer拿ctx+28；不能从函数名推API复制或异步持有。MQ消息只在栈上，预清零不能证明满长非NUL读安全；不做异常输入验证。

旧共享error使用ctx+74及有界容量，40 B descriptor的+0=id、+1c=len、+20=buffer，以ctx+64(&descriptor,ctx+68)调用；dequeue D+2c/+30正是同ctx+64/+68，因此此处是对象字段接合。继承合同只能说明同步调用边界，不保证reply深copy/传输。

## 真正新增

新增业务结论及新body均0；新增的是本认领非作者独立字节核对、分支/安装点核对与有限阶段验收。作者所述语义接受，无需作者补修。没有把四个ACK目标body纳入本题，也没有把旧通用result卡当成新callback内容。

## 未闭精确边与停止

mode1 a00bda7c/a00bd910、mode0 result a00bd938，以及等待state2 a00ba9f6/a00ba994的内部行为未读；mode0共享error只继承Q22。SDK dequeue是否copy/失败填充/释放、reply是否复制或真实接收、+88生产者、完整ctx销毁/并发、clock wrap、真实MCU执行继续未知。一个有种子的后续是单独登记a00bd938与a00bda7c的ACK→reply连接，先查重后派，不据此自动开读。formatter/parser/MQ/SDK内部止API。

全程独立静态，只写独占report/analysis；未执行固件、模型、SIM/QEMU、回放、构建、设备或外网，未改ROM、生产配置、分析器或共享REA；未派下级。技术开始UTC 2026-10-24 18:27:35，技术结束UTC 2026-10-24 18:29:53，技术/必要检查墙钟138秒；提交/停止时钟见交付；正常工具耗时计入墙钟，无主动等待/中断，token遥测不可得。报告提交后停止，ignored留存由父窗核对转存。
