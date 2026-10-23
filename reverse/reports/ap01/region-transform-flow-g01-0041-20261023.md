# 0041 G01：对象属性到四点区域变换及 caller 消费

结论：`a00dca48(obj,area,1)` 将四 word 区域展开成四个点（右、下坐标各先加1），对起点以及 `+4` 链上的 mode==2 节点依次作整数缩放/旋转，再把四点的有符号最小/最大坐标写回原 area。flag1 表示先当前节点、再父链的正向顺序；它不是“逆变换”。写回没有末尾减1。C21谓词的 aux+0x32 bits11:10 与本轮 aux+0x30 bits27:26 恰是同一位域；谓词命中的节点指针没有传入，但本轮自己继续遍历链。两处 caller 不消费此 callee 的返回寄存器，只消费变换后的区域。

本轮闭合正常非空对象的属性读取→选择→参数换算→点数组→包围区域→已有交集消费，共11个核心函数；未恢复最终区域提交或物理刷新，未认证开源版本。属性的写入者及对象链生命周期仍是输入端断边。

## 范围与原始证据

固定基线 `004ff564bca0dcf22c078a6b192e1095fd53da04`，分支 `codex/re-0041-g01`，独立 worktree `D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g01`。已读管理共同规则、G01完整任务书、C22正式报告、REA技能和native guide；本树输出父级与worktree逐级祖先未见适用AGENTS.md。只写本报告及独占analysis目录，没有改变主树、其他agent文件、共享索引或分析器模型，没有下级agent。

[verify.py](../../analysis/region-transform-flow-g01-0041-20261023/verify.py) 从主仓库只读ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin` 取字节，映射 `file_offset=address-0x9ffff000`，普通RV32+C用Capstone 5.0.7逐条解码，直接控制目标独立拆立即数，厂商字独立拆位后引用既有只读SLEIGH原文。本次没有新开/切换REA目标或共享可写数据库，也没有运行历史验证器。

[evidence.json](../../analysis/region-transform-flow-g01-0041-20261023/evidence.json) 保存原字节、地址、偏移、解码、直接控制目标、11函数历史extent/callee记录、所用厂商构造器原文、5B属性元数据、182B正弦表、来源字符串及247项静态检查；[instructions.txt](../../analysis/region-transform-flow-g01-0041-20261023/instructions.txt) 按地址可读。没有增加哈希/复制清单。总14窗口、2466B代码、823条指令、61条厂商字；247是机械核对数，不是语义结论数。

| 核心地址与完整连续范围（末端不含） | 本轮合同 |
| --- | --- |
| `a00dca48..a00dcb22`，218B | 区域→四点→四点包围区域，a0=obj/a1=可写area/a2=flags |
| `a00dc9ba..a00dca48`，142B | a0=node/a1=点数组/a2=数量/a3=flags；按mode和flags遍历、调本节点变换 |
| `a00dc862..a00dc9ba`，344B | a0=obj/a1=点数组/a2=数量/a3=inverse；形成角度、比例与绝对支点 |
| `a0083796..a00837ae`，24B | style(obj,selector,0x70)角度word读取包装 |
| `a019dfd0..a019dff0`，32B | style(obj,0,0x6e)，signed <=0 时返回1 |
| `a019dff0..a019e010`，32B | style(obj,0,0x6f)，signed <=0 时返回1 |
| `a00dc658..a00dc862`，522B | 对象state参与的style读取、缺省；本轮语义限定0x6e..0x72正常非空对象 |
| `a00dc070..a00dc19a`，298B | 对象style描述符数组的选择及有序取值；无外部不透明依赖 |
| `a00dc020..a00dc070`，80B | 两种style容器中的property查找，命中复制一个word到out |
| `a0089e10..a0089ff0`，480B | a0=点数组/a1=count/a2=angle/a3=sx/a4=sy/a5=pivot*/a6=先缩放；全整数原地点变换 |
| `a0089d76..a0089e10`，154B | 有符号角度整数到基于表的正弦标量，无callee |

另取两处C22已核caller窗口 `a00ddb14..a00ddb26`、`a00ddb60..a00ddb84` 及既有交集 `a00892f4..a008934a`，仅核相关接口/原字节，不重做完整门控。11个extent和直接callee集合均与历史whole-ROM图证据一致，所有核心直接分支落在本函数指令边界，没有间接callee（JR ra是返回）。`a00dc658` 的空对象诊断分支仍包含不透明 `a008b51a/a0019672`，本轮没有验证或展开该非正常前置条件路径。

## 数据布局与属性生产边界

机器布局（字段名为解释，不是原C结构）：node+4=32位链指针；+8=aux指针；+0xc=style描述符数组指针；+0x14/+0x18/+0x1c/+0x20=坐标四word；+0x28 word的bits25:20=描述符数量，低16位也由取值器用作state；+0x2a无符号halfword的bit3=选择器前缀控制位。aux+0x30 word的bits27:26为mode；aux空则mode=0。同一word与halfword的重叠必须保留，不能拆成互不关联的虚构字段。

每个style描述符8B：+0为style指针，+4为控制/selector word；bit25参与前缀选择，bits23:16参与group匹配，低16位为state。style+0为存储指针，+4为属性存在位图，+8为u8数量/格式。property p的快速位是 `1 << min(p>>2,31)`，本轮p均得到bit27；这只是快速排除，不替代真正ID匹配。

`a00dc020(style,p,out)` 两种格式均只写 `word[out]`，无申请、释放、指针保存：

```c
n = load_u8(style+8); base = load32(style);
if (n != 255) {
    ids = base + 4*n;
    for (i=0; unsigned(i)<n; i++)
        if (load_u8(ids+i)==p) { store32(out,load32(base+4*i)); return 1; }
    return 0;
}
// sentinel格式：8B一项；第一byte为ID，word+4为值，ID=0终止。
for (q=base; (id=load_u8(q))!=0; q+=8)
    if (id==p) { store32(out,load32(q+4)); return 1; }
