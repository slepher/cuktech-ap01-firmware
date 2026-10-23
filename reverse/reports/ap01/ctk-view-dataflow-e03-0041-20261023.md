# 0041 E03：CTK 转换的真实调用、数值消费与栈视图寿命

本轮恢复了一条可由原指令连接的正常 port1 数据流：应用构造片段注册 `a00adabc(app,item)` 到 `62fcb530`；`a00a389c` 遍历该链调用它；回调在端口1更新分支建立 **0x52 B 栈视图**，调用 `a00f4740(dst,1)`，成功后消费名称、四槽端口数值和电池数据。消费函数只读取 dst 的标量，未保留 dst 指针；下一分支复用相同栈槽，最终随回调的 0x100 B 栈帧归还。

`a00a389c → a00adabc → a00f4740` 现在有注册与间接调用证据，已经不同于 E01/E02 中“关系未证”的状态。这里没有把 `a00a389c` 当成转换器的直接 caller。整个 6054 B 回调、页面所有构造/销毁和物理显示仍未恢复。订阅节点和 app 的最终销毁没有在本闭包中定位，保留具体断边。

## 范围、基线和来源

基线 `78b8a5d43a4bd873b21321bd7bf6ced5f4adb16c`，分支 `codex/re-0041-e03`，独立 worktree `re0041-e03`。只写本报告及同名独占 analysis 目录。采用 REA 技能的证据优先、事实/推断/未知分离方法，使用既有 retained dossier 与 immutable ROM 原字节，没有切换全局 target、打开共享可写数据库、执行固件或历史回放，也没有外连、编译、修改 ROM/生产模型/正式代码。

原厂 ROM 为主仓库只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，基址 `9ffff000`；沿用既有身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不新增机械哈希清单。

先读 [E01](uiiface-item-ownership-e01-0041-20261023.md)、[E02](uiiface-ownership-review-e02-0041-20261023.md)、[UiIFace 生命周期](uiiface-lifecycle-0041-20261023.md)、总量消费者及模式控制。转换器、item 查找、响应生产/五字段清理采用 E02 已验收合同，只核本轮使用的接口，没有重做 cmd50/51/52 或 +34/+38 的独立 UI 读者。

原 retained 来源均在主仓库 `evidence/rea-0041-20261017/evidence/`，provider 为 Ghidra 12.1.4、私有 `RISCV:LE:32:ap01thead2`：

| 来源 | Evidence / 本轮使用 |
| --- | --- |
| `whole-rom-retained-private-20261023-001.json` | `ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5`，a00adabc 的调用/参数/分支辅助定位 |
| `whole-rom-private-20261023.evidence.json` 同一 record | 完整 incoming references 和三处转换器直接 call；[选取引用](../../analysis/ctk-view-dataflow-e03-0041-20261023/references.json) |
| `whole-rom-private-20261023-127.json` | `ev_69cdec12971877a40f70556d5f5b52e5b8bc80983fc6e4dafd756a403580bd88`，名称消费者 |
| `whole-rom-private-20261023-128.json` | `ev_af327f2740ec89643fb4772c2c966d0baa8901bf2e994375c1fc4890657b8e37`，端口数值消费者 |
| `whole-rom-private-20261023-106.json` | `ev_c8441eed57687866ad85b6a464446d07f1518000b24c0aad5dce0d6060353370`，状态消费者 |
| `whole-rom-private-20261023-108.json` | `ev_e7217a0d90a7e2f1283d7b82189b2d3b173cf7aa2cf94d673ad4563afec05b74`，电池消费者 |
| E01 consumer `…-129.json` | `ev_a83096b36b47fd87435b94d459872366820aeacdc83d31b3cff59acfd8dcf791`，既有转换合同 |

本轮不重复保存上述完整 dossier；新增 [原指令窗口](../../analysis/ctk-view-dataflow-e03-0041-20261023/instruction-windows.json)保留每条地址、文件偏移、原字节、标准解码或厂商编码字段。结论以原指令为准，旧反编译有 unreachable 警告，不据此删除原控制流。

## 九个核心合同

