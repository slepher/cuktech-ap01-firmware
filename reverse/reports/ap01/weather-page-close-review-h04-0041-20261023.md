# H04：天气页确认键离页与 DELETE 所有权独立复核

2026-10-23；分支 `codex/re-0041-h04`，基线 `2ac1fd0aa25b00863e860cd6fc20892916cc2295`。使用 reverse-engineer-anything 技能。新 agent 独立复核 [H03](weather-page-close-h03-0041-20261023.md)，读取共同规则、H04 完整任务书及 [H02](weather-lifecycle-review-h02-0041-20261023.md)。

**裁定：H03 正常 type0x19 确认键离页→父/子 DELETE→控件递归→class 析构/摘链/free 的指令合同，限定接受，无核心语义纠正。116 B context 的最终释放仍未核；原报告保留该断边正确。** 这是条件正常路径的静态恢复，不是事件安装、主页面显示或全部堆回收已经实际成功的证明。

## 原件、独立方法与范围

只读原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，沿用既有身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；地址映射 `offset=VA-0x9ffff000`。没有新增散列清单或复制工作区。

本轮新写 [review.py](../../analysis/weather-page-close-review-h04-0041-20261023/review.py)，直接重读 ROM，用 Capstone 5.0.7 解码 RV32/RV32C，另按原 word 自行核 JAL、I/S 型访存、常量与厂商位域。没有运行或导入 H03/H02 verifier，也未将其汇编文本当作新解码输入。没有打开/切换共享 REA target 或数据库；技能用于证据和边界纪律，本轮使用隔离本地只读分析。

[review-evidence.json](../../analysis/weather-page-close-review-h04-0041-20261023/review-evidence.json) 保存 **21 个范围、1905 条解码覆盖、187 项检查、10 条关键厂商字、5 条只读 profile 规则、class 表和构造根引用索引**。[review-disassembly.txt](../../analysis/weather-page-close-review-h04-0041-20261023/review-disassembly.txt) 保存本轮独立解码的合同窗口与原字节；完整构造的中间控件装配只保留 context 根寄存器引用，避免机械复制整段无关构造。完整 822 条构造仍在每次运行时解码、索引。新补核 `a00b3666→373e/3740→37ca` 的确认键分支衔接，以及 `a00b2f7e..2f86` 的 window class 参数。

不新造 REA Evidence ID。H03 留存的历史 REA `ev_6902d9aeda43e6ba929e27d5b84e3a8070273c6287e4a0c7c358de90fac24baf`、`ev_cbd4287ff839b53d9291e0aa4beeb3f46cf0a02dd1b36665e4f15334df3b4bfc` 只是被复核报告的来源；本轮裁定依据为直接读取的原指令和下述检查。

## 按 H03 核心清单逐项裁定