return 0;
```

`a00dc070(obj,selector,p,out)` 保留两阶段扫描。先取obj+0x2a的bit3，再按每轮重读word[obj+0x28]的bits25:20控制数量，数组指针也重读。前缀条目的bit25置位时，只有对象控制位为0才检查：group必须等于 `selector & 0x00ff0000`，style存在位命中后调用c020，返回1立刻返回1；不符合就继续。遇到首个bit25未置位条目时，从**同一个索引**进入一般扫描，不重置到0。

一般扫描令requested=`selector&0xffff`、best=-1。只考虑存在位命中、group一致、`candidate_state & (~requested & 0xffff)==0` 且 signed(best)<candidate_state 的条目；c020真命中才更新best。candidate等于requested则立即1，否则继续，后来的更大可用state可覆盖out。结束返回best!=-1。失败不保证out始终原值：先命中较小state后会保留其值并返回1；未命中时c020不写。这里没有未知callback或隐式“找最大对象指针”。

`a00dc658(obj,selector,p)` 先读取u16[obj+0x28]，OR传入selector，out局部清零，再调用c070。成功即取out；失败后按ROM属性元数据和selector走继承/缺省。**本轮五个ID没有进入继承链**：`a056a49e..a056a4a2` 对应0x6e..0x72，字节原值 `32 32 32 00 00`，bit0均0；本轮传入selector=0，与u16合成的selector也不含0x00ff0000高group，因此直接走缺省。0x6e/0x6f默认0x100；0x70/0x71/0x72默认0。本轮没有把所有style的继承算法作为“已恢复”，但其全函数原字节均保存。其他property默认表、obj+0原型链和group非零路径不是这个闭包的输入。

| property | 原始取值及后续用途 |
| --- | --- |
| 0x70 | a0083796设置a2=0x70，保留caller给的a1=0，返回完整word；c862作为angle保留s6 |
| 0x6e / 0x6f | 两个getter依次读取；signed非正结果改为1。c862又分别保留“零再改1”分支，不能删为统一假定；0x100是无缩放 |
| 0x71 / 0x72 | c862依次读取，保留两次调用顺序；前值先存局部，后值另存；作为支点x/y候选 |

属性设置者、descriptor/存储分配者、state更新者和mode写者本轮没有展开；这些是具定位字段的上游来源断边，不以来源字符串替代写入链证据。

## 链顺序与每个节点的参数提取

`a00dc9ba` 在入口a0=0直接JR ra，不读area。非空时每层先读aux，再读mode（厂商原字 `a00dc9d6=6da9b98b`，rd=rs1=s3、unsigned bits27:26）。flags保留完整word，但只用bit1选择逆序/逆向、bit0选择父链：

```c
walk(node, pts, n, flags):
    if (node==0): return;                  // 机器a0=0
    aux=load32(node+8);
    mode=aux ? bits_u32(load32(aux+0x30),27,26) : 0;
    if (flags & 2) {
        if (flags & 1) walk(load32(node+4),pts,n,flags);
        if (mode==2) transform_node(node,pts,n,1);
        return;
    }
    if (mode==2) transform_node(node,pts,n,0);
    if (flags & 1) walk(load32(node+4),pts,n,flags);
