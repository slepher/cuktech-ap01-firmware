# 0041 E06：CTK app 局部 DELETE 与未闭合注销边独立复核

2026-10-23；独立 agent，分支 `codex/re-0041-e06`，基线 `26fc8d750bf8cc90705dc2adf3a6c6e3840bd2dd`。应用 REA 技能，只作静态复核。

**E05 的 app 构造持有、item 注册、真实 DELETE 的 T1/state 清理、条件窗口递归析构与同头另一键摘链合同限定接受，无实质纠正。完整正常退出、`a00adabc` 注销、node/T3/context 最终归还仍未闭合。** 本复核接受的是 E05 正式报告明确限定的局部生命周期及断边，不把历史任务标题中的“完整闭包”当成已经恢复的行为。未修改 E05。

## 范围与独立证据

先读管理规则、E05、E04及 REA 技能。E04 的借用 item、栈 view、port1/port2 互斥合同只针对核注册 userdata、dispatcher 参数和返回后取 next，未重做 converter 或两个端口显示。核心沿 E05 十二组合同；短辅助保留在证据窗口中，不扩展 root 删除 incoming、全 registry teardown 或全部 UI。

原件仅从主仓库绝对路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin` 只读，映射 `offset=VA-9ffff000`，身份沿用 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，未新增哈希/复制清单。

[独立验证器](../../analysis/ctk-app-close-review-e06-0041-20261023/verify-e06.py) 新建 Capstone 实例，重新从 ROM 读字节；E05 JSON 只用作待核窗口和比较期望，不导入或执行其验证器。定位时读取过 E05 的只读 decoder 输出，最终证据由本轮独立脚本生成。[本轮证据](../../analysis/ctk-app-close-review-e06-0041-20261023/independent-checks.json) 保存27个窗口、897条指令、地址/偏移/原字节、标准解码或厂商字段、分支/调用目标、class words、独立有界同头检索与 retained 引用边界。E05 的19窗740条指令逐条原字节、连续边界、标准解码/厂商字段与目标匹配；另加适配器入口、descriptor分配、G独立分配、另一移除器 state 来源及候选上下文。

厂商语义对照主仓库只读 `evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc`：extu 用 msb/lsb，lrw 为 `load32(rs1+(rs2<<shift))`，srw 为 `store32(rs1+(rs2<<shift),rd)`；本地模型并非独立上游规范。`d76d0:0bb5464c` 明确 extu a0,a3,19,4；`d7800:8b54f744` 明确 store32(a4+(a5<<2),s1)；`89ce4:0bd6f540` 是 word link store；`89d3a:8bc5e540` 与 `f2fca:8bc5f540` 是 link word load。未把厂商字当未知 nop 或以反编译替代编码。

REA 既存来源为主仓库只读 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json`，Ghidra12.1.4/私有 `RISCV:LE:32:ap01thead2`；本轮重新读取以下 retained 记录的 incoming/callers，不开共享可写数据库、不切全局 target：

|入口|Evidence ID / 用途|
|---|---|
|`a005cc1e`|`ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866`；app 初始化定位|
|`a00adabc`|`ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5`；callback 有界 incoming|
|`a00afc88`|`ev_cbd4287ff839b53d9291e0aa4beeb3f46cf0a02dd1b36665e4f15334df3b4bfc`；输入 callback 身份和搜索范围|

未连接设备/外部服务、执行固件、编译项目、历史回放、异常输入/漏洞验证；未改 ROM、生产代码、配置或分析器模型。仅写本报告和 E06 独占 analysis 目录。

## 十二组合同裁定

