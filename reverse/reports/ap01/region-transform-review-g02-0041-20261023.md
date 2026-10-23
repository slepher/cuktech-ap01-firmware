# 0041 G02：区域变换完整小闭包独立复核

结论：**限定接受 G01，无语义纠正项**。已独立核 G01 的11核心连续函数，范围为正常非空节点、transform的0x6e..0x72属性和 `a00dca48(obj,area,1)` 两处 caller 合同。右/下加1后不减1、当前节点先于父链、signed包围框、比例及旋转中的低32位截断、callee的a0覆盖和caller忽略均成立。此接受不覆盖所有style属性、外部对象生命周期、最终区域提交/屏幕显示，也不认证源码原名或准确开源版本。

本轮问题已得到有证据答案：对象属性如何经链选择、整数点运算到四word区域并被交集消费。没有以一段短helper替代闭包。来源未认证的style及正弦函数均保留在范围；不修改G01、ROM、生产代码、构建或分析模型。

## 独立方法与证据入口

分支 `codex/re-0041-g02`，固定启动基线 `41046d1774061c2ebb47607ef87f969b63a5758b`。只写本报告及 `reverse/analysis/region-transform-review-g02-0041-20261023/`。已读用户原始粘贴请求、管理共同规则/G02任务书、G01、C22、REA技能/native guide；本树及已检查的worktree祖先未见适用AGENTS.md。其他agent并行，本轮没有改共享索引、主树或他树，不创建下级agent。

[review.py](../../analysis/region-transform-review-g02-0041-20261023/review.py) 是本轮新写的静态提取/字段核查，不导入或执行 G01/C22 的验证器。主仓库ROM只读：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `file_offset = address - 0x9ffff000`。普通指令用 Capstone 5.0.7 解码；自写字段拆分辨认厂商字；直接跳转/调用目标独立拆立即数；厂商语义仅引用既有本地SLEIGH文本。未新开/切换REA目标或共享可写数据库，没有执行模型。

[instructions.txt](../../analysis/region-transform-review-g02-0041-20261023/instructions.txt) 是本轮从ROM重新取得的地址/偏移/字节/解码；[evidence.json](../../analysis/region-transform-review-g02-0041-20261023/evidence.json) 包含14窗口、字段、正弦表、所用模型构造器原文与135项机械核查。历史原始图记录仅用于定位边界，G01的伪代码不作为新证据；本轮与G01重叠的793条指令原字节相同。没有新建哈希清单或复制清单。

| 核心地址，末端不含 | 独立复核的 ABI/范围 |
| --- | --- |
| `a00dca48..a00dcb22` | a0=obj，a1=可写16B area，a2=flags；四点构造与写回 |
| `a00dc9ba..a00dca48` | a0=node，a1=可写8B步长点数组，a2=count，a3=flags；递归 |
| `a00dc862..a00dc9ba` | a0=obj，a1=pts，a2=count，a3=inverse；getter与参数换算 |
| `a0083796..a00837ae` | 角度包装，固定a2=0x70，a1保留caller给的0 |
| `a019dfd0..a019dff0` | 固定selector=0、property=0x6e，signed<=0返回1 |
| `a019dff0..a019e010` | 固定selector=0、property=0x6f，signed<=0返回1 |
| `a00dc658..a00dc862` | a0=obj，a1=selector，a2=property，a0=属性word；仅五ID正常路径 |
| `a00dc070..a00dc19a` | a0=obj，a1=selector，a2=property，a3=out；style选择 |
| `a00dc020..a00dc070` | a0=style，a1=property，a2=out；命中写word并返回1 |
| `a0089e10..a0089ff0` | a0=pts，a1=count，a2=angle，a3/a4=sx/sy，a5=pivot*，a6=scale_first |
| `a0089d76..a0089e10` | a0=由caller符号截取为16位的角度；a0=正弦标量 |

另独立取C21谓词 `a00dbff4..a00dc020`、caller `a00ddb14..a00ddb2a` 与 `a00ddb60..a00ddb84`。仅针对核C22输入/返回合同，没有重做其完整失效门控或交集实现。表中11核心没有未知间接callee；c658空对象诊断的 `a008b51a/a0019672` 明确存在但不展开。函数体解码完整不等于所有属性/所有入口语义验收。

## 逐项裁决与指令依据

