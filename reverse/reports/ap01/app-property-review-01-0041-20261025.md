# Q-15：typed 属性阶段非作者复核（0041）

结论：**可独立使用阶段已闭合但接口未闭，限定接受作者交付**。在有效 count 与借用字符串仍有效的前提下，collector→延后 consumer→send API 的静态合同成立。行为纠正0，新增业务0；count 初始化/复位、共享存储并发及队列后续持有均未闭。

复核者 `app_property_review_01`，未参与作者取证。启动基线 `3d0d89d9d951aec94c5d5920e7002fbd039f2fb8`，分支 `codex/app-property-review-01-20261025`；被复核作者提交 `bfed293a5b32c7d0538e41786a2ece71eeccfe82`。只写本报告及同 stem analysis；主树流程3.1/3.2/5.1/7、rolling顶部与Q15派发前提只读继承。使用 reverse-engineer-anything 的留存证据及观察/推论/未知区分规则，不启动或切换REA，不执行作者脚本。

## 继承结论与证据边界

被复核报告：[作者合同](app-property-research-01-0041-20261025.md)。caller/deferred/Q11前提继承不重验；formatter/copy/队列止API，不认证库版本或云端接收。

原件主树 `roms/0041/ap01-1.0.2_0041.bin`，本轮检查长度6,769,704 B；SHA256身份沿派发 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不新算全ROM。VA映射 file_offset=VA−`0x9ffff000`。独立读取三body 1,294 B和四wrapper130 B，核作者留存原字一致；16个必要NUL字符串逐字节一致。

旧REA来源均在主树 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{编号}.json` 的 `/structuredContent/normalized_result`，Ghidra12.1.4、`RISCV:LE:32:ap01thead2`。三个body profile digest均 `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。

|记录|范围/长度|Evidence ID|
|---|---|---|
|144|a0195034..a01950e3 /176 B|ev_89e3ae9d1a09935389925ac12a464c788cae672e9b1631dccf95d099355d501f|
|159|a01b5d70..a01b606b /764 B|ev_d130f16f50acaa43d7f20c98370e94baef9d75355aea1e27d2af68d7ebee7db2|
|021|a00a116e..a00a12cf /354 B|ev_e56e7bf85b43acfb10c1c6065be0dd6f8d6ff82cbb1c1c92f3665a396e97610e|
|024|仅真实consumer(0)两处上下文|ev_c1e4264fde90a17127f8044f76f1c829bac816668b38d62f57229fdc852b638c|

普通RV32/RVC指令用宿主Capstone逐指令解码并人工对照关键参数、位宽和分支。两条厂商指令明确保留：a0195090=`0b55de41`，留存 `th.srw a0,t3,t4,0`；a01b5f6e=`8b96fb42`，留存 `th.mvnez a3,s7,a5`。宿主decoder不支持它们，语义沿已绑定private profile，未替换NOP、未执行模型，也不声称独立认证整个指令模型。

## 本轮复核结果

|验收项|独立静态判断与关键位置|
|---|---|
|六参、槽与门|a0..a5依次id0/id1/type/value_ptr/extent/flag；a019503e signed count<=19进入，故count>=20拒绝而负值无下界。a0195082左移5，槽stride **0x20=32 B**；a01950cc仅递增count。|
|位宽与复制|S+0/+4写word；S+8=`sh zero`，consumer a01b5e8e=`lh`；S+0xa存type byte但collector用完整a2比较。1/2复制byte，3复制half，4复制word，其它分支存指针word；S+0x18 extent word，S+0x1c flag byte。|
|四wrapper|a01950e4/5106/5122/5144长度34/28/34/34 B；唯一JAL均到a0195034，type分别1/0/4/2。数值使用栈临时并在collector返回前复制；string只存指针。flag由caller传入，低byte控制，不是固定1。|
|mode与循环|初次signed count<=0返回；mode0起始`result`，任意非零起始`properties_changed`。a01b5dd8每轮重读count，i==20停止；不承诺固定snapshot批次。|
|真实consumer(0)|024中a00a29fe置a0=0，a00a2a00 AUIPC+0x113000、a00a2a04 JALR+0x370；a00a2cd4置a0=0，a00a2cd6 AUIPC+0x113000、a00a2cda JALR+0x9a。两对目标均a01b5d70。|
|输出类型|mode0前缀` %u %u %d`，状态signed16；非零mode为` %u %u`。type0的extent只作非零门；type1 bool文本，2/3/4 unsigned，6/7/8 signed；5/9读S+0x10/+0x14，用`%llu/%lld`，但collector和本轮wrapper未闭合其构造链，不能外推。|
|长度与推进|每槽先检查signed `513-strlen(B)>0`；prefix_len>=余量早退。value_len>=重新计算的余量仅跳过value并继续下槽。flag=0也推进。a01b5df2和5e00最终unsigned strlen<=512才send；513/512只是数值门，不证明B分配容量。|
|发送API|message非空、handle!=-1后，以栈buffer、size0x101、`%s%c`与CR13格式化。a00a1228 unsigned返回<=256才继续；a00a1254重读handle传queue；queue仅返回-1判失败，其它值最终0，无全长返回检查。consumer忽略send返回。|
|资源与所有权|string在collector不深拷贝，须有效到consumer格式化结束。send同步读取B并将自己的栈buffer交队列；队列是否复制/何时完成未知。数值栈copy、string借用和send栈buffer三者不能混同。三body无free或clear-count写端，不能外推全ROM无复位。|

上述为静态观察/受既有profile约束的解释，不是目标运行结果。消息确为命令文本，无JSON容器。send的255字符可连CR通过、256字符被拒绝，只在常规snprintf返回语义前提下成立；接受作者将它列为API替代推论，不认证原formatter内部。

## 真正新增与纠正

业务新增0，行为纠正0。证据定位补强一项：作者脚本按文本搜索直接目标，因此其024 assembly片段未收录两对AUIPC/JALR，只有正确伪码上下文；本轮直接从024 assembly计算出上述两个真实调用点，支持原报告consumer(0)结论，不要求重跑作者脚本。

独立复验源码：[verify.py](../../analysis/app-property-review-01-0041-20261025/verify.py)，结果：[independent-evidence.json.tmp](../../analysis/app-property-review-01-0041-20261025/independent-evidence.json.tmp)。脚本仅提取、解码和比对；语义表为人工对原字/留存控制流的复核，脚本PASS不替代语义判断。没有执行固件、模型、SIM/QEMU、回放、构建、设备或网络；没有全ROM搜索。

## 未闭精确边与交付

count初始化/复位writer及owner、其它status writer、共享B真实容量/并发/跨调用寿命、string在延后期间是否有效、queue栈buffer复制及完成/取消/错误归还、云端接收仍未知。本轮不追a00a12d0截断、不搜count-reset、不跨全局owner。后继只能先由管理窗口为已有a0199064队列API边界或count真实writer准备新种子并查重；本复核不展开。

报告/复验源码精确路径本地提交，不推送；ignored `independent-evidence.json.tmp` 留父窗按原相对路径转存。提交前脚本运行、JSON解析、diff --check及忽略规则检查；最终commit/工作树状态另见交付消息。

计时：首个显式时钟UTC 2026-10-24 17:14:11，早于此已有两次材料读取，不能冒充完整任务起点；检查完成时间与此区间差值由交付消息补充。派发预测3–5分钟，材料<1/typed1/consumer-send1–2/交付1；没有主动等待或中断，工具时间含于墙钟。token与有效工时不可得，不造数。
