# 0041 E01：UiIFace CTK 端口嵌套快照所有权

本轮把端口项 `+0x28/+0x2c/+0x30` 的创建、原位更新、实际数据转换消费者和局部释放连成闭包，同时记录同族 `+0x34/+0x38` 的创建、更新及释放。关键结果是：这些字段归 UiIFace 的端口项持有；普通 `0x52` 响应覆盖已有缓冲区，不交换指针；类型变化与端口失活会释放并清零；已核消费者只借用这些缓冲区、复制数值到调用者对象。全局 deinit 不因此获得逐项释放语义，`+0x34/+0x38` 的页面数值消费者仍留明确断边。

本报告为分析命名、布局和伪代码，不是原源码。原厂 ROM 身份沿用既有证据 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射基址 `9ffff000`。只做静态读取；未运行固件、连接设备/服务、做异常输入或缺陷验证、修改 ROM、生产代码、构建配置或分析器模型，也未运行历史回放。恢复状态为**局部闭合，整体部分恢复，待独立复核**。

## 范围与证据

基线 `2ee39b3`，独占工作树 `re0041-e01`。主流程是 `a00a8582` 中三个限定片段：`cmd0x51` 类型变化、`cmd0x52` CTK 扩展快照覆盖、`cmd0x50` 失活清理；并非完整恢复该响应容器。核心及直接依赖共 10 个入口：

| 地址 | 参数/返回与本轮职责 |
| --- | --- |
| `a00a8582` | `(cmd word,len word,payload*)`；无本轮认证的返回值；上述三个片段 |
| `a00a3d80` | `(item*)`；无有效返回合同；顺序释放五字段并清零 |
| `a00a53ee` | `()` → 0/1；选择一个待查询的 CTK 端口并提交 `0x52` 描述符 |
| `a00a53c0` | `(index word)` → 借用 item* 或 NULL；仅核本闭包必需的索引合同 |
| `a00a389c` | `(index word)`；间接 `callback(userdata,item*)`，返回后清 item mask；不重做订阅注册 |
| `a00f4740` | `(dst*,port_1based word)` → 0/1；CTK 数据转换，读三嵌套缓冲区，只写 dst 及一个全局状态字节 |
| `a00501be` | `(left*,right*,length word)` → 字节比较结果，0 表示相等 |
| `a008e362` | `(size word)` → 零初始化分配结果；下层 allocator 保留原合同 |
| `a0080d8e` | `(ptr*,size word)` → 原 ptr；零填充适配 |
| `a008ab8a` | `(ptr*)`；NULL/`62fc95e0` 忽略，否则交下层释放；不推定普通 free 的全部语义 |

[指令窗口](../../analysis/uiiface-item-ownership-e01-0041-20261023/instruction-windows.json)包含 21 个窗口、1,011 条指令及相应原字节/文件偏移，覆盖上述非库业务入口及必要调用片段。[消费者 dossier](../../analysis/uiiface-item-ownership-e01-0041-20261023/retained-consumer.json)复用历史 `whole-rom-private-20261023-129.json`，Evidence `ev_a83096b36b47fd87435b94d459872366820aeacdc83d31b3cff59acfd8dcf791`；[查询 dossier](../../analysis/uiiface-item-ownership-e01-0041-20261023/retained-request.json)复用 `048.json`，Evidence `ev_0d8e9c7f2e07427f5bbbb5afffb0862d03b6e2dc6384b4faa105424d304b06c7`。均保留完整 profile、来源和模型限制。