|核心 / ABI|裁定|独立复核结果|
|---|---|---|
|`a005cc1e` 的选定初始化片段|接受|`cd78` 从栈重读 parent，`cd7c` 调构造，`cd80` app=s4；`cd82/cd84` 独立分配8B；`d122/d12c` 重读并写 app+10；T1/T3及两注册身份见下。完整初始化不是本轮验收范围。|
|`a00b2f6c(parent)`|接受|传 class=`a05647fc`，返回 app；旧全局值写 app+2c，新 G 写全局和 app+30。G与app来自不同调用，不能画成全局app根。|
|`a00d76ae(class,parent)` 分配/父挂接段|接受|class+20=`681` 的 bits19..4给size68；class/parent word分别写+0/+4。非空 parent 的扩展+30为 u16 count，增量用 sh，重读 count后 realloc(count*4)，追加app。|
|`a01b28ce(callback,app)`|接受|head=`62fcb530`；按callback单键去重，命中直接返回，不更新已有app；未命中 append后 word写 callback/app，无额外分配成功检查。未认证业务返回码。|
|`a00a389c(index)`|接受针对核|a0=node+4 app，a1=item，间接call node+0；返回后重新读head offset，再读next。node只是保存借用app，没有retain证据。E04互斥port合同保持。|
|`a01ad654` 与 descriptor写入段|接受|a0=app、a1=cb、a2=filter、a3=userdata；非空对象段保存后三参，调用扩展辅助，再以app扩展+8进 `a01b93b4`。descriptor申请12B，cb@0、filter@8、userdata@4。|
|`a00ab8ec(event*)` 全函数|接受|归一 event+8 的 bit15 后只收29；从event+4取app，从app+10取state，从event+c取T1。零state/零timer有各自日志早退；非零先删T1，再free state，最后word清app+10。没有item注销调用。|
|`a008ae58(timer)` 全函数|接受|`(62fc95f0,timer)` 调摘链；`ae7a` byte置 `62fc95fe=1`；a0恢复timer后独立调free接口 `a008ab8a`。|
|`a0089d02(head,node)` 与两个setter|接受|first/last/中间分支仅改head、邻节点link；调用目标只有 `89cda/89cee`，它们只存link，没有free。摘链不等于归还。|
|`a00dcf52(obj)` 公共删除|接受条件原序|先检查/置 obj+2a halfword的1000位，再发29事件；发送器返回0清该位后返回，非0才清事件、递归child0、输入/动画处理、class析构、父/屏数组移除及free(obj)。|
|`a00d7806(obj)` / `a00b1df8(class,obj)`|接受|以(class,obj)调用class+8；callback之后重读obj.class，再向base class递归。window dtor删app+60的独立class timer，恢复old G/输入关联，最后处理app+30新G。|
|`a00f2f98` 同头对照片段|接受|比较键由 `f2fa4/f2fa8` 合成固定 `a00f5288`；相等时对同head摘链，之后free的是s2页面state，非node。本片段不是 `a00adabc` 注销。|

必要辅助 append、event交付、base dtor保留本轮原字节。allocator/free、事件列表清理、输入/组操作等仍按明确地址和参数合同引用，没有因标准库外观而排除，也未认证具体开源来源版本及所有下游副作用。

## app、G、timer与state不能混同

`b2f86` 创建app，`b2f90` 另调 `a00d733a`。补核后者的 `d7344/d7348/d734c`，可见其以独立head `62fc95b0` 调 `a008aec0` 获得返回值，不是把刚才app直接返回。`b2f9c` 读全局 `62fc95bc` 原word，`b2fa2` 写app+2c；`b2fa6` 把a0仍为G的返回值写全局；`b2fde` 保存s1=G到app+30。称G为“组/输入关联句柄”是依据这些操作和输入type4挂接的业务解释，不是原源码类型声明。

```text
parent.ext.child_array ──> app(0x68 B)
app.class = a05647fc；app.parent = parent
62fc95bc ──> G；app+2c ──> old G；app+30 ──> G
app+10 ──> state8
head62fcb530 ──> node16{cb=a00adabc, borrowed app, prev, next}
app.event descriptor12{cb=a00ab8ec, userdata=T1, filter=29}
T1{cb=a00af262, 1000 ms, borrowed app}
app+58 ──> T3{cb=a00abd9c, 3000 ms, borrowed app}
app+60 ──> distinct class timer
```

