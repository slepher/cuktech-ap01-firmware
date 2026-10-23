# 0041 E13：CTK offline panel/stack-view 合同复用闭包

本题主体已有覆盖，**新增业务恢复为 0**。E04 所说“本轮未恢复”的 `a00ef1d4`，早在 `charge-0041-round4.json records[4]` 已有完整 262 B 实现、伪代码和原汇编；较新的 whole-rom-private callback 又保留了状态变化分支。此次不重新导出函数，只把离线入口、两端口汇合、panel 四槽复位与 stack-view 生命周期连接成可直接继承的局部合同，并核必要原字节。E04 的局部验收范围无需被推翻，但其未核范围不能外推为历史上没有分析。

基线 `1c6db79`；独立树 `re0041-e13`，分支 `codex/re-0041-e13`。只写本报告和独占 analysis 目录。使用 REA skill 的既有证据复用、原字节及事实/推断/未知区分方法；未打开 REA target，未接触可写数据库，未执行目标、SIM、项目构建、历史回放、设备或网络操作，未修改 ROM、生产代码、配置或分析器模型。其他研究树保持不变。

## 继承结论：出处、行为和局限

| 既有出处 | 已解释行为 | 局限及本轮处理 |
| --- | --- | --- |
| [E02](uiiface-ownership-review-e02-0041-20261023.md)、[E04](ctk-view-review-e04-0041-20261023.md) | `a00f4740(view,port)` 数值视图；三个借用资源；0x52 B frame 内视图；转换返回差异；在线端口互斥；主要标量消费者 | 全部继承，不重做 converter、在线 port1/2 或扩展字段读者 |
| 主仓只读 `reverse/rehost/charge-0041-round4.json records[4]` | `a00ef1d4(panel,view)` 完整四槽有效行/无效行复位 | 不是新增函数；旧记录完整汇编可用，仅必要边与原字节核对 |
| 同文件 records[5]；E04 完整 SOC 消费验收 | `a00ef2da(panel,view)` SOC/时间显示 | 直接继承其本地标量读取及 view 不持久保存合同，不重导出 |
| 主仓只读 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json` callback record | `a00adabc(app,item)` 完整离线分支和 port2 汇合、调用原序 | 反编译存在 unreachable-block warnings；结论只认证以下必要指令窗口，不认证整个 6054 B callback |
| 主仓只读 `reverse/rehost/page-logic-0041.json records[15]` | `a0024906` 为既有 fill helper | 沿旧合同使用，未分析通用内存库来源 |
| charge-complete、page-logic-evidence/evidence2、较晚 round3/evidence 22 个顶层 JSON | 精确地址复用检索已完成 | 所选三个目标地址的文本命中计数在验证 JSON；round3 未命中不是未曾分析或全历史排除。round3 本题无需新导出 |
| 最终 ZIP charge UI、旧 SIM/照片（E12 已复用） | 安全服务重建的电池/端口显示 | 不作为 ROM offline ABI 或调用顺序依据，不重新读取全部源码或运行 |

可定位 Evidence：reset `ev_b112edff9d7110ba2ca8c038a09aa76b465fcf1eb08182b0822edef61a81a2b6`；SOC `ev_587151d11950a61f008e9dd2c3634908159039c4ff83ad10304e57d29504f127`；callback `ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5`。前两者为旧 generic RV32 Ghidra 记录，厂商 ABI 原本有局限；本轮所选 reset/离线窗口全为标准指令，未运行模型。callback 为 Ghidra 12.1.4 / 私有 ap01thead2 留存，不能把其旧 warnings 隐去。ROM 使用主仓绝对路径只读，基址 `9ffff000`，沿用既有身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不新增哈希清单。

另复用 [H07](weather1-navigation-h07-0041-20261023.md)、[multi-screen-app-host §3.1](multi-screen-app-host-0041.md)、[screen-host append](screen-host-append-validation-20261020.md) 及 `reverse/analysis/screen-host-append-20261020.json#/functions`：`a00b2ff4` 已知读 win+0x34 的活动子页索引；`a00b3106(win,target,anim_dir)` 已有完整332 B原汇编（Evidence `ev_182941f3e3fa2b7a776b17694b73e08f88952c81a3f8a48af0f4513bc5808b76`），更新active/prev与坐标、以方向1右向左滑至目标。screen-host-interface/lifecycle 的宿主策略、保护与历史执行不是本次ROM调用的额外证据；guide-complete 的引导状态和reset hooks也不能替代原件导航ABI。此处可靠滑动合同直接继承，不应再派selector/滑动通用恢复题。