| 合同 / 核心入口 | 判定与独立依据 |
| --- | --- |
| `a00afc88` 中 `a00b14cc..15b1` 装配 | 接受。`14dc→a00b2f6c` 得 W；`14e2` a0=8，`14e4→a008e362` 得 S；`1518/151a` 以 W 创建天气 P。`1534/1538` 是 S+2/S+6 的 byte，`156a` 是 W+0x10 的 word。`1558..1566` timer `(a00b59c4,1000,P)`；`157e/158c/159a` hook filter=0x11/1/0xb、userdata=0；`159e..15ae→07c4` DELETE hook `(W,a00b1a02,0x29,timer)`。不能混淆两处 userdata。未检查安装返回。 |
| `a00b35ee` 确认键分支 | 接受。event+0→W，W+0x10→S；code 清 bit15 后比0x11，先置 `62fc403a=1`，`a00a769a()!=0` 返回。getter 的 key=10 由 `3666` 排除19、`3740` 排除20后进入 `37ca/37cc`；W+0x64 LBU 非零则先清再返回，S+2 LBU 必须0x19。`3904` a0=s1=W，`3906` JAL 恰为公共删除 `a00ded6c`，未检查其返回。 |
| `a00b1a02` 父 DELETE | 接受。event+4 为 W，event+12 为 timer。S=LW(W+0x10)，S空或timer空均只日志返回；timer非空才 `1a70→a008ae58`，`1a74` a0=s2=S，`1a76→a008ab8a`，`1a7a` 清 W+0x10。free 的是 S8。不能把timer空的原失败臂补成free(S)。 |
| `a00ded6c` 公共删除 | 接受。先查 obj+0x2a halfword bit12，已置位则返回；保存父对象和根显示信息，`dedac→a00dcf52(obj)`，随后仅对仍存活且非删除中父对象做原更新并发0x2a/0x2c；根对象另清 display+0x2c8 条件引用。不把它当class析构walker，调用方不依赖数值返回。 |
| `a00dcf52` 删除核心 | 接受。halfword bit12先置位，再发送 `(obj,0x29,0)`。发送结果恰0才清bit12退出；非零才继续。清事件list后反复取 `a00dcee4(obj,0)`，`dd044` C.JAL 真实递归回 `dcf52`，再重读首子对象。输入/待删除记录清理后 `dd000→a00d7806(obj)`，随后从父children或display数组移动尾项、更新计数/resize，最后 `dd03c/03e` free(obj)。 |
| `a00d831a` 同步发送 | 接受。48 B 栈帧，事件 current/target/code/userdata/param/previous/flags 见下。低3 flag 清零，不是全事件清零；栈事件压到 `62fc95e8`，同步 `8358→8234`，`835c/8364` 恢复 previous 且不覆盖 a0。因此返回dispatcher状态；obj空直接1。 |
| `a00d8234` dispatcher | 接受。pre list→class event→normal list；前一阶段状态必须1，flags bit1 可停止后续并归一成功，bit0 导致相关分发返回0。class ABI=`class_event(class,event)`，descriptor ABI为单参，两者不能合并。父传播还受parent、flags bit2、对象flag和码位图控制；DELETE不冒泡，详见原字。 |
| `a008acfa` descriptor 分发 | 接受。list空返回1；先保存20 B list视图及其旧busy位，置busy，循环按原count取descriptor。cb空、filter bit16、bit15不匹配均跳过；清bit15后filter0匹配全码，否则等event.code。`ad92` 写event+0xc，`ad90/96/98` 以 event 为a0间接调用。callback数值返回被随后LBU覆盖，实际读取event.flags；原清理/旧busy状态分支保留，不能将free/callback数值当成功门。 |
| `a00b3b26` 天气 DELETE | 接受，H02针对核。event+4→P，P+0x10→B，B+4→C；B空直接返回，未新增C非空门。清28word的原偏移序见下；`3bca` 同键注销、`3bce` a0=s2=B、`3bd0` free(B)、`3bd4` 清P+0x10。不是free(C)。 |
| `a00d7806` class 析构 walker | 接受。取obj.class+8，非空则 `dtor(class,obj)`；回调返回后重新读取obj.class与base，base非空写回obj.class再递归。该函数自身没有对象数组摘除或free(obj)，这些属于删除核心后段。 |
| `a00d87d0` base class 析构 | 接受。先遍历当前事件链，current/target等obj时置flags bit0；再按原序调用样式/组等helper。显式free实参为 `LW(LW(obj+8))` 和 `LW(obj+8)`，中间重读extra并清字段/清list，最后清obj+8；从未显式以obj+0x10取C。opaque helper内部不作全局否定。 |

必要短依赖也有原字核验：key getter `a00d8af6` 的原code必须恰0x11才读 `*(event.param)`，param空返回0；`a00dcee4` 用extra+0x30无符号halfword计数及厂商word索引；`a01ad654` 保存三参，确保extra后将extra+8交给registry；`a01b9432/9438/943a` 写 `{cb@0,filter@8,userdata@4}`。`a00b1df8(class,W)` 先条件删除W+0x60 timer，再恢复W+0x2c相关输入组、处理W+0x30对象；该timer与父DELETE event.userdata的timer是不同字段来源，未证明相等。

## 决定性原字、ABI 与布局

`a00b3878` 原字节 `0b1af540`，word `0x40f51a0b`，字段 `(op=11,f3=1,rd=20,rs1=10,rs2=15,high25=32)`；只读 `ap01thead2.sinc` 的确切 `th.mveqz` 规则为rs2==0才复制rs1。因此遍历顶层子项时，`child+0x3c-1==0` 才更新s4，循环不提前退出，留下**最后**一个匹配。第二层从index0开始，首次 `wrapper.type32==4` 取wrapper+4后退出；找不到时的0值保留，不能增添空值门。