T1来自 `d0f2..d104`，在s1保存，`d18c:a686` 把s1传为DELETE userdata。T3来自 `d106..d11a`，写app+58后调用 `a008bd16`；不能把该无参调用命名为销毁T3。window dtor在 `b1e06:a851` 取app+60，和+58/T1不是同一保存位置。其内部的type4输入遍历在每次循环取下一输入，解除app并重挂old G；`b1e36` 在调用后从app+2c重读old G，不用循环外缓存代替。`b1e40` 从app+30取新G传给 `a00d8370`；本轮只认证该调用，不认证整个G内部资源析构。

parent count 的写宽也影响所有权图：`d77ce` lhu、`d77d4` sh，随后重读parent.ext；array被realloc后写回扩展，再重读count/array，厂商srw把app追加。`d7800` 的index为count+`3fffffff`，乘4后等效 `(count-1)*4` 的32位地址运算，不能把它看成向app+30直接写入或另一个对象持有者。

## DELETE 的实际局部状态机

以下伪代码是按本轮原指令重建，非原源码；省略日志常量但保留顺序和返回门。

```c
app_delete(e) {
    if ((load32(e+8) & 0xffff7fff) != 0x29) return;
    app = load32(e+4);               // original target
    state = load32(app+0x10);
    if (state == 0) { log(); return; }
    t1 = load32(e+0x0c);             // descriptor userdata
    if (t1 == 0) { log(); return; }   // does not free/clear state
    a008ae58(t1);
    a008ab8a(state);
    store32(app+0x10,0);             // after free
}

window_dtor(class,app) {
    timer = load32(app+0x60);
    if (timer != 0) a008ae58(timer);
    store32(0x62fc95bc,load32(app+0x2c));
    // enumerate input type4: detach app; reread app+2c and reattach old G
    a00d8370(load32(app+0x30));
}
```

mask的字节是 `b8ee:6177` 加 `b8f0:7d17`，符号扩展的 `c.lui -8` 再减1得 `ffff7fff`，不是只取低15位。`b908:4441` 从event+4读app，不能用event当前target或event userdata替代。`b95e:4a85` 明确free参数s2=state；`b964:23a80400` 是word清app+10。完整callback只有日志、timer delete和free的直接调用，无对62fcb530或 `a0089d02` 的调用边；这一否定只针对完整callback本身。

event交付 `ad8e..ad98` 取descriptor+4→写event+c→a0=event→间接call descriptor+0。返回后的 `ad9a` 读取event+18 flags，并不把callback残留a0当成功码。公共删除器 `dcf88/dcf8c` 检查的是 `a00d831a` 的返回状态；不能从app_delete的free残留返回值推出删除成功。对象已处于1000删除位的入口直接返回；新置位但发送器返回0时清位返回。只有继续分支才存在以下条件顺序：

```text
app的29 callback(T1/state局部清理)
→ app事件列表清理
→ 反复重读child(app,0)，递归删除子对象
→ 必要输入/动画解绑
→ class析构(window后base)
→ 从parent child array或display screen array移除/realloc
→ free(app)
```

base dtor在callback后重读obj.class的机制由 `d781c..d7826` 支持；不能按入口class快照递归。base dtor已核窗口包括活跃event的删除标记、样式/事件/扩展child-array清理；它未直接读app+10或62fcb530。opaque辅助可能有本轮未恢复的副作用，因此“已核指令未直接访问”不提升为全程序否定。普通对象free不证明子页业务context、目标订阅node或T3已经归还。

## 同头摘链与有界否定

