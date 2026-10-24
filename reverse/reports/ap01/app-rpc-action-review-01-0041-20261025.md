# Q22 普通 action / action_v3 非作者复核（S-P32）

结论：限定接受作者 `9f9220cab18fa8982e23a224b5877de15df73602` 的五窗静态阶段，行为纠正0、新增业务字节0。接受的是 ACK→序列化/错误→本层返回的合同；完整 action 接口仍未闭合。复核者未参与作者工作，未执行作者脚本。

独占分支 `codex/app-rpc-action-review-01-20261025`，启动基线 `9100a552b6862e9a3f884182b9da4f45eeac68ee`。任务依据 S-P32 及主树 reverse-design §3.1/3.2/5.1/7、rolling-management 顶部与Q22补位行。主树有其他协作者未提交修改，未接触或回退。材料优先取主树同路径；复核树只写本报告及同 stem analysis。

## 原件和独立检查

原件主树 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−0x9ffff000。复核自写[verify_independent.py](../../analysis/app-rpc-action-review-01-0041-20261025/verify_independent.py)直接读取原件，不import/执行作者 verify_windows.py。

五窗为 `a00bec0c+676`、`a00c5b8c+664`、`a00bd924+20`、`a00c0b5a+20`、`a00bd7fa+278`，总1658 B。逐窗offset/SHA与作者contract一致；cached原窗逐字节一致；作者494条反汇编原字全部对原件核对。独立Capstone 5.0.7/RV32+C逐窗解码完整覆盖，只在 `a00c5d74` 留4 B未知。另核14项NUL字符串（含`%lu.%lu.%lu`），未进入formatter/JSON内部。

主树 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json` 的 `/records/297`、`/records/54`，实际record/profile/EID与parent-links完全匹配，安装处摘录逐行存在。profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`；EID分别 `ev_ecf6e8c1592c11cde466318e02e74ee337b4493e2c4cff9d3f3fe3a4aecdda71`、`ev_24a567d316d2266ca0c3faa04db22e09e5ea377b4dc6d3a88fbdb09be4bc6d16`。不把该旧profile/EID赋给新增回调证据。安装ctx+6c/+70的地址算术分别还原为本轮两result/error。根调用writer为ctx+0x14，旧+20文字是十进制；本轮reply为ctx+0x64，两者独立。

必要tokenizer前提只读 `upper-miio-b.md` 的a00b7878/a0191d52补充卡：前者非空透传a0..a3至a00b7776、空返回0（`ev_a257a7cd32815c2f931657625dc044b0b3a01ba811a1932e29999fc6702b803d`）；后者原地最多64 token，quote/object/array span与截停均非通用JSON验证（`ev_a81349569cb931f335ad69d594b206a00853f48a9fbdb7b851eeea61695106cf`）。不重认证其内部或异常输入。

## 验收与返回层次

| 检查 | 独立核对结果/地址 |
|---|---|
| result ABI/长度门 | 两版a0=ctx/a1=ACK。v1 a00bec4a..56为n>2且奇数；v3 a00c5bc6..c8为n>3，无奇偶门。 |
| ID | v1两个token经strlen/转换比较ctx+258/+25c（a00becd0..dc）；v3三个比较+254/+258/+25c（a00c5c6c..80）。均未读版本字节+250。转换止API，不推严格数字校验。 |
| code/out | v1 token2、v3 token3交同一状态转换。a00bedae..b4/a00c5d4c..52先跳过非零状态，再跳过最小token数。故n=3/4时无out；状态非0可成功reply但无out。 |
| out形状 | v1从token3/4逐piid/value成对raw写，每次+2，普通lw；v3从token4逐value对象，每次+1。形状来自调用/字符串，不代表实际报文或JSON类型验证。 |
| 版本区别 | v1 did/siid/aiid，后两项取ACK原文；v3 did/iid，iid取ctx三ID格式化至32 B栈区；did最多32 B。 |
| custom | a00c5d74字节0b463b45，word453b460b，opcode0b/funct3=4/hi22/rd=a2/base=s6/index=s3。由s6=token表及s3从4递增、随后strlen/raw写入支持索引装载解释；未认证新ISA，v3逐value解释保留此条件。 |
| error wrapper | a00bd92c/a00c0b62均直调a00bd7fa，a0/a1/a2未改，helper返回值透传。 |
| shared error | buffer=ctx+74，容量min(unsigned ctx+78,558)。a00bd864..878以unsigned(status+10000)<=5000保留[-10000,-5000]，否则-10000。message NULL或空串省略。 |
| descriptor/reply | 三处40 B栈descriptor，+4起36 B清零，+0=request id(ctx+3c)，+1c=bounded length，+20=ctx+74；ctx+64(&descriptor,ctx+68)，返回原值。没有判空reply。 |

必须区分两层finalize失败：共享error自身finalize失败（a00bd8c6..ce）返回-1、不调用reply；result finalize失败（a00bee4e..52 / a00c5dc2..c6）转invalid ACK，调用error(ctx,-9998,"user ack invalid")后强制-1，可能由error helper发起error reply。token/ID失败同一路径。因此不能把result -1说成未发送，也不能据-1重复发送。成功result返回reply回调值，同样不代表设备action成功。

## 所有权、覆盖和断边

ACK/token只在本调用中借用并同步消费，本层无指针存ctx、无malloc/free；ctx+74输出缓冲借用。descriptor/临时iid/token表在栈上，只保证reply调用期间有效，reply若异步持有须自行复制/接管，但当前未证明。五窗未清ctx+64/+68/+6c/+70、+230/+250/+254..25c或state/deadline，没有property staged-list可套用。归还仅本层栈帧；旧cmd.result及root状态生命周期继续继承。

本轮覆盖五窗全部可见控制流；新业务覆盖0。完整接口断边仍为：数字/tokenizer/JSON/raw/formatter API内部、唯一custom精确语义、ctx+64真实目标的复制/传输与持有合同、writer激活/上游state/deadline、真实action/权限/取消/并发。后继只能按真实callback目标/调用方持有或旧cmd.result状态卡接续。未运行固件、作者脚本、模型、SIM/QEMU、回放、构建、设备或外网；未改ROM、生产配置、分析器或共享REA。

独立机器核对与反汇编为ignored `independent-check.json`、`independent-disassembly.txt`，留独占树供父窗同相对路径转存；精确文件SHA/长度由交付时列出。源码可提交，未强行加入ignored产物。

时间记录：技术起点UTC 2026-10-24 17:45:40（首工具clock）；技术检查结束、提交与停止另行分列。预测4–6分；提前闭合即交付。无异常排队/中断事件；正常文件/工具墙钟不冒充有效工时，token遥测不可得，不造数。

技术/必要检查结束：UTC 2026-10-24 17:47:48；技术墙钟128秒（2分08秒），早于4–6分预测闭合。提交/停止不计入该数。
