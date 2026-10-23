# 0041 G04：失效提交、合并和直接消费独立复核

结论：**有两处事件分派机器表达纠正后，限定接受 G03。** 主要区域合同成立：提交写 display 内嵌 32×16B 区域值；mode2 写 full/count=1；普通路径 event35 必须恰返回1，之后才读 count；包含则省略、满32则退 full；event38 的 param 为0。直接消费者按交叠和 unsigned 低32位面积严格小于条件合并，标记而不缩 count；mode1/2 直接借记录、mode0 借本帧分行区域；最后依次清512B、32B、word count。没有动态失效区域节点队列，也没有证实最终显示完成。

纠正仅在本报告生效，不改 G03：filter 比较是 `filter & 0xffff7fff`，不是“低15位”；bit0 的返回必须按检查位置区分，不能统一说“bit0 停止返回0”。回调后的 bit1 停止归一返回1，原掩码2不作为返回值。这些纠正不改变提交 `event35(...) == 1` 的原门；安装的实际 callback/filter、param 是否被保留和 event38 如何触发消费者仍未验收。

## 范围与独立证据

分支 `codex/re-0041-g04`，固定基线 `f82380b91fd0eb84d933d49414a2a32dd91b9ea2`。已读用户原始粘贴请求、管理共同规则/G04完整任务书、[G03](invalidation-submit-g03-0041-20261023.md)、[C22](region-gating-review-c22-0041-20261023.md)、[G02](region-transform-review-g02-0041-20261023.md)及 REA 技能/native guide；本树未见 AGENTS.md。只写本报告和独占 analysis 目录，不开下级 agent，不改主树/其他树/共享索引。

