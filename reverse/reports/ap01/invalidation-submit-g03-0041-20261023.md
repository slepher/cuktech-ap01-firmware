# 0041 G03：区域提交、内嵌记录与直接消费者

结论：`a00ddbf6` 的第三门非零后，入口区域副本经可选外扩、显示器重新选择、显示边界裁剪、格式对齐和同步事件，写入 **display+0x44 的32项内嵌区域数组**，由 word[display+0x264] 计数。这不是本轮发现的动态节点队列。提交只消除“新矩形完全包含于既有矩形”的重复；真正的重叠/面积合并在直接消费者 `a00e0ac8` 进行。容量耗尽退化为全屏记录，消费者最终复位数组、合并标记和计数。没有据此认定像素或DMA/LCD已经完成。

任务主问题在提交→一直接消费者的范围内得到答案；**事件注册callback身份、事件38到消费者的真实调度连接、callback是否保留param、绘制callee内是否保留area指针仍是精确断边**。特别是 `a00ddc7e` 为 `a00ddbf6` 内续接地址，`a00ddd90` 和 `a00e105e` 同样不是新函数。下文伪代码是机器语义整理，不是原源码、固件执行或正式C类型。

## 范围、来源和证据

固定启动基线 `da4c9dc408d3fe1b7cfe2faed15d5011369f735c`，分支 `codex/re-0041-g03`，独立worktree `D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g03`。读取管理共同规则、完整G03任务书、REA技能/native guide、[C22](region-gating-review-c22-0041-20261023.md)和[G02](region-transform-review-g02-0041-20261023.md)。前门/第三门/变换作为既有合同，未重新宣称验收。未发现本树适用的AGENTS.md。

