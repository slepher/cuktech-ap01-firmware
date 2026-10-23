# H03：天气详情页正常离页、DELETE 交付与 context 断边

2026-10-23；分支 `codex/re-0041-h03`，基线 `dcc2a0889e5f7c83f652de0d1aea6a968f4107e8`。使用 reverse-engineer-anything 技能，承接 [H01](weather-subscriber-lifecycle-h01-0041-20261023.md) 和 [H02](weather-lifecycle-review-h02-0041-20261023.md)，仅静态读取 0041 原件。此结果待新 agent 独立技术复核。

**结论：已连接一条实际“确认键离页→父窗口删除→天气子页 DELETE→wrapper 清理→子控件递归删除”路径。0x74 B 天气 context 的最终释放仍未证实。** 新证据区分出三个业务堆对象：父窗口的 8 B 状态、天气子页的 20 B wrapper、116 B context；父 DELETE 的 `free(state8)` 和子 DELETE 的 `free(wrapper20)` 均不能替换为 `free(ctx116)`。

## 范围、原件和证据

原 ROM 只读路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，沿用身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；`file_offset=VA-0x9ffff000`。没有重建散列/复制清单，没有切换 REA 全局 target、打开共享数据库、修改模型或原件。

[instruction-evidence.json](../../analysis/weather-page-close-h03-0041-20261023/instruction-evidence.json) 是本轮主证据：直接从 ROM 重新读取原字节并解码，保留地址、文件偏移、字节、19 个有界窗口共 1025 条指令、194 项检查、关键厂商字位域、class 指针和三条业务日志字符串。[verify.py](../../analysis/weather-page-close-h03-0041-20261023/verify.py) 与 [rom_inspect.py](../../analysis/weather-page-close-h03-0041-20261023/rom_inspect.py) 可复现；另完整解码构造函数 822 条指令，仅留 context 根寄存器的引用，避免复制无关控件构造。