本轮新写 [review.py](../../analysis/invalidation-submit-review-g04-0041-20261023/review.py)，不导入或执行旧验证器。只读主仓库 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA-0x9ffff000`。普通指令 Capstone 5.0.7，按原半字低位决定2/4B宽度；分支/JAL/RVC跳转目标独立拆立即数，厂商字独立拆字段，再读本地只读 `ap01thead2.sinc` 文本作语义依据。未打开/切换任何共享 REA target/数据库，未执行厂商模型。

[instructions.txt](../../analysis/invalidation-submit-review-g04-0041-20261023/instructions.txt) 为重新从 ROM 提取的地址、偏移、原字节、普通解码/厂商字段及直接目标；[evidence.json](../../analysis/invalidation-submit-review-g04-0041-20261023/evidence.json) 保存18窗口、3776B、1262指令、29厂商字、120项关键字段/控制目标检查和实际使用模型原文。数目表示静态工具覆盖，不是语义结论数。不新增哈希清单，不复制 ROM，不以历史伪代码代替证据。

12个核心合同和必要短依赖如下。连续窗口完整取字节不代表窗口内所有业务已恢复。

| 地址（末端不含） | 本轮独立核查 ABI / 范围 |
| --- | --- |
| `a00ddbf6..a00dddf4` | a0=obj、a1=requested area；前段针对核 C22，dc7e 后完整提交流 |
| `a0080e3e..a0080e6c` | a0=display或0，a0=width word；默认回退及 rotation 选择 |
| `a0080e6c..a0080e9a` | 同上，height；与width相反的维度选择 |
| `a008b43a..a008b456` | a0=dst、a1=src，按0/4/8/12四word顺序复制 |
| `a00894aa..a008954c` | a0=inner、a1=outer、a2=radius；接受本路径 radius0，非零圆角子流程留边 |
| `a00814f4..a0081554` | a0=display、a1=event、a2=param；本帧event、两phase、最终分派返回 |
| `a008acfa..a008adf4` | a0=list、a1=event*、a2=phase；descriptor选择、callback(event*)、标志/返回/清理 |
| `a0089472..a00894aa` | a0/a1=area*，signed交叠，边相等算交叠，0/1 |
| `a008928c..a00892ac` | a0=area*，a0=低32位面积 |
| `a00e0ac8..a00e1294` | a0=timer或0；取display、合并、直接消费/清空；其他buffer/list业务不作整体验收 |
| `a000589c` 的16/20B对齐路径 | a0=dst、a1=src、a2=n；内嵌值/事件list快照复制，无地址持有 |
| `a0024906..a00249c4` 的对齐零填充 | a0=dst、a1=0、a2=len；只接受本闭包28/32/64/512B路径 |

额外短依赖为 `a0080d8e` 零填充包装、`a008ac38..a008acfa` 列表清理、`a00ecd68..a00ecd76` vector正常slot续接、`a00ddbe4..a00ddbf6` 第三门尾部。`a00ddc7e/a00ddd90/a00e105e/a00ecd68` 均不能另立为函数起点。allocator/vector整体、radius非零、绘制本体没有因疑似开源排除，只保留精确边。

## 逐项裁决

| G03项目 | G04裁决与独立原指令依据 |
| --- | --- |
| 第三门成功连接后段 | **接受**。`dc76`调用 `a00ddab4`，`dc7a`零到 `ddd82`；第三门尾 `dbe8`搬s3到a0。既有变换/数学仅承接 C22/G02，未重验全部style。 |
| 扩张、重新取display | **接受**。`dc7e`重读obj+8，`dc82`LHU(aux+0x32)，mask0xc00恰0x800才以5/5调expand；`dca2`再次getter，`dcae`默认回退，`dcb6`再查门。不是缓存前门结果。 |
| 渲染门/全屏/格式 | **接受**。`dcbc/dcc0`取u16&0x400，零才`ddd06`；full在s0-64，clipped在s0-48，入口副本s0-80。`ddd08/0c`先零low，两个getter-1写high；intersect后只格式byte7把x1&-8、x2|7，不再裁剪。诊断终止callee不补造return。 |
| mode2全屏 | **接受**。`ddd58/5e`比较byte模式2；`ddd64`传full，不是clipped；`ddd6c`copy16，`ddd70/72`SW count=1，`ddd76/78/7e`event38/param0。没有event35或包含扫描，也没清旧joined。 |
| 普通event35恰1及重读 | **接受**。`ddd90/94`传可写clipped/0x35；`ddda0=e311f5fe` BNE(a0,1)退出；之后`ddda4`才LW count。追加定位`dddbe`、copy后`dddce`再次LW count，不能折叠成snapshot。 |
| 包含消重/容量/追加 | **接受**。contains四项signed比较，radius0在`94f8/94fa`直接1；命中`dddea`退出不发event38。`dddb2`BGEU(31,snapshot)；否则SW count0并选full；四wordcopy→重读+1→SW count→event38。扫描索引`dddee`截u16，容量不是halfword字段。 |
| 无动态区域队列/返回 | **接受**。提交只算`display+44+16*count`、copy和SW，没有区域节点分配。公共尾`ddd82..8e`不写a0：不能统一为成功/失败，包含可返回1、提交留最后event结果。 |
| 事件间接ABI | **接受**。event28B清零后+0/+4=display、+8=code、+0x10=param；`ad92`写+0xc userdata，`ad98`以a0=event* JALR descriptor.callback，回调返回寄存器不直接作分派结果。 |
| filter的“低15位” | **纠正1**。`ad42=e17a`构造s5=0xffff8000，`ad50=fd1a`减1得0xffff7fff，`ad80=b3f75701`AND。因此比较值是清bit15后的**32位**filter，其他高位没有在此被截断。bit16先独立跳过、bit15匹配phase仍接受；“低15位零/等code”仅在其他高位已知为0的额外前提下等价，本轮没有注册值域证据可加该前提。 |
| bit1停止/bit0返回 | **纠正2，细节见下节**。回调后bit1优先，经`adae`归一1；入口bit0返回0，回调后仅bit0返回0；`ad56/5a`循环头bit0命中却留下s1=1并到退出，所以不能对所有位置作统一bit0→0结论。 |
| unsigned面积严格小于合并 | **接受**。overlap用signed比较；union四个SLT+MVNEZ为signed min/min/max/max；面积MUL低32位、两面积ADD低32位，`0dfe=637b2a01` BGEU不满足严格小于即跳过；先copy4覆盖i，再`0e10`SB joined[j]=1，不减count。 |
| 消费循环/借用 | **接受**。主计数门`0d08`为signed BLT，每轮重读count；joined跳过；mode1/2经`121e..1242`给内嵌area地址及a1=0；mode0读四word后构造s0-128本帧块，`1148/11fc`交a00e082e，返回后调a00dc39e再继续。 |
| mode1链副本/复位 | **接受到边界**。仅mode1且相关buffer非零进入`1244..1282`，未标记项调a008af14并copy16到返回存储；这是另一list副本。`0d40`零512B→`0d4e`零32B→`0d54`SW count0。链副本未由这三步释放。 |

表内 dc/dd 地址前缀为 `a00d`，14/15/ac/ad/92/94 为 `a008`，0c/0d/0e/10/11/12 为 `a00e`；完整地址和原字节在新 instructions。模式/矩形功能名是机器布局解释，不是源码类型认证。

## 两处纠正的精确替代合同

事件 descriptor 三word为 callback/userdata/filter。过滤实际依序为：callback空跳过；`filter & 0x10000`非零跳过；extu(filter,15,15)必须等phase；`match=filter & 0xffff7fff`，match非零必须等event+8，零则不过滤。不能把`match`写成`filter & 0x7fff`。这项纠正影响未知安装filter的精确匹配合同；不证明已安装某handler的行为改变，也不猜测未知高位的用途。

事件返回使用callee-saved s1，末尾 `add8`搬到a0。标志来自 **byte[event+0x18]**，不是把callback a0或完整标志掩码透传：

| 检查位置 | 原流及返回 |
| --- | --- |
| list为空 `ad14→adf0` | 明确s1=1，返回1；此检查先于event bit0读取。 |
| 入口 `ad16..ad1e` | 非空list且bit0置位，先s1=0，直尾返回0。 |
| 每次取slot前 `ad56..ad5c` | `s1=flags&1`；非零到ada8。原list原先busy则直尾，否则ac38(snapshot)后尾；s1仍为1。因此这里的bit0退出是1。 |
| callback后 `ad9a..ada2` | 重读flags；s1=flags&2，非零跳adae后改为1；后续busy/清理路径也归一1。包含bit0同时置位的情况，bit1优先。 |
| callback后仅bit0 `ada4..ada8` | 前一个AND2已把s1置0；bit0非零不继续，清理后仍返回0。 |
| 正常遍历完 `ad52→adae` | 置1；原不忙且bit0为0时清busy/acc6，最后adf0再置1；需要snapshot清理时保留1。 |

循环头bit0分支的**控制路径事实**成立，但本轮未证明实际安装的正常handler能使它命中。仅在同步callback改变flags、且没有其他对event写入的简化闭包中，回调后的检查已经抓住bit0，或bit1停止本次迭代，不会把新bit0带到下一轮头。不能把这一可达性条件抹除后声称发现某个正常系统触发，也不能为了原概括而删除机器存在的分支。实际callback安装/重入/外部持有未核。

对提交主链的影响：wrapper先phase1，只有结果恰1才phase0；bit1返回1允许第二phase，不等于取消整个事件。phase0结果或首phase拒绝结果原样返回。`ddda0`仍只接受1；因此不能将提交门改成“非零”，不能把bit1原掩码2拿去解释为拒绝，也不能对未安装handler预判通过。param在event+0x10同步传入；以上过滤/停止纠正不会将param复制为长期对象。分派器本身只在本帧保存param；未知callback是否另存它仍是断边。

## 布局、伪代码、状态与所有权

机器布局：area={s32 x1,y1,x2,y2}，16B；display+0/+4为尺寸word，+0x3c flags byte，+0x3d mode byte，+0x3e被LHU/SH的状态位，+0x40格式byte，+0x44..0x243为32个area值，+0x244..0x263为32个joined byte，+0x264 word count，+0x26c为另一list，+0x2e8事件list。宽高选择依 `(word[d+0x300]&5)==1` 交换两个word；不能只凭名称断定固定物理方向。

下面是受边界限制的整理伪代码，不是原源码或可执行重建；W表示低32位。getter、事件及各循环处机器会按上表重读，`D()`表示从62fc958c重新取当前display，不能改成全函数恒定指针。

```c
// submit: C22/G02成功后，从dc7e继续
if (obj.aux && (u16(obj.aux+0x32)&0xc00)==0x800) expand(local,5,5);
d=get_display(obj); if (!d) d=word_at_62fc9590;
if (!d || !enabled(d)) goto tail;
u32 i=u16(d+0x3e)&0x400;
if (i) opaque_diagnostic_and_terminal(); // 不补造统一返回
Area full={0,0,W(width(d)-1),W(height(d)-1)};
if (!intersect(&clipped,&local,&full)) goto tail;
if (u8(d+0x40)==7) { clipped.x1&=-8; clipped.x2|=7; }
if (u8(d+0x3d)==2) {
    copy16(d+0x44,&full); word(d+0x264)=1;
    event(d,0x38,0); goto tail;
}
if (event(d,0x35,&clipped)!=1) goto tail;
u32 n=word(d+0x264);
for (;i<n;i=(i+1)&0xffff)
    if (contains(&clipped,d+0x44+16*i,0)) goto tail;