补核 `f2f54/f2f56`：s1来自event+4，s2来自该对象+10；`f2f8c..f2f94` 先处理另一控制链callback，随后才进入 `f2f98`。item头比较键是 `a00f5288`，和 `a00adabc` 数值不同。匹配时 `f2fba` 以node作为a1调用摘链；`f2fbe:4a85` 重新把s2送a0，`f2fc0` free(s2)，`f2fc4` 清s1+10。不能把这次free误归到a1=node，也不能拿前面的 `a01b2966` 当item注销器。

`a0089d02` 原序分别更新head.first/head.last和前后邻接link；辅助 `89cda` / `89cee` 只word写prev/next。其完整实现没有free，且没有把node交给可析构callback。T1 delete另外调用free恰好提供对照：调用摘链和内存归还确为两个动作。

本轮独立重复 E05 的限定方法：在 `[a0000000,a01b9800)` 每半字位置找LUI `62fcb000`，向后34B找同rs1的I类load/addi、imm530..53c，得到同样16候选。新增原字节上下文核实分类：

|候选|裁定|
|---|---|
|`a00a38c4→38c8/38d2`|item dispatcher，同head530|
|`a00a5652→5656`|head530初始化 `{8,0,0}`|
|`a01b28ce→28d2/28ec`|item注册器|
|`a00f2f98→2f9c/2fb6`|上述固定另一callback移除器|
|`a00a3a1c`、`a00a562c`、`a01b25ae`、`a01b25e8` 的53c候选|相邻通知head，不是item head530|
|`a00a5640→5656`|跨入新一次LUI `a00a5652`，不是独立引用|
|`a00ab18e→ab1a0`|`ab19a` 已用 `c.lui a5,7` 覆盖，最终7530；false positive|

保留此检索的边界：不覆盖别名、作为参数传递的head、其他寄存器算术、长距离/不同常量构造、运行时计算或更外的地址范围。retained `a00adabc` 仍只有 `a005d142` PARAM/data incoming，direct callers为空；静态参数引用符合间接回调，不证明没有计算引用、注销或其他生命周期入口。

## 事实、推断、未核与实际验证

事实是本轮ROM字节、class size、字段写宽、注册参数、借用边、完整DELETE与timer/list清理原序、条件对象递归、同头固定另一键。CTK app/window/state/G/timer等业务名称是字符串/挂接/既有合同支持的解释，不是原源码类型、引用计数所有权或运行观察。

未核保持四条断边：

1. **正常退出者→这个已注册app的公共删除。** a00afc88身份已知，但其其他窗口删除不能冒充本app；分配失败时直接class dtor也不是正常DELETE。
2. **app退出→以a00adabc/app注销head62fcb530的目标node。** app_delete本身没有该边，同头另一键摘链不能替代。root incoming/registry teardown是后继范围，本轮未开展。
3. **目标node、T3、子页业务context的最终归还。** 单独state8、class timer和window本体free均不能填补。未宣称常驻、永不注销或泄漏。
4. **退出与item callback期间可达性/调度同步。** dispatcher返回后重读next不提供引用计数或同步合同；本轮不作竞态/异常/缺陷判断。

实际执行 `python reverse/analysis/ctk-app-close-review-e06-0041-20261023/verify-e06.py` 成功：740条旧指令独立匹配，27窗897条指令连续边界，17项厂商字段/直接边/AUIPC-JALR检查、class size/dtor/key常量、16个候选和3份 retained来源重新读取通过。人工逐分支复核完整app DELETE、timer delete、list unlink和setter、window/class/base析构、公共删除返回门与递归次序、所有候选分类。脚本处理ROM为数据，没有执行目标；不把静态验证称为实际退出测试。

限定验收无实质纠正，完整退出/注销未核；无工具或审批阻塞。仅建议一个后继闭包：**真实app持有者的正常root删除incoming→目标item节点的参数/别名teardown→node最终回收**，优先找到实际调用参数后再连接，保留T3/context独立资源身份，不扩全UI或重做E04转换。