主页面更新两次 `a01b2086` 的前三参数均 `(匹配page,wrapper+4,a00a5c94返回)`。`38ae..38ca` 先从原栈字段读取零扩展byte及halfword，第一次sp+8=1；`38d8..38f4` 在第一次调用后重读相同字段，第二次sp+8=0。`a00a690c/a00a68a8` 提供栈字段块的内部以及主页面更新器本身沿用外部合同，没有由日志推断其实际绘制或返回成功。

`a008ad78` 原字节 `8bb6f73c`，word `0x3cf7b68b`，extu的msb/lsb都15，即取filter bit15为0/1，与preprocess相等才交付。DELETE filter=0x29，bit15=0，进入normal阶段。`a00d8300:37a71858` 的LUI和 `8308:4517` 的C.ADDI构造 `0x58189ff1`；`0x29-0x16=19`，bit19=1使 `830c` 跳回返回，**不执行 `830e` 的current_target=parent**。因此父hook由父对象独立DELETE触发；不能解释成子天气DELETE冒泡到了父。

`a00dd0e0/0ee/134` 和child getter中的lrw均核了shift=2；`dd0f2/138` 为addsl shift=2，随后向前一个word存储，保证析构后的数组移位仍是4 B指针。`dd102` 是extu15..0，父child计数的LHU/SH与原有signed BLT保留，未把所有比较泛化为unsigned。只读profile提供既存解码规则，不等同厂商原C源码或精确开源版本认证。

```c
// RV32分析视图，非原C声明；未核字节不补用途。
Window W: class@0, parent@4, extra@8, state8_ptr@0x10,
          prior_group@0x2c, related_obj@0x30, timer2@0x60, gate8@0x64;
State S:  allocation8; type8@2=0x19; scroll8@6;
Page P:   class@0=a0263ef4; extra@8; wrapper_ptr@0x10;
Wrapper B: allocation20; type32@0=0x19; ctx_ptr32@4=C; other12_unknown;
Context C: allocation116; controls32[21]@0; rows32[7]@0x54;
           state8@0x70; tail3_unknown;
Event e: current@0, target@4, code32@8, userdata@0xc,
         param@0x10, previous@0x14, flags8@0x18; // 栈视图尾padding
Descriptor: cb@0, userdata@4, filter32@8;
```

`a00b2f7e/2f82` 真实构造class参数为 `a05647fc`，其base=`a0263ef4`，dtor=`a00b1df8`；天气factory前缀class=`a0263ef4`，其base=0，dtor=`a00d87d0`。这些确定的class链不含自定义context析构项。

## 复核后状态与所有权伪代码

以下保留原指令顺序；helper合同不代表原实现已全量恢复。

```c
enter_branch(e) { // a00b35ee中的正常key10分支
    W=e.current; S=LW(W+0x10);
    if ((e.code & 0xffff7fff)!=0x11) return;
    SB(0x62fc403a,1);
    if (a00a769a()!=0) return;
    key=a00d8af6(e);           // 原code==0x11，param非空才取word
    // 原19/20分支不进入本闭包；本分支只有10继续。
    if (key!=10) return;
    if (LBU(W+0x64)) { SB(W+0x64,0); return; }
    if (LBU(S+2)!=0x19) return;
    find_last_top_child_word3c_1_then_first_page_type4();
    a00a5c94_and_two_original_stack_field_providers();
    a01b2086(original_fields_reloaded,stack_flag=1);
    a01b2086(original_fields_reloaded,stack_flag=0);
    a00ded6c(W);              // 返回未判断
}

parent_delete(e) { // cb(event)，不能写成cb(class,event)
    if ((e.code & 0xffff7fff)!=0x29) return;
    W=e.target; S=LW(W+0x10); if (!S) { log(); return; }
    timer=e.userdata; if (!timer) { log(); return; }
    a008ae58(timer); a008ab8a(S); SW(W+0x10,0);
}

delete_core(obj) {
    if (LHU(obj+0x2a)&0x1000) return;
    SH(obj+0x2a,LHU(obj+0x2a)|0x1000);
    status=a00d831a(obj,0x29,0); // 同步栈事件：pre/class/normal
    if (status==0) { SH(obj+0x2a,LHU(obj+0x2a)&0xefff); return; }
    if (LW(obj+8)) a008b7f0(LW(obj+8)+8);
    while ((child=a00dcee4(obj,0))!=0) delete_core(child);
    input_and_pending_delete_record_cleanup_in_original_order(obj);
    a00d7806(obj);           // 每级dtor(class,obj)，随后重读class/base
    unlink_move_pointer_array_update_count_and_resize(obj);
    a008ab8a(obj);
}

weather_delete(e) {
    if ((e.code & 0xffff7fff)!=0x29) return;
    P=e.target; B=LW(P+0x10); if (!B) return;
    C=LW(B+4);
    for (off in original_order) SW(C+off,0);
    a00b3abe(a00b5cd4,P);   // 已验收同callback/page键首匹配注销
    a008ab8a(B); SW(P+0x10,0);
}
```