| G01主张 | 本轮裁决和可定位指令 |
| --- | --- |
| 四点、右下+1 | **接受**。`ca52/ca56/ca58/ca62`分别读area+0/+8/+4/+12；`ca64=0507`、`ca68=8507`分别加1。`ca5a..ca84`写8个栈word，`ca72`count=4，`ca88`调walk。 |
| flags=1先当前后父链 | **接受**。`c9da`AND2、`c9e2`AND1。正向 `ca24`inverse=0，`ca2e`调node，返回恢复pts/count，`ca3e`才读node+4，`ca42`递归。逆向 `c9ec/c9f6`先父链，`ca06/ca0a`后本节点inverse=1。mode在递归前保存s3。 |
| mode与C21同一位域 | **接受**。`c9d2`LW(aux+0x30)，`c9d6`字节`8bb9a96d`即word `0x6da9b98b`，rd=rs1=x19、extu27:26。C21 `c00c`LHU(aux+0x32)，mask0xc00、比较0x800；小端重叠恰是word27:26==2。谓词不返回命中节点，walk从原起点重新遍历。 |
| getter次序/缺省 | **接受**。`c880/c888/c890`角度→sx→sy；两个getter在 `dfd8/dff8`设0x6e/0x6f，`dfe2/e002`signed>0才保留结果。`c896/c89c`仍保留零改1；`c8a0..c8ac`identity绕过支点读取。`c8b0/c8c4`依次0x71/0x72。 |
| style读取与state选择 | **限定接受五ID路径**。`c6a8`LHU(obj+0x28)，与selector OR后`c6be`调c070；`c0c2/c100`每轮重读word数量，`c0c6/c104`取25:20，数组也逐轮读；`c0ec`前缀bit25分支，`c0ee..c0fa`同索引进入一般扫描；`c122..c14e`核group、state子集及signed best，真命中才更新best。 |
| 两种property容器 | **接受**。`c026`LBU(style+8)，!=255时values为word数组、ID紧跟4*n；`c05e`按byte读ID，`c066/c04a`读word并写out。255时 `c050`读ID、0终止，8B步长；命中读上一项+4并写out。没有allocator。 |
| 本轮默认无继承 | **接受**。`a056a49e..a056a4a2=32 32 32 00 00`，五ID的metadata bit0皆0；selector从0与u16合成，group高位0。`c6dc..c6e6→c75c..c76a→c6f6`走缺省；`c80a..c83a`给0x6e/0x6f=256、0x70..0x72=0。没有为此接受其他属性继承。 |
| 百分比标记与对象尺寸 | **接受机器表达，功能名为推断**。`c8d4..c906`检查0x60000000/0x20000000、保留0x9fffffff和sentinel0x1fffffff、signed比较0x10000000后可能0x0fffffff-q。`c906..c91a`x、`c948..c95c`y均先high-low+1、低32位MUL、signed DIV100。`c964/c96c`再次读取low加到支点。 |
| inverse参数 | **接受**。`c97c..c98e`分别算DIV(W(scale+65535),scale)，NEG(angle)；`c992`a6=inverse XOR1；`c996`a5=s0-40=sp+24。flags=1实际inverse=0。不能改成实数倒数。 |
| 点整数缩放与旋转 | **接受**。`9e4e..9e70`先对全数组减pivot；无角度路径 `9e90/9ea4`MUL、`9e94/9ea8`ASR8；有角度 `9ec6`DIV10，四次sin前 `9ee4/9ef4/9f02/9f10`为ext15:0；插值 `9f42/9f46`MULA、DIV10、ASR5；`9f70..9fee`按比例/scale_first分支，ASR10或18。 |
| 正弦依赖 | **接受机器算法，未认证库**。`9da8..9dba`每次±360后截signed16；`9d94/9dc8/9de2`分四象限，按u16表索引；正32767转32768、负-32767转-32768。表 `a02640dc` 共91项，末项原值32768。 |
| 包围框signed、无最终-1 | **接受**。`ca9a..cb12`用signed SLT和条件移动挑极值；`cab6/cad4/cafc/cb16`按area+0/+8/+4/+12顺序写入，无减1、失败回滚或identity区域返回分支。 |
| a0返回及caller | **接受**。`caf4=33a5e600`是最后一次写a0，含义为pts[0].y小于前三候选最小值，不是成功码。`db22`后重读父；`db70`后`db74/db78/db7a`重新布参给交集，`db80`判断交集a0。变换返回不作条件。 |
| 栈借用/指针持有 | **限定接受同步闭包**。walk帧-40/-36保存count/pts跨callee；node传本帧sp+24的pivot；点函数全部callee只有sin，sin仅读表。本路径没有持久保存area/pts/pivot，无异步/申请/释放。对象/style外部生命周期未核。 |