## 本轮局部复核与表述收紧

状态变化入口并非“任何非在线值都刷新所有 panel”。继承 E04 的 port 解码后，`index` 为 port-1 的零扩展 u16。`adc32` 取旧状态 `u8[62fc403c+index]`，新状态来自 `item+0x0d` 的 u8（先存 frame-0xd4）。`adc3a` 新旧相同跳过变化块；旧非零到 `ae196` 后，`ae19a` 新非零则跳公共状态保存。因此本题离线分支准确门为 **旧非零、新零**。

离线块先通知 `a00a769a()`、置 `62fc403a=1`，保留 popup 查找/条件关闭原序（`a008184e→a00a7334(...,0xc,&local)`；成功且 local 非零时只在 `local+0x40==index` 调 `a00ded6c`）。随后清 `62fc4041+index`。这些 helper 的完整内部业务未重做。

`ae1f0..ae1f8` 调 `a00b2ff4(app)` 得 selector：返回1且 index0、或返回2且 index1时，`ae378..37e` 调 `a00b3106(app,0,1)`；其后才进入两字节清零及 panel 刷新。结合已恢复滑动合同，这就是当前C1/C2详情页对应端口离线时，切回 Power child0，并使用 anim_dir=1；仅该端口对应的活动详情页触发切页。a0为同一app对象：E04/E05已连接主window构造→注册userdata，callback以保存寄存器s6持有它，此处又传入同一s6。没有发现需要另立新题的对象身份差异；真实屏幕/墙钟效果仍不由静态证明。

`ae200..20e` 以 `(u8)index` 清全局 `62fc4062+index` 及 `62fc4067+index`；原字节 `ae20a:238b0702` / `ae20e:a38d0702` 为两次 byte store。index0 从 child(app,1)+0x10 指向对象的 +4 取 panel；index1 从 child(app,2) 同链取 panel。index1 于 `ae3a6` 设 a1=2，`ae3a8` 跳到 `ae234`；index0 于 `ae232` 设 a1=1。**同一静态 converter call `ae238` 承担这两个离线端口。** 更高 index 不经过这两个详细 panel 刷新，而跳 `ae250` 的公共汇总更新；不能据此说它们不做任何离线处理。

两个分支均先 fill(frame-0x94,0,0x52)，再 convert(view,port)，然后立即 `reset(panel,view)`、`battery(panel,view)`。`ae238:ef608450→a00f4740`、`ae242:ef003479→a00ef1d4`、`ae24c:ef10e408→a00ef2da` 的实际机器字以验证 JSON 为准；调用间均重新设置 a0=panel、a1=view，没有依据 converter 返回值作门控。返回0可能仍消费初始零或 converter 已写内容，不能默认 converter 失败一定完全未写，更不能把在线失败跳过消费套到这里。

## 继承实现：四槽复位和数据合同

`a00ef1d4(a0=panel,a1=view)` 保存 view 到 s4，row 初值 view+0x10，slot 初值 panel+0x20，flag 初值 panel+0xa0，终点 view+0x50。每轮 row+=0x10、slot+=0x20、flag+=1，因此恰好四槽，**不按 view+6 的数量控制迭代**。view+6 仅作为名称函数第四参。

| 行条件/字段 | 顺序及下游 |
| --- | --- |
| `u8[row+0x0e] == 1` | `a00f4610(slot,row)` → `a00f44e8(slot,u8[row+0xc],u8[row+0xd],u8[view+6])` → `a00ef0ec(slot,u8[row])` → `u8[panel+0xa0+i]=1` |
| 行有效字节为其他值（包括0或2） | 按序 `a00d8f7c(widget,1)` 操作 slot+4、+1c、+8、+10、+14、+18 六个控件；slot+c 文本写 ROM `a0607610` 的 `--`；给其低24位颜色666666；最后 flag=0 |