历史 REA 只用作入口定位与对照：[retained-functions.json](../../analysis/weather-page-close-h03-0041-20261023/retained-functions.json) 保存 `a00b35ee` 的 `ev_6902d9aeda43e6ba929e27d5b84e3a8070273c6287e4a0c7c358de90fac24baf` 和 `a00afc88` 的 `ev_cbd4287ff839b53d9291e0aa4beeb3f46cf0a02dd1b36665e4f15334df3b4bfc`，来自主仓库 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json`，profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。旧 profile 的反编译不是本轮厂商语义的依据。既存 [delete ABI](../../analysis/screen-host-delete-abi-20261020.json) 的三个函数仅作历史定位；没有执行该报告涉及的历史验证。

## 一个真实离页动作如何到达天气页

`a00afc88` 是一个大事件处理器，本题只恢复其 `a00b14cc..a00b15b1` 天气临时窗口装配片段，未接管整个函数：

1. `14dc` 调 `a00b2f6c` 得到外层窗口 `W`；`14e2/14e4` 分配 8 B 状态 `S`。`1518/151a` 用 `W` 调 `a00b821e` 创建天气子页 `P`。
2. `1532/1534` 写 `S+2` byte=`0x19`，`1538` 清 `S+6` byte。这个 byte 型页面状态与 `P.wrapper.type32=0x19` 是两个不同位置，不能合并成一个结构。
3. `153c/1544` 经 `P+0x10→wrapper+4` 取得 context，`1554` 初次显示消费。`1558..1566` 注册 `a00b59c4`、周期1000、userdata=`P` 的 timer；这里仅记录 timer 身份/所有权接口，不重复 timer callback 或天气显示。
4. `156a` 写 `W+0x10=S`。`157e/158c/159a` 将 `a00b35ee` 安装到 `W` 的 `0x11/1/0xb`；`159e..15ae→a00b07c4` 为 `W` 安装 `a00b1a02`、码 `0x29`、userdata=刚得到的 timer。`07c4` 是共享安装尾部，不能另称新的构造函数。

`a00b35ee(event)` 以 `event+0` 取当前接收对象 `W`，以 `event+8 & 0xffff7fff` 取事件码。确认键离页实际门控为：

- 事件码 `0x11`；先写 `62fc403a=1`，调用 `a00a769a()`；返回非零便返回。
- `a00d8af6(event)` 返回10。该 getter 只在原事件码恰为 `0x11` 时读取 `event+0x10` 指向的 word，否则记录日志并返回0；参数指针空也返回0。日志 `a05604f0` 明写 `key enter`，支持“确认键”名称。
- `W+0x64` byte 若非零，先清该 byte 后返回；只有为0才继续。`S+2` byte 必须为 `0x19`，否则返回。
- `383c..3890` 从 `a008184e()` 返回对象的子项中寻找 `child+0x3c==1` 的项（循环持续，留下最后一个匹配）；再在该项子页中找 `page+0x10→type32==4` 的首个项，取其 wrapper+4。循环结束可留下0；原件没有为这些结果新增非零门。本报告所称正常恢复分支是存在相应项的路径，不假造全局必有匹配。
- 取 `a00a5c94()` 返回值和 `a00a690c/a00a68a8` 写入的两个栈字段块，按原序调用 `a01b2086` 两次；首三参数分别是找到的页面、其 wrapper+4、上述返回值，后续字段从栈逐次重读，两次 `sp+8` 参数分别1、0。未重新恢复这个主页面消费者，不把其返回当作导航成功检查。
- `a00b3904` 的 `c.mv a0,s1` 将原外层窗口 `W` 放进 a0；`3906` 的 JAL 真实目标是 `a00ded6c`。返回未检查。字符串 `a0560554="ui wx1 dtl1: key enter\n"` 和 `a0561fac="j_win_ui_wx1_dtl_event_custom_handler"` 与该分支身份一致。

厂商关键字 `a00b3878: 0b1af540 / word 0x40f51a0b` 是 `th.mveqz s4,a0,a5`，字段 `op=11,f3=1,rd=20,rs1=10,rs2=15,op2531=32`。因此只有 `child+0x3c-1==0` 才更新候选，不能采用旧反编译的无条件赋值或臆测另外的比较。

## DELETE 是怎样同步交付的

| 核心入口 | ABI / 本题职责 |
| --- | --- |
| `a00afc88` 的选定装配片段 | 建立 `W/S/P`、注册父输入与 DELETE；不恢复其余导航 |
| `a00b35ee..a00b390f` 的前缀/确认键分支 | `a0=event`；上述门控后调用公共删除；其他方向滚动只作边界 |
| `a00b1a02..a00b1a81` | 父 DELETE，读取 event+4 的 W 和 event+12 的 timer |
| `a00ded6c..a00dee1d` | `a0=obj`；公共删除入口，调用核心后向活父对象发0x2a/0x2c；调用方不消费返回 |
| `a00dcf52..a00dd143` | `a0=obj`；删除标志、发送0x29、结果门、递归子对象、class析构、摘链/free(obj) |
| `a00d831a..a00d836f` | `a0=obj,a1=code,a2=param`；构造栈事件，压入当前事件链，同步分发后恢复前链；返回分发状态 |
| `a00d8234..a00d8319` | `a0=event`；pre list→class event→normal list→有条件父传播；状态/事件flag门 |
| `a008acfa..a008adf3` | `a0=list,a1=event,a2=preprocess`；过滤 descriptor，写 event userdata，间接调用 `cb(event)`；不使用callback数值返回 |
| `a00b3b26..a00b3be5` | 天气 DELETE，沿用 H02 清ctx字段/同键注销/free wrapper 合同 |
| `a00d7806..a00d7831` | `a0=obj`；按 class+8 调 `dtor(class,obj)`，再把 obj.class 换成 base class 递归 |
| `a00d87d0..a00d885f` | base class 析构；标记活跃事件对象已删除、清对象内部资源，具体见下；不推定ctx释放 |

必要短依赖是 key getter `a00d8af6`、子项查询 `a00dcee4`、event安装 adapter `a01ad654`、descriptor 写入 `a01b9432..943b`、外层 window class 析构 `a00b1df8`；分配/释放、输入设备/定时器、主页面更新保持明确的外部合同，不展开全 GUI。

`a00d831a` 用48 B栈帧建立如下 28 B 事件视图（尾部保留padding；只清flags低3位，不伪造全栈清零）：

```c
struct EventView {
    Address current_target; // +0，初值obj；父传播可改
    Address target;         // +4，初值obj
    uint32_t code;          // +8
    Address user_data;      // +0xc，初值0；每个descriptor交付前重写
    Address param;          // +0x10
    Address previous;       // +0x14，保存62fc95e8原值
    uint8_t flags;          // +0x18，低3位清0
};
```

`a00d833a/833e/834a/834e/8352/8346` 的 SW 分别建立上述六个word。`8356` 将栈事件挂入全局链，`8358` 同步调用dispatcher，`835c/8364` 恢复 previous；这些恢复指令不覆盖 a0，因此上交dispatcher状态。obj=0的短分支返回1。

`a01ad654` 保存 callback/filter/userdata，确保 obj+8 结构存在，再以 `obj+8+8` 为 list 传 `a01b93b4`。descriptor 明确是12 B：`cb@0,userdata@4,filter@8`；`9432/9438/943a` 为三次原存储。注册是否实际成功并无上层检查，不声称运行时已安装。

dispatcher 正常序为 `a008acfa(list,event,1)` → `a00d81f8(0,event)` class事件 → `a008acfa(list,event,0)`。每段状态必须等于1且对应事件flags未要求停止/删除才继续。class事件以 `class+0xc` 查回调，ABI=`class_event(class,event)`；与 DELETE descriptor callback 的单参 ABI 不同。list为空视为成功。list delivery略过已标记 descriptor（filter bit16），filter bit15 必须等于 preprocess；去掉 bit15 后为0匹配所有码，否则与 event.code 相等。`a008ad78` 原 word `0x3cf7b68b` 是 `extu a3,a5,15,15`，并非有符号整型变换。天气/父 hook 的 filter `0x29` 的 bit15=0，因此进入 normal-list 阶段。调用前 `ad8e..ad98` 是：

```c
event->user_data = descriptor->user_data;
descriptor->cb(event); // a0=event，间接JALR；a0返回值被忽略
// 检查的是 event.flags，不是 free()/callback 返回值
```

DELETE不向父传播：`code-0x16=19`，dispatcher的 `0x58189ff1` 排除位图中bit19=1。该位图由 `a00d8300/8308` 的 LUI/ADDI 构造；本轮核其原字节及bit。子页事件的 original target 因而保持子页，不会靠父天气 hook错误清父状态的假链来解释生命周期。

## 原顺序、布局和所有权

```text
外层 W.class=a05647fc（base=a0263ef4）
  W+0x10 -> S，alloc(8)，S+2:u8=0x19，S+6:u8滚动状态
  子页 P.class=a0263ef4
    P+0x10 -> B，alloc(0x14)，B.type32@0=0x19，B.ctx32@4=C
      C=alloc(0x74)，前112B为28个控件/行地址；+0x70为byte状态
    P 的子控件在对象树中；清 C 的指针不会从对象树删除它们