| 入口 | 本轮 ABI / 返回与范围 |
| --- | --- |
| `a01b28ce` | `(callback,userdata)`，端口项订阅注册；返回未作有效业务值认证 |
| `a00a389c` | `(item_index word)`，借用 item，间接 `callback(userdata,item)`；已有合同针对核 |
| `a00adabc` | `(app*,item*)`，真实 caller；只恢复入口门控、端口映射、port1 CTK 分支及栈归还，非全部页面行为 |
| `a00dcee4` | `(parent*,signed child_index)` → child* 或0；本路径传1，随后 caller 未加空检查 |
| `a00f4740` | `(dst*,port word)` →0/1；E02 转换合同，只针对核调用 ABI |
| `a00f44e8` | `(slot*,u8 kind,u8 ordinal,u8 total)`，标签/初始状态消费；四参均有证据 |
| `a00ef0ec` | `(slot*,active word)`，标量状态决定颜色/flag 更新 |
| `a00f4610` | `(slot*,row*)`，读方向、功率、电压/电流整数及小数，向控件 setter 传标量 |
| `a00ef2da` | `(panel*,view*)`，读 SOC、显示小数模式及小时/分钟；向控件 setter 传标量 |

`a005cc1e` 的一处注册片段和 `a00a55ba` 的头初始化作为必要构造证据，不把这两个大容器认作整函数已恢复。通用链表追加 `a008af14`、填充 `a0024906`、GUI setters、日志/格式化/allocator 保留既有或局部接口边界；未认证其准确上游来源/版本，因此没有以“标准库已知”为理由排除它们。

## 注册与真实触发

`a005d13c:37e50aa0` / `a005d142:1305c5ab` 构造 a0=`a00adabc`，`a005d140:d285` 将 s4 应用上下文放 a1。`a005d146:97501500` / `a005d14a:e7808078` 是一组 AUIPC/JALR，目标 `a01b28ce`，不是两个独立调用。它紧邻总量回调 `a00ad07e` 的注册，但使用另一注册器/链表。

`a01b28ce` 取 `62fcb530` 的 first 并按 head.link_offset+4 取 next，只比较 node+0 callback；相同 callback 返回，不更新 userdata。未命中调用 `a008af14(head)` 追加后依次写 `node+0=callback`、`node+4=userdata`。初始化 `a00a5652..5660` 明确将此头设为 `{8,0,0}`，a4=8 来自 `a00a5630`。节点据已有追加合同为16 B，布局 `{callback@0, userdata@4, link@8, next@12}`。注册器没有新增失败回滚或 app retain。

`a00a38c8` 和 `38d2` 选择同一个 `62fcb530`；`38ee` 取 callback、`38f2` 取 userdata 放 a0、`38f4` 将之前固定的 item 放 a1、`38f6:8297` 间接调用。因此当此节点仍挂在链上时，端口项分发可到达 `a00adabc(app,item)`。响应生产/通知的触发沿 E02 合同，例如更新 mask 后 `a00a389c(index)`。回调返回后 dispatcher 按原头部偏移取 next，完整遍历结束才清原缓存数组中 item 的 mask；不把回调内读 mask 写成已经清零。

真实 callback 的 incoming references 在该 retained record 中只有一条：`a005d142` 的 PARAM/data 引用；direct callers 列表为空与间接注册调用一致。这个有界引用结果不能证明没有其他计算出的注册/移除路径。

## 端口、panel 和 dst 如何产生

callback 用 s6=app、s2=item。入口 app/item 为空只日志返回；`a00891b8()` 返回非零时保存 `item.mask` 到 `app+0x54`，日志后返回；不将此函数身份扩写为完整动画调度器。返回0后还要求 `load8(app+0x4c)!=0`。日志支持“动画进行/跳过更新”的解释，但实际 gate 由指令返回值确定。

端口号不是 converter 反向返回的。callback 读 `load32(item+0x24)` 的 bits5..4 和 bits3..0，映射：

| 高2位 | 低4位（高位0时使用） | caller port s3 |
| --- | --- | ---: |
| 0 | 0 / 1 / 2 | 1 / 2 / 3 |
| 1 | 未用于此映射 | 4 |
| 2 | 未用于此映射 | 5 |