这一严格 `==1` 与 E04 在线更新的 `!=0` 条件不同。`ef210:8347e900` 读 byte，`ef214:639a6707` 是 bne 对常数1。不是新增行为发现，而是旧完整 callee 原序的局部认证。名称消费者会按已有合同初始化功率文本并调用 status(slot,0)，所以 reset 的真实 **values→name→status** 顺序必须保留；不能为了“看起来合理”改成在线名称初始化后数值更新的顺序。其后只打印完成日志并恢复 0x40 B 本地 frame，无需业务返回值；caller也没有测试 reset 或 SOC 返回值。

以下为旧合同的顺序整理，不是原源码，省略 popup/汇总 helper 内部：

```c
if (new_status != old_status && old_status != 0 && new_status == 0) {
    notify_and_conditionally_close_popup();
    store8(0x62fc4041 + index, 0);
    selector = current_selector(app);
    if ((selector == 1 && index == 0) || (selector == 2 && index == 1))
        switch_call(app, 0, 1); // 继承已知Power目标0、动画方向1
    store8(0x62fc4062 + (uint8_t)index, 0);
    store8(0x62fc4067 + (uint8_t)index, 0);
    if (index == 0 || index == 1) {
        panel = load32(load32(child(app,index+1)+0x10)+4);
        fill(view,0,0x52);
        convert(view,index+1); // 原程序不检查返回
        reset_four_slots(panel,view);
        battery_and_time(panel,view);
    }
    // 原有child0汇总控件/位与timer处理继续；本题不扩整个页面状态机
}
```

## 真正新增

新增业务、整函数导出、可排除上游实现均为 **0**。新增交付仅为旧证据索引与上述局部合同整理、32 个机器字锚点和有界静态验证。原始 `--` 为本轮只读定位的三个字节 `2d2d00`，用于复核旧 generic decompiler 的 DAT 文本占位，不是新资源恢复。E04 本身仍是局部验收，没有宣称全 offline 已验收；本轮也不冒称独立技术验收。

## 所有权、未知与一个后续闭包

panel 由 app child 的现有结构借用，不在 reset 中分配/归还。view 在 callback 0x100 B frame 的 `s0-0x94..s0-0x42`，含四条16 B row；reset 仅暂存其地址到本次保存寄存器，store 为保存寄存器、本地颜色或 panel+a0 的四个 byte 标志。其直接调用里只有已验收 `a00f4610` 收 row；名称/status只收控件和标量。E04 已核 values/SOC 不持久存 row/view，不向下游转交 view。因此本条 **reset→SOC** 链没有延长 view 的生命周期，callback 返回后 frame 归还即失效；不得把其 prologue 保存旧 s4 当作新 view 持久 store。颜色仍仅认证低24位，局部 word 高字节未强行补零。

事实是保留指令、参数寄存器、读取宽度、分支与调用顺序；“离线、selector、panel、方向/SOC/功率”等业务名称为既有字符串和结构支持的分析解释，未观察设备执行。继承的 converter 三资源仍归 item，不因栈视图刷新转移所有权。公共 `ae250` 之后的 child0 汇总/位清除/定时器块虽已有留存，本轮不扩大为全部状态机的认证。

本题有证据所需的接入ABI、同app身份、切回Power、panel四槽及栈view合同均可继承闭合，没有真正未覆盖的selector/滑动差异。两个helper已被H07及旧宿主覆盖，本专项未展开其内部不构成新的分析缺口。**后续闭包建议：本专项不再另立研究题，由管理者从其他已定位断边补位。** 实际物理显示/异步墙钟时序、app/item最终注销、+34/+38读者、全局deinit仍属已有范围未知，均非本任务闭包所需；通用动画合同不重做，历史合成对象执行不外推为本离线分支运行观察。

## 实际静态验证

[验证器](../../analysis/ctk-offline-transition-e13-0041-20261024/verify.py) 通过；[结果](../../analysis/ctk-offline-transition-e13-0041-20261024/static-checks.json) 保存 **32 个选定原字节锚点、162 条有界标准指令连续边界检查、直接/条件/压缩跳转目标、旧 source 命中索引、22 个较晚 round3 顶层JSON的有界检索**。锚点检查比较 retained operands 人工复核，脚本独立解码 mnemonic/长度/目标；不声称脚本完整证明所有数据流或全函数等价。脚本未导入其他验证器、未复制全函数/ZIP源码，未新开target，无工具阻塞。