```

这是递归，不是将命中节点一次性返回。正向在本节点变换返回后才读node+4；逆向先读父指针递归，再处理原节点。mode在递归之前已保存，不在返回后重读。flags=1时依次当前→父→更高节点，每层重新读取自身aux和mode。C21包括起点的存在性扫描只使这一次walk有必要运行，不为walk提供命中节点缓存。没有证明任意链终止或并发不变性。

`a00dc862` 次序：角度→sx→sy→两个零值分支→若angle=0且sx=sy=256立即尾部；否则读取0x71→0x72→对x候选换算→对y候选换算→加当前对象x1/y1成为绝对支点→按inverse调整→调用点变换。即无变换时**不读取支点属性**。

候选v的坐标换算保持实际32位比较和RV32 MUL/DIV，下面W表示每一步保留低32位，s表示signed32解释，DIV表示signed向零截断：

```c
relative(v, object_low, object_high):
    if ((v & 0x60000000)==0x20000000) {
        q=v & 0x9fffffff;
        if (q != 0x1fffffff) {
            if (s(q)>=0x10000000) q=W(0x0fffffff-q);
            // 实际顺序：high-low，+1，mul，signed div100。
            v=DIV(W(W(object_high-object_low+1)*q),100);
        }
    }
    return W(v+object_low);