```

天气 factory 前缀 `a00d91d2/d91d6` 合成 class `a0263ef4`。原表 `a0263efc` 的 destructor=`a00d87d0`；外层表 `a05647fc` base 指针为 `a0263ef4`，`a0564804` destructor=`a00b1df8`。没有为这两个基类凭名称添加释放 user_data 的行为。

伪代码保留实际调用与条件，是分析重建，不是原源码：

```c
on_enter(event) { // a00b35ee 的已恢复正常分支
    W=event.current_target; S=load32(W+0x10);
    if ((event.code & 0xffff7fff)!=0x11) return;
    store8(0x62fc403a,1);
    if (a00a769a()!=0 || a00d8af6(event)!=10) return;
    if (load8(W+0x64)!=0) { store8(W+0x64,0); return; }
    if (load8(S+2)!=0x19) return;
    locate_last_child_with_word_3c_1_then_first_type4();
    obtain_two_stack_field_blocks_and_call_a01b2086_in_original_order(1,0);
    a00ded6c(W);
}

parent_delete(e) { // a00b1a02
    if ((e.code & 0xffff7fff)!=0x29) return;
    W=e.target; S=load32(W+0x10);
    if (!S) { log(); return; }
    timer=e.user_data;
    if (!timer) { log(); return; } // 原失败臂不free(S)，不能补成理想清理
    a008ae58(timer);
    a008ab8a(S);                   // 8 B，非天气ctx
    store32(W+0x10,0);
}

delete_core(obj) { // a00dcf52，省略本题外输入设备与异步delete记录的具体循环
    flags=load16(obj+0x2a);
    if (flags & 0x1000) return;
    store16(obj+0x2a, flags | 0x1000);
    if (a00d831a(obj,0x29,0)==0) {
        store16(obj+0x2a,load16(obj+0x2a)&0xefff); return;
    }
    if (load32(obj+8)) a008b7f0(load32(obj+8)+8);
    while ((child=a00dcee4(obj,0))!=0) delete_core(child);
    detach_matching_input_references_and_pending_delete_records_in_original_order();
    a00d7806(obj);                 // class dtor walker；不是公共删除入口
    remove_object_from_parent_children_or_display_array_and_resize();
    a008ab8a(obj);                 // obj地址；非ctx或wrapper
}