clear的原偏移序为 `18,30,40,38,04,0c,34,10,44,48,1c,20,3c,08,24,00,2c,28,14,4c,50,54,58,5c,60,64,68,6c`（十六进制），集合恰0..0x6c的28word；C+0x70及尾3 B保留。

事件安装和发送返回允许继续的正常路径中，S8先在父DELETE归还；之后递归到P时，C前112 B清零、订阅同键注销、B20归还、P+0x10清零；之后才继续P的child[0]递归、P的base析构/摘链/free(P)。W最后运行window/base析构并摘链/free(W)。窗口内其他子对象按实际child[0]顺序处理；没有证明天气P是W的第一个子对象，也不改变H03的限定顺序。

对象树的子指针由extra/children数组持有。C保存的控件地址清零不会清该对象数组，因此后续递归无须重读已清的C字段。当前event为同步栈借用，本条DELETE param=0；descriptor userdata交付前重写。天气刷新timer的userdata=P，父DELETE的userdata=timer，是两次独立注册。已核显式free分别为S、B、obj与extra内部指针，彼此不能替代。

## context 断边、来源及未核项

完整解码 `a00b821e..a00b8bfb` 的822条后，allocation根C保持在s2；普通 `SW s2` 唯一持久存储为 `8be2: SW s2,4(s4)`。全部直接s2引用中没有把它直接搬入a0..a7传callee的指令，`8818: ADDI s3,s2,0x54` 明确派生行数组指针。这个结果只限本函数根寄存器，既不覆盖callee逃逸，也不是全ROM别名穷尽。构造失败臂明确调用的是 `a00d7806` class walker；本轮不把它改名为公共删除/整个对象归还，也不开展失败行为验证。

独立查看所列正常离页、两个DELETE、dispatcher、删除核心、class walker及两个确定class析构后，显式free参数没有C。最终已知根链是 `P→B→C`，子DELETE在free(B)/清P+0x10处切断已知挂接；**C从成功alloc(0x74)到最终归还者的调用或间接安装仍未定位**。没有搜索全ROM所有free、全部UI类型/导航、全部opaque样式/输入/allocator内部，也没有运行时堆追踪。不能由此推出C必然常驻或作泄漏/缺陷判断。

原地址、字节、宽度、原序、返回门、显式free实参及class指针为事实；“确认键”由key10和H03已有原日志支持；恢复主页面这一业务解释由对象查找与两次更新调用支持。实际画面、定时器停止内部、registry实际占用、外部helper潜在别名和全部堆生命周期未证。

天气重排/主要显示/五槽注销只沿用H02已验收合同，并重新针对核子hook的清零/参数边界，没有重做全天气流。event/object机制与LVGL设计一致，但精确版本和未修改源码比对未建立；分配器、list/timer/样式/输入helper及厂商胶合均未以“标准库”名义排除，只保持明确未展开边界。

## 实际验证与后继

运行 `python reverse/analysis/weather-page-close-review-h04-0041-20261023/review.py`：**passed，1905条原件指令，187项检查**，含原调用目标、所有权根和实际free寄存器、三套结构、事件ABI/flags/bit19、两次主页面参数重读、厂商mveqz/extu/lrw/addsl、28word原序、class链及完整构造根引用边界。报告相对链接存在，`git diff --check`通过。没有执行固件/模拟器/设备/历史回放、外连、编译项目或修改ROM、生产代码、配置和分析器模型。

恢复程度：H03所要求的一条正常离页闭包及精确ctx断边得到新agent独立原字支持；接受范围不包含所有GUI删除、全部失败清理或ctx最终free。建议唯一后继为：从构造 `a00b8818` 的C+0x54派生行指针开始，选其实际持有/间接传出的一条有界链，判断有无第二context所有权根；若没有，明确停止于该链而不扩全ROM free扫描。