表中ca/c9/c8/c6/c0/db地址前缀均为a00d；dfd/e00地址为a019；9d/9e/9f地址为a008。完整地址/原字节以新instructions为准。接受项以观察到的代码及既有厂商模型为依据，不是硬件执行结果。

## 必要布局、伪代码和状态流

布局为机器解释而非原C声明：area四个signed32坐标顺序[x1,y1,x2,y2]，点为{x,y}两个word；node+4链指针、+8 aux、+0xc descriptor数组、+0x14/+0x18/+0x1c/+0x20区域、+0x28 word混合state及数量、+0x2a halfword bit3控制前缀style。aux+0x30 bits27:26=mode。descriptor步长8，+0指style、+4控制及selector；style+0存储、+4存在位、+8 u8格式/数量。不可把重叠word/halfword拆成互不相关字段。

下列伪代码不是原源码；W是每步保留低32位，s是signed32，ASR是算术右移，DIV为signed向零截断。

```c
area_transform(obj, area, flags):
    // 48B帧，pts在sp+0..31，原area保存在s1。
    pts = {{area.x1,area.y1}, {area.x1,W(area.y2+1)},
           {W(area.x2+1),area.y1}, {W(area.x2+1),W(area.y2+1)}}
    walk(obj,pts,4,flags)
    area.x1 = signed_min(pts[2].x,pts[3].x,pts[1].x,pts[0].x)
    area.x2 = signed_max(pts[3].x,pts[2].x,pts[1].x,pts[0].x)
    area.y1 = signed_min(pts[2].y,pts[3].y,pts[1].y,pts[0].y)
    area.y2 = signed_max(pts[3].y,pts[2].y,pts[1].y,pts[0].y)
    // 机器a0仅残留y1的最后SLT，不作业务返回约定。

walk(node,pts,n,flags):
    if node == 0: return
    aux=load32(node+8); mode=aux ? bits(load32(aux+0x30),27,26) : 0
    if flags&2:
        if flags&1: walk(load32(node+4),pts,n,flags)
        if mode==2: node_transform(node,pts,n,1)
    else:
        if mode==2: node_transform(node,pts,n,0)
        if flags&1: walk(load32(node+4),pts,n,flags)

node_transform(node,pts,n,inverse):
    angle=style70(node,0); sx=positive_style6e(node); sy=positive_style6f(node)
    if sx==0: sx=1
    if sy==0: sy=1
    if angle==0 && sx==256 && sy==256: return
    px=style(node,0,0x71); py=style(node,0,0x72)
    // x后y：标记判断/percent换算；尺寸字段按原序重读，最后另读low。
    pivot.x=relative_then_add_low(px,node+0x14,node+0x1c)
    pivot.y=relative_then_add_low(py,node+0x18,node+0x20)
    if inverse:
        sx=DIV(W(sx+65535),sx); sy=DIV(W(sy+65535),sy); angle=W(-angle)
    points(pts,n,angle,sx,sy,&pivot,inverse^1)
```

不把setter未核的值域扩为任意坐标实验。点函数对angle仅一次大于3600减3600或小于0加3600，随后d=DIV(angle,10)、r=angle-10*d；四次sin实参为signed16(d)、signed16(d+1)、signed16(d+90)、signed16(d+91)。插值得S/C，经DIV10再ASR5；非无限取模。

每点先减pivot后的x/y保留在寄存器：不缩放时newx=ASR(W(C*x-S*y),10)、newy=ASR(W(C*y+S*x),10)。scale_first时先W(sx*x)、W(sy*y)，再旋转ASR18；否则先旋转的W结果各乘sx/sy再ASR18。无角度时分别ASR(W(sx*x),8)、ASR(W(sy*y),8)。所有乘加减都必须保留RV32截断，负数ASR不能替换为DIV256。最后各加pivot并写x后y；y运算用旧x寄存器，未使用新写x。pivot.x在本点运算前读，pivot.y在x写后读；本入口pivot与pts是不同帧的不同局部，不别名。

