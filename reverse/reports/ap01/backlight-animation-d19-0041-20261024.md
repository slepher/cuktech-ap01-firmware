# D19：亮度提交后的动画身份与清理（0041，2026-10-24）

结论：`a00f43d4(timer)` 提交亮度后启动的是 **2000ms 单周期、无限重复的 UI 数值动画**。`a00f4378` 是 path 回调，`a00f43bc` 是 exec 回调；本入口没有安装 ready/completed、deleted 或 ctx userdata。动画 target 是 `*(ctx+0x10)`，不是 ctx。旧设置页证据早已保存正常结束亮度编辑时按 `(target,a00f43bc)` 查询、删除并对同一 target 写 0 的路径。本轮只补这些字段和身份的原字节核对，未恢复全部动画或完整页面析构。

只做静态研究。基线 `e2991b9`，独立分支 `codex/re-0041-d19`。主仓 ROM、ignored 旧证据只读；未使用共享 REA target、执行固件/SIM/回放/构建、连接设备/外网或修改生产代码、配置、模型。采用 reverse-engineer-anything 技能的已有证据优先、局部原字节核对流程；没有新开分析会话。本文伪代码和字段名是恢复表达，不是原源码或上游 typedef 认证。

## 继承结论：先已有，再确定缺口

|既有出处|已解释的行为|局限与本轮处理|
|---|---|---|
|[背光第二轮](buzzer-backlight-round2-0041-20261023.md)，UI 入口部分；[第三轮](buzzer-backlight-round3-0041-20261023.md)|`timer+0xc→ctx`，`ctx+0x8c` byte→`a01b29ec`；`a00f5eb6` 首次创建2000ms、repeat=1 timer，已有 timer 不重启；背光 setter/PWM 合同|全部继承。timer 的一次 repeat 与其后动画的 repeat 是不同对象，不能混用。第三轮重点是 MiIO timer，不补此动画寿命|
|主仓 `reverse/rehost/system-complete-0041.json`、`guide-complete-0041.json`、`settings-0041-round2{,b,c,d,e}.json`、`page-logic{,-evidence,-evidence2}.json`|已有设置操作、页面 context 与服务/SIM 策略；字段检索能定位亮度提交与退出分支|全部文件按入口、回调、初始化地址和 `+84/+8c` 检索，计数见核对记录。精确 timer/path 地址未命中，exec `a00f43bc` 在 system complete 与 settings round2b/c 已命中清理身份；不能拿 SIM 生命周期替代 ROM|
|主仓 `settings-0041-round2b.json records[10]`，Evidence `ev_d2c060238142516e1df7a388e5984d96623578a75366a96c1472e9ed8c8df9fb`；round2c records[6]及 system complete 缓存|`a00fd1ac` 已保存正常状态 `0x40→0x3f`、timer 清理、按 target/exec 查询删除、同对象写0与后续提交；列表子对象 `+0x10` userdata 的 tag=`0x1d`、pair[1]=ctx|这是旧覆盖，不算新增功能。本轮只核 `a00feb74..a00febc3` 必要窗口，不重导设置大函数|
|主仓 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-125.json`，`structuredContent`，Evidence `ev_65a0d85b67cba9945c5911cf445f9f17d9f0ca6f766b502580109ef15b078c4a`|已完整保存 `a00f43d4` 的原序：复制 ctx 内0x60B→初始化→覆盖字段→start→另一个对象颜色更新|descriptor 构造已覆盖，不重导。较晚 `round3/evidence/*.json` 对 `a00f43d4/a00f4378/a00f43bc` 的文本检索未命中；该负结果仅限这些文件和文本表示|

主仓绝对前缀统一为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/`。本轮[核对记录](../../analysis/backlight-animation-d19-0041-20261024/review-result.json)保存完整复用路径、record 定位及 Evidence ID；[原字节小窗口](../../analysis/backlight-animation-d19-0041-20261024/instruction-windows.json)以名称定位下述指令。没有复制旧函数、全库源码或哈希清单。

## 本轮复核或纠正

### descriptor 与 userdata 不是同一个 context

调用次序保持原样：`a00f442a` 复制 `ctx+0x24` 的0x60B到栈，再由 `a008df3c(&a)` 初始化；初始化经 `a0080d8e(a,0x60)` 调既有清零 helper `a0024906(a,0,0x60)`，随后写默认值。故不能把初始 memcpy 的内容认作持续有效的动画 context。通用清零 helper 既有出处为 page-logic records[15]，本轮不恢复其厂商优化算法或扩作整库来源认证。

以本次传给 start 的栈首地址为 `a+0`，实际生效字段如下。偏移由栈 `s0-0x70` 和原 store 差值核算，语义由后续真实读槽交叉支持。

|偏移|本入口值|证据及用途|
|---|---|---|
|`+00`|`*(ctx+10)`|`a00f4426/445a` 保存 target；不是 ctx 本体|
|`+04`|`a00f43bc`|`a00f4452`；start/tick 以 `a0=target,a1=value` 调用|
|`+08,+0c,+10,+14,+18,+1c`|0|初始化清零后无本入口覆写；tick 的 `+0c` 是启动通知，`+10/+14` 分别完成/删除通知，`+18` 为取相对起值；`+1c` 仅确认零，userdata typedef 名未认证|
|`+20`|`a00f4378`|`a00f4446`；以 `a0=动画节点` 调用并取返回值，是 path，不是 ready|
|`+24,+28,+2c`|0、`0x80000000`、510|起值、当前值哨兵、终值；当前值哨兵保证首次值可执行更新|
|`+30,+34`|2000、0|周期长度、活动时间；后者保持初始化值|
|`+38,+3c,+40`|0|本入口没有 playback/repeat delay|
|`+44`|`0xffffffff`|`a00f4462/4474`，无限 repeat 哨兵，而不是一次2000ms后完成|
|`+5c` bit4|1|init 默认 early apply；start 会立即计算并执行一次|

`a008bf6e(&a)` 先从全局动画链 `62fc9628` 分配节点，再 `memcpy(node,&a,0x60)`（`a008bfe6..bff8`），因此持有的是独立节点副本。返回 node 在本调用点未保存；栈 descriptor 退出即结束。`a+00 != &a`，start 中“自指 var 改为 node”的分支不适用于本入口。没有把 timer ctx 借给 path/exec，也没有 ready 用来释放 ctx 的证据。

对象 userdata 的旧连接是：设置列表子对象 `+0x10→pair`，`pair[0]=0x1d` 识别亮度页、`pair[1]→ctx`；它解释事件路径怎样找到 ctx。动画再从 `ctx+0x10` 取另一个 UI target。不能把对象的这个 userdata 偏移与动画 descriptor 的同数值偏移 `+0x10` 混淆。

### path、exec、完成与删除身份

必要恢复伪代码如下，保持有符号除法、乘法和移位；正常时间范围内没有溢出推断。

```c
int path_a00f4378(Anim *a) {
    int q = map_a008a73a(a->active_time, 0, a->duration, 0, 1024);
    // map 对端点夹取，中间是有符号整数乘除。
    int value = a->start + (((a->end - a->start) * q) >> 10);
    if (value > 255) value = 510 - value;
    return value;
}
void exec_a00f43bc(void *target, int value) {
    a018fb3c(target, value & 0xff);
    // a018fb3c -> a00df94c(target, 0x3e, value, 0x20000)
}
```

原字节锚：`a00f4384/4386` 读 duration/active_time，`a00f4390→a008a73a`；`a00f439a` `mul`、`439e` 算术右移10、`43a6` 有符号 `bge`；`a00f43c4=93f5f50f` 将 exec 值截成 byte；`a018fb46` 装 selector=`0x20000`，`fb4a` 装 property=`0x3e`。ROM 数值属性绑定已确认；未额外认证这个属性的上游符号名或具体控件类型，不能仅凭0..255就命名为背光 PWM。

在正常0..2000周期内，path 形成0→约255→0的三角数值；原式先经1024格量化再投射至510，不能替换为连续浮点正弦。start 的 `a008c044..c054` 和 tick 的 `a008c194..c1b2` 均按 `path(node)→exec(node->target,value)` 调用。

tick 的 `a008c0a2` 将 `s3=-1`；到期读 `node+44`，在 `a008c232` 与 -1 比较，相等跳过递减，随后按 repeat 路径重置活动时间。因此本入口正常循环没有到达 completed 的有限期限。通用有限完成分支仍存在：从链摘 node→调度状态更新→可选 `+10(node)`→可选 `+14(node)`→`a008ab8a(node)` 释放；本 descriptor 两个通知都为0。不能将这些通用槽中任一个误标为 `a00f4378`，也不能说2000ms后释放 UI 对象。

## 真正新增：最小 ABI 与寿命闭包

相对旧报告的描述性缺口，本轮补齐实际 slot/target 身份、path/exec 参数与返回约定、`0xffffffff` 无限 repeat 的消费位置，以及 early apply 的节点复制边。主业务和函数原材料已有覆盖，**新增完整业务功能数为0**；没有新增开源认证排除。

正常结束亮度编辑的清理连接直接继承旧设置页，必要原字节复核确认：状态 `0x40→0x3f` 后检查 `ctx+84`；若 tick 差不大于1999，先 `a008ae58(timer)`，随后将 `ctx+84=0`；较晚分支仅清槽。然后取 **相同 `ctx+10` target**，调用 `a0089184(target,a00f43bc)` 查询；非空时 `a01b2eb4(target,a00f43bc)` 删除，最后 `a018fb3c(target,0)`。后续 label 变色/刷新/业务提交继承旧记录，不改变执行顺序。

`a0089184` 的 `a00891a6..91ae` 比较节点 `+00` 与 target、`+04` 与 exec；`a01b2ee0..2ef0` 使用同一对匹配（通用API支持0通配，此调用两项均非0），命中后 `a008ac06(node)` 从动画链摘除，按 `+14` 可选通知后 `a008ab8a(node)` 释放，再重扫。显式删除不走 `+10` completed。本实例 `+14=0`，故这里不释放 target/ctx、不调用业务 ready；释放的是动画节点。查询遍历的厂商字 `a00891b2=8bc7e740` 保留为未知，本轮不替换其模型、不把局部比较当作完整列表算法认证；该调用身份同时受旧完整汇编与真实 delete 匹配交叉支持。

## 未闭精确边、恢复程度与验证

局部已回答：descriptor 生效字段、对象/ctx 区别、path/exec ABI、周期与 repeat、正常结束编辑的动画节点清理身份。模块仍部分恢复：所有离页/对象析构是否均经过上述结束编辑分支、target 与 ctx 的完整创建/销毁所有者、一次性 timer 到期后槽的其他管理路径，本轮没有闭合。尤其不能由显式结束编辑推断所有页面删除都先删动画；未从 SIM 行为推导 ROM 对象寿命。

后续只需沿 `ctx+10` target 的正常页面 DELETE 连接到现有 `(target,a00f43bc)` 删除或通用对象删除路径，核其与 ctx 释放的顺序；不需要扩全部动画、GUI 或背光驱动。

实际验证：运行本目录 [verify.py](../../analysis/backlight-animation-d19-0041-20261024/verify.py)，直接只读 ROM，以 `0x9ffff000` 映射核19个小窗口、6个关键 store/比较/宽度锚，核旧 settings 的真实查询/删除调用，保留唯一厂商未知字。没有新反编译、重导旧函数、整库提取或哈希账。`git diff --check` 通过。此为研究者自核，未冒称独立技术验收。