响应汇编复用[已存修复观测](../../analysis/buzzer-backlight-0041-20261023.json)中的 `a00a8582`，Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`；清理器对照[既有生命周期观测](../../analysis/uiiface-lifecycle-0041-20261023/retained-functions.json)的 `a00a3d80`。本轮未重开共享 REA 会话或改全局 target。[采集脚本](../../analysis/uiiface-item-ownership-e01-0041-20261023/collect-evidence.py)仅从主仓库绝对路径读取 ROM/留存原件，所有输出在本轮目录。[字符串原字节](../../analysis/uiiface-item-ownership-e01-0041-20261023/resource-strings.json)为名称和日志字段提供局部支持。

## 布局与创建/替换

沿用总对象 `62fcb2cc`、首 word 为数组、`u8 count@+6`、item 步长 `0x1a8` 的已核合同；不重新恢复总快照 getter。新增字段视图：

```c
// 424 B item 中的局部视图，不能以此推测未列出的字段。
u32 update_mask;           // item +0x00
u8  active_state;          // +0x0d，0x51 仅对非零项做类型更新
u8  device_type;           // +0x0e，0x15 为 CTK remote 分支
u32 remote_dev_ptr;        // +0x28，20 B
u32 remote_port_ptr;       // +0x2c，24 B
u32 remote_bms_ptr;        // +0x30，12 B
u32 remote_cells_ptr;      // +0x34，24 B，按日志 BC/BN/V1..V5 分析命名
u32 remote_power_ptr;      // +0x38，24 B，按日志 PB/PE/P1..P5 分析命名
```

`cmd0x55` 的原有 424 B 零初始化使新项五指针初始为零；该创建合同与本轮观察相容。真正嵌套分配在 **cmd0x51，而非 cmd0x55**：`a00a93a4..a00a940c` 从 `62fcb2d4` 的每端口 8 B 记录更新活动项。类型分类完整决策树不在本轮认证；其中未知设备 fallback 路径 `a00a9454..a00a947c` 在原始 `62fcb2d0` 记录可用、索引小于 `62fcb01c` 且记录 `u16@+4` 的 `0x1000` 置位时选 `0x15`。

```c
// a00a9504..a00a9598；new_type 来自原分类树，不能替换成仅CTK谓词。
u32 changes = 0;
if (item->device_type != new_type) {
    item->device_type = new_type;       // 先发布类型字节
    free_ctk_fields(item);             // 两条类型变化路径都清理旧字段
    if (new_type == 0x15) {
        log_create_ctk();
        if (item->p28 == 0) item->p28 = zero_alloc(20);
        if (item->p2c == 0) item->p2c = zero_alloc(24);
        if (item->p30 == 0) item->p30 = zero_alloc(12);
        if (item->p34 == 0) item->p34 = zero_alloc(24);
        if (item->p38 == 0) item->p38 = zero_alloc(24);
    }
    changes = 0x40;
}
// 后续还更新 +10 u16、+12 u8、+0f u8，分别累积0x100/0x200/0x80。
// changes非零则写 item+0 的word并同步通知。
```

顺序由 `a00a951a` 清理、`a00a9544/9554/9564/9574/958c` 五次分配及紧随 word store 支持。类型未变时直接进入 `a00a9598`，没有重新补齐空嵌套字段。分配结果直接存入对应字段，没有本片段中的整组成功判定、回滚或再交换；不添加这些逻辑。分配 adapter 对非空结果清零；底层 allocator 来源版本未认证。

## 查询、响应覆盖与同步借用

`a00a53ee` 缓存 `62fcb01c` 数量及 `62fcb6c4` 原始 8 B 数组。它按 **u8 局部索引**扫描，借用 UiIFace item，找 `type==0x15 && raw[index].byte2!=0` 的首项；提交栈描述符 `{u16 0x0152@0, payload_pointer@4=&index}`，调用 `a01951e2` 后清原始记录 byte2，返回 1；找不到返回 0。该 `0x0152` 按既有命令描述符合同表示 `cmd0x52,len1`。提交器如何复制栈数据、异步发送以及 byte2 的全部生产者属于已有发送合同/后继范围；本轮不推定该栈指针被长时持有。该函数在 `cmd0x52` 收尾被再次调用，推进下一条查询。

`cmd0x52` 在 `a00a861e` 清活动命令字节 `62fcb2f0`，取 `payload[0]` 为端口索引并调用 `a00a53c0`。该 helper：全局快照为空或 word 索引 `>=u8 count` 返回 NULL；否则返回 `array+index*424`，不分配或取得所有权。响应路径仅对借用结果非空继续。

局部 header 先从 `payload+1` 复制 8 B。其首 word 为 `0x2b010112` 时选 Dev；为 `0x2b010114` 时以 header 最末 byte（即 `payload[8]`）选 1/2/3/6；其他组合跳查询推进。各资源的**真正拷贝源为 `payload+5`**，不把 header 的第一 word 再包含进去：

| header / subtype | 目标 item 字段 | 固定长度 | 通知 mask |
| --- | --- | ---: | ---: |
| `0x2b010112` | `+0x28` | 20 | `0x4000` |
| `0x2b010114 / 1` | `+0x30` | 12 | `0x8000` |
| `0x2b010114 / 2` | `+0x34` | 24 | `0x10000` |
| `0x2b010114 / 3` | `+0x2c` | 24 | `0x20000` |
| `0x2b010114 / 6` | `+0x38` | 24 | `0x40000` |

每个分支都先缓存目标字段到 s2，再依次执行 `compare(target,payload+5,n)`、判断比较结果、判断缓存指针、`copy(target,payload+5,n)`、日志、**直接赋值** `item->update_mask=mask`、同步 `a00a389c(index)`；没有 OR 旧 mask，没有分配、释放、替换 target 指针。比较返回 0 不复制、不发这次通知。原指令把比较放在 NULL 判断前，例如 `a00a86a8→a00a86ac→a00a86b2`；伪代码保留调用次序，不前移 NULL 判断，也不开展异常验证。

`a00501be` 的 aligned word 快速比较后退到 unsigned-byte 逐字节比较，返回首个差的 byte 差值；相等/长度归零返回 0。`a00501ee:8b47e580` 与 `a00501f4:8bc6e580` 分别是无符号索引 byte load，后者利用预先 `right--` 和 `index++` 保持相同索引；不是有符号字符比较。复制接口 `a000589c(dst,src,n)` 沿用既有字节复制合同，本轮不重做其 1,080 B 优化库体或认证上游出处。

`a00a389c` 从当前全局取得数组并固定借用 item 地址，遍历已有 `62fcb530` 链，间接调用 `callback(node.userdata,item*)`；回调后依原头部偏移取 next。结束时经 `a00a38d8:0b502a41` 清**之前缓存数组中该 item 的 word mask**，不是重读全局后清。没有借用嵌套资源的 retain/release、没有深拷贝；不据此推定回调中的并发、重建或增删规则。

## 实际消费者：CTK 值转换，不持有资源

`a00f4740` 日志为 `j_ui_cuk_con_update_init_value`，路径 `lv_power/ui/lv_ui_cuk_con.c`。本轮恢复它的数据转换，不追页面创建、控件渲染、事件及销毁。入口执行 `index=(port_1based-1)&0xff` 后借用 item；依次要求 item、`p28`、`p2c`、`p30` 非空，否则日志并返回 0；没有检查 `dst`、`p34` 或 `p38`。成功正常返回 1，整个函数无分配、free、指针存储到 dst 或对三资源写入。

它将 p28 byte `+4,+5,+0b,+0a,+11` 依次写 dst byte `+2,+1,+3,+4,+5`，五项和截成 u8 写 `dst+6`。这些来自 Dev 日志 AN/CN/WN/DN/MuxN 的端口种类数量视图，消费者日志对应 a_num/c_num/wl_num/dc_num/mux_num；只以日志支持名称，不补造完整协议结构。若和非零且 `62fc4067[index]` 为零，置该全局 byte 为 1；不在此函数清零。每次读 p28 均从 item 重取指针，不能把这些重读取合并成恒定局部指针。

`mask&0x8000` 的两次判断分别重读 item mask：

```c
if (load32(item+0)&0x8000) {
    u16 raw_soc=load16(load32(item+0x30)+8);
    if (load16(load32(item+0x28)+6)==0) {
        store16(dst+10,0); store8(dst+0x50,0);
        store16(dst+8,(raw_soc+99)/100);
    } else {
        store16(dst+8,raw_soc/100); store8(dst+0x50,1);
        store16(dst+10,(raw_soc%100)/10);
    }
}
store8(dst,port_1based);             // 不等候BMS变化
if (load32(item+0)&0x8000) {
    u32 minutes=(load16(load32(item+0x30)+10)<<3)/60;
    store16(dst+12,minutes/60); store16(dst+14,minutes%60);
    log_soc_and_remaining_time();
}
```

实际 `div/divu/remu` 字存在于 `a00f495c/4994/499a/499e/49f4/49fa/49fe`，即使旧反编译标记移除这些“不可达块”，原指令分支可达，不能省去数值更新。第一条 div 处理经 lhu、加 99 得到的非负 word，后续除法为 unsigned；半字 store 截断保留。

若五种数量的 u8 和 `<=4`，按 dst 的 CN、AN、WN、MuxN 数量依次生成类型 1、2、3、6 的标签，每项写 `dst+0x1c+16*j` type、`+0x1d+16*j` ordinal；单项 ordinal=0，多项从1计数，累加索引按 u8 截断。**数量 dst+4 计入总和，却没有对应标签生成循环**；本轮按 `a00f4a12..a00f4adc` 保留，未“修复”为五类一致循环。

随后重读 `mask&0x20000`；成立才把 dst `+1e/+2e/+3e/+4e` 清零。从 p2c 的 `u16@+2` 取 start=bits7..4、end=bits3..0；start=1/end=0 特例把 end 变为1。输出指针为 `dst+16*start`，输入序号 j 从0开始；从 start 循环至 end（循环比较用 start 低8位），仅 `(u8)(start-1)<4` 的位置更新，其他位置仍推进 j 与输出指针。每次字段读取都重读 p2c。

每条输入使用 `p2c+4*j`：`kind=bits11..8(load16(+6))`；输出 `+0=kind!=0`；kind3 写 `+1=0`、kind4 写 `+1=1`、其他 kind 保留旧 `+1`。`v=(load16(+4)+50)/100`，`c=(load8(+6)+1)>>1`；写半字 `+4=v/10,+6=v%10,+8=c/10,+a=c%10,+2=(v*c+50)/100`，并 byte `+e=1`。相应 div/rem 原字节也保留；日志命名支持电压、电流和功率视图，但本轮未认证线缆协议单位、校准或所有取值约束。

这些转换把**数值**复制到调用者 dst，未把资源所有权或缓冲区指针交给页面。因此对已核 `+28/+2c/+30` 能证实“项持有、响应覆盖、消费者借用、局部释放”闭包。没有证据将 dst 寿命与缓冲区寿命相等同。

## 释放时机与断边

`a00a3d80` 先日志，然后按 `+28,+2c,+30,+34,+38` 顺序：load 字段到 a0，非零则调 `a008ab8a(a0)`，返回后 store word 0。不存在整组先清零，也不清 item 的 type、mask、数值或历史。关键 free 参数在 `a00a3dae/3dba/3dc6/3dd2/3dde` 明确 load；旧反编译省略参数不代表无参 free。adapter 忽略 NULL/静态 sentinel，否则转 `a002e14e`。

三处直接调用都在同一响应容器：`a00a951a` 切到 CTK 类型、`a00a972a` 切到其他类型、`a00a935e` cmd0x50 失活。后一路 `a00a9340..a00a9364` 先 `fill(item,0,0x24)`，再清 `+0d`、按原始状态半字 bits10..0 中 bit10 写 `+0c`、调用清理器、将本地变化 mask 置 `0xfff` 并进入已有项通知尾部。`fill` 仅覆盖前36 B，五指针位于其后，故仍由清理器显式释放。未把该语义扩大到所有 offline 判定分支。

事实：这三个调用点给出真实可定位的局部释放链；cmd0x51 类型同值时不清、不分配；cmd0x52 原位更新不改变持有者。推断：Dev/Port/BMS/Cells/Power 是基于日志名和消费者使用的分析命名。未知及限制：

- `+34/+38` 的分配、复制、日志读取、通知、清理都已证实，但其真正页面值转换消费者不在本轮定位范围；不能声称五组全部 UI 闭合。
- 全局 `a00a3d22` deinit 仍只有通知离线、释放 item 数组和总对象，没有逐项调用清理器；沿用[原生命周期断边](uiiface-lifecycle-0041-20261023.md)，不拼接一条未发生的释放链，也不做缺陷判断。
- `a00a53ee` 中 pending byte 的生产者、查询完成推进与 UI callback 的实际注册/调用关系仅有局部合同；`a00f4740` 是否由本次同步 dispatcher 直接触发未证明。两者通过同一 item 字段连接是事实，不把它们写成已认证的一条直接 call chain。
- `a00a8582` 的完整类型分类、其他 response、长度合同与外部串行化不在本轮；分配器、字节复制、日志及提交器的准确上游来源版本未认证；新增开源认证排除为0。

## 实际静态验证与后续闭包

运行采集脚本成功：21窗口、1,011条指令，窗口内无剩余未知解码。THead 指令按原字节显式取操作数字段，`thmsb=(26..31),thlsb=(20..25)`；例如 `a00f4af0:8b3a4b1c` → `extu s5,s6,7,4`，`a00f4b4e:0b37872c` → `extu a4,a4,11,8`，`a00a38d8:0b502a41` → 索引 word 零写。语义对照已存私有 `ap01thead2.sinc`，没有把该本地模型说成上游独立认证。检查原字节范围、分支落点、固定长度/字段偏移/掩码、free a0、consumer 的原整数除余及间接 ABI；未执行功能测试或历史回放。

后续建议限定一组：从 `a00f4740` 的真实调用点反向闭合“端口项通知 → CTK 转换 → 调用者 dst 消费”以及借用寿命；只针对该数据转换调用点与必要注册片段，约5–12函数，避免扩大成完整 CTK 页面。`+34/+38` 的独立实际消费者可留再后一轮。本轮结论仍需新的独立 agent 技术复核。