bits5..4 来自 `a00adbc4` 厂商 extu，原字段确认为 msb5/lsb4。未列值的全页处理不认证。正常在线路径形成 `s5=port-1`，`s11=(port-1)&0xff`。选定的 port1 分支在 `a00aef16..20` 要求全局 `62fc4062` 为1且 port=1。全页此前其他状态/弹窗处理仍按原 callback 路径执行；本报告没有把局部伪代码提升为回调入口直达该分支的完整等价替代。

`a00aef40..58` 调 `a00dcee4(app,1)`；caller 从返回 child 的 `+0x10` wrapper，再读 wrapper+4 得 panel。`a00dcee4` 的正常非空路径先读 parent+8 容器，u16+0x30 count；负索引先加 count，仍负或无符号越界返回0；有效时以容器+0 的数组和 index<<2 取 child。caller 未在上述两次解引用前检查返回0，保留原正常路径，不补检查或进行异常验证。

callback 入口 `a00adabc:1171` 分配0x100 B，`a00adad8:0002` 使 s0 为进入前 sp。dst 固定为 **s0-0x94**；`a00aef4c` n=0x52、`4a` fill=0、`50` dst，`58` 调填充器，`5c` port=1、`5e` dst，`62` 调 converter。此栈槽没有 heap 申请和归还操作。

视图布局以 E02 的写入和本轮消费者读取交叉确认：

| dst 偏移 | 宽度 / 用途 |
| --- | --- |
| +00 | u8 原 port |
| +01..+05 / +06 | 五类数量 / u8 总数；+04计入总数但 converter 没有独立标签循环 |
| +08 / +0a | u16 SOC整数 / 小数位 |
| +0c / +0e | u16 小时 / 分钟 |
| +10+16*i，i=0..3 | 16 B 数值 row；+0 active，+1 direction，+2 u16功率，+4/+6电压整数/小数，+8/+a电流整数/小数 |
| row+0c / +0d / +0e | u8名称kind / ordinal / 本次行数据有效标志 |
| +50 | u8 SOC小数显示标志 |

panel 布局由消费者相对地址恢复：`+4` SOC widget、`+8` SOC label、`+c`单位label、`+10/+14/+18/+1c`时间控件；`panel+0x20+0x20*i` 是第i个32 B slot。slot `+0`容器、`+4`名称、`+8`方向、`+c`功率、`+10`功率单位、`+14`电压、`+18`电流、`+1c`特殊图标。以上是局部视图，不声称其构造/销毁或完整结构体已知。

## 返回值、初始化状态和正常消费顺序

`a00aef66` 是 **beq a0,zero → a00af12e**；转换返回0立即跳过 port1 的名称、行数值、电池消费，去考察 port2。返回1后还有独立全局状态门：`state=load8(62fc4067+index)`。

- state=1：按 u8 dst+6 总数生成名称，再写 state=2；
- state>=2：跳过名称创建，继续值更新；
- state=0：不消费该 port1 视图。原比较是 unsigned，不能缩成“只接受state恰好2”。

名称循环在 `a00af062..82` **先 i++ 再访问**，i从1到 total；传 slot=`panel+32*i`，kind=`dst+12+16*i`、ordinal=`dst+13+16*i`。a3=total 来自每次 `af07e` 的 lbu，并在比较后到 `af076` 调用前保持，故 `a00f44e8` 有四个实际业务参数。只读 Ghidra 形参或只列 a0..a2 会遗漏决定 `kind6` 名称的 total。

主数值循环恰好四槽，row游标从 dst+0x10 起、slot从 panel+0x20 起，各次分别加0x10/0x20。每槽先读 row+0xe 非零，然后检查 **重新读取的 item.mask 或 app+0x54** 是否含0x20000；成立依次 `a00ef0ec(slot,load8(row+0))`、`a00f4610(slot,row)`。不提前缓存两种 mask、不移除每槽重读。循环后再次读 item.mask/app+0x54 的0x8000；成立才 `a00ef2da(panel,dst)`。