业务状态是：caller已有区域副本→谓词允许→四点栈数组→逐个mode2节点同步变换→signed包围框覆盖副本→caller的后续祖先裁剪。没有成功/失败事件状态、临时资源转移或回滚。identity节点会提前返回，但外层四点+1及包围框写回照常发生。

## 所有权、来源、验证和断边

area由caller借给本帧，可写但不接管；pts属于a00dca48的48B帧；pivot属于c862的64B帧；style查值的out属于c658的48B帧。c070/c020仅同步写out，c862只同步借pts/pivot给9e10，9e10只依赖读表sin。持久node/aux/descriptor/style/table只读借用，唯一非栈外写是调用者传入area及points入参。这证明本闭包内无指针持有，不能证明调用期间外部没有释放/改state或任何并发串行化机制。

厂商57字逐字按原编码拆分。以 `0x6da9b98b` 的extu和 `caf8=0x42a6970b` 的mvnez为例，后者rd=x14、rs1=x13、rs2=x10、funct7=33，rs2非0才选新值；和前置signed SLT组成min。MULA/MULS的寄存器4B宽给低32位累加/累减。模型来源是主仓库只读 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc`，使用的构造器逐条存入新evidence。本轮没有上游ISA认证，也没有修改模型来补未知字。

来源层次：G01保留的whole-ROM inventory ID `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2` 与各函数extent/callee是历史静态定位。新证据是本轮从同一ROM读取的2428B及字段核验，不假称新REA会话。G01所引ROM `lv_obj_style.c` 路径与 `lv_obj_get_style_prop` 字符串只支持LVGL来源候选；本轮未重新认证完整来源字符串链、准确版本或厂商差异。正弦/Q15→Q10是表和插值支持的功能推断，不作为已确认标准数学库排除。

实际运行：`python reverse/analysis/region-transform-review-g02-0041-20261023/review.py` 最终 **passed：11核心、14窗口、2428B、814指令、57厂商字、135静态检查、793重叠原指令一致**。人工阅读完整11核心及所选caller窗口，核原实参与保存恢复、写入次序、状态字段重读和所有权。机械检查数仅描述研究工具覆盖量，不代表语义完成百分比。提取器首版的输出父目录定位与重叠计数预期已按实际窗口纠正，未涉及任何ROM行为修改；最终脚本不运行历史验证器、模型或代码路径。

未执行固件、项目编译、历史回放、异常输入/缺陷/漏洞实验，也无设备/外部服务连接。未改ROM、生产代码、安全检查、构建或分析模型。没有新增开源排除。

| 状态 | 剩余准确边界 |
| --- | --- |
| 本次接受 | 11核心正常路径、五属性、flags1及同函数逆序分支、四点/参数/整数算术/写回、两caller不消费变换返回 |
| 本次仅合同 | C22交集写后判断及门控，未重验整个C22；正常对象前置条件来自caller |
| 未核输入端 | mode/state/style setter、node+4/aux/descriptor/style生产与释放、调用期间外部串行化 |
| 未核依赖域 | c658空对象诊断两callee；其他property、group非零及全style继承；正弦源码/表生成来源 |
| 未核输出端 | `a00ddbf6`的成功后段 `a00ddc7e` 起、提交/合并/持久保存与最终显示；具体后续callee本次未知 |

一个后继闭包建议：以 **a00ddbf6 在第三门非零后的 a00ddc7e** 为入口，回答“本次已变换/裁剪的入口栈区域何时被复制、提交或持有，后续哪个确切消费者使用它”。必要前置合同是C22的第三门0早退/非零继续、area为入口帧副本，以及本轮变换只原地改四word、不提供成功码。只追后段正常提交→必要存储/消费/归还的小闭包；具体callee、队列形式与合并规则目前未知，不能把候选名称写成已知调用链。本轮没有为准备后继扩扫或自行接任。

提交操作记录：首次仅暂存四个独占输出文件的git add，被worktree Git元数据 `index.lock` 写权限拒绝；按用户既有本地分支提交授权申请所需元数据写入，不改变文件权限或绕过限制。