```

x尺寸重读obj+0x1c、+0x14，y尺寸重读obj+0x20、+0x18；最终支点又分别重读obj+0x14、+0x18。不缓存一份“对象区域快照”。标记形式支持“百分比支点”的解释；确切原枚举名/合法域未知，不能改为浮点百分比或省略sentinel。

inverse非零时，分别计算 `DIV(W(sx+65535),sx)`、`DIV(W(sy+65535),sy)`，angle取32位NEG；原码不是一般实数倒数。传点变换的a6为 `inverse XOR 1`，a5指向本帧s0-40（sp+24）的两个支点word，a0为点数组、a1=count、a2=angle、a3/a4为最终比例。当前正常入口使inverse=0，因此a6=1；逆向合同来自同一小函数，不扩展其他caller。

## 点变换的整数算术合同

`a0089e10` 全函数仅依赖 `a0089d76`，无浮点指令/浮点调用ABI、allocator、callback或全局输出。无变换（angle=0且sx=sy=256）立即返回机器a0=0，不读取点和pivot。其余先对全部count点逐点执行x减pivot.x、y减pivot.y，点步长8；两个pivot值在循环中分别重读，不先复制为一个全程不变结构。

angle=0时每点执行 `x=W(ASR(W(sx*x),8)+load32(pivot))` 后写x，随后y同样乘sy/算术右移8/加重读pivot.y后写y；不使用C signed溢出语义，不以DIV256替换负数算术右移。

angle非零时，原码只做一次角度修正：大于3600减3600，小于0加3600，其余保持；不能改写成无界取模。令d=DIV(angle,10)、r=W(angle-10*d)，四次sin调用的实参均先符号截取低16位，次序d、d+1、d+90、d+91。随后：

```c
S=ASR(DIV(W(r*sin16(d+1) + W((10-r)*sin16(d))),10),5);
C=ASR(DIV(W(r*sin16(d+91)+ W((10-r)*sin16(d+90))),10),5);
// 每点x/y是前一轮“减pivot”后的word；所有乘/加/减均W。
if (sx==256 && sy==256) {
    newx=ASR(W(C*x-S*y),10);
    newy=ASR(W(C*y+S*x),10);
} else if (scale_first!=0) {
    x=W(sx*x); y=W(sy*y);
    newx=ASR(W(C*x-S*y),18);
    newy=ASR(W(C*y+S*x),18);
} else {
    newx=ASR(W(W(C*x-S*y)*sx),18);
    newy=ASR(W(W(C*y+S*x)*sy),18);
}
store32(point,newx+load32(pivot));
store32(point+4,newy+load32(pivot+4));
```

伪代码表达数据依赖，不表示原源码。实际x输出先写，再完成y的加pivot/写；计算y保留所需原x寄存器，所以没有以新x参与y。实际load pivot.x早于该点分支运算，load pivot.y晚于x写入；本轮pivot是独立栈局部，不与点数组别名。ASR为signed算术右移，全部中间乘法保留RV32低32位；这不是精确实数矩阵，也不声称任意数值域的数学互逆。

`a0089d76` 对负角反复加360、对>359反复减360，每次截取signed16；按四象限查 `u16@a02640dc`（91项、每项2B），符号由象限决定。正半周读值32767时映射32768；负半周出现-32767时映射-32768。表首项0，90度项原值32768，本轮保存全部182B。91项表和插值支持“正弦/Q15→Q10”的功能命名推断；没有通过执行模型验证数值，不把函数宣称为已认证标准数学库。

厂商字依据既有本地模型：`ext/extu`分别有符号/无符号位提取（msb bits31:26、lsb bits25:20），`mula/muls`累加/累减低32位乘积，`mveqz/mvnez`条件寄存器选择，`addsl/lrw/srw/lrbu/lrhu`形成相应移位索引；每种使用的构造器及token原文均在evidence中。61条均按字拆位并和原模型文本绑定，没有补新模型语义或把本地模型提升成新取得的上游ISA认证。

## 四点、写回、返回与 caller 消费

48B帧中的点数组为sp+0..31（s0-48..-17），area原指针保留s1；先读area.x1、x2、y1、y2并形成下列8word，所有加1均模2^32：

```c
pts[0]={x1,y1}; pts[1]={x1,y2+1};
pts[2]={x2+1,y1}; pts[3]={x2+1,y2+1};
walk(obj,pts,4,flags);
// 分别比较每轴四个signed32坐标；原实际写回顺序如下：
area.x1=min_s32(pts[2].x,pts[3].x,pts[1].x,pts[0].x);
area.x2=max_s32(pts[3].x,pts[2].x,pts[1].x,pts[0].x);
area.y1=min_s32(pts[2].y,pts[3].y,pts[1].y,pts[0].y);
area.y2=max_s32(pts[3].y,pts[2].y,pts[1].y,pts[0].y);
```

两次c862 identity返回也不取消外层的+1与包围区域写回；源码式“如果无变换，直接返回原area”会改变原程序。没有任何减1、饱和、区域有效性判断或失败回滚。`a00dcab6/a00dcad4/a00dcafc/a00dcb16`依次写偏移0/8/4/12。signed SLT与条件移动求min/max，不是unsigned极值。

`a00dca48` 没有规范化成功码。最后修改a0的是 `a00dcaf4` 的signed SLT：`pts[0].y < min_s32(pts[2].y,pts[3].y,pts[1].y)`，后续store/比较/尾部均不改变a0，所以机器返回恰0或1，但语义是这一比较，**不能解释为变换成功/区域有效**。原C返回类型可能void，尚未认证。walk/node/点变换本身也没有统一状态返回，caller均不以它们作成功判断。

两处上层：

- `a00ddb22`以(obj,入口area副本,1)调用，返回后到db26重读父指针；区域已原地变换，后续每轮祖先temp被用来裁剪它。
- `a00ddb70`以(当轮祖先,temp,1)调用，db74立即设置交集的右输入=temp、左/目的=入口area，db7c调用 `a00892f4`；db80消费的是**交集**返回，非变换返回。

已有交集仍按signed max/min先写四word再判断有效性，边界相等允许1；所以变换后的局部写和后续交集失败并无回滚。两类区域都是更上层不同栈帧中的局部副本，不能混成请求者原始area或持久显示缓存。沿每节点绝对支点叠加后位于共同祖先坐标系是结构/数学解释；真实屏幕旋转、坐标原点配置和面板坐标仍未从本闭包认证。

## 所有权、来源、验证与断边

正常非空路径的11核心函数全部直接callee已纳入；没有调用者传入area/pts/pivot指针的持久保存、分配/释放或异步callback。持久对象/aux/style/descriptor和表均借用读取，唯一对外写是a00dca48原area四word及点变换的传入点数组；c070/c020写的是c658传入的栈word。本路径walk只同步传递pts，node helper只同步传递本帧pivot，返回前所有点处理完成。各层保存的count/点指针跨递归通过本帧s0-40/-36暂存后恢复；不是所有节点共用一份全局工作区。栈借用合同至此可静态闭合；**对象和style在调用期间的外部串行化/存活期没有恢复**。

来源事实：ROM中的 `a0569318` 为 `/home/jiangmingmin/ap01/AP01_BL618/apps/graphics/lvgl/lvgl/src/core/lv_obj_style.c`，`a056a3b4` 为 `lv_obj_get_style_prop`，由c658空对象诊断实参直接引用；另外保存NULL/断言字符串。它们支持c658与LVGL style有关，不能认证准确版本、原属性枚举、其余函数原名或厂商差异。本轮无外部服务访问、无新开源排除；没有因函数短小或看似数学标准库而跳过。whole-ROM inventory Evidence继承 `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2`，每核心函数独立extent/callee Evidence ID与来源文件已保存在evidence.functions；例如主函数extent `ev_972bc787e27b9dadae80749f1f4c35f579659da0e31a42e87545a52294500194`、直接callee `ev_d14045a1d461d86f8d6edc4455f7ae66a2bd741e141e9f4cfbe62655d736bae7`。这些是历史静态来源，本次新增的是独立原字节核验，并非新REA会话观察。

实际运行 `python reverse/analysis/region-transform-flow-g01-0041-20261023/verify.py`，最终 **passed：11核心/14窗口/2466B/823指令/61厂商字/247静态检查**。脚本核完整连续边界、所有核心直接控制目标/调用图、关键读宽/flags/参数/几何原字节、C22caller及交集原字节一致、元数据和表端点；另人工逐条阅读本轮原指令，核递归重读、callee参数、点顺序、机器返回和无指针持有。检查初版曾把caller窗口外合法跳转误纳入“必须窗内”断言，已限定为完整核心函数；表端点初始预期32767由ROM实际32768纠正，报告保留原值。这是分析脚本修正，不是固件缺陷调查。

没有运行固件、模型、历史回放、项目编译或测试，没有连接设备/外部服务、异常输入/漏洞/缺陷验证，没有修改ROM、生产代码、安全检查、构建或模型。未自称独立技术验收；待新agent复核。

任务问题已在正常调用范围内闭合，限制/断边按类别保留：

| 类别 | 精确边界 |
| --- | --- |
| 坐标 | 已解四word→四点→逐链变换→写回及交集；真实面板/最终显示坐标、`a00ddc7e`后提交仍未解 |
| 算术 | 整数低32位、signed DIV/ASR和表已解；无浮点ABI断边；表生成方式、原数学源码/版本未知 |
| 依赖 | 正常非空11核心无不透明依赖；c658空对象诊断a008b51a/a0019672、其他property/group及其上游设置不在本正常闭包 |
| 指针持有 | 本闭包不持久保存借用指针已核；obj+4/aux/style/descriptor的生产释放和外部串行化未知，不能据同步使用宣称全生命周期安全 |

一个后继闭包建议：由新的独立agent复核本G01的11核心及两处caller合同，重点+1且无-1、flags=1递归顺序、aux重叠位域、取值ID/缺省、32位截断/ASR与变换返回被忽略。复核以本轮原字节和保留历史extent为入口，不重做全门控，不接管整个style/变换库或物理刷新。


提交操作记录：首次明确四个独占文件的git add因主仓库.git/worktrees/re0041-g01/index.lock写权限被拒；按既有本地提交授权申请Git元数据升级，不改权限、不绕过限制。