```c
// 正常 port1 分支的顺序视图；不是原源码或完整 callback。
if (load8(0x62fc4062)==1 && port==1) {
    panel=load32(load32(child(app,1)+0x10)+4);
    fill(frame_base-0x94,0,0x52);
    dst=frame_base-0x94;
    if (convert(dst,1)!=0) {
        state=load8(0x62fc4067+index);
        if (state==1) {
            i=0;
            while ((uint8_t)i < load8(dst+6)) {
                i++;
                name(panel+32*i, load8(dst+12+16*i),
                     load8(dst+13+16*i), load8(dst+6));
                i=(uint8_t)i;
            }
            store8(0x62fc4067+index,2);
        } else if (state<2) goto next_port;
        row=dst+0x10; slot=panel+0x20;
        for (i=0;i!=4;i++,row+=16,slot+=32) {
            if (load8(row+14)!=0) {
                log_row(i);
                if ((load32(item)|load32(app+0x54))&0x20000) {
                    status(slot,load8(row));
                    values(slot,row);
                }
            }
        }
        if ((load32(item)|load32(app+0x54))&0x8000) battery(panel,dst);
    }
}
next_port: /* 原指令 a00af12e，可能重新填充同一栈槽 */;
```

伪代码 OR 只压缩“先读 item，未满足才读 app”的短路判断，实际原指令保留该读取顺序。名称调用的 total 在原程序直接承接循环比较的 a3，不是为本报告新加一次原程序 load。

## 主要消费者恢复

`a00f44e8(slot,kind,ordinal,total)` 用 `a0601608[kind]` 的静态名称表；kind3隐藏 slot+4、显示+1c 特殊图标，其他类型相反。kind6且 total1 选静态 `Total`，total>=2 选 `USB MUX`；total0跳过该名称文本写入。非零 ordinal 使用 `%s%d`，零则直接 text setter；kind6/total1 的 `Total` 路径不附 ordinal。随后显示 +10/+14/+18，给 +c 设置固定初始字符串，再调 `status(slot,0)`。字符串来自 ROM，传下游的不是 dst 中的地址。

`a00ef0ec(slot,active)` 在 active0 时隐藏方向控件+8，+c/+10/+14/+18 设低24位颜色 `666666`；非零时显示方向控件，四个标签设 `ffffff`。这两个 flag 操作使用已经纠正的 `a00d8f7c/a00d9044` 接口名称；未重新认证全 GUI flag 内部，也不把 setter 返回值当业务结果。

`a00f4610(slot,row)` 的完整本地路径：

1. lbu row+1；0选择静态 `IN` 与低24位颜色 `89d8f3`，非零选择静态 `OUT` 与 `ffd24b`，设置 slot+8 文本/颜色。
2. 按原序调用对齐/布局 helper `a00dbb68(slot+8,slot+0,3,-14,12)`。
3. lhu row+2，格式 `%d` 更新 slot+c；布局 helper 将 slot+10 相对 slot+c 按 `(0x15,5,0)` 对齐。
4. lhu row+4/+6 用 `%d.%d V` 更新 slot+14；lhu row+8/+a 用 `%d.%d A` 更新 slot+18。

上述所有 row load 都是 lbu/lhu；没有把原16位值解释成有符号 short。颜色调用的 a1 由局部栈上的三字节构成，本文报告的是低24位 RGB，未声称其传递word高字节一定为0。

`a00ef2da(panel,dst)` 先向 panel+4 的 widget setter 传 lhu dst+8。SOC整数100且小数0时显示整数；否则 dst+0x50 非零时用 `%d.%d`，为0用 `%d`。SOC<10 时 widget/标签使用红色低24位 `ff5e34`；其他路径 widget 用 `06ff8b`，SOC及单位标签用 `ffffff`；保留原 setter/布局顺序。小时、分钟均0则依次隐藏四个时间控件；否则依次显示，再分别以 `%02d` 读取 lhu dst+c/e 更新对应数字控件。原字节与 [ROM字符串](../../analysis/ctk-view-dataflow-e03-0041-20261023/resource-strings.json)支持这些单位/格式名称，不能据此认定实际屏幕已经显示。

`values` 与 `battery` 把 dst/row 指针保存到本函数的临时寄存器用于 load，但没有将其 store 到控件或全局，也没有作为指针传给下游。给 formatter 的是零扩展标量、给文本 setter 的是 ROM 常量；其他参数是控件地址或颜色/布局标量。因此栈视图在这些消费者返回后无需 retain/release，文本内部如何分配/复制仍属于下游接口边界。

## 栈复用、另一调用点与清理边界