weather_delete(e) { // H02合同，真实顺序在本轮边界针对核
    if ((e.code & 0xffff7fff)!=0x29) return;
    P=e.target; B=load32(P+0x10); if (!B) return;
    C=load32(B+4);
    clear_28_words_in_original_offset_order(C); // 保留C+0x70..73
    a00b3abe(a00b5cd4,P);                    // 同键首匹配注销
    a008ab8a(B); store32(P+0x10,0);          // 20 B wrapper
}
```

所以在 event 已安装、状态允许且发送返回非零的这条正常路径，顺序明确为：**父 W 的 DELETE / 停1000ms timer / free(S8) / 清W+0x10 → 天气 P 的 DELETE / 清C前112B / 同键注销 / free(B20) / 清P+0x10 → P的控件逐个递归删除 → P的base class析构 / 从父数组摘除 / free(P) → W的window class及base class析构 / 摘除 / free(W)。** 子树内其他非天气对象顺序取决于实际 child[0] 顺序，不能宣称天气页在整个窗口全部子页中总是第一个。

`a00b1df8(W)` 另查 `W+0x60` timer，非零才删除；它恢复前输入组/相关对象引用；不同于父 DELETE 的 event.user_data timer，不合并成一个 timer。`a00d87d0(class,obj)` 遍历当前事件链，当 current_target 或 target 等于 obj 时置 event.flags bit0，然后处理样式/组等内部资源。其显式 free 实参来自 `load32(load32(obj+8))` 和 `load32(obj+8)`，并调用 `a008b7f0(obj.extra+8)`；不是从 obj+0x10 取天气ctx。这些 opaque helpers 的内部资源不在本轮全量恢复范围，不能凭显式free个数声称全堆已释放。

## context 最终归还：有界检查与精确断边

本轮完整解码 `a00b821e..a00b8bfb` 的822条指令，对 allocation 后保持C的s2全部普通/厂商指令引用做静态索引。直接持久 `SW s2` 唯一是 `a00b8be2: sw s2,4(s4)`；未见直接将s2搬至a0..a7传给callee。`a00b8818` 派生 `s3=C+0x54` 用于行指针数组，**此检查不是全局别名分析**，不把该直接引用结论扩展为“绝无任何派生地址或callee外部保留”。前缀只有分配失败时的 `free(wrapper)`，成功C并未交给该free。

再检查本题已列的正常离页分支、两个DELETE hook、event传递、完整删除核心、class walker以及两个已识别class析构：父hook只持S8，子hook唯一free的a0是B20；删除核心最终free的a0是obj；没有发现把C重新装入a0送到free的指令链。H01/H02已核天气消费和timer userdata按P查C，本轮不复制整条数据流。正常DELETE后 `B` 被free且 `P+0x10=0`，所确认的 **P→B→C 根引用在该处脱挂**；P随后仍可凭自身child数组递归删除控件，无须读已清的C控件指针。

**精确未闭合边：成功构造 `C=alloc(0x74)` → `B+4=C` → DELETE清C字段并free(B) / 清P+0x10；从C到最终归还者没有已定位的调用或间接安装证据。** 未搜索全ROM所有free调用、全部UI类型/所有导航、所有opaque样式/输入/allocator实现，也未进行运行时堆追踪。因此本报告既不说“C必然常驻”，也不作泄漏/缺陷判断，不能将上述条件正常路径写成完整堆回收成功。

## 来源、验证和恢复程度

事实是上述地址、原字节、定宽访存、结构链、callback ABI、返回/flag门、发送前于递归及显式free实参；“确认键”有原日志和数值10支撑；临时窗口/主页面恢复是装配、对象层级与两次更新用途的业务推断。原厂 `lv_power_ui/lv_ui_wx1_dtl.c` 字符串支持厂商胶合身份。通用层与LVGL对象/event设计相符，但精确版本/源码来源未认证，没有将其当标准库排除；只读profile规则是厂商字的核对来源，不是假称厂商原C源码。

实际执行 `python reverse/analysis/weather-page-close-h03-0041-20261023/verify.py`：**passed，1025条选定原指令、194项检查，另822条构造引用解码。** 覆盖JAL目标、两处不同userdata挂接、父DELETE的8B free参数、事件栈布局/前链恢复、pre/normal标志和间接单参ABI、DELETE排除冒泡、递归/析构/free顺序、厂商mveqz和bit15提取、class表、H02的28word与wrapper参数。未执行固件、模拟器、设备、历史回放或异常输入；未外连、编译项目、修改ROM/生产模型。`git diff --check` 和本报告相对链接检查通过。

本题恢复到一条真实离页触发和完整事件交付/对象层级删除的有证据小闭包；context最终free仅达到可定位断边，未声称问题不存在或完整拥有者已恢复。建议唯一后继：由新agent独立复核本H03的父/子对象区分、确认键门控、event返回/flag合同及ctx断边；不要据本报告直接扩成全部GUI删除或凭假定补上free(C)。