没有打开、切换或修改共享REA数据库。新证据从主仓库只读ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin` 取得，映射 `file_offset=VA-0x9ffff000`。静态函数定位沿用 whole-ROM inventory `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2` 及其主仓库ledger；没有重跑历史研究脚本或构建/执行固件。

[instructions.txt](../../analysis/invalidation-submit-g03-0041-20261023/instructions.txt) 保留原指令地址、文件偏移、原字节、普通指令及厂商字段、重新拆分的控制目标；[evidence.json](../../analysis/invalidation-submit-g03-0041-20261023/evidence.json) 保留18窗口、3758B、1254条指令、29个厂商字、所用本地模型原文、来源字符串及70项机械断言。[verify.py](../../analysis/invalidation-submit-g03-0041-20261023/verify.py) 和 [explore.py](../../analysis/invalidation-submit-g03-0041-20261023/explore.py) 只读取ROM并解码，不模拟路径或运行SLEIGH模型。Capstone用于标准RV32/RVC，厂商字以编码字段和只读本地 `ap01thead2.sinc` 核对。没有新建哈希清单/ROM复制/机械重复旧证据。

12个核心合同如下；“消费者”只恢复本问题所需记录流、合并与归还，完整函数字节留证不等于全显示过程已恢复。

| 地址，末端不含 | ABI和实际恢复范围 |
| --- | --- |
| `a00ddbf6..a00dddf4` | a0=obj、a1=requested_area；重点dc7e后提交，前段只针对核C22调用合同 |
| `a0080e3e..a0080e6c` | a0=display或0；宽度word，rotation字段选择0/4偏移 |
| `a0080e6c..a0080e9a` | a0=display或0；高度word，与宽度选择相反 |
| `a008b43a..a008b456` | a0=dst、a1=src；依次读取/写入0/4/8/12四word |
| `a00894aa..a008954c` | a0=inner、a1=outer、a2=radius；本路径radius=0，signed矩形包含判定 |
| `a00814f4..a0081554` | a0=display、a1=event_code、a2=param；同步两阶段事件，返回最终分派值 |
| `a008acfa..a008adf4` | a0=list、a1=event*、a2=phase；遍历事件descriptor并直接callback(event*) |
| `a0089472..a00894aa` | a0/a1=area*；signed坐标交叠，边相等算交叠，返回0/1 |
| `a008928c..a00892ac` | a0=area*；低32位 `(x2-x1+1)*(y2-y1+1)` |
| `a00e0ac8..a00e1294` | a0=timer或0；取/选display、记录合并、未标记记录交给绘制入口、清理记录 |
| `a000589c` 的word对齐n=16/20路径 | a0=dst、a1=src、a2=n；只恢复本闭包分离word对齐16B及事件list快照20B拷贝；完整未对齐分支不纳入 |
| `a0024906..a00249c4` | a0=dst、a1=填充值、a2=len；只恢复本闭包word对齐/值0/长度28、32、64、512正常路径 |

必要短依赖另留 `a0080d8e` 清零包装、`a008ac38..acfa` 分派后清理、`a00ecd68..cd76` 正常vector slot运算。后者完整函数起点为a00ecd14，cd68为已经完成范围/空检查后的续接，不能把cd68当新函数。通用复制/填充没有认证开源来源，也没有因疑似libc将本轮所需路径排除。

## 提交的原顺序和分支

1. **后置扩张**：`a00ddc7e..dc9c` 再读原obj+8，aux非零且LHU(aux+0x32)&0xc00恰等于0x800时，调 `a00892ac(入口副本,5,5)`。这是第三门之后的又一次检查和扩张，不能并进G02变换，也不能缓存第三门中的谓词。
2. **重新取display**：`dca0..dcb2` 再调 `a00dce2e(obj)`；零则读全局word@62fc9590，仍零直接尾部。`dcb4..dcba` 再查 `a0081804(display)`，零尾部。getter身份仍沿用C22不透明合同，不能假定与第一门取值永远相同。
3. **渲染期状态门**：`dcbc..dcc4` LHU(display+0x3e)&0x400存入s2。非零走诊断 `a008b51a`，随后 `ddcfa..ddd04` 准备(path,line=0x115,0)跳回dc42的 `a0019672`。没有新记录写入。该终止callee是否返回及随后控制属性未认证，不能伪造本函数统一失败返回或擅自修正状态。
4. **全屏框/交集**：`ddd06..ddd32` 先写full.x1=0、full.y1=0，再调用宽getter减1写full.x2，再调用高getter减1写full.y2；`a00892f4(&clipped,&入口副本,&full)`。返回零直接尾部，局部clipped可已被写，不回滚。full的四word在s0-64..-52，clipped在s0-48..-36；入口副本在s0-80..-68，三份不混同。
5. **格式7对齐**：`ddd38..ddd54` LBU(display+0x40)==7才把clipped.x1 AND -8、clipped.x2 OR7；没有对齐y，也没有对齐后再裁剪。这是机器观察，不认证格式枚举名。
6. **模式2**：`ddd58..ddd7e` LBU(display+0x3d)==2，调用 `a000589c(display+0x44,&full,16)`，明确写count=1，再event(display,0x38,0)。**使用full而非clipped**，没有event0x35、重复扫描和count+1；旧记录/标记没有在提交端整体清零。
7. **其他模式可调整事件**：`ddd90..ddda0` 事件 `(display,0x35,&clipped)`；只有返回**恰1**才继续，不等1直接退出。本轮分派器正常路径仅产生0/1；不能把返回判断从指令的“恰1”弱化。param可写；下一步消费的是调用返回后的栈clipped，事件允许同步修改它。
8. **包含消重、容量和追加**：`ddda4` 在事件返回之后重新读count保存s3，s2在成功渲染门后恰为0。逐项 `(inner=&clipped,outer=display+0x44+16*s2,radius=0)` 调contains。非零直接退出，既不写count也不发0x38。s2逐项加1后 `dddee=0x3c09390b` 提取15:0；与缓存s3进行unsigned比较。扫描完：s3<=31选clipped；否则先写count=0并选full。**再重读count**算dst，copy4；**再重读count**加1，写回count，最后event0x38(param=0)。普通新增的实际store序为区域+0/+4/+8/+12→count→事件。

普通包含判断是 `inner.x1>=outer.x1 && inner.y1>=outer.y1 && inner.x2<=outer.x2 && inner.y2<=outer.y2`，全部signed32；本路径radius0在 `a00894f8..94fa` 直接返回1，后面的圆角点检测不会被调用。提交阶段没有把两个重叠框求union，也没有移除较小旧记录。

关键原字节例：`a00ddda0=e311f5fe` 的BNE仅接受a0=1；`a00dddb2=63f63701` 的BGEU按unsigned s3<=31走普通追加；`a00ddd72=23a2f426` 是SW(display+0x264)，不是halfword计数。失败路径没有释放新节点，因为这个提交路径没有分配节点。

```c
// 前置门、第三门及变换沿用C22/G02；以下从dc7e继续。
if (obj.aux && (u16(obj.aux+0x32)&0xc00)==0x800) expand(local,5,5);
d=get_display(obj); if (!d) d=word_at_62fc9590;
if (!d) goto machine_tail;
if (!enabled(d)) goto machine_tail;
u32 i=u16(d+0x3e)&0x400;
if (i) { diagnostic(...); opaque_terminal(path,0x115,0); /* 不伪造return */ }
Area full; full.x1=0; full.y1=0;
full.x2=W(width(d)-1); full.y2=W(height(d)-1);
Area clipped;
if (!intersect(&clipped,&local,&full)) goto machine_tail;
if (u8(d+0x40)==7) { clipped.x1 &= -8; clipped.x2 |= 7; }
if (u8(d+0x3d)==2) {
    copy16_word_aligned(d+0x44,&full,16);
    word(d+0x264)=1;
    event(d,0x38,0); goto machine_tail;
}
if (event(d,0x35,&clipped)!=1) goto machine_tail;
u32 snapshot=word(d+0x264); // 不把重读折成snapshot
for (; i<snapshot; i=(i+1)&0xffff)
    if (contains(&clipped,d+0x44+16*i,0)) goto machine_tail;