Area *src=&clipped;
if (n>31u) { word(d+0x264)=0; src=&full; }
copy4(d+0x44+16*word(d+0x264),src);
u32 after=word(d+0x264); word(d+0x264)=W(after+1);
event(d,0x38,0);
tail: /* epilogue不重写a0 */

// consumer: 其他buffer/list操作仍存在，以下只表达记录算法
for (u32 i=0;i<D()->count;++i) {
    if (D()->joined[i]) continue;
    for (u32 j=0;j<D()->count;++j) {
        if (D()->joined[j] || i==j) continue;
        Area *a=&D()->area[i], *b=&D()->area[j];
        if (!overlap(a,b)) continue;
        Area u=signed_union(*a,*b);
        if (u32(size(&u)) < u32(W(size(a)+size(b)))) {
            copy4(a,&u); D()->joined[j]=1;
        }
    }
}
// event3b、设render位、按索引跳joined；主索引比较为signed
// mode1/2: a00e082e(&D()->area[k],0)
// mode0: 构造本帧分行area，a00e082e(&stack_area,y_offset)
// 各绘制call后a00dc39e(D())；event3c后清render位
// 如模式1且相应buffer存在，先将未标记area复制到+26c链
zero(D()+0x44,512);
zero(D()+0x244,32);
D()->count=0;
```

合并没有在成功后重启j，也不压缩记录；因此不等价于全局最小覆盖。外层/内层合并比较为unsigned，绘制主索引比较为signed；不能以同一C循环类型把两者规范化。提交与消费者有多次display/count读取；本轮没有串行化/锁的完整证据，不据此作并发修复。

所有权流：请求者area→入口16B副本→full/clipped本帧值→event借clipped→复制16B到display内嵌记录→消费端就地union覆盖/标记→绘制借内嵌area或本帧分行area→可选mode1链副本→内嵌区域清零复用。提交端没有把栈地址作为记录值保存；copy4与16/20B对齐复制路径只读写word，均不持有指针。event descriptor快照/删除清理是另一资源；a008ac38压紧/调用a008ab8a及vector shrink不等于free(area)。mode1链副本最终归还没有被内嵌清零证明。

绘制callee `a00e082e` 未进入，因此“借用”只说明 caller 传参来源，不保证callee跨调用不持有area。mode0的区域在本帧后续循环复用，mode1/2的记录最终被上述清零；真实callee持有合同仍须后继恢复。`event38(display,0)` 与 `a00e0ac8` 共用布局、不是已证实的调用/唤醒链。

## 原指令与来源边界

关键厂商字重新从 ROM 核：`dddee=0x3c09390b` 为extu(x18,x18,15,0)；`ad78=0x3cf7b68b` 为extu(x13,x15,15,15)；`0daa/0dbc/0dce=0x42c6970b`、`0de0=0x42d7178b` 为MVNEZ，结合前置signed SLT得到union极值。`1052=0x8127c70b` 是unsigned byte索引读joined，基址display+244、索引s2。n16/n20复制用 `5992=0x5845c70b` LWIA 与 `5998=0x5848570b` SWIA，postincrement4；n=16/20经word余数循环完成，不进入大块/未对齐路径。零填充通过包装a1转a2、a1=0，标准SW覆盖本轮对齐字节范围，最后不持有dst。

事实为原字节、字段宽度/符号、直接目标、实参寄存器/间接ABI、重读、写序及本轮限定返回流；功能解释如display、invalid area、joined由结构/调用和 G03 指向的本地ROM路径字符串支持。G03来源入口 `a0569c48` 的lv_refr.c路径、`a056a3a8` 的lv_inv_area、`a056a360` 的lv_display_refr_timer只辅助命名；**准确LVGL版本、原源码身份和厂商修改边界未认证**。未外连查源码，未因疑似libc/LVGL排除未知实现。

## 实际验证、未核与后继

实际运行新 `review.py`：**passed，18窗口/3776B/1262指令/29厂商字/120检查**。人工读取新listing的提交后段、width/height、copy4、radius0包含、事件wrapper/dispatcher及清理、overlap/size、消费者合并/记录交付/清理、复制零填充限定路径；按寄存器流核两项纠正。静态断言核指令宽度、存取偏移、厂商字段、关键直接控制目标。没有执行旧验证器、固件、设备连接、外部服务、异常区域/漏洞验证、历史回放、项目编译或生产测试。

**未核项**：实际事件注册callback/filter值域、callback对event/param的外部保存与重入；event38到timer消费者的安装/唤醒调度；a00e082e更深指针持有与具体绘制/物理完成；mode1链副本最终释放及整体buffer同步。a00e0ac8的其他buffer/list分支有原字节留证，但不宣称全部语义验收。C22/G02只接受所需调用边，不重开全部style/变换。

建议一个后继闭包：**display事件descriptor真实安装→本链event35/38实际handler→param持有/返回→event38到a00e0ac8的具体调度连接**，约5–12核心及必要短依赖。当前只定位精确边，不能预设handler地址或称事件38已异步刷新；不将后继扩成全事件系统、绘制栈或所有注册/恢复安装。