port2 `a00af12e..180` 要求 `62fc4063==1 && port==2`，取 child(app,2)，在同一个 **s0-0x94** 重新 fill0x52，调用 `a00f4740(dst,2)`，返回0跳 `a00af250`。本轮只针对核这个复用/返回边，没有把对称 port2 的全部后续 UI 分支重复恢复。

不能把“converter 返回0禁止所有调用者消费”当全局结论：另外 `a00ae238` 是原 offline/状态变化路径中的直接 call，随后 `a00ae242` 调 `a00ef1d4`、`ae24c` 调 `a00ef2da`，**没有测试 converter 的返回值**。这里同样先清0x52 B，因此失败时后续可消费零初始化视图。该路径仅用于限定返回合同/确认第三调用点，不扩写 `a00ef1d4` 全函数或整个离线页面行为。三处 call target 均由原 JAL 编码核验。

callback 公共结尾 `a00af250..25e` 检查/清 `app+0x54` 后跳同一 epilogue `a00adb20`；该 epilogue 恢复保存寄存器、sp+=0x100、返回。没有 dst 的独立 free：栈槽在回调内部可被其他局部用途或 port2 清零复用，并于本次回调返回失效。item 嵌套资源仍归 item 持有，converter 仅借用并写数值，三者生命周期不同。

订阅节点/app 生命周期仍不闭合：注册器只是保存 callback/userdata；完整 callback incoming refs 只给出该注册 PARAM 边，没有可直接认出的注销/清理引用。本轮针对读取 `a01b28ce` 注册函数、同头 dispatcher、完整 callback incoming refs，**没有恢复 item链任意间接摘链、app 的 DELETE/destructor 或节点最终释放**。不能拿控制链 `a01b2966` 的行为代替本 item链注销，亦不能把 stack归还称作页面销毁。这里是具体引用与所有权断边，无“永久常驻/永不注销/泄漏”结论。

## 厂商字、事实与实际验证

关键厂商指令均保留原编码，字段独立提取，并只与主仓库只读 `processor/data/languages/ap01thead2.sinc` 对照；该本地模型不是另一份上游规范：

| 地址 / 原字节 | 本轮使用的局部语义 |
| --- | --- |
| `a00adbc4` / `0bb74714` | extu a4,a5,5,4：端口分类高2位 |
| `a00dcf48` / `0bc5b744` | indexed word load a0=`*(u32*)(a5+(a1<<2))`：child数组 |
| `a01b2912` / `0b47d740` | indexed word next load a4=`*(u32*)(a4+a3)`，a3=head.link_offset+4 |
| `a00af068` / 见窗口 | indexed unsigned byte，ordinal来自 dst+13+16*i |
| `a00af06c` / 见窗口 | indexed unsigned byte，kind来自 dst+12+16*i |
| `a00f4506` / 见窗口 | indexed word，静态名称表 kind<<2 |
| `a00a38d8` / `0b502a41` | 原缓存数组 item.mask 清0；已有E02合同针对核 |

事实是原字节/寄存器 ABI、三处直接 caller、同头注册/分发、端口常量、字节/半字读宽、stack大小/地址、零返回跳转和消费者不存储/转交 dst。CTK/page/panel、功率/电压/电流及颜色名称是由字符串/单位/调用模式支持的分析命名。未知包括完整 app/page 状态机、最终物理显示、注册节点和 app 最终清理，以及通用 GUI/格式化/allocator 的准确来源版本。

执行 [verify-static.py](../../analysis/ctk-view-dataflow-e03-0041-20261023/verify-static.py) 成功：**18窗口、817条原指令，8个厂商字单列，8条指定直接边、1组AUIPC/JALR注册目标及唯一 incoming ref 核验通过**；无未解码指令。另逐项人工核对调用者的 a3 保活、循环先增后读、四槽游标、mask短路重读、unsigned状态比较、颜色三字节和三处转换返回差异。静态脚本是地址/编码/边界验证，没有执行 firmware，也不等于端到端显示验证。没有复制整个大 callback 作为“已恢复”交付。

恢复状态：本次 port1 **注册/触发→转换→主要数值消费者→dst栈复用/归还**局部闭包完成，等待新 agent 独立技术复核。后继建议只复核本文九合同与关键窗口，重点 a3=total、frame-relative 标签地址、0/1门控和offline第三调用点不判返回；订阅/app销毁继续作为另一个业务问题，不顺带扩展全页。
