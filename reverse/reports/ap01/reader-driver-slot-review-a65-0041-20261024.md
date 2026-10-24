# A65：J08/6 已注册D的盘符、配置与四槽写端独立复核

2026-10-24；认领 **J08/6**，非作者 `/root/a56`，作者A64 `/root/g23` 已停止；固定基线 `bd457a6`，独占 `re0041-a65` / `codex/re-0041-a65`。主仓[唯一认领表](rolling-management-0041-20261023.md#链条认领表)已登记A65。沿最新[流程](reverse-design.md)、[保留规则](../../analysis/README.md)与REA技能的留存优先规则，只核必要基址连续性与写端。

**限定接受A64，语义纠正0、新增功能0。** 所选正常门及callee保存s2约定成立时，e5da把旧s2高位更新为G=0x62fc957c；e77a形成 **B=G+0x180=0x62fc96fc=D−0x50**。B不是D。通过有效地址核算，真实byte/word写端对应同一个已注册D=0x62fc974c：首byte0x2f，D+4为4096，D+0x0c/+0x10/+0x14/+0x1c分别为0xa00ef468/0xa00ef502/0xa00ef55e/0xa00ef632。

本复核不读任何target/helper body，不重验注册/选择/清零，不重导整个initializer或借未留存探索补连续性。未运行collect.py或旧技术脚本、目标/固件/指令/模型、SIM/QEMU、构建、回放、异常输入、设备或外部服务；不切换共享REA、不改生产ROM配置模型/共享表，无下级agent、提交推送。新JSON按本地原相对analysis路径忽略保留。

## 继承结论

|已验来源|继承范围与本题边界|
|---|---|
|[A62](reader-driver-register-gap-a62-0041-20261024.md)/[A63](reader-driver-register-review-a63-0041-20261024.md)，J08/5|正常insert-head输入list=0x62fc9740；N非零后N.word0=D=0x62fc974c。先发布N再填D的原序/正常s1保存条件保留；不重验helper、注册或并发生命周期|
|[A56](reader-driver-selection-a56-0041-20261024.md)/[A57](reader-driver-selection-review-a57-0041-20261024.md)，J08/1|reader按N.word0取D，以D首byte比较source首byte，按真实槽接口使用。只继承读端，不重读144B或认实际source一定匹配|
|[A47/A49接口](photo-reader-mode-a47-0041-20261024.md)、[A50/A52读写](photo-reader-consumer-a50-0041-20261024.md)|open/close/read/seek的真实参数域和D+4配置消费已验；这里仅把实际写入值接到这些槽，不认证目标函数声明/行为、H类型或IO成功|
|A21/A22、A25/A26|G清零及正常caller、旧s2高位/相关片段已有合同。只读其必要s2定义/覆盖位置，不重验clear/PNG/像素主体|
|[A60/A61](reader-driver-global-init-review-a61-0041-20261024.md)|两槽初始化和正常门局部关系已验。此处只用**实际保存的**e4c4及e506..e52a原字段；不把A60未保留的探索字节当连续性证据|
|[A64作者报告](reader-driver-slot-bind-a64-0041-20261024.md)|基址更新、缺口校准和具体slot绑定差集；其67项作者检查不代替非作者核验，本次另写字段/覆盖检查器|

原件身份沿[CATALOG](../../../roms/CATALOG.md)：0041 `ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，VA映射`file_offset=VA−0x9ffff000`。仅核长度、引用摘要，不重算哈希。旧片段沿原profile/Evidence来源，本次新字段没有生成REA生产ID/profile。

## 本轮复核或纠正

### 正常s2定义链与真实边界

所选新连续段逐条Capstone5.0.7 RV32/RVC完整解码，结合必要旧已发布行，只检查s2定义/控制边；独立I-format/C.BNEZ核关键更新与目标。没有把同一global区域中的s1/s2或B/D混作同值。

|范围/锚点|独立检查与条件|
|---|---|
|旧A25 e3c4至e4b8|已有普通s2定义只有 `0xa008e3c4: LUI s2,0x62fc9`。引用这个高位来源，不重读旧ROM/清零算法，不先猜s2已经是G|
|新[e4b8,e4bc)4B、旧A21[e4bc,e4c4)|补足真实短缺口；所选普通指令没有新s2定义。外部call正常保持callee-saved s2是前提，不展开body|
|旧实际e4c4、旧实际[e506,e52a)|由保存的压缩门字节独立解e4c4非零→e506；连续已发布普通行覆盖e506..52a且无s2定义。没有使用A60当时未留存的另一个48B探索窗|
|新[e52a,e536)、[e536,e598)|按真实边界完整解码；s2无新显式定义；e596原字21e1解为a0非零→e5d6。只接受该正常门，不补零诊断块或把线性后续当正常到达|
|新[e5d6,e612)|只有e5da的ADDI s2,s2,0x57c定义s2，独立字段rd=rs1=18、imm0x57c；接高位得G。独立确认e5f4是4B指令、e5f6不是起点；未从半条指令拼伪RVC/NOP|
|旧A21[e612,e628)、新[e628,e6ea)、旧A21[e6ea,e768)|必要覆盖齐全、所选普通指令无另一s2定义；控制/外部调用只摘要留存，跨call继续以正常callee保存s2为条件，不认证其副作用、异常或诊断返回|
|旧A62 e768/e76c、slot段e770..e7b2|继承e76c的正常call/保存约定，不读其body；slot段完整解码无s2定义。e770先把a5作字符常量，**e77a之后**a5才固定为B，之后所读slot段无新a5定义|

这些是**所选正常控制流的显式定义连续性**与ABI条件，不是全异常路径/动态CFG/所有caller的证明。若前置服务不返回、callee不遵守保存约定、异步/别名改变实际global，不能据本合同保证运行到达四槽或永久保持其值。

### 盘符/配置/目标的有效地址

U/I地址构造、SB的byte宽度、C.LUI数值、C.SW的word宽度/寄存器/位移独立拆位。下表是事实性的写端与同D地址换算：

|写端|地址构造与实际存储|接受结果|
|---|---|---|
|e770/e776|a5=0x2f；SB到s2+0x1d0=0x62fc974c|D首byte=0x2f（`/`），不是word store或实际盘符使用观察|
|e774/e77e|C.LUI a4,1的word值为0x1000；C.SW到B+0x54=0x62fc9750|D+4=4096，不是1，也不证明缓存已分配/实际IO长度|
|e780/e784/e788|LUI/ADDI a4=0xa00ef468；word写B+0x5c=0x62fc9758|D+0x0c绑定该open target地址|
|e78a/e78e/e792|构造0xa00ef502；word写B+0x60=0x62fc975c|D+0x10绑定该close target地址|
|e794/e798/e79c|构造0xa00ef55e；word写B+0x64=0x62fc9760|D+0x14绑定该read target地址|
|e7a8/e7ac/e7b0|构造0xa00ef632；word写B+0x6c=0x62fc9768|D+0x1c绑定该seek target地址|

**语义纠正0。** A64已正确保留B=D−0x50而非B=D，四槽指针与config的原始写入在独立字段中一致。旧A62的s2未知是当时输入局限，不据此重写历史；本轮接受的是A64补证后的条件身份桥。

局部表达（非原源码，不省略正常门/ABI条件）：

```c
G = 0x62fc9000 + 0x57c;  // e5da后s2
D = 0x62fc974c;          // 继承A62/A63注册端
B = G + 0x180;          // e77a；B == D - 0x50
byte(G + 0x1d0) = 0x2f;
word(B + 0x54) = 4096;
word(B + 0x5c) = 0xa00ef468;
word(B + 0x60) = 0xa00ef502;
word(B + 0x64) = 0xa00ef55e;
word(B + 0x6c) = 0xa00ef632;
```

## 真正新增

新增业务/语义纠正/ISA/来源认证/整库排除均0。新增为对A64同差集的非作者字段与覆盖证据及限定接受；不把独立重读连续性窗口计为新driver功能，不验收任何callback target body或完整initializer。

## 未闭精确边与实际检查

仍未知实际source与此D的匹配、letter唯一/字段后续writer与并发可见性、真实文件操作、底层H/IO返回、注册执行机会、D/节点注销与寿命、完整SDK/LVGL来源版本。default五ROM照片mode0保持；不能因D首byte为`/`或target来自POSIX路径owner就认证其实际使用或未改库。optional ready/其他slot未借本项认证。

有种子后继只沿已知target与真实调用端接口登记具体正常语义，例如 **D+0x14→0xa00ef55e，(D,H,dst,want,&got)**；先查已有成果/当前认领，不能在本复核沿target展开或重开全部FS。open/close目标另题研究状态由管理窗口维护，本项不把地址绑定接受当body接受。

[review.py](../../analysis/reader-driver-slot-review-a65-0041-20261024/review.py) 实际 **58项PASS**：必要新连续性窗口368B、slot控制段66B，共434B；配套只保存控制/定义摘要和 **19个稀疏原字段**，不复制完整listing。旧A21/A25/A60/A62仅必要原路径/已发布记录引用，没有运行作者collect.py或旧验证脚本，不把A60探索描述当输入。

本地忽略 [review-evidence.json](../../analysis/reader-driver-slot-review-a65-0041-20261024/review-evidence.json) 保留工具版本、VA/文件偏移、关键字段、正常门/ABI局限、有效地址及来源。JSON、相对链接、Git忽略和diff检查通过；未打开目标body、共享REA或新模型。交付后停止本项，供管理窗口整合/补位，无提交推送。
