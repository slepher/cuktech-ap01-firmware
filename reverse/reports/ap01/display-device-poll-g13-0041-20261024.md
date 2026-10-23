# G13：显示 fd 的 framebuffer poll 与 revents 通知接入

2026-10-24；基线 `db28e99`；分支 `codex/re-0041-g13`。**找到 `/dev/fb0` 正常注册所用 ops 的具体 poll 方法 `a0132116`，以及该方法的条件立即通知→`node+1c` word 写入→已装 `a0109b8e` callback 静态链。** 未观察设备 ready 或运行时 fd/inode 值；异步硬件事件入口未恢复。作者必要静态验证通过，待独立技术复核；新增页面业务和整库来源认证均为0。

## 继承结论：已有出处→行为→局限

|已有出处|可直接复用的行为|本题实际缺口|
|---|---|---|
|[F05](miio-exit-callback-f05-0041-20261023.md)、[F06](display-exit-review-f06-0041-20261023.md)、[F07](display-source-auth-f07-0041-20261023.md)/F08|配置首槽是 `/dev/fb0`；显示后端由 display+2e0 取得；a0086d26..6d40 以 pathname、flags3 调 a003f4f6，并把返回 fd 写后端首 word；不是另外的 loop backend fd|fd 经正常 open 查找的 inode 对应哪张 ops、poll 槽是什么。候选 LVGL/NuttX 来源不代替 ROM 设备表|
|[G07](display-alternate-work-g07-0041-20261023.md)/G08|a008335e 从同 display getter 的后端首 word 取 fd→state+58；state+60 poll/poll+34 watcher、mask4、adapter、stop/刷新/pending 清零|全部继承，不重导消费者或业务 poll|
|[G09](display-ready-dispatch-g09-0041-20261024.md)/G10、[G11](display-ready-producer-g11-0041-20261024.md)/G12|fd 桶同 watcher、fallback ADD `(fd,node+14,1)`→a003e674→a003e344、callback a0109b8e 写 node+10 byte1、materializer 读 node+1c 并复制 data64|只补具体设备正常 revents 写者与 callback 接入。登记返回非负不等于 ready|
|factory-test/retained-initializer.json；Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`；近期 G07/G09/G11 retained 核对|真实 initializer、显示发布、backend_fd 解析及 collect 已经留存|不再复制整 initializer/raw；不将旧 pending 当缺失依据|
|whole-rom-coverage-0041-20261023-round1.json 的 `video/fb.c`/`lcd/fb_dev.c` 既有 source xrefs、extent/direct-call 索引|`video/fb.c` 对 a0132116、a0055a14 的既有定位；a003e2a0 已有 extent `ev_564da8a679b82c09090d06388230fb67447ca45c5bf47baf9fb0022885ac9f14`；a0132116 extent `ev_8a2b060d0845dc16c99a4cdbbbe48e775d0ede8a16577048097c3a78e52e83f2`|已有函数定位不冒称本轮首次发现。仅补字段/表绑定的必要窗口|

先继承 G07/G09/G11、F05/F07 已有 complete/最终矩阵/ZIP 与来源复用结果，不重做 SIM 显示恢复。本轮另在较晚 `whole-rom-round3-initial.evidence.json` 按 a003e2a0/a0055a14/a0132116/a01b5a12 精确检索，未命中 body（索引见 evidence.json）。这个有界结果不表示所有历史证据都未分析它们。没有以 SIM、照片或安全替代证明 ROM 设备 ABI。

## 本轮复核或纠正

没有纠正 G11/G12 的节点布局。补充区分：`P=node+14` 是设备层 poll 视图；`P+8` 才是 `node+1c` revents，`P+c` 是 callback arg=node，`P+10` 才是 callback。`P+14` 是设备登记用私有槽回指，不是 revents 或 callback。没有把 `backend_fd` 当本 fd，也没有把所有 callback 触发升级为非零 revents。

具体设备表仍须从注册到 inode 绑定；仅凭 `video/fb.c` 字符串、候选源码同名或 fd 非负均不足以选中 poll 方法。本轮依原字节认证下面这条正常注册路径，同时保留“实际 open 命中该 inode、运行中未换表”的条件。

## 真正新增：fb0 注册、ops 与设备方法

`a0056a14` 仅在保存的 plane 数状态 s7==1 时走 `6a1a..6a2a`：a2=`a01c0bc4`，原字符串 `/dev/fb%d`，a3=0，以 buffer=`frame-d0`、size16 调格式化 helper。故该分支形成 `/dev/fb0`；另一分支 `6ce6..6cf8` 使用 `/dev/fb%d.%d`，不能混为同名设备。`6a2e..6a3c` 随后以 `(path_buffer, a01c1368, s3)` 调 `a01b5a12`，返回负值转原清理分支。本题不将注册调用当作已经成功。

`a01b5a12` 保存 ops 到 s1、第三参数至栈，调用 inode 获取/创建 helper；非负后在 `5a4a` 写 inode+10=同 ops，`5a4c` 写 inode+18=第三参数；半字 inode+e 的低 nibble 改1，其他位保留。失败走原解锁并返回保存的错误；成功解锁、返回0。没有重建目录解析全集。

表 `a01c1368` 的 **+20 word=`a0132116`**。a003e344 的已知设备分派在 `e388/e38c` 取 inode+10→ops+20，非空后 `e394/e398` 恢复 P 为a1、以原 file为a0、setup为a2作间接调用。此处只补 ops 槽身份，不重导 G11 的 fd 解析/借用归还。

`a0132116(file,P,setup)` 的 `2122..2128` 读取 inode=file+c、D=inode+18、F=file+10，再读 D 首 word。正常非空前置路径进入保存/清 mstatus bit8 的临界区（`2146/2148`），尾部 `215a` 恢复原 mstatus。不能把这个静态临界区解读成已观察 IRQ。

设备 setup 的必要结构如下；F/D/P 均为偏移视图，不是完整原 struct：

```c
// 非原源码；仅正常前置路径。
if (setup) {
    if (word(F+8)==0) i=0;
    else if (word(F+12)==0) i=1;
    else { restore_mstatus(); return -16; }
    slot = F + 8 + i*4;
    word(slot)=P;
    word(P+0x14)=slot;              // node+28 私有回指
    plane = a01320e0(D,word(F+4));
    value = a0059678(plane);
    if (value != 0)
        a003e2a0(slot,1,4);
    restore_mstatus();
    return 0;
} else {
    slot=word(P+0x14);
    if (slot) {
        word(slot)=0;
        word(P+0x14)=0;
    }
    restore_mstatus();
    return 0;
}
```

`2170` 原字 `0x04e7970b` 为 addsl a4,a5,a4,2，`2176` 原字 `0x0497948b` 为 addsl s1,a5,s1,2；分别形成 F+i*4 后在+8存 P，以及 F+(i+2)*4 的 slot 本身。`217a` 将同 slot 写 P+14。两条厂商字独立按 opcode/funct3/top5/rd/base/index/shift 核对并引用现存只读模型规则，未修改模型。

a01320e0 的正常尾部以 `(F+4+1)*0x28` 索引 D+10 数组；本题仅以返回 plane 指针调用身份描述，不扩展 plane 表分配。a0059678 的原算术是 `word(plane+4) - a0059660(plane)`，后者正常非空路径返回 `word(plane+8)-word(plane+c)`；本轮不把这些未完全认证字段强命名为容量/硬件状态。设备 poll 的精确门是 helper **非零**，不是正值、不是事件已由硬件产生。调用通知之后仍返回0。

## 真正新增：revents 写入和已安装 callback

`a003e2a0(array,count,event_mask)` 的正常参数为 `(slot,1,4)`；`e2b0/e2b2` 保存 array并令 i=0。`e2cc` 原字 `0x4499450b` 为 lrw a0,s2,s1,2，即 `P=word(array+i*4)`，不是直接把 slot 本体当 P。

对非空 P，原顺序为：

```c
requested = word(P+4);
old_revents = word(P+8);
r = ((requested | 0x18) & event_mask) | old_revents;
if (r & 0x18) r &= ~4u;
word(P+8) = r;                     // e2e4，32位；P+8=node+1c
reread = word(P+8);               // e2e6，保留原重读
if ((reread | (requested & 0x10000)) != 0) {
    cb = word(P+0x10);             // e2f0
    if (cb) cb(P);                // e2fc；原a0仍是P
}
```

一般 helper 在调用后恢复 event_mask/count，递增 i，count 达到或 event_mask 为0时结束；本实际 callsite 的 count=1。本题不外推所有设备调用者。**G11 的同节点初始化 requested 包含0x10000，故 helper 可在 revents仍0时通知；不能仅凭 callback 写 flag 推出 ready。** 本 mask4 情形下，无错误位且 requested含4时，确有 r保留4→word(node+1c)=4 的条件连接；若已有0x18错误位则按原序清4。

G11 已认证 `word(P+c)=node`、`word(P+10)=a0109b8e`。本轮 e2fc 的 a0=P 因而精确满足该 callback 在 a0109b8e 读参数+c 取得 node、写 node+10 byte1 的 ABI；没有新造 callback 或传 node本体替代P。其后 materializer、记录、fd桶、watcher和业务 callback 直接引用 G11/G09/G07，不计新增。setup 的通知可以在函数返回/ADD挂链之前发生；本轮不改原序，也不以此推断任何并发执行结果。

所有权：F 的两个槽借用 backend 节点中的 P；P+14 借用 F 内槽地址。setup失败满槽分支不安装；正常 teardown先清槽再清回指，不释放节点/F。后端节点归还与 file借用寿命继续引用G11；本题不把通知看成所有权转移。

## 未闭精确边、来源和实际验证

- **事实**：fb0格式路径、注册ops参数、inode字段写入、表+20目标、设备P双槽、通知helper的word写入/重读/间接调用及原字节。**推断**：这是所选显示 fd 的 framebuffer正常poll方法，前提是正常fb0注册成功、open命中该inode并保持该ops/private身份；不是运行时身份观测。
- **未知**：实际板上走fb0还是另一平面分支、注册/open及F初始化是否实际成功、fd是否复用、helper条件是否实际非零、异步硬件生产者何时通知、是否实际获得mask4。没有把静态正常分支说成执行证明。没有搜索所有VFS/IRQ/设备/网络。
- 来源仅由既有 `video/fb.c` 路径和ROM合同支持NuttX framebuffer家族；精确版本、编译配置、是否未改源码仍未知。F07本地LVGL来源匹配不认证本设备实现，开源排除0。
- [verify.py](../../analysis/display-device-poll-g13-0041-20261024/verify.py) 实际通过：33项局部原字节/调用/表值/厂商编码检查，276B必要新窗口；[evidence.json](../../analysis/display-device-poll-g13-0041-20261024/evidence.json) 保存这些窗口、既有索引Evidence和较晚round3精确复用结果。最初字符串切片少取1B的脚本断言已修正后全部通过，不涉及ROM结论变更。原ROM绝对路径只读，映射VA−0x9ffff000。
- 没有新开、共享或切换REA target；按REA技能复用旧Evidence和局部ROM原字节，未虚构新REA ID。没有执行固件、SIM、构建、历史回放、设备或网络；只写本独占报告/analysis。提交前检查差异和 `git diff --check`；本报告不冒称独立验收。

一个必要后继是新agent独立复核本次 fb0注册→ops+20→P双槽→通知revents/callback 的条件合同，尤其 P+14私有回指与node+1c宽度、0x10000可通知而revents为0的限制。异步硬件入口仍可定位为同F槽数组之外谁调用a003e2a0，但不在本轮扩展或自行承接。