Area *chosen=&clipped;
if (snapshot>31u) { word(d+0x264)=0; chosen=&full; }
copy4(d+0x44+16*word(d+0x264),chosen);
u32 n=word(d+0x264); word(d+0x264)=W(n+1);
event(d,0x38,0);
machine_tail: /* 恢复寄存器和sp，不重写a0 */
```

机器a0不能当统一成功码：display不存在时可残留getter的0；交集失败是0；重复包含返回1；事件拒绝残留最终分派值；提交/模式2返回最后event的a0。C22早退值继续有效；本轮没有认证原C函数返回类型。

## 事件ABI、栈借用及清理

`a00814f4` 建64B帧，event在s0-44..-17共28B，先经zero-wrapper清零。再写+0/+4=display、+8=code、+0x10=param，分派时把display+0x2e8作为list。第一次phase1；仅返回恰1才第二次phase0，其他返回原样退出。每次callback通过a0借用event*；event+0xc在callback前写descriptor的userdata，param仍在+0x10。无需假造callback(display,param)双参ABI。

`a008acfa` 对list头20B作本帧快照，保存entry count和原busy位，再置原list+0x14 bit0。每项经vector slot取得descriptor；callback=word[descriptor+0]，userdata=word[+4]，filter=word[+8]。filter bit16跳过；bit15须等phase；低15位零表示不过滤code，非零须等event+8。`a008ad92` 写event+0xc，`ad98` JALR直接同步调用。回调后**重读**event+0x18；先检查bit1：非零跳adae将s1改为1，停止遍历并最终返回1，**不是返回原掩码2**。bit1未置、bit0置时停止并返回0；都未置继续，完成返回1。进入时event bit0已经置位则返回0；null list返回1。bit1停止仍会允许包装器的第二phase，不能称全事件派发被取消。

嵌套分派依据原busy位分别处理：原不忙且event没有相应终止标志时，清原list busy并调用acc6处理待清项；需要快照清理时调ac38。ac38压紧未删除项、释放标记descriptor等；allocator/vector shrink保留精确边 `a008ab8a/a00ecc68`，不据其名称认证来源。这里清的是事件列表暂存/descriptor状态，不是区域记录的归还；不可写成free(area)。

event本体和param都同步传到间接callback；**已核分派器本身没有持久保存param**。然而callback身份没有在本轮恢复，descriptor可指向任意正常安装handler，因此不能证明它们不将param存到外部。普通提交的后续copy4确保内嵌记录存的是16B值而非栈指针；这不排除事件callback另行持有指针。模式2 n16对齐路径只进行四次word拷贝、返回a0原dst，没有持有地址；这个限定不覆盖通用helper的未对齐路径。event的28B清零及消费者512/32B清零均在本轮限定零填充路径可核，无分配/异步调用。

## 直接消费者及记录归还

`a00e0ac8` 与提交方访问同一display机器布局。a0非零时先把word[timer+0xc]写全局62fc958c；a0零则用全局62fc9590写62fc958c。后续反复读取62fc958c，不把display固定缓存为一个不变值。具体timer安装、event38是否唤醒该timer本轮未证实，不能把“共享布局消费者”写成“event38已经证明调用此函数”。

已核的必要正常顺序：选display→检查显示缓冲相关字段→event0x39→更新若干对象状态（a00d929a，内部边界）→合并记录→必要显示缓冲同步/list处理边界→event0x3b→设渲染标志→逐项未合并记录交给绘制→event0x3c→清渲染标志→记录清理→event0x3a及周边资源清理边界。e0c04回e0b1e退出，均为同一函数内控制。缺少display、无有效buffer等非主路径在原字节留证；不扩大成全部显示初始化/错误处理恢复。

**合并在消费端**，关键窗口 `a00e0c06..0c1a`、`0d5a..0e18`：外层i跳过byte[d+0x244+i]!=0的记录；内层j重读count，跳过已标记及i==j。对areas[i]/areas[j]先overlap；仅交叠才按signed min/min/max/max构造本帧union。area-size以RV32低32位计算三面积；若 `u32(union_area) < u32(W(area_i+area_j))` 才copy4覆盖areas[i]，再写joined[j]=1。相等时不合并。j继续前进，不重启已经检查过的j；count不会因合并减少，标记项仍占槽，下一轮outer会跳过它们。不能替换为一般集合最小覆盖算法。union写序为x1/y1/x2/y2；成功覆盖记录也按copy4原序。

`a00e0d96..0de4` 的条件移动均依前置signed SLT；`0daa=0x42c6970b` 等mvnez选择新坐标。面积是word乘法，`0dfe` 为unsigned BGEU，因此不能改写成无限精度几何面积比较。`0e10` 是SB joined[j]，不是count减1。

**直接读记录并交给绘制**：

- `a00e0cb6..0cc4` 反向扫描joined，找最后未标记索引s2；`0d02..0d08` 每轮重读count，`0x105e..1066` 跳过joined[s3]。找到最后项时将display+0x3c bit0置1，并在每项前清bit1；display+0x3e bit10在主消费循环期间置1，结束后清零。
- 正常mode1：`0x1082/1086→0x121e..1242` 若mode-1截u8<=1，会置display+0x3c bit1，算 `a0=display+0x44+16*index`，a1=0，直接进入 `a00e1148→a00e082e(area,0)`。mode2也走这个入口；它的提交记录已是full。这里是**借用内嵌记录地址**，没有消费前临时复制。
- mode0：`a00e108a..109c` 明确按+44/+48/+4c/+50读取四个word，按缓冲容量/格式分行，本帧s0-128..-113构造area，`a00e1148` 或 `11fc` 调同一 `a00e082e(&stack_area,y_offset)`，返回后调 `a00dc39e(display)` 再继续下一块/下一项。宽度/格式与行数计算callee `a0081b54`、事件0x35的行高调整及绘制本体仍作为精确边界，不认证像素算法。未知mode值分支留原指令，不扩到所有模式。
- `a00e0d0c..0d22` 主循环之后event0x3c并清渲染bit10；`0d28` 重读count，零则直接到收尾。非零且无模式1额外保留list处理时到`0d36`；模式1的 `1244..1282` 先为各未标记记录向display+26c链请求16B存储并用a000589c拷贝区域，然后也回0d36。list allocator `a008af14` 及其节点所有权是边界，不把它与32槽内嵌数组混同。
- **归还/复用**：`a00e0d36..0d54` 严格先zero(display+44,512)，后zero(display+244,32)，最后SW count=0。它复用display内嵌内存，不free每个area。模式1另存到链中的副本不由这三步释放；缓冲同步链处理 `e0c28..0cb4`、`e0e4e..1050` 不作完整生命周期验收。若之前发现必要绘制对象为空，`e0bba` 也明确清count再进诊断/收尾，不把该分支解释成已经绘制。

```c
// 仅为消费者已核记录算法；current_display()在机器中多次重读。
for (u32 i=0; i<d.count; ++i) {
    if (d.joined[i]) continue;
    for (u32 j=0; j<d.count; ++j) {
        if (d.joined[j] || i==j) continue;
        if (!overlap(&d.area[i],&d.area[j])) continue;
        Area u = signed_union(d.area[i],d.area[j]);
        if (u32(size(u)) < u32(W(size(d.area[i])+size(d.area[j])))) {
            copy4(&d.area[i],&u); d.joined[j]=1;
        }
    }
}
// 其他buffer/list业务在明确边界，不由此伪代码抹除。
event(d,0x3b,0); d.render_word |= 0x400;
for (s32 k=0; k<d.count; ++k) {
    if (d.joined[k]) continue;
    // 原码更新last/flush等位；mode0按块，mode1/2直接借area地址。
    if (mode_is_1_or_2) opaque_a00e082e(&d.area[k],0);
    else if (mode==0) opaque_chunked_calls_a00e082e(...);
    opaque_a00dc39e(d);
}
event(d,0x3c,0); d.render_word &= ~0x400;
// mode1有额外list副本保存边，不等于归还内嵌area。
zero(d.area,512); zero(d.joined,32); d.count=0;
```

以上伪代码只呈现合同，不把实际多次load、条件分支、other-buffer业务省略等价成可执行重建。消费者自身没有在内嵌数组中存area指针；绘制callee可能持有传入记录/stack_area，本轮未进入该callee，不能承诺其跨调用寿命。

## 布局、状态与恢复程度

机器布局为：display+0/+4两维word；+0x3c packed flags byte；+0x3d mode byte；+0x3e被LHU/SH访问的状态位，其中0x400为提交期间禁止门/消费者渲染门；+0x40格式byte；+0x44..0x243为32×16B区域；+0x244..0x263为32B joined标记；+0x264为word count；+0x26c起另一list容器；+0x2e8为event list。width/height以 `(word[d+0x300]&5)==1` 交换+0/+4的选择；空a0可回退默认display，默认也空返回0。正式结构名/枚举及正常值域未知。

所有权状态为：caller请求→入口16B副本（前门/第三门/变换可写）→局部clipped/full→同步event借用clipped→copy4或限定copy16写display内嵌值→消费者就地合并及joined标记→绘制callee借用→必要模式1链上副本→内嵌记录清零复用。分配/释放的事件descriptor和模式1链节点是不同资源，不能合并进area ownership。没有锁/并发串行化的完整证据，不能把重读“优化”为恒定字段，也不为未知并发设计修复。

事实：指令、字段偏移/宽度、正常控制目标、上列读写/返回/间接ABI及复制/清零限定路径。推断：display、invalid area、joined等功能解释；得到ROM字符串 `a0569c48=/home/jiangmingmin/ap01/AP01_BL618/apps/graphics/lvgl/lvgl/src/core/lv_refr.c`、`a056a3a8=lv_inv_area`、`a056a360=lv_display_refr_timer`、`a0569e5c=Invalidate area is not allowed during rendering.` 支持该命名。准确LVGL版本、厂商修改边界和源码身份未认证；没有开源排除，也不计算全ROM完成百分比。

## 实际验证、限制和一个后继

实际运行 `python reverse/analysis/invalidation-submit-g03-0041-20261023/verify.py` 最终passed：18窗口/3758B/1254指令/29厂商字/70机械核查。人工完整阅读提交后段、两阶段事件分派、radius0包含、overlap/size、消费者记录合并/交付/清理及复制填充限定路径。字段断言验证关键store宽度/偏移、事件参数位置、厂商extu字段、jump/branch目标；数量是工具覆盖，不是语义验收数量。临时探索曾从ce70（非边界）解出无效中途指令，该片段未用于任何结论，也未列入最终证据窗口；getter继续保持C22不透明合同。

有界定位记录：在ROM映射地址a007f000..a01af000的2B对齐候选位置按标准LW imm0x264原字掩码搜索，得到提交后段、a00e0c16/0c80/0cb6/0d04/0d28/0d68/127a，以及a0147f56/7f68/7f88等候选；本轮只展开与display+44/+244同布局并有实际读/清count关系的a00e0ac8。不将该扫描视作全部xref或“没有其他消费者”，也未把a0147fxx泛化为区域消费者。

最终未执行固件、设备连接、外部服务、异常区域/缺陷/漏洞测试、历史回放、项目编译或生产测试；未修改ROM、生产代码、安全检查、构建或分析模型。仅独占analysis目录/本报告发生写入，不回滚他人更改、不创建下级agent。本轮自行静态核验不等于新agent独立验收。

本地提交前首次git add因独立worktree的index.lock位于主仓库只读Git元数据区域而被拒绝；按照已授权本地提交范围，申请元数据写入升级后暂存五个明确独占文件，没有更改权限或主树索引。diff检查发现生成指令文本中无operand的EBREAK行尾空格，已修生成器并重新验证。

精确断边：提交的display getter `a00dce2e`、诊断/终止属性、事件列表注册者及 `a008ad98 JALR descriptor.callback(event*)`；event0x38到timer入口a00e0ac8的触发连接；`a00e1148/11fc→a00e082e` 的记录/栈area借用是否被进一步保存、`a00dc39e` 后处理；模式1的 `a008af14/a000589c` 链副本的最终持有者。物理显示/DMA/LCD及全部buffer/list刷新不在范围。

建议仅启动一个后继闭包：恢复此display事件列表的0x35/0x38实际注册descriptor→callback(event*)→param消费/保存及0x38调度连接。入口证据是 `a00814f4` 的display+2e8、`a008ad80..ad98` 的filter/userdata/callback及本轮submit的ddd90/ddd76；先定位安装者而非猜timer回调。目标是确认谁能同步调整clipped、谁通知刷新、是否留下栈param；若动态callback身份不可唯一解析，列具体安装点/断边，不接管最终绘制或全GUI事件系统。
